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