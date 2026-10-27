/**
 * Capture the review screenshots the impeccable finish review needs.
 *
 *   node scripts/capture.mjs               # the landing page
 *   node scripts/capture.mjs course        # the course index
 *   node scripts/capture.mjs lessons/L00   # one lesson
 *
 * A second argument captures one element instead of the page:
 *
 *   node scripts/capture.mjs "" ".shapes"  # the friction figure alone
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

const raw = process.argv[2] ?? '';
// "index" means the landing page; an empty argument cannot be passed through
// a shell reliably, so the word stands in for it.
const target = (raw === 'index' ? '' : raw).replace(/^\/+|\/+$/g, '');
const selector = process.argv[3] ?? null;
const url = target ? `${base}${target}/` : base;
const suffix = target ? `-${target.replace(/\//g, '-')}` : '';
// An element capture gets its own name, so it never overwrites the page
// capture of the same route.
const selSuffix = selector ? `--${selector.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '')}` : '';

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();

async function shoot(name, width, height, fullPage, selector) {
  // An element capture is usually narrower than the viewport, so it is taken
  // at 2x and stays sharp when the image is used at post size.
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: selector ? 2 : 1,
  });
  await page.goto(url, { waitUntil: 'networkidle' });
  // let webfonts settle before the capture
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(600);
  const subject = selector ? page.locator(selector) : page;
  if (selector) {
    // The sticky nav sits over the element when it is scrolled into view, so
    // an element capture would start with a bar of chrome across the top.
    await page.evaluate(() => {
      const nav = document.querySelector('header.nav');
      if (nav) nav.style.visibility = 'hidden';
    });
    await subject.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
  }
  await subject.screenshot({ path: resolve(outDir, name), fullPage });
  await page.close();
  console.log('wrote', name, '->', url);
}

await shoot(`desktop${suffix}${selSuffix}.png`, 1440, 900, true, selector);
await shoot(`mobile${suffix}${selSuffix}.png`, 390, 844, true, selector);
if (!target && !selector) {
  await shoot('plate.png', 1440, 900, false, '.plate__frame');
}

await browser.close();
