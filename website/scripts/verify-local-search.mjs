import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const websiteRoot = path.resolve(__dirname, "..");

const packagePath = path.join(websiteRoot, "package.json");
const configPath = path.join(websiteRoot, "docusaurus.config.js");
const navbarContentPath = path.join(
  websiteRoot,
  "src",
  "theme",
  "Navbar",
  "Content",
  "index.js",
);
const customCssPath = path.join(websiteRoot, "src", "css", "custom.css");

const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));
const configSource = fs.readFileSync(configPath, "utf8");
const navbarContentSource = fs.readFileSync(navbarContentPath, "utf8");
const customCssSource = fs.readFileSync(customCssPath, "utf8");

if (!packageJson.dependencies?.["@easyops-cn/docusaurus-search-local"]) {
  throw new Error("Missing @easyops-cn/docusaurus-search-local dependency");
}

if (!configSource.includes('"@easyops-cn/docusaurus-search-local"')) {
  throw new Error("Docusaurus local search theme is not registered");
}

if (!configSource.includes("indexDocs: true")) {
  throw new Error("Local search is not configured for docs indexing");
}

if (!configSource.includes("indexPages: false")) {
  throw new Error("Local search is still indexing pages");
}

if (!configSource.includes('docsDir: "../docs"')) {
  throw new Error("Local search docsDir is not aligned with the site's actual docs directory");
}

if (!configSource.includes("docsRouteBasePath: \"/docs\"")) {
  throw new Error("Local search docsRouteBasePath is not locked to /docs");
}

const logoIndex = navbarContentSource.indexOf("<NavbarLogo />");
const searchBarIndex = navbarContentSource.indexOf("<SearchBar />");
const leftItemsIndex = navbarContentSource.indexOf("<NavbarItems items={leftItems} />");

if (
  logoIndex === -1 ||
  searchBarIndex === -1 ||
  leftItemsIndex === -1 ||
  !(logoIndex < searchBarIndex && searchBarIndex < leftItemsIndex)
) {
  throw new Error("SearchBar is not rendered to the right of the navbar brand");
}

if (!customCssSource.includes("--search-local-modal-width")) {
  throw new Error("Search styling overrides are missing from custom.css");
}

console.log("Local search wiring looks correct.");
