"""
utils.py — 数据生成、特征提取、标签构造、Dataset 定义
=========================================================
本模块集中了所有与"数据"相关的功能，是整个框架的基础层。
其他脚本（train.py、eval.py）从这里导入所需工具，不重复定义。

主要内容：
  - 仿真数据生成（阵列观测模型）
  - 两种输入特征：协方差矩阵（CM）、原始 IQ
  - 两种标签格式：multi-hot 分类标签、归一化回归标签
  - DOADataset：统一的 PyTorch Dataset 接口
  - MUSIC 基线（用于 eval.py 中的对比实验）
"""

import numpy as np
import torch
from torch.utils.data import Dataset

# ================================================================
# 1. 阵列信号仿真
# ================================================================

def steering_vector(theta_deg, M, d=0.5):
    """
    计算 ULA 导向矢量
    theta_deg : 入射角（度）
    M         : 阵元数
    d         : 阵元间距（归一化波长，默认 0.5λ）
    返回      : 复数向量，形状 (M,)
    """
    theta = np.deg2rad(theta_deg)
    m = np.arange(M)
    return np.exp(1j * 2 * np.pi * d * np.sin(theta) * m)


def sample_angles(K, theta_min, theta_max, min_sep, rng, max_tries=2000):
    """
    随机采样 K 个满足最小间隔约束的角度（升序）
    min_sep : 任意两个信源角度之差的下限（度）
    """
    for _ in range(max_tries):
        thetas = np.sort(rng.uniform(theta_min, theta_max, K))
        if K == 1 or np.min(np.diff(thetas)) >= min_sep:
            return thetas
    raise RuntimeError(
        f"无法采样满足 min_sep={min_sep}° 的 {K} 个角度，"
        f"请放宽 min_sep 或缩小 K。"
    )


def generate_one_sample(thetas, M, N, snr_dB, d=0.5, rng=None):
    """
    按照阵列观测模型 X = A·S + N 生成单个样本
    thetas  : 信源角度列表（度）
    M       : 阵元数
    N       : 快拍数
    snr_dB  : 每个信源的信噪比（dB），信源等功率
    返回    : 观测矩阵 X，形状 (M, N)，复数
    """
    if rng is None:
        rng = np.random.default_rng()
    K = len(thetas)
    sigma2  = 1.0                           # 噪声功率固定为 1
    sig_pow = 10 ** (snr_dB / 10) * sigma2  # 信号功率由 SNR 决定

    A = np.column_stack([steering_vector(th, M, d) for th in thetas])  # (M, K)
    S = np.sqrt(sig_pow / 2) * (
        rng.standard_normal((K, N)) + 1j * rng.standard_normal((K, N)))
    noise = np.sqrt(sigma2 / 2) * (
        rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N)))
    return A @ S + noise  # (M, N)


def generate_dataset(num_samples, K, M, N, snr_range_dB,
                     theta_min=-60.0, theta_max=60.0, min_sep=5.0,
                     d=0.5, seed=0):
    """
    批量生成 DOA 仿真数据集

    参数
    ----
    num_samples   : 样本总数
    K             : 信源数（固定）
    M             : 阵元数
    N             : 快拍数
    snr_range_dB  : SNR 范围，(low, high)，每个样本随机采样
    theta_min/max : 角度范围（度）
    min_sep       : 多信源最小角度间隔（度）
    d             : 阵元间距（归一化波长）
    seed          : 随机种子

    返回
    ----
    X_data  : 观测矩阵，形状 (num_samples, M, N)，复数
    labels  : 真实 DOA，形状 (num_samples, K)，单位度，升序
    snrs    : 每个样本的 SNR（dB），形状 (num_samples,)
    """
    rng = np.random.default_rng(seed)
    X_data = np.zeros((num_samples, M, N), dtype=complex)
    labels = np.zeros((num_samples, K))
    snrs   = np.zeros(num_samples)

    for i in range(num_samples):
        thetas = sample_angles(K, theta_min, theta_max, min_sep, rng)
        snr    = rng.uniform(snr_range_dB[0], snr_range_dB[1])
        X_data[i] = generate_one_sample(thetas, M, N, snr, d, rng)
        labels[i] = thetas     # sample_angles 已保证升序
        snrs[i]   = snr

    return X_data, labels, snrs


# ================================================================
# 2. 输入特征提取
# ================================================================

def extract_cm_feature(X):
    """
    协方差矩阵特征（CM）：适合 CNN 输入
    输入  : X，形状 (M, N)，复数
    输出  : feature，形状 (2, M, M)，float32
            通道 0 = 实部，通道 1 = 虚部
    """
    M_, N_ = X.shape
    R = (X @ X.conj().T) / N_               # (M, M) 复数
    return np.stack([R.real, R.imag], axis=0).astype(np.float32)


def extract_iq_feature(X):
    """
    原始 IQ 序列特征：适合 LSTM 输入
    输入  : X，形状 (M, N)，复数
    输出  : feature，形状 (N, 2M)，float32
            每个时刻（快拍）对应 [Re(x_1),...,Re(x_M), Im(x_1),...,Im(x_M)]
    """
    iq = np.concatenate([X.real, X.imag], axis=0)  # (2M, N)
    return iq.T.astype(np.float32)                  # (N, 2M)


def build_features(X_data, feature_type='cm'):
    """
    批量提取特征
    feature_type : 'cm'（协方差矩阵）或 'iq'（原始 IQ 序列）
    返回形状     : 'cm' → (n, 2, M, M)；'iq' → (n, N, 2M)
    """
    if feature_type == 'cm':
        return np.stack([extract_cm_feature(X_data[i]) for i in range(len(X_data))])
    elif feature_type == 'iq':
        return np.stack([extract_iq_feature(X_data[i]) for i in range(len(X_data))])
    else:
        raise ValueError(f"未知 feature_type: {feature_type}，请选 'cm' 或 'iq'")


# ================================================================
# 3. 标签构造
# ================================================================

def make_classification_label(thetas, theta_min, theta_max, resolution):
    """
    分类标签：multi-hot 向量
    thetas : 真实角度列表（度）
    返回   : float32 向量，形状 (D,)，D = (theta_max - theta_min) / resolution + 1
    """
    grid  = np.arange(theta_min, theta_max + resolution * 0.5, resolution)
    label = np.zeros(len(grid), dtype=np.float32)
    for th in thetas:
        idx = int(round((th - theta_min) / resolution))
        idx = np.clip(idx, 0, len(grid) - 1)
        label[idx] = 1.0
    return label


def make_regression_label(thetas, theta_min, theta_max):
    """
    回归标签：将升序角度归一化到 [-1, 1]
    """
    thetas_sorted = np.sort(thetas)
    return (2.0 * (thetas_sorted - theta_min) / (theta_max - theta_min) - 1.0
            ).astype(np.float32)


def denormalize_angles(norm_values, theta_min, theta_max):
    """
    反归一化：[-1, 1] → 真实角度（度）
    """
    return (norm_values + 1.0) / 2.0 * (theta_max - theta_min) + theta_min


# ================================================================
# 4. DOADataset：统一的 PyTorch Dataset 接口
# ================================================================

class DOADataset(Dataset):
    """
    统一的 DOA 数据集类，支持分类和回归两种任务

    参数
    ----
    features     : 已提取的特征数组，形状视 feature_type 而定
    labels_deg   : 真实角度，形状 (n, K)，单位度
    task         : 'classification' 或 'regression'
    theta_min/max: 角度范围（度），构造标签时使用
    resolution   : 分类任务格点分辨率（度），仅 classification 用
    """
    def __init__(self, features, labels_deg,
                 task='classification',
                 theta_min=-60.0, theta_max=60.0, resolution=1.0):
        self.features = features
        self.task     = task

        if task == 'classification':
            self.labels = np.stack([
                make_classification_label(labels_deg[i], theta_min, theta_max, resolution)
                for i in range(len(labels_deg))
            ])
        elif task == 'regression':
            self.labels = np.stack([
                make_regression_label(labels_deg[i], theta_min, theta_max)
                for i in range(len(labels_deg))
            ])
        else:
            raise ValueError(f"未知 task: {task}")

        # 保存辅助信息，eval.py 中用于后处理
        self.theta_min  = theta_min
        self.theta_max  = theta_max
        self.resolution = resolution
        if task == 'classification':
            self.grid = np.arange(theta_min, theta_max + resolution * 0.5, resolution)
            self.D    = len(self.grid)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        x = torch.tensor(self.features[idx])
        y = torch.tensor(self.labels[idx])
        return x, y


# ================================================================
# 5. MUSIC 基线（eval.py 中用于对比）
# ================================================================

def music_doa(X, K, theta_grid_deg, d=0.5):
    """
    MUSIC 算法：给定观测矩阵 X，返回 K 个 DOA 估计值（度）
    失败时返回 None（低 SNR 下可能找不到足够峰值）
    """
    M, N = X.shape
    R = (X @ X.conj().T) / N
    eigvals, eigvecs = np.linalg.eigh(R)
    # eigh 升序，取前 M-K 个特征向量作为噪声子空间
    U_n = eigvecs[:, :M - K]
    En  = U_n @ U_n.conj().T

    # 谱搜索
    theta_grid = np.deg2rad(theta_grid_deg)
    spectrum = np.zeros(len(theta_grid_deg))
    for i, theta in enumerate(theta_grid):
        m = np.arange(M)
        a = np.exp(1j * 2 * np.pi * d * np.sin(theta) * m)
        denom = np.real(a.conj() @ En @ a)
        spectrum[i] = 1.0 / (denom + 1e-12)

    # 峰值检测
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(spectrum)
    if len(peaks) < K:
        return None
    top_idx = peaks[np.argsort(spectrum[peaks])[-K:]]
    return np.sort(theta_grid_deg[top_idx])
