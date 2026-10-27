// Temporary audit script (not part of the deliverable).
// Captures each of the eleven figures at the animation END state under
// NORMAL motion, into the repo's review-evidence folder.
import { chromium } from '../node_modules/playwright/index.mjs';
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const outDir = resolve(repoRoot, '.impeccable', 'review', 'mdraw');
await mkdir(outDir, { recursive: true });

const IDS = ["L90", "L61", "L60", "L40", "L63", "L44", "L53", "L54", "L62", "L73", "L41"];
const BASE = process.argv[2] || "http://localhost:4321";

// zoomed crops on the arrow tips, in SVG viewBox user units
const CLIPS = {
  L61: [400, 55, 120, 240],
  L63: [340, 70, 100, 180],
  L60: [420, 55, 120, 130],
  L40: [60, 100, 420, 190],
  L44: [380, 80, 100, 170],
  L62: [250, 90, 80, 110],
  L41: [380, 60, 80, 140],
  L90: [300, 30, 340, 250],
};

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1400, height: 2400 },
  deviceScaleFactor: 3,
  reducedMotion: "no-preference",
});
const page = await ctx.newPage();

for (const id of IDS) {
  await page.goto(`${BASE}/lessons/${id}/index.html`, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);
  const loc = page.locator(".fig__svg").first();
  await loc.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  await loc.screenshot({ path: resolve(outDir, `${id}.png`) });
  if (CLIPS[id]) {
    const box = await loc.boundingBox();
    const vb = await loc.evaluate((el) => el.getAttribute("viewBox"));
    const [, , vw, vh] = vb.split(/\s+/).map(Number);
    const [cx, cy, cw, ch] = CLIPS[id];
    await page.screenshot({
      path: resolve(outDir, `${id}-arrows.png`),
      clip: {
        x: box.x + cx * (box.width / vw),
        y: box.y + cy * (box.height / vh),
        width: cw * (box.width / vw),
        height: ch * (box.height / vh),
      },
    });
  }
  console.log(`${id}.png`);
}

await browser.close();
