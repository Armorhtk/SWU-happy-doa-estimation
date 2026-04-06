"""
models.py — 网络结构定义
=========================
本模块定义两种网络结构，均可从 train.py 直接调用：

  CM_CNN_Classifier   : 协方差矩阵输入 → CNN → 多标签分类（BCEWithLogits）
  IQ_LSTM_Regressor   : 原始 IQ 序列输入 → LSTM → 直接角度回归（MSE）

两个网络遵循相同的设计约定：
  - forward() 的输入/输出形状在 docstring 中明确标注
  - 不在 forward() 内部施加与损失函数重复的激活（如不加 Sigmoid/Softmax）
  - 输出升序排列（回归任务处理配对歧义）
"""

import torch
import torch.nn as nn


# ================================================================
# 示例一：CM-CNN 多标签分类网络
# ================================================================

class CM_CNN_Classifier(nn.Module):
    """
    基于协方差矩阵（CM）的 CNN 分类网络

    输入  : (B, 2, M, M)  —— 实部/虚部双通道
    输出  : (B, D)         —— D 个角度格点的 logit（未经激活）
            配合 BCEWithLogitsLoss 使用；推理时对输出做 Sigmoid

    网络结构：
      [Conv-BN-ReLU × 2 + MaxPool] × 2  →  AdaptiveAvgPool(2×2)
      →  Flatten  →  FC-ReLU-Dropout  →  FC(D)
    """
    def __init__(self, M: int, D: int, base_channels: int = 32, dropout: float = 0.3):
        """
        M             : 阵元数（决定输入空间尺寸）
        D             : 角度格点总数（输出维度）
        base_channels : 第一卷积块的输出通道数，第二块为 2 倍
        dropout       : 全连接层 Dropout 比例
        """
        super().__init__()
        c1, c2 = base_channels, base_channels * 2

        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(2, c1, kernel_size=3, padding=1),
            nn.BatchNorm2d(c1),
            nn.ReLU(inplace=True),
            nn.Conv2d(c1, c1, kernel_size=3, padding=1),
            nn.BatchNorm2d(c1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Block 2
            nn.Conv2d(c1, c2, kernel_size=3, padding=1),
            nn.BatchNorm2d(c2),
            nn.ReLU(inplace=True),
            nn.Conv2d(c2, c2, kernel_size=3, padding=1),
            nn.BatchNorm2d(c2),
            nn.ReLU(inplace=True),
            # 自适应池化：与 M 无关，输出固定为 (c2, 2, 2)
            nn.AdaptiveAvgPool2d((2, 2)),
        )

        fc_in = c2 * 2 * 2
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(fc_in, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, D),
            # 不加 Sigmoid：BCEWithLogitsLoss 内部已包含
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, 2, M, M) → logit: (B, D)"""
        return self.classifier(self.features(x))


# ================================================================
# 示例二：IQ-LSTM 直接角度回归网络
# ================================================================

class IQ_LSTM_Regressor(nn.Module):
    """
    基于原始 IQ 序列的 LSTM 直接角度回归网络

    输入  : (B, N_snap, 2M)  —— 快拍序列，每步 2M 维
    输出  : (B, K)            —— K 个归一化角度，值域 (-1, 1)，升序排列
            推理后需调用 utils.denormalize_angles() 还原为真实角度

    网络结构：
      多层 LSTM（取最后时刻隐状态）→ FC-ReLU-Dropout → FC(K) → Tanh → sort
    """
    def __init__(self, input_size: int, K: int,
                 hidden_size: int = 128, num_layers: int = 2,
                 dropout: float = 0.3):
        """
        input_size  : LSTM 每步输入维度（= 2M）
        K           : 信源数（输出维度）
        hidden_size : LSTM 隐状态维度
        num_layers  : LSTM 层数
        dropout     : LSTM 层间 Dropout（仅 num_layers > 1 时生效）及回归头 Dropout
        """
        super().__init__()
        self.lstm = nn.LSTM(
            input_size  = input_size,
            hidden_size = hidden_size,
            num_layers  = num_layers,
            batch_first = True,
            dropout     = dropout if num_layers > 1 else 0.0,
        )
        self.regressor = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, K),
            nn.Tanh(),   # 输出限制在 (-1, 1)，与归一化标签对齐
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x      : (B, N_snap, 2M)
        output : (B, K)，升序（处理多信源配对歧义）
        """
        out, _ = self.lstm(x)          # (B, N_snap, hidden)
        last   = out[:, -1, :]         # 取最后时刻隐状态 (B, hidden)
        pred   = self.regressor(last)  # (B, K)
        pred, _ = torch.sort(pred, dim=1)  # 升序排列，可微操作
        return pred


# ================================================================
# 便捷工厂函数
# ================================================================

def build_model(model_name: str, **kwargs) -> nn.Module:
    """
    model_name : 'cm_cnn' 或 'iq_lstm'
    kwargs     : 传入对应构造函数的参数
    """
    if model_name == 'cm_cnn':
        return CM_CNN_Classifier(**kwargs)
    elif model_name == 'iq_lstm':
        return IQ_LSTM_Regressor(**kwargs)
    else:
        raise ValueError(f"未知 model_name: {model_name}，请选 'cm_cnn' 或 'iq_lstm'")
