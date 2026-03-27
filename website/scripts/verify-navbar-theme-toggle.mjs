import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const websiteRoot = path.resolve(__dirname, "..");

const navbarContentPath = path.join(
  websiteRoot,
  "src",
  "theme",
  "Navbar",
  "Content",
  "index.js",
);
const navbarTogglePath = path.join(
  websiteRoot,
  "src",
  "theme",
  "Navbar",
  "ColorModeToggle",
  "index.js",
);
const navbarToggleStylesPath = path.join(
  websiteRoot,
  "src",
  "theme",
  "Navbar",
  "ColorModeToggle",
  "styles.module.css",
);

if (!fs.existsSync(navbarContentPath)) {
  throw new Error("Missing swizzled Navbar Content component");
}

if (!fs.existsSync(navbarTogglePath)) {
  throw new Error("Missing custom Navbar ColorModeToggle component");
}

if (!fs.existsSync(navbarToggleStylesPath)) {
  throw new Error("Missing custom Navbar ColorModeToggle styles");
}

const navbarContentSource = fs.readFileSync(navbarContentPath, "utf8");
const navbarToggleSource = fs.readFileSync(navbarTogglePath, "utf8");

const toggleIndex = navbarContentSource.indexOf("<NavbarColorModeToggle");
const itemsIndex = navbarContentSource.indexOf("<NavbarItems items={rightItems} />");

if (toggleIndex === -1 || itemsIndex === -1 || toggleIndex > itemsIndex) {
  throw new Error("Navbar toggle is not rendered to the left of right-side navbar items");
}

if (!navbarToggleSource.includes("setColorMode(isDark ? \"light\" : \"dark\")")) {
  throw new Error("Navbar toggle is not using the agreed light/dark two-state switch");
}

console.log("Navbar theme toggle wiring looks correct.");
