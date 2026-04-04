---
id: doa-intro-narrowband-far-field-model-and-steering-vector
title: 1.2 远场窄带信号模型与导向矢量
slug: /doa-intro/narrowband-far-field-model-and-steering-vector
---

## 1.2 远场窄带信号模型与导向矢量

在上一节，我们直接给出了导向矢量的表达式：

$$
\mathbf{a}(\theta) = \left[1,\ e^{j\psi},\ e^{j2\psi},\ \cdots,\ e^{j(M-1)\psi}\right]^\top, \quad \psi = \frac{2\pi d}{\lambda}\sin\theta
$$

并承诺"这个形式来自两个假设"。本节就来兑现这个承诺，把这两个假设讲清楚。

这两个假设是：**远场假设**（far-field assumption）和**窄带假设**（narrowband assumption）。它们各自解决一个问题——前者让我们把球面波近似为平面波，后者让我们把时间延迟等效为相位偏移。两者合在一起，导向矢量的表达式才能成立。

---

### 1.2.1 远场假设：从球面波到平面波

先问一个基础问题：信号从信号源出发，以什么形式传播到阵列上？

严格来说，点源辐射的是**球面波**（spherical wave）。球面波的波前是以信号源为中心的球面，其幅度随距离 $r$ 按 $1/r$ 衰减，相位按距离线性增长。对于靠近阵列的近场源，波前的曲率不可忽略，阵列各元看到的波前形状是弯曲的，每个阵元到信号源的距离必须单独计算——这在数学上相当麻烦，工程处理也复杂得多。

好在实际应用中，信号源往往距离阵列很远。当距离足够大时，波前在阵列所覆盖的范围内已经接近平坦，可以近似为**平面波**（plane wave）。这就是远场假设的含义：**信号源位于阵列的远场区域，入射波在阵列处可视为平面波**。

多远才算"远场"？工程上通常以**瑞利距离**（Rayleigh distance）作为判据：

$$
r \gg \frac{2L^2}{\lambda}
$$

其中 $L$ 是阵列孔径（即阵列的总长度），$\lambda$ 是信号波长。对于一个 8 阵元、半波长间距的 ULA，孔径 $L = 7 \times \lambda/2 = 3.5\lambda$，对应的瑞利距离约为 $2 \times (3.5)^2 / 1 = 24.5\lambda$。以 10 GHz 毫米波雷达（$\lambda \approx 3$ cm）为例，这个距离约为 73 cm——对于车载雷达感知数米到数十米外的目标而言，远场条件是完全成立的。

远场假设带来的最关键结果是：**从特定方向 $\theta$ 入射的平面波，到达各阵元的路程差仅取决于阵元位置和入射角**，与阵元到信号源的绝对距离无关。具体地，以第 1 个阵元为参考，平面波到达第 $m$ 个阵元的路程比参考阵元多：

$$
\Delta r_m = (m-1)d\sin\theta
$$

这个几何关系如下图所示。平面波波前与阵列轴的夹角为 $90° - \theta$，由简单的三角关系即可推导出上式。

```text
          来波方向
           ↘  θ
    ────────────────────────► 阵列轴
    ●    ●    ●    ●    ●
    1    2    3    4    5
    ← d  →
    路程差：(m-1)·d·sinθ
```

正是这个整齐的等差路程差结构，才使得导向矢量具有等差相位递进的优美形式。如果是近场源，各阵元到信号源的距离各不相同，路程差不再是等差关系，导向矢量的表达式会复杂得多。

---

### 1.2.2 窄带假设：时间延迟变相位偏移

有了远场假设，我们知道了路程差 $\Delta r_m = (m-1)d\sin\theta$，对应的时间延迟为：

$$
\tau_m = \frac{(m-1)d\sin\theta}{c}
$$

下一个问题来了：信号延迟了 $\tau_m$ 秒，对接收信号意味着什么？

一般来说，时间延迟 $\tau$ 对应的操作是把信号 $s(t)$ 变成 $s(t - \tau)$，这在数学上是一个卷积运算，处理起来相对繁琐。但是，如果信号是**窄带信号**，情况会简单得多——时间延迟可以等效为一个纯相位偏移。

这里需要稍微解释一下。所谓**窄带信号**（narrowband signal），是指信号的带宽 $W$ 远小于其载波频率 $f_0$，即 $W \ll f_0$。这类信号可以表示为：

$$
z(t) = \text{Re}\{s(t) e^{j2\pi f_0 t}\}
$$

其中 $s(t)$ 是变化缓慢的复包络（即复基带信号），$e^{j2\pi f_0 t}$ 是高频载波。

当窄带信号经历一个小时延 $\tau$ 时，结果是：

$$
z(t - \tau) = \text{Re}\{s(t - \tau)\, e^{j2\pi f_0 (t-\tau)}\}
$$

由于 $s(t)$ 变化很慢（带宽窄），在 $\tau$ 很小时，有 $s(t - \tau) \approx s(t)$。于是：

$$
z(t - \tau) \approx \text{Re}\{s(t)\, e^{-j2\pi f_0 \tau}\, e^{j2\pi f_0 t}\}
$$

这意味着：**在窄带条件下，时间延迟 $\tau$ 等效于对复基带信号乘以一个相位因子 $e^{-j2\pi f_0 \tau}$**，而信号的包络形状 $s(t)$ 本身几乎不变。

这个近似成立的条件，可以更精确地表述为：

$$
W \cdot \tau_{\max} \ll 1
$$

其中 $\tau_{\max}$ 是阵列中最大的传播时延，也就是整个阵列两端之间的时延差。对于 $M$ 阵元 ULA，$\tau_{\max} = (M-1)d\sin\theta / c$，在 $d = \lambda/2$、$M = 8$、$\theta = 90°$ 的极端情况下，$\tau_{\max} = 3.5\lambda / c = 3.5 / f_0$。条件变为 $W \ll f_0 / 3.5 \approx 0.29 f_0$，对大多数通信和雷达系统均成立。

---

### 1.2.3 导向矢量的完整推导

现在把两个假设合在一起。对于来自方向 $\theta$ 的窄带远场信号，第 $m$ 个阵元接收到的复基带信号为：

$$
x_m(t) = s(t) \cdot e^{-j2\pi f_0 \tau_m} = s(t) \cdot e^{-j\frac{2\pi f_0}{c}(m-1)d\sin\theta}
$$

注意到 $f_0 / c = 1/\lambda$，代入得：

$$
x_m(t) = s(t) \cdot e^{-j\frac{2\pi}{\lambda}(m-1)d\sin\theta}
$$

定义**空间频率**（spatial frequency）：

$$
\psi = \frac{2\pi d}{\lambda}\sin\theta
$$

则 $x_m(t) = s(t) \cdot e^{-j(m-1)\psi}$。将所有 $M$ 个阵元的输出组成向量，单个信号源的情况下有：

$$
\mathbf{x}(t) = \underbrace{\begin{bmatrix} 1 \\ e^{-j\psi} \\ e^{-j2\psi} \\ \vdots \\ e^{-j(M-1)\psi} \end{bmatrix}}_{\mathbf{a}(\theta)} s(t) = \mathbf{a}(\theta)\, s(t)
$$

这正是**导向矢量**（steering vector）$\mathbf{a}(\theta)$ 的来源。它的每个分量都是模为 1 的复数，仅相位不同，且相位按阵元编号线性递增。

> **符号约定说明**：部分教材中导向矢量写作 $e^{+j(m-1)\psi}$，另一些写作 $e^{-j(m-1)\psi}$，两种写法均合理，差异来自时延定义和傅里叶变换符号约定的不同。本教程统一采用 $e^{j(m-1)\psi}$（正号），与 1.1 节保持一致。读者在阅读其他文献时注意对齐符号约定即可，不影响算法本质。

对于 $d = \lambda/2$ 的标准半波长间距，$\psi = \pi\sin\theta$，导向矢量化简为：

$$
\mathbf{a}(\theta) = \left[1,\ e^{j\pi\sin\theta},\ e^{j2\pi\sin\theta},\ \cdots,\ e^{j(M-1)\pi\sin\theta}\right]^\top
$$

这是后续几乎所有 DOA 算法公式中最常见的形式，值得多看几眼，熟悉它的结构。

---

### 1.2.4 空间频率与角度的关系

导向矢量把角度信息 $\theta$ "编码"进了空间频率 $\psi = \frac{2\pi d}{\lambda}\sin\theta$。理解这个映射关系，对后续理解分辨率和模糊问题非常重要。

首先，$\psi$ 关于 $\theta$ 的映射是**单调的**，但不是线性的——它通过 $\sin\theta$ 联系角度，在 $\theta = 0°$（正侧射方向）附近最为灵敏，在 $\theta \to \pm 90°$ 附近灵敏度下降。这意味着：同样是 $1°$ 的角度分辨率，在侧射方向比在端射方向更容易实现。

其次，为了让 $\theta$ 与 $\psi$ 之间保持一一对应（不产生模糊），需要 $\psi \in [-\pi, \pi)$ 恰好覆盖 $\sin\theta \in [-1, 1]$ 的全部取值范围，而不超出。由 $\psi = \frac{2\pi d}{\lambda}\sin\theta$，当 $\sin\theta = \pm 1$ 时，$|\psi|_{\max} = \frac{2\pi d}{\lambda}$。要求 $|\psi|_{\max} \leq \pi$，即：

$$
\frac{2\pi d}{\lambda} \leq \pi \implies d \leq \frac{\lambda}{2}
$$

这就是**半波长间距**的由来：它是保证角度无模糊的临界条件，正对应空间域的奈奎斯特采样定理。若 $d > \lambda/2$，则某些角度 $\theta_1 \neq \theta_2$ 会产生完全相同的导向矢量，即 $\mathbf{a}(\theta_1) = \mathbf{a}(\theta_2)$，算法无法区分它们，这种现象称为**栅瓣**（grating lobe）或空间混叠。

下面的代码演示了 $d = \lambda/2$ 与 $d = \lambda$ 两种间距下，空间频率 $\psi$ 与角度 $\theta$ 的映射关系：

```python
import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(-90, 90, 500)  # 角度范围（度）
theta_rad = np.deg2rad(theta)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, d, title in zip(axes,
                        [0.5, 1.0],
                        ['d = λ/2（无混叠）', 'd = λ（出现混叠）']):
    psi = 2 * np.pi * d * np.sin(theta_rad)
    ax.plot(theta, psi)
    ax.axhline(y=np.pi, color='r', linestyle='--', label='ψ = π')
    ax.axhline(y=-np.pi, color='r', linestyle='--', label='ψ = -π')
    ax.set_xlabel('入射角度 θ（度）')
    ax.set_ylabel('空间频率 ψ（弧度）')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()
```

运行后可以看到：当 $d = \lambda/2$ 时，$\psi$ 的变化范围恰好在 $[-\pi, \pi]$ 之内；当 $d = \lambda$ 时，$\psi$ 会超出这个范围，意味着有多个角度对应同一个 $\psi$ 值——模糊由此产生。

---

### 1.2.5 两个假设的适用范围与局限

学完这两个假设，有必要停下来想想：它们在什么情况下会失效？

**远场假设失效**的典型场景是近场定位，例如在室内对相距几十厘米的传感器节点进行定位，此时波前曲率不可忽略，需要使用近场模型，导向矢量的形式会包含距离项，DOA 估计也就变成了联合距离-角度估计。

**窄带假设失效**的情况则更常见于宽带系统，例如超宽带（UWB）定位和部分雷达体制中，信号带宽相对于载频不可忽略，时延不能再简单等效为相位偏移，需要采用宽带波束形成或在频域分子带处理。

对于本教程覆盖的大多数场景——通信系统中的阵列信号处理、窄带雷达与声呐、以及 FMCW 毫米波雷达中对单个频率点的处理——两个假设均成立，我们可以放心地使用本节导出的导向矢量模型。

---

### 1.2.6 小结

本节从物理出发，逐步推导了导向矢量的表达式。两个假设各司其职：

- **远场假设**：将球面波近似为平面波，使各阵元的路程差具有等差结构 $\Delta r_m = (m-1)d\sin\theta$；
- **窄带假设**：将时间延迟等效为相位偏移 $e^{j(m-1)\psi}$，使导向矢量可以用一个简洁的复指数向量表示。

两者合力，给出了 ULA 导向矢量的标准形式：

$$
\mathbf{a}(\theta) = \left[1,\ e^{j\psi},\ e^{j2\psi},\ \cdots,\ e^{j(M-1)\psi}\right]^\top, \quad \psi = \frac{2\pi d}{\lambda}\sin\theta
$$

而阵元间距取 $d = \lambda/2$，则是保证角度与空间频率之间一一对应、不产生模糊的必要条件。

至此，阵列观测模型 $\mathbf{x}(t) = \mathbf{A}(\boldsymbol{\theta})\mathbf{s}(t) + \mathbf{n}(t)$ 中的每一项都有了坚实的物理支撑。接下来，我们将在这个模型的基础上，引入**协方差矩阵**这一核心工具，进而理解常规波束形成是如何从观测数据中"寻找"信号方向的。
