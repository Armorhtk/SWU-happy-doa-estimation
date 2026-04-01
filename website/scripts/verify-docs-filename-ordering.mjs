import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..", "..");
const placeholderLine = "本节正在开发中，后续内容将按教程架构逐步补充。";

const expectedDirectories = [
  path.join(repoRoot, "docs", "01-doa-intro"),
  path.join(repoRoot, "docs", "02-traditional-methods"),
  path.join(repoRoot, "docs", "03-deep-learning-methods"),
  path.join(repoRoot, "docs", "04-research-practice"),
];

const expectedDocs = [
  {
    path: path.join(repoRoot, "docs", "01-preface.md"),
    id: "preface",
    title: "教程导览",
    slug: "/preface",
  },
  {
    path: path.join(repoRoot, "docs", "02-course-roadmap.md"),
    id: "course-roadmap",
    title: "课程路线",
    slug: "/course-roadmap",
  },
  {
    path: path.join(repoRoot, "docs", "98-faq.md"),
    id: "faq",
    title: "FAQ",
    slug: "/faq",
  },
  {
    path: path.join(repoRoot, "docs", "99-about.md"),
    id: "about",
    title: "关于项目",
    slug: "/about",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "01-overview.md"),
    id: "foundations-overview",
    title: "1.1 概览",
    slug: "/foundations/overview",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "02-quickstart.md"),
    id: "foundations-narrowband-far-field-model",
    title: "1.2 窄带远场阵列信号模型",
    slug: "/foundations/narrowband-far-field-model",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "03-array-basics.md"),
    id: "foundations-ula-and-steering-vector",
    title: "1.3 均匀直线阵几何与导向矢量",
    slug: "/foundations/ula-and-steering-vector",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "04-snapshots-covariance.md"),
    id: "foundations-snapshots-and-covariance",
    title: "1.4 快拍、协方差矩阵与数据表示",
    slug: "/foundations/snapshots-and-covariance",
  },
  {
    path: path.join(repoRoot, "docs", "01-doa-intro", "05-first-experiment.md"),
    id: "foundations-conventional-beamforming",
    title: "1.5 常规波束形成与第一张空间谱",
    slug: "/foundations/conventional-beamforming",
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "01-overview.md"),
    id: "traditional-methods-overview",
    title: "第二章 经典 DOA 估计算法",
    slug: "/traditional-methods/overview",
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "02-subspace-decomposition.md"),
    id: "traditional-subspace-decomposition",
    title: "2.1 信号与噪声子空间分解理论",
    slug: "/traditional-methods/subspace-decomposition",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "03-adaptive-beamforming.md"),
    id: "traditional-adaptive-beamforming",
    title: "2.2 自适应波束形成（Capon / MVDR）",
    slug: "/traditional-methods/adaptive-beamforming",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "04-music-and-esprit.md"),
    id: "traditional-music-and-esprit",
    title: "2.3 MUSIC 与 ESPRIT",
    slug: "/traditional-methods/music-and-esprit",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "05-spatial-smoothing-and-root-music.md"),
    id: "traditional-spatial-smoothing-and-root-music",
    title: "2.4 空间平滑与 Root-MUSIC",
    slug: "/traditional-methods/spatial-smoothing-and-root-music",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "06-model-order-selection.md"),
    id: "traditional-model-order-selection",
    title: "2.5 信源数估计准则（AIC / MDL）",
    slug: "/traditional-methods/model-order-selection",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "02-traditional-methods", "07-cramer-rao-bound.md"),
    id: "traditional-cramer-rao-bound",
    title: "2.6 Cramer-Rao 下界与统计性能标尺",
    slug: "/traditional-methods/cramer-rao-bound",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "01-overview.md"),
    id: "deep-learning-overview",
    title: "第三章 深度学习 DOA 估计",
    slug: "/deep-learning/overview",
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "02-data-processing-and-feature-engineering.md"),
    id: "deep-learning-data-processing-and-feature-engineering",
    title: "3.1 阵列信号数据处理与特征工程",
    slug: "/deep-learning/data-processing-and-feature-engineering",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "03-learning-paradigms.md"),
    id: "deep-learning-learning-paradigms",
    title: "3.2 监督学习与无监督学习的 DOA 估计范式",
    slug: "/deep-learning/learning-paradigms",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "03-deep-learning-methods", "04-training-and-generalization.md"),
    id: "deep-learning-training-and-generalization",
    title: "3.3 训练策略与模型泛化性能对比实验",
    slug: "/deep-learning/training-and-generalization",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "01-overview.md"),
    id: "research-practice-overview",
    title: "第四章 论文复现与毫米波实战",
    slug: "/research-practice/overview",
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "02-paper-reproduction.md"),
    id: "research-practice-paper-reproduction",
    title: "4.1 经典 / SOTA 论文复现",
    slug: "/research-practice/paper-reproduction",
    placeholder: true,
  },
  {
    path: path.join(repoRoot, "docs", "04-research-practice", "03-automotive-mmwave-practice.md"),
    id: "research-practice-automotive-mmwave-practice",
    title: "4.2 自动驾驶毫米波雷达 DOA 估计实战",
    slug: "/research-practice/automotive-mmwave-practice",
    placeholder: true,
  },
];

const forbiddenPaths = [
  path.join(repoRoot, "docs", "doa-intro"),
  path.join(repoRoot, "docs", "traditional-methods"),
  path.join(repoRoot, "docs", "deep-learning-methods"),
  path.join(repoRoot, "docs", "research-practice"),
  path.join(repoRoot, "docs", "02-traditional-methods", "02-music.md"),
  path.join(repoRoot, "docs", "03-deep-learning-methods", "02-pytorch-baseline.md"),
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
