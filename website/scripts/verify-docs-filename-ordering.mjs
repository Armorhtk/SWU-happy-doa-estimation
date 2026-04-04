import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..", "..");
const placeholderLine = "本节正在开发中，后续内容将按教程架构逐步补充。";

const expectedDirectories = [
  path.join(repoRoot, "docs", "01-doa-intro"),
  path.join(repoRoot, "docs", "02-traditional-methods"),
  path.join(repoRoot, "docs", "03-deep-learning-methods"),
  path.join(repoRoot, "docs", "04-research-practice"),
  path.join(repoRoot, "docs", "05-appendices"),
];

const expectedDocs = [
  {
    path: path.join(repoRoot, "docs", "01-preface.md"),
    id: "preface",
    title: "导读",
    slug: "/preface",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "01-array-observation-model-and-ula.md"),
    id: "doa-intro-array-observation-model-and-ula",
    title: "1.1 阵列观测模型与均匀线阵",
    slug: "/doa-intro/array-observation-model-and-ula",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "02-narrowband-far-field-model-and-steering-vector.md"),
    id: "doa-intro-narrowband-far-field-model-and-steering-vector",
    title: "1.2 远场窄带信号模型与导向矢量",
    slug: "/doa-intro/narrowband-far-field-model-and-steering-vector",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "03-covariance-beamforming-and-spatial-spectrum.md"),
    id: "doa-intro-covariance-beamforming-and-spatial-spectrum",
    title: "1.3 协方差矩阵、常规波束形成与空间谱估计",
    slug: "/doa-intro/covariance-beamforming-and-spatial-spectrum",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "04-resolution-and-cramer-rao-bound.md"),
    id: "doa-intro-resolution-and-cramer-rao-bound",
    title: "1.4 分辨率问题与克拉美—罗下界",
    slug: "/doa-intro/resolution-and-cramer-rao-bound",
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "01-overview.md"),
    id: "traditional-methods-overview",
    title: "第二章 经典DOA估计算法",
    slug: "/traditional-methods/overview",
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "02-subspace-decomposition.md"),
    id: "traditional-eigendecomposition-and-subspace-basics",
    title: "2.1 特征值分解与子空间基本思想",
    slug: "/traditional-methods/eigendecomposition-and-subspace-basics",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "03-model-order-selection.md"),
    id: "traditional-source-number-estimation-and-model-order-selection",
    title: "2.2 信源数估计与模型阶数选择",
    slug: "/traditional-methods/source-number-estimation-and-model-order-selection",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "04-music.md"),
    id: "traditional-music",
    title: "2.3 MUSIC算法原理与实现",
    slug: "/traditional-methods/music",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "05-esprit.md"),
    id: "traditional-esprit",
    title: "2.4 ESPRIT算法原理与实现",
    slug: "/traditional-methods/esprit",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "06-coherent-sources-and-spatial-smoothing.md"),
    id: "traditional-coherent-sources-and-spatial-smoothing",
    title: "2.5 相干信号问题及空间平滑处理",
    slug: "/traditional-methods/coherent-sources-and-spatial-smoothing",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "07-performance-metrics-and-experiments.md"),
    id: "traditional-performance-metrics-and-experiments",
    title: "2.6 DOA估计性能评价指标与算法实验分析",
    slug: "/traditional-methods/performance-metrics-and-experiments",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "01-overview.md"),
    id: "deep-learning-overview",
    title: "第三章 数据驱动DOA估计算法",
    slug: "/deep-learning/overview",
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "02-basic-tasks-and-workflow.md"),
    id: "deep-learning-basic-tasks-and-workflow",
    title: "3.1 深度学习DOA估计的基本任务与实现流程",
    slug: "/deep-learning/basic-tasks-and-workflow",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "03-dataset-construction-and-input-features.md"),
    id: "deep-learning-dataset-construction-and-input-features",
    title: "3.2 数据集构建与输入特征表示",
    slug: "/deep-learning/dataset-construction-and-input-features",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "04-classification-based-methods.md"),
    id: "deep-learning-classification-based-methods",
    title: "3.3 基于分类的DOA估计方法",
    slug: "/deep-learning/classification-based-methods",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "05-regression-based-methods.md"),
    id: "deep-learning-regression-based-methods",
    title: "3.4 基于回归的DOA估计方法",
    slug: "/deep-learning/regression-based-methods",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "06-comparison-with-classical-methods.md"),
    id: "deep-learning-comparison-with-classical-methods",
    title: "3.5 深度学习方法与经典方法对比",
    slug: "/deep-learning/comparison-with-classical-methods",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "01-overview.md"),
    id: "research-practice-overview",
    title: "第四章 论文复现和工程实践",
    slug: "/research-practice/overview",
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "02-trans-paper-reproduction.md"),
    id: "research-practice-trans-paper-reproduction",
    title: "4.1 深度学习DOA估计Trans论文复现",
    slug: "/research-practice/trans-paper-reproduction",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "03-fmcw-mmwave-signal-processing-pipeline.md"),
    id: "research-practice-fmcw-mmwave-signal-processing-pipeline",
    title: "4.2 FMCW毫米波雷达信号处理基本流程",
    slug: "/research-practice/fmcw-mmwave-signal-processing-pipeline",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "04-automotive-mmwave-doa-validation.md"),
    id: "research-practice-automotive-mmwave-doa-validation",
    title: "4.3 车载毫米波雷达DOA估计实测验证",
    slug: "/research-practice/automotive-mmwave-doa-validation",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "05-appendices", "01-math-foundations.md"),
    id: "appendices-math-foundations",
    title: "附录A 数学基础要点",
    slug: "/appendices/math-foundations",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "05-appendices", "02-faq-and-debugging.md"),
    id: "appendices-faq-and-debugging",
    title: "附录B 常见问题与调试指南",
    slug: "/appendices/faq-and-debugging",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "05-appendices", "03-references-and-open-source.md"),
    id: "appendices-references-and-open-source",
    title: "附录C 参考资料与开源代码",
    slug: "/appendices/references-and-open-source",
    placeholder: true,
  },
];

const forbiddenPaths = [
  path.join(repoRoot, "docs", "02-course-roadmap.md"),
  path.join(repoRoot, "docs", "98-faq.md"),
  path.join(repoRoot, "docs", "99-about.md"),
  path.join(repoRoot, "docs", "doa-intro"),
  path.join(repoRoot, "docs", "traditional-methods"),
  path.join(repoRoot, "docs", "deep-learning-methods"),
  path.join(repoRoot, "docs", "research-practice"),
  path.join(repoRoot, "docs", "01-doa-intro", "01-overview.md"),
  path.join(repoRoot, "docs", "01-doa-intro", "02-quickstart.md"),
  path.join(repoRoot, "docs", "01-doa-intro", "03-array-basics.md"),
  path.join(repoRoot, "docs", "01-doa-intro", "04-snapshots-covariance.md"),
  path.join(repoRoot, "docs", "01-doa-intro", "05-first-experiment.md"),
  path.join(repoRoot, "docs", "02-traditional-methods", "03-adaptive-beamforming.md"),
  path.join(repoRoot, "docs", "02-traditional-methods", "04-music-and-esprit.md"),
  path.join(repoRoot, "docs", "02-traditional-methods", "05-spatial-smoothing-and-root-music.md"),
  path.join(repoRoot, "docs", "02-traditional-methods", "06-model-order-selection.md"),
  path.join(repoRoot, "docs", "02-traditional-methods", "07-cramer-rao-bound.md"),
  path.join(repoRoot, "docs", "03-deep-learning-methods", "02-data-processing-and-feature-engineering.md"),
  path.join(repoRoot, "docs", "03-deep-learning-methods", "03-learning-paradigms.md"),
  path.join(repoRoot, "docs", "03-deep-learning-methods", "04-training-and-generalization.md"),
  path.join(repoRoot, "docs", "04-research-practice", "02-paper-reproduction.md"),
  path.join(repoRoot, "docs", "04-research-practice", "03-automotive-mmwave-practice.md"),
];

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

for (const directory of expectedDirectories) {
  assert(fs.existsSync(directory), `Expected ordered docs directory to exist: ${directory}`);
}

for (const doc of expectedDocs) {
  assert(fs.existsSync(doc.path), `Expected ordered doc file to exist: ${doc.path}`);
  const content = fs.readFileSync(doc.path, "utf8");
  assert(content.includes(`id: ${doc.id}`), `Expected id "${doc.id}" in ${doc.path}`);
  assert(content.includes(`title: ${doc.title}`), `Expected title "${doc.title}" in ${doc.path}`);
  assert(content.includes(`slug: ${doc.slug}`), `Expected slug "${doc.slug}" in ${doc.path}`);
  if (doc.placeholder) {
    assert(
      content.includes(placeholderLine),
      `Expected placeholder copy in ${doc.path}.`,
    );
  }
}

for (const forbiddenPath of forbiddenPaths) {
  assert(!fs.existsSync(forbiddenPath), `Legacy path should not remain: ${forbiddenPath}`);
}

console.log("Docs filename ordering wiring looks correct.");
