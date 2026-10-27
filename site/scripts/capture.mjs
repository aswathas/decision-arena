/**
 * Capture the review screenshots the impeccable finish review needs.
 *
 *   node scripts/capture.mjs               # the landing page
 *   node scripts/capture.mjs course        # the course index
 *   node scripts/capture.mjs lessons/L00   # one lesson
 *
 * Writes:
 *   .impeccable/review/desktop.png   1440 wide, full page
 *   .impeccable/review/mobile.png     390 wide, full page
 *   .impeccable/review/plate.png      the first-viewport plate alone
 *
 * With an argument, the captures are written next to each other with the
 * argument in the name, so the course pages do not overwrite the landing
 * page's evidence.
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const outDir = resolve(repoRoot, '.impeccable', 'review');
const base = process.env.SITE_URL ?? 'http://localhost:4321/';

const target = (process.argv[2] ?? '').replace(/^\/+|\/+$/g, '');
const url = target ? `${base}${target}/` : base;
const suffix = target ? `-${target.replace(/\//g, '-')}` : '';

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();

async function shoot(name, width, height, fullPage, selector) {
  const page = await browser.newPage({ viewport: { width, height } });
  await page.goto(url, { waitUntil: 'networkidle' });
  // let webfonts settle before the capture
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(600);
  const subject = selector ? page.locator(selector) : page;
  await subject.screenshot({ path: resolve(outDir, name), fullPage });
  await page.close();
  console.log('wrote', name, '->', url);
}

await shoot(`desktop${suffix}.png`, 1440, 900, true, null);
await shoot(`mobile${suffix}.png`, 390, 844, true, null);
if (!target) {
  await shoot('plate.png', 1440, 900, false, '.plate__frame');
}

await browser.close();
