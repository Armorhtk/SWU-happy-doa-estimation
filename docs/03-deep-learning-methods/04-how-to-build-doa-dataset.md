---
id: deep-learning-how-to-build-doa-dataset
title: 3.3 如何构建DOA数据集
slug: /deep-learning/how-to-build-doa-dataset
---

# 3.3 如何构建DOA数据集

深度学习的能力来自数据。在讨论网络结构和训练技巧之前，有一个更基础的问题必须首先回答：数据从哪里来，长什么样，最终要处理成什么格式才能送进网络？

对于 DOA 估计来说，这个问题有一个让初学者感到惊喜的答案：我们完全不依赖真实采集的硬件数据，而是基于第一章建立的阵列观测模型，用纯仿真的方式按需生成任意数量的训练样本。这既省去了昂贵的实测系统，也使得对信噪比、信源数、角度分布等各种条件的精确控制成为可能。

本节的行文顺序固定为三步：先讲如何用仿真生成原始数据，再讲数据的形态与结构，最后讲如何把原始数据处理成网络可以直接接受的输入格式。每一步都有可运行的代码配合说明。

---

## 3.3.1 生成数据：从物理模型到仿真样本

回顾第一章的核心观测模型。$M$ 阵元 ULA 在 $N$ 个快拍时刻采集到的数据矩阵为：

$$
\mathbf{X} = \mathbf{A}(\boldsymbol{\theta})\,\mathbf{S} + \mathbf{N} \in \mathbb{C}^{M \times N}
$$

其中 $\mathbf{A}(\boldsymbol{\theta}) = [\mathbf{a}(\theta_1), \cdots, \mathbf{a}(\theta_K)]$ 是 $M \times K$ 的阵列流形矩阵，$\mathbf{S} \in \mathbb{C}^{K \times N}$ 是信号矩阵，$\mathbf{N} \in \mathbb{C}^{M \times N}$ 是加性高斯白噪声矩阵。

这个公式本身就是一个数据生成器。只要确定了角度组合 $\boldsymbol{\theta}$、信噪比 SNR 和快拍数 $N$，就能按下述步骤产生一个训练样本：

**第一步**：随机采样角度。从预设的角度范围（比如 $[-60°, 60°]$）中随机抽取 $K$ 个角度，作为本样本的真实 DOA，同时记录下来作为标签。

**第二步**：构造阵列流形矩阵。根据 ULA 导向矢量公式，把 $K$ 个角度对应的导向矢量并排排列，得到 $\mathbf{A} \in \mathbb{C}^{M \times K}$。

**第三步**：生成信号矩阵和噪声矩阵。$K$ 个信号源各自生成复高斯随机信号，信号功率由 SNR 决定；噪声矩阵是独立同分布的复高斯白噪声。

**第四步**：合成观测矩阵。按公式 $\mathbf{X} = \mathbf{A}\mathbf{S} + \mathbf{N}$ 计算阵列观测数据。

以下是单个样本的完整生成代码，它直接复用了第一、二章建立的仿真框架：

```python
import numpy as np

def steering_vector(theta_deg, M, d=0.5):
    """ULA 导向矢量"""
    theta = np.deg2rad(theta_deg)
    m = np.arange(M)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * m)

def generate_sample(thetas, M, N, snr_dB, d=0.5, rng=None):
    """
    生成单个 DOA 仿真样本
    参数：
        thetas  : 信源角度列表，单位度，如 [20.0, -35.0]
        M       : 阵元数
        N       : 快拍数
        snr_dB  : 信噪比（dB），每个信源功率相同
        d       : 阵元间距（归一化波长）
        rng     : numpy 随机数生成器（可复现时传入）
    返回：
        X       : 阵列观测矩阵，形状 (M, N)，复数
    """
    if rng is None:
        rng = np.random.default_rng()

    K = len(thetas)
    sigma2 = 1.0                              # 噪声功率固定为 1
    sig_pow = 10 ** (snr_dB / 10) * sigma2   # 每个信源信号功率

    # 阵列流形矩阵 (M, K)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas])

    # 复高斯信号矩阵 (K, N)，每个信源等功率
    S = np.sqrt(sig_pow / 2) * (
        rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N))
    )

    # 复高斯白噪声矩阵 (M, N)
    noise = np.sqrt(sigma2 / 2) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
    )

    X = A @ S + noise  # (M, N)
    return X
```

这段代码不到 30 行，却是整个数据集的核心引擎。只需在外层循环里不断改变 `thetas`、`snr_dB` 和随机种子，就能生成任意数量的独立样本。

---

## 3.3.2 数据的形态：一个样本长什么样

弄清楚原始数据的结构，是后续一切处理的起点。我们逐层来看。

**原始观测矩阵**：一个仿真样本的原始形态是 $\mathbf{X} \in \mathbb{C}^{M \times N}$——一个复数矩阵，行对应阵元，列对应时间快拍。对于常见配置（$M=8$，$N=512$），每个样本是一个 $8 \times 512$ 的复数数组，其中每个元素都有实部和虚部两个分量。

**标签**：与 $\mathbf{X}$ 对应的标签，是生成这次样本时使用的真实角度 $\boldsymbol{\theta} = [\theta_1, \cdots, \theta_K]$。标签的具体格式取决于任务类型（分类还是回归，见 3.2.3 节），但原始的角度值是最基础的记录。

**数据集结构**：把大量样本堆叠起来，整个训练集的观测数据就是一个形状为 $(\text{num\_samples}, M, N)$ 的三维复数数组，对应的标签是形状为 $(\text{num\_samples}, K)$（回归）或 $(\text{num\_samples}, D)$（分类）的二维实数数组。

理解这个形态，后面所有特征处理都是在这个基础上进行变换，不会有新的"黑箱"。

---

## 3.3.3 角度采样策略：让训练集覆盖场景

角度如何采样，直接影响训练集的分布质量，进而影响网络的泛化能力。有几点经验性的原则值得说明。

**均匀覆盖角度范围。** 最基本的做法是在目标角度范围内均匀随机采样。以单信源为例，如果覆盖范围是 $[-60°, 60°]$，可以直接用 `rng.uniform(-60, 60)` 采样。对多信源，为避免角度过于拥挤，通常加入最小角度间隔约束——比如任意两个信源角度之差不小于 $3°$ 到 $5°$，否则重新采样。

**混合多种 SNR。** 仅在单一 SNR 下训练的网络，面对不同 SNR 的测试数据时往往泛化不佳。实践中通常在宽泛的 SNR 范围内（如 $-10$ dB 到 $20$ dB）均匀或随机采样，使同一个网络能适应不同噪声条件。

**训练集、验证集、测试集的划分。** 一个规范的实验流程将数据集分为三部分：训练集用于更新网络参数，验证集（通常占总样本 10%~20%）用于训练过程中监控是否过拟合、决定何时停止训练，测试集在训练全程不参与任何决策、仅在最后一次性评估最终性能。测试集的 SNR 设置可以包含训练集没有覆盖的值（如专门的"外推泛化"实验），以检验网络的泛化边界。

下面是一个批量生成训练集的函数，处理了角度随机采样、SNR 随机化和多信源间隔约束：

```python
def sample_angles(K, theta_min, theta_max, min_sep, rng):
    """
    随机采样 K 个角度，保证任意两个角度间隔不小于 min_sep 度
    """
    for _ in range(1000):   # 最多尝试 1000 次
        thetas = np.sort(rng.uniform(theta_min, theta_max, K))
        if K == 1 or np.min(np.diff(thetas)) >= min_sep:
            return thetas
    raise RuntimeError("无法在给定约束下采样到合法角度组合，请放宽条件")

def generate_dataset(num_samples, K, M, N, snr_range_dB,
                     theta_min=-60, theta_max=60, min_sep=5, d=0.5, seed=0):
    """
    生成 DOA 仿真数据集
    返回：
        X_data   : 原始观测矩阵，形状 (num_samples, M, N)，复数
        labels   : 真实角度，形状 (num_samples, K)，单位度
        snrs     : 每个样本的 SNR（dB），形状 (num_samples,)
    """
    rng = np.random.default_rng(seed)
    X_data = np.zeros((num_samples, M, N), dtype=complex)
    labels = np.zeros((num_samples, K))
    snrs   = np.zeros(num_samples)

    for i in range(num_samples):
        thetas = sample_angles(K, theta_min, theta_max, min_sep, rng)
        snr = rng.uniform(snr_range_dB[0], snr_range_dB[1])
        X_data[i] = generate_sample(thetas, M, N, snr, d, rng)
        labels[i] = thetas
        snrs[i]   = snr

    return X_data, labels, snrs

# 示例：生成 10000 个双信源训练样本
X_train, labels_train, snrs_train = generate_dataset(
    num_samples=10000, K=2, M=8, N=256,
    snr_range_dB=(-5, 20), theta_min=-60, theta_max=60,
    min_sep=5, seed=42
)
print(f"X_train 形状: {X_train.shape}")       # (10000, 8, 256)
print(f"labels_train 形状: {labels_train.shape}")  # (10000, 2)
```

运行后，`X_train` 就是 10000 个样本的原始观测矩阵堆叠，每个样本是 $8 \times 256$ 的复数矩阵，`labels_train` 对应地记录了每个样本的真实双 DOA。

---

## 3.3.4 处理成网络输入：CM 特征和 IQ 特征

有了原始观测矩阵 `X_data`，接下来是最关键的一步：把它变换成网络真正接受的实数张量形式。这里分别介绍协方差矩阵（CM）和 IQ 两种处理路线。

### 协方差矩阵输入（CM 特征）

第一步，从观测矩阵 $\mathbf{X} \in \mathbb{C}^{M \times N}$ 计算样本协方差矩阵：

$$
\hat{\mathbf{R}} = \frac{1}{N}\mathbf{X}\mathbf{X}^H \in \mathbb{C}^{M \times M}
$$

$\hat{\mathbf{R}}$ 是 Hermitian 矩阵，复数，形状 $M \times M$。

第二步，把 $\hat{\mathbf{R}}$ 变换成实数张量，送入网络。最常用的做法是将实部和虚部分别作为两个通道，拼成形状 $(2, M, M)$ 的三维张量：

```python
def X_to_cm_feature(X):
    """
    从原始观测矩阵计算协方差矩阵特征（双通道实数格式）
    输入：X，形状 (M, N)，复数
    输出：feature，形状 (2, M, M)，实数
          第 0 通道为实部，第 1 通道为虚部
    """
    M, N = X.shape
    R_hat = (X @ X.conj().T) / N         # (M, M)，复数
    feature = np.stack([R_hat.real, R_hat.imag], axis=0)  # (2, M, M)
    return feature.astype(np.float32)

def build_cm_dataset(X_data):
    """
    批量处理，X_data 形状 (num_samples, M, N)
    返回形状 (num_samples, 2, M, M) 的实数数组
    """
    return np.stack([X_to_cm_feature(X_data[i]) for i in range(len(X_data))])
```

如果使用的是 MLP 而不是 CNN，还需要进一步将 $(2, M, M)$ 的矩阵展开成一维向量。因为 $\hat{\mathbf{R}}$ 是 Hermitian 矩阵，上下三角包含冗余信息，只取下三角部分（$M(M+1)/2$ 个复数，即 $M(M+1)$ 个实数）也是常见的做法，可以将输入维度减半：

```python
def cm_to_vector(R_hat):
    """提取协方差矩阵下三角（含对角），展平为实数向量"""
    M = R_hat.shape[0]
    idx = np.tril_indices(M)
    lower = R_hat[idx]           # 下三角元素，复数
    return np.concatenate([lower.real, lower.imag]).astype(np.float32)
```

### IQ 数据输入

IQ 路线更直接：不计算协方差矩阵，而是把原始观测矩阵的实部和虚部分开，拼成 $(2M, N)$ 的实数矩阵：

$$
\mathbf{M}_{\text{IQ}} = \begin{bmatrix} \text{Re}(\mathbf{X}) \\ \text{Im}(\mathbf{X}) \end{bmatrix} \in \mathbb{R}^{2M \times N}
$$

代码很简洁：

```python
def X_to_iq_feature(X):
    """
    从原始观测矩阵提取 IQ 特征
    输入：X，形状 (M, N)，复数
    输出：feature，形状 (2M, N)，实数
    """
    return np.concatenate([X.real, X.imag], axis=0).astype(np.float32)

def build_iq_dataset(X_data):
    """
    批量处理，X_data 形状 (num_samples, M, N)
    返回形状 (num_samples, 2*M, N) 的实数数组
    """
    return np.stack([X_to_iq_feature(X_data[i]) for i in range(len(X_data))])
```

如果送入 CNN（把 $(2M, N)$ 当作二维特征图），直接用上面的结果；如果网络接受的是带通道维度的格式（如 PyTorch 的 Conv2d 期望 $(C, H, W)$），可以在最外层再加一个维度：`feature = feature[np.newaxis, ...]`，得到 $(1, 2M, N)$。

### 两种特征的直觉对比

把两种特征的尺寸和信息含量并排看清楚：

| 特征类型 | 张量形状（单样本） | 信息特点 | 适配网络 |
|---|---|---|---|
| CM（双通道） | $(2, M, M)$ | 二阶统计量，有损压缩，丢失绝对相位 | CNN / MLP |
| CM（向量化） | $(M(M+1),)$ | 同上，展平后无空间结构 | MLP |
| IQ | $(2M, N)$ 或 $(1, 2M, N)$ | 保留全部原始信息，快拍数 $N$ 固定 | CNN / ResNet |

---

## 3.3.5 构造标签：从角度到训练目标

原始数据处理好了，标签也需要对应地变换成适合训练的格式。这里把分类和回归两种情形分别给出具体代码。

**分类标签（multi-hot 向量）**：把连续角度转换为离散格点上的 0/1 标签。

```python
def angles_to_classification_label(thetas, theta_min=-60, theta_max=60, resolution=1.0):
    """
    将角度列表转换为分类标签（multi-hot 向量）
    参数：
        thetas      : 真实角度数组，单位度
        theta_min   : 覆盖范围最小角度
        theta_max   : 覆盖范围最大角度
        resolution  : 格点间距（度）
    返回：
        label : multi-hot 向量，形状 (D,)，D = (theta_max-theta_min)/resolution + 1
    """
    grid = np.arange(theta_min, theta_max + resolution * 0.5, resolution)
    D = len(grid)
    label = np.zeros(D, dtype=np.float32)
    for th in thetas:
        idx = int(round((th - theta_min) / resolution))
        idx = np.clip(idx, 0, D - 1)
        label[idx] = 1.0
    return label
```

**回归标签（归一化角度值）**：直接将角度映射到 $[-1, 1]$ 区间。

```python
def angles_to_regression_label(thetas, theta_min=-60, theta_max=60):
    """
    将角度数组归一化到 [-1, 1]，作为回归标签
    输入：thetas，形状 (K,)，单位度
    输出：label，形状 (K,)，值域 [-1, 1]
    """
    thetas_sorted = np.sort(thetas)    # 升序，处理配对问题
    label = 2.0 * (thetas_sorted - theta_min) / (theta_max - theta_min) - 1.0
    return label.astype(np.float32)
```

---

## 3.3.6 完整数据集流水线与 PyTorch Dataset

把以上所有步骤串联起来，用 PyTorch 的 `Dataset` 类封装成可以直接训练的数据接口：

```python
import torch
from torch.utils.data import Dataset, DataLoader

class DOADataset(Dataset):
    """
    DOA 估计数据集
    feature_type : 'cm'（协方差矩阵双通道）或 'iq'（原始 IQ）
    task         : 'classification' 或 'regression'
    """
    def __init__(self, X_data, labels_deg, feature_type='cm',
                 task='classification', theta_min=-60, theta_max=60,
                 resolution=1.0):
        self.feature_type = feature_type
        self.task = task
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.resolution = resolution

        # 构建特征
        if feature_type == 'cm':
            self.features = build_cm_dataset(X_data)   # (N, 2, M, M)
        elif feature_type == 'iq':
            self.features = build_iq_dataset(X_data)   # (N, 2M, T)
        else:
            raise ValueError(f"未知特征类型: {feature_type}")

        # 构建标签
        if task == 'classification':
            self.labels = np.stack([
                angles_to_classification_label(
                    labels_deg[i], theta_min, theta_max, resolution)
                for i in range(len(labels_deg))
            ])
        elif task == 'regression':
            self.labels = np.stack([
                angles_to_regression_label(labels_deg[i], theta_min, theta_max)
                for i in range(len(labels_deg))
            ])
        else:
            raise ValueError(f"未知任务类型: {task}")

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        x = torch.tensor(self.features[idx], dtype=torch.float32)
        y = torch.tensor(self.labels[idx],   dtype=torch.float32)
        return x, y

# 使用示例
dataset = DOADataset(X_train, labels_train,
                     feature_type='cm', task='classification',
                     theta_min=-60, theta_max=60, resolution=1.0)
loader  = DataLoader(dataset, batch_size=64, shuffle=True)

# 检查一个批次的形状
for x_batch, y_batch in loader:
    print(f"输入特征形状: {x_batch.shape}")  # (64, 2, 8, 8)
    print(f"标签形状:     {y_batch.shape}")  # (64, 121)，D=(60-(-60))/1+1=121
    break
```

至此，从仿真生成原始数据到封装成 PyTorch `DataLoader`，整条数据流水线已经完整。每次 `DataLoader` 迭代时，会自动地将数据按 `batch_size` 切分、打乱顺序，并直接返回可以送入网络的张量。

---

## 3.3.7 几个实践中容易忽视的细节

**细节一：数据量的选取。** 没有一个放之四海而皆准的"训练样本数"答案，但有一个粗略的估算逻辑：分类任务中，如果格点数 $D = 121$、信源数 $K = 1$，理论上每个格点需要若干个样本，通常每格 50 到 100 个，总样本数在 6000 到 12000 左右可以作为起点。多信源时可行的角度组合数更多，需要相应增加。双信源在 $[-60°, 60°]$、$1°$ 分辨率、$5°$ 最小间隔下，不同组合数约为 $C^2_{121} \approx 7000$，每种组合生成多个 SNR 的样本即可达到合理的数据量规模。

**细节二：训练集与测试集不共用随机种子。** 生成训练集和测试集时，要使用不同的随机种子，确保两者的角度采样完全独立，没有数据泄漏。评估网络泛化能力的测试集，应当视作"网络从未见过的新数据"。

**细节三：特征归一化的必要性。** 协方差矩阵的数值范围受信号功率和快拍数的影响，不同 SNR 下幅度差异可能达到数个数量级。直接送入网络可能导致梯度不稳定。实践中，通常对 CM 特征做除以最大绝对值的归一化，或用 BatchNorm 让网络自适应地处理。IQ 特征也类似，可以对每个样本做零均值单位方差的标准化。

**细节四：快拍数 $N$ 对输入尺寸的影响。** 对于 CM 特征，无论 $N$ 是 128 还是 1024，协方差矩阵始终是 $M \times M$ 的，网络输入尺寸不变。但对于 IQ 特征，网络的卷积层或全连接层尺寸与 $N$ 直接挂钩，不同快拍数需要重新设计或调整网络。如果需要一个网络适应多种快拍数，使用全局平均池化代替固定尺寸的全连接层是常见的解法。

---

## 3.3.8 小结

本节从物理模型出发，完整地走了一遍 DOA 数据集的构建流程。

数据生成方面，基于第一章的阵列观测模型 $\mathbf{X} = \mathbf{A}\boldsymbol{\theta}) \mathbf{S} + \mathbf{N}$，通过随机采样角度、SNR 和信号，可以按需批量生成大量仿真样本，完全不依赖实测硬件。角度采样时需保证均匀覆盖、多 SNR 混合，多信源时加入最小间隔约束以保证数据质量。

数据形态方面，每个样本的原始形态是 $\mathbb{C}^{M \times N}$ 的复数矩阵，配合角度标签。将大量样本堆叠后形成完整数据集。

输入特征方面，有两条处理路线：CM 路线先计算 $M \times M$ 的样本协方差矩阵，再将实部和虚部拼成 $(2, M, M)$ 的双通道实数张量；IQ 路线直接将实部和虚部拼成 $(2M, N)$ 的二维实数矩阵，保留更完整的原始信息，但对快拍数 $N$ 敏感。标签根据任务类型分别构造为 multi-hot 分类向量或归一化回归向量，并最终封装进 PyTorch 的 `Dataset` 和 `DataLoader`。

数据准备好了。接下来的 3.4 节，我们就可以正式建立第一个 DOA 分类网络，把这些张量真正送进去训练了。