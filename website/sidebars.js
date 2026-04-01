module.exports = {
  tutorialSidebar: [
    {
      type: "doc",
      id: "preface",
      label: "教程导览",
    },
    {
      type: "category",
      label: "第一章 数学模型与波束形成",
      collapsed: false,
      items: [
        "doa-intro/foundations-overview",
        "doa-intro/foundations-narrowband-far-field-model",
        "doa-intro/foundations-ula-and-steering-vector",
        "doa-intro/foundations-snapshots-and-covariance",
        "doa-intro/foundations-conventional-beamforming",
      ],
    },
    {
      type: "category",
      label: "第二章 经典 DOA 估计算法",
      collapsed: false,
      link: {
        type: "doc",
        id: "traditional-methods/traditional-methods-overview",
      },
      items: [
        "traditional-methods/traditional-subspace-decomposition",
        "traditional-methods/traditional-adaptive-beamforming",
        "traditional-methods/traditional-music-and-esprit",
        "traditional-methods/traditional-spatial-smoothing-and-root-music",
        "traditional-methods/traditional-model-order-selection",
        "traditional-methods/traditional-cramer-rao-bound",
      ],
    },
    {
      type: "category",
      label: "第三章 深度学习 DOA 估计",
      collapsed: false,
      link: {
        type: "doc",
        id: "deep-learning-methods/deep-learning-overview",
      },
      items: [
        "deep-learning-methods/deep-learning-data-processing-and-feature-engineering",
        "deep-learning-methods/deep-learning-learning-paradigms",
        "deep-learning-methods/deep-learning-training-and-generalization",
      ],
    },
    {
      type: "category",
      label: "第四章 论文复现与毫米波实战",
      collapsed: false,
      link: {
        type: "doc",
        id: "research-practice/research-practice-overview",
      },
      items: [
        "research-practice/research-practice-paper-reproduction",
        "research-practice/research-practice-automotive-mmwave-practice",
      ],
    },
    "faq",
    "about",
  ],
};
