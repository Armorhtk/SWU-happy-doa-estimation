---
id: traditional-music
title: 2.3 MUSIC算法原理与实现
slug: /traditional-methods/music
---

## 2.3 MUSIC 算法原理与实现

有了子空间分解的理论基础（2.1 节）和信源数估计的工具（2.2 节），现在终于到了第二章的核心之一：**MUSIC 算法**（Multiple Signal Classification，多重信号分类）。

MUSIC 由 Ralph Schmidt 于 1986 年正式提出，此后迅速成为超分辨率 DOA 估计领域最广为人知的算法，影响延续至今。它的思路并不复杂——实质上是把 2.1 节末尾那一行等式 $\mathbf{U}_n^H\mathbf{a}(\theta_k) = \mathbf{0}$ 变成一个实用的谱峰搜索程序。理解了子空间正交性，MUSIC 的原理就已经掌握了一半；剩下的一半，是把它从理论命题变成可以跑出结果的代码。

---

### 2.3.1 从正交性到伪谱：MUSIC 的核心公式

2.1 节得到了一个关键结论：对于 $K$ 个信源，真实入射方向 $\theta_k$ 满足

$$
\mathbf{U}_n^H \mathbf{a}(\theta_k) = \mathbf{0}, \quad k = 1, 2, \cdots, K
$$

其中 $\mathbf{U}_n$ 是噪声子空间的基矩阵（$M \times (M-K)$）。这个等式等价地说：$\mathbf{a}(\theta_k)$ 与噪声子空间正交，因而 $\|\mathbf{U}_n^H \mathbf{a}(\theta_k)\|^2 = \mathbf{a}^H(\theta_k)\mathbf{U}_n\mathbf{U}_n^H\mathbf{a}(\theta_k) = 0$。

MUSIC 的思路是：把这个等式反过来用——对所有候选角度 $\theta$ 扫描，计算导向矢量 $\mathbf{a}(\theta)$ 与噪声子空间的"距离"，距离为零的地方就是信号方向。为了让结果呈现为峰值而不是谷值（更直观），取倒数，定义 **MUSIC 伪谱**（MUSIC pseudo-spectrum）：

$$
\boxed{P_{\text{MUSIC}}(\theta) = \frac{1}{\mathbf{a}^H(\theta)\mathbf{U}_n\mathbf{U}_n^H\mathbf{a}(\theta)} = \frac{1}{\|\mathbf{U}_n^H\mathbf{a}(\theta)\|^2}}
$$

当 $\theta = \theta_k$（真实方向）时，分母趋近于零，$P_{\text{MUSIC}}(\theta)$ 出现尖锐的峰值；当 $\theta$ 偏离信号方向时，$\mathbf{a}(\theta)$ 不再与噪声子空间正交，分母大于零，$P_{\text{MUSIC}}(\theta)$ 较小。对伪谱在 $[-90°, 90°]$ 上扫描，找到最大的 $K$ 个峰值，对应的角度就是 DOA 估计值。

这里需要说明一点：$P_{\text{MUSIC}}(\theta)$ 被称为"伪谱"而非"功率谱"，是因为它的峰值高度本身没有直接的物理功率含义——它只是正交度的一种反映，用来定位方向，而不代表信号的实际能量大小。这与 1.3 节常规波束形成的空间谱（真实输出功率）有本质区别。

---

### 2.3.2 MUSIC 算法的完整流程

把上述思路整理成算法步骤，非常清晰：

**第一步**：采集 $N$ 个快拍，构造样本协方差矩阵

$$\hat{\mathbf{R}} = \frac{1}{N}\sum_{n=1}^{N}\mathbf{x}[n]\mathbf{x}^H[n] = \frac{1}{N}\mathbf{X}\mathbf{X}^H$$

**第二步**：对 $\hat{\mathbf{R}}$ 做特征值分解，按降序排列特征值

$$\hat{\mathbf{R}} = \hat{\mathbf{U}}\hat{\boldsymbol{\Lambda}}\hat{\mathbf{U}}^H, \quad \hat{\lambda}_1 \geq \hat{\lambda}_2 \geq \cdots \geq \hat{\lambda}_M$$

**第三步**：利用已估计的信源数 $K$（来自 2.2 节），划分子空间

$$\hat{\mathbf{U}}_n = [\hat{\mathbf{u}}_{K+1}, \hat{\mathbf{u}}_{K+2}, \cdots, \hat{\mathbf{u}}_M] \quad (M \times (M-K) \text{ 矩阵})$$

**第四步**：构造噪声子空间投影矩阵，计算 MUSIC 伪谱

$$P_{\text{MUSIC}}(\theta) = \frac{1}{\mathbf{a}^H(\theta)\hat{\mathbf{U}}_n\hat{\mathbf{U}}_n^H\mathbf{a}(\theta)}, \quad \theta \in [-90°, 90°]$$

**第五步**：在伪谱中寻找 $K$ 个最大峰值，其对应角度即为 DOA 估计值 $\hat{\theta}_1, \hat{\theta}_2, \cdots, \hat{\theta}_K$

整个流程的计算瓶颈在第二步的特征值分解，复杂度为 $O(M^3)$；第四步的谱搜索复杂度为 $O(M \cdot I)$，其中 $I$ 是扫描网格的点数（通常取 $I = 1801$ 对应 $0.1°$ 步长）。

---

### 2.3.3 完整代码实现

下面给出一个结构清晰、注释完整的 MUSIC 实现，并与常规波束形成作对比，直观展示超分辨率效果：

```python
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 工具函数
# ============================================================

def steering_vector(theta_deg, M, d=0.5):
    """ULA 导向矢量"""
    theta = np.deg2rad(theta_deg)
    m = np.arange(M)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * m)

def sample_cov(X):
    """样本协方差矩阵"""
    N = X.shape[1]
    return (X @ X.conj().T) / N

def music_spectrum(R_hat, K, theta_grid, M, d=0.5):
    """
    MUSIC 伪谱计算
    参数：
        R_hat      : 样本协方差矩阵，(M, M)
        K          : 信源数
        theta_grid : 角度扫描网格（度）
        M          : 阵元数
        d          : 阵元间距（波长归一化）
    返回：
        spectrum   : MUSIC 伪谱（与 theta_grid 等长）
        U_n        : 噪声子空间矩阵
    """
    # 特征值分解（eigh 针对 Hermitian 矩阵，结果升序，需翻转）
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    eigvecs = eigvecs[:, ::-1]          # 降序排列

    # 噪声子空间：后 M-K 个特征向量
    U_n = eigvecs[:, K:]                # (M, M-K)
    En = U_n @ U_n.conj().T            # 噪声子空间投影矩阵

    # 谱搜索
    spectrum = np.zeros(len(theta_grid))
    for i, theta in enumerate(theta_grid):
        a = steering_vector(theta, M, d)
        denom = np.real(a.conj() @ En @ a)
        spectrum[i] = 1.0 / (denom + 1e-12)  # 加小量防止除零

    return spectrum, U_n

def cbf_spectrum(R_hat, theta_grid, M, d=0.5):
    """常规波束形成空间谱"""
    spectrum = np.zeros(len(theta_grid))
    for i, theta in enumerate(theta_grid):
        a = steering_vector(theta, M, d)
        spectrum[i] = np.real(a.conj() @ R_hat @ a)
    return spectrum

def find_peaks(spectrum, theta_grid, K):
    """寻找伪谱中最大的 K 个峰值"""
    from scipy.signal import find_peaks as sp_find_peaks
    peaks, _ = sp_find_peaks(spectrum)
    if len(peaks) == 0:
        return theta_grid[np.argsort(spectrum)[-K:]]
    # 按峰值高度排序，取前 K 个
    top_K = peaks[np.argsort(spectrum[peaks])[-K:]]
    return np.sort(theta_grid[top_K])

# ============================================================
# 仿真参数
# ============================================================

M = 8                          # 阵元数
K = 2                          # 信源数
N = 300                        # 快拍数
d = 0.5                        # 阵元间距（半波长）
thetas_true = [20, 30]         # 真实 DOA（刻意设得很近，间隔仅 10°）
SNR_dB = 10                    # 信噪比
sigma2 = 1.0
sig_pow = 10 ** (SNR_dB / 10) * sigma2

# 生成仿真数据
rng = np.random.default_rng(42)
A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
S = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N)) +
                              1j * rng.standard_normal((K, N)))
noise = np.sqrt(sigma2 / 2) * (rng.standard_normal((M, N)) +
                                 1j * rng.standard_normal((M, N)))
X = A @ S + noise
R_hat = sample_cov(X)

# ============================================================
# 计算 MUSIC 伪谱与 CBF 空间谱
# ============================================================

theta_grid = np.linspace(-90, 90, 1801)
music_spec, _ = music_spectrum(R_hat, K, theta_grid, M, d)
cbf_spec = cbf_spectrum(R_hat, theta_grid, M, d)

# 归一化（dB）
music_dB = 10 * np.log10(music_spec / music_spec.max())
cbf_dB   = 10 * np.log10(cbf_spec   / cbf_spec.max())

# 峰值检测
doa_est = find_peaks(music_spec, theta_grid, K)
print(f"真实 DOA：{thetas_true}°")
print(f"MUSIC 估计 DOA：{doa_est.round(1)}°")

# ============================================================
# 绘图对比
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

for ax, spec, title in zip(axes,
                            [cbf_dB, music_dB],
                            ['常规波束形成（CBF）', 'MUSIC 伪谱']):
    ax.plot(theta_grid, spec, 'b-', linewidth=1.2)
    for th in thetas_true:
        ax.axvline(x=th, color='r', linestyle='--', linewidth=1,
                   label=f'真实方向 {th}°' if th == thetas_true[0] else f'{th}°')
    ax.set_xlabel('角度 θ（度）')
    ax.set_ylabel('归一化幅度（dB）')
    ax.set_title(title)
    ax.set_xlim([-90, 90])
    ax.set_ylim([-40, 2])
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()
```

运行上述代码，你将清楚地看到两幅图的差异：左图（CBF）在 20° 和 30° 之间只有一个宽峰，根本无法区分两个信源；右图（MUSIC）则在 20° 和 30° 各出现一个尖锐的峰值，两个信源被清晰分辨。这就是超分辨率的直观体现——仅仅 10° 的角度间隔，在 8 阵元半波长 ULA 的瑞利分辨率（约 14°）以内，CBF 束手无策，而 MUSIC 轻松搞定。

---

### 2.3.4 MUSIC 为什么是"伪谱"而不是"谱"

稍微停一下，多说一点关于"伪谱"这个名字的含义，因为它揭示了 MUSIC 与常规波束形成的一个本质区别。

常规波束形成的空间谱 $P_{\text{CBF}}(\theta) = \mathbf{a}^H(\theta)\hat{\mathbf{R}}\mathbf{a}(\theta)$ 有明确的物理意义：它是阵列在方向 $\theta$ 上的**输出功率**，各角度上的积分近似等于总接收功率，具有功率谱的性质。

MUSIC 伪谱则不然。$P_{\text{MUSIC}}(\theta) = 1/\|\hat{\mathbf{U}}_n^H\mathbf{a}(\theta)\|^2$ 是一个**几何距离的倒数**，它描述的是"候选导向矢量距离信号子空间有多近"，而非"从该方向接收到了多少功率"。两个峰值的高度之比，不代表两个信源的功率之比；不同方向上的伪谱值不能相加、不满足归一化，"面积"没有物理意义。

理解这一点很重要：MUSIC 是一个**方向定位工具**，不是功率测量工具。它的输出只有峰值位置有意义，峰值高度的绝对大小不直接可用。

---

### 2.3.5 MUSIC 的性能分析：影响估计精度的因素

MUSIC 的超分辨率能力不是无条件的，它依赖于以下几个核心条件，任何一个被破坏，性能都会明显下降。

**条件一：快拍数 $N$ 足够大。** 样本协方差矩阵 $\hat{\mathbf{R}}$ 是真实 $\mathbf{R}$ 的随机近似，只有当 $N$ 足够大时，噪声子空间的估计 $\hat{\mathbf{U}}_n$ 才接近理论值 $\mathbf{U}_n$。快拍数越少，子空间估计偏差越大，伪谱峰值越宽、位置越不准。经验上，$N \geq 2M$ 是基本要求，$N \geq 10M$ 才能期待较好的性能。

**条件二：信噪比足够高。** SNR 决定了信号特征值与噪声特征值的分离程度。当 SNR 很低时，信号特征值与 $\sigma^2$ 非常接近，子空间划分出现错误，噪声向量混入信号子空间（或反之），正交性条件不再成立，伪谱峰值消失或位移。这就是 1.4 节提到的"阈值效应"在 MUSIC 上的具体表现。

**条件三：信源相互独立（非相干）。** MUSIC 的推导假设信源协方差矩阵 $\mathbf{R}_s$ 满秩，等价于各信源之间不相干。如果两个信号源完全相干（如多径传播，一个信号从两个方向到达），$\mathbf{R}_s$ 秩亏缺，信号子空间维度缩减，MUSIC 将完全失效。解决这一问题需要空间平滑预处理，将在 2.5 节专门讨论。

**条件四：信源数 $K$ 估计正确。** 如果 $K$ 估计偏大，会有多余的特征向量被分入信号子空间，噪声子空间被"污染"，伪谱会出现虚假峰值；如果 $K$ 估计偏小，真实信源的导向矢量被错误地归入噪声子空间，对应的峰值消失。

下面用一段代码量化展示 SNR 和快拍数对 MUSIC 估计精度的影响，以 RMSE 作为指标：

```python
import numpy as np

def music_doa_estimate(X, K, thetas_grid, M, d=0.5):
    """一次 MUSIC DOA 估计，返回排序后的估计角度"""
    R_hat = (X @ X.conj().T) / X.shape[1]
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :M - K]                  # 升序排列，前 M-K 个是噪声
    En = U_n @ U_n.conj().T

    spectrum = np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj()
                       @ En @ steering_vector(th, M, d)) + 1e-12)
        for th in thetas_grid
    ])

    from scipy.signal import find_peaks as sp_peaks
    peaks, _ = sp_peaks(spectrum)
    top = peaks[np.argsort(spectrum[peaks])[-K:]]
    return np.sort(thetas_grid[top])

# 蒙特卡洛仿真：SNR 扫描
M, K, d = 8, 2, 0.5
thetas_true = np.array([20.0, 35.0])
theta_grid = np.linspace(-90, 90, 1801)
N_trials = 200
N_snap = 200

snr_range = np.arange(-5, 21, 5)
rmse_list = []

for snr_dB in snr_range:
    sig_pow = 10 ** (snr_dB / 10)
    errors = []
    rng = np.random.default_rng(0)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
    for _ in range(N_trials):
        S = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N_snap)) +
                                     1j * rng.standard_normal((K, N_snap)))
        noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N_snap)) +
                                     1j * rng.standard_normal((M, N_snap)))
        X = A @ S + noise
        try:
            est = music_doa_estimate(X, K, theta_grid, M, d)
            if len(est) == K:
                errors.append(np.mean((est - thetas_true) ** 2))
        except Exception:
            pass
    rmse_list.append(np.sqrt(np.mean(errors)) if errors else np.nan)

import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.plot(snr_range, rmse_list, 'o-', label='MUSIC RMSE')
plt.xlabel('信噪比 SNR（dB）')
plt.ylabel('RMSE（度）')
plt.title(f'MUSIC 估计精度 vs SNR（M={M}, N={N_snap}）')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
```

观察输出曲线：高 SNR 时 RMSE 很小且随 SNR 增加平稳下降，趋近于 CRB；在某个阈值 SNR 附近，RMSE 突然跳升——这正是算法进入"失效区"的表现。这条曲线的形状是衡量任何 DOA 算法稳健性的标准图像，在第二章后续算法对比中（2.6 节）还会反复出现。

---

### 2.3.6 Root-MUSIC：免搜索的代数变体

标准 MUSIC 需要对角度网格逐点计算伪谱，搜索精度依赖网格步长（步长越小越准，但计算量越大），且结果受离散化误差限制。对于 ULA，有一种优雅的替代方案可以完全绕开这个问题——**Root-MUSIC**。

核心思路是：对 ULA，导向矢量的第 $m$ 个分量是 $e^{j(m-1)\psi}$，令 $z = e^{j\psi}$（其中 $\psi = 2\pi d\sin\theta$），则导向矢量可以写成：

$$\mathbf{a}(\theta) = [1, z, z^2, \cdots, z^{M-1}]^\top$$

MUSIC 伪谱的分母 $\mathbf{a}^H(\theta)\mathbf{U}_n\mathbf{U}_n^H\mathbf{a}(\theta)$ 是关于 $z$ 和 $z^*$ 的多项式。定义：

$$C(z) = \mathbf{a}^\top(z^{-1})\mathbf{U}_n\mathbf{U}_n^H\mathbf{a}(z)$$

这是一个关于 $z$ 的 $2(M-1)$ 阶多项式。理论上，真实信源方向对应的 $z_k = e^{j\psi_k}$ 恰好在单位圆上，是 $C(z) = 0$ 的根。Root-MUSIC 的做法是：求这个多项式的全部 $2(M-1)$ 个根，选取单位圆内部（模长最接近 1）的 $K$ 个根，从每个根的相位反算出 DOA：

$$\hat{\theta}_k = \arcsin\!\left(\frac{\angle z_k}{2\pi d}\right)$$

Root-MUSIC 消除了网格搜索，直接给出精确解，且不受离散化误差影响。实践中，在中高 SNR 下，Root-MUSIC 的精度往往比标准 MUSIC 略高，计算效率也更优。代价是它只适用于 ULA（其他阵型的导向矢量不能写成 Vandermonde 形式，多项式技巧失效）。

```python
import numpy as np

def root_music(R_hat, K, d=0.5):
    """
    Root-MUSIC 算法（适用于 ULA）
    返回：估计 DOA（度），降序排列
    """
    M = R_hat.shape[0]
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :M - K]          # 噪声子空间（升序，前 M-K 列）
    C = U_n @ U_n.conj().T            # (M, M) 噪声投影矩阵

    # 构造多项式系数：对 C 的各反对角线求和
    # 第 l 条反对角线（l = -(M-1), ..., 0, ..., M-1）
    coeffs = np.zeros(2 * M - 1, dtype=complex)
    for i in range(M):
        for j in range(M):
            coeffs[i - j + (M - 1)] += C[i, j]

    # 求多项式根
    roots = np.roots(coeffs)

    # 选取单位圆内且模长最接近 1 的 K 个根
    roots_inside = roots[np.abs(roots) < 1.0]
    if len(roots_inside) < K:
        roots_inside = roots  # 若不足 K 个，退化处理
    idx = np.argsort(np.abs(np.abs(roots_inside) - 1))[:K]
    selected = roots_inside[idx]

    # 从根的相位反算角度
    psi = np.angle(selected)
    sin_theta = psi / (2 * np.pi * d)
    sin_theta = np.clip(sin_theta, -1, 1)   # 防止数值误差越界
    doa_est = np.rad2deg(np.arcsin(sin_theta))

    return np.sort(doa_est)

# 验证：与标准 MUSIC 对比
M, K, d = 8, 2, 0.5
thetas_true = [20.0, 35.0]
rng = np.random.default_rng(0)
A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
S = np.sqrt(5.0) * (rng.standard_normal((K, 200)) + 1j * rng.standard_normal((K, 200)))
noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, 200)) + 1j * rng.standard_normal((M, 200)))
X = A @ S + noise
R_hat = sample_cov(X)

doa_root = root_music(R_hat, K, d)
print(f"真实 DOA：{thetas_true}°")
print(f"Root-MUSIC 估计：{doa_root.round(2)}°")
```

---

### 2.3.7 小结

本节围绕 MUSIC 算法完成了从原理到实现的完整链路。

**原理层面**：MUSIC 把 2.1 节的子空间正交性命题 $\mathbf{U}_n^H\mathbf{a}(\theta_k)=\mathbf{0}$ 转化为一个谱峰搜索问题——构造伪谱 $P_{\text{MUSIC}}(\theta) = 1/\|\hat{\mathbf{U}}_n^H\mathbf{a}(\theta)\|^2$，在真实方向处出现尖锐峰值。它不是功率谱，是方向定位工具。

**实现层面**：标准 MUSIC 流程是"计算协方差矩阵 → 特征值分解 → 提取噪声子空间 → 谱搜索 → 峰值检测"，代码结构清晰，对 ULA 可进一步用 Root-MUSIC 替换谱搜索，消除离散化误差、提升效率。

**性能层面**：MUSIC 的超分辨率能力依赖充足快拍、足够高 SNR 和信源非相干三个条件。在这些条件满足时，它可以接近 CRB；条件被破坏时，性能会出现阈值式的急剧下降，尤其对相干信号完全失效。

下一节将介绍 ESPRIT 算法——它走了一条完全不同的路：不搜索角度，而是直接从信号子空间的代数结构中求解 DOA，计算效率更高，在某些条件下精度也更好。
