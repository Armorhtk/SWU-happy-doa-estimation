---
id: quickstart
title: 快速开始
slug: /quickstart
---

# 快速开始

这页的目标很明确：让你在本地机器上尽快跑通第一份 DOA 入门代码。

## 1. 你需要什么

- Windows、macOS 或 Linux
- Python 3.10+
- 能安装 `numpy` 和 `matplotlib`

如果你已经有 `rfgen` conda 环境，可以直接复用。

## 2. 安装依赖

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

## 3. 运行第一份实验

```powershell
python examples/doa_intro_array_scan.py
```

如果一切正常，你会看到类似下面的输出：

```text
Saved figure to: .../artifacts/doa_intro_array_scan.png
Try changing --angle, --num-sensors, or --spacing-scale and compare the curves.
```

生成的图片会保存在 `artifacts/doa_intro_array_scan.png`。

## 4. 立刻改 3 个参数

先别急着背公式。请直接改这些参数，再观察曲线如何变化：

- `--angle 35`
- `--num-sensors 12`
- `--spacing-scale 0.75`

建议每次只改一个参数，这样你才能把现象和原因对应起来。

## 5. 常见问题

### `ModuleNotFoundError: No module named 'src'`

请在仓库根目录执行命令，而不是在 `examples/` 子目录里直接运行。

### 图像没有弹窗，只生成了文件

这是正常现象。示例默认把图保存到 `artifacts/`，你可以直接打开图片看结果。

### `pip` 安装失败

优先确认：

- 当前 Python 版本是否为 3.10+
- 虚拟环境是否已经激活
- 是否在仓库根目录执行 `pip install -r requirements.txt`
