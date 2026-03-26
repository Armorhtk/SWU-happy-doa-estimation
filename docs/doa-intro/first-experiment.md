---
id: doa-first-experiment
title: 第一组空间响应实验
slug: /doa-intro/first-experiment
---

# 第一组空间响应实验

## 运行步骤

```powershell
python examples/doa_intro_array_scan.py
```

也可以显式改参数：

```powershell
python examples/doa_intro_array_scan.py --angle 30 --num-sensors 12 --spacing-scale 0.5
```

## 建议观察

### 1. 改变真实角度

把 `--angle` 从 `20` 改到 `-25`。  
你应该看到主峰位置整体跟着移动。

### 2. 增加阵元数

把 `--num-sensors` 从 `8` 改到 `12` 或 `16`。  
你通常会看到主峰更尖，这意味着角度区分能力在增强。

### 3. 增大阵元间距

把 `--spacing-scale` 从 `0.5` 改到 `0.75` 甚至 `1.0`。  
你需要观察是否出现额外峰值，这就是后面学习传统方法时必须重视的阵列设计问题。

## 练习

1. 为什么单个天线通常无法直接估计来波方向？
2. 当 `--num-sensors` 增大时，扫描曲线为什么会变尖？
3. 为什么入门阶段推荐先使用 `lambda/2` 的阵元间距？

## 参考答案

1. 因为单个天线缺少空间采样维度，无法形成不同阵元之间的相位差比较。
2. 因为阵列孔径变大后，对不同角度的响应区分更明显，主瓣通常更窄。
3. 因为半波长间距更容易避免栅瓣，让初学者先建立稳定的空间响应直觉。
