/**
 * Prepare the images that go with a LinkedIn post.
 *
 *   node scripts/post-media.mjs 01-hook=../../.impeccable/review/desktop-lessons-L61--lesson-figure.png
 *   node scripts/post-media.mjs 02-course=../../.impeccable/review/desktop-course--fig-map.png
 *
 * Each argument is name=path. The script writes docs/linkedin/media/<name>.jpg
 * at 1200 x 1200 (the square the feed gives the most room to), and keeps the
 * file small enough for a mobile reader.
 *
 * The fit is chosen by the shape of the source, because the wrong choice
 * destroys the picture:
 *   - a source that is wider than it is tall is FITTED, not cropped, so the
 *     whole figure stays in frame (a cropped figure loses its right-hand
 *     scale, which is the part the reader needs);
 *   - a source that is taller than it is wide is CROPPED from the top, so a
 *     long page becomes its first screen rather than a thin strip.
 *
 * Override with name:fit=path, name:land=path or name:crop=path.
 *
 * Costs: file read and write only. No network.
 */
import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const outDir = resolve(repoRoot, 'docs', 'linkedin', 'media');
const PAPER = '#f2f5f7';

const SHAPES = {
  fit: { width: 1200, height: 1200 },
  land: { width: 1200, height: 627 },
  crop: { width: 1200, height: 1200 },
};

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('usage: node scripts/post-media.mjs <name>=<path> [...]');
  process.exit(1);
}

await mkdir(outDir, { recursive: true });

for (const arg of args) {
  const index = arg.indexOf('=');
  if (index < 1) {
    console.log(`skip ${arg}: expected name=path`);
    continue;
  }
  let name = arg.slice(0, index);
  const source = resolve(process.cwd(), arg.slice(index + 1));
  let mode = null;
  for (const key of Object.keys(SHAPES)) {
    if (name.endsWith(`:${key}`)) {
      mode = key;
      name = name.slice(0, -(key.length + 1));
    }
  }
  const out = resolve(outDir, `${name}.jpg`);
  try {
    const meta = await sharp(source).metadata();
    const wide = (meta.width || 1) >= (meta.height || 1);
    const choice = mode || (wide ? 'land' : 'crop');
    const shape = SHAPES[choice];
    let pipeline = sharp(source);
    if (choice === 'crop') {
      pipeline = pipeline.resize(shape.width, shape.height, { fit: 'cover', position: 'top' });
    } else {
      pipeline = pipeline.resize(shape.width, shape.height, {
        fit: 'contain',
        background: PAPER,
      });
    }
    await pipeline.jpeg({ quality: 82, progressive: true }).toFile(out);
    console.log('wrote', out, `(${choice}, ${meta.width}x${meta.height})`);
  } catch (error) {
    console.log(`FAIL ${name}: ${error.message}`);
  }
}
