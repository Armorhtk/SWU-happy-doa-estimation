---
id: traditional-coherent-sources-and-spatial-smoothing
title: 2.5 相干信号问题及空间平滑处理
slug: /traditional-methods/coherent-sources-and-spatial-smoothing
---


## 2.5 相干信号问题及空间平滑处理

前面四节把子空间方法的核心内容——理论基础、信源数估计、MUSIC 和 ESPRIT——逐一讲完了。读到这里，同学们已经具备了在理想条件下独立实现和运行经典 DOA 算法的能力。

但有一个"刺客"一直潜伏在理想假设的背后，准备在工程实践中给你一个措手不及：**相干信号**（coherent signals）。这种情形在无线通信和雷达实际场景中极为常见，而 MUSIC 和 ESPRIT 在面对它时会彻底失效——不是性能下降，而是**直接崩溃**。理解为什么，以及如何应对，是本节的全部任务。

---

### 2.5.1 什么是相干信号，为何普遍存在

先把概念说清楚。**相干信号**（coherent signals）是指两个或多个信号源发出的信号之间存在确定性线性关系。最极端的情形是完全相干：一个信号恰好是另一个信号的常数倍（幅度缩放加相位偏移），即 $s_2(t) = \alpha \cdot s_1(t)$，$\alpha$ 是复常数。更一般地，若信源协方差矩阵 $\mathbf{R}_s$ 的秩小于信源数 $K$，就称这些信号是相干的（或部分相干的）。

这种情形在实际中并不罕见，最典型的来源有三类：

**多径传播**是最常见的来源。在城市环境、室内或水下声呐场景中，一个发射机的信号会通过直射路径和多条反射/绕射路径同时到达阵列，形成多个"虚假信源"。这些路径上的信号都来自同一个发射源，天然完全相干。车载毫米波雷达中，近处的地面、护栏等强反射体尤其容易制造这种情况。

**主动干扰**也会产生相干信号。通信对抗中，干扰机有时会复制目标信号并重放，使接收端出现完全相干的干扰源。

**信号泄漏与串扰**。某些阵列系统中，阵元间的电磁耦合会导致一个信源的信号"泄漏"到其他虚拟方向，也会造成相干结构。

可以说，**只要场景中存在明显的多径效应，相干信号问题就几乎必然出现**。这不是小概率事件，而是工程中必须正面应对的常态。

---

### 2.5.2 相干信号如何击垮 MUSIC 和 ESPRIT

理解问题的根源，需要回到协方差矩阵的理论结构。

回忆 1.3 节的结论：

$$
\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}
$$

子空间方法能够工作，关键前提是信号分量 $\mathbf{A}\mathbf{R}_s\mathbf{A}^H$ 的秩等于 $K$——即有 $K$ 个线性无关的信号维度，特征值分解后恰好有 $K$ 个"大"特征值能与 $M-K$ 个"小"特征值清晰分离。

**一旦信号相干，$\mathbf{R}_s$ 的秩下降**。极端情形下两个完全相干的信号，$\mathbf{R}_s$ 秩为 1，整个信号分量 $\mathbf{A}\mathbf{R}_s\mathbf{A}^H$ 的秩也只有 1，而不是 2。特征值分布随之扭曲：本应有 2 个大特征值，现在只有 1 个大于 $\sigma^2$；本应有 $M-2$ 个噪声特征值，现在有 $M-1$ 个。

这意味着什么？当我们仍然以 $K=2$ 来划分子空间，就会把一个原本属于"信号"的特征向量错误归入噪声子空间。这个被误归的特征向量，恰好包含了区分两个相干信源方向的关键信息。把它混入噪声子空间后，MUSIC 伪谱分母不再能在两个真实方向处趋近于零，峰值消失；ESPRIT 的旋转矩阵求解也会因子空间畸变而给出错误的特征值。

用一个简单的仿真可以把这个失效过程展示得非常直观：

```python
import numpy as np
import matplotlib.pyplot as plt

def steering_vector(theta_deg, M, d=0.5):
    theta = np.deg2rad(theta_deg)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * np.arange(M))

def music_spectrum(R_hat, K, theta_grid, M, d=0.5):
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    En = U_n @ U_n.conj().T
    spec = np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj() @ En
                       @ steering_vector(th, M, d)) + 1e-12)
        for th in theta_grid
    ])
    return spec / spec.max()

M, K, d = 8, 2, 0.5
thetas_true = [20.0, 40.0]
theta_grid = np.linspace(-90, 90, 1801)
N, SNR_dB = 300, 15
sig_pow = 10 ** (SNR_dB / 10)
rng = np.random.default_rng(0)

A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])

# ---- 情形一：独立信号 ----
S_indep = np.sqrt(sig_pow / 2) * (rng.standard_normal((K, N)) +
                                   1j * rng.standard_normal((K, N)))

# ---- 情形二：完全相干（s2 = alpha * s1）----
alpha = 0.8 * np.exp(1j * np.pi / 3)           # 幅度 0.8，相位偏转 60°
s1 = np.sqrt(sig_pow / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
S_coher = np.vstack([s1, alpha * s1])

noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N)) +
                              1j * rng.standard_normal((M, N)))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, S, title in zip(axes,
                        [S_indep, S_coher],
                        ['独立信号（正常工作）', '完全相干信号（MUSIC 失效）']):
    X = A @ S + noise
    R_hat = (X @ X.conj().T) / N
    spec = music_spectrum(R_hat, K, theta_grid, M, d)
    spec_dB = 10 * np.log10(spec + 1e-10)

    ax.plot(theta_grid, spec_dB, 'b-', linewidth=1.2)
    for th in thetas_true:
        ax.axvline(x=th, color='r', linestyle='--', linewidth=1)
    ax.set_xlabel('角度 θ（度）')
    ax.set_ylabel('归一化伪谱（dB）')
    ax.set_title(title)
    ax.set_xlim([-90, 90])
    ax.set_ylim([-30, 2])
    ax.grid(True)

plt.tight_layout()
plt.show()
```

运行后，左图（独立信号）在 20° 和 40° 处出现两个清晰的峰；右图（完全相干）峰值紊乱，两个信源方向处完全找不到应有的峰——这就是"击垮"的字面含义。

---

### 2.5.3 前向空间平滑：从一个协方差矩阵到多个子阵的平均

解决相干问题的经典方案由 Shan、Wax 和 Kailath 于 1985 年提出，称为**空间平滑**（spatial smoothing）。其核心思想出人意料地简单：**把一个大阵列分成多个重叠的小子阵，对各子阵的协方差矩阵取平均，用平均结果代替原始协方差矩阵**。

为什么这样能解决相干问题？直觉上，相干信号的"问题"在于两个信源的信号之间有一个固定的相位关系，这个固定相位关系使得 $\mathbf{R}_s$ 秩亏缺。当我们在不同的子阵上观察时，子阵位置不同带来的额外相位偏移会破坏这个固定关系——每个子阵看到的相对相位是不同的，把它们平均之后，相干性被"稀释"，$\mathbf{R}_s$ 的有效秩得以恢复。

具体操作如下。对于 $M$ 阵元的 ULA，取子阵长度为 $P$（$P < M$），可以滑动地划分出 $L = M - P + 1$ 个重叠子阵：

- 子阵 $l$（$l = 1, 2, \cdots, L$）：由第 $l$ 到第 $l+P-1$ 个阵元组成

第 $l$ 个子阵的观测向量 $\mathbf{x}_l(t)$ 是原始观测向量 $\mathbf{x}(t)$ 的第 $l$ 到第 $l+P-1$ 行，对应的导向矢量 $\mathbf{a}_l(\theta_k)$ 是完整导向矢量的对应子向量。可以验证：

$$
\mathbf{a}_l(\theta_k) = e^{j(l-1)\psi_k} \cdot \mathbf{a}_1(\theta_k)
$$

即第 $l$ 个子阵的导向矢量恰好是第一个子阵的导向矢量乘以相位因子 $e^{j(l-1)\psi_k}$。

第 $l$ 个子阵的协方差矩阵 $\mathbf{R}_l = \mathbb{E}[\mathbf{x}_l(t)\mathbf{x}_l^H(t)]$ 对应于一个"移位"的信号模型。展开之后可以证明，对所有子阵协方差矩阵取平均，得到**前向空间平滑协方差矩阵**：

$$
\mathbf{R}_{\text{SS}} = \frac{1}{L}\sum_{l=1}^{L} \mathbf{R}_l
$$

这是一个 $P \times P$ 的矩阵。可以证明，当 $L \geq K$（子阵数不少于信源数）时，即使所有 $K$ 个信源完全相干，$\mathbf{R}_{\text{SS}}$ 的信号分量秩也能恢复到 $K$，子空间方法重新可用。

用样本协方差矩阵实现时，将整体样本协方差矩阵的第 $l$ 到 $l+P-1$ 行、$l$ 到 $l+P-1$ 列取出（即主对角线上的 $P \times P$ 子矩阵），就是第 $l$ 个子阵的样本协方差矩阵 $\hat{\mathbf{R}}_l$：

$$
\hat{\mathbf{R}}_l = \hat{\mathbf{R}}[l-1:l+P-1,\ l-1:l+P-1]
$$

代码实现非常直接：

```python
def spatial_smoothing(R_hat, P):
    """
    前向空间平滑
    参数：
        R_hat : 完整协方差矩阵，(M, M)
        P     : 子阵长度
    返回：
        R_ss  : 空间平滑后的协方差矩阵，(P, P)
    """
    M = R_hat.shape[0]
    L = M - P + 1                   # 子阵数
    R_ss = np.zeros((P, P), dtype=complex)
    for l in range(L):
        R_ss += R_hat[l:l+P, l:l+P]
    return R_ss / L
```

代码只有寥寥几行，却是处理相干信号问题的核心武器，值得好好记住。

---

### 2.5.4 前向—后向空间平滑：进一步提升秩恢复效果

前向空间平滑已经能够解决问题，但工程界还发展出了一种改进版本——**前向—后向空间平滑**（Forward-Backward Spatial Smoothing，FBSS），能在相同的子阵参数下进一步提升协方差矩阵的估计质量。

其思路是：利用 ULA 导向矢量的共轭对称结构，构造一个"后向"协方差矩阵与前向矩阵求平均。定义**交换矩阵**（exchange matrix）$\mathbf{J}$：它是一个反对角线全为 1 的 $P \times P$ 矩阵（即把向量的元素顺序完全颠倒）。后向空间平滑协方差矩阵定义为：

$$
\mathbf{R}_{\text{b}} = \mathbf{J}\hat{\mathbf{R}}_{\text{SS}}^*\mathbf{J}
$$

其中 $^*$ 表示共轭（不转置）。前向—后向平均后的协方差矩阵为：

$$
\mathbf{R}_{\text{FB}} = \frac{1}{2}\left(\mathbf{R}_{\text{SS}} + \mathbf{R}_{\text{b}}\right) = \frac{1}{2}\left(\mathbf{R}_{\text{SS}} + \mathbf{J}\mathbf{R}_{\text{SS}}^*\mathbf{J}\right)
$$

FBSS 相比纯前向空间平滑有两个好处：其一，等效地将子阵数从 $L$ 变为 $2L$（前向 $L$ 个加后向 $L$ 个），使协方差矩阵估计更稳定；其二，$\mathbf{R}_{\text{FB}}$ 是实对称的厄米矩阵，其特征值分布对称，有时能使子空间分离更清晰。实践中，FBSS 已经成为处理相干信号的标准配置，代码仅需在前向平滑基础上增加几行：

```python
def fb_spatial_smoothing(R_hat, P):
    """
    前向—后向空间平滑（Forward-Backward Spatial Smoothing）
    参数：
        R_hat : 完整协方差矩阵，(M, M)
        P     : 子阵长度
    返回：
        R_fb  : 前向-后向平滑协方差矩阵，(P, P)
    """
    R_ss = spatial_smoothing(R_hat, P)          # 前向平滑

    # 构造交换矩阵
    J = np.eye(P)[::-1]                         # P×P 反对角单位矩阵

    # 后向平滑分量
    R_b = J @ R_ss.conj() @ J

    return 0.5 * (R_ss + R_b)
```

---

### 2.5.5 子阵参数的选取：$P$ 和 $L$ 的权衡

空间平滑引入了一个新的设计参数：子阵长度 $P$（或等价地，子阵数 $L = M - P + 1$）。这两个量之间存在一个对立的权衡，是实际使用时必须注意的：

**$P$ 越大，子阵的有效孔径越大，DOA 估计精度越高**（子阵越长，分辨率越好，CRB 越小）。

**$L$ 越大（即 $P$ 越小），平滑效果越好，相干解相关能力越强**。理论上，前向空间平滑能处理的最大相干信源数为 $L - 1 = M - P$；若使用 FBSS，则最多能处理 $\lfloor(M + 1)/2\rfloor - 1$ 个完全相干信源（在最优参数下）。

工程实践中，常用的经验选取原则是：

$$
P \approx \frac{2M}{3}, \quad L \approx \frac{M}{3}
$$

例如 $M = 12$，可取 $P = 8$，$L = 5$，此时子阵有效孔径为 $8$ 阵元（比原来的 $12$ 阵元缩短了 $1/3$），同时拥有 $5$ 个子阵用于平均，能处理最多 $4$ 个相干信源。

注意空间平滑的代价：**有效阵列孔径从 $M$ 缩减到 $P$**，这意味着分辨率和 CRB 性能都会有所下降。这不是算法的缺陷，而是用"孔径换秩恢复"的必然代价——没有免费的午餐。当相干信源数很少时，$L$ 可以取得小一些，尽量保住孔径。

---

### 2.5.6 完整示例：空间平滑 + MUSIC 处理相干信号

把上面所有模块拼在一起，给出一个完整的示例：用空间平滑预处理后，对完全相干的两个信源成功估计 DOA。

```python
import numpy as np
import matplotlib.pyplot as plt

def steering_vector(theta_deg, M, d=0.5):
    theta = np.deg2rad(theta_deg)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * np.arange(M))

def spatial_smoothing(R_hat, P):
    M = R_hat.shape[0]
    L = M - P + 1
    R_ss = np.zeros((P, P), dtype=complex)
    for l in range(L):
        R_ss += R_hat[l:l+P, l:l+P]
    return R_ss / L

def fb_spatial_smoothing(R_hat, P):
    R_ss = spatial_smoothing(R_hat, P)
    J = np.eye(P)[::-1]
    R_b = J @ R_ss.conj() @ J
    return 0.5 * (R_ss + R_b)

def music_spectrum(R_hat, K, theta_grid, M, d=0.5):
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    En = U_n @ U_n.conj().T
    spec = np.zeros(len(theta_grid))
    for i, theta in enumerate(theta_grid):
        a = steering_vector(theta, M, d)
        spec[i] = 1.0 / (np.real(a.conj() @ En @ a) + 1e-12)
    return spec

# 仿真参数
M, K, d = 12, 2, 0.5
P = 8                               # 子阵长度（L = 12-8+1 = 5 个子阵）
thetas_true = [20.0, 40.0]
N, SNR_dB = 500, 10
sig_pow = 10 ** (SNR_dB / 10)
theta_grid = np.linspace(-90, 90, 1801)

rng = np.random.default_rng(42)
A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])

# 生成完全相干信号
alpha = 0.9 * np.exp(1j * np.pi / 4)
s1 = np.sqrt(sig_pow / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
S = np.vstack([s1, alpha * s1])
noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N)) +
                              1j * rng.standard_normal((M, N)))
X = A @ S + noise
R_hat = (X @ X.conj().T) / N

# 三种处理方式的 MUSIC 伪谱
spec_raw  = music_spectrum(R_hat, K, theta_grid, M, d)         # 无平滑（M 阵元）
R_ss = spatial_smoothing(R_hat, P)
spec_ss   = music_spectrum(R_ss, K, theta_grid, P, d)          # 前向平滑
R_fb = fb_spatial_smoothing(R_hat, P)
spec_fb   = music_spectrum(R_fb, K, theta_grid, P, d)          # 前向-后向平滑

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
configs = [
    (spec_raw,  '无平滑（MUSIC 失效）',       M),
    (spec_ss,   '前向空间平滑（SS-MUSIC）',   P),
    (spec_fb,   '前向-后向平滑（FBSS-MUSIC）', P),
]

for ax, (spec, title, M_eff) in zip(axes, configs):
    spec_dB = 10 * np.log10(spec / spec.max() + 1e-10)
    ax.plot(theta_grid, spec_dB, 'b-', linewidth=1.2)
    for th in thetas_true:
        ax.axvline(x=th, color='r', linestyle='--', linewidth=1,
                   label=f'{th}°')
    ax.set_xlabel('角度 θ（度）')
    ax.set_ylabel('归一化伪谱（dB）')
    ax.set_title(title)
    ax.set_xlim([-90, 90])
    ax.set_ylim([-30, 2])
    ax.legend(fontsize=8)
    ax.grid(True)

plt.tight_layout()
plt.show()
```

运行后，三幅图的对比非常清晰：左图（无平滑）在 20° 和 40° 找不到两个正确峰值；中图（前向平滑）恢复了两个峰，但峰形略宽；右图（前向—后向平滑）峰形更尖锐、对称，估计结果最好。这正是三种方法在实践效果上的真实排序。

---

### 2.5.7 几点工程注意事项

**相干还是独立，应先做判断再选方案。** 空间平滑会压缩有效孔径，如果信号本身是独立的，不必要地使用空间平滑反而会损失性能。实践中，可以先看特征值分布：若理论上应有 $K$ 个大特征值，但实际只有更少个显著特征值，很可能存在相干信号。也可以检验 $\mathbf{R}_s$ 的条件数——条件数异常大意味着接近秩亏缺。

**子阵长度 $P$ 应满足 $P \geq K + 1$**。空间平滑后用 MUSIC 或 ESPRIT，子阵协方差矩阵的维度是 $P \times P$，其中 $K$ 维属于信号子空间，至少需要 $P - K \geq 1$ 维噪声子空间。否则算法退化。

**快拍数不足时，空间平滑效果有限。** 空间平滑本身是对协方差矩阵的线性操作，不产生新的独立快拍。如果原始快拍数很少，各子阵的协方差矩阵估计本身误差就大，平均后的 $\mathbf{R}_{\text{SS}}$ 质量也有限。通常建议快拍数至少满足 $N \geq 3P$。

**ESPRIT 与空间平滑的结合**。空间平滑输出的 $\mathbf{R}_{\text{SS}}$ 或 $\mathbf{R}_{\text{FB}}$ 是一个 $P \times P$ 的协方差矩阵，可以直接代入 ESPRIT 算法（取 $M = P$），按子阵行数分块即可。这意味着 SS-ESPRIT 也是一个完全可用的组合，适合对计算速度要求较高的场景。

---

### 2.5.8 小结

本节围绕相干信号问题，完成了从"认识失效"到"掌握解法"的完整闭环。

**问题本质**：相干信号使信源协方差矩阵 $\mathbf{R}_s$ 秩亏缺，导致协方差矩阵 $\mathbf{R}$ 的信号特征值数目少于真实信源数 $K$，子空间划分错误，MUSIC 和 ESPRIT 直接失效。

**解决方案**：空间平滑通过对多个重叠子阵的协方差矩阵取平均，利用子阵位移带来的额外相位多样性破坏信号间的确定性相位关系，恢复 $\mathbf{R}_s$ 的有效秩。前向空间平滑是基础版本，前向—后向空间平滑（FBSS）进一步利用 ULA 的共轭对称性，效果更优，是工程中的推荐选择。

**代价与权衡**：空间平滑以有效孔径换取秩恢复——子阵长度 $P < M$，分辨率和估计精度相应下降。子阵参数 $P$ 的选取应在孔径保留与解相关能力之间取得平衡，经验规则 $P \approx 2M/3$ 是一个合理的起点。

掌握了空间平滑，就具备了在存在多径的真实场景中应用经典 DOA 算法的基本能力。下一节我们先补上一块经典拼图：**自适应波束形成**。它不像 MUSIC 和 ESPRIT 那样依赖显式的子空间分解，却能借助协方差矩阵对干扰和旁瓣进行更聪明的抑制，是从常规波束形成走向更高分辨方法的重要过渡。
