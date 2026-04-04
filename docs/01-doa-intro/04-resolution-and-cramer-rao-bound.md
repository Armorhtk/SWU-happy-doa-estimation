---
id: doa-intro-resolution-and-cramer-rao-bound
title: 1.4 分辨率问题与克拉美—罗下界
slug: /doa-intro/resolution-and-cramer-rao-bound
---

## 1.4 分辨率问题与克拉美—罗下界

上一节末尾留下了一个悬念：常规波束形成的分辨率受孔径限制，两个角度相近的信号源可能无法被区分。这引出了两个紧密相关的问题：

**第一**，分辨率的瓶颈究竟在哪里？为什么常规方法会受限，而第二章的子空间算法能够突破？

**第二**，就算算法再好，估计精度总有一个物理极限。这个极限是多少？由什么决定？

这两个问题，正是本节要回答的。前者引出**空间谱分辨率**的本质理解，后者引出统计估计理论中的经典工具——**克拉美—罗下界**（Cramér-Rao Bound，CRB）。

---

### 1.4.1 什么是分辨率问题

先把问题说清楚。所谓分辨率，是指算法**区分两个角度相近的信号源**的能力。如果两个信号源的入射角分别为 $\theta_1$ 和 $\theta_2$，角度差 $\Delta\theta = |\theta_1 - \theta_2|$ 越小，区分难度越大。

在上一节，我们看到常规波束形成的空间谱在真实方向 $\theta_0$ 附近产生一个宽度约为 $\lambda/(Md)$ 的主瓣。当两个信号源的角度差 $\Delta\theta$ 小于这个主瓣宽度时，两个峰会融合成一个，算法无法区分它们——这就是**瑞利分辨率限制**。

为什么会这样？根本原因在于，常规波束形成本质上是在做空间域的**傅里叶变换**：把角度 $\theta$ 映射为空间频率 $\psi = (2\pi d / \lambda)\sin\theta$，然后对离散的 $M$ 个阵元做 DFT。大家学习信号处理时一定见过时域的分辨率限制：对 $N$ 个时域样本做 DFT，频率分辨率是 $1/N$。完全类比地，对 $M$ 个空域样本（阵元）做 DFT，空间频率分辨率是 $1/M$，折算成角度就是那个 $\lambda/(Md)$ 的主瓣宽度。

**这个限制是傅里叶变换本身决定的，不是算法设计的问题。** 只要坚持用傅里叶方法，孔径有限就必然带来这个下限，不管你的工程技巧多高超。

那么，超分辨率方法（如 MUSIC、ESPRIT）为什么能突破它？答案是：这些方法不再把 DOA 估计当成傅里叶分析问题，而是把它看作一个**参数化的统计估计问题**——充分利用了阵列数据满足特定物理模型这一先验信息。只要信噪比足够高、快拍数足够多，参数估计的精度可以远超傅里叶分辨率限制。

当然，"参数估计也有极限"——这就是克拉美—罗下界要告诉我们的。

---

### 1.4.2 克拉美—罗下界：估计精度的理论地板

**克拉美—罗下界**（Cramér-Rao Bound，CRB）是数理统计中的一个基本定理，它给出了任何**无偏估计量**方差的下界：无论你用什么算法，只要它是无偏的，其估计误差的方差就不可能低于 CRB。

> **什么是无偏估计？** 如果一个估计量 $\hat{\theta}$ 在统计意义上没有系统偏差，即 $\mathbb{E}[\hat{\theta}] = \theta$（期望等于真值），则称它是无偏估计。CRB 是针对无偏估计给出的下界，有偏估计不受此约束，但有偏估计在实际中往往更难分析和使用。

CRB 的表述如下：对于从含噪数据 $\mathbf{x}$ 中估计参数 $\theta$ 的问题，任何无偏估计量 $\hat{\theta}$ 的方差满足：

$$
\text{var}(\hat{\theta}) \geq \left[\mathbf{J}(\theta)\right]^{-1}
$$

其中 $\mathbf{J}(\theta)$ 是**费希尔信息矩阵**（Fisher Information Matrix，FIM）。对于单个标量参数，费希尔信息量定义为：

$$
J(\theta) = -\mathbb{E}\left[\frac{\partial^2}{\partial\theta^2}\ln f(\mathbf{x};\theta)\right]
$$

这里 $f(\mathbf{x};\theta)$ 是观测数据的概率密度函数（在已知参数 $\theta$ 下的似然函数）。

费希尔信息量的直观含义是：**似然函数关于参数的曲率越大，数据中包含的关于该参数的信息量越多，估计精度的理论极限越高**。如果似然函数在真值附近非常"尖锐"（曲率大），就意味着稍微偏离真值时似然就大幅下降，参数因此容易被精确定位。反之，如果似然函数很"平坦"，参数就难以确定。

---

### 1.4.3 单信源 DOA 估计的 CRB 推导

我们来推导单个信号源情形下 DOA 估计的 CRB，这是最清晰的情形，结论也最有物理直觉。

**数据模型**：单个信源，方向 $\phi$，复振幅 $\alpha = ae^{jb}$（幅度 $a$、相位 $b$），阵列观测为：

$$
\mathbf{x} = \alpha\,\mathbf{a}(\phi) + \mathbf{n}, \quad \mathbf{n} \sim \mathcal{CN}(\mathbf{0}, \sigma^2\mathbf{I})
$$

未知参数向量为 $\boldsymbol{\theta} = [a, b, \phi]^\top$，其中 $a$、$b$ 是我们不关心但必须考虑的**冗余参数**（nuisance parameter），$\phi$ 才是真正想估计的 DOA。

经过推导（过程涉及对高斯似然函数求二阶导数并取期望，此处略去细节），费希尔信息矩阵中与 $\phi$ 相关的元素为：

$$
J_{\phi\phi} = \frac{2a^2}{\sigma^2}\,\mathbf{a}_1^H(\phi)\,\mathbf{a}_1(\phi)
$$

其中 $\mathbf{a}_1(\phi) = \frac{\partial \mathbf{a}(\phi)}{\partial \phi}$ 是导向矢量对方向角的导数。可以证明，$\phi$ 与 $a$、$b$ 之间的费希尔信息交叉项均为零，因此 $\phi$ 的 CRB 就等于 $J_{\phi\phi}^{-1}$：

$$
\text{CRB}(\phi) = \frac{\sigma^2}{2a^2\,\|\mathbf{a}_1(\phi)\|^2}
$$

对 ULA 而言，导向矢量各分量为 $[\mathbf{a}(\phi)]_m = e^{j(m-1)\psi}$，$\psi = (2\pi d/\lambda)\sin\phi$，对 $\phi$ 求导得：

$$
[\mathbf{a}_1(\phi)]_m = j(m-1)\frac{2\pi d}{\lambda}\cos\phi \cdot e^{j(m-1)\psi}
$$

因此：

$$
\|\mathbf{a}_1(\phi)\|^2 = \left(\frac{2\pi d}{\lambda}\right)^2\cos^2\phi \sum_{m=1}^{M}(m-1)^2 = \left(\frac{2\pi d}{\lambda}\right)^2\cos^2\phi \cdot B^2
$$

其中 $B^2 = \sum_{m=0}^{M-1} m^2 = \frac{M(M-1)(2M-1)}{6}$，当 $M$ 较大时近似为 $B^2 \approx M^3/3$。

记信噪比 $\text{SNR} = a^2/\sigma^2$（单阵元信号功率与噪声功率之比），代入并整理，对 $N$ 个快拍下的 CRB 为：

$$
\boxed{\text{CRB}(\phi) \approx \frac{1}{2N \cdot \text{SNR}} \cdot \frac{1}{\left(\frac{2\pi d}{\lambda}\right)^2 \cos^2\phi \cdot B^2}}
$$

这个结果包含了三方面信息，读起来非常有物理感，值得逐条体会。

---

### 1.4.4 CRB 的物理解读

**信噪比越高，CRB 越小。** 分母中有 $\text{SNR}$ 项，信噪比越高，理论估计精度越好。这完全符合直觉：信号越强，噪声相对越小，方向越容易定准。

**快拍数越多，CRB 越小。** 分母中有 $N$，快拍数翻倍，CRB 减半，对应估计标准差下降为原来的 $1/\sqrt{2}$。这体现了统计估计的基本规律：更多观测带来更高精度。

**阵列孔径越大，CRB 越小。** 分母中有 $B^2 \propto M^3$，这是最关键的一项。当阵元数 $M$ 翻倍（阵列孔径加倍）时，$B^2$ 增大为原来的约 $8$ 倍，CRB 下降至约 $1/8$，对应估计标准差减小至约 $1/(2\sqrt{2})$。**孔径对精度的影响远比快拍数更显著**——这正是工程上宁愿增加天线数量、扩大阵列孔径的根本原因。

**偏离正侧射方向时，CRB 变大。** 分母中有 $\cos^2\phi$，当 $\phi$ 趋近 $\pm 90°$（端射方向）时，$\cos\phi \to 0$，CRB 趋向无穷大。这说明对端射方向的目标，DOA 估计从理论上就很困难——因为在端射方向附近，导向矢量对角度的变化不再敏感，小角度变化几乎不改变各阵元的相位差。

下面用代码直观地展示 CRB 随 SNR 和快拍数的变化规律：

```python
import numpy as np
import matplotlib.pyplot as plt

# 阵列参数
M = 8           # 阵元数
d = 0.5         # 阵元间距（波长归一化，λ/2）
phi = np.deg2rad(30)  # 入射角 30°

# B² = Σ m², m = 0,...,M-1
B2 = sum(m**2 for m in range(M))

# CRB(phi) 计算函数（单位：弧度²）
def crb_rad2(SNR_linear, N, phi, d, B2):
    denom = 2 * N * SNR_linear * (2 * np.pi * d)**2 * np.cos(phi)**2 * B2
    return 1.0 / denom

# 1. CRB vs SNR（固定 N=100）
snr_dB = np.linspace(-10, 30, 200)
snr_lin = 10**(snr_dB / 10)
N_fix = 100
crb_vs_snr = np.sqrt(crb_rad2(snr_lin, N_fix, phi, d, B2))
crb_vs_snr_deg = np.rad2deg(crb_vs_snr)

# 2. CRB vs N（固定 SNR=0 dB）
N_arr = np.logspace(1, 4, 200)
snr_fix = 1.0   # 0 dB
crb_vs_N = np.sqrt(crb_rad2(snr_fix, N_arr, phi, d, B2))
crb_vs_N_deg = np.rad2deg(crb_vs_N)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].semilogy(snr_dB, crb_vs_snr_deg)
axes[0].set_xlabel('信噪比 SNR（dB）')
axes[0].set_ylabel('CRB 标准差（度）')
axes[0].set_title(f'CRB vs SNR（M={M}, N={N_fix}, φ=30°）')
axes[0].grid(True, which='both')

axes[1].loglog(N_arr, crb_vs_N_deg)
axes[1].set_xlabel('快拍数 N')
axes[1].set_ylabel('CRB 标准差（度）')
axes[1].set_title(f'CRB vs 快拍数（M={M}, SNR=0 dB, φ=30°）')
axes[1].grid(True, which='both')

plt.tight_layout()
plt.show()
```

运行这段代码，你会看到两条典型的双对数或半对数直线：CRB 标准差随 SNR 每增加 20 dB 下降约 10 倍，随快拍数每增加 100 倍下降约 10 倍（斜率 $-1/2$）。这正是理论公式中 SNR 和 $N$ 各贡献一个倒数的直接体现。

---

### 1.4.5 CRB 的意义：评价算法的标尺

CRB 最重要的工程意义不只是"告诉你极限在哪"，而是提供了一把**评价算法性能的客观标尺**。

对于一个具体的 DOA 算法，我们通常通过蒙特卡洛仿真（重复运行若干次、取 RMSE）来评估其实际性能，然后与 CRB 比较：

- 如果算法的 RMSE 与 $\sqrt{\text{CRB}}$ 非常接近，则说明该算法几乎达到了最优，没有太多改进空间；
- 如果 RMSE 远大于 $\sqrt{\text{CRB}}$，则说明算法有明显的性能损失，可能存在改进余地；
- 如果 RMSE 低于 $\sqrt{\text{CRB}}$，则算法一定是有偏估计，或者仿真/推导存在错误。

在高 SNR、大快拍数条件下，MUSIC 和 ESPRIT 等经典算法的 RMSE 能够非常接近 CRB，这被称为算法是**渐近有效的**（asymptotically efficient）。这正是子空间方法备受重视的理论依据之一——它们不仅分辨率高，统计效率也接近最优。

---

### 1.4.6 从 CRB 看超分辨率的本质

现在我们可以回头把两个问题连起来。

常规波束形成受瑞利分辨率限制（约 $\lambda/Md$），这是**傅里叶分析本身的局限**，与统计估计精度是两回事。CRB 则揭示了：在参数化模型下，只要信噪比足够高，角度估计精度可以做到远比 $\lambda/Md$ 精细——理论上没有"分辨率下限"，精度随 SNR 和快拍数持续提升。

但 CRB 同时也告诉我们：在低 SNR 或少快拍条件下，精度会急剧恶化，最终算法会出现所谓的**阈值效应**（threshold effect）——在某个 SNR 阈值以下，估计误差突然跳离 CRB，算法失效。这个行为在所有超分辨率算法中都存在，是实际应用中必须考量的性能拐点。

换句话说：**超分辨率算法不是"免费的"，它们用对信号模型结构的充分利用换来高精度，代价是对噪声和模型误差更为敏感**。理解这一点，对后续学习 MUSIC、ESPRIT 以及深度学习方法都至关重要。

---

### 小结

本节从两个角度理解了 DOA 估计的基本极限：

**分辨率角度**：常规波束形成的分辨率受孔径限制，约为 $\lambda/(Md\cos\theta)$。这是傅里叶分析框架下不可突破的瑞利极限。子空间方法通过参数化建模绕开这一限制，实现超分辨率估计。

**统计估计角度**：CRB 给出了任意无偏估计量的方差下界。对于单信源 ULA 情形，CRB 正比于 $1/(N \cdot \text{SNR} \cdot M^3 \cdot \cos^2\phi)$，揭示了快拍数、信噪比、阵列孔径和入射角对估计精度的定量影响。CRB 也是衡量算法性能优劣的标尺——渐近有效的算法在高 SNR 下可达到 CRB。

至此，第一章的四节内容构成了一个完整的基础框架：从阵列几何和观测模型（1.1 节）、到信号物理假设和导向矢量（1.2 节）、再到统计工具和基础算法（1.3 节）、最后到性能极限与评价标准（1.4 节）。

带着这套框架，我们正式进入第二章——经典 DOA 估计算法。我们将看到，MUSIC 和 ESPRIT 是如何从协方差矩阵的特征结构出发，突破瑞利限制、逼近 CRB 的。


## 📦 本章代码与动手实践

学完第一章的概念和公式之后，最好的巩固方式就是亲手跑一遍。本节把前四节的核心代码整合成一个完整的仿真脚本，从构造阵列、生成数据，到估计协方差矩阵、绘制空间谱、标注 CRB，一气呵成。

代码设计上尽量保持结构清晰、注释完整，方便大家在此基础上修改和实验。

---

### 完整仿真脚本

```python
"""
第一章综合仿真：ULA 阵列观测模型 + 常规波束形成 + CRB 参考线
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 第一部分：阵列参数与信号参数
# ============================================================

M       = 8       # 阵元数
d       = 0.5     # 阵元间距（半波长，以波长为单位）
N       = 200     # 快拍数
SNR_dB  = 10      # 信噪比（dB）
thetas  = [30, 50]  # 信号源真实入射角（度），可设置多个

SNR_lin = 10 ** (SNR_dB / 10)   # 线性信噪比
sigma2  = 1.0                    # 噪声功率（固定为 1，信号功率由 SNR 决定）
sig_pow = SNR_lin * sigma2       # 每个信源的信号功率

# ============================================================
# 第二部分：导向矢量与阵列流形矩阵
# ============================================================

def steering_vector(theta_deg, M, d):
    """计算 ULA 导向矢量"""
    theta = np.deg2rad(theta_deg)
    psi   = 2 * np.pi * d * np.sin(theta)
    m     = np.arange(M)
    return np.exp(1j * m * psi)

# 构造阵列流形矩阵 A，列为各信源导向矢量
A = np.column_stack([steering_vector(th, M, d) for th in thetas])
K = len(thetas)   # 信源数

# ============================================================
# 第三部分：生成多快拍仿真数据
# ============================================================

rng = np.random.default_rng(seed=42)

# 各信源独立的复高斯信号，功率归一化后乘以 sqrt(sig_pow)
S = np.sqrt(sig_pow / 2) * (
    rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N))
)

# 加性复高斯白噪声，功率 sigma2
noise = np.sqrt(sigma2 / 2) * (
    rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
)

# 阵列观测矩阵：(M, N)
X = A @ S + noise

# ============================================================
# 第四部分：样本协方差矩阵
# ============================================================

R_hat = (X @ X.conj().T) / N

# ============================================================
# 第五部分：常规波束形成空间谱
# ============================================================

theta_grid = np.linspace(-90, 90, 1801)   # 扫描网格，步长 0.1°

def cbf_spectrum(R_hat, theta_grid, M, d):
    """常规波束形成：逐角度计算输出功率"""
    spectrum = np.zeros(len(theta_grid))
    for i, th in enumerate(theta_grid):
        a = steering_vector(th, M, d)
        spectrum[i] = np.real(a.conj() @ R_hat @ a)
    return spectrum

spectrum = cbf_spectrum(R_hat, theta_grid, M, d)
spectrum_dB = 10 * np.log10(spectrum / spectrum.max() + 1e-12)

# ============================================================
# 第六部分：CRB 计算（各角度的估计标准差下界）
# ============================================================

def crb_std_deg(theta_deg, M, d, SNR_lin, N):
    """
    返回单信源 DOA 的 CRB 标准差（度）
    公式：CRB(φ) = 1 / [2N·SNR·(2πd)²·cos²φ·B²]
    """
    phi  = np.deg2rad(theta_deg)
    B2   = sum(m**2 for m in range(M))      # Σ m², m=0,...,M-1
    crb  = 1.0 / (2 * N * SNR_lin * (2 * np.pi * d)**2
                  * np.cos(phi)**2 * B2)
    return np.rad2deg(np.sqrt(crb))

# 计算各真实方向的 CRB 标准差
crb_values = [crb_std_deg(th, M, d, SNR_lin, N) for th in thetas]

# ============================================================
# 第七部分：绘图
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# --- 左图：空间谱 ---
ax = axes[0]
ax.plot(theta_grid, spectrum_dB, color='steelblue', linewidth=1.5,
        label='常规波束形成')
for th in thetas:
    ax.axvline(x=th, color='tomato', linestyle='--', linewidth=1.2,
               label=f'真实方向 {th}°')
ax.set_xlabel('角度 θ（度）')
ax.set_ylabel('归一化功率（dB）')
ax.set_title('常规波束形成空间谱')
ax.set_xlim(-90, 90)
ax.set_ylim(-40, 3)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.4)

# --- 右图：CRB 随角度的变化曲线 ---
ax = axes[1]
phi_range = np.linspace(-80, 80, 500)
crb_curve = [crb_std_deg(ph, M, d, SNR_lin, N) for ph in phi_range]
ax.semilogy(phi_range, crb_curve, color='steelblue', linewidth=1.5,
            label=f'CRB 曲线（SNR={SNR_dB} dB, N={N}）')
for th, cv in zip(thetas, crb_values):
    ax.scatter([th], [cv], color='tomato', zorder=5, s=60,
               label=f'θ={th}°: CRB std ≈ {cv:.3f}°')
ax.set_xlabel('入射角度 θ（度）')
ax.set_ylabel('CRB 标准差（度，对数轴）')
ax.set_title('DOA 估计 CRB 随角度变化')
ax.legend(fontsize=8)
ax.grid(True, which='both', alpha=0.4)

plt.tight_layout()
plt.savefig('chapter1_simulation.png', dpi=150)
plt.show()

# ============================================================
# 第八部分：数值汇报
# ============================================================

print("=" * 45)
print("第一章仿真结果汇报")
print("=" * 45)
print(f"阵元数 M = {M}，快拍数 N = {N}，SNR = {SNR_dB} dB")
print(f"阵元间距 d = {d}λ")
print("-" * 45)
for th, cv in zip(thetas, crb_values):
    print(f"  信源 θ = {th:>5.1f}°  |  CRB 标准差 = {cv:.4f}°")
print("=" * 45)
```

---

### 🔬 动手作业

理解一个概念最好的办法，是主动去"破坏"它，看看参数变化会带来什么。下面是几道小作业，每道题只需修改脚本顶部的参数或添加几行代码，观察输出图的变化，思考背后的原因。

---

**作业 1：把两个信源靠近，观察分辨率极限**

把 `thetas = [30, 50]` 改为 `[30, 40]`，再改为 `[30, 35]`，最后改为 `[30, 32]`。

观察空间谱中两个峰的变化：它们从清晰分开，到逐渐靠拢，最终融合成一个峰。

> **思考**：根据 1.3 节中 $\Delta\theta_\text{CBF} \approx \lambda/(Md\cos\theta)$ 的公式，对于 $M=8$、$d=0.5\lambda$、$\theta \approx 30°$，常规波束形成的分辨率约是多少度？你观察到的"合并"临界角间隔与理论值是否吻合？

---

**作业 2：增减阵元数，感受孔径的作用**

分别将 `M` 设为 `4`、`8`、`16`，保持其他参数不变（建议信源间隔设为 `[20, 35]`）。

观察：阵元数增加时，空间谱主瓣如何变化？CRB 标准差下降了多少倍？

> **思考**：CRB 的分母中有 $B^2 \approx M^3/3$，理论上 $M$ 翻倍时 CRB 应下降为原来的几分之一？对照数值汇报中的结果，与理论是否吻合？

---

**作业 3：降低信噪比，观察 CRB 的变化**

将 `SNR_dB` 从 `10` 依次改为 `0`、`-5`、`-10`，同时保持 `N = 200` 不变。

观察空间谱中噪声基底的抬升，以及 CRB 标准差的增长。

> **思考**：SNR 每下降 10 dB（即变为原来的 1/10），CRB 标准差理论上增大多少倍？实际计算结果是否印证这一规律？

---

**作业 4：减少快拍数，观察样本协方差矩阵质量的影响**

固定 `SNR_dB = 10`，将 `N` 从 `200` 依次改为 `50`、`20`、`10`。

重点观察两件事：第一，空间谱的形状是否变得不稳定（每次运行结果可能略有不同）；第二，CRB 随 $N$ 的变化规律。

> **思考**：1.3 节提到"快拍数至少应为阵元数的若干倍"。当 $N < M$（比如 $N=4 < M=8$）时，样本协方差矩阵 $\hat{\mathbf{R}} = \frac{1}{N}\mathbf{X}\mathbf{X}^H$ 的秩是多少？这会对空间谱产生什么影响？（提示：一个秩不足的矩阵意味着什么？）

---

**作业 5：把信源移向端射方向，感受 $\cos^2\phi$ 的效应**

保持 `M=8`、`N=200`、`SNR_dB=10`，将单个信源的角度从 `0°` 逐步改为 `60°`、`75°`、`85°`。

对比不同角度下的 CRB 标准差数值，并观察空间谱主瓣宽度的变化。

> **思考**：CRB 公式中有 $\cos^2\phi$ 项。当 $\phi = 60°$ 与 $\phi = 0°$ 相比，CRB 理论上大多少倍？试用数值汇报中的数据验证这一比值。

---

**作业 6（选做）：增加第三个信源，观察多信源情形**

将 `thetas = [30, 50]` 改为 `[−20, 10, 45]`，保持其他参数不变。

> **思考**：常规波束形成能否同时分辨这三个信源？如果三个信源中有两个角度很近，会发生什么？此外，注意脚本中的 CRB 计算是**单信源**情形下的近似，多信源时 CRB 会更复杂（涉及费希尔信息矩阵的全矩阵形式）——这在本教程中不展开，但可以记住：多信源相互靠近时，CRB 会因为信号之间的耦合而显著增大。

---

完成以上作业之后，你对第一章的几个核心结论——阵列孔径决定分辨率、SNR 和快拍数决定估计精度、端射方向估计更难——应该已经有了不只是"读懂"，而是"亲手验证过"的理解。这种理解会在第二章学习 MUSIC 和 ESPRIT 时给你带来很大帮助。
