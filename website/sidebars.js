module.exports = {
  tutorialSidebar: [
    "course-roadmap",
    "preface",
    {
      type: "category",
      label: "DOA 入门",
      items: [
        "doa-intro/doa-intro-overview",
        "doa-intro/doa-intro-setup",
        "doa-intro/doa-array-basics",
        "doa-intro/doa-first-experiment",
      ],
    },
    {
      type: "category",
      label: "传统方法",
      items: [
        "traditional-methods/traditional-methods-overview",
        "traditional-methods/traditional-music",
      ],
    },
    {
      type: "category",
      label: "深度学习方法",
      items: [
        "deep-learning-methods/deep-learning-overview",
        "deep-learning-methods/deep-learning-pytorch-baseline",
      ],
    },
    "faq",
    "about",
  ],
};
