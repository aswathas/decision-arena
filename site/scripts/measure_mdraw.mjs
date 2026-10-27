// Check that every .m-draw stroke in a figure is painted end to end.
//
// The shared motion primitive paints a stroke by animating stroke-dashoffset
// from --m-length to 0, with stroke-dasharray: var(--m-length). The dash
// pattern must cover the element's real painted length, otherwise the tail of
// the path falls into a dash GAP and is never painted - including the
// arrowhead on a marker-end.
//
// Usage:
//   node site/scripts/measure_mdraw.mjs [baseUrl] [figureIds,comma,separated]
//
// Exit code 0 when nothing is short, 1 when something is.
import { chromium } from '../node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';

const BASE = process.argv[2] || 'http://localhost:4321';
const IDS = (process.argv[3] || 'L90,L61,L60,L40,L63,L44,L53,L54,L62,L73,L41').split(',');

const browser = await chromium.launch();
const page = await browser.newPage();
const rows = [];

for (const id of IDS) {
  await page.goto(`${BASE}/lessons/${id}/index.html`, { waitUntil: 'networkidle' });
  const data = await page.evaluate(() => {
    const out = [];
    for (const el of document.querySelectorAll('.m-draw')) {
      const cs = getComputedStyle(el);
      const tag = el.tagName.toLowerCase();

      // the real painted length of the element
      let len = 0;
      if (tag === 'path') {
        len = el.getTotalLength();
      } else if (tag === 'line') {
        len = Math.hypot(el.x2.baseVal.value - el.x1.baseVal.value, el.y2.baseVal.value - el.y1.baseVal.value);
      } else if (tag === 'rect') {
        len = 2 * (el.width.baseVal.value + el.height.baseVal.value);
      } else if (tag === 'circle') {
        len = 2 * Math.PI * el.r.baseVal.value;
      } else if (tag === 'polyline' || tag === 'polygon') {
        const pts = el.points;
        for (let i = 1; i < pts.numberOfItems; i++) {
          const a = pts.getItem(i - 1);
          const b = pts.getItem(i);
          len += Math.hypot(b.x - a.x, b.y - a.y);
        }
      }

      // the dash pattern: an odd count repeats, so the period is the sum of the list
      const list = cs.strokeDasharray.split(/[,\s]+/).filter(Boolean).map(parseFloat);
      const pattern = list.length % 2 === 0 ? list : list.concat(list);
      const period = pattern.reduce((a, b) => a + b, 0);

      // is [0, len] fully painted at offset 0? walk the pattern.
      let painted = 0;
      let pos = 0;
      let on = true;
      let guard = 0;
      while (pos < len && guard++ < 10000) {
        const seg = pattern[pos % pattern.length];
        if (on) painted += Math.min(seg, len - pos);
        pos += seg;
        on = !on;
      }

      out.push({
        tag,
        d: el.getAttribute('d') || '',
        dasharray: cs.strokeDasharray,
        period,
        len,
        painted,
        marker: el.getAttribute('marker-end') || '',
        short: painted < len - 0.01,
      });
    }
    return out;
  });
  data.forEach((d, i) => rows.push({ id, idx: i + 1, ...d }));
}

await browser.close();

console.log('figure | # | dasharray | period | real length | painted | marker');
for (const r of rows) {
  console.log(
    `${r.id} | ${r.idx} | ${r.dasharray} | ${r.period} | ${r.len.toFixed(2)} | ${r.painted.toFixed(2)} | ${r.marker}`
  );
}

const bad = rows.filter((r) => r.short);
console.log(`\n.m-draw elements checked: ${rows.length}`);
console.log(`short elements         : ${bad.length}`);
for (const b of bad) {
  console.log(`  SHORT ${b.id} #${b.idx}  painted ${b.painted.toFixed(2)} of ${b.len.toFixed(2)}  d="${b.d}"`);
}
process.exit(bad.length === 0 ? 0 : 1);
