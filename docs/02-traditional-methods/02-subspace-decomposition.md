---
id: traditional-eigendecomposition-and-subspace-basics
title: 2.1 特征值分解与子空间基本思想
slug: /traditional-methods/eigendecomposition-and-subspace-basics
---


## 2.1 特征值分解与子空间基本思想

第一章用了相当多的篇幅建立基础：阵列观测模型、导向矢量、协方差矩阵，以及常规波束形成的空间谱。最后，我们在 1.3 节末尾留下了一个悬念，在 1.4 节进一步挑明了问题所在——常规方法的分辨率受傅里叶极限约束，两个靠近的信号源会在空间谱上"融合"成一个宽峰，无法被区分。

第二章要回答的问题是：**突破傅里叶分辨率限制的方法是什么，为什么它能做到这一点？**

答案的核心，就是本节要介绍的**子空间思想**。把这个思想讲透，MUSIC 和 ESPRIT 才会显得自然而然、水到渠成。

---

### 2.1.1 从一个问题出发

让我们先退一步，从一个更本质的角度来审视协方差矩阵。

第一章告诉我们，协方差矩阵的理论结构是：

$$
\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}
$$

其中 $\mathbf{A} = [\mathbf{a}(\theta_1), \mathbf{a}(\theta_2), \cdots, \mathbf{a}(\theta_K)]$ 是 $M \times K$ 的导向矢量矩阵，$\mathbf{R}_s$ 是 $K \times K$ 的信源协方差矩阵，$\sigma^2\mathbf{I}$ 是噪声项。

现在提一个问题：这个 $M \times M$ 的矩阵 $\mathbf{R}$ 里面，到底藏了多少"有效信息"？

从信号的角度想一想：空间中只有 $K$ 个独立信号源（$K < M$），阵列接收到的 $M$ 路信号，本质上只是这 $K$ 个信号的线性叠加。换句话说，$M$ 维观测空间中，真正"有信号"的方向只有 $K$ 个，剩下的 $M - K$ 个方向上只有噪声。这暗示协方差矩阵 $\mathbf{R}$ 应该有某种低维结构——而揭示这种结构的工具，正是**特征值分解**（Eigenvalue Decomposition，EVD）。

---

### 2.1.2 特征值分解：矩阵的"骨骼"

特征值分解（Eigenvalue Decomposition，EVD）是线性代数中的核心工具。对于一个 $M \times M$ 的 Hermitian 矩阵（满足 $\mathbf{R} = \mathbf{R}^H$ 的复对称矩阵，协方差矩阵恰好满足这一条件），其特征值分解总是存在且可以写成：

$$
\mathbf{R} = \mathbf{U}\boldsymbol{\Lambda}\mathbf{U}^H
$$

其中：
- $\boldsymbol{\Lambda} = \mathrm{diag}(\lambda_1, \lambda_2, \cdots, \lambda_M)$ 是对角矩阵，对角元素 $\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_M \geq 0$ 是 $\mathbf{R}$ 的**特征值**（eigenvalue），按降序排列；
- $\mathbf{U} = [\mathbf{u}_1, \mathbf{u}_2, \cdots, \mathbf{u}_M]$ 是酉矩阵（满足 $\mathbf{U}^H\mathbf{U} = \mathbf{I}$），其列向量 $\mathbf{u}_i$ 是对应于 $\lambda_i$ 的**特征向量**（eigenvector）。

特征向量的几何含义是：$\mathbf{u}_i$ 是矩阵 $\mathbf{R}$ 作用下"方向不变"的向量，只有尺度发生变化——$\mathbf{R}\mathbf{u}_i = \lambda_i \mathbf{u}_i$。特征值 $\lambda_i$ 衡量了该方向上的"能量权重"。酉矩阵 $\mathbf{U}$ 的各列两两正交（$\mathbf{u}_i^H \mathbf{u}_j = 0$，$i \neq j$），且每列模长为 1，它构成了 $M$ 维空间的一组**标准正交基**。

展开来写，特征值分解等价于：

$$
\mathbf{R} = \sum_{i=1}^{M} \lambda_i \mathbf{u}_i \mathbf{u}_i^H
$$

这是一个矩阵的"谱分解"——把 $\mathbf{R}$ 表示成 $M$ 个秩一矩阵 $\mathbf{u}_i\mathbf{u}_i^H$ 的加权叠加，权重正是特征值 $\lambda_i$。从这个角度看，特征值分解把矩阵拆成了若干"成分"，每个成分对应一个空间方向（特征向量）和该方向上的能量（特征值）。

---

### 2.1.3 协方差矩阵的特征值结构

现在来看，对阵列协方差矩阵 $\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}$ 做特征值分解，会得到什么？

**先从无噪声的情形入手**（$\sigma^2 = 0$）。此时 $\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H$，这个矩阵的秩最多是 $K$（因为 $\mathbf{A}$ 只有 $K$ 列，假设各导向矢量线性无关，信源相互独立）。秩为 $K$ 意味着：

$$
\mathbf{R} = \mathbf{U}_s \boldsymbol{\Lambda}_s \mathbf{U}_s^H
$$

只有 $K$ 个非零特征值，收集在对角矩阵 $\boldsymbol{\Lambda}_s$ 中；对应的 $K$ 个特征向量收集在 $M \times K$ 的矩阵 $\mathbf{U}_s$ 中。其余 $M - K$ 个特征值全为零，对应的特征向量构成矩阵 $\mathbf{U}_n$（$M \times (M-K)$）。

关键结论来了：由于 $\mathbf{R}\mathbf{u}_i = \lambda_i\mathbf{u}_i$，若 $\lambda_i = 0$，则 $\mathbf{A}\mathbf{R}_s\mathbf{A}^H\mathbf{u}_i = \mathbf{0}$，这等价于 $\mathbf{u}_i$ 与 $\mathbf{A}$ 的列空间正交。也就是说，$\mathbf{U}_n$ 的各列与所有导向矢量 $\mathbf{a}(\theta_k)$ 正交。

**加上白噪声**（$\sigma^2 > 0$）之后，利用 $\sigma^2\mathbf{I} = \sigma^2(\mathbf{U}_s\mathbf{U}_s^H + \mathbf{U}_n\mathbf{U}_n^H)$，展开可得：

$$
\mathbf{R} = \mathbf{U}_s(\boldsymbol{\Lambda}_s + \sigma^2\mathbf{I}_K)\mathbf{U}_s^H + \mathbf{U}_n(\sigma^2\mathbf{I}_{M-K})\mathbf{U}_n^H
$$

写成完整的特征值分解形式：

$$
\mathbf{R} = [\mathbf{U}_s \quad \mathbf{U}_n]
\begin{bmatrix}
\boldsymbol{\Lambda}_s + \sigma^2\mathbf{I}_K & \mathbf{0} \\
\mathbf{0} & \sigma^2\mathbf{I}_{M-K}
\end{bmatrix}
\begin{bmatrix}
\mathbf{U}_s^H \\ \mathbf{U}_n^H
\end{bmatrix}
$$

这个结果有两个非常重要的含义，值得逐一分析清楚。

**含义一：特征值分成两组。** 前 $K$ 个特征值是 $\lambda_k^{(s)} + \sigma^2$（$k = 1, \cdots, K$），明显大于 $\sigma^2$；后 $M-K$ 个特征值全部等于 $\sigma^2$，形成一个"平台"。加入白噪声相当于把每个特征值都抬高了 $\sigma^2$，但特征向量没有发生任何变化——这一点至关重要，正是子空间方法能够从含噪数据中提取方向信息的根本原因。

**含义二：特征向量的几何结构不变。** 尽管噪声改变了特征值的大小，但 $\mathbf{U}_s$ 和 $\mathbf{U}_n$ 与无噪声时完全相同。因此，$\mathbf{U}_n$ 的各列与导向矢量 $\mathbf{a}(\theta_k)$ 的正交关系，在白噪声环境下依然成立：

$$
\mathbf{U}_n^H \mathbf{a}(\theta_k) = \mathbf{0}, \quad k = 1, 2, \cdots, K
$$

这一行等式，是整个子空间方法论的核心命题，请同学们牢记。

---

### 2.1.4 信号子空间与噪声子空间

有了上面的分析，我们可以正式引入两个核心概念。

**信号子空间**（signal subspace）：由协方差矩阵 $\mathbf{R}$ 较大的 $K$ 个特征值对应的特征向量张成的线性子空间，记为 $\mathrm{span}(\mathbf{U}_s)$。可以证明，这个子空间与导向矢量矩阵 $\mathbf{A}$ 的列空间完全相同：

$$
\mathrm{span}(\mathbf{U}_s) = \mathrm{span}(\mathbf{A}) = \mathrm{span}([\mathbf{a}(\theta_1), \cdots, \mathbf{a}(\theta_K)])
$$

直观地说：信号子空间就是所有信号到来方向的导向矢量共同"撑起"的 $K$ 维空间。

**噪声子空间**（noise subspace）：由较小的 $M-K$ 个特征值（均等于 $\sigma^2$）对应的特征向量张成的线性子空间，记为 $\mathrm{span}(\mathbf{U}_n)$。噪声子空间是信号子空间在 $M$ 维空间中的正交补，即 $M$ 维空间中"扣除信号后剩下的部分"。

这两个子空间相互正交（$\mathbf{U}_s^H\mathbf{U}_n = \mathbf{0}$），合在一起撑满整个 $M$ 维观测空间。它们的关系可以用一个简单的图景来理解：

> 想象 $M$ 维空间是一个大房间，信号子空间是一个 $K$ 维的"信号平面"，噪声子空间是与它垂直的 $M-K$ 维"噪声墙面"。$K$ 个导向矢量各自"站在"信号平面里，与噪声墙面完全垂直。

于是，关键等式 $\mathbf{U}_n^H\mathbf{a}(\theta_k) = \mathbf{0}$ 的几何含义就很清楚了：**每个真实信号方向对应的导向矢量，恰好落在信号子空间内，因而与噪声子空间正交**。换句话说，如果我们拿着一个候选方向 $\theta$ 对应的导向矢量 $\mathbf{a}(\theta)$ 去投影到噪声子空间，投影长度为零当且仅当 $\theta$ 是真实信号方向——这就是从协方差矩阵中"找出"信号方向的基本逻辑。

---

### 2.1.5 用特征值判断信源数

子空间分解还带来一个额外的收获：可以从特征值的分布中直接读出信源数 $K$。

理论上，$\mathbf{R}$ 的 $M$ 个特征值（按降序排列）应呈现出如下图景：前 $K$ 个特征值显著大于 $\sigma^2$，后 $M-K$ 个特征值恰好等于 $\sigma^2$，形成一个清晰的"平台"。信源数 $K$ 就是大于 $\sigma^2$ 的特征值个数。

```python
import numpy as np
import matplotlib.pyplot as plt

# 仿真参数
M = 8           # 阵元数
K = 2           # 信源数
N = 500         # 快拍数
d = 0.5         # 阵元间距（波长归一化）
thetas = np.deg2rad([20, 40])   # 真实信号方向
sigma2 = 0.1    # 噪声功率

# 构造导向矢量矩阵 A
psi = 2 * np.pi * d * np.sin(thetas)                   # 空间频率
A = np.exp(1j * np.outer(np.arange(M), psi))           # M×K

# 生成信号与噪声（信号功率归一化为 1）
S = (np.random.randn(K, N) + 1j * np.random.randn(K, N)) / np.sqrt(2)
noise = np.sqrt(sigma2 / 2) * (np.random.randn(M, N) + 1j * np.random.randn(M, N))
X = A @ S + noise           # 阵列观测矩阵 M×N

# 计算样本协方差矩阵并做特征值分解
R_hat = (X @ X.conj().T) / N
eigenvalues, eigenvectors = np.linalg.eigh(R_hat)  # eigh 针对 Hermitian 矩阵
eigenvalues = eigenvalues[::-1]                     # 按降序排列
eigenvectors = eigenvectors[:, ::-1]

# 绘制特征值分布
plt.figure(figsize=(7, 4))
plt.stem(range(1, M + 1), eigenvalues.real, basefmt='k-')
plt.axhline(y=sigma2, color='r', linestyle='--', label=f'噪声功率 σ² = {sigma2}')
plt.xlabel('特征值编号')
plt.ylabel('特征值大小')
plt.title('协方差矩阵特征值分布（M=8，K=2）')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 分离信号子空间与噪声子空间
U_s = eigenvectors[:, :K]           # 信号子空间，M×K
U_n = eigenvectors[:, K:]           # 噪声子空间，M×(M-K)

print("信号子空间维度：", U_s.shape)
print("噪声子空间维度：", U_n.shape)
print("前 K 个特征值（信号+噪声）：", eigenvalues[:K].real.round(4))
print("后 M-K 个特征值（纯噪声）：", eigenvalues[K:].real.round(4))
```

运行这段代码，你会看到：前两个特征值明显偏大，后六个特征值接近 $\sigma^2 = 0.1$，形成一条平坦的"噪声基线"。这个视觉上的"断层"，正是识别信源数的直觉依据。

> **注意**：在实际场景中，噪声功率 $\sigma^2$ 通常未知，各特征值也因有限快拍而存在估计误差，后 $M-K$ 个特征值不会精确相等，断层也不会如此清晰——信源数估计因此成为一个独立的问题，我们将在 2.2 节专门讨论。

---

### 2.1.6 子空间方法的核心逻辑

到这里，子空间方法的基本思想已经完整了。让我们整理一下整条推理链，用尽量简练的语言把它说清楚。

**第一步**，从观测数据计算样本协方差矩阵 $\hat{\mathbf{R}}$。

**第二步**，对 $\hat{\mathbf{R}}$ 做特征值分解，通过特征值的大小分布将特征向量分成两组：与较大特征值对应的 $K$ 个特征向量构成**信号子空间** $\hat{\mathbf{U}}_s$，与较小特征值（接近 $\sigma^2$）对应的 $M-K$ 个特征向量构成**噪声子空间** $\hat{\mathbf{U}}_n$。

**第三步**，利用子空间的正交性定位信号方向。真实信号方向 $\theta_k$ 满足 $\mathbf{U}_n^H\mathbf{a}(\theta_k) = \mathbf{0}$，即导向矢量与噪声子空间正交。因此，在所有候选角度 $\theta$ 中，找到使 $\|\hat{\mathbf{U}}_n^H\mathbf{a}(\theta)\|$ 最小（或趋近于零）的那些角度，就是信号来波方向的估计值。

这三步就是 MUSIC 算法的完整框架，我们将在 2.3 节看到它的完整实现。而 ESPRIT 算法则走了另一条路——它不搜索角度，而是直接利用信号子空间的旋转不变性代数求解，我们在 2.4 节讨论。

为什么这套方法能突破傅里叶分辨率限制？因为它不是在做"空间 DFT"，而是在**检验一个精确的正交条件**：导向矢量 $\mathbf{a}(\theta)$ 是否落在信号子空间内。当快拍数足够多、信噪比足够高时，这个条件的判断可以做到极高的精度——只要两个信源的导向矢量不完全相同（即角度不完全相等），子空间方法原则上就能区分它们，分辨率不受孔径大小的硬性约束。这就是"超分辨率"（super-resolution）名称的由来。

---

### 2.1.7 小结

本节从协方差矩阵的特征值分解出发，建立了子空间方法的核心框架：

**第一**，协方差矩阵 $\mathbf{R}$ 在白噪声条件下的特征值分为两组：前 $K$ 个大于 $\sigma^2$，后 $M-K$ 个等于 $\sigma^2$。白噪声只改变特征值大小，不改变特征向量方向。

**第二**，与 $K$ 个较大特征值对应的特征向量张成**信号子空间**，其列空间与导向矢量矩阵 $\mathbf{A}$ 的列空间相同；与 $M-K$ 个较小特征值对应的特征向量张成**噪声子空间**，两者相互正交。

**第三**，真实信号方向满足 $\mathbf{U}_n^H\mathbf{a}(\theta_k) = \mathbf{0}$，即导向矢量与噪声子空间正交。这一正交条件是子空间类 DOA 算法（MUSIC、ESPRIT 等）的统一出发点，也是超越傅里叶分辨率限制的根本所在。

理解了子空间的思想，第二章后续内容的逻辑就会清晰很多。不过在正式推导 MUSIC 之前，还有一个实际问题绕不开：信源数 $K$ 通常是未知的——没有正确的 $K$，子空间就无从划分。这就是 2.2 节要解决的问题。