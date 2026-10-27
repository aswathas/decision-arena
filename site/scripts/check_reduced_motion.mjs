/**
 * Check the reduced-motion end state of the figures that move a marker.
 *
 *   node scripts/check_reduced_motion.mjs
 *
 * Under prefers-reduced-motion the animation is switched off, so the figure
 * must still show the END of the story: the marker where it ends up, not where
 * it started. A figure that resets to its start position teaches the wrong
 * thing to exactly the readers who asked for less motion.
 */
import { chromium } from '../node_modules/playwright/index.mjs';

const BASE = process.env.SITE_URL ?? 'http://localhost:4321/';
// The end state of each marker, as the offset it must end up at. The browser
// reports a transform as a matrix, so the check compares the numbers.
const CASES = [
  { id: 'L13', selector: '.L13-travel', expect: { tx: -273, ty: 0 } },
  { id: 'L24', selector: '.fig-marker', expect: { tx: 0, ty: 58 } },
];

const browser = await chromium.launch();
const page = await browser.newPage({ reducedMotion: 'reduce' });
let failures = 0;

for (const item of CASES) {
  await page.goto(`${BASE}lessons/${item.id}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  const transform = await page.evaluate((selector) => {
    const el = document.querySelector(`svg.fig__svg ${selector}`);
    if (!el) return null;
    return getComputedStyle(el).transform;
  }, item.selector);
  const matrix = transform && transform.match(/matrix\(([^)]+)\)/);
  const numbers = matrix ? matrix[1].split(',').map((n) => Math.round(Number(n))) : null;
  const ok = numbers
    && numbers[4] === item.expect.tx
    && numbers[5] === item.expect.ty;
  console.log(
    `${ok ? 'ok  ' : 'FAIL'} ${item.id} ${item.selector} -> ${transform} `
    + `(expected x=${item.expect.tx} y=${item.expect.ty})`
  );
  if (!ok) failures += 1;
}

await browser.close();
console.log(`\nreduced-motion end states checked: ${CASES.length}, failed: ${failures}`);
process.exit(failures ? 1 : 0);
