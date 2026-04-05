---
id: traditional-source-number-estimation-and-model-order-selection
title: 2.2 信源数估计与模型阶数选择
slug: /traditional-methods/source-number-estimation-and-model-order-selection
---

## 2.2 信源数估计与模型阶数选择

上一节在推导子空间分解时，有一个参数被我们默默地当作已知量来使用——信源数 $K$。正是 $K$ 决定了协方差矩阵的特征值该在哪里划分，哪些特征向量属于信号子空间，哪些属于噪声子空间。可以说，$K$ 是整个子空间框架的"枢纽"：它估计错了，后续的 MUSIC 和 ESPRIT 都会偏离正轨。

那么，$K$ 在实际中能直接知道吗？

很多时候不能。雷达场景下，目标数量随时在变；通信场景下，接入的用户数是动态的；即使在已知"有几个用户"的系统里，多径传播还会引入额外的"虚假信源"。因此，**信源数估计**（source number estimation）——也叫**模型阶数选择**（model order selection）——是一个必须认真对待的实际问题。

本节将介绍两类方法：一是基于特征值分布直观判断的"肘点法"，二是有理论依据的信息论准则（AIC 与 MDL）。前者直观、易于上手，后者严谨、可自动化。两者各有适用场合，了解它们的异同对工程实践很有帮助。

---

### 2.2.1 理想情形：特征值的"台阶"

先回到 2.1 节的结论。在信号独立、噪声白化的理想条件下，协方差矩阵 $\mathbf{R}$ 的 $M$ 个特征值（降序排列）呈现出清晰的两段结构：

$$
\underbrace{\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_K}_{\text{信号特征值}，> \sigma^2} \gg \underbrace{\lambda_{K+1} = \lambda_{K+2} = \cdots = \lambda_M = \sigma^2}_{\text{噪声特征值，完全相等}}
$$

信号特征值 $\lambda_k = \lambda_k^{(s)} + \sigma^2$ 大于噪声背景 $\sigma^2$，而噪声特征值全部精确相等，形成一个水平"平台"。信源数 $K$ 就是比这个平台更高的特征值个数，在特征值曲线上对应一个清晰的"台阶"或"肘点"（elbow）。

这在理论上非常美妙。但实际中只能获得有限快拍下的样本协方差矩阵 $\hat{\mathbf{R}}$，三个现实因素会破坏这个整洁的结构：

**第一，估计误差的扰动。** 有限快拍下，$\hat{\mathbf{R}}$ 是 $\mathbf{R}$ 的随机近似，噪声特征值不会精确相等，而是在 $\sigma^2$ 附近随机涨落，形成一个高低不平的"噪声丛"。

**第二，低信噪比下的特征值交叠。** 当信号功率与噪声功率相近时，信号特征值仅比 $\sigma^2$ 略高，容易淹没在噪声特征值的起伏之中，"台阶"消失，断层模糊。

**第三，噪声功率 $\sigma^2$ 未知。** 在实际系统中，噪声功率往往需要从数据中估计，无法预先知道哪个数值才是"平台基线"。

这三个因素叠加在一起，使得从特征值曲线中读出 $K$ 成为一件需要方法、而不能光靠"目测"的事情。

---

### 2.2.2 直观方法：肘点法

最简单的处理思路，是直接绘制特征值曲线（横轴为特征值编号，纵轴为特征值大小），视觉上寻找曲线斜率发生突变的"肘点"——在那之前是信号特征值（陡降段），在那之后是噪声特征值（平坦段），肘点对应的编号就是 $K$ 的估计值。

这种方法的优点是直观、无需额外参数，适合在仿真调试或探索性分析时快速判断。缺点是在中低 SNR 或少快拍时，斜率变化不明显，肘点位置主观性较强，不适合自动化处理。

下面用代码演示这个过程，并与理想情形作对比：

```python
import numpy as np
import matplotlib.pyplot as plt

# 仿真参数
M = 8           # 阵元数
K_true = 2      # 真实信源数
d = 0.5         # 阵元间距（波长归一化）
thetas = np.deg2rad([20, 50])   # 真实信号方向
sigma2 = 0.1    # 噪声功率（SNR ≈ 10 dB）

def run_sim(N, seed=42):
    rng = np.random.default_rng(seed)
    psi = 2 * np.pi * d * np.sin(thetas)
    A = np.exp(1j * np.outer(np.arange(M), psi))
    S = (rng.standard_normal((K_true, N)) +
         1j * rng.standard_normal((K_true, N))) / np.sqrt(2)
    noise = np.sqrt(sigma2 / 2) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N)))
    X = A @ S + noise
    R_hat = (X @ X.conj().T) / N
    eigvals = np.linalg.eigvalsh(R_hat)[::-1].real  # 降序排列
    return eigvals

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, N, label in zip(axes, [500, 30], ['N=500（快拍充足）', 'N=30（快拍较少）']):
    eigvals = run_sim(N)
    ax.stem(range(1, M + 1), eigvals, basefmt='k-')
    ax.axhline(y=sigma2, color='r', linestyle='--', label=f'真实噪声功率 σ²={sigma2}')
    ax.axvline(x=K_true + 0.5, color='g', linestyle=':', label=f'真实 K={K_true}')
    ax.set_xlabel('特征值编号')
    ax.set_ylabel('特征值大小')
    ax.set_title(label)
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()
```

运行后，左图（$N=500$）中信号特征值与噪声特征值之间的台阶清晰可辨，肘点位于第 2 和第 3 个特征值之间，视觉上很容易判断 $K=2$。右图（$N=30$）中噪声特征值的随机涨落明显增大，断层模糊，目测已经不够可靠——这正是需要统计准则的场合。

---

### 2.2.3 信息论准则：AIC 与 MDL

为了让信源数估计可以自动化、有理论保障，研究者们将模型选择问题纳入了**信息论**框架。最具代表性的两个准则由 Wax 和 Kailath 于 1985 年提出：**AIC**（Akaike Information Criterion，赤池信息准则）和 **MDL**（Minimum Description Length，最小描述长度准则）。

它们的基本思路是一致的：把信源数 $d$ 视为一个待选择的模型参数，对每个候选值 $d = 0, 1, \cdots, M-1$ 分别计算一个准则值，取准则值最小时对应的 $d$ 作为信源数的估计。

**核心思路：衡量噪声特征值的"一致程度"**

假设真实信源数为 $K$，则理论上后 $M-d$ 个噪声特征值应该完全相等。若候选值 $d$ 小于真实 $K$，则被当作"噪声特征值"的那些里面混入了信号特征值，大小差异明显，"一致程度"差；若 $d$ 恰好等于 $K$，被归为噪声的特征值方差最小，最为均匀。

这种"一致程度"可以用后 $M-d$ 个特征值的**几何平均与算术平均之比**来量化：

$$
L(d) = -N(M - d)\ln\frac{\left(\prod_{i=d+1}^{M} \hat{\lambda}_i\right)^{1/(M-d)}}{\dfrac{1}{M-d}\sum_{i=d+1}^{M} \hat{\lambda}_i}
$$

几何平均总是不大于算术平均（均值不等式），两者越接近说明这些特征值越均匀，比值趋近于 1，$-\ln(\text{比值})$ 趋近于 0。所以 $L(d)$ 越小，表示后 $M-d$ 个特征值越一致，更可能都是噪声特征值。

但如果只最小化 $L(d)$，$d = M-1$ 时永远最小（只剩一个特征值，"方差为零"）——这是过拟合。信息论准则的关键在于加入**惩罚项**，对模型复杂度（即信源数 $d$）进行约束：

$$
\text{AIC}(d) = -2L(d) + 2p(d)
$$

$$
\text{MDL}(d) = -L(d) + \frac{1}{2}p(d)\ln N
$$

其中 $p(d) = d(2M - d)$ 是候选模型的自由参数个数（对应于 $d$ 个信源条件下的模型复杂度），$N$ 是快拍数。

两者的区别在于惩罚力度：AIC 的惩罚项是常数 $2p(d)$，与快拍数无关；MDL 的惩罚项是 $\frac{1}{2}p(d)\ln N$，随快拍数增加而增大。理论分析表明，**AIC 是渐近有偏的，倾向于高估信源数；MDL 是渐近一致的，在 $N \to \infty$ 时收敛到真实值**。工程实践中，MDL 通常更可靠，是更常用的选择。

---

### 2.2.4 AIC/MDL 的代码实现

把上述公式翻译成代码，并对不同信噪比和快拍数条件测试准确率，是理解这两个准则的最好方式：

```python
import numpy as np

def estimate_source_number(R_hat, N, method='MDL'):
    """
    基于 AIC 或 MDL 准则估计信源数
    参数：
        R_hat  : 样本协方差矩阵，形状 (M, M)
        N      : 快拍数
        method : 'AIC' 或 'MDL'
    返回：
        K_hat  : 估计的信源数
        scores : 每个候选 d 对应的准则值（列表）
    """
    M = R_hat.shape[0]
    eigvals = np.linalg.eigvalsh(R_hat)[::-1].real  # 降序排列

    scores = []
    for d in range(M):
        noise_eigs = eigvals[d:]       # 候选噪声特征值（后 M-d 个）
        n = M - d                      # 噪声特征值个数

        geo_mean = np.exp(np.mean(np.log(noise_eigs)))   # 几何平均
        ari_mean = np.mean(noise_eigs)                    # 算术平均

        L_d = -N * n * np.log(geo_mean / ari_mean)       # 对数似然项
        p_d = d * (2 * M - d)                             # 自由参数数

        if method == 'AIC':
            score = -2 * L_d + 2 * p_d
        else:  # MDL
            score = -L_d + 0.5 * p_d * np.log(N)

        scores.append(score)

    K_hat = int(np.argmin(scores))
    return K_hat, scores


# -------------------------------------------------------
# 仿真验证：对比不同快拍数下 AIC 与 MDL 的估计结果
# -------------------------------------------------------
import matplotlib.pyplot as plt

M = 8
K_true = 2
d_spacing = 0.5
thetas = np.deg2rad([20, 50])
sigma2 = 0.1
rng = np.random.default_rng(0)

psi = 2 * np.pi * d_spacing * np.sin(thetas)
A = np.exp(1j * np.outer(np.arange(M), psi))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

for ax, N in zip(axes, [200, 20]):
    S = (rng.standard_normal((K_true, N)) +
         1j * rng.standard_normal((K_true, N))) / np.sqrt(2)
    noise = np.sqrt(sigma2 / 2) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N)))
    X = A @ S + noise
    R_hat = (X @ X.conj().T) / N

    K_aic, scores_aic = estimate_source_number(R_hat, N, method='AIC')
    K_mdl, scores_mdl = estimate_source_number(R_hat, N, method='MDL')

    x = range(M)
    ax.plot(x, scores_aic, 'o-', label=f'AIC（估计 K={K_aic}）')
    ax.plot(x, scores_mdl, 's--', label=f'MDL（估计 K={K_mdl}）')
    ax.axvline(x=K_true, color='r', linestyle=':', label=f'真实 K={K_true}')
    ax.set_xlabel('候选信源数 d')
    ax.set_ylabel('准则值')
    ax.set_title(f'N = {N}')
    ax.legend()
    ax.grid(True)

plt.suptitle('AIC 与 MDL 准则值随候选信源数的变化')
plt.tight_layout()
plt.show()

print(f"N=200 时：AIC 估计 K={K_aic}，MDL 估计 K={K_mdl}，真实 K={K_true}")
```

运行代码，你将看到准则值曲线在 $d = K_{\text{true}} = 2$ 处出现最小值，AIC 和 MDL 均能在快拍充足时准确估计信源数。当快拍数减少到 $N=20$ 时，可以观察到两条曲线的最小值点可能略有差异——这正体现了 AIC 和 MDL 在小样本条件下的行为差别。

---

### 2.2.5 使用信息论准则的注意事项

AIC 和 MDL 虽然理论完备，但在工程中使用时有几点值得注意。

**信噪比的门槛效应。** 当信号功率与噪声功率非常接近（低 SNR）时，信号特征值几乎淹没在噪声中，任何准则都很难准确识别。这不是算法的缺陷，而是问题本身在低 SNR 下的根本困难——可用于"区分"信源的信息量太少。在实际系统中，如果预判工作在低 SNR，可以适当增加快拍数以改善估计质量。

**相干信号破坏等特征值结构。** 若信号源之间存在相干性（比如多径传播导致同一信号从多个方向到达），信源协方差矩阵 $\mathbf{R}_s$ 秩亏缺，导致信号特征值中出现额外的零值，破坏了理论假设。此时 AIC/MDL 会低估信源数。这个问题将在 2.5 节的空间平滑处理中专门讨论。

**阵元间噪声不均匀（色噪声）。** AIC 和 MDL 的推导均假设噪声是空间白噪声（$\sigma^2\mathbf{I}$）。若各阵元噪声功率不同，噪声特征值将不再相等，准则值曲线的"平台"消失，估计结果会出现较大偏差。实际系统中应尽量对各通道做增益校准。

**MDL 优于 AIC 的场合。** 快拍数较大时，MDL 的惩罚项 $\frac{1}{2}p(d)\ln N$ 比 AIC 的 $2p(d)$ 更重，对过拟合的抑制更强，渐近性能更优。对于本教程面向的大多数应用场景，**优先选用 MDL**。

---

### 2.2.6 实际工程中的处理策略

在真实系统中，信源数估计往往不是一个孤立的计算步骤，而是嵌入在整个 DOA 估计流程中，与算法性能相互影响。下面给出几条实用建议。

**先"看一眼"特征值曲线，再用准则做验证。** 在调试和仿真阶段，特征值的可视化是非常有价值的。它不仅帮助判断信源数，还能揭示信噪比是否充足、是否存在相干信号等问题。养成在算法流程中输出并查看特征值分布的习惯，会让排查问题容易很多。

**对估计结果做合理性约束。** 在某些场景下，信源数的范围可以先验限定。例如雷达系统中已知最多跟踪 5 个目标，那么即使准则给出 $\hat{K} = 7$，也应限制在合理范围内。把先验知识用进来，永远比盲目相信算法输出更稳健。

**快拍数不足时，接受更大的估计误差。** 快拍数 $N$ 较小时（尤其 $N < 5M$），所有信源数估计方法的可靠性都会下降，这是统计估计的基本规律。对于快拍数受限的场景，需要在算法鲁棒性和估计精度之间权衡，必要时可保守地使用较小的 $\hat{K}$，以避免将噪声特征向量混入信号子空间。

---

### 2.2.7 小结

本节围绕"如何确定信源数 $K$"这一实际问题，介绍了两类方法。

**视觉方法（肘点法）**：绘制特征值曲线，寻找信号特征值与噪声特征值之间的"台阶"断层。直观易懂，适合快拍充足、信噪比较高的仿真调试场景。

**信息论准则（AIC/MDL）**：对每个候选信源数 $d$ 计算一个权衡"拟合程度"与"模型复杂度"的综合准则值，取最小值对应的 $d$ 作为估计结果。MDL 渐近一致、理论更严谨，是工程中的推荐选择。

在实际系统中，这两种方法并不互斥——视觉判断提供直觉，信息论准则提供自动化决策。将两者结合使用，是稳健的工程实践。

掌握了信源数估计的工具，我们就可以放心地进入 2.3 节：在已知 $K$ 的前提下，MUSIC 算法如何利用噪声子空间的正交性，构造出超分辨率的空间伪谱？