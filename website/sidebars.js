module.exports = {
  tutorialSidebar: [
    {
      type: "doc",
      id: "preface",
      label: "导读",
    },
    {
      type: "category",
      label: "第一章 DOA估计入门",
      collapsed: true,
      items: [
        "doa-intro/doa-intro-array-observation-model-and-ula",
        "doa-intro/doa-intro-narrowband-far-field-model-and-steering-vector",
        "doa-intro/doa-intro-covariance-beamforming-and-spatial-spectrum",
        "doa-intro/doa-intro-resolution-and-cramer-rao-bound",
      ],
    },
    {
      type: "category",
      label: "第二章 经典DOA估计算法",
      collapsed: true,
      items: [
        "traditional-methods/traditional-eigendecomposition-and-subspace-basics",
        "traditional-methods/traditional-source-number-estimation-and-model-order-selection",
        "traditional-methods/traditional-music",
        "traditional-methods/traditional-esprit",
        "traditional-methods/traditional-coherent-sources-and-spatial-smoothing",
        "traditional-methods/traditional-adaptive-beamforming-capon-mvdr",
        "traditional-methods/traditional-performance-metrics-and-experiments",
      ],
    },
    {
      type: "category",
      label: "第三章 基于深度学习的DOA估计",
      collapsed: true,
      items: [
        "deep-learning-methods/deep-learning-foundations-quick-tour",
        "deep-learning-methods/deep-learning-why-deep-learning-for-doa",
        "deep-learning-methods/deep-learning-basic-task-formulations",
        "deep-learning-methods/deep-learning-how-to-build-doa-dataset",
        "deep-learning-methods/deep-learning-classification-based-methods",
        "deep-learning-methods/deep-learning-direct-angle-regression",
        "deep-learning-methods/deep-learning-pseudo-spatial-spectrum-regression",
        "deep-learning-methods/deep-learning-code-framework-implementation",
        "deep-learning-methods/deep-learning-comparison-and-selection-with-classical-methods",
        "deep-learning-methods/deep-learning-deep-unfolding-and-hybrid-paradigms",
      ],
    },
    {
      type: "category",
      label: "第四章 论文复现和工程实践",
      collapsed: true,
      items: [
        "research-practice/research-practice-trans-paper-reproduction",
        "research-practice/research-practice-fmcw-mmwave-signal-processing-pipeline",
        "research-practice/research-practice-automotive-mmwave-doa-validation",
        "research-practice/research-practice-sim2real-in-deep-learning-doa",
        "research-practice/research-practice-unsupervised-doa-methods",
      ],
    },
    {
      type: "category",
      label: "附录",
      collapsed: true,
      items: [
        "appendices/appendices-math-foundations",
        "appendices/appendices-faq-and-debugging",
        "appendices/appendices-references-and-open-source",
      ],
    },
  ],
};
