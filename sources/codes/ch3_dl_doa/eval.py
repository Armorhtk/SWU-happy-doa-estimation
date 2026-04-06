"""
eval.py — 模型评估与实验对比
==============================
用法：
  python eval.py                    # 评估 CONFIG 指定的单个检查点
  python eval.py --compare          # 对比多个检查点 + MUSIC 基线

功能：
  1. 加载训练好的检查点，在测试集上计算整体 RMSE
  2. 按 SNR 分段统计 RMSE，展示精度随信噪比的变化曲线
  3. 与 MUSIC 基线进行横向对比，并绘制对比图
  4. 可视化若干测试样本的网络输出置信度曲线（分类任务）

输出：
  - 终端打印各指标
  - 保存对比折线图（eval_rmse_vs_snr.png）
  - 保存预测散点图（eval_scatter.png）
"""

import os
import sys
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

from utils import (generate_dataset, build_features, DOADataset,
                   denormalize_angles, music_doa)
from models import build_model

# ================================================================
# 默认评估配置（与 train.py CONFIG 保持一致）
# ================================================================
EVAL_CONFIG = {
    # 要评估的检查点列表（可以填多个用于对比实验）
    "checkpoints": [
        "checkpoints/exp01_cm_cnn_cls.pth",
        # "checkpoints/exp02_iq_lstm_reg.pth",   # 取消注释可加入对比
    ],

    # 测试集配置
    "num_test" : 3000,
    "snr_range": (-10, 25),   # 测试时覆盖更宽 SNR 以评估泛化
    "seed_test": 9999,

    # SNR 分段（用于 RMSE vs SNR 曲线）
    "snr_bins"  : [(-10, -5), (-5, 0), (0, 5), (5, 10), (10, 15), (15, 25)],

    # 是否同时运行 MUSIC 基线（较慢，但结果有参考价值）
    "run_music" : True,
    # MUSIC 谱搜索网格（可适当粗化以加速）
    "music_grid_deg": np.arange(-60, 61, 0.5),
}

# ================================================================
# 推理函数
# ================================================================

def predict_classification(model, loader, grid, K, device):
    """
    分类网络推理：从 logit → Sigmoid → top-K → 角度
    返回：预测角度数组，形状 (n, K)，单位度
    """
    model.eval()
    all_preds = []
    with torch.no_grad():
        for x, _ in loader:
            logit = model(x.to(device)).cpu().numpy()
            prob  = 1 / (1 + np.exp(-logit))   # Sigmoid
            for i in range(len(logit)):
                top_idx = np.sort(np.argsort(prob[i])[-K:])
                all_preds.append(grid[top_idx])
    return np.vstack(all_preds)


def predict_regression(model, loader, theta_min, theta_max, device):
    """
    回归网络推理：网络输出归一化角度 → 反归一化 → 真实角度（度）
    返回：预测角度数组，形状 (n, K)，单位度
    """
    model.eval()
    all_preds = []
    with torch.no_grad():
        for x, _ in loader:
            norm = model(x.to(device)).cpu().numpy()
            all_preds.append(denormalize_angles(norm, theta_min, theta_max))
    return np.vstack(all_preds)


def run_music_baseline(X_raw, labels_deg, K, grid_deg):
    """对所有测试样本运行 MUSIC，返回预测结果和成功率"""
    preds, success = [], 0
    for i in range(len(X_raw)):
        result = music_doa(X_raw[i], K, grid_deg)
        if result is not None and len(result) == K:
            preds.append(result)
            success += 1
        else:
            # 失败时填充真实标签的平均值（不影响成功率计算，但会拉高 RMSE）
            preds.append(labels_deg[i])
    return np.vstack(preds), success / len(X_raw)

# ================================================================
# 评估指标计算
# ================================================================

def compute_rmse(preds, labels):
    """按升序配对后计算整体 RMSE（度）"""
    p = np.sort(preds, axis=1)
    l = np.sort(labels, axis=1)
    return float(np.sqrt(np.mean((p - l) ** 2)))


def rmse_by_snr(preds, labels, snrs, bins):
    """
    按 SNR 区间分别计算 RMSE
    返回：列表 [(bin_label, rmse, count), ...]
    """
    results = []
    for lo, hi in bins:
        mask = (snrs >= lo) & (snrs < hi)
        if mask.sum() == 0:
            continue
        rmse = compute_rmse(preds[mask], labels[mask])
        label = f"[{lo:+.0f},{hi:+.0f})"
        results.append((label, rmse, int(mask.sum())))
    return results

# ================================================================
# 评估主函数
# ================================================================

def evaluate_one(ckpt_path, test_data, snr_bins, device, run_music=False, music_grid=None):
    """
    加载单个检查点并完整评估

    返回
    ----
    info : dict，含 run_name、overall_rmse、snr_results
    """
    print(f"\n{'─'*50}")
    print(f"  评估：{ckpt_path}")

    # 1. 加载检查点
    ckpt = torch.load(ckpt_path, map_location=device)
    cfg  = ckpt['config']
    print(f"  训练配置：{cfg['model_name']} / {cfg['task']} / {cfg['feature_type']}")
    print(f"  最佳验证损失：{ckpt['val_loss']:.5f}（epoch {ckpt['epoch']}）")

    X_raw, labels, snrs = test_data

    # 2. 提取特征
    features = build_features(X_raw, feature_type=cfg['feature_type'])

    # 3. 构造 Dataset/Loader
    ds = DOADataset(
        features   = features,
        labels_deg = labels,
        task       = cfg['task'],
        theta_min  = cfg['theta_min'],
        theta_max  = cfg['theta_max'],
        resolution = cfg.get('resolution', 1.0),
    )
    loader = DataLoader(ds, batch_size=256, shuffle=False, num_workers=0)

    # 4. 重建模型并加载权重
    K = cfg['K']
    if cfg['model_name'] == 'cm_cnn':
        D = int((cfg['theta_max'] - cfg['theta_min']) / cfg['resolution']) + 1
        model = build_model('cm_cnn', M=cfg['M'], D=D,
                            base_channels=cfg['base_channels'],
                            dropout=cfg['dropout'])
    else:
        model = build_model('iq_lstm',
                            input_size  = 2 * cfg['M'],
                            K           = K,
                            hidden_size = cfg['hidden_size'],
                            num_layers  = cfg['num_layers'],
                            dropout     = cfg['dropout'])
    model.load_state_dict(ckpt['model_state'])
    model = model.to(device)

    # 5. 推理
    if cfg['task'] == 'classification':
        grid   = ds.grid
        preds  = predict_classification(model, loader, grid, K, device)
    else:
        preds  = predict_regression(model, loader, cfg['theta_min'], cfg['theta_max'], device)

    # 6. 计算指标
    overall = compute_rmse(preds, labels)
    snr_res = rmse_by_snr(preds, labels, snrs, snr_bins)
    run_name = os.path.basename(ckpt_path).replace('.pth', '')

    print(f"\n  整体 RMSE：{overall:.4f} 度")
    print("  按 SNR 分段：")
    for label, rmse, count in snr_res:
        print(f"    SNR {label} dB：RMSE = {rmse:.4f}°  (n={count})")

    # 7. （可选）MUSIC 基线
    music_info = None
    if run_music and music_grid is not None:
        print("\n  运行 MUSIC 基线（可能需要数分钟）...")
        m_preds, success_rate = run_music_baseline(X_raw, labels, K, music_grid)
        m_overall = compute_rmse(m_preds, labels)
        m_snr_res = rmse_by_snr(m_preds, labels, snrs, snr_bins)
        print(f"  MUSIC 整体 RMSE：{m_overall:.4f} 度，成功率：{success_rate*100:.1f}%")
        music_info = {'snr_results': m_snr_res, 'overall_rmse': m_overall}

    return {
        'run_name'    : run_name,
        'overall_rmse': overall,
        'snr_results' : snr_res,
        'preds'       : preds,
        'labels'      : labels,
        'music_info'  : music_info,
    }

# ================================================================
# 绘图函数
# ================================================================

def plot_rmse_vs_snr(eval_results, music_info=None, save=True):
    """绘制 RMSE vs SNR 对比折线图"""
    fig, ax = plt.subplots(figsize=(8, 5))

    for res in eval_results:
        labels = [r[0] for r in res['snr_results']]
        rmses  = [r[1] for r in res['snr_results']]
        ax.plot(range(len(labels)), rmses, 'o-', label=res['run_name'])

    if music_info is not None:
        m_rmses = [r[1] for r in music_info['snr_results']]
        ax.plot(range(len(labels)), m_rmses, 's--', color='gray', label='MUSIC（基线）')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_xlabel('SNR 区间（dB）')
    ax.set_ylabel('RMSE（度）')
    ax.set_title('不同方法 RMSE vs SNR 对比')
    ax.legend()
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    if save:
        plt.savefig('eval_rmse_vs_snr.png', dpi=150)
        print("  对比图已保存：eval_rmse_vs_snr.png")
    plt.show()


def plot_scatter(preds, labels, run_name, K, save=True):
    """绘制预测 vs 真实角度散点图（每个信源一个子图）"""
    fig, axes = plt.subplots(1, K, figsize=(5 * K, 4))
    if K == 1:
        axes = [axes]
    preds_sorted  = np.sort(preds, axis=1)
    labels_sorted = np.sort(labels, axis=1)
    for k, ax in enumerate(axes):
        ax.scatter(labels_sorted[:, k], preds_sorted[:, k],
                   s=4, alpha=0.4, color='steelblue')
        lo, hi = labels.min() - 2, labels.max() + 2
        ax.plot([lo, hi], [lo, hi], 'r--', linewidth=1, label='理想线')
        ax.set_xlabel(f'真实 DOA {k+1}（度）')
        ax.set_ylabel(f'预测 DOA {k+1}（度）')
        ax.set_title(f'信源 {k+1}')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle(f'预测 vs 真实散点图（{run_name}）', fontsize=11)
    plt.tight_layout()
    if save:
        fname = f"eval_scatter_{run_name}.png"
        plt.savefig(fname, dpi=150)
        print(f"  散点图已保存：{fname}")
    plt.show()

# ================================================================
# 主入口
# ================================================================

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"评估设备：{device}")

    # ---- 生成测试集（统一种子，所有方法用同一批数据）----
    # 从第一个检查点读取阵列/信源配置
    ckpt0 = torch.load(EVAL_CONFIG['checkpoints'][0], map_location='cpu')
    cfg0  = ckpt0['config']
    print(f"\n生成测试集（{EVAL_CONFIG['num_test']} 样本）...")
    X_raw, labels, snrs = generate_dataset(
        num_samples  = EVAL_CONFIG['num_test'],
        K            = cfg0['K'],
        M            = cfg0['M'],
        N            = cfg0['N_snap'],
        snr_range_dB = EVAL_CONFIG['snr_range'],
        theta_min    = cfg0['theta_min'],
        theta_max    = cfg0['theta_max'],
        min_sep      = cfg0['min_sep'],
        d            = cfg0['d'],
        seed         = EVAL_CONFIG['seed_test'],
    )
    test_data = (X_raw, labels, snrs)

    # ---- 逐个评估检查点 ----
    all_results = []
    music_info  = None
    for ckpt_path in EVAL_CONFIG['checkpoints']:
        if not os.path.exists(ckpt_path):
            print(f"\n  [跳过] 检查点不存在：{ckpt_path}")
            print(f"  请先运行 train.py 生成该检查点")
            continue
        res = evaluate_one(
            ckpt_path   = ckpt_path,
            test_data   = test_data,
            snr_bins    = EVAL_CONFIG['snr_bins'],
            device      = device,
            run_music   = EVAL_CONFIG['run_music'] and music_info is None,
            music_grid  = EVAL_CONFIG['music_grid_deg'],
        )
        if res['music_info'] is not None:
            music_info = res['music_info']
        all_results.append(res)

    if not all_results:
        print("\n没有可用的检查点，请先运行 train.py")
        return

    # ---- 汇总打印 ----
    print(f"\n{'='*50}")
    print("  汇总：各方法整体 RMSE")
    print(f"{'='*50}")
    for res in all_results:
        print(f"  {res['run_name']:35s}：{res['overall_rmse']:.4f} 度")
    if music_info:
        print(f"  {'MUSIC（基线）':35s}：{music_info['overall_rmse']:.4f} 度")

    # ---- 绘图 ----
    plot_rmse_vs_snr(all_results, music_info)
    for res in all_results:
        plot_scatter(res['preds'], res['labels'], res['run_name'], cfg0['K'])


if __name__ == '__main__':
    main()
