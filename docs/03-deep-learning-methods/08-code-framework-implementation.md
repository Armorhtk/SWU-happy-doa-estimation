---
id: deep-learning-code-framework-implementation
title: 3.7 深度学习DOA估计代码框架实现
slug: /deep-learning/code-framework-implementation
---

# 3.7 深度学习DOA估计代码框架实现

前面几节用了大量篇幅讲清楚了数据怎么生成、特征怎么提取、分类和回归的任务形式各自是什么。每一节都配有代码片段，但这些片段是分散的，都只聚焦于当下那一个知识点。到了真正动手实验的时候，读者会遇到一个现实问题：**这些片段怎么拼在一起？一个完整的深度学习 DOA 实验，从零到出结果，应该是什么样的工作流？**

本节就是为了回答这个问题而写的。我们不再讲新的方法，而是把前几节的所有内容整合为一个结构清晰的最小可运行框架，并用教程式的语言把每个文件、每个关键步骤说清楚。

---

## 3.7.1 框架结构总览

整个框架由四个 Python 文件组成，存放在 `sources/codes/ch3_dl_doa/` 目录下：

```text
ch3_dl_doa/
├── utils.py    数据生成、特征提取、标签构造、Dataset 类
├── models.py   网络结构定义（CM-CNN 分类、IQ-LSTM 回归）
├── train.py    训练主脚本（含早停、检查点保存、训练曲线）
└── eval.py     评估与对比脚本（RMSE 分析、MUSIC 基线对比）
```

这四个文件之间的关系是单向的：`utils.py` 和 `models.py` 是基础层，不依赖其他文件；`train.py` 从两者导入；`eval.py` 从三者导入。这种结构的好处在于：每个文件职责单一，改一个地方不会意外破坏其他地方。

在正式上手之前，先把整个实验流程的全貌梳理清楚：

```text
utils.py 生成仿真数据
    │
    ▼
提取特征（CM 或 IQ）→ 构造 DOADataset
    │
    ▼
train.py 训练模型
    ├── 分类任务：CM-CNN + BCEWithLogitsLoss
    └── 回归任务：IQ-LSTM + MSELoss
    │
    ├── 每 epoch：前向 → 计算损失 → 反向 → 更新参数
    ├── 验证集监控 → 早停 → 保存最优检查点
    └── 输出训练曲线图
    │
    ▼
eval.py 评估模型
    ├── 加载检查点 → 在测试集上推理
    ├── 计算整体 RMSE 与按 SNR 分段 RMSE
    ├── 与 MUSIC 基线对比
    └── 绘制 RMSE vs SNR 折线图 + 预测散点图
```

---

## 3.7.2 utils.py：数据与特征的统一入口

`utils.py` 是整个框架的地基，所有与"数据"有关的操作都在这里完成。它对外提供五类功能：仿真数据生成、两种输入特征提取、两种标签构造、统一的 `DOADataset` 类，以及 MUSIC 基线函数。

**仿真数据生成**遵循第一章建立的阵列观测模型。核心函数是 `generate_dataset`，它接受阵列参数（$M$、$N$、$d$）、信号参数（$K$、角度范围、最小间隔）和 SNR 范围，批量生成观测矩阵、真实 DOA 标签和对应的 SNR 记录：

```python
from utils import generate_dataset

X_raw, labels, snrs = generate_dataset(
    num_samples  = 12000,
    K=2, M=8, N=256,
    snr_range_dB = (-5, 20),
    theta_min=-60, theta_max=60, min_sep=5,
    seed=42
)
# X_raw  : (12000, 8, 256) 复数
# labels : (12000, 2)       真实 DOA（度，升序）
# snrs   : (12000,)         每样本的 SNR（dB）
```

返回值中的 `snrs` 在训练时不直接使用，但在 `eval.py` 里按 SNR 区间分段评估时会用到。把它和数据一起记录下来，是为了让测试集的评估更有信息量。

**特征提取**通过 `build_features` 完成，只需传入 `feature_type` 参数即可切换：

```python
from utils import build_features

# 协方差矩阵特征（适配 CM-CNN）
feat_cm = build_features(X_raw, feature_type='cm')  # (12000, 2, 8, 8)

# 原始 IQ 序列特征（适配 IQ-LSTM）
feat_iq = build_features(X_raw, feature_type='iq')  # (12000, 256, 16)
```

两种特征之间的核心差别在第 3.2 节已经讨论过：CM 特征是对观测数据做了二阶统计压缩，输入维度与快拍数无关；IQ 特征保留了全部原始信息，但维度随快拍数增长。

**`DOADataset` 类**把特征数组和标签数组打包成 PyTorch 的 `Dataset`，同时在内部完成标签的转换。传入 `task='classification'` 它就生成 multi-hot 标签；传入 `task='regression'` 它就生成归一化到 $[-1,1]$ 的角度向量。使用者不需要手动做这些转换：

```python
from utils import DOADataset

ds = DOADataset(
    features=feat_cm, labels_deg=labels,
    task='classification',
    theta_min=-60, theta_max=60, resolution=1.0
)
# ds[0] 返回 (特征张量, multi-hot 标签张量)
```

---

## 3.7.3 models.py：两个网络结构

`models.py` 定义两种网络，分别对应分类任务（CM-CNN）和回归任务（IQ-LSTM）。

**CM-CNN 分类网络**的输入是 $(B, 2, M, M)$ 的协方差矩阵双通道特征，输出是 $(B, D)$ 的原始 logit 向量，不经过激活函数——激活和损失计算都在 `BCEWithLogitsLoss` 内部完成，数值上更稳定。`AdaptiveAvgPool2d((2, 2))` 让网络对不同的 $M$ 保持兼容：不管阵元数是 4 还是 16，池化后的特征图大小始终是 $2 \times 2$，全连接层维度不需要修改。

**IQ-LSTM 回归网络**的输入是 $(B, N_{\text{snap}}, 2M)$ 的快拍序列，在时间维度上逐步处理，取最后时刻的隐状态经过回归头输出 $K$ 个归一化角度。`forward` 方法末尾做了 `torch.sort`，强制升序排列来处理多信源配对问题。这个操作是可微的，不会阻断梯度流。

两个网络都通过 `build_model` 工厂函数来实例化，避免调用者直接操心构造函数参数：

```python
from models import build_model

# 分类网络：M=8 阵元，D=121 格点（-60°到60°步长1°）
model_cls = build_model('cm_cnn', M=8, D=121, base_channels=32, dropout=0.3)

# 回归网络：输入维度 2M=16，K=2 个信源
model_reg = build_model('iq_lstm', input_size=16, K=2,
                        hidden_size=128, num_layers=2, dropout=0.3)
```

---

## 3.7.4 train.py：训练主脚本

打开 `train.py`，你会在顶部看到一个名为 `CONFIG` 的字典，所有超参数都集中在这里：

```python
CONFIG = {
    "run_name"    : "exp01_cm_cnn_cls",  # 每次实验改这里
    "M"           : 8,
    "K"           : 2,
    "N_snap"      : 256,
    "feature_type": "cm",
    "task"        : "classification",
    "model_name"  : "cm_cnn",
    ...
}
```

`run_name` 是这次实验的标识符，它决定了检查点的文件名（`checkpoints/exp01_cm_cnn_cls.pth`）和训练曲线图的名称。每次改超参数做新实验，先改 `run_name`，就不会覆盖上一组的结果。

训练函数 `train(cfg)` 按顺序执行四个步骤，每个步骤的进展都有编号打印，方便确认脚本没有卡住：

**步骤一（生成数据）**：按 `cfg` 里的参数调用 `generate_dataset`，打印样本数量和 SNR 范围。

**步骤二（特征提取与 Dataset）**：调用 `build_features` 和 `DOADataset`，按 `val_ratio` 划分训练集和验证集，构造 `DataLoader`。验证集的比例默认是 15%，不参与参数更新，专门用于监控过拟合。

**步骤三（模型实例化）**：根据 `model_name` 调用 `build_model`，打印可训练参数数量——这个数字能帮你直觉上判断模型是否太大或太小。

**步骤四（训练循环）**：这是核心。每个 epoch 先跑训练集（`is_train=True`），再跑验证集（`is_train=False`），记录两者的损失。`run_one_epoch` 函数里有一行梯度裁剪：

```python
nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
```

这行对 CNN 几乎没有影响（CNN 的梯度通常不会爆炸），但对 LSTM 至关重要——RNN 的梯度在时间维度反向传播时很容易数量级激增，裁剪是标准的防御措施。统一放在这里而不是条件判断，省去了维护两套代码的麻烦。

**早停机制**：如果验证损失连续 `patience` 个 epoch 没有改善，训练提前终止。每次验证损失创历史新低时，保存完整检查点：

```python
torch.save({
    'epoch'      : epoch,
    'model_state': model.state_dict(),
    'val_loss'   : best_val,
    'config'     : cfg,         # 把超参数一并存进去
}, ckpt_path)
```

把 `cfg` 也存进检查点是一个关键设计：`eval.py` 加载检查点时可以直接从里面读取阵列参数、特征类型、模型配置，而不需要调用者手动传入。这避免了"训练时的参数和评估时传的参数对不上"的常见错误。

**运行第一个示例（CM-CNN 分类）**：

```bash
cd ch3_dl_doa
python train.py
```

控制台输出类似：

```text
[1/4] 生成仿真数据集...
  生成 12000 个样本，耗时 8.3s
  SNR 范围：-4.9 ~ 19.9 dB

[2/4] 提取 CM 特征...
  特征形状：(12000, 2, 8, 8)，耗时 1.2s

[3/4] 实例化 cm_cnn 网络...
  可训练参数数量：98,937

[4/4] 开始训练（最多 40 epochs，早停 patience=10）...
  Epoch   1/40 | train=0.43821  val=0.40617  lr=1.00e-03 ✓
  Epoch   5/40 | train=0.29344  val=0.27813  lr=1.00e-03 ✓
  ...
  Epoch  40/40 | train=0.12403  val=0.13917  lr=6.25e-05
```

训练完成后，`checkpoints/exp01_cm_cnn_cls.pth` 就是可以直接送给 `eval.py` 的最优检查点。

**切换到 IQ-LSTM 回归**只需在 `train.py` 底部取消注释那段 `CONFIG_LSTM` 并执行：

```python
CONFIG_LSTM = {
    **CONFIG,                         # 继承大部分参数
    "run_name"    : "exp02_iq_lstm_reg",
    "N_snap"      : 128,              # LSTM 对快拍数敏感，先用较短序列
    "feature_type": "iq",
    "task"        : "regression",
    "model_name"  : "iq_lstm",
    "hidden_size" : 128,
    "num_layers"  : 2,
}
train(CONFIG_LSTM)
```

---

## 3.7.5 eval.py：评估与对比

模型训练好后，`eval.py` 负责在一个更宽广、从未见过的测试集上评估性能，并把多种方法放在一起横向对比。

`EVAL_CONFIG` 字典里列出了要评估的检查点路径，以及测试集的 SNR 范围（故意设置得比训练时更宽，以测试泛化）：

```python
EVAL_CONFIG = {
    "checkpoints": [
        "checkpoints/exp01_cm_cnn_cls.pth",
        "checkpoints/exp02_iq_lstm_reg.pth",
    ],
    "snr_range": (-10, 25),    # 比训练时宽，包含 -10 dB 极端情况
    "run_music": True,         # 是否同时运行 MUSIC 基线
    ...
}
```

`eval.py` 运行时会依次：生成统一的测试集（所有方法用同一批数据，保证对比公平）→ 逐个加载检查点并推理 → 计算整体 RMSE 和按 SNR 分段 RMSE → 运行 MUSIC 基线 → 打印汇总表并绘图。

**运行评估**：

```bash
python eval.py
```

终端输出示例：

```text
评估：checkpoints/exp01_cm_cnn_cls.pth
  整体 RMSE：0.7423 度
  按 SNR 分段：
    SNR [-10,-5) dB：RMSE = 3.2104°  (n=498)
    SNR [ -5, 0) dB：RMSE = 1.0832°  (n=502)
    SNR [  0, 5) dB：RMSE = 0.5641°  (n=501)
    SNR [  5,10) dB：RMSE = 0.4012°  (n=500)
    ...

汇总：各方法整体 RMSE
──────────────────────────────────────────
  exp01_cm_cnn_cls    ：0.7423 度
  exp02_iq_lstm_reg   ：0.5817 度
  MUSIC（基线）        ：1.3241 度
```

这里出现的数字只是示意，读者实际跑出的结果会因超参数设置不同而有所差别。重要的不是绝对数值，而是**各方法之间的相对大小**，以及 RMSE 随 SNR 变化的趋势是否符合预期（低 SNR 下所有方法精度都会下降，深度学习方法的下降通常比 MUSIC 更平缓）。

`eval.py` 最后会保存两张图：`eval_rmse_vs_snr.png`（各方法的 RMSE-SNR 折线图，这是最直观的性能对比图）和 `eval_scatter_*.png`（预测角度 vs 真实角度的散点图，理想情况下所有点沿 $y=x$ 对角线分布）。

---

## 3.7.6 动手调参：怎样让 RMSE 更低

把框架跑通是第一步，更有价值的是通过调参理解哪些因素真正影响了精度。下面给出几个有针对性的调参方向，每个方向都有明确的预期变化，读者可以验证自己的理解是否正确。

**方向一：数据规模对精度的影响。** 把 `num_train` 从 12000 减到 3000，再增大到 30000，看 RMSE 如何变化。经典的学习曲线形状是：数据量翻倍，RMSE 持续下降，但降幅随数据量增大而减小（边际收益递减）。如果发现 3000 和 30000 的结果差不多，说明网络容量才是瓶颈；如果差距很大，说明当前数据量还不够。

**方向二：SNR 覆盖范围对泛化的影响。** 先只用 $[5, 20]$ dB 的高 SNR 数据训练，再用 $[-10, 20]$ dB 的宽范围训练，用同一份测试集（含 $-10$ dB 到 $25$ dB 的全范围）评估。你会发现：窄范围训练的模型在高 SNR 测试时表现不输，但在低 SNR 测试时精度骤降——而宽范围训练的模型在全 SNR 下更稳健。这直接印证了 3.1 节关于训练集覆盖度的讨论。

**方向三：快拍数对 IQ-LSTM 的影响。** 对 IQ-LSTM 实验，分别测试 `N_snap = 64, 128, 256`（记得相应调整网络输入尺寸，框架里 `IQ_LSTM_Regressor` 的 LSTM 层对序列长度自动适配），比较三者的 RMSE。这个实验会让你直观感受到：快拍越多，LSTM 能积累的统计信息越丰富，精度越高；但快拍数翻倍，计算时间也大致翻倍，需要权衡。

**方向四：CM-CNN 与 IQ-LSTM 的横向对比。** 在相同的阵列配置和 SNR 范围下，分别训练两个模型，在同一测试集上对比。这不是要分出"谁更好"，而是理解两种设计路线各自的特点：CM 特征丢失了绝对相位信息但维度小、训练快；IQ 特征信息更完整但对快拍数敏感。在什么条件下两者差距大？在什么条件下差距小？这些观察比看一个抽象的结论要深刻得多。

每次调参，建议先改 `run_name`（比如 `exp03_cm_cnn_lowsnr`），再运行 `train.py`，训练完后运行 `eval.py`。按下面的格式把结果记下来：

| 实验名 | 特征 | 任务 | N\_snap | SNR 范围 | num\_train | 整体 RMSE | 备注 |
|---|---|---|---|---|---|---|---|
| exp01 | CM | 分类 | 256 | $[-5, 20]$ | 12000 | —— | 基准 |
| exp02 | IQ | 回归 | 128 | $[-5, 20]$ | 12000 | —— | |
| exp03 | CM | 分类 | 256 | $[-10, 20]$ | 12000 | —— | 宽 SNR |
| exp04 | CM | 分类 | 256 | $[-5, 20]$ | 30000 | —— | 更多数据 |

这张表会是你在第三章最有价值的学习产出之一。

---

## 3.7.7 小结

本节把前几节的内容整合为一个完整的四文件框架：`utils.py` 负责数据生成和特征提取，`models.py` 定义两种网络结构，`train.py` 驱动训练并保存检查点，`eval.py` 加载结果并与 MUSIC 基线对比。

框架的设计优先考虑可读性和可操作性：所有超参数集中在 `CONFIG` 字典里，每次实验改 `run_name` 避免覆盖历史结果，检查点里存储了完整的训练配置，让评估时不需要手动对齐参数。

跑通代码只是开始，真正的学习在于通过调参建立直觉：数据量、SNR 覆盖、快拍数、网络容量，这些因素各自怎样影响最终的 RMSE？答案不在本节的文字里，而在你自己跑出来的那张调参记录表里。

在调参的过程中，读者朋友们可能已经注意到一件事：`eval.py` 的对比图里，MUSIC 基线在高 SNR 下往往并不比深度学习方法差，有时反而更好；而在低 SNR 或极端快拍数条件下，深度学习的优势才会比较明显。这个观察并不是偶然的——它触及了一个更基础的问题：深度学习方法和经典方法，究竟各自擅长什么场景，在实际工程中该怎么选？这正是 3.8 节要系统回答的问题。
