// Measure text boxes in the figures: intersections and right-edge overflow.
import { chromium } from '../node_modules/playwright/index.mjs';

const IDS = process.argv[2] ? process.argv[2].split(',') : null;
const BASE = 'http://localhost:4321/lessons/';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(BASE + 'L13/', { waitUntil: 'networkidle' });

const ids = IDS || (await page.evaluate(async () => {
  const res = await fetch('/lessons/');
  return [];
}));

// discover lesson ids from the built pages list
const fs = await import('node:fs');
const path = await import('node:path');
const dist = path.resolve('dist/lessons');
const allIds = IDS || fs.readdirSync(dist).filter(d => fs.existsSync(path.join(dist, d, 'index.html')));

for (const id of allIds) {
  await page.goto(BASE + id + '/', { waitUntil: 'networkidle' });
  const report = await page.evaluate(() => {
    const out = [];
    for (const svg of document.querySelectorAll('svg.fig__svg')) {
      const texts = [...svg.querySelectorAll('text')];
      const boxes = texts.map(t => {
        const b = t.getBBox();
        return {
          text: t.textContent,
          x: b.x, y: b.y, w: b.width, h: b.height,
          right: b.x + b.width, bottom: b.y + b.height,
        };
      });
      const pairs = [];
      for (let i = 0; i < boxes.length; i++) {
        for (let j = i + 1; j < boxes.length; j++) {
          const a = boxes[i], b = boxes[j];
          const ix = Math.min(a.right, b.right) - Math.max(a.x, b.x);
          const iy = Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y);
          if (ix > 0 && iy > 0) {
            pairs.push({ a: a.text, b: b.text, ix: +ix.toFixed(2), iy: +iy.toFixed(2) });
          }
        }
      }
      const over = boxes.filter(b => b.right > 640).map(b => ({ text: b.text, right: +b.right.toFixed(1), x: +b.x.toFixed(1) }));
      if (pairs.length || over.length) out.push({ pairs, over });
    }
    return out;
  });
  if (report.length) {
    console.log('=== ' + id);
    for (const r of report) {
      for (const p of r.pairs) console.log('  OVERLAP  ' + JSON.stringify(p));
      for (const o of r.over) console.log('  OVERFLOW ' + JSON.stringify(o));
    }
  }
}
await browser.close();
