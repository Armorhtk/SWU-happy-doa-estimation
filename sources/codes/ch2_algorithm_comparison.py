"""
ch2_algorithm_comparison.py
============================
第二章：经典 DOA 估计算法 —— 完整实现与对比实验（含 Capon/MVDR）

算法模块：
  CBF / Capon(MVDR) / MUSIC / Root-MUSIC / TLS-ESPRIT

辅助模块：
  MDL 信源数估计 / 前向-后向空间平滑

实验模块：
  exp1  RMSE vs SNR（五算法 + CRB）
  exp2  RMSE vs 快拍数
  exp3  分辨率概率 vs 角度间隔
  exp4  空间平滑处理相干信号演示
  exp5  三方法空间谱对比（CBF / Capon / MUSIC）

用法：
  python ch2_algorithm_comparison.py            # 全部实验
  python ch2_algorithm_comparison.py --exp 1    # 仅实验一
"""

import argparse
import inspect
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# ============================================================
# 全局仿真参数（统一在此修改）
# ============================================================
CONFIG = dict(
    M           = 8,
    d           = 0.5,
    K           = 2,
    thetas_true = [20.0, 40.0],
    N_trials    = 500,
    theta_grid  = np.linspace(-90, 90, 1801),
    seed        = 42,
    capon_eps   = 0.01,      # Capon 对角加载量 ε
)

# ============================================================
# ① 公共工具
# ============================================================

def steering_vector(theta_deg, M, d=0.5):
    """ULA 导向矢量，长度 M"""
    theta = np.deg2rad(theta_deg)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * np.arange(M))


def sample_cov(X):
    """样本协方差矩阵  R_hat = X X^H / N"""
    return (X @ X.conj().T) / X.shape[1]


def generate_data(thetas_true, M, K, N, snr_dB, d=0.5, rng=None):
    """生成独立信源仿真数据，返回 (X, R_hat)"""
    if rng is None:
        rng = np.random.default_rng()
    sig_pow = 10 ** (snr_dB / 10)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
    S = np.sqrt(sig_pow / 2) * (
        rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N))
    )
    noise = (1 / np.sqrt(2)) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
    )
    X = A @ S + noise
    return X, sample_cov(X)


def crb_std_deg(thetas_deg, M, N, snr_dB, d=0.5):
    """
    单信源近似 CRB 标准差（度），对多信源取 RMS 作为参考线
    """
    snr = 10 ** (snr_dB / 10)
    B2 = sum(m ** 2 for m in range(M))
    crbs = []
    for th in thetas_deg:
        phi = np.deg2rad(th)
        crb = 1.0 / (2 * N * snr * (2 * np.pi * d) ** 2 * np.cos(phi) ** 2 * B2)
        crbs.append(np.rad2deg(np.sqrt(crb)))
    return float(np.sqrt(np.mean(np.array(crbs) ** 2)))


def _pick_peaks(spec, theta_grid, K):
    """从谱中取最大 K 个峰值对应的角度"""
    peaks, _ = find_peaks(spec)
    if len(peaks) < K:
        return np.sort(theta_grid[np.argsort(spec)[-K:]])
    top = peaks[np.argsort(spec[peaks])[-K:]]
    return np.sort(theta_grid[top])


# ============================================================
# ② MDL 信源数估计
# ============================================================

def mdl_estimate(R_hat, N):
    """MDL 信源数估计，返回 K_hat"""
    M = R_hat.shape[0]
    eigvals = np.linalg.eigvalsh(R_hat)[::-1].real
    scores = []
    for d in range(M):
        noise_eigs = eigvals[d:]
        n = M - d
        geo = np.exp(np.mean(np.log(np.maximum(noise_eigs, 1e-12))))
        ari = np.mean(noise_eigs)
        L_d = -N * n * np.log(geo / (ari + 1e-12))
        p_d = d * (2 * M - d)
        scores.append(-L_d + 0.5 * p_d * np.log(N))
    return int(np.argmin(scores))


# ============================================================
# ③ 空间平滑
# ============================================================

def spatial_smoothing(R_hat, P):
    """前向空间平滑，子阵长度 P，返回 (P×P) 矩阵"""
    M = R_hat.shape[0]
    L = M - P + 1
    R_ss = np.zeros((P, P), dtype=complex)
    for l in range(L):
        R_ss += R_hat[l:l + P, l:l + P]
    return R_ss / L


def fb_spatial_smoothing(R_hat, P):
    """前向-后向空间平滑（FBSS），子阵长度 P，返回 (P×P) 矩阵"""
    R_ss = spatial_smoothing(R_hat, P)
    J = np.eye(P)[::-1]
    R_b = J @ R_ss.conj() @ J
    return 0.5 * (R_ss + R_b)


# ============================================================
# ④ DOA 算法
# ============================================================

def cbf(R_hat, K, theta_grid, M, d=0.5):
    """常规波束形成，返回估计 DOA（度）"""
    spec = np.array([
        np.real(steering_vector(th, M, d).conj()
                @ R_hat @ steering_vector(th, M, d))
        for th in theta_grid
    ])
    return _pick_peaks(spec, theta_grid, K)


def capon(R_hat, K, theta_grid, M, d=0.5, eps=0.0):
    """
    Capon/MVDR 自适应波束形成，返回估计 DOA（度）
    eps : 对角加载量（建议 0.01 ~ 噪声功率量级）
    """
    R_loaded = R_hat + eps * np.eye(M)
    R_inv = np.linalg.inv(R_loaded)
    spec = np.zeros(len(theta_grid))
    for i, th in enumerate(theta_grid):
        a = steering_vector(th, M, d)
        denom = np.real(a.conj() @ R_inv @ a)
        spec[i] = 1.0 / (denom + 1e-12)
    return _pick_peaks(spec, theta_grid, K)


def capon_spectrum_only(R_hat, theta_grid, M, d=0.5, eps=0.0):
    """返回 Capon 谱（用于绘图）"""
    R_inv = np.linalg.inv(R_hat + eps * np.eye(M))
    spec = np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj()
                       @ R_inv @ steering_vector(th, M, d)) + 1e-12)
        for th in theta_grid
    ])
    return spec


def music(R_hat, K, theta_grid, M, d=0.5):
    """标准 MUSIC 谱搜索，返回估计 DOA（度）"""
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    En = U_n @ U_n.conj().T
    spec = np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj()
                       @ En @ steering_vector(th, M, d)) + 1e-12)
        for th in theta_grid
    ])
    return _pick_peaks(spec, theta_grid, K)


def music_spectrum_only(R_hat, K, theta_grid, M, d=0.5):
    """返回 MUSIC 伪谱（用于绘图）"""
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    En = U_n @ U_n.conj().T
    return np.array([
        1.0 / (np.real(steering_vector(th, M, d).conj()
                       @ En @ steering_vector(th, M, d)) + 1e-12)
        for th in theta_grid
    ])


def root_music(R_hat, K, d=0.5):
    """Root-MUSIC（ULA 专用，多项式求根），返回估计 DOA（度）"""
    M = R_hat.shape[0]
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_n = eigvecs[:, :-K]
    C = U_n @ U_n.conj().T

    coeffs = np.zeros(2 * M - 1, dtype=complex)
    for i in range(M):
        for j in range(M):
            coeffs[i - j + (M - 1)] += C[i, j]

    roots = np.roots(coeffs)
    inside = roots[np.abs(roots) < 1.0 - 1e-6]
    if len(inside) < K:
        inside = roots
    idx = np.argsort(np.abs(np.abs(inside) - 1))[:K]
    selected = inside[idx]

    psi = np.angle(selected)
    sin_theta = np.clip(psi / (2 * np.pi * d), -1.0, 1.0)
    return np.sort(np.rad2deg(np.arcsin(sin_theta)))


def esprit(R_hat, K, d=0.5, method='TLS'):
    """TLS/LS-ESPRIT（ULA 专用），返回估计 DOA（度）"""
    M = R_hat.shape[0]
    eigvals, eigvecs = np.linalg.eigh(R_hat)
    U_s = eigvecs[:, -K:]

    U_s1 = U_s[:-1, :]
    U_s2 = U_s[1:, :]

    if method == 'LS':
        Psi = np.linalg.lstsq(U_s1, U_s2, rcond=None)[0]
    else:  # TLS
        C = np.hstack([U_s1, U_s2])
        _, _, Vh = np.linalg.svd(C)
        V = Vh.conj().T
        V12 = V[:K, K:]
        V22 = V[K:, K:]
        Psi = -V12 @ np.linalg.inv(V22)

    eigs = np.linalg.eigvals(Psi)
    psi = np.angle(eigs)
    sin_theta = np.clip(psi / (2 * np.pi * d), -1.0, 1.0)
    return np.sort(np.rad2deg(np.arcsin(sin_theta)))


# ============================================================
# ⑤ 蒙特卡洛框架（自动识别函数签名）
# ============================================================

def monte_carlo_rmse(algo_func, algo_kwargs,
                     thetas_true, M, K, N, snr_dB, d,
                     n_trials, seed=0):
    """
    蒙特卡洛 RMSE 计算
    algo_func   : 算法函数
    algo_kwargs : 传给算法的额外关键字参数（字典）
    返回        : (rmse, failure_rate)
    """
    rng = np.random.default_rng(seed)
    errors_sq = []
    failures = 0
    theta_grid = CONFIG['theta_grid']
    has_grid = 'theta_grid' in inspect.signature(algo_func).parameters

    for _ in range(n_trials):
        _, R_hat = generate_data(thetas_true, M, K, N, snr_dB, d, rng)
        try:
            if has_grid:
                est = algo_func(R_hat, K, theta_grid, M, d, **algo_kwargs)
            else:
                est = algo_func(R_hat, K, d, **algo_kwargs)

            if len(est) == K:
                err = np.sort(est) - np.sort(thetas_true)
                errors_sq.append(np.mean(err ** 2))
            else:
                failures += 1
        except Exception:
            failures += 1

    if not errors_sq:
        return np.nan, 1.0
    return float(np.sqrt(np.mean(errors_sq))), failures / n_trials


# ============================================================
# ⑥ 实验一：RMSE vs SNR
# ============================================================

def exp1_rmse_vs_snr():
    """实验一：固定快拍数，扫描 SNR，五算法 RMSE 对比"""
    cfg = CONFIG
    M, d, K = cfg['M'], cfg['d'], cfg['K']
    thetas = cfg['thetas_true']
    eps = cfg['capon_eps']
    N = 200
    snr_range = np.arange(-10, 21, 2)
    n_trials = cfg['N_trials']
    seed = cfg['seed']

    algos = [
        ('CBF',         cbf,        {}),
        ('Capon/MVDR',  capon,      {'eps': eps}),
        ('MUSIC',       music,      {}),
        ('Root-MUSIC',  root_music, {}),
        ('TLS-ESPRIT',  esprit,     {}),
    ]

    results = {name: [] for name, _, _ in algos}
    crb_curve = []

    print("实验一：RMSE vs SNR（5 种算法）")
    for snr in snr_range:
        print(f"  SNR = {snr:+.0f} dB ...", end=' ', flush=True)
        crb_curve.append(crb_std_deg(thetas, M, N, snr, d))
        for name, func, kwargs in algos:
            rmse, _ = monte_carlo_rmse(
                func, kwargs, thetas, M, K, N, snr, d, n_trials, seed
            )
            results[name].append(rmse)
        print("done")

    fig, ax = plt.subplots(figsize=(9, 5))
    styles = ['b-o', 'g-s', 'r-^', 'm-D', 'c-v']
    for (name, _, _), style in zip(algos, styles):
        ax.semilogy(snr_range, results[name], style,
                    label=name, linewidth=1.5, markersize=5)
    ax.semilogy(snr_range, crb_curve, 'k-', linewidth=2.5,
                label='CRB（单信源近似）')
    ax.set_xlabel('SNR（dB）')
    ax.set_ylabel('RMSE（度）')
    ax.set_title(f'实验一：RMSE vs SNR（M={M}, N={N}, K={K}）')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.4)
    plt.tight_layout()
    plt.savefig('exp1_rmse_vs_snr.png', dpi=150)
    plt.show()
    print("  图像已保存为 exp1_rmse_vs_snr.png\n")


# ============================================================
# ⑦ 实验二：RMSE vs 快拍数
# ============================================================

def exp2_rmse_vs_snapshots():
    """实验二：固定 SNR，扫描快拍数，五算法 RMSE 对比"""
    cfg = CONFIG
    M, d, K = cfg['M'], cfg['d'], cfg['K']
    thetas = cfg['thetas_true']
    eps = cfg['capon_eps']
    snr_dB = 5
    snap_range = np.unique(
        np.round(np.logspace(np.log10(10), np.log10(2000), 20)).astype(int)
    )
    n_trials = cfg['N_trials']
    seed = cfg['seed']

    algos = [
        ('CBF',         cbf,        {}),
        ('Capon/MVDR',  capon,      {'eps': eps}),
        ('MUSIC',       music,      {}),
        ('Root-MUSIC',  root_music, {}),
        ('TLS-ESPRIT',  esprit,     {}),
    ]

    results = {name: [] for name, _, _ in algos}
    crb_curve = []

    print("实验二：RMSE vs 快拍数（5 种算法）")
    for N in snap_range:
        print(f"  N = {N} ...", end=' ', flush=True)
        crb_curve.append(crb_std_deg(thetas, M, N, snr_dB, d))
        for name, func, kwargs in algos:
            rmse, _ = monte_carlo_rmse(
                func, kwargs, thetas, M, K, N, snr_dB, d, n_trials, seed
            )
            results[name].append(rmse)
        print("done")

    fig, ax = plt.subplots(figsize=(9, 5))
    styles = ['b-o', 'g-s', 'r-^', 'm-D', 'c-v']
    for (name, _, _), style in zip(algos, styles):
        ax.loglog(snap_range, results[name], style,
                  label=name, linewidth=1.5, markersize=5)
    ax.loglog(snap_range, crb_curve, 'k-', linewidth=2.5,
              label='CRB（单信源近似）')
    ax.set_xlabel('快拍数 N')
    ax.set_ylabel('RMSE（度）')
    ax.set_title(f'实验二：RMSE vs 快拍数（M={M}, SNR={snr_dB} dB, K={K}）')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.4)
    plt.tight_layout()
    plt.savefig('exp2_rmse_vs_snapshots.png', dpi=150)
    plt.show()
    print("  图像已保存为 exp2_rmse_vs_snapshots.png\n")


# ============================================================
# ⑧ 实验三：分辨率概率 vs 角度间隔
# ============================================================

def exp3_resolution_probability():
    """实验三：固定 SNR 和快拍数，扫描角度间隔，统计成功分辨概率"""
    cfg = CONFIG
    M, d, K = cfg['M'], cfg['d'], cfg['K']
    eps = cfg['capon_eps']
    snr_dB = 10
    N = 200
    theta_center = 30.0
    delta_range = np.arange(2, 22, 1)
    theta_grid = cfg['theta_grid']
    n_trials = cfg['N_trials']
    seed = cfg['seed']

    algos = [
        ('CBF',         cbf,        {}),
        ('Capon/MVDR',  capon,      {'eps': eps}),
        ('MUSIC',       music,      {}),
        ('Root-MUSIC',  root_music, {}),
        ('TLS-ESPRIT',  esprit,     {}),
    ]

    results = {name: [] for name, _, _ in algos}

    print("实验三：分辨率概率 vs 角度间隔（5 种算法）")
    for delta in delta_range:
        thetas = [theta_center - delta / 2, theta_center + delta / 2]
        threshold = delta / 2.0
        print(f"  Δθ = {delta}° ...", end=' ', flush=True)

        for name, func, kwargs in algos:
            rng = np.random.default_rng(seed)
            sig_pow = 10 ** (snr_dB / 10)
            A = np.column_stack([steering_vector(th, M, d) for th in thetas])
            has_grid = 'theta_grid' in inspect.signature(func).parameters
            success = 0

            for _ in range(n_trials):
                S = np.sqrt(sig_pow / 2) * (
                    rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N))
                )
                noise = (1 / np.sqrt(2)) * (
                    rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
                )
                X = A @ S + noise
                R_hat = sample_cov(X)
                try:
                    if has_grid:
                        est = func(R_hat, K, theta_grid, M, d, **kwargs)
                    else:
                        est = func(R_hat, K, d, **kwargs)
                    if len(est) == K:
                        err = np.sort(est) - np.sort(thetas)
                        if np.all(np.abs(err) < threshold):
                            success += 1
                except Exception:
                    pass

            results[name].append(success / n_trials)
        print("done")

    rayleigh = np.rad2deg(1.0 / (M * d))
    fig, ax = plt.subplots(figsize=(9, 5))
    styles = ['b-o', 'g-s', 'r-^', 'm-D', 'c-v']
    for (name, _, _), style in zip(algos, styles):
        ax.plot(delta_range, results[name], style,
                label=name, linewidth=1.5, markersize=5)
    ax.axvline(x=rayleigh, color='gray', linestyle=':', linewidth=1.5,
               label=f'瑞利分辨率 ≈ {rayleigh:.1f}°')
    ax.set_xlabel('角度间隔 Δθ（度）')
    ax.set_ylabel('成功分辨概率')
    ax.set_title(f'实验三：分辨率概率 vs 角度间隔（M={M}, SNR={snr_dB} dB, N={N}）')
    ax.set_ylim([0, 1.05])
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig('exp3_resolution_probability.png', dpi=150)
    plt.show()
    print("  图像已保存为 exp3_resolution_probability.png\n")


# ============================================================
# ⑨ 演示四：空间平滑处理相干信号
# ============================================================

def demo_spatial_smoothing():
    """演示：完全相干信号 + FBSS + MUSIC"""
    M, d, K = 12, 0.5, 2
    P = 8
    thetas_true = [20.0, 40.0]
    N, snr_dB = 500, 10
    theta_grid = np.linspace(-90, 90, 1801)

    rng = np.random.default_rng(42)
    sig_pow = 10 ** (snr_dB / 10)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
    alpha = 0.9 * np.exp(1j * np.pi / 4)
    s1 = np.sqrt(sig_pow / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    S = np.vstack([s1, alpha * s1])
    noise = (1 / np.sqrt(2)) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
    )
    X = A @ S + noise
    R_hat = sample_cov(X)

    spec_raw = music_spectrum_only(R_hat, K, theta_grid, M, d)
    spec_ss  = music_spectrum_only(spatial_smoothing(R_hat, P),    K, theta_grid, P, d)
    spec_fb  = music_spectrum_only(fb_spatial_smoothing(R_hat, P), K, theta_grid, P, d)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, spec, title in zip(axes,
                                [spec_raw, spec_ss, spec_fb],
                                ['无平滑（MUSIC 失效）',
                                 '前向空间平滑（SS-MUSIC）',
                                 '前向-后向平滑（FBSS-MUSIC）']):
        s_dB = 10 * np.log10(spec / spec.max() + 1e-10)
        ax.plot(theta_grid, s_dB, 'b-', linewidth=1.2)
        for th in thetas_true:
            ax.axvline(x=th, color='r', linestyle='--', linewidth=1)
        ax.set_xlabel('角度 θ（度）')
        ax.set_ylabel('归一化伪谱（dB）')
        ax.set_title(title)
        ax.set_xlim([-90, 90])
        ax.set_ylim([-30, 2])
        ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig('demo_spatial_smoothing.png', dpi=150)
    plt.show()
    print("  图像已保存为 demo_spatial_smoothing.png\n")


# ============================================================
# ⑩ 演示五：三方法空间谱对比
# ============================================================

def demo_spectrum_comparison():
    """演示：两个靠近信源（间隔 10°），CBF / Capon / MUSIC 谱对比"""
    M, d, K = 8, 0.5, 2
    thetas_true = [20.0, 30.0]
    SNR_dB, N = 15, 300
    theta_grid = np.linspace(-90, 90, 1801)
    eps = CONFIG['capon_eps']

    rng = np.random.default_rng(42)
    sig_pow = 10 ** (SNR_dB / 10)
    A = np.column_stack([steering_vector(th, M, d) for th in thetas_true])
    S = np.sqrt(sig_pow / 2) * (
        rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N))
    )
    noise = (1 / np.sqrt(2)) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))
    )
    X = A @ S + noise
    R_hat = sample_cov(X)

    spec_cbf = np.array([
        np.real(steering_vector(th, M, d).conj() @ R_hat @ steering_vector(th, M, d))
        for th in theta_grid
    ])
    spec_cap = capon_spectrum_only(R_hat, theta_grid, M, d, eps=eps)
    spec_mus = music_spectrum_only(R_hat, K, theta_grid, M, d)

    def to_dB(s):
        return 10 * np.log10(s / s.max() + 1e-10)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(theta_grid, to_dB(spec_cbf), 'b-',  linewidth=1.2, label='CBF')
    ax.plot(theta_grid, to_dB(spec_cap), 'g--', linewidth=1.5, label='Capon/MVDR')
    ax.plot(theta_grid, to_dB(spec_mus), 'r-',  linewidth=1.2, label='MUSIC')
    for th in thetas_true:
        ax.axvline(x=th, color='k', linestyle=':', linewidth=1)
    ax.set_xlabel('角度 θ（度）')
    ax.set_ylabel('归一化幅度（dB）')
    ax.set_title(f'三方法空间谱对比（M={M}, SNR={SNR_dB} dB, Δθ=10°）')
    ax.set_xlim([-90, 90])
    ax.set_ylim([-35, 2])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig('demo_spectrum_comparison.png', dpi=150)
    plt.show()
    print("  图像已保存为 demo_spectrum_comparison.png\n")


# ============================================================
# 主入口
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='第二章算法对比实验（CBF / Capon / MUSIC / Root-MUSIC / ESPRIT）'
    )
    parser.add_argument(
        '--exp', type=int, choices=[0, 1, 2, 3, 4, 5], default=0,
        help=('0=全部  '
              '1=RMSE vs SNR  '
              '2=RMSE vs 快拍数  '
              '3=分辨率概率  '
              '4=空间平滑演示  '
              '5=三方法谱对比')
    )
    args = parser.parse_args()

    exp_map = {
        1: exp1_rmse_vs_snr,
        2: exp2_rmse_vs_snapshots,
        3: exp3_resolution_probability,
        4: demo_spatial_smoothing,
        5: demo_spectrum_comparison,
    }

    if args.exp == 0:
        for fn in exp_map.values():
            fn()
    else:
        exp_map[args.exp]()