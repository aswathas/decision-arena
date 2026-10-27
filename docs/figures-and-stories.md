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

The work is split by phase. **Each agent owns exactly the files in its own
rows. Nothing else. If you need a file that is not yours, say so instead of
editing it.**

| workstream | phases | lessons | files it owns |
|---|---|---|---|
| A | 0, 1, 2 | L00, L10, L01-L04, L11-L14 | `course/lessons/L0*.md`, `course/lessons/L1*.md` (the 10 lesson ids above) + `site/src/figures/<ID>.astro` + `site/public/illustrations/<ID>.jpg` for those ids |
| B | 3, 4 | L20-L24, L30-L34 | the same three kinds of file, for those 10 ids |
| C | 5, 6, 7 | L40-L44, L50-L54, L60-L63 | the same three kinds of file, for those 14 ids |
| D | 8, 9 | L70-L73, L80-L83, L90-L93 | the same three kinds of file, for those 12 ids |

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
| `tools/check_site_a11y.py` | every built page has one h1, no duplicate ids, labelled SVGs, a skip link, a lang, a description, and every link - including in-page anchors - resolves |
| the Impeccable detector | no kickers, no tiny text, no low contrast, no runaway measure, on the built pages |
| `python -m unittest discover -s tests` | the harness and the learning engine still work |

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
