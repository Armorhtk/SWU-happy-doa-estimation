---
id: traditional-adaptive-beamforming-capon-mvdr
title: 2.6 自适应波束形成：Capon/MVDR 算法原理与实现
slug: /traditional-methods/adaptive-beamforming-capon-mvdr
---


## 2.6 自适应波束形成：Capon/MVDR 算法原理与实现

在正式进入子空间方法之前（2.1—2.5 节），我们有必要在这里插入一个重要的"过渡台阶"：**自适应波束形成**（adaptive beamforming）。

1.3 节已经介绍了常规波束形成（CBF）：用固定的权矢量 $\mathbf{w} = \mathbf{a}(\phi)$ 对阵列输出做加权求和，哪个方向功率最大就认为信号从哪来。这个方法直觉清晰，但它的权矢量是**数据无关的**——无论当前场景中有没有干扰、信噪比是高是低，权矢量始终不变。正因为如此，CBF 的旁瓣无法自适应地压低，强干扰会通过旁瓣"漏"进来，严重拉偏估计结果，而分辨率也死死受限于阵列孔径。

本节介绍的 **Capon 波束形成器**（也称 MVDR，Minimum Variance Distortionless Response，最小方差无失真响应波束形成器），由 Jack Capon 于 1969 年提出，是将"数据自适应"思想引入空间谱估计的奠基性工作。它的核心变革只有一句话：**在保证目标方向增益不变的前提下，让权矢量随数据自适应调整，最小化总输出功率**。这使得来自其他方向的干扰被自动置零（"打零陷"），从而在抗干扰能力和角度分辨率两个维度上都显著超越 CBF。

---

### 2.6.1 从 CBF 的局限说起

先把问题具体化。CBF 的空间谱是：

$$
P_{\text{CBF}}(\phi) = \mathbf{a}^H(\phi)\,\mathbf{R}\,\mathbf{a}(\phi)
$$

把 $\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}$ 代入，展开可得：

$$
P_{\text{CBF}}(\phi) = \sum_k \sigma_k^2 |\mathbf{a}^H(\phi)\mathbf{a}(\theta_k)|^2 + \sigma^2 M
$$

注意第一项：即使 $\phi$ 瞄准了真实信源 $\theta_1$，其他信源 $\theta_2, \theta_3, \cdots$ 的功率也会通过内积 $|\mathbf{a}^H(\phi)\mathbf{a}(\theta_k)|^2$（即旁瓣响应）叠加进来。当某个干扰信源功率远大于目标信源时，这个"旁瓣泄漏"会在谱上压制目标峰，甚至产生假峰——这就是多信源场景下 CBF 方向估计产生偏差的根本原因。

Capon 的解决思路是：与其被动接受旁瓣响应，不如主动把它压下去。

---

### 2.6.2 Capon 的优化问题：有约束的功率最小化

Capon 波束形成器把权矢量设计转化为一个优化问题。对于每个搜索方向 $\phi$，寻找最优权矢量 $\mathbf{w}(\phi)$，使得：

$$
\min_{\mathbf{w}} \quad \mathbf{w}^H\mathbf{R}\mathbf{w}
$$
$$
\text{s.t.} \quad \mathbf{w}^H\mathbf{a}(\phi) = 1
$$

目标函数 $\mathbf{w}^H\mathbf{R}\mathbf{w}$ 是波束形成器的总输出功率，包含来自所有方向的信号和噪声。约束条件 $\mathbf{w}^H\mathbf{a}(\phi) = 1$ 则保证：从 $\phi$ 方向来的信号经过波束形成后增益恰好为 1，即目标方向的信号"无失真"地通过——这就是"无失真响应"（Distortionless Response）名称的来源。

两个条件合在一起，意味着：**在保留目标方向信号的前提下，尽可能压制其他所有方向（包括干扰）的能量**。这是一个有物理意义的最优化，不是凭空定义的数学游戏。

用拉格朗日乘子法求解（求 $\mathbf{w}$ 对拉格朗日函数的导数并令其为零），可以得到解析的闭合形式：

$$
\mathbf{w}_{\text{Capon}}(\phi) = \frac{\mathbf{R}^{-1}\mathbf{a}(\phi)}{\mathbf{a}^H(\phi)\mathbf{R}^{-1}\mathbf{a}(\phi)}
$$

将最优权矢量代回输出功率表达式，得到 **Capon 空间谱**：

$$
\boxed{P_{\text{Capon}}(\phi) = \frac{1}{\mathbf{a}^H(\phi)\,\mathbf{R}^{-1}\,\mathbf{a}(\phi)}}
$$

对比 CBF 的 $P_{\text{CBF}}(\phi) = \mathbf{a}^H(\phi)\mathbf{R}\mathbf{a}(\phi)$，Capon 谱把 $\mathbf{R}$ 换成了 $\mathbf{R}^{-1}$，分子从内积变为常数 $1$，整个表达式取了倒数。这个结构上的"反转"是自适应能力的来源——$\mathbf{R}^{-1}$ 会对协方差矩阵中强度大的方向（干扰方向）产生强烈的压制作用，让它们在谱上变得极小，而不是像 CBF 那样任由旁瓣放大。

实践中，用样本协方差矩阵 $\hat{\mathbf{R}}$ 代替理论值 $\mathbf{R}$：

$$
\hat{P}_{\text{Capon}}(\phi) = \frac{1}{\mathbf{a}^H(\phi)\,\hat{\mathbf{R}}^{-1}\,\mathbf{a}(\phi)}
$$

同样对 $\phi$ 在 $[-90°, 90°]$ 上扫描，寻找 $K$ 个峰值作为 DOA 估计结果。

---

### 2.6.3 Capon 为何优于 CBF：直观理解

同学们可能会问：把 $\mathbf{R}$ 换成 $\mathbf{R}^{-1}$，这个操作的物理直觉是什么？

可以从两个角度来理解。

**角度一：对高功率方向施加"惩罚"。** 协方差矩阵 $\mathbf{R}$ 在强干扰方向对应的分量较大；取逆之后，$\mathbf{R}^{-1}$ 在那些方向的分量变小。分母 $\mathbf{a}^H(\phi)\mathbf{R}^{-1}\mathbf{a}(\phi)$ 在干扰方向上因此变小，Capon 谱的倒数则在干扰方向变大——等等，这不是应该在干扰方向变小吗？让我们理清一下：干扰方向上 $\mathbf{a}^H\mathbf{R}^{-1}\mathbf{a}$ **并非**简单变小。真正的效果是：最优权矢量 $\mathbf{w}_{\text{Capon}}$ 会把干扰方向的旁瓣自动置零（"自适应零陷"），因此当 $\phi$ 扫过干扰方向时，约束已无法在这里保持目标增益为 1 和最小功率同时成立，谱值因此低于真实信号方向。

**角度二：与白化操作的类比。** 在信号检测理论中，"白化"（whitening）是把观测数据乘以 $\mathbf{R}^{-1/2}$ 以消除噪声/干扰的空间相关性，从而让各向同性地看待所有方向。Capon 的 $\mathbf{R}^{-1}$ 本质上也是在做类似的白化操作——先把数据空间"压扁"到各向同性，再做匹配滤波。这使得不同方向的响应不再受干扰功率强弱的左右，而是更"公平"地反映各方向的真实信号存在情况。

结论：**CBF 是固定孔径的空间傅里叶分析；Capon 是数据驱动的自适应干扰抑制**，在干扰较强时优势尤为明显。

---

### 2.6.4 代码实现与三种方法的谱对比

Capon 谱的实现只比 CBF 多一步矩阵求逆，代码非常简洁：

```python
import numpy as np
import matplotlib.pyplot as plt

def steering_vector(theta_deg, M, d=0.5):
    theta = np.deg2rad(theta_deg)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * np.arange(M))

def capon_spectrum(R_hat, theta_grid, M, d=0.5, diagonal_loading=0.0):
    """
    Capon（MVDR）空间谱
    参数：
        R_hat            : 样本协方差矩阵，(M, M)
        theta_grid       : 角度扫描网格（度）
        M                : 阵元数
        d                : 阵元间距（波长归一化）
        diagonal_loading : 对角加载量 ε（默认 0，即不加载）
    返回：
        spectrum : Capon 谱，与 theta_grid 等长
    """
    # 对角加载：R_loaded = R_hat + ε·I，提升数值稳定性
    R_loaded = R_hat + diagonal_loading * np.eye(M)
    R_inv = np.linalg.inv(R_loaded)

    spectrum = np.zeros(len(theta_grid))
    for i, theta in enumerate(theta_grid):
        a = steering_vector(theta, M, d)
        denom = np.real(a.conj() @ R_inv @ a)
        spectrum[i] = 1.0 / (denom + 1e-12)
    return spectrum

# ============================================================
# 仿真：两个靠近的信源，对比 CBF / Capon / MUSIC
# ============================================================

M, K, d = 8, 2, 0.5
thetas_true = [20.0, 30.0]     # 角度间隔 10°，小于 CBF 分辨率
SNR_dB, N = 15, 300
theta_grid = np.linspace(-90, 90, 1801)

rng = np.random.default_rng(42)
sig_pow = 10 ** (SNR_dB / 10)
A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
S = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N)) +
                              1j * rng.standard_normal((K, N)))
noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N)) +
                              1j * rng.standard_normal((M, N)))
X = A @ S + noise
R_hat = (X @ X.conj().T) / N

# 计算三种谱
spec_cbf = np.array([
    np.real(steering_vector(th, M, d).conj() @ R_hat @ steering_vector(th, M, d))
    for th in theta_grid
])
spec_capon = capon_spectrum(R_hat, theta_grid, M, d)

eigvals, eigvecs = np.linalg.eigh(R_hat)
U_n = eigvecs[:, :-K]
En = U_n @ U_n.conj().T
spec_music = np.array([
    1.0 / (np.real(steering_vector(th, M, d).conj() @ En
                   @ steering_vector(th, M, d)) + 1e-12)
    for th in theta_grid
])

# 归一化（dB）
def to_dB(s):
    return 10 * np.log10(s / s.max() + 1e-10)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(theta_grid, to_dB(spec_cbf),   'b-',  linewidth=1.2, label='CBF')
ax.plot(theta_grid, to_dB(spec_capon), 'g--', linewidth=1.5, label='Capon/MVDR')
ax.plot(theta_grid, to_dB(spec_music), 'r-',  linewidth=1.2, label='MUSIC')
for th in thetas_true:
    ax.axvline(x=th, color='k', linestyle=':', linewidth=1)
ax.set_xlabel('角度 θ（度）')
ax.set_ylabel('归一化幅度（dB）')
ax.set_title(f'三种方法空间谱对比（M={M}, SNR={SNR_dB} dB, Δθ=10°）')
ax.set_xlim([-90, 90])
ax.set_ylim([-35, 2])
ax.legend()
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
```

运行后你将看到：CBF 在 20° 和 30° 处合并为一个宽峰，无法分辨；Capon 谱明显变窄，能分辨出两个独立峰，但峰形比 MUSIC 宽；MUSIC 的峰最尖锐，分辨率最高。这三条曲线直观地展示了三种算法的分辨能力梯度。

---

### 2.6.5 对角加载：实用中的稳定化技巧

Capon 谱的计算涉及矩阵求逆 $\hat{\mathbf{R}}^{-1}$，这带来一个实际问题：当快拍数 $N$ 不足（尤其 $N \leq M$）时，$\hat{\mathbf{R}}$ 可能奇异或近奇异，直接求逆会导致数值极不稳定，Capon 谱出现剧烈振荡甚至崩溃。

应对这一问题的标准做法是**对角加载**（diagonal loading）：在求逆之前，在协方差矩阵的对角线上添加一个小正数 $\varepsilon$：

$$
\hat{\mathbf{R}}_{\text{loaded}} = \hat{\mathbf{R}} + \varepsilon\mathbf{I}
$$

然后对 $\hat{\mathbf{R}}_{\text{loaded}}$ 求逆。对角加载的效果是：将所有特征值至少抬高到 $\varepsilon$，消除了近奇异问题。从贝叶斯角度看，$\varepsilon\mathbf{I}$ 等价于引入了一个先验——假设存在功率为 $\varepsilon$ 的各向同性白噪声，从而让求解更稳健。

$\varepsilon$ 的选取是一个权衡：太小则稳定效果不够，太大则 Capon 谱退化回 CBF（当 $\varepsilon \gg \|\hat{\mathbf{R}}\|$ 时，$\hat{\mathbf{R}}_{\text{loaded}} \approx \varepsilon\mathbf{I}$，$\hat{\mathbf{R}}_{\text{loaded}}^{-1} \approx (1/\varepsilon)\mathbf{I}$，谱退化为 $P \propto \mathbf{a}^H\mathbf{a} = M$，与方向无关）。工程上常用的经验值是 $\varepsilon = \sigma^2$（噪声功率的估计值）或 $\varepsilon = \delta \cdot \text{tr}(\hat{\mathbf{R}})/M$，其中 $\delta \in [0.01, 0.1]$ 是相对加载比例。

---

### 2.6.6 Capon 谱的理论性质

了解 Capon 的两个重要理论性质，有助于在实际中正确使用和解读它。

**性质一：Capon 谱是真实功率谱的下界。** 可以证明，对于真实协方差矩阵 $\mathbf{R}$，Capon 谱满足：

$$
P_{\text{Capon}}(\phi) \leq P_{\text{CBF}}(\phi)
$$

这意味着 Capon 谱在所有方向上都不超过 CBF 谱。更进一步，在真实信号方向 $\theta_k$ 处，Capon 谱近似给出该信源的真实功率 $\sigma_k^2$（在大快拍数、高 SNR 极限下）。这赋予了 Capon 谱一定的功率估计意义，而 MUSIC 伪谱则完全没有功率含义。

**性质二：Capon 谱的分辨率与 CBF 对比。** Capon 谱的主瓣宽度（在 $-3$ dB 处）约为 CBF 的一半。对于 $M$ 阵元 ULA，CBF 分辨率约 $\lambda/(Md)$，Capon 约为 $\lambda/(2Md)$——分辨率提高了约 2 倍。这个提升源于 $\mathbf{R}^{-1}$ 对旁瓣的抑制作用，但仍然受到阵列孔径的根本限制，不能像子空间方法那样实现真正意义上的"超分辨率"。

---

### 2.6.7 Capon 与 MUSIC 的本质差异

站在更高处看，Capon 和 MUSIC 走的是两条本质不同的路。

CBF 和 Capon 都属于**波束形成类方法**（beamforming-based methods）：设计一个权矢量，对阵列输出加权求和，输出功率最大（或最优）的方向就是 DOA 估计值。两者的区别只在于权矢量是否自适应——CBF 固定，Capon 随数据变化。这类方法的共同特点是：谱值有功率量纲（单位瓦特），可以用来估计信源功率，对模型误差和噪声的鲁棒性较好，但分辨率受孔径限制。

MUSIC 和 ESPRIT 属于**子空间类方法**（subspace-based methods）：利用协方差矩阵的特征结构，将观测空间分解为信号子空间和噪声子空间，通过检验正交性或旋转不变性来精确定位方向。这类方法的特点是：伪谱无功率意义，仅用于方向定位；在高 SNR、足够快拍条件下分辨率可以远超孔径限制（超分辨率）；但对模型匹配程度要求更高，低 SNR 或少快拍时性能骤降。

一张简短的对比可以说明它们各自的定位：

| 维度 | CBF | Capon/MVDR | MUSIC/ESPRIT |
|---|---|---|---|
| 方法类型 | 固定波束形成 | 自适应波束形成 | 子空间分解 |
| 分辨率 | 受瑞利限制 | 约为 CBF 的 2 倍 | 超分辨率 |
| 谱的物理意义 | 输出功率（真实） | 近似信源功率 | 无（仅定位用） |
| 低 SNR 鲁棒性 | 最强 | 较强 | 阈值以下骤降 |
| 快拍不足时 | 可用 | 需对角加载 | 可能失效 |
| 对强干扰 | 受旁瓣影响 | 自适应置零 | 取决于 SNR |
| 实现复杂度 | 最低 | 低（仅需矩阵逆） | 中（需特征值分解） |

从这张表可以看到：**Capon 是 CBF 与子空间方法之间一个兼顾鲁棒性与分辨率的中间方案**——它比 CBF 强，但比子空间方法的分辨上限低；比子空间方法鲁棒，但在高 SNR 时精度又不如子空间方法。这种"中间人"定位使得 Capon 在工程实践中有着独特的适用场景，特别是在：快拍数有限（$N$ 接近 $M$）、存在较强干扰且信源角度间隔不太小、对算法鲁棒性要求高于对极限分辨率要求的场合。

---

### 2.6.8 小结

本节系统介绍了 Capon/MVDR 自适应波束形成器。

**原理层面**：Capon 将权矢量设计转化为有约束的优化问题——在目标方向无失真的约束下最小化总输出功率，得到最优权矢量 $\mathbf{w}_{\text{Capon}} = \mathbf{R}^{-1}\mathbf{a}/(\mathbf{a}^H\mathbf{R}^{-1}\mathbf{a})$，对应空间谱 $P_{\text{Capon}}(\phi) = 1/[\mathbf{a}^H(\phi)\mathbf{R}^{-1}\mathbf{a}(\phi)]$。与 CBF 相比，用 $\mathbf{R}^{-1}$ 替换 $\mathbf{R}$ 实现了对干扰方向的自适应抑制。

**工程层面**：快拍数不足时需引入对角加载以保证数值稳定；$\varepsilon$ 的选取在稳定性与性能之间权衡，通常取噪声功率量级。

**定位层面**：Capon 是介于 CBF（固定波束形成）与 MUSIC/ESPRIT（子空间方法）之间的过渡方案——分辨率优于 CBF（约 2 倍），低于子空间方法；鲁棒性优于子空间方法，适合快拍受限或有强干扰的工程场景。它的谱值保留了功率的物理意义，是子空间伪谱所不具备的。

在接下来的 2.7 节算法性能对比实验中，我们将把 Capon 与 CBF、MUSIC、ESPRIT 放在同一框架下比较，通过 RMSE vs SNR 曲线和分辨率概率曲线，让这四种算法的性能差距在数字上一目了然。
