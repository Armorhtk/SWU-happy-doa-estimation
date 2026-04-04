---
id: doa-intro-covariance-beamforming-and-spatial-spectrum
title: 1.3 协方差矩阵、常规波束形成与空间谱估计
slug: /doa-intro/covariance-beamforming-and-spatial-spectrum
---

## 1.3 协方差矩阵、常规波束形成与空间谱估计

前两节建立了阵列的物理模型，给出了观测方程：

$$
\mathbf{x}(t) = \mathbf{A}(\boldsymbol{\theta})\,\mathbf{s}(t) + \mathbf{n}(t)
$$

现在面对的问题是：在实际中，我们只能拿到一段有限长的观测数据 $\mathbf{x}(t)$，而 $\boldsymbol{\theta}$、$\mathbf{s}(t)$ 都是未知的。该如何从 $\mathbf{x}(t)$ 中把方向信息提取出来？

答案是：不直接操作瞬时观测值，而是先从数据中提炼出一个更稳定的统计量——**协方差矩阵**（covariance matrix）。它是阵列信号处理的核心工具，几乎所有经典 DOA 算法都以它为出发点。

---

### 1.3.1 为什么需要协方差矩阵

先来想一个简单问题。假设你只拿到一个时刻的观测向量 $\mathbf{x}(t_0)$，能估计出信号方向吗？

很难。原因有两个：第一，单次观测被噪声严重污染，信噪比低；第二，即使没有噪声，$\mathbf{x}(t_0) = \mathbf{A}\mathbf{s}(t_0)$ 中信号幅度 $\mathbf{s}(t_0)$ 也是未知的，方向和幅度纠缠在一起，无法分离。

但如果多观测几百次、几千次呢？这些观测在时间上相互独立，信号方向 $\boldsymbol{\theta}$ 却是不变的。把这些观测的统计特性汇总起来，噪声的随机性会被平均掉，而方向信息会稳定地保留——这就是协方差矩阵的核心思路。

**协方差矩阵**定义为：

$$
\mathbf{R} = \mathbb{E}[\mathbf{x}(t)\mathbf{x}^H(t)]
$$

其中 $\mathbb{E}[\cdot]$ 是统计期望，上标 $H$ 表示共轭转置。$\mathbf{R}$ 是一个 $M \times M$ 的矩阵，其第 $(i, j)$ 个元素是第 $i$ 个阵元与第 $j$ 个阵元观测信号之间的互相关：

$$
[\mathbf{R}]_{ij} = \mathbb{E}[x_i(t)\, x_j^*(t)]
$$

当 $i = j$ 时，这是第 $i$ 个阵元的信号功率；当 $i \neq j$ 时，它反映了两个阵元之间信号的相关程度。方向信息正是藏在这些不同阵元之间的相关结构里。

---

### 1.3.2 协方差矩阵的理论结构

把观测模型代入协方差矩阵的定义，展开计算：

$$
\mathbf{R} = \mathbb{E}[(\mathbf{A}\mathbf{s}(t) + \mathbf{n}(t))(\mathbf{A}\mathbf{s}(t) + \mathbf{n}(t))^H]
$$

在两个标准假设下——信号与噪声互不相关，噪声是空间白噪声（各阵元噪声相互独立、功率相等）——交叉项消失，结果化简为：

$$
\boxed{\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}}
$$

这是阵列信号处理中最核心的一个等式，值得仔细读懂每一项：

- $\mathbf{R}_s = \mathbb{E}[\mathbf{s}(t)\mathbf{s}^H(t)]$ 是 $K \times K$ 的**信源协方差矩阵**（source covariance matrix），描述各信号源之间的功率与相关关系。若各信号源相互独立，则 $\mathbf{R}_s$ 是对角矩阵，对角元素为各信源功率 $\sigma_k^2$。
- $\mathbf{A}\mathbf{R}_s\mathbf{A}^H$ 是 $M \times M$ 的**信号分量**，秩为 $K$（假设 $K < M$），它的列空间恰好是由 $K$ 个导向矢量张成的子空间。
- $\sigma^2\mathbf{I}$ 是**噪声分量**，$\sigma^2$ 是噪声功率，$\mathbf{I}$ 是 $M \times M$ 单位矩阵——噪声贡献均匀叠加在 $\mathbf{R}$ 的对角线上。

这个结构告诉我们：**协方差矩阵 $\mathbf{R}$ 是信号分量和噪声分量的叠加，方向信息完全包含在信号分量 $\mathbf{A}\mathbf{R}_s\mathbf{A}^H$ 之中**。DOA 估计的任务，从这个角度来看，就是从 $\mathbf{R}$ 中分离出信号分量，进而恢复 $\mathbf{A}$（也就是各导向矢量对应的角度）。

---

### 1.3.3 样本协方差矩阵：从理论到实践

理论上的 $\mathbf{R}$ 需要无穷多次观测才能精确计算，实际中我们只有有限的 $N$ 个**快拍**（snapshot）——每个快拍就是阵列在一个时刻的观测向量 $\mathbf{x}[n]$。

> **什么是快拍？** 快拍（snapshot）是阵列信号处理中的术语，指阵列在某一采样时刻采集到的 $M$ 维观测向量。如果我们以采样频率对信号采样，采集了 $N$ 个时间点的数据，就说有 $N$ 个快拍。快拍数 $N$ 越大，统计估计越准确。

用 $N$ 个快拍构造**样本协方差矩阵**（sample covariance matrix）：

$$
\hat{\mathbf{R}} = \frac{1}{N}\sum_{n=1}^{N}\mathbf{x}[n]\mathbf{x}^H[n] = \frac{1}{N}\mathbf{X}\mathbf{X}^H
$$

其中 $\mathbf{X} = [\mathbf{x}[1], \mathbf{x}[2], \cdots, \mathbf{x}[N]]$ 是 $M \times N$ 的数据矩阵。可以证明，$\hat{\mathbf{R}}$ 是 $\mathbf{R}$ 的无偏估计，即 $\mathbb{E}[\hat{\mathbf{R}}] = \mathbf{R}$，且当 $N \to \infty$ 时，$\hat{\mathbf{R}} \to \mathbf{R}$。

快拍数 $N$ 的选取对估计质量有重要影响。一个实用的经验法则是：$N$ 至少应为阵元数 $M$ 的若干倍，通常要求 $N \geq 2M$ 甚至更多。快拍数过少时，$\hat{\mathbf{R}}$ 的估计误差较大，会使后续 DOA 算法性能明显下降——这一点在低信噪比场景下尤为突出，也是 1.4 节和第二章会深入讨论的问题。

用代码来看看样本协方差矩阵是怎么计算的：
```python
import numpy as np

def compute_scm(X):
    """
    计算样本协方差矩阵
    参数：
        X : 数据矩阵，形状为 (M, N)，M 为阵元数，N 为快拍数
    返回：
        R_hat : 样本协方差矩阵，形状为 (M, M)
    """
    N = X.shape[1]
    R_hat = (X @ X.conj().T) / N
    return R_hat

# 示例：生成仿真数据
M = 8       # 阵元数
N = 200     # 快拍数
d = 0.5     # 阵元间距（波长归一化）

# 单个信号源，入射角 30°，信噪比 10 dB
theta = np.deg2rad(30)
psi = 2 * np.pi * d * np.sin(theta)
a = np.exp(1j * np.arange(M) * psi)         # 导向矢量

# 生成信号与噪声
s = (np.random.randn(N) + 1j * np.random.randn(N)) / np.sqrt(2)  # 单位功率信号
sigma2 = 0.1                                  # 噪声功率（对应 SNR = 10 dB）
noise = np.sqrt(sigma2 / 2) * (np.random.randn(M, N) + 1j * np.random.randn(M, N))

X = np.outer(a, s) + noise                   # 阵列观测矩阵

R_hat = compute_scm(X)
print("样本协方差矩阵形状：", R_hat.shape)   # (8, 8)
print("对角元素（各阵元功率估计）：\n", np.real(np.diag(R_hat)).round(3))
```

---

### 1.3.4 常规波束形成：最直觉的方向搜索

有了协方差矩阵，最自然的方向估计思路是什么？

想象你手里有一个"方向探测器"，可以朝任意角度 $\phi$ 转动，测量从该方向来的信号功率。如果 $\phi$ 恰好对准了某个信号源，从那个方向来的信号就能相干叠加，输出功率最大；如果 $\phi$ 偏离了信号方向，各阵元的信号相位不对齐，叠加结果会相互抵消，输出功率变小。这就是**常规波束形成**（Conventional Beamforming，CBF）的基本思路，也称为**延迟-求和波束形成**（Delay-and-Sum Beamforming，DAS）。

具体地，定义一个**波束形成器权矢量** $\mathbf{w}(\phi) = \mathbf{a}(\phi)$，即把搜索方向 $\phi$ 对应的导向矢量作为权矢量。在方向 $\phi$ 上的波束形成输出为：

$$
y(t, \phi) = \mathbf{w}^H(\phi)\,\mathbf{x}(t) = \mathbf{a}^H(\phi)\,\mathbf{x}(t)
$$

它的物理含义很直观：对各阵元的观测值 $x_m(t)$ 乘以对应的相位补偿因子 $e^{-j(m-1)\psi_\phi}$，再求和——相当于把"虚拟接收方向"对准 $\phi$，检查从那个方向来的能量有多少。

输出功率（即**空间谱**）为：

$$
P_{\text{CBF}}(\phi) = \mathbb{E}[|y(t, \phi)|^2] = \mathbf{a}^H(\phi)\,\mathbf{R}\,\mathbf{a}(\phi)
$$

实践中用样本协方差矩阵 $\hat{\mathbf{R}}$ 代替 $\mathbf{R}$：

$$
\hat{P}_{\text{CBF}}(\phi) = \mathbf{a}^H(\phi)\,\hat{\mathbf{R}}\,\mathbf{a}(\phi)
$$

对 $\phi$ 在 $[-90°, 90°]$ 做密集扫描，将每个角度对应的功率画出来，就得到了**空间谱**（spatial spectrum）。空间谱的峰值位置对应信号源的方向估计值——这个操作在概念上与时域的功率谱估计完全类比：时域扫描频率、空域扫描角度，功率谱的峰对应频率成分，空间谱的峰对应方向。

下面是一个完整的常规波束形成实现：
```python
def cbf_spectrum(R_hat, theta_grid, M, d=0.5):
    """
    常规波束形成空间谱估计
    参数：
        R_hat      : 样本协方差矩阵，(M, M)
        theta_grid : 角度扫描网格（度），如 np.linspace(-90, 90, 361)
        M          : 阵元数
        d          : 阵元间距（波长归一化）
    返回：
        spectrum   : 空间谱功率，与 theta_grid 等长
    """
    spectrum = np.zeros(len(theta_grid))
    m = np.arange(M)
    for i, theta in enumerate(theta_grid):
        psi = 2 * np.pi * d * np.sin(np.deg2rad(theta))
        a = np.exp(1j * m * psi)
        spectrum[i] = np.real(a.conj() @ R_hat @ a)
    return spectrum

# 接上文仿真数据
theta_grid = np.linspace(-90, 90, 361)
spectrum = cbf_spectrum(R_hat, theta_grid, M)

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.plot(theta_grid, 10 * np.log10(spectrum / spectrum.max()))
plt.axvline(x=30, color='r', linestyle='--', label='真实方向 30°')
plt.xlabel('角度 θ（度）')
plt.ylabel('归一化功率（dB）')
plt.title('常规波束形成空间谱')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
```

运行这段代码，你会看到空间谱在 $30°$ 附近出现明显的峰值，这就是 DOA 估计的结果。

---

### 1.3.5 常规波束形成的本质与局限

空间谱在峰值处为什么会最大？来做一个简单的分析。

对于单个信号源（方向 $\theta_0$，功率 $\sigma_s^2$）加白噪声的情形，协方差矩阵为：

$$
\mathbf{R} = \sigma_s^2\,\mathbf{a}(\theta_0)\mathbf{a}^H(\theta_0) + \sigma^2\mathbf{I}
$$

代入波束形成功率公式：

$$
P_{\text{CBF}}(\phi) = \sigma_s^2 |\mathbf{a}^H(\phi)\mathbf{a}(\theta_0)|^2 + \sigma^2 M
$$

其中 $\sigma^2 M$ 是噪声的固定贡献，第一项随搜索方向 $\phi$ 变化。当 $\phi = \theta_0$ 时，$|\mathbf{a}^H(\phi)\mathbf{a}(\theta_0)| = M$（完全对齐，相干叠加），第一项取得最大值 $\sigma_s^2 M^2$；当 $\phi \neq \theta_0$ 时，内积 $|\mathbf{a}^H(\phi)\mathbf{a}(\theta_0)| < M$，功率下降。这正是空间谱在真实方向出现峰值的原因。

然而，常规波束形成有一个根本性的局限：**分辨率受阵列孔径限制**。上面的内积 $|\mathbf{a}^H(\phi)\mathbf{a}(\theta_0)|$ 是一个 sinc 型函数，其主瓣宽度约为 $\lambda / (Md)$（弧度），对应的角度分辨率约为：

$$
\Delta\theta_{\text{CBF}} \approx \frac{\lambda}{Md\cos\theta}
$$

对于 8 阵元、半波长间距的 ULA（$Md = 4\lambda$），正侧射方向（$\theta = 0°$）的分辨率约为 $1/4$ 弧度，即约 $14°$。这意味着：**如果两个信号源的角度差小于约 $14°$，常规波束形成就无法将它们区分开来**，空间谱上只会看到一个宽峰，而非两个独立的峰。

这个限制称为**瑞利分辨率**（Rayleigh resolution limit），它本质上是孔径有限带来的衍射极限——和光学显微镜无法分辨过近的两个点是同一个道理。

这就是经典子空间方法（MUSIC、ESPRIT）要解决的核心问题：打破瑞利分辨率限制，实现超分辨率 DOA 估计。而要理解这些方法，我们首先需要理解协方差矩阵更深层的矩阵结构——特征值分解和子空间分解。这一话题，将在 1.4 节作为"分辨率问题"的延伸引出，并在第二章全面展开。

---

### 1.3.6 小结

本节围绕协方差矩阵这一核心工具，完成了三件事：

**第一**，建立了协方差矩阵的理论模型 $\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}$，揭示了方向信息在矩阵结构中的藏身之处。

**第二**，介绍了样本协方差矩阵 $\hat{\mathbf{R}} = \frac{1}{N}\mathbf{X}\mathbf{X}^H$ 作为实践中的计算对象，理解了快拍数 $N$ 对估计精度的影响。

**第三**，以常规波束形成为例，展示了从协方差矩阵出发构造空间谱、通过谱峰定位信号方向的完整流程——同时也看到了它的分辨率上限。

掌握了这三点，我们就站在了第二章经典算法的门口。下一节将从理论角度正面回答：分辨率的极限究竟在哪里，以及估计误差可以压缩到多小——这就是克拉美—罗下界（Cramér-Rao Bound）要告诉我们的事情。
