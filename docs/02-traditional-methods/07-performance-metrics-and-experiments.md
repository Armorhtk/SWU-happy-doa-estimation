---
id: traditional-performance-metrics-and-experiments
title: 2.6 DOA估计性能评价指标与算法实验分析
slug: /traditional-methods/performance-metrics-and-experiments
---


## 2.6 DOA 估计性能评价指标与算法实验分析

经历了前五节的理论与实现，我们手中已经握有一套完整的经典 DOA 算法工具箱：常规波束形成（CBF）、MUSIC、Root-MUSIC、ESPRIT，以及针对相干信号的空间平滑变体。现在到了一个重要的节点：**停下来，把这些算法放在同一个实验框架下做系统比较**。

这件事不只是为了知道"谁赢了"，更是为了建立一种工程判断力：不同条件下该选哪种算法，性能差距有多大，实际应用中最值得关注的瓶颈在哪里。本节将先澄清性能评价的指标体系，再通过三组系统仿真实验给出直观答案。

完整的实验代码集中在 `sources/codes/ch2_algorithm_comparison.py`，正文中只展示关键的函数接口和结果分析，有意深入的读者朋友可以直接运行该文件并调整参数进行探索。

---

### 2.6.1 评价指标：用什么衡量算法好坏

在开始比较之前，必须先说清楚"好坏"的度量标准。DOA 估计领域常用以下几个指标，各自侧重不同的性能维度。

**均方根误差（RMSE）** 是最核心的精度指标。对 $N_{\text{trial}}$ 次蒙特卡洛实验，每次得到 $K$ 个 DOA 估计值，RMSE 定义为：

$$
\text{RMSE} = \sqrt{\frac{1}{N_{\text{trial}} \cdot K} \sum_{t=1}^{N_{\text{trial}}} \sum_{k=1}^{K} (\hat{\theta}_k^{(t)} - \theta_k)^2}
$$

RMSE 越小说明估计越准确。通常将其与 CRB 对比，判断算法是否接近理论最优。实验中某次试验可能出现"灾难性失败"（算法完全找不到正确峰值），此类异常值会使 RMSE 剧烈偏大，因此有时需要额外统计**失败率**（failure rate）来补充说明。

**成功概率（Probability of Resolution，P_res）** 是分辨率的评价指标。定义：若一次试验中算法成功找到 $K$ 个峰值，且每个峰值与对应真实方向的误差均小于某个阈值（如 $\Delta\theta/2$，其中 $\Delta\theta$ 是两信源角度差），则判定为"成功分辨"。$P_{\text{res}}$ 越高，说明算法在该条件下分辨率越稳定。

**计算复杂度** 是工程场景中不能忽略的实用指标。对于在线处理（如雷达实时跟踪），算法的运行时间直接决定可行性。子空间方法的瓶颈一般在特征值分解（$O(M^3)$）和谱搜索（$O(M \cdot I)$），Root-MUSIC 和 ESPRIT 无需谱搜索，因此在大 $I$ 时速度优势明显。

以下三组实验分别考察 **RMSE vs SNR**、**RMSE vs 快拍数**、**分辨率 vs 角度间隔**，这是 DOA 算法对比文献中最标准的三条性能曲线。

---

### 2.6.2 实验一：RMSE vs SNR

**实验设置**：8 阵元 ULA，$d = 0.5\lambda$，两个独立信源 $\theta = [20°, 40°]$，快拍数 $N = 200$，SNR 从 $-10$ dB 扫描至 $20$ dB，每个 SNR 点做 500 次蒙特卡洛。比较 CBF、MUSIC、Root-MUSIC、TLS-ESPRIT 四种算法，并标注 CRB 曲线作为参考基准。

实验结果（运行 `ch2_algorithm_comparison.py` 中的 `exp1_rmse_vs_snr()` 可复现）的典型规律如下：

在**高 SNR 区间**（$\geq 5$ dB 左右），MUSIC、Root-MUSIC、ESPRIT 三条曲线高度重合，且非常接近 CRB——这验证了子空间方法的渐近有效性。CBF 曲线则始终高于子空间方法约一个数量级，差距不随 SNR 的提升而消失，这正是其分辨率受傅里叶限制的体现。

在**中等 SNR 区间**，三种子空间方法出现细微差异：Root-MUSIC 通常比标准 MUSIC 略好（消除了离散化误差），ESPRIT 与 Root-MUSIC 性能相当，印证了两者渐近等价的理论结论。

在**低 SNR 区间**，各算法相继出现"阈值效应"：RMSE 不再沿 CRB 曲线平滑下降，而是突然跳升，甚至比 CBF 更差——这是因为子空间划分出现错误，算法进入失效模式。有趣的是，CBF 的 RMSE 反而在低 SNR 下比失效的子空间方法更"稳定"（虽然精度低），体现了简单方法的鲁棒性。

> **工程含义**：在已知工作 SNR 范围的系统中，子空间方法只要不触及阈值，精度远优于 CBF；但若 SNR 可能掉入阈值以下，须考虑设计鲁棒的备份机制或使用多帧积累提升有效 SNR。

---

### 2.6.3 实验二：RMSE vs 快拍数

**实验设置**：与实验一相同，但固定 SNR = 5 dB，快拍数 $N$ 从 $20$ 到 $2000$ 对数均匀扫描，每点 500 次蒙特卡洛。

典型规律：

所有方法的 RMSE 均随快拍数增加而单调下降，但速率不同。子空间方法在快拍数较少时（$N < 2M = 16$）可能失效——样本协方差矩阵秩不足，特征值分解结果失去意义。当 $N \geq 3M$ 至 $5M$ 之后，MUSIC 和 ESPRIT 开始稳定趋近 CRB。CRB 曲线斜率为 $-1/2$（双对数坐标下），各子空间方法在大快拍数时均平行地跟随这一斜率，说明它们的渐近斜率与 CRB 一致。CBF 在增加快拍数时同样有所改善，但改善幅度比子空间方法小，且受硬性的分辨率限制，不能无限收敛到零误差。

> **工程含义**：快拍数是可以通过系统设计控制的参数（增加积累时间或采样率）。当 SNR 受限时，增加快拍数是改善子空间方法性能的有效途径，且成本通常低于增加阵元数。

---

### 2.6.4 实验三：分辨率概率 vs 角度间隔

这一组实验最能直观体现"超分辨率"的实质含义。

**实验设置**：8 阵元 ULA，SNR = 10 dB，$N = 200$，两信源的均值方向固定在 $30°$，角度间隔 $\Delta\theta$ 从 $2°$ 扫描至 $20°$，每点做 500 次蒙特卡洛，统计各算法的成功分辨概率 $P_{\text{res}}$（判定阈值为 $\Delta\theta / 2$）。

```python
# 典型分辨率实验的核心逻辑（完整版见配套代码）
def resolution_probability(algo_func, thetas_true, snr_dB, N, M, d, n_trials=500):
    """
    计算给定角度间隔下的成功分辨概率
    thetas_true : 两个信源的真实方向（度）
    返回 : 成功分辨的概率
    """
    delta_theta = abs(thetas_true[1] - thetas_true[0])
    threshold = delta_theta / 2.0       # 判定阈值：误差小于半角度间隔
    success = 0

    sig_pow = 10 ** (snr_dB / 10)
    rng = np.random.default_rng(42)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])

    for _ in range(n_trials):
        S = np.sqrt(sig_pow / 2) * (rng.standard_normal((2, N)) +
                                     1j * rng.standard_normal((2, N)))
        noise = (1 / np.sqrt(2)) * (rng.standard_normal((M, N)) +
                                     1j * rng.standard_normal((M, N)))
        X = A @ S + noise
        R_hat = (X @ X.conj().T) / N

        try:
            est = algo_func(R_hat)
            if len(est) == 2:
                err = np.sort(est) - np.sort(thetas_true)
                if np.all(np.abs(err) < threshold):
                    success += 1
        except Exception:
            pass

    return success / n_trials
```

典型实验结果呈现出非常清晰的对比：CBF 的 $P_{\text{res}}$ 在角度间隔约 $14°$（对应 8 阵元 ULA 的瑞利分辨率）以上才接近 1，以下迅速跌至 0；MUSIC 和 ESPRIT 在 $\Delta\theta \geq 4°$ 时 $P_{\text{res}}$ 即可稳定在 0.9 以上，体现出约 3 倍于 CBF 的分辨力提升。Root-MUSIC 因消除离散化误差，在极小角度间隔（$2°$—$4°$）时略优于标准 MUSIC。

---

### 2.6.5 算法横向对比总结

把三个实验的规律整理成一张参考表，方便读者在工程选型时查阅：

| 性能维度 | CBF | MUSIC | Root-MUSIC | TLS-ESPRIT |
|---|---|---|---|---|
| 高 SNR 精度 | 差（受傅里叶限制） | 接近 CRB | 接近 CRB | 接近 CRB |
| 低 SNR 鲁棒性 | 稳定（但精度低） | 有阈值效应 | 有阈值效应 | 有阈值效应 |
| 分辨率 | 受瑞利限制（≈$14°$） | 超分辨（≈$4°$） | 超分辨（略优） | 超分辨（相当） |
| 是否需要谱搜索 | 需要 | 需要 | 不需要 | 不需要 |
| 对阵型要求 | 任意阵 | 任意阵 | 仅 ULA | 需移不变结构 |
| 对相干信号 | 性能下降 | 完全失效 | 完全失效 | 完全失效 |
| 配合空间平滑 | 不适用 | SS-MUSIC ✓ | SS-Root-MUSIC ✓ | SS-ESPRIT ✓ |
| 计算量 | 低 | 中（需谱搜索） | 中 | 低 |

这张表并无绝对意义上的"最优"算法，只有在特定约束下的最优选择。几个常见的工程决策场景可以归纳如下：

**追求精度，条件理想**（高 SNR、足够快拍、信源独立）：Root-MUSIC 或 TLS-ESPRIT 均是首选，两者精度相当，ESPRIT 计算量更小。

**需要快速实时处理**：ESPRIT 无需谱搜索，延迟最低，适合雷达实时跟踪。

**存在多径/相干信号**：必须先做空间平滑（推荐 FBSS），再接 MUSIC 或 ESPRIT。代价是有效孔径缩短、分辨率下降。

**阵型非 ULA 或阵元方向图未知**：只能用标准谱搜索 MUSIC，ESPRIT 和 Root-MUSIC 不适用。

**低 SNR 或少快拍极端场景**：子空间方法均可能进入阈值区，退化至 CBF 甚至不如 CBF。此时可考虑用 CBF 作为粗估计，再引导子空间方法做精化，或增加快拍数积累。

---

### 2.6.6 📦 本章代码与动手实践

本章各节的算法实现与仿真实验已集成到一个独立的 Python 脚本中，请查看：

```text
sources/codes/ch2_algorithm_comparison.py
```

该脚本包含以下功能模块，均可独立调用：

- `utils`：导向矢量、样本协方差矩阵、CRB 计算等公共工具函数
- `cbf`：常规波束形成
- `music`：标准 MUSIC 谱搜索
- `root_music`：Root-MUSIC（多项式求根）
- `esprit`：TLS-ESPRIT
- `mdl_estimate`：MDL 信源数估计
- `spatial_smoothing` / `fb_spatial_smoothing`：前向/前向—后向空间平滑
- `exp1_rmse_vs_snr()`：实验一（RMSE vs SNR）
- `exp2_rmse_vs_snapshots()`：实验二（RMSE vs 快拍数）
- `exp3_resolution_probability()`：实验三（分辨率概率 vs 角度间隔）

脚本开头的参数区（`CONFIG` 字典）集中管理所有仿真参数，修改后重新运行即可复现不同条件下的实验。建议同学们至少完成以下几个动手任务，把本章的核心结论从"读懂"变成"验证过的"：

> **任务 A**：运行实验一，找到 MUSIC 和 CBF 的 RMSE 曲线"相交点"（即两者精度相当的 SNR 值），思考：这一交叉点在工程上意味着什么？
>
> **任务 B**：运行实验三，固定 SNR，将阵元数从 8 改为 4，观察 CBF 和 MUSIC 各自的分辨率曲线如何变化——孔径减半对两种方法的影响是否对称？
>
> **任务 C**：在实验一的基础上，手动将两个信源改为完全相干（`alpha * s1`），观察 MUSIC 的 RMSE 曲线如何崩溃；然后在前处理中加入 FBSS，观察性能恢复情况。注意记录空间平滑后有效孔径缩短对 CRB 的影响。

---

### 2.6.7 第二章小结

至此，第二章的内容完整收官。回顾一下这一章走过的路：

我们从特征值分解出发（2.1 节），认识了信号子空间和噪声子空间这两个贯穿全章的核心概念；学会了用 MDL 等信息论准则自动估计信源数（2.2 节）；随后系统地掌握了 MUSIC 的谱搜索逻辑与 Root-MUSIC 的多项式变体（2.3 节），以及 ESPRIT 基于旋转不变性的代数直接求解（2.4 节）；在面对相干信号这一实际工程难题时，理解了空间平滑为何有效，以及前向—后向平滑的优势（2.5 节）；最后，在本节通过系统实验把算法性能的全貌呈现出来，建立了算法选型的工程判断框架（2.6 节）。

这些经典方法诞生于 1980 年代，历经四十年依然是 DOA 估计领域的主流基准。它们的价值不仅在于实用，更在于提供了一套清晰的物理直觉和数学框架——子空间分解、正交性检验、旋转不变性——这些思想在第三章的深度学习方法中依然以不同形式回响，是理解数据驱动方法优劣的重要参照。

带着这套经典算法的完整认识，我们继续前行，进入第三章：当神经网络接管 DOA 估计时，会有什么不同？
