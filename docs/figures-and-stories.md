# Figures, stories and motion - the command reference

How the illustrated course is produced, and who owns what. The contract that
governs the *content* is [`site/FIGURES.md`](../site/FIGURES.md); this file is
the **command reference** - the commands, the order, the ownership map and the
gates.

## The pipeline, in order

```bash
# 1. the lessons are the source of truth
python tools/course_check.py --index        # regenerate course/curriculum.json
python tools/course_check.py --check        # the course gate

# 2. the illustrated-course gate (story + diagram + picture, per lesson)
python tools/check_course_figures.py
python tools/check_course_figures.py --list  # what is still missing

# 3. build the site
cd site && npm run build                     # base "/"
cd site && npm run preview                   # serve on :4321

# 4. the checks on the built site
python tools/check_site_a11y.py              # every built page: a11y + links
cd site && node scripts/capture.mjs          # recapture the review screenshots
cd site && node scripts/measure.mjs          # measure the first viewport

# 5. the detector (needs the preview server running)
impeccable.cmd detect --json --viewport 1440x900 http://localhost:4321/lessons/L00/
```

## Generating one picture

The pictures are generated on this machine, not downloaded. A scraped image
carries a licence the repository cannot carry.

```bash
# 1. write the prompt (one JSON object) - see site/FIGURES.md for the template
# 2. generate
mcode-tools connector call connector__matrix__generate_image --args-file prompt.json
#    -> {"success_items":[{"node_id":"...","file_name":"L00.jpg"}]}
# 3. get the download URL
mcode-tools get_asset_url <node_id>
# 4. download it into place
curl -o site/public/illustrations/L00.jpg "<download_url>"
```

The style clause of the prompt is fixed; only the scene clause changes. The
fixed clause is what keeps 46 pictures looking like one publication.

## Ownership map - one writer per file

The work was split by phase, then re-cut twice as the run went long: the point
was always to finish, and the only way to finish is to keep every file with
exactly one writer. **Each agent owns exactly the files in its own rows.
Nothing else. If you need a file that is not yours, say so instead of editing
it.**

| workstream | lessons it owns | files it owns |
|---|---|---|
| A | L00, L10 | `course/lessons/L00-*.md`, `course/lessons/L10-*.md` + `site/src/figures/<ID>.astro` + `site/public/illustrations/<ID>.jpg` for those ids |
| B | L11-L14, plus a repair pass on L20-L24 and L30-L33 | the lesson files for L11-L14, `site/src/figures/<ID>.astro` for L11-L14 and for the nine repair ids, `site/public/illustrations/<ID>.jpg` for L11-L14 |
| C | L40-L44, L50-L54, L60-L63 | the same three kinds of file, for those 14 ids |
| D | L70-L73 | `site/src/figures/<ID>.astro` for those ids; the pictures are already generated and committed, so D does not touch them |
| E | L01-L04 | `site/src/figures/<ID>.astro` + `site/public/illustrations/<ID>.jpg` for those ids (the stories were written by A) |
| F | L45 | `course/lessons/L45-*.md` + `site/src/figures/L45.astro` + `site/public/illustrations/L45.jpg` |
| G | L80-L83, L90-L93 | `site/src/figures/<ID>.astro` for those ids, plus the `## The story` section of `course/lessons/L93-publication.md`; the pictures are already generated and committed |

The repair pass in workstream B exists because the figures and the pictures
were produced by different waves of the run: a figure written before its
picture existed has no `<img>` inside it, and the lesson page then shows a
diagram with no picture. The fix is one block per file:

```astro
<img
  class="fig__picture"
  src={`${import.meta.env.BASE_URL}illustrations/<ID>.jpg`}
  alt="<one sentence describing the actual generated picture>"
/>
```

as the **first child** of `<div class="fig__frame">`, before the `<svg>`. The
`BASE_URL` prefix is what makes it work under the GitHub Pages base path
`/decision-arena`.

Files nobody but the orchestrator touches:

- `site/src/styles/global.css` - the tokens and the motion primitives
- `site/src/pages/lessons/[id].astro` - the page that renders the figure
- `site/src/components/*` - the shared chrome
- `tools/*` - the gates
- `course/FORMAT.md`, `course/curriculum.json` - the course contract
- `DESIGN.md`, `.impeccable/design.json` - the design system

## The order the work is done in

1. **The story first.** A diagram without a story is a picture of a concept
   nobody has met yet. Write `## The story` in the lesson file, read it
   yourself, and only then draw.
2. **The diagram second.** The diagram is the story made mechanical: the
   same situation, with the moving parts visible.
3. **The picture third.** The picture is the story seen: the human scene,
   no labels, no numbers.
4. **Check.** `python tools/check_course_figures.py` must pass for your ids
   before you report the workstream done.

## The gates, and what they mean

| gate | what it protects |
|---|---|
| `tools/course_check.py --check` | a lesson is well-formed: front matter, the eight required sections in order, a quiz with three good questions, real prerequisites |
| `tools/check_course_figures.py` | a lesson is finished as a *teaching artifact*: it has a story in the word band, a diagram with an accessible name and description, and a picture that exists and is under the size limit |
| `tools/test_check_course_figures.py` | the figures gate itself: thirteen deliberately broken figures, each of which must be rejected. A gate nobody has tested is a gate nobody can trust |
| `tools/check_site_a11y.py` | every built page has one h1, no duplicate ids, labelled SVGs, a skip link, a lang, a description, and every link - including in-page anchors - resolves |
| the Impeccable detector | no kickers, no tiny text, no low contrast, no runaway measure, on the built pages |
| `python -m unittest discover -s tests` | the harness and the learning engine still work |

### The three browser checks

The Python gate cannot measure pixels, so three things are checked in a real
browser instead. They need the site built and served.

```bash
cd site && npm run build
node site/node_modules/astro/bin/astro.mjs preview --port 4321   # if not already serving

cd site
node scripts/measure_mdraw.mjs http://localhost:4321   # every drawn stroke covers its path
node scripts/measure_figs.mjs                          # no text overlaps, none past the frame
node scripts/check_reduced_motion.mjs                  # the reduced-motion end state is the end state
```

- **measure_mdraw** walks the dash pattern of every `.m-draw` element and
  compares the painted arc against the real path length. A dash period shorter
  than the path loses the tail of the stroke - and the arrowhead with it.
- **measure_figs** compares the bounding boxes of every `<text>` in every
  figure. Overlaps above about two pixels are real collisions; a fraction of a
  pixel is ordinary line spacing.
- **check_reduced_motion** emulates `prefers-reduced-motion: reduce` and reads
  the transform of the markers that travel. With the motion off, a marker must
  still sit where the story ends, not where it started.

## Motion, in one paragraph

Motion is authored, not decorative, and there are five primitives for it:
`.m-draw`, `.m-rise`, `.m-pulse`, `.m-fade`, `.m-sweep`, all defined in
`site/src/styles/global.css`. One idea per figure, 0.6s to 2.4s, ease-out,
and every one of them is switched off by
`@media (prefers-reduced-motion: reduce)`. An animation may introduce a
number; it must never make a number unreadable.

## What this work is not

- It is not a second progress system. The reader still learns in the
  repository, with the tutor, and the per-concept record stays in
  `learning/progress.json`.
- It is not decoration. Every figure teaches one thing, and the caption says
  what.
- It is not scraped imagery. Every picture is generated here, and every
  diagram is hand-written SVG in the site's own palette.
