# Figures, stories and motion - the contract

This file is the single source of truth for the illustrated course. Read it
before you write a figure, a story, or an image. Every agent that touches
this work reads this file; nothing here is duplicated in a brief.

The site is **The Analysis Chart**: a printed technical plot. Cool plot-paper
ground, near-black ink with a blue cast, prussian indigo as the one committed
colour, hairline rules only, no rounded cards, no shadows, no gradients, no
serif, every number in tabular monospace. A figure that breaks this world
does not belong on the site, however good the drawing is.

## What a lesson gets

Three artifacts, one per lesson:

1. **A story** - a `## The story` section in the lesson's own markdown file
   (`course/lessons/<id>-<slug>.md`). It teaches the concept from first
   principles: a concrete situation, a person, a mechanism made physical. It
   is not a summary of the lesson and it is not a marketing paragraph.
2. **A diagram** - `site/src/figures/<ID>.astro`, an inline SVG that shows the
   mechanism moving. This is the precise figure: axes, thresholds,
   distributions, state shapes.
3. **A picture** - `site/public/illustrations/<ID>.jpg`, a generated 2D
   line-art drawing of the same idea in a human scene. This is the one the
   learner *sees* first.

The lesson page renders them in this order: the reference strip, the figure
plate (picture + diagram + caption), the lesson body (which opens with the
story), then the exercise and the quiz key.

## The story - `## The story`

Rules, all of them:

- **120 to 220 words.** Long enough to carry a scene, short enough to read in
  a minute.
- **First principles.** Start from something the reader already understands -
  a number on a screen, a queue at a counter, a coin on a table - and build
  the concept out of it. No "in machine learning, we...".
- **A person, or a thing doing something.** "A support desk", "a scale with a
  needle", "a door with a threshold" count. Abstract nouns do not.
- **No new claims.** Every fact in the story must already be true somewhere in
  the lesson or the repo. You are making the lesson's idea memorable, not
  adding a fact.
- **No numbers you invented.** If you need a number, it must be in the lesson
  already (0.5, 0.9271, 300-450 words, and so on). A made-up measurement is
  a lie with a story around it.
- **Plain English, no jargon** the lesson has not already defined. A beginner
  reads this section first.
- Place it **after `## What breaks`** and **before `## The real thing`**: the
  naive story breaks, the story makes the real thing imaginable, and then the
  real thing is named.

The eight required sections keep their order; `## The story` is an extra
section and the gate only checks that the required ones are present and in
order.

## The diagram - `site/src/figures/<ID>.astro`

One Astro component per lesson, named by lesson id: `L00.astro`, `L31.astro`.

Template - copy this shape exactly:

```astro
---
/* L00 - what a decision model is not. One writer: the figures workstream. */
---

<figure class="fig">
  <div class="fig__frame">
    <svg
      class="fig__svg"
      viewBox="0 0 640 340"
      role="img"
      aria-labelledby="L00-fig-title L00-fig-desc"
    >
      <title id="L00-fig-title">One ticket, three shapes, one threshold</title>
      <desc id="L00-fig-desc">
        The same support ticket drawn three ways - as prose, as a flat row of
        fields, and as a nested stack - with a vertical threshold line that
        each version crosses at a different height.
      </desc>
      <!-- the drawing -->
    </svg>
  </div>
  <figcaption class="fig__caption">
    <span class="edge-code">figure {ID}</span>
    <span class="fig__caption-text">One sentence naming what the reader is looking at.</span>
  </figcaption>
</figure>

<style>
  /* scoped to this figure */
</style>
```

Rules:

- **The `viewBox` is `0 0 640 340`** (or a close ratio). No `width`/`height`
  attributes on the `<svg>` - it scales to its frame.
- **Every figure has a `<title>` and a `<desc>`**, and they are linked with
  `aria-labelledby`. The `<desc>` says what is drawn, in words, for a reader
  who cannot see it. It is not a caption repeat.
- **Hairlines.** `stroke-width="1"`, colours from the token set only. Never a
  literal colour that is not a token; use `var(--color-ink)`,
  `var(--color-prussian)`, `var(--color-rule)`, `var(--color-rule-soft)`,
  `var(--color-ground-deep)`, `var(--color-prussian-tint)`.
- **No fills that are not flat.** No gradients, no filters, no shadows, no
  `opacity` on text.
- **No `<script>`, no external URLs, no `url(...)` references to anything
  remote.** The site makes no third-party request.
- **Mono type for every label**, at 10-12px, in `var(--color-ink-70)`. Use
  `font-family="var(--font-mono)"` and `font-variant-numeric: tabular-nums`.
  Labels are short: a word, a number, a symbol.
- **The figure teaches.** It is a diagram of the concept, not decoration. If
  you cannot say in one sentence what the reader learns from it, redraw it.
- **Text in the SVG is text, and it is real.** Never fake a label with
  rectangles.

## Motion

Motion is authored, not decorative. One idea per figure, and it must be the
idea the figure is about.

Shared primitives, already in `site/src/styles/global.css` - use these
before writing your own keyframes:

| class | what it does |
|---|---|
| `.m-draw` | a path draws itself, `stroke-dashoffset` to `0` |
| `.m-rise` | a bar or block rises into place |
| `.m-sweep` | a marker travels along its path |
| `.m-pulse` | a dot pulses once, then rests |
| `.m-fade` | an element fades in, staggered by `--m-delay` |

Rules:

- **Every animation is short**: 0.6s to 2.4s, with an ease-out. Nothing
  loops forever except a slow ambient drift, and even that is capped.
- **Motion must be suppressible.** The global rule
  `@media (prefers-reduced-motion: reduce)` in `global.css` turns every
  animation off. Do not defeat it with `!important`.
- **No motion on text that must be read.** An animation may introduce a
  number; it must not make a number unreadable.
- If a figure has no motion, that is acceptable - but say so in the caption's
  edge code? No. A still figure is fine.

## The picture - `site/public/illustrations/<ID>.jpg`

A generated 2D line-art drawing of the same idea in a human scene. Generate
it with the tool on this machine, do not download images from the internet -
a scraped image carries a licence the repository cannot carry.

### How to generate one

```bash
# 1. write the prompt to a file (one JSON object)
# 2. generate
mcode-tools connector call connector__matrix__generate_image --args-file <prompt.json>
# 3. take the node_id from success_items, then
mcode-tools get_asset_url <node_id>
# 4. download the download_url to site/public/illustrations/<ID>.jpg
```

The prompt template - keep the style clause identical every time, change only
the scene:

```
2D technical line-art diagram, single-weight ink strokes, flat fills, no
gradients, no 3D, no photorealism, no text, no letters, no numbers. Palette
limited to: near-black ink #0b1218, deep prussian blue #0f3d6e, cool pale
paper #f2f5f7, and a pale blue tint #e2ebf4. Scene: <THE SCENE, CONCRETELY>.
The composition is a calm, precise engineering drawing on pale paper,
generous white space, hairline rules, schematic and legible, like a figure in
a printed technical manual.
```

Use `aspect_ratio` `4:3` and `resolution` `1K`. The scene clause must be
concrete and physical: *what is in the picture, and what is moving or
crossing what*. Not an abstract noun.

### Rules

- **One picture per lesson**, named `<ID>.jpg`.
- **No text, letters or numbers in the image.** The site labels it; a
  generated image with garbled text is worse than no image.
- **The picture must be legible at 640px wide.** If the scene came back as an
  unreadable mess, regenerate with a simpler scene clause. It is allowed to
  say "fewer elements".
- **Under 400KB.** If it is bigger, regenerate at 1K with a simpler scene.
- The picture is a *scene*; the SVG is the *diagram*. Do not draw the same
  thing twice in the same way.

## The caption

Every figure carries a caption with two parts: the edge code (`figure L31`)
and one sentence naming what the reader is looking at. The sentence is
written for someone skimming: it should be usable as a caption under a
figure in a printed manual.

## What the gate checks

`python tools/check_course_figures.py` fails if:

- a lesson has no `## The story`, or the story is empty or out of the word
  range;
- a lesson has no `site/src/figures/<ID>.astro` or no
  `site/public/illustrations/<ID>.jpg`;
- a figure has no `<title>`, no `<desc>`, no `aria-labelledby`, or a
  `viewBox` that is not a sensible size;
- a figure references a remote URL, a `<script>`, or a colour literal that is
  not one of the six tokens;
- an illustration is missing, empty, or over 400KB.

Run it before you claim a workstream is done.
