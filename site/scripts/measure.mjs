/**
 * Measure the first viewport against the contract's promise.
 *
 *   node scripts/measure.mjs
 *
 * The contract says both primary actions and the shared caption rule must be
 * inside the first viewport at desktop width. "Inside the first viewport" is
 * a number, not an opinion, so this reports it.
 */
import { chromium } from 'playwright';

const url = process.env.SITE_URL ?? 'http://localhost:4321/';

const browser = await chromium.launch();

async function measure(label, width, height) {
  const page = await browser.newPage({ viewport: { width, height } });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);

  const report = await page.evaluate((h) => {
    const box = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {
        top: Math.round(r.top + window.scrollY),
        bottom: Math.round(r.bottom + window.scrollY),
        left: Math.round(r.left),
        width: Math.round(r.width),
      };
    };
    const actions = Array.from(document.querySelectorAll('.panel__action .action')).map((el) => {
      const r = el.getBoundingClientRect();
      return { text: el.textContent.trim().split('\n')[0], bottom: Math.round(r.bottom) };
    });
    return {
      viewportHeight: h,
      title: box('.plate__title'),
      sub: box('.plate__sub'),
      frame: box('.plate__frame'),
      caption: box('.plate__caption'),
      plot: box('.field__svg'),
      column: box('.column__svg'),
      actions,
    };
  }, height);

  console.log(`\n=== ${label} (${width}x${height}) ===`);
  const at = (name, v) => console.log(`  ${name.padEnd(12)} ${v ? `top ${String(v.top).padStart(5)}  bottom ${String(v.bottom).padStart(5)}  w ${v.width}` : 'not found'}`);
  at('title', report.title);
  at('subtitle', report.sub);
  at('plate frame', report.frame);
  at('plot', report.plot);
  at('column', report.column);
  at('caption', report.caption);
  for (const a of report.actions) {
    const inFold = a.bottom <= report.viewportHeight;
    console.log(`  action "${a.text}" bottom ${a.bottom}  ${inFold ? 'IN FOLD' : 'BELOW FOLD'}`);
  }
  if (report.caption) {
    console.log(`  caption       ${report.caption.bottom <= report.viewportHeight ? 'IN FOLD' : 'BELOW FOLD'}`);
  }
  await page.close();
}

await measure('desktop', 1440, 900);
await measure('mobile', 390, 844);

await browser.close();
