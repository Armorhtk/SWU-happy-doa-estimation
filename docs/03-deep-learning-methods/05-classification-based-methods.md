---
id: deep-learning-classification-based-methods
title: 3.4 基于分类的DOA估计方法
slug: /deep-learning/classification-based-methods
---

# 3.4 基于分类的DOA估计方法

有了数据集，现在可以正式建立第一个 DOA 估计网络了。本节介绍的分类方法，是深度学习 DOA 估计中最直观、最容易上手的一条路，也是大多数入门论文的起点。把这一条路走清楚，后续的回归方法就会显得顺理成章。

---

## 3.4.1 分类的核心思想：把角度空间"格点化"

分类的思路一句话就能说清楚：把连续的角度范围切成若干个小格，每个格点是一个"类别"，让网络预测信号落在哪个格点上。

设角度范围是 $[q_{\min}, q_{\max}]$，格点间距（分辨率）是 $\Delta q$，则类别总数为：

$$
D = \frac{q_{\max} - q_{\min}}{\Delta q} + 1
$$

以覆盖 $[-60°, 60°]$、分辨率 $1°$ 为例，$D = 121$，对应 121 个类别。网络的最后一层输出 $D$ 个数值，经过激活函数后解读为各格点处"有信号"的置信度，训练时标签也是一个长度 $D$ 的向量。

这个格点化操作，把一个物理上连续的参数估计问题，转化成了一个机器学习中成熟的多标签分类问题。任务形式清晰，损失函数行为可预期，是分类方法容易训练、容易调试的根本原因。

当然，格点化带来了一个天花板：**真实 DOA 是连续的，而网络只能输出格点**。一个落在 $23.6°$ 的信号，网络最好的输出也只能是 $24°$（$1°$ 分辨率下）。精度上界由 $\Delta q$ 决定，想要更高精度就必须用更密的格点，输出维度 $D$ 随之增大。这个"网格失配"（grid mismatch）问题，是分类方法固有的局限，了解它，才能在与回归方法比较时做出理性的判断。

---

## 3.4.2 输出层设计：Softmax 还是 Sigmoid

3.2 节已经说明了单信源和多信源在输出层上的区别，这里把具体的设计逻辑再拎清楚，因为它直接决定了网络代码的写法。

**单信源**：整个 $D$ 个格点中有且仅有一个是"正确答案"，这是**单标签多分类**问题。输出层用 **Softmax** 激活，将 $D$ 个 logit 值转化为概率分布（总和为 1），每个格点的输出值代表"信号恰好来自该方向"的概率。训练目标是让正确格点的概率尽量接近 1，其余接近 0，损失函数用**交叉熵（CE）**：

$$
\mathcal{L}_{\text{CE}} = -\frac{1}{B}\sum_{k=1}^{B}\sum_{d=1}^{D} p_{kd} \log q_{kd}
$$

其中 $p_{kd}$ 是第 $k$ 个样本在第 $d$ 个类别上的真实标签（one-hot，即正确格点为 1，其余为 0），$q_{kd}$ 是 Softmax 输出的预测概率，$B$ 是批次大小。

推理时，取 Softmax 输出中值最大的格点作为预测结果：

$$
\hat{d} = \arg\max_{d \in \{1,\ldots,D\}} q_d, \quad \hat{\theta} = q_{\min} + (\hat{d} - 1) \cdot \Delta q
$$

**多信源（信源数固定为 $K$）**：$D$ 个格点中有 $K$ 个"正确答案"，这是**多标签分类**问题。此时不能再用 Softmax——Softmax 强制所有输出概率之和为 1，不适合多个标签同时为真的情形。取而代之的是 **Sigmoid** 激活：每个格点独立地判断"该方向有无信号"，输出值域 $(0, 1)$，代表该格点处存在信号的置信度，各格点之间相互独立，概率之和不必为 1。损失函数改用**二元交叉熵（BCE）**，对每个格点单独计算二分类损失后取平均：

$$
\mathcal{L}_{\text{BCE}} = -\frac{1}{B \cdot D}\sum_{k=1}^{B}\sum_{d=1}^{D}\left[t_{kd}\log o_{kd} + (1-t_{kd})\log(1-o_{kd})\right]
$$

其中 $t_{kd} \in \{0, 1\}$ 是真实的多热标签，$o_{kd}$ 是 Sigmoid 输出的置信度。

推理时，从 $D$ 个 Sigmoid 输出中选出置信度最高的 $K$ 个格点，对应的角度就是预测结果：

$$
\{\hat{d}_1, \cdots, \hat{d}_K\} = \text{top-}K_{d \in \{1,\ldots,D\}}\, o_d
$$

---

## 3.4.3 网络结构：以 CM-CNN 为例

结构的选择取决于输入的形态。对于协方差矩阵输入（形状 $(2, M, M)$ 的双通道实数矩阵），CNN 是最自然的选择——它能通过卷积层提取矩阵中的局部相关结构，比直接展平送入 MLP 效果更好。

下面给出一个清晰的 CM-CNN 分类网络实现，结构设计参照了相关文献的基本范式，同时保持代码的可读性和可修改性：

```python
import torch
import torch.nn as nn

class CM_CNN_Classifier(nn.Module):
    """
    基于协方差矩阵的 CNN 分类网络（CM-CNN）
    输入形状：(batch, 2, M, M)  —— 实部和虚部各一通道
    输出形状：(batch, D)        —— D 个格点的 logit 值
    """
    def __init__(self, M=8, D=121, num_sources=1):
        super().__init__()
        self.num_sources = num_sources

        # 特征提取：卷积模块
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(2, 32, kernel_size=3, padding=1),   # (B, 32, M, M)
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                               # (B, 32, M/2, M/2)

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # (B, 64, M/2, M/2)
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((2, 2)),                  # (B, 64, 2, 2)
        )

        # 分类头：全连接层
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 2 * 2, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, D),
            # 注意：这里不加激活函数，输出原始 logit
            # 单信源用 Softmax + CE，多信源用 Sigmoid + BCE
            # 激活函数在损失函数内部或推理时施加
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
```

几点设计说明：最后一层不加任何激活函数，输出"原始分值"（logit）而非概率。这是因为 PyTorch 的 `CrossEntropyLoss` 内部已经包含 Softmax 操作，`BCEWithLogitsLoss` 内部已经包含 Sigmoid，将激活放在损失函数外面在数值上更不稳定（浮点精度问题）。`AdaptiveAvgPool2d((2, 2))` 使得网络对不同的 $M$ 值具有一定适应性，无需根据阵元数修改网络结构。`Dropout(0.3)` 是防止过拟合的常见正则化手段，对小数据集尤其重要。

---

## 3.4.4 训练流程

有了网络，接下来是标准的训练循环。下面的代码直接复用 3.3 节生成的数据和 `DOADataset`：

```python
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

# ============================================================
# 准备数据
# ============================================================
# 沿用 3.3 节生成的 X_train, labels_train
# 这里以双信源分类任务为例

M, D_grid = 8, 121   # 格点数：[-60°, 60°]，步长 1°

dataset = DOADataset(
    X_train, labels_train,
    feature_type='cm', task='classification',
    theta_min=-60, theta_max=60, resolution=1.0
)

n_val = int(0.15 * len(dataset))
n_train = len(dataset) - n_val
train_set, val_set = random_split(dataset, [n_train, n_val],
                                  generator=torch.Generator().manual_seed(42))

train_loader = DataLoader(train_set, batch_size=64, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_set,   batch_size=64, shuffle=False, num_workers=0)

# ============================================================
# 实例化网络、损失函数、优化器
# ============================================================
num_sources = 2   # 双信源：Sigmoid + BCE
model = CM_CNN_Classifier(M=M, D=D_grid, num_sources=num_sources)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# 单信源用 CrossEntropyLoss，多信源用 BCEWithLogitsLoss
if num_sources == 1:
    criterion = nn.CrossEntropyLoss()
else:
    criterion = nn.BCEWithLogitsLoss()

optimizer = optim.Adam(model.parameters(), lr=1e-3)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# ============================================================
# 训练循环
# ============================================================
def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        # CrossEntropyLoss 期望整数标签（单信源）；
        # BCEWithLogitsLoss 期望浮点标签向量（多信源）
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(x)
    return total_loss / len(loader.dataset)

def val_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            total_loss += loss.item() * len(x)
    return total_loss / len(loader.dataset)

num_epochs = 40
best_val_loss = float('inf')

for epoch in range(1, num_epochs + 1):
    train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
    val_loss   = val_epoch(model, val_loader, criterion, device)
    scheduler.step()

    # 保存验证集上最优的模型
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_cm_cnn.pth')

    if epoch % 5 == 0:
        print(f"Epoch {epoch:3d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
```

这段训练代码是所有深度学习 DOA 实验的骨架。几乎每一个后续实验（回归、不同网络结构、不同输入特征）都只需替换其中的 `model`、`criterion` 和数据集参数，外层循环逻辑保持不变。

---

## 3.4.5 推理与性能评估

训练完成后，加载最优模型，在测试集上做推理并评估 RMSE。

```python
def predict_classification(model, x_tensor, num_sources, D,
                           theta_min=-60, resolution=1.0):
    """
    分类网络推理：从 logit 向量还原角度预测值
    返回：预测角度数组，形状 (batch, num_sources)，单位度
    """
    model.eval()
    with torch.no_grad():
        logits = model(x_tensor)

    if num_sources == 1:
        # 单信源：取 argmax，转换为角度
        pred_idx = torch.argmax(logits, dim=1).cpu().numpy()
        pred_deg = theta_min + pred_idx * resolution
        return pred_deg[:, np.newaxis]   # (batch, 1)
    else:
        # 多信源：取 top-K 置信度对应的格点
        probs = torch.sigmoid(logits).cpu().numpy()
        batch_size = probs.shape[0]
        pred_deg = np.zeros((batch_size, num_sources))
        for i in range(batch_size):
            top_idx = np.argsort(probs[i])[-num_sources:]   # 最大的 K 个
            top_idx = np.sort(top_idx)                       # 按格点升序排列
            pred_deg[i] = theta_min + top_idx * resolution
        return pred_deg   # (batch, K)

# 在测试集上评估
model.load_state_dict(torch.load('best_cm_cnn.pth', map_location=device))

# 构建测试集
X_test, labels_test, _ = generate_dataset(
    num_samples=2000, K=2, M=M, N=256,
    snr_range_dB=(-5, 20), seed=999
)
test_dataset = DOADataset(X_test, labels_test,
                          feature_type='cm', task='classification',
                          theta_min=-60, theta_max=60, resolution=1.0)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

all_preds, all_labels = [], []
for x, y in test_loader:
    preds = predict_classification(
        model, x.to(device), num_sources=2, D=D_grid,
        theta_min=-60, resolution=1.0
    )
    all_preds.append(preds)
    # 从 multi-hot 向量还原角度标签
    y_np = y.numpy()
    label_deg = np.array([
        -60 + np.where(y_np[i] > 0.5)[0] * 1.0
        for i in range(len(y_np))
    ])
    all_labels.append(label_deg)

all_preds  = np.concatenate(all_preds,  axis=0)  # (2000, 2)
all_labels = np.concatenate(all_labels, axis=0)  # (2000, 2)

# 计算 RMSE（假设预测和标签均已按升序排列）
rmse = np.sqrt(np.mean((all_preds - all_labels) ** 2))
print(f"测试集 RMSE：{rmse:.3f} 度")
```

这里有一个细节值得注意：评估 RMSE 时，预测角度和真实角度都要**按升序排列后再逐一配对**，这与 3.2 节讨论配对问题的结论一致。如果顺序不一致，同一个样本的"第一个预测"和"第一个真实标签"可能根本不是同一个信源，计算出的误差会偏大。

---

## 3.4.6 分类方法的性能边界与局限

学会了用，还要知道边界在哪里。

**精度上限由格点间距决定。** 这是分类方法最根本的约束。以 $1°$ 分辨率为例，即便网络完美地预测出了正确格点，最大误差也有 $\pm 0.5°$，RMSE 理论下限约为 $0.29°$（$1°$ 均匀分布的标准差）。要打破这个上限，要么细化格点（但 $D$ 和训练难度同步增加），要么在格点预测结果的基础上再做插值（比如对周边格点的置信度做加权平均，估计一个亚格点的角度值）。

格点内插的最简单形式是对 Sigmoid/Softmax 输出做加权质心（centroid）计算：

```python
def centroid_refine(probs, theta_grid, window=3):
    """
    对概率最大峰值做邻域加权质心插值，获得亚格点估计
    probs      : (D,) 概率向量
    theta_grid : (D,) 格点角度值
    window     : 质心计算的邻域宽度（格点数，取奇数）
    """
    peak_idx = np.argmax(probs)
    half = window // 2
    lo = max(0, peak_idx - half)
    hi = min(len(probs), peak_idx + half + 1)
    local_probs = probs[lo:hi]
    local_angles = theta_grid[lo:hi]
    return np.sum(local_probs * local_angles) / (np.sum(local_probs) + 1e-12)
```

这个简单的插值往往能将 RMSE 降低 $20\%$—$40\%$，代价几乎为零，是分类方法的常见"后处理"技巧。

**多信源时的配对敏感性。** top-K 选峰在信源角度相近时可能选错——两个真实 DOA 相差很小，它们对应的格点置信度峰值可能发生混叠，网络难以将它们分开，导致估计失败。这个问题本质上是分类框架的分辨率约束，与格点间距和角度间隔之间的关系直接相关。通常建议信源角度间隔大于 $3 \sim 5$ 个格点宽度，分类方法才能可靠工作。

---

## 3.4.7 小结

本节完整地走了一遍基于分类的 DOA 估计：从任务定义、输出层设计（Softmax/Sigmoid），到网络搭建（CM-CNN）、训练循环、推理解码，再到 RMSE 评估和精度上限分析。

分类方法的核心优势在于任务形式成熟、训练过程稳定、标签设计简洁。单信源用 Softmax 加交叉熵，多信源换成 Sigmoid 加二元交叉熵，推理时分别用 argmax 和 top-K 选峰——改动量极少，逻辑一脉相承。主要局限是网格失配带来的精度天花板，但可以通过亚格点插值缓解。

掌握了分类这条路，3.5 节的直接角度回归就会显得更有针对性：它正是为了克服分类的精度上限而提出的。我们来看，当输出层从"预测格点"变成"直接输出角度值"时，网络的设计和训练会发生哪些变化。