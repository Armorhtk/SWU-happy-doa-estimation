import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const websiteRoot = path.resolve(__dirname, "..");
const indexPath = path.join(websiteRoot, "src", "pages", "index.js");
const heroRadarPath = path.join(websiteRoot, "src", "components", "HeroRadar.js");

const indexSource = fs.readFileSync(indexPath, "utf8");

if (!fs.existsSync(heroRadarPath)) {
  throw new Error("Missing homepage Hero radar component at website/src/components/HeroRadar.js");
}

if (!indexSource.includes('import HeroRadar from "../components/HeroRadar";')) {
  throw new Error("Homepage does not import the HeroRadar component");
}

if (!indexSource.includes("<HeroRadar")) {
  throw new Error("Homepage does not render the HeroRadar component");
}

if (indexSource.includes('useBaseUrl("/img/radar.svg")')) {
  throw new Error("Homepage still uses the static /img/radar.svg asset as the hero visual");
}

console.log("Homepage hero radar wiring looks correct.");
