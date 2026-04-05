---
id: traditional-esprit
title: 2.4 ESPRIT算法原理与实现
slug: /traditional-methods/esprit
---

## 2.4 ESPRIT 算法原理与实现

学完 MUSIC，我们已经掌握了子空间方法的第一种思路：把正交性检验化为谱峰搜索。这条路行之有效，但有一个内在的代价——必须对角度网格逐点扫描，计算量随网格密度线性增长，最终的估计精度也受限于网格步长（Root-MUSIC 解决了离散化问题，但仍需求解多项式根）。

本节介绍的 ESPRIT 算法走了一条截然不同的路。它的全称是 **Estimation of Signal Parameters via Rotational Invariance Techniques**（基于旋转不变性的信号参数估计），由 Roy、Paulraj 和 Kailath 在 1986—1989 年间提出。ESPRIT 的核心思想不是"搜索"，而是直接从信号子空间的代数结构中"解方程"——完全绕开谱搜索，直接输出 DOA 的数值解，计算效率更高，在中高 SNR 条件下精度也与 MUSIC 相当。

---

### 2.4.1 关键物理直觉：两个子阵之间的相位关系

ESPRIT 的出发点是一个简单但深刻的物理观察。回忆 ULA 的导向矢量：

$$
\mathbf{a}(\theta) = \left[1,\ e^{j\psi},\ e^{j2\psi},\ \cdots,\ e^{j(M-1)\psi}\right]^\top, \quad \psi = \frac{2\pi d}{\lambda}\sin\theta
$$

把这个 $M$ 维阵列分成两个长度为 $M-1$ 的"子阵"：

- **子阵 1**（$\mathbf{x}_1$）：取前 $M-1$ 个阵元，即阵元 $1, 2, \cdots, M-1$
- **子阵 2**（$\mathbf{x}_2$）：取后 $M-1$ 个阵元，即阵元 $2, 3, \cdots, M$

两个子阵在空间上完全相同，只是整体向后平移了一个阵元间距 $d$。对于第 $k$ 个信源，两个子阵对应的导向矢量分别是：

$$
\mathbf{a}_1(\theta_k) = \left[1,\ e^{j\psi_k},\ \cdots,\ e^{j(M-2)\psi_k}\right]^\top
$$

$$
\mathbf{a}_2(\theta_k) = \left[e^{j\psi_k},\ e^{j2\psi_k},\ \cdots,\ e^{j(M-1)\psi_k}\right]^\top
$$

对比两者，可以发现一个精确的关系：

$$
\mathbf{a}_2(\theta_k) = e^{j\psi_k}\,\mathbf{a}_1(\theta_k)
$$

子阵 2 的导向矢量就是子阵 1 的导向矢量乘以一个纯相位因子 $\phi_k = e^{j\psi_k}$。这个相位因子直接携带了方向信息——只要知道 $\phi_k$，就能反算出 $\psi_k$，进而求出 $\theta_k$：

$$
\hat{\theta}_k = \arcsin\!\left(\frac{\angle \phi_k}{2\pi d / \lambda}\right)
$$

这就是 ESPRIT 的物理核心：**利用两个平移子阵之间的相位旋转关系来定位信号方向**。问题变成了——如何从数据中估计出这 $K$ 个相位因子 $\phi_1, \phi_2, \cdots, \phi_K$？

---

### 2.4.2 从子阵到信号子空间：旋转不变方程

把两个子阵的观测矩阵分别记为 $\mathbf{X}_1$（取数据矩阵 $\mathbf{X}$ 的前 $M-1$ 行）和 $\mathbf{X}_2$（取后 $M-1$ 行），则两者满足：

$$
\mathbf{X}_1 = \mathbf{A}_1 \mathbf{S} + \mathbf{N}_1
$$
$$
\mathbf{X}_2 = \mathbf{A}_2 \mathbf{S} + \mathbf{N}_2 = \mathbf{A}_1 \boldsymbol{\Phi} \mathbf{S} + \mathbf{N}_2
$$

其中 $\mathbf{A}_1 = [\mathbf{a}_1(\theta_1), \cdots, \mathbf{a}_1(\theta_K)]$，$\boldsymbol{\Phi} = \mathrm{diag}(\phi_1, \phi_2, \cdots, \phi_K)$ 是 $K \times K$ 的对角矩阵，对角元素就是我们要求的各信源相位旋转因子。

现在，联系信号子空间的性质。2.1 节证明了，信号子空间 $\mathrm{span}(\mathbf{U}_s)$ 与导向矢量矩阵的列空间相同。对于子阵 1 和子阵 2，分别提取各自的信号子空间矩阵 $\mathbf{U}_{s1}$（由 $\hat{\mathbf{R}}$ 的前 $M-1$ 行/列定义的子矩阵）和 $\mathbf{U}_{s2}$——但实际实现中，更简洁的做法是：直接对整体协方差矩阵 $\hat{\mathbf{R}}$ 做特征值分解，取信号子空间矩阵 $\hat{\mathbf{U}}_s$（$M \times K$），然后把它按行分成两块：

$$
\hat{\mathbf{U}}_{s1} = \hat{\mathbf{U}}_s[1:M-1,\ :] \quad \text{（前 $M-1$ 行）}
$$
$$
\hat{\mathbf{U}}_{s2} = \hat{\mathbf{U}}_s[2:M,\ :] \quad \text{（后 $M-1$ 行）}
$$

由于 $\mathrm{span}(\mathbf{U}_s) = \mathrm{span}(\mathbf{A})$，存在一个非奇异的 $K \times K$ 变换矩阵 $\mathbf{T}$，使得 $\mathbf{U}_s = \mathbf{A}_1 \mathbf{T}$（在子阵 1 的坐标系下）。由此可以推导出：

$$
\mathbf{U}_{s2} = \mathbf{A}_2 \mathbf{T} = \mathbf{A}_1 \boldsymbol{\Phi} \mathbf{T} = \mathbf{U}_{s1} \cdot \underbrace{\mathbf{T}^{-1}\boldsymbol{\Phi}\mathbf{T}}_{\boldsymbol{\Psi}}
$$

这就是 **ESPRIT 的核心方程**：

$$
\boxed{\mathbf{U}_{s2} = \mathbf{U}_{s1}\,\boldsymbol{\Psi}}
$$

其中 $\boldsymbol{\Psi} = \mathbf{T}^{-1}\boldsymbol{\Phi}\mathbf{T}$ 是 $\boldsymbol{\Phi}$ 的相似变换。由于相似变换不改变特征值，$\boldsymbol{\Psi}$ 的特征值与 $\boldsymbol{\Phi}$ 完全相同，正是 $\phi_1, \phi_2, \cdots, \phi_K$。

因此，求 DOA 的问题转化为了三步代数运算：**求 $\boldsymbol{\Psi}$，然后对 $\boldsymbol{\Psi}$ 做特征值分解，从特征值的相位读出方向角**。整个过程不需要任何角度搜索。

---

### 2.4.3 最小二乘（LS）与总体最小二乘（TLS）求解

在实际中，由于有限快拍带来的估计误差，$\hat{\mathbf{U}}_{s2} \approx \hat{\mathbf{U}}_{s1}\boldsymbol{\Psi}$ 只是近似成立。如何从这个近似方程中最优地估计 $\boldsymbol{\Psi}$，是 ESPRIT 实现的关键。

**最小二乘（LS-ESPRIT）**：把 $\hat{\mathbf{U}}_{s2} = \hat{\mathbf{U}}_{s1}\boldsymbol{\Psi}$ 看作一个超定线性方程组，$\hat{\mathbf{U}}_{s1}$ 已知、$\boldsymbol{\Psi}$ 未知，以最小化残差 $\|\hat{\mathbf{U}}_{s2} - \hat{\mathbf{U}}_{s1}\boldsymbol{\Psi}\|_F^2$ 为目标，得到最小二乘解：

$$
\hat{\boldsymbol{\Psi}}_{\text{LS}} = \hat{\mathbf{U}}_{s1}^\dagger\,\hat{\mathbf{U}}_{s2} = (\hat{\mathbf{U}}_{s1}^H\hat{\mathbf{U}}_{s1})^{-1}\hat{\mathbf{U}}_{s1}^H\hat{\mathbf{U}}_{s2}
$$

其中 $\hat{\mathbf{U}}_{s1}^\dagger$ 是 $\hat{\mathbf{U}}_{s1}$ 的 Moore-Penrose 伪逆。

LS 方法假设 $\hat{\mathbf{U}}_{s1}$ 是精确的，只有 $\hat{\mathbf{U}}_{s2}$ 含有误差。但实际上两者都来自同一个有误差的样本协方差矩阵，误差是对称的。**总体最小二乘（TLS-ESPRIT）**正是为解决这一不对称性而设计的，它同时考虑了 $\hat{\mathbf{U}}_{s1}$ 和 $\hat{\mathbf{U}}_{s2}$ 的误差。

TLS 的实现方法是对拼接矩阵 $\mathbf{C} = [\hat{\mathbf{U}}_{s1},\ \hat{\mathbf{U}}_{s2}]$（$(M-1) \times 2K$ 矩阵）做 SVD，取最小 $K$ 个奇异值对应的右奇异向量，分块后求解 $\boldsymbol{\Psi}$。TLS 在理论上比 LS 更接近最优，实践中在中等快拍数时性能也略优。

对初学者而言，LS 方法代码更直接、更易理解，性能已经相当好，建议从 LS 入手；理解原理后再切换至 TLS 只需改动几行。

---

### 2.4.4 ESPRIT 的完整算法流程与代码

把上述推导整理成算法步骤：

**第一步**：计算样本协方差矩阵 $\hat{\mathbf{R}} = \frac{1}{N}\mathbf{X}\mathbf{X}^H$

**第二步**：特征值分解，取信号子空间矩阵 $\hat{\mathbf{U}}_s$（$M \times K$，对应最大 $K$ 个特征值）

**第三步**：按行分块，提取两个子阵的信号子空间

$$\hat{\mathbf{U}}_{s1} = \hat{\mathbf{U}}_s[0:M-1,\ :],\quad \hat{\mathbf{U}}_{s2} = \hat{\mathbf{U}}_s[1:M,\ :]$$

**第四步**：用 LS 或 TLS 求解旋转矩阵 $\hat{\boldsymbol{\Psi}}$

**第五步**：对 $\hat{\boldsymbol{\Psi}}$ 做特征值分解，取 $K$ 个特征值 $\{\hat{\phi}_k\}$

**第六步**：从特征值相位反算 DOA

$$\hat{\theta}_k = \arcsin\!\left(\frac{\angle\hat{\phi}_k}{2\pi d}\right), \quad k = 1, \cdots, K$$

下面是完整的 Python 实现，同时包含 LS 和 TLS 两个版本：

```python
import numpy as np

def esprit(R_hat, K, d=0.5, method='TLS'):
    """
    ESPRIT 算法（适用于 ULA）
    参数：
        R_hat  : 样本协方差矩阵，(M, M)
        K      : 信源数
        d      : 阵元间距（波长归一化，默认 0.5）
        method : 'LS' 或 'TLS'（默认 TLS）
    返回：
        doa_est : 估计 DOA（度），升序排列，长度为 K
    """
    M = R_hat.shape[0]

    # 第二步：特征值分解，取信号子空间（eigh 输出升序，取后 K 列）
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_s = eigvecs[:, -K:]           # (M, K)，对应最大 K 个特征值

    # 第三步：按行分块
    U_s1 = U_s[:-1, :]             # (M-1, K)
    U_s2 = U_s[1:, :]              # (M-1, K)

    # 第四步：求旋转矩阵 Psi
    if method == 'LS':
        # LS：Psi = pinv(U_s1) @ U_s2
        Psi = np.linalg.lstsq(U_s1, U_s2, rcond=None)[0]

    else:  # TLS
        # TLS：对 [U_s1, U_s2] 做 SVD，取最小 K 个奇异值的右奇异向量
        C = np.hstack([U_s1, U_s2])         # (M-1, 2K)
        _, _, Vh = np.linalg.svd(C)
        V = Vh.conj().T                     # (2K, 2K)
        V12 = V[:K, K:]                     # K × K
        V22 = V[K:, K:]                     # K × K
        Psi = -V12 @ np.linalg.inv(V22)

    # 第五步：对 Psi 做特征值分解
    eigenvalues = np.linalg.eigvals(Psi)    # 长度为 K

    # 第六步：从特征值相位反算角度
    psi_est = np.angle(eigenvalues)                     # 相位
    sin_theta = psi_est / (2 * np.pi * d)
    sin_theta = np.clip(sin_theta, -1.0, 1.0)           # 防止数值越界
    doa_est = np.rad2deg(np.arcsin(sin_theta))

    return np.sort(doa_est)


# ============================================================
# 仿真验证：与 MUSIC 对比
# ============================================================
import matplotlib.pyplot as plt

def steering_vector(theta_deg, M, d=0.5):
    theta = np.deg2rad(theta_deg)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * np.arange(M))

M = 8
K = 2
d = 0.5
thetas_true = np.array([20.0, 35.0])
SNR_dB = 10
N = 200

rng = np.random.default_rng(42)
A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
sig_pow = 10 ** (SNR_dB / 10)
S = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N)) +
                              1j * rng.standard_normal((K, N)))
noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N)) +
                              1j * rng.standard_normal((M, N)))
X = A @ S + noise
R_hat = (X @ X.conj().T) / N

doa_ls  = esprit(R_hat, K, d, method='LS')
doa_tls = esprit(R_hat, K, d, method='TLS')

print(f"真实 DOA：{thetas_true}°")
print(f"LS-ESPRIT  估计：{doa_ls.round(2)}°")
print(f"TLS-ESPRIT 估计：{doa_tls.round(2)}°")
```

运行后你将看到，ESPRIT 无需任何角度扫描，直接输出两个数值，与真实方向非常接近。整个计算过程只涉及矩阵分解和一次小矩阵的特征值求解，速度远比逐点扫描的 MUSIC 快。

---

### 2.4.5 ESPRIT 与 MUSIC 的深层比较

同学们可能会问：MUSIC 和 ESPRIT 都是子空间方法，都能实现超分辨率，究竟有什么本质区别？两者的核心差异可以用一句话概括：**MUSIC 利用噪声子空间的正交性做"方向检验"，ESPRIT 利用信号子空间的旋转不变性做"方程求解"**。

这一差异带来了几个具体的实践影响，值得细看：

**不需要谱搜索**。ESPRIT 直接求解代数方程，不依赖角度网格，估计精度不受离散化限制，在这一点上优于标准 MUSIC（但与 Root-MUSIC 相当）。

**不需要导向矢量的显式函数形式**。MUSIC 在谱搜索时，每个候选角度都需要计算 $\mathbf{a}(\theta)$，这要求我们知道阵列的精确几何关系。ESPRIT 的计算完全在子空间内部进行，只利用了"两个子阵之间存在相位旋转"这一结构性约束，而不需要知道 $\mathbf{a}(\theta)$ 的显式表达——这意味着 ESPRIT 对阵元方向图、互耦误差等建模误差有更好的鲁棒性。

**仅适用于具有移不变结构的阵列**。ESPRIT 的核心假设是两个子阵之间存在精确的平移关系。对于 ULA，这天然成立；但对于非均匀阵列、圆形阵列等不满足移不变性的阵型，标准 ESPRIT 不能直接使用（需要扩展变体），而 MUSIC 只要知道各阵元的方向图就可以工作。

**计算复杂度更低**。ESPRIT 的主要计算来自特征值分解（$O(M^3)$）和一次小矩阵特征值求解（$O(K^3)$），省去了谱搜索的 $O(M \cdot I)$ 部分。当角度网格点数 $I$ 很大时，ESPRIT 的计算优势明显。

**统计性能相当**。在大快拍数、高 SNR 条件下，LS-ESPRIT 和 TLS-ESPRIT 均是渐近有效的（RMSE 趋近于 CRB），与 MUSIC 相当。低 SNR 或少快拍时，两者都存在阈值效应，性能相差不大。

下面用蒙特卡洛仿真直观对比 ESPRIT 和 MUSIC 的 RMSE 随 SNR 的变化：

```python
import numpy as np

def music_estimate(R_hat, K, theta_grid, M, d=0.5):
    """简化版 MUSIC，返回前 K 个峰值对应的角度"""
    from scipy.signal import find_peaks
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    En = U_n @ U_n.conj().T
    spec = np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj()
               @ En @ steering_vector(th, M, d)) + 1e-12)
        for th in theta_grid
    ])
    peaks, _ = find_peaks(spec)
    if len(peaks) < K:
        return np.sort(theta_grid[np.argsort(spec)[-K:]])
    top = peaks[np.argsort(spec[peaks])[-K:]]
    return np.sort(theta_grid[top])

M, K, d = 8, 2, 0.5
thetas_true = np.array([20.0, 38.0])
theta_grid  = np.linspace(-90, 90, 1801)
N_snap      = 200
N_trials    = 300
snr_range   = np.arange(-5, 21, 5)

rmse_music  = []
rmse_esprit = []

for snr_dB in snr_range:
    sig_pow = 10 ** (snr_dB / 10)
    err_m, err_e = [], []
    rng = np.random.default_rng(0)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])

    for _ in range(N_trials):
        S = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N_snap)) +
                                     1j * rng.standard_normal((K, N_snap)))
        noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N_snap)) +
                                     1j * rng.standard_normal((M, N_snap)))
        X = A @ S + noise
        R = (X @ X.conj().T) / N_snap

        try:
            est_m = music_estimate(R, K, theta_grid, M, d)
            if len(est_m) == K:
                err_m.append(np.mean((est_m - thetas_true) ** 2))
        except Exception:
            pass

        try:
            est_e = esprit(R, K, d, method='TLS')
            if len(est_e) == K:
                err_e.append(np.mean((est_e - thetas_true) ** 2))
        except Exception:
            pass

    rmse_music.append(np.sqrt(np.mean(err_m)) if err_m else np.nan)
    rmse_esprit.append(np.sqrt(np.mean(err_e)) if err_e else np.nan)

import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.semilogy(snr_range, rmse_music,  'o-',  label='MUSIC')
plt.semilogy(snr_range, rmse_esprit, 's--', label='TLS-ESPRIT')
plt.xlabel('SNR（dB）')
plt.ylabel('RMSE（度）')
plt.title(f'MUSIC vs ESPRIT（M={M}, N={N_snap}）')
plt.legend()
plt.grid(True, which='both')
plt.tight_layout()
plt.show()
```

运行结果会显示：在中高 SNR 区间，两条曲线高度重合，性能相当；在低 SNR 的阈值附近，两者都出现 RMSE 跳升，行为相似。这证实了两种算法在渐近性能上的等价性——选择哪一个，主要取决于应用场景对计算速度、阵型灵活性和实现复杂度的不同侧重。

---

### 2.4.6 几个实现细节的提醒

**特征值的配对问题**。ESPRIT 输出的是 $K$ 个特征值，每个特征值对应一个信源。由于特征值分解的结果是无序的，输出的 DOA 顺序不一定与信源的"物理顺序"（如按角度从小到大）对应。代码中用 `np.sort()` 对结果排序，仅保证输出角度升序，并不保证与真实信源一一对应——在需要追踪特定信源的应用中，需要额外的配对逻辑。

**角度越界的处理**。由 $\hat{\phi}_k$ 的相位反算 $\sin\theta$ 时，数值误差可能导致 $|\sin\theta| > 1$（物理上不可能），需要用 `np.clip` 截断，否则 `arcsin` 会报错。这在低 SNR 或少快拍时尤其容易发生。

**子空间的提取方式**。本节实现中，$\hat{\mathbf{U}}_s$ 直接取整体协方差矩阵的前 $K$ 个最大特征向量，再按行分块。另一种等价做法是分别对两个子阵数据构造各自的协方差矩阵，再提取信号子空间——两种方式在大快拍数时结果接近，本节的做法更简洁，推荐使用。

---

### 2.4.7 小结

ESPRIT 算法为子空间方法家族提供了一个计算上更高效、对建模误差更鲁棒的选择。

**原理层面**：ESPRIT 利用 ULA 两个平移子阵之间的旋转不变性，将 DOA 估计转化为对小矩阵 $\boldsymbol{\Psi}$ 的特征值求解问题。$\boldsymbol{\Psi}$ 的特征值 $\phi_k = e^{j\psi_k}$ 的相位直接对应信号方向，完全绕开角度搜索。

**实现层面**：算法流程是"协方差矩阵 → 特征值分解 → 行分块 → 求 $\boldsymbol{\Psi}$（LS 或 TLS）→ 特征值分解 → 反算角度"，代码简洁，适合在快速原型系统中使用。TLS 版本比 LS 更严谨，工程中优先选用。

**与 MUSIC 的比较**：两者在渐近统计性能上相当，均可接近 CRB。ESPRIT 不需要谱搜索、不依赖导向矢量显式形式，计算量更小；MUSIC 适用范围更广，不要求阵列具有移不变结构。实际工程中，两者经常并行使用，互相验证。

至此，两大经典超分辨率算法——MUSIC 与 ESPRIT——已经完整呈现。但还有一个实际场景我们尚未处理：如果信号源之间存在相干性，两种算法都会遭遇严重的性能下降。这就是下一节——相干信号与空间平滑处理——要解决的问题。
