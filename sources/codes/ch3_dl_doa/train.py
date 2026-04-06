"""
train.py — 训练主脚本
======================
用法：直接运行，在脚本顶部的 CONFIG 字典里修改超参数。

流程：
  1. 按配置生成训练/验证数据
  2. 提取特征，构造 DOADataset 和 DataLoader
  3. 实例化模型、损失函数、优化器、学习率调度器
  4. 训练循环（含早停）
  5. 保存最优检查点到 checkpoints/<run_name>.pth
  6. 绘制并保存训练曲线

调参记录建议：
  修改 CONFIG 中的 run_name 字段标记本次实验，
  配合 eval.py 对比多组实验的测试集 RMSE。
"""

import os
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import matplotlib.pyplot as plt

from utils import generate_dataset, build_features, DOADataset
from models import build_model

# ================================================================
# CONFIG：所有超参数集中在这里，按需修改
# ================================================================
CONFIG = {
    # --- 实验标识 ---
    "run_name": "exp01_cm_cnn_cls",  # 检查点文件名前缀，每次实验改一下

    # --- 阵列与信号参数 ---
    "M"        : 8,       # 阵元数
    "K"        : 2,       # 信源数
    "N_snap"   : 256,     # 快拍数
    "d"        : 0.5,     # 阵元间距（归一化波长）
    "theta_min": -60.0,   # 角度范围下限（度）
    "theta_max":  60.0,   # 角度范围上限（度）
    "min_sep"  :  5.0,    # 多信源最小角度间隔（度）
    "snr_range": (-5, 20),# 训练集 SNR 范围（dB）

    # --- 数据集规模 ---
    "num_train": 12000,   # 训练样本总数（含验证集）
    "val_ratio":  0.15,   # 验证集比例

    # --- 输入特征与任务 ---
    # feature_type : 'cm'（协方差矩阵，配合 cm_cnn）
    #                'iq'（原始 IQ 序列，配合 iq_lstm）
    "feature_type": "cm",
    # task         : 'classification'（多标签分类）
    #                'regression'（直接角度回归）
    "task"        : "classification",
    "resolution"  : 1.0,  # 分类任务格点分辨率（度），回归任务忽略

    # --- 模型选择 ---
    # model_name : 'cm_cnn'（分类）或 'iq_lstm'（回归）
    "model_name"   : "cm_cnn",
    "base_channels": 32,   # cm_cnn 参数：卷积通道数
    "hidden_size"  : 128,  # iq_lstm 参数：LSTM 隐层维度
    "num_layers"   : 2,    # iq_lstm 参数：LSTM 层数
    "dropout"      : 0.3,

    # --- 训练超参数 ---
    "batch_size"  : 64,
    "lr"          : 1e-3,
    "num_epochs"  : 40,
    "lr_step"     : 10,    # StepLR：每隔 lr_step 个 epoch，lr × lr_gamma
    "lr_gamma"    : 0.5,
    "patience"    : 10,    # 早停：验证损失连续 patience 个 epoch 不改善则停止

    # --- 路径 ---
    "ckpt_dir": "checkpoints",
    "seed"     : 42,
}

# ================================================================
# 工具函数
# ================================================================

def get_criterion(task):
    if task == 'classification':
        return nn.BCEWithLogitsLoss()
    elif task == 'regression':
        return nn.MSELoss()
    else:
        raise ValueError(f"未知 task: {task}")


def run_one_epoch(model, loader, criterion, optimizer, device, is_train):
    model.train() if is_train else model.eval()
    total_loss = 0.0
    ctx = torch.enable_grad() if is_train else torch.no_grad()
    with ctx:
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if is_train:
                optimizer.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            if is_train:
                loss.backward()
                # LSTM 需要梯度裁剪防止梯度爆炸
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
                optimizer.step()
            total_loss += loss.item() * len(x)
    return total_loss / len(loader.dataset)


def plot_training_curve(train_losses, val_losses, run_name, save=True):
    fig, ax = plt.subplots(figsize=(7, 4))
    epochs = range(1, len(train_losses) + 1)
    ax.plot(epochs, train_losses, label='训练损失')
    ax.plot(epochs, val_losses,   label='验证损失')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title(f'训练曲线（{run_name}）')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    if save:
        fname = f"{run_name}_curve.png"
        plt.savefig(fname, dpi=150)
        print(f"  训练曲线已保存：{fname}")
    plt.show()

# ================================================================
# 主训练函数
# ================================================================

def train(cfg):
    torch.manual_seed(cfg['seed'])
    np.random.seed(cfg['seed'])
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n{'='*55}")
    print(f"  实验：{cfg['run_name']}")
    print(f"  模型：{cfg['model_name']}，任务：{cfg['task']}，特征：{cfg['feature_type']}")
    print(f"  设备：{device}")
    print(f"{'='*55}")

    # ---- 1. 生成数据 ----
    print("\n[1/4] 生成仿真数据集...")
    t0 = time.time()
    X_raw, labels_deg, snrs = generate_dataset(
        num_samples   = cfg['num_train'],
        K             = cfg['K'],
        M             = cfg['M'],
        N             = cfg['N_snap'],
        snr_range_dB  = cfg['snr_range'],
        theta_min     = cfg['theta_min'],
        theta_max     = cfg['theta_max'],
        min_sep       = cfg['min_sep'],
        d             = cfg['d'],
        seed          = cfg['seed'],
    )
    print(f"  生成 {cfg['num_train']} 个样本，耗时 {time.time()-t0:.1f}s")
    print(f"  SNR 范围：{snrs.min():.1f} ~ {snrs.max():.1f} dB")

    # ---- 2. 特征提取与 Dataset ----
    print(f"\n[2/4] 提取 {cfg['feature_type'].upper()} 特征...")
    t0 = time.time()
    features = build_features(X_raw, feature_type=cfg['feature_type'])
    print(f"  特征形状：{features.shape}，耗时 {time.time()-t0:.1f}s")

    full_ds = DOADataset(
        features    = features,
        labels_deg  = labels_deg,
        task        = cfg['task'],
        theta_min   = cfg['theta_min'],
        theta_max   = cfg['theta_max'],
        resolution  = cfg['resolution'],
    )
    n_val   = int(cfg['val_ratio'] * len(full_ds))
    n_train = len(full_ds) - n_val
    train_ds, val_ds = random_split(
        full_ds, [n_train, n_val],
        generator=torch.Generator().manual_seed(cfg['seed']))

    train_loader = DataLoader(train_ds, batch_size=cfg['batch_size'],
                              shuffle=True,  num_workers=0, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=cfg['batch_size'] * 2,
                              shuffle=False, num_workers=0, pin_memory=True)
    print(f"  训练集 {n_train} 样本，验证集 {n_val} 样本")

    # ---- 3. 实例化模型 ----
    print(f"\n[3/4] 实例化 {cfg['model_name']} 网络...")
    if cfg['model_name'] == 'cm_cnn':
        if cfg['task'] == 'classification':
            # D = 格点总数
            resolution = cfg['resolution']
            D = int((cfg['theta_max'] - cfg['theta_min']) / resolution) + 1
            model = build_model('cm_cnn', M=cfg['M'], D=D,
                                base_channels=cfg['base_channels'],
                                dropout=cfg['dropout'])
        else:
            raise ValueError("cm_cnn 对应 task='classification'")
    elif cfg['model_name'] == 'iq_lstm':
        if cfg['task'] == 'regression':
            model = build_model('iq_lstm',
                                input_size  = 2 * cfg['M'],
                                K           = cfg['K'],
                                hidden_size = cfg['hidden_size'],
                                num_layers  = cfg['num_layers'],
                                dropout     = cfg['dropout'])
        else:
            raise ValueError("iq_lstm 对应 task='regression'")
    else:
        raise ValueError(f"未知 model_name: {cfg['model_name']}")

    model     = model.to(device)
    criterion = get_criterion(cfg['task'])
    optimizer = optim.Adam(model.parameters(), lr=cfg['lr'])
    scheduler = optim.lr_scheduler.StepLR(
        optimizer, step_size=cfg['lr_step'], gamma=cfg['lr_gamma'])

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  可训练参数数量：{n_params:,}")

    # ---- 4. 训练循环（含早停） ----
    print(f"\n[4/4] 开始训练（最多 {cfg['num_epochs']} epochs，早停 patience={cfg['patience']}）...")
    os.makedirs(cfg['ckpt_dir'], exist_ok=True)
    ckpt_path = os.path.join(cfg['ckpt_dir'], f"{cfg['run_name']}.pth")

    best_val   = float('inf')
    no_improve = 0
    train_losses, val_losses = [], []

    for epoch in range(1, cfg['num_epochs'] + 1):
        tr_loss  = run_one_epoch(model, train_loader, criterion, optimizer, device, True)
        val_loss = run_one_epoch(model, val_loader,   criterion, optimizer, device, False)
        scheduler.step()

        train_losses.append(tr_loss)
        val_losses.append(val_loss)

        improved = val_loss < best_val
        if improved:
            best_val   = val_loss
            no_improve = 0
            torch.save({
                'epoch'      : epoch,
                'model_state': model.state_dict(),
                'val_loss'   : best_val,
                'config'     : cfg,
            }, ckpt_path)
        else:
            no_improve += 1

        marker = " ✓" if improved else ""
        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{cfg['num_epochs']} | "
                  f"train={tr_loss:.5f}  val={val_loss:.5f}"
                  f"  lr={scheduler.get_last_lr()[0]:.2e}{marker}")

        if no_improve >= cfg['patience']:
            print(f"  早停触发：验证损失连续 {cfg['patience']} epoch 无改善")
            break

    print(f"\n  训练完成，最佳验证损失 = {best_val:.5f}")
    print(f"  检查点已保存至：{ckpt_path}")

    plot_training_curve(train_losses, val_losses, cfg['run_name'])
    return ckpt_path


# ================================================================
# 入口：直接运行 train.py 时执行
# ================================================================
if __name__ == '__main__':
    train(CONFIG)

    # ----------------------------------------------------------------
    # 想训练另一组配置？复制 CONFIG，改 run_name 和参数后再 train()
    # 例如：切换到 IQ-LSTM 回归
    # ----------------------------------------------------------------
    # CONFIG_LSTM = {
    #     **CONFIG,
    #     "run_name"    : "exp02_iq_lstm_reg",
    #     "N_snap"      : 128,
    #     "feature_type": "iq",
    #     "task"        : "regression",
    #     "model_name"  : "iq_lstm",
    #     "hidden_size" : 128,
    #     "num_layers"  : 2,
    # }
    # train(CONFIG_LSTM)
