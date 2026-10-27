/**
 * Optimize the generated illustrations.
 *
 * The image generator returns a 1K JPEG of roughly 600KB. Forty-six of those
 * is 27MB of repository weight for pictures that are shown at 640px wide, so
 * every generated illustration is re-encoded here: resized to 1200px on the
 * long edge and re-compressed as a progressive JPEG. The result is around a
 * fifth of the size and visually identical at the size the site shows it.
 *
 * The raw downloads live in a scratch directory inside the repository that is
 * git-ignored, so the repository only ever holds the optimized file.
 *
 *   node scripts/optimize-illustrations.mjs
 *   node scripts/optimize-illustrations.mjs --raw <dir> --out <dir>
 */
import sharp from 'sharp';
import { readdir, mkdir, stat } from 'node:fs/promises';
import { basename, extname, join, resolve } from 'node:path';

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const here = new URL('.', import.meta.url).pathname.replace(/^\//, '');
const rawDir = resolve(flag('raw', join(here, '..', '.illustrations-raw')));
const outDir = resolve(flag('out', join(here, '..', 'public', 'illustrations')));

await mkdir(outDir, { recursive: true });

let files = [];
try {
  files = (await readdir(rawDir)).filter((f) => /\.(jpe?g|png)$/i.test(f));
} catch {
  console.log(`no raw images in ${rawDir} - nothing to do`);
  process.exit(0);
}

let totalIn = 0;
let totalOut = 0;

for (const file of files) {
  const id = basename(file, extname(file));
  const input = join(rawDir, file);
  const output = join(outDir, `${id}.jpg`);
  const before = (await stat(input)).size;
  await sharp(input)
    .resize({ width: 1200, height: 1200, fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 74, progressive: true, mozjpeg: true })
    .toFile(output);
  const after = (await stat(output)).size;
  totalIn += before;
  totalOut += after;
  console.log(
    `${id}: ${Math.round(before / 1024)}KB -> ${Math.round(after / 1024)}KB`,
  );
}

console.log(
  `\n${files.length} image(s): ${Math.round(totalIn / 1024)}KB -> ${Math.round(totalOut / 1024)}KB`,
);
