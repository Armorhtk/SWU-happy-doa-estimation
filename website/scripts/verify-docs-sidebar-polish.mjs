import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const repoRoot = resolve(process.cwd());
const configSource = readFileSync(resolve(repoRoot, "website", "docusaurus.config.js"), "utf8");
const cssSource = readFileSync(resolve(repoRoot, "website", "src", "css", "custom.css"), "utf8");
const sidebarSource = readFileSync(resolve(repoRoot, "website", "sidebars.js"), "utf8");
const normalizedSidebarSource = sidebarSource.replace(/\r\n/g, "\n");

assert(
  configSource.includes("hideable: true"),
  "Expected docs sidebar hideable mode to be enabled in docusaurus.config.js.",
);

for (const marker of [
  ".docs-wrapper",
  "--ifm-background-color: #ffffff",
  ".theme-doc-sidebar-item-link-level-1 > .menu__link",
  ".theme-doc-sidebar-item-category-level-1 > .menu__list-item-collapsible > .menu__link",
  ".theme-doc-sidebar-container .button.button--secondary.button--outline",
  'html[data-theme="dark"].docs-wrapper',
]) {
  assert(cssSource.includes(marker), `Expected docs sidebar polish styles to include ${marker}.`);
}

assert(
  !cssSource.includes('[data-theme="dark"] .docs-wrapper {'),
  "Expected docs dark-mode styles to avoid the broken descendant selector for .docs-wrapper.",
);

for (const chapterLink of [
  'label: "第二章 经典 DOA 估计算法"',
  'id: "traditional-methods/traditional-methods-overview"',
  'label: "第三章 深度学习 DOA 估计"',
  'id: "deep-learning-methods/deep-learning-overview"',
  'label: "第四章 论文复现与毫米波实战"',
  'id: "research-practice/research-practice-overview"',
]) {
  assert(
    sidebarSource.includes(chapterLink),
    `Expected sidebar categories to link directly to overview docs via ${chapterLink}.`,
  );
}

for (const duplicatedOverviewItem of [
  'items: [\n        "traditional-methods/traditional-methods-overview",',
  'items: [\n        "deep-learning-methods/deep-learning-overview",',
  'items: [\n        "research-practice/research-practice-overview",',
]) {
  assert(
    !normalizedSidebarSource.includes(duplicatedOverviewItem),
    `Expected sidebar category items to omit duplicated overview entry ${duplicatedOverviewItem}.`,
  );
}

console.log("Docs sidebar polish wiring verified.");
