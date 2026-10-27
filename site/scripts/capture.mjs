/**
 * Capture the review screenshots the impeccable finish review needs.
 *
 *   node scripts/capture.mjs
 *
 * Writes:
 *   .impeccable/review/desktop.png   1440 wide, full page
 *   .impeccable/review/mobile.png     390 wide, full page
 *   .impeccable/review/plate.png      the first-viewport plate alone
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const outDir = resolve(repoRoot, '.impeccable', 'review');
const url = process.env.SITE_URL ?? 'http://localhost:4321/';

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();

async function shoot(name, width, height, fullPage, selector) {
  const page = await browser.newPage({ viewport: { width, height } });
  await page.goto(url, { waitUntil: 'networkidle' });
  // let webfonts settle before the capture
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(600);
  const target = selector ? page.locator(selector) : page;
  await target.screenshot({ path: resolve(outDir, name), fullPage });
  await page.close();
  console.log('wrote', name);
}

await shoot('desktop.png', 1440, 900, true, null);
await shoot('mobile.png', 390, 844, true, null);
await shoot('plate.png', 1440, 900, false, '.plate__frame');

await browser.close();
