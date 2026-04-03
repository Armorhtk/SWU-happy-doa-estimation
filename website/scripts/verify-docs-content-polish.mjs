import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const repoRoot = resolve(process.cwd());
const cssSource = readFileSync(resolve(repoRoot, "website", "src", "css", "custom.css"), "utf8");

for (const marker of [
  "--docs-content-max-width",
  ".docs-wrapper .theme-doc-markdown",
  ".docs-wrapper .theme-doc-markdown > h2",
  ".docs-wrapper .theme-doc-markdown > h3",
  ".docs-wrapper .theme-doc-markdown > p",
  ".docs-wrapper .theme-doc-markdown > p:first-of-type",
  ".docs-wrapper .theme-doc-markdown blockquote",
  ".docs-wrapper .theme-doc-markdown .admonition",
  ".docs-wrapper .theme-doc-markdown ul",
  ".docs-wrapper .theme-doc-markdown table",
  ".docs-wrapper .theme-doc-markdown img",
  ".docs-wrapper .theme-doc-markdown p:has(> img) + p > em:only-child",
  ".docs-wrapper .theme-doc-markdown hr",
  ".docs-wrapper .theme-doc-markdown code",
  ".docs-wrapper .theme-doc-markdown pre",
]) {
  assert(cssSource.includes(marker), `Expected docs content polish styles to include ${marker}.`);
}

console.log("Docs content polish wiring verified.");
