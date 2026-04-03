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
      link: {
        type: "doc",
        id: "traditional-methods/traditional-methods-overview",
      },
      items: [
        "traditional-methods/traditional-eigendecomposition-and-subspace-basics",
        "traditional-methods/traditional-source-number-estimation-and-model-order-selection",
        "traditional-methods/traditional-music",
        "traditional-methods/traditional-esprit",
        "traditional-methods/traditional-coherent-sources-and-spatial-smoothing",
        "traditional-methods/traditional-performance-metrics-and-experiments",
      ],
    },
    {
      type: "category",
      label: "第三章 数据驱动DOA估计算法",
      collapsed: true,
      link: {
        type: "doc",
        id: "deep-learning-methods/deep-learning-overview",
      },
      items: [
        "deep-learning-methods/deep-learning-basic-tasks-and-workflow",
        "deep-learning-methods/deep-learning-dataset-construction-and-input-features",
        "deep-learning-methods/deep-learning-classification-based-methods",
        "deep-learning-methods/deep-learning-regression-based-methods",
        "deep-learning-methods/deep-learning-comparison-with-classical-methods",
      ],
    },
    {
      type: "category",
      label: "第四章 论文复现和工程实践",
      collapsed: true,
      link: {
        type: "doc",
        id: "research-practice/research-practice-overview",
      },
      items: [
        "research-practice/research-practice-trans-paper-reproduction",
        "research-practice/research-practice-fmcw-mmwave-signal-processing-pipeline",
        "research-practice/research-practice-automotive-mmwave-doa-validation",
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
