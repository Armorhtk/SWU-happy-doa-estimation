---
id: doa-intro-setup
title: 环境准备与快速开始
slug: /doa-intro/setup
---

# 环境准备与快速开始

这页的目标很明确：让你在本地机器上尽快跑通第一份 DOA 入门代码。

## 你需要什么

- Windows、macOS 或 Linux
- Python 3.10+
- 能安装 `numpy` 和 `matplotlib`

如果你已经有 `rfgen` conda 环境，可以直接复用。

## 安装依赖

### 方式 A：使用现成的 conda 环境

```powershell
conda activate rfgen
pip install -r requirements.txt
```

### 方式 B：新建虚拟环境

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行第一份实验

```powershell
python examples/doa_intro_array_scan.py
```

如果一切正常，你会看到类似下面的输出：

```text
Saved figure to: .../artifacts/doa_intro_array_scan.png
Try changing --angle, --num-sensors, or --spacing-scale and compare the curves.
```
