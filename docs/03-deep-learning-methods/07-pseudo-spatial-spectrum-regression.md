---
id: deep-learning-pseudo-spatial-spectrum-regression
title: 3.6 基于回归的DOA估计方法（二）：伪空间谱回归
slug: /deep-learning/pseudo-spatial-spectrum-regression
---

# 3.6 基于回归的DOA估计方法（二）：伪空间谱回归

分类方法受制于格点，直接回归要求信源数已知。有没有一种方式，既能突破格点精度天花板，又能自然地适应信源数的变化？伪空间谱回归给出了一个优雅的答案：**让网络的输出不是角度，而是一条空间谱曲线**——在真实 DOA 处出现峰值，其他地方接近零。最后从这条曲线上做峰值检测，完成角度定位。

---

## 3.6.1 核心思路：输出一条谱，信源数由峰值决定

伪谱回归的任务形式可以这样理解：网络学的是"给我一段阵列数据，你告诉我空间里哪些方向有信号"。它的输出是一个长度为 $D$ 的向量 $\hat{\mathbf{s}} \in \mathbb{R}^D$，对应 $D$ 个预设角度格点上的"谱值"。真实 DOA 处的谱值应当高，其他位置应当低。

这与 MUSIC 伪谱在概念上非常接近——都是在角度空间上描绘一条曲线，通过峰值定位方向。区别在于：MUSIC 伪谱是从阵列数据出发，通过子空间分解的数学推导得到的；伪谱回归是通过神经网络学习，从数据直接端对端地映射出一条谱形状。

信源数的问题在这里被优雅地绕开了：网络的输出维度始终是 $D$，不依赖信源数。训练时，不同信源数的样本可以混在一起训练同一个网络；推理时，对输出谱做峰值检测，检测到几个峰就是几个信源，完全自适应。

---

## 3.6.2 参考谱的构造：训练目标长什么样

伪谱回归需要为每个训练样本构造一条"参考谱"作为训练目标。最常用的做法是在真实 DOA 位置放置高斯形状的峰值：

$$
f_{\text{ref}}(\theta_d) = \sum_{k=1}^{K} \exp\!\left(-\frac{(\theta_d - \theta_k)^2}{2\sigma_G^2}\right)
$$

其中 $\theta_d$ 是第 $d$ 个格点对应的角度，$\sigma_G$ 控制高斯峰的宽度，$K$ 个信源在各自的真实 DOA 处各产生一个峰，叠加后就是参考谱。

$\sigma_G$ 的选取是一个值得认真对待的超参数：

- $\sigma_G$ 太小（接近格点间距 $\Delta q$），峰太窄，网络很难精确学到峰值的位置，收敛困难；
- $\sigma_G$ 太大，峰太宽，信源间距较小时两个峰会发生混叠，网络学到的是一个宽峰而非两个独立峰，检测失败。

经验上，$\sigma_G$ 取 $2 \sim 5$ 个格点间距是合理的起点（比如格点分辨率 $1°$，则 $\sigma_G = 2° \sim 5°$），可根据任务的最小信源间隔约束适当调整。

参考谱的值域在 $(0, 1]$ 之间（高斯函数的取值范围），适合与网络输出层的 Sigmoid 激活配合使用，让网络输出也落在 $(0, 1)$ 区间内，再用 MSE 损失来最小化输出谱与参考谱之间的逐点差距。

```python
import numpy as np

def make_reference_spectrum(thetas, theta_min=-60, theta_max=60,
                             resolution=1.0, sigma_G=3.0):
    """
    为给定角度列表构造高斯参考谱
    参数：
        thetas     : 真实 DOA 列表，单位度
        theta_min  : 角度范围下限
        theta_max  : 角度范围上限
        resolution : 格点间距（度）
        sigma_G    : 高斯峰宽度（度）
    返回：
        ref_spec   : 参考谱，形状 (D,)，值域 [0, 1]
    """
    grid = np.arange(theta_min, theta_max + resolution * 0.5, resolution)
    D = len(grid)
    ref_spec = np.zeros(D, dtype=np.float32)
    for th in thetas:
        ref_spec += np.exp(-0.5 * ((grid - th) / sigma_G) ** 2)
    # 截断到 [0, 1]（多峰叠加时可能超过 1）
    return np.clip(ref_spec, 0.0, 1.0)
```

---

## 3.6.3 网络结构与输出层

伪谱回归的网络主干与前两节相同，只有输出层不同：输出维度从 $K$（直接回归）或最后一层分类 logit（分类），变成 $D$ 维的谱向量，加 **Sigmoid** 激活将每个格点的输出约束到 $(0, 1)$：

```python
class CM_CNN_SpectrumRegressor(nn.Module):
    """
    基于协方差矩阵的 CNN 伪谱回归网络
    输入形状：(batch, 2, M, M)
    输出形状：(batch, D)，值域 (0, 1)，对应各格点处的谱值置信度
    """
    def __init__(self, M=8, D=121):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(2, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((2, 2)),
        )

        self.spectrum_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 2 * 2, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, D),
            nn.Sigmoid(),   # 输出谱值，范围 (0, 1)
        )

    def forward(self, x):
        x = self.features(x)
        return self.spectrum_head(x)
```

---

## 3.6.4 标签构造与训练

训练时，标签不再是角度向量或 one-hot 向量，而是 3.6.2 节构造的参考谱 $\mathbf{f}_{\text{ref}} \in \mathbb{R}^D$。`DOADataset` 需要新增一种 `task='spectrum'` 的处理分支：

```python
# 在 DOADataset.__init__ 中新增 spectrum 分支
if task == 'spectrum':
    sigma_G = kwargs.get('sigma_G', 3.0)
    self.labels = np.stack([
        make_reference_spectrum(
            labels_deg[i], theta_min, theta_max, resolution, sigma_G)
        for i in range(len(labels_deg))
    ])
```

损失函数使用 `nn.MSELoss()`，逐格点计算预测谱与参考谱之间的均方差：

$$
\mathcal{L}_{\text{spec}} = \frac{1}{B \cdot D} \sum_{i=1}^{B} \sum_{d=1}^{D} \left(\hat{s}_{id} - f_{\text{ref}, id}\right)^2
$$

训练循环与前两节完全一致，只需替换 `criterion` 和 `dataset`：

```python
model     = CM_CNN_SpectrumRegressor(M=8, D=121).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
# 其余训练代码与 3.4、3.5 节相同
```

---

## 3.6.5 推理：从输出谱提取 DOA

推理阶段，网络输出 $D$ 维谱向量后，需要做峰值检测来获得 DOA 估计值。这一步的实现有几个值得注意的地方：

```python
from scipy.signal import find_peaks

def predict_spectrum(model, x_tensor, theta_min=-60, resolution=1.0,
                     height_threshold=0.3, min_distance=3):
    """
    伪谱回归推理：输出谱 → 峰值检测 → DOA 估计
    参数：
        height_threshold : 峰值高度阈值，低于此值的峰忽略
        min_distance     : 两个峰之间的最小格点间距（抑制重复峰）
    返回：
        doas_list : 每个样本的预测 DOA 列表（信源数自适应）
    """
    model.eval()
    with torch.no_grad():
        spectra = model(x_tensor).cpu().numpy()  # (batch, D)

    grid = np.arange(0, spectra.shape[1]) * resolution + theta_min
    doas_list = []

    for spec in spectra:
        peaks, props = find_peaks(
            spec,
            height=height_threshold,
            distance=min_distance
        )
        if len(peaks) == 0:
            # 无峰时取最大值格点
            peaks = [np.argmax(spec)]
        doas = np.sort(grid[peaks])
        doas_list.append(doas)

    return doas_list
```

这里有三个超参数需要根据场景调整：`height_threshold` 控制哪些"凸起"才算真正的峰（过低会有噪声伪峰，过高会漏掉弱信源）；`min_distance` 控制两个峰之间的最小格点数（过小会把一个宽峰识别成两个峰）；两者共同决定了伪谱峰值检测的分辨率和灵敏度。实际使用时，建议先在验证集上网格搜索这两个参数的最优值。

---

## 3.6.6 三种方法的综合对比

至此，三种 DOA 估计任务形式都已介绍完毕。把它们放在一起做一次清晰的横向对比，有助于在实际工程中做出合理的选型判断。

| 维度 | 分类 | 直接角度回归 | 伪谱回归 |
|---|---|---|---|
| **精度上限** | 受格点间距约束 | 无上限（连续估计） | 无上限（峰值可插值） |
| **信源数是否需要预知** | 多信源需知道 $K$（top-K 选峰） | 必须预先固定 $K$ | 不需要，峰值自适应 |
| **训练难度** | 最低，收敛稳定 | 中等，需处理配对 | 中等，需调 $\sigma_G$ |
| **标签设计** | one-hot / multi-hot | 归一化角度向量 | 高斯参考谱 |
| **推理结果** | 离散格点 | 连续角度值 | 连续（峰值可插值） |
| **推理后处理** | argmax / top-K | 反归一化 | 峰值检测（含超参数）|
| **与 MUSIC 谱的类比** | 无 | 无 | 直接对应 |
| **适用起点** | 入门首选，快速验证 | 信源数固定、追求精度 | 信源数可变、可视化友好 |

从这张表可以看到，三种方法各有侧重、彼此互补。分类入门最简单，是调通整个训练流程的最佳起点；直接回归追求最高连续精度，在固定信源数场景中表现往往最优；伪谱回归在灵活性和可解释性上有独特优势，尤其适合需要与 MUSIC 伪谱进行可视化对比、或信源数在推理时不确定的场景。

---

## 3.6.7 小结

伪谱回归把 DOA 估计转化为"学一条空间谱曲线"的任务：网络输出 $D$ 维谱向量（Sigmoid 激活，值域 $(0,1)$），训练目标是高斯参考谱，损失函数用 MSE，推理时通过峰值检测定位 DOA。最大的特点是信源数自适应——网络结构和训练过程都不依赖具体的信源数，只在推理的峰值检测步骤中动态确定。代价是引入了若干峰值检测超参数（高度阈值、最小间距），需要在验证集上调校。

至此，第三章关于任务定义、数据集构建和三种基本任务形式的核心内容已经完整。3.7 节将把这些内容落地为两个最小可运行的完整代码示例——一个分类、一个回归，帮助读者直接从概念跨入可以运行的实验。