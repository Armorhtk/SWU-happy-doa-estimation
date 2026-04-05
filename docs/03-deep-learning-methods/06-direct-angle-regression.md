---
id: deep-learning-direct-angle-regression
title: 3.5 基于回归的DOA估计方法（一）：直接角度回归
slug: /deep-learning/direct-angle-regression
---

# 3.5 基于回归的DOA估计方法（一）：直接角度回归

3.4 节的分类方法有一个显而易见的天花板：无论格点再密，预测结果都只能落在某个格点上，真实 DOA 是连续的，网格失配误差客观存在。直接角度回归正是为了突破这个天花板而生的。它的思路更直接：**不再离散化，让网络直接输出角度的数值**。

---

## 3.5.1 任务定义：从"选格点"变成"预测数值"

分类任务中，网络的输出是一个 $D$ 维的置信度向量，每一维对应一个格点。直接回归彻底抛弃了格点的概念：对于 $K$ 个信源，网络的最后一层直接输出 $K$ 个实数，就是 $K$ 个信源的角度预测值。

这看起来非常自然，但带来两个需要处理的工程问题。

**问题一：输出范围的归一化。** 角度值通常在 $[-90°, 90°]$ 这样有范围的区间内，而神经网络全连接层的原始输出范围是 $(-\infty, +\infty)$。如果不加约束，网络可能输出 $300°$ 或 $-500°$ 这样毫无意义的值，梯度下降过程也会因输出尺度不匹配而不稳定。解决方法是在输出层加一个 **Tanh 激活函数**，将输出压缩到 $(-1, 1)$ 区间，同时将训练标签也归一化到相同区间，训练后推理时再反归一化还原为角度值。

具体映射关系是：

$$
\tilde{\theta} = \frac{2(\theta - \theta_{\min})}{\theta_{\max} - \theta_{\min}} - 1 \in (-1, 1)
$$

反归一化时：

$$
\hat{\theta} = \frac{(\hat{\tilde{\theta}} + 1)}{2} \cdot (\theta_{\max} - \theta_{\min}) + \theta_{\min}
$$

**问题二：多信源的配对歧义。** 单信源时没有这个问题，网络只输出一个值就够了。但当 $K \geq 2$ 时，网络输出 $K$ 个角度值，它们与真实 DOA 之间存在哪种对应关系？举个例子：真实 DOA 是 $[10°, 30°]$，而某次网络输出了 $[29.5°, 10.2°]$——顺序反了，但其实预测得很准。如果不处理配对问题，直接计算 $(29.5 - 10)^2 + (10.2 - 30)^2$ 得到的损失会非常大，梯度方向完全错误，网络无法学习。

最直接的处理方法是：**对训练标签和网络输出都强制按升序排列**。训练时标签已经是升序的（3.3 节的 `angles_to_regression_label` 就做了 `np.sort`），网络输出也在计算损失之前按升序排列。这样保证了"第 $k$ 个输出"始终与"第 $k$ 小的真实 DOA"配对。这个约定的代价是隐式地要求网络的输出具有单调性，实践证明在多数场景下这是可以被满足的。

---

## 3.5.2 网络结构与输出层

与分类网络相比，回归网络只需改动最后一层：把 $D$ 维的 logit 输出改为 $K$ 维的 Tanh 输出。特征提取的主干部分完全可以沿用 CM-CNN 的结构：

```python
import torch
import torch.nn as nn

class CM_CNN_Regressor(nn.Module):
    """
    基于协方差矩阵的 CNN 直接角度回归网络
    输入形状：(batch, 2, M, M)
    输出形状：(batch, K)，值域 (-1, 1)，对应归一化角度
    """
    def __init__(self, M=8, K=2):
        super().__init__()

        # 特征提取主干：与分类网络完全相同
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

        # 回归头：输出 K 个归一化角度值
        self.regressor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 2 * 2, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, K),
            nn.Tanh(),          # 输出限制在 (-1, 1)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.regressor(x)
        # 对输出排序，保证升序（处理配对歧义）
        x, _ = torch.sort(x, dim=1)
        return x
```

注意 `forward` 末尾的 `torch.sort`——它在每次前向传播时都把 $K$ 个输出强制升序排列。这个操作是可微的（排序本身的梯度通过索引传回），所以不影响正常的反向传播，可以放心使用。

---

## 3.5.3 损失函数：MSE

回归任务的损失函数是**均方误差（MSE）**：

$$
\mathcal{L}_{\text{MSE}} = \frac{1}{B \cdot K} \sum_{i=1}^{B} \sum_{k=1}^{K} \left(\hat{\tilde{\theta}}_k^{(i)} - \tilde{\theta}_k^{(i)}\right)^2
$$

其中 $\hat{\tilde{\theta}}_k^{(i)}$ 是第 $i$ 个样本第 $k$ 个信源的归一化预测值（网络输出），$\tilde{\theta}_k^{(i)}$ 是对应的归一化真实标签。PyTorch 的 `nn.MSELoss()` 直接实现了这个公式。

训练循环与 3.4 节的分类网络几乎完全相同，差别只在于 `criterion` 换成了 `nn.MSELoss()`，数据集的 `task` 参数改为 `'regression'`：

```python
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

M, K = 8, 2

# 沿用 3.3 节的 generate_dataset 和 DOADataset
dataset = DOADataset(
    X_train, labels_train,
    feature_type='cm', task='regression',
    theta_min=-60, theta_max=60
)

n_val   = int(0.15 * len(dataset))
n_train = len(dataset) - n_val
train_set, val_set = random_split(dataset, [n_train, n_val],
                                  generator=torch.Generator().manual_seed(42))
train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
val_loader   = DataLoader(val_set,   batch_size=64, shuffle=False)

model     = CM_CNN_Regressor(M=M, K=K).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# 训练循环与 3.4 节相同，此处省略重复代码
# 只需将 criterion 替换为 nn.MSELoss() 即可
```

---

## 3.5.4 推理与反归一化

网络输出是归一化到 $(-1, 1)$ 的角度值，推理后需要反归一化还原为真实角度：

```python
def predict_regression(model, x_tensor, theta_min=-60, theta_max=60):
    """
    回归网络推理：从归一化输出还原角度（度）
    返回：预测角度，形状 (batch, K)
    """
    model.eval()
    with torch.no_grad():
        normalized = model(x_tensor).cpu().numpy()  # (batch, K)，值域 (-1, 1)

    # 反归一化
    pred_deg = (normalized + 1) / 2 * (theta_max - theta_min) + theta_min
    return pred_deg   # (batch, K)，单位度
```

RMSE 的计算与 3.4 节相同：预测角度和真实角度对齐配对后取均方根。

---

## 3.5.5 直接回归的优势与局限

**优势：精度无上限。** 这是直接回归最根本的优势。只要网络足够强、训练数据足够多，理论上预测精度可以任意接近真实值，不受格点间距的约束。在高信噪比、训练数据充足的条件下，回归方法的 RMSE 往往能明显低于相同结构的分类方法。

**局限：收敛更难，对数据量要求更高。** 分类任务的损失函数有明确的类别结构，网络学习的目标是"把对的类别推高、错的类别压低"，方向性非常清晰。回归任务的 MSE 损失在角度空间中是连续的，网络需要精确学习每一个数值，早期训练时梯度的方向指引相对弱，容易出现收敛慢或局部最优的情况。实践中，通常需要比分类任务更大的数据集（至少多 $1 \sim 2$ 倍）、更细心的学习率调度，才能达到理想的收敛效果。

**局限：信源数必须固定。** 网络的输出维度 $K$ 在设计时就已固定，一旦训练完成，就只能用于 $K$ 个信源的场景。更换信源数需要重新设计网络和重新训练。这一点是直接回归相比分类（或下一节的伪谱回归）最明显的灵活性不足。

---

## 3.5.6 小结

直接角度回归把 DOA 估计还原为最自然的数值预测任务：输出层加 Tanh 约束输出范围，标签归一化到 $(-1, 1)$，用 MSE 损失训练，推理后反归一化还原角度。多信源时对输出强制升序排列处理配对问题。相比分类，精度上限消失了，但训练难度有所上升，且信源数必须预先确定。

对于精度要求高、信源数固定已知的场景，直接回归是三种任务形式中最值得优先考虑的一种。下一节介绍的伪谱回归，则解决了信源数不固定这个痛点。

