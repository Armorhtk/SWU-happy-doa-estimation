# SWU-happy-doa-estimation

当前为早期公开版本，课程内容将持续补充完善。

测试网站：https://armorhtk.github.io/SWU-happy-doa-estimation/

# 目录

- [导读](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/preface)
- [第一章 DOA估计入门](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/doa-intro/array-observation-model-and-ula)
  - [1.1 阵列观测模型与均匀线阵](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/doa-intro/array-observation-model-and-ula)
  - [1.2 远场窄带信号模型与导向矢量](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/doa-intro/narrowband-far-field-model-and-steering-vector)
  - [1.3 协方差矩阵、常规波束形成与空间谱估计](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/doa-intro/covariance-beamforming-and-spatial-spectrum)
  - [1.4 分辨率问题与克拉美—罗下界](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/doa-intro/resolution-and-cramer-rao-bound)
- [第二章 经典DOA估计算法](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/eigendecomposition-and-subspace-basics)
  - [2.1 特征值分解与子空间基本思想](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/eigendecomposition-and-subspace-basics)
  - [2.2 信源数估计与模型阶数选择](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/source-number-estimation-and-model-order-selection)
  - [2.3 MUSIC算法原理与实现](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/music)
  - [2.4 ESPRIT算法原理与实现](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/esprit)
  - [2.5 相干信号问题及空间平滑处理](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/coherent-sources-and-spatial-smoothing)
  - [2.6 自适应波束形成：Capon/MVDR 算法原理与实现](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/adaptive-beamforming-capon-mvdr)
  - [2.7 DOA估计性能评价指标与算法实验分析](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/traditional-methods/performance-metrics-and-experiments)
- [第三章 基于深度学习的DOA估计](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/foundations-quick-tour)
  - [3.0 【补充】深度学习相关基础速览](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/foundations-quick-tour)
  - [3.1 为什么需要深度学习进行DOA估计](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/why-deep-learning-for-doa)
  - [3.2 深度学习DOA估计的基本任务形式](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/basic-task-formulations)
  - [3.3 如何构建DOA数据集](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/how-to-build-doa-dataset)
  - [3.4 基于分类的DOA估计方法](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/classification-based-methods)
  - [3.5 基于回归的DOA估计方法（一）：直接角度回归](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/direct-angle-regression)
  - [3.6 基于回归的DOA估计方法（二）：伪空间谱回归](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/pseudo-spatial-spectrum-regression)
  - [3.7 深度学习DOA估计代码框架实现](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/code-framework-implementation)
  - [3.8 深度学习方法与经典方法的对比与选型](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/comparison-and-selection-with-classical-methods)
  - [3.9 【拓展】深度展开网络与数据-模型混合驱动范式](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/deep-learning/deep-unfolding-and-hybrid-paradigms)
- [第四章 论文复现和工程实践](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/trans-paper-reproduction)
  - [4.1 深度学习DOA估计Trans论文复现](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/trans-paper-reproduction)
  - [4.2 FMCW毫米波雷达信号处理基本流程](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/fmcw-mmwave-signal-processing-pipeline)
  - [4.3 车载毫米波雷达DOA估计实测验证](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/automotive-mmwave-doa-validation)
  - [4.4 【拓展】深度学习DOA估计中的Sim2Real问题](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/sim2real-in-deep-learning-doa)
  - [4.5 【拓展】无监督DOA估计方法](https://armorhtk.github.io/SWU-happy-doa-estimation/docs/research-practice/unsupervised-doa-methods)
