---
name: Decision Arena
description: A printed technical plot for engineers who must judge a decision model on their own workload.
colors:
  ground: "#f2f5f7"
  ground-deep: "#e7edf1"
  ink: "#0b1218"
  ink-70: "#45555f"
  ink-45: "#5d6b76"
  rule: "#cfd9e0"
  rule-soft: "#dfe7ec"
  prussian: "#0f3d6e"
  prussian-tint: "#e2ebf4"
  graphite: "#8a97a1"
typography:
  display:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "clamp(2.05rem, 1.1rem + 2.6vw, 3.25rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.021em"
  headline:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "clamp(1.5rem, 1.05rem + 1.5vw, 2.15rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.021em"
  title:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "clamp(1.35rem, 1.05rem + 1vw, 1.75rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.021em"
  lead:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "1.1875rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: 'IBM Plex Mono, ui-monospace, "Cascadia Mono", monospace'
    fontSize: "0.6875rem"
    fontWeight: 400
    letterSpacing: "0.09em"
  mono-caption:
    fontFamily: 'IBM Plex Mono, ui-monospace, "Cascadia Mono", monospace'
    fontSize: "0.8125rem"
    fontWeight: 400
  numeric:
    fontFamily: 'IBM Plex Mono, ui-monospace, "Cascadia Mono", monospace'
    fontSize: "1rem"
    fontWeight: 400
    fontFeature: '"tnum" 1'
  prose-heading:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "1.35rem"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.015em"
  prose-subheading:
    fontFamily: 'IBM Plex Sans, ui-sans-serif, system-ui, sans-serif'
    fontSize: "1.05rem"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.021em"
rounded:
  default: "0"
  focus: "1px"
spacing:
  tight: "0.45rem"
  label-gap: "0.6rem"
  hairline-inset: "0.85rem"
  strip: "0.9rem"
  block: "1.1rem"
  panel-inset: "1.2rem"
  row: "1.35rem"
  column: "1.5rem"
  gutter: "1.8rem"
  section: "2.4rem"
  prose-step: "2.6rem"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
    padding: "0.85rem 1.35rem"
  button-primary-hover:
    backgroundColor: "{colors.prussian}"
    textColor: "#ffffff"
  toggle-option:
    backgroundColor: "transparent"
    textColor: "{colors.ink-45}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
    padding: "0.42rem 0.72rem"
  toggle-option-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
  command:
    backgroundColor: "{colors.ground-deep}"
    textColor: "{colors.ink}"
    typography: "{typography.mono-caption}"
    rounded: "{rounded.default}"
    padding: "0.7rem 0.9rem"
  metric-chip:
    backgroundColor: "{colors.prussian-tint}"
    textColor: "{colors.prussian}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
    padding: "0.2rem 0.5rem"
  panel:
    backgroundColor: "{colors.ground}"
    padding: "clamp(1.1rem, 2.2vw, 1.85rem)"
  stat:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.numeric}"
  nav-link:
    textColor: "{colors.ink-70}"
    typography: "{typography.label}"
  foot-line:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink-45}"
    typography: "{typography.mono-caption}"
  meta-label:
    backgroundColor: "transparent"
    textColor: "{colors.ink-45}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
  meta-value:
    backgroundColor: "transparent"
    textColor: "{colors.ink-70}"
    typography: "{typography.caption}"
    rounded: "{rounded.default}"
  path-id:
    backgroundColor: "transparent"
    textColor: "{colors.prussian}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
  path-chip:
    backgroundColor: "transparent"
    textColor: "{colors.ink-70}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
    padding: "0.12rem 0.4rem"
  rail-link:
    backgroundColor: "transparent"
    textColor: "{colors.ink-70}"
    typography: "{typography.caption}"
    rounded: "{rounded.default}"
  disclosure-marker:
    backgroundColor: "transparent"
    textColor: "{colors.ink-45}"
    typography: "{typography.label}"
    rounded: "{rounded.default}"
  prose-code:
    backgroundColor: "{colors.ground-deep}"
    textColor: "{colors.ink}"
    typography: "{typography.mono-caption}"
    rounded: "{rounded.default}"
    padding: "0.08em 0.32em"
---

# Design System: Decision Arena

## Overview

**Creative North Star: "The Analysis Chart"**

The site is a printed technical plot. Not a page *about* a plot — a plot. The lineage runs from the synoptic analysis chart through the contour map to the engineer's data plot, and the governing idea is that a measurement belongs on the sheet with its own axes, its own margin codes and its own run file named in the caption. Everything here is drawn from that world: cool plot-paper ground, ink with a blue cast, one committed data colour, hairline rules only, and tabular monospace for every number because the numbers are the product.

The landing page is a figure plate. One hairline frame, two panels divided by a single hairline rule in the journal convention, and panel labels `(a)` and `(b)` set inline with their headings (`site/src/pages/index.astro:115`, `site/src/pages/index.astro:137`). There is no card row, no split hero, no icon tile, no eyebrow above a heading, and no rounded anything. The two legitimate next moves — run the battery, or learn to read what it prints — are the same kind of object on the same sheet, so they are drawn with the same instruments: the same button style, the same caption rule, the same edge codes.

The course reader is the second surface, and it is the same sheet with a longer reading column. A lesson is a technical document, so it is set like a specification: a reference strip above the title carrying the phase, the reading time, the concepts, the paths, the prerequisites and the file the reader is going to write; the lesson's own text at one measure; the lesson's own `##` sections listed in the margin; and the answer key behind a disclosure at the foot (`site/src/pages/lessons/[id].astro:39-155`). The course index is the plate's curriculum column drawn out into a table of contents (`site/src/pages/course/index.astro:27-168`). The reader adds no new world: it reuses every token, adds no colour, no radius, no shadow, no gradient and no new typeface, and it keeps the chrome identical — the nav and foot were extracted into shared components so that all forty-eight pages are drawn with the same instruments (`site/src/components/Nav.astro:9-23`, `site/src/components/Foot.astro:5-11`).

Depth is printed, not cast. There is not a single `box-shadow` in the artifact. Hierarchy comes from hairline rules, one tonal step of ground (`--color-ground-deep`), weight, size and the rare inversion of an inverted panel (`site/src/styles/global.css:8-29`, `site/src/pages/index.astro:794-796`). The single authored moment is the projection toggle in the friction field: one series is promoted to ink while the others fall back to graphite context, over 180ms (`site/src/components/FieldPlot.astro:504-524`). The reader has no authored motion of its own: its only motion belongs to the reader, the browser opening a disclosure.

**Key Characteristics:**
- Cool plot-paper ground, never cream, never warm; one committed data colour (prussian indigo).
- Hairline rules only — every border in the build is 1px, including every `border-left`.
- Zero corner radius on every surface; the only non-zero radius is a 1px focus-ring radius.
- Every number in IBM Plex Mono with tabular figures.
- One filled control per surface; everything else is a link or a hairline.
- Provenance printed in the margin: run ids, providers and file paths are set as edge codes next to the data they describe.
- The reader is the same sheet: a data strip above the title, one measure, a margin rail, and the answer key behind a disclosure.
- A label above a heading is only allowed when it carries data — a phase, a run id, a measurement name — never a decorative preamble.

## Colors

A cold, printed, ten-value palette: one paper, one ink family, two rule weights, one data blue and one grey for data that must not be mistaken for real.

### Primary
- **Prussian Indigo** (`#0f3d6e`): the single committed data colour. It marks the decision threshold region (as a 45° hatch), the metric name in the measurement list, the file paths in the evidence section, the panel tags `(a)` and `(b)`, the focus ring, the selection highlight and the hover state of the primary button. In the reader it marks the phase id in the course index, the first lesson's id in the start block, the path ids, and the correct option's marker in the quiz key. If a second hue appears anywhere, a panel has failed.
- **Prussian Tint** (`#e2ebf4`): the pale ground for prussian-bearing chips and fills — the metric name chip in the measurement list, the curriculum bands in the course column, the capstone band's base fill. It is never used as a page background.

### Secondary
- **Graphite** (`#8a97a1`): reserved for simulated data. The two unselected series in the friction field and their markers are graphite, so a reader can see the shape of the other readings without mistaking them for the selected one. Graphite never carries body text and never appears in the type ramp, and the reader does not use it at all.

### Neutral
- **Plot Ground** (`#f2f5f7`): the page. Cool, faintly blue, never cream. Also the background of the friction field's SVG canvas and the fill of inline code in the reader.
- **Deep Ground** (`#e7edf1`): the single tonal step, used for the command blocks, the one inverted section (the closing "start lesson one" band), inline code and code blocks.
- **Ink** (`#0b1218`): near-black with a blue cast. Headings, body text, the filled button, the promoted series, the threshold rule.
- **Secondary Ink** (`#45555f`): supporting prose — ledes, captions, notes, nav links, the reader's strip values and the rail's section links.
- **Tertiary Ink** (`#5d6b76`): edge codes, axis labels, station labels, the reader's strip labels and the disclosure's plus/minus marker, and other measured-label text. This is the lightest tone allowed to carry text (5.01:1 on ground).
- **Rule** (`#cfd9e0`): the structural hairline. Section dividers, the plate frame, the panel divider, row separators, block tops, the reader's strip tops and the rail's top rule.
- **Soft Rule** (`#dfe7ec`): the lighter hairline for row separators inside a list — measurements, phases, lesson rows, table rows, quiz questions — where the rule is subordinate to the data.

### Named Rules
**The One Colour Rule.** Prussian indigo is the only committed data colour on the page. A second accent hue is a defect, not an extension.

**The Graphite Means Simulated Rule.** Graphite is the colour of data that came from the offline simulator. It is never used for a real measurement and never used for text. If a future surface plots live-provider data, that series is ink or prussian, not graphite.

**The Cool Ground Rule.** The ground stays cool. No cream, no warm tint, no gradient, no texture overlay. A warm paper would make the prussian read as decorative instead of committed.

**The Reader Inherits The Palette Rule.** The course reader adds no hue, no fill, no opacity and no second accent. Every surface it introduces — the reference strip, the fact strip, the path chips, the rail, the disclosure, the code blocks — is drawn from the ground, the deep ground, the two inks, the two rules and prussian. A new surface that needs a colour the reader did not already have is a signal that it wants a different world.

## Typography

**Display Font:** IBM Plex Sans (fallback `ui-sans-serif, system-ui, sans-serif`), self-hosted woff2 at weights 400/500/600 (`site/public/fonts/fonts.css:22-43`).
**Body Font:** IBM Plex Sans (same stack, same files).
**Label/Mono Font:** IBM Plex Mono (fallback `ui-monospace, "Cascadia Mono", monospace`), self-hosted woff2 at weights 400/500 (`site/public/fonts/fonts.css:5-20`).

**Character:** A technical grotesk with drafting character, paired with a plain mono that reads like a column of a data sheet. The pairing is deliberately unflattering: no serif anywhere, no display face, no optical sizing tricks. Headings are set at weight 600 with a tight line-height (1.08) and negative tracking (-0.021em), balanced by `text-wrap: balance` so no line is left ragged; body copy is set at 1.6 and measured at 58 characters on the plate (`site/src/styles/global.css:60-72`, `site/src/pages/index.astro:449`).

### Hierarchy
- **Display** (600, `clamp(2.05rem, 1.1rem + 2.6vw, 3.25rem)`, 1.08): the `h1` of the two entry surfaces — "Judge a decision model on your own workload." on the landing page and "The whole course, in order." on the course index (`site/src/pages/index.astro:440`, `site/src/pages/course/index.astro:187`). Nothing else uses this size.
- **Headline** (600, `clamp(1.5rem, 1.05rem + 1.5vw, 2.15rem)`, 1.08): section headings, the closing call to action, and the lesson's own title, which is set at this role rather than at display (`site/src/pages/lessons/[id].astro:204-209`).
- **Title** (600, `clamp(1.35rem, 1.05rem + 1vw, 1.75rem)`, 1.08): the two panel headings inside the plate, each preceded inline by its journal panel tag (`site/src/pages/index.astro:501`).
- **Prose heading** (600, `1.35rem`, 1.08, -0.015em): the `##` sections of a lesson body, each opening with a 1px top rule — the section break of a printed document (`site/src/pages/lessons/[id].astro:317-323`).
- **Prose subheading** (600, `1.05rem`, 1.08): the `###` sections of a lesson body (`site/src/pages/lessons/[id].astro:325-328`).
- **Lead** (400, `1.1875rem`, 1.5): the standfirst under the title and the lede opening each section — the one sentence that says what the section is for.
- **Body** (400, `1rem`, 1.6): all running prose, held to a 58ch measure on the plate. Never wider, never justified.
- **Caption** (400, `0.8125rem`, 1.55): the small sans size — panel bodies, notes, stat labels, the reader's strip values, rail entries and the foot.
- **Label** (400, `0.6875rem`, 0.09em tracked, uppercase): the measured label — edge codes, nav links, metric chips, strip labels, captions. The projection toggle tracks slightly wider at 0.11em.
- **Mono caption** (400, `0.8125rem`, IBM Plex Mono): the mono size used where the content is machine-readable rather than measured — command blocks, code, the foot's two lines.
- **Numeric** (400, `1rem`, IBM Plex Mono, `font-variant-numeric: tabular-nums`): every number on the page. Carried by the `.num` utility class, which is applied to stat values, file paths, run ids, metrics, station values, axis readings, lesson ids, reading times and fact counts (`site/src/styles/global.css:98-103`).

### Named Rules
**The Tabular Number Rule.** Every numeral is set in IBM Plex Mono with tabular figures, so a column of readings aligns as a column. A number set in the sans face is a defect.

**The Measured Label Rule.** Small labels are mono, uppercase, tracked and set in tertiary ink — they are the labels a plot puts on its axes and its margin, not decorative captions. They carry measurement names, run ids, providers, file paths and station codes.

**The Document Is Not A Poster Rule.** Only the two entry surfaces carry the display size. A lesson page is a document, so its own `h1` — the lesson title, rendered from the lesson file — is set at the headline role, and the reader's headings step down from there. A reading surface that opens at poster scale is a surface that has confused itself with the landing page.

## Layout

The landing page is one 1440px-max column with fluid gutters (`clamp(1rem, 4vw, 3rem)`); every top-level block is the same width, so the sheet reads as one continuous figure rather than a stack of differently-sized sections (`site/src/pages/index.astro:428-432`, `site/src/pages/index.astro:529-534`).

**The plate.** The title block is capped at 64rem so the headline does not run the full 1440px; the frame beneath it is a two-column grid, `minmax(0, 1.5fr)` for panel (a) and `minmax(0, 1fr)` for panel (b), with a single 1px rule between them. Panel (a) is wider because it carries the chart; panel (b) carries the curriculum column. Inside a panel the order is fixed and identical: panel tag + heading, one-sentence promise, then the action and its command, then the demonstration — the actions sit above the demonstrations so both doors are actionable in the first viewport (`site/src/pages/index.astro:112-154`).

**The reading column and the margin rail.** A lesson page is a two-column grid: the reading column `minmax(0, 68ch)` and the rail `15rem`, with a gutter of `clamp(2rem, 5vw, 4rem)` between them (`site/src/pages/lessons/[id].astro:245-251`). The rail is sticky at `top: 4.5rem`, opens with a 1px top rule, and lists only the sections of the lesson it sits beside. Below 1080px the rail stops being a column and becomes a single wrapped contents line placed above the body (`site/src/pages/lessons/[id].astro:606-629`), so the lesson's own title still lands near the top of the screen.

**Prose measure.** 58 characters on the plate — the standfirst, panel bodies, section ledes, captions, caveats, the closing block and the command block. 58ch rather than the 65-75ch default because the plate is a technical document, and the tighter measure is what keeps a caption legible beside a chart. The reader opens its measure to 60ch (`site/src/pages/lessons/[id].astro:313-315`, `site/src/pages/course/index.astro:455-456`), because a lesson is read for minutes at a time rather than scanned, and 60ch is the tightest measure that still keeps a line of prose from breaking short.

**Grids inside sections.** The measurement list is a three-column grid (`3.2rem` index, `1fr` name, `1.1fr` metric and note). The phase list is `3.2rem / 1fr / 4.5rem` with the lesson count right-aligned. The command blocks, course paths and the closing two-column note all use `repeat(auto-fit, minmax(...))` — 19rem, 15rem and 20rem respectively — so they reflow by available width rather than by device (`site/src/pages/index.astro:561-568`, `site/src/pages/index.astro:718-725`, `site/src/pages/index.astro:742-747`, `site/src/pages/index.astro:774-780`). The course index draws the same conventions at a different scale: a phase block is `2.6rem / 1fr / auto`, a lesson row is `3.2rem / 1fr / 4.5rem`, and a path is a two-column block of `1fr / 1.6fr` with the lesson-id run set beside the path's description (`site/src/pages/course/index.astro:287-297`, `site/src/pages/course/index.astro:321-327`, `site/src/pages/course/index.astro:372-379`).

**Breakpoints** (the only three in the build):
- `1080px` — the plate frame collapses to one column and the divider rule becomes a horizontal rule; the evidence section collapses to one column; on the reader the margin rail becomes a wrapped contents line (`site/src/pages/index.astro:883-896`, `site/src/pages/lessons/[id].astro:606-629`).
- `760px` — the friction plot takes a 680px floor width and scrolls sideways inside its own frame, with a "Scroll the chart sideways →" hint appearing above it. This one belongs to the chart alone (`site/src/components/FieldPlot.astro:403-406`).
- `720px` — the nav wraps, the mark's sub-line is dropped, the measurement and phase grids compress their index columns, the course index's grids drop their third column, and the lesson's previous/next row becomes one column (`site/src/pages/index.astro:898-911`, `site/src/pages/course/index.astro:468-492`, `site/src/pages/lessons/[id].astro:631-639`).

**Vertical rhythm.** Sections are separated by a 1px rule and padded `clamp(2.5rem, 6vw, 5rem)`. Blocks that begin with a hairline use a consistent 0.85rem inset beneath it; the standing gaps are 1.1rem between blocks, 1.35rem between rows, 1.5rem between columns and 2.4rem between a section head and its content. The reader adds three more steps from the same family: 0.9rem under a strip's hairline, 1.2rem as the inset of a reader panel, and 2.6rem above a prose section's heading.

### Named Rules
**The Plot Keeps Its Width Rule.** A chart is never squeezed to fit. It takes a floor width and scrolls sideways inside its own frame, because a nine-station plot rendered at four-pixel type is the same as an absent plot.

**The One Column Rule.** On the plate, sections are one column of full-width bands separated by hairlines; there is no body sidebar. The reader is the world's one two-column form, and it is the printed specification's: one column of prose and a narrow margin rail that lists that page's own sections and nothing else. Nothing else in the system may sit beside prose.

**The Margin Rail Rule.** A rail in the margin is 15rem, sticky, opened by a 1px rule, and it lists the sections of the page it sits beside. It is never a second content column, never a card, never a promo, and it never carries a link the page does not already own.

## Elevation & Depth

There are no shadows anywhere in the artifact — `box-shadow` appears in no stylesheet. Depth is printed: a hairline rule separates one region from the next, one tonal step (`--color-ground-deep`) lifts the command blocks, the inline code, the code blocks and the single inverted section, and weight and size carry the rest. The only translucency in the system is the sticky navigation bar, which mixes the ground to 92% over a 6px backdrop blur so the paper stays readable as content passes under it (`site/src/components/Nav.astro:26-33`). Focus is the one overlay: a 2px prussian outline at 3px offset (`site/src/styles/global.css:85-89`). The reader adds no depth device of its own: the disclosure opens with no shadow, no lift and no transition, because the answer key is not an object floating above the page — it is the page, still folded.

### Shadow Vocabulary
- None. If a future surface needs separation, it uses a 1px rule in `--color-rule` or `--color-rule-soft`, or one step of ground. A shadow is a new token, not an extension of this one.

### Named Rules
**The Hairline Rule.** Separation is drawn with a 1px rule, never with a shadow, never with a soft border, never with a heavier stroke. Every `border-left` in the build is 1px.

**The One Inversion Rule.** The world has exactly one inverted surface: the sticky nav, which is the only translucent element. Ink-on-paper is used for the primary button, and the press state is prussian — that is the whole of the inversion vocabulary. Do not add glass, blur or lifted panels to anything else.

## Shapes

Zero radius, everywhere. Every surface is a square-edged rectangle defined by a 1px hairline; no corner rounding exists in any stylesheet, and no shadow substitutes for one. The single exception is the focus ring, which carries a 1px radius so it does not clip against a square edge (`site/src/styles/global.css:88`).

Fill is either the ground, the deep ground, the prussian tint, or a hatch. The two hatches are the system's only texture and both are 45° line patterns in prussian: a 7px pattern at 0.55 opacity marking the region where a decision crosses the 0.5 threshold (`site/src/components/FieldPlot.astro:134`), and a 6px pattern at 1.4 stroke marking the capstone band of the curriculum column (`site/src/components/CourseColumn.astro:109`). Hatching is how this world says "look here" without adding a colour.

The reader adds no new shape. Its chips, its strips, its rail and its code blocks are square-edged; the one typographic mark it introduces is the disclosure's `+` and `-`, set in the mono face at the same weight as the arrow in the plate — a character, not an icon.

## Components

### Buttons
- **Shape:** square (radius 0), 1px ink border.
- **Primary:** the only filled control on a surface. Ink ground, ground-coloured mono label, padding `0.85rem 1.35rem`, mono at 0.8125rem. It is a link styled as a control, so it carries the action label and its own arrow.
- **Hover / Focus:** background and border cross-fade to prussian over 140ms with white text; the arrow slides 3px to the right over 180ms. Focus is the global 2px prussian outline at 3px offset.
- **Secondary / Ghost:** there is none. Every other call to action is a text link with a 1px underline in `--color-rule` that turns prussian on hover (`site/src/pages/index.astro:821-833`).

### Toggle options
- **Style:** hairline boxes, never pills. Transparent ground, 1px rule border, mono micro label uppercase at 0.11em tracking, tertiary ink.
- **State:** the pressed option inverts to ink ground with ground-coloured text; the unpressed options stay transparent. `aria-pressed` carries the state, and the same state is echoed in the chart and the readout.
- **Focus:** 2px prussian outline at 2px offset.

### Command block
- **Style:** the deep ground, a 1px rule, mono at 0.8125rem, padding `0.7rem 0.9rem`. A dimmed `$` prompt sits at the baseline ahead of the command; the command itself is `white-space: pre` and the block scrolls horizontally rather than wrapping.
- **Use:** only for a command the reader can copy, always immediately under an edge code that names what the command does. The reader reuses it unchanged under "Do it in the repo" (`site/src/pages/lessons/[id].astro:90-93`).

### Edge code
- **Style:** the system's label primitive — mono, 0.6875rem, uppercase, 0.09em tracked, tertiary ink. It names a data object (`run 20261027-212313-friction-mock · provider mock`), a file (`raw calls`), a step (`1 - see what is configured on this machine`), a figure, a phase (`phase 01 · Foundations`) or a position (`previous`, `next`).

### Metric chip
- **Style:** prussian on the prussian tint, mono micro, padding `0.2rem 0.5rem`. It names the metric that answers the question — `ECE + Brier`, `action_change_rate`.

### Stat readout
- **Style:** a 1px rule on top, then a tabular number at `clamp(2rem, 1.2rem + 2.4vw, 3rem)`, line-height 1, tracking -0.02em, then a label in secondary ink capped at 34ch.
- **Note:** a stat is a reading with a label, never the hero-metric template — there is no supporting-stat cluster and no accent behind it.

### Navigation
- **Style:** a sticky hairline bar, mark and links on one baseline. The mark is the wordmark in weight 600 plus a mono micro sub-line ("the neutral harness"); the links are mono micro uppercase in secondary ink with a 1px transparent underline that turns prussian on hover.
- **Scope:** one shared component for the whole product — the landing page, the course index and all forty-six lesson pages (`site/src/components/Nav.astro:9-23`). The link set is the product's four destinations plus the repository: what it measures, run it, evidence, the course, GitHub.
- **Mobile:** the bar wraps, the links wrap with it, and the mark's sub-line is dropped.

### Page foot
- **Style:** a 1px top rule, then two mono lines in tertiary ink at 0.8125rem — identity on the left, the repository on the right — each capped at 58ch (`site/src/components/Foot.astro:5-11`). One shared component for all forty-eight pages. It is the system's only footer and it never grows a second line of links.

### The figure plate (signature)
- **Style:** a 1px frame around two panels. The divider between them is a single 1px rule, drawn as a left border on panel (b) and re-drawn as a top border when the frame collapses.
- **Caption rule:** the caption strip sits *above* the frame, not below it — a 1px top rule with two edge codes, one per panel, naming the run id, the provider and the committed files on the left, the lesson and quiz counts on the right. It is a title strip, so it is legible without scrolling to the figure's foot.
- **Order:** panel tag, heading, promise, action + command, demonstration. Identical in both panels.

### The friction field (signature)
- **Style:** an inline SVG, `viewBox 0 0 940 400`, `role="img"` with a `<title>` and a `<desc>` that states what the chart shows and how many readings flip. Y axis is P(answer) from 0 to 1 with the 0.5 decision threshold drawn as a dashed ink rule; grid lines are soft, the threshold rule is the only dashed line in the system.
- **Data:** three series (prose, flat json, nested json) as 1px polylines with 7px square markers; the selected series is promoted to ink at 1.75 stroke width over 180ms, the others fall back to graphite. Stations are grouped in three cases by vertical separators, with case ids set in mono uppercase beneath.
- **Annotation:** one callout at a time, on the featured station — a 1px leader line, a hairline circle at the marker, the reading at 21px tabular mono and the station name in mono uppercase.
- **Foot:** an edge code with the run id and provider, the measurement line (questions, mean spread, max, flips at 0.5), and the printed note that the run is simulated.

### The curriculum column (signature)
- **Style:** an inline SVG, `viewBox 0 0 420 <height>`, `role="img"` with a `<title>` and `<desc>`. Ten stacked bands, 62px wide, each band's thickness equal to its lesson count at 7px per lesson, so the course is drawn to scale. The capstone band is the 45° hatch. Band counts are tabular mono at the band's centre; the phase id and title sit to the right of the column.

### Measurement list
- **Style:** an ordered list with no bullets and a 1px top rule; each row is a 1px soft-rule bottom border and a three-column grid. The index is a tabular mono ordinal in tertiary ink, the name is a 1.12rem weight-600 heading with the question it answers beneath it, and the right column carries the metric chip and the cost of getting it wrong.

### Caveat
- **Style:** a 1px prussian left border with 1.1rem of left padding, secondary ink, 58ch, with the leading clause in ink weight 600. Inline with a figure, the same caveat loses the stripe and uses a 1px rule on top instead (`site/src/pages/index.astro:624-646`).

### The reference strip (signature)
- **Style:** a 1px rule on top, then a wrapped row of label/value pairs — the label is the measured-label primitive (mono, 0.6875rem, uppercase, tertiary ink) and the value is 0.8125rem in secondary ink. No box, no fill, no shadow; it is the stamp a specification carries above its title (`site/src/pages/lessons/[id].astro:45-74`).
- **Content:** the facts the reader needs before the first word — on a lesson, the reading time, the concepts, the paths, the lessons to read first and the file the reader is about to write; on the course index, the lesson count, the quiz count, the phase count, the path count and the total reading time (`site/src/pages/course/index.astro:37-58`).
- **The rule:** every label above the title must carry a measurement. A label that names no number, no file, no phase and no concept is a kicker, and a kicker is not part of this system.

### Path id and lesson-id chip
- **Path id:** the path's own name — mono micro uppercase at 0.09em in prussian (`site/src/pages/course/index.astro:392-398`). It is a label, not a button.
- **Lesson-id chip:** a lesson id inside a path's run — a 1px soft-rule border, `0.12rem 0.4rem` padding, mono at 0.6875rem in secondary ink, turning prussian on the border on hover (`site/src/pages/course/index.astro:438-449`). Chips in a run are joined by a 0.3rem hairline dash, so the sequence reads as a path and not as a bag of tags (`site/src/pages/course/index.astro:428-436`).

### The margin rail (signature)
- **Style:** a sticky 15rem column opened by a 1px top rule, headed by the edge code "in this lesson", then an ordered list of the lesson's own `##` sections as caption-size links in secondary ink that turn ink with a prussian underline on hover, and a foot rule with a link to the whole course (`site/src/pages/lessons/[id].astro:138-154`).
- **Source:** the list is read from the lesson file itself, not from a hand-maintained table of contents (`site/src/data/course.ts:63-88`).
- **Narrow:** below 1080px it becomes a wrapped contents line above the body, still the same links in the same order.

### The quiz disclosure (signature)
- **Style:** a native `<details>` per question, opened by a summary that carries the question's ordinal and the concept it tests, both in the measured-label primitive. The marker is a `+` set in the mono face at the margin edge, and becomes `-` when open (`site/src/pages/lessons/[id].astro:475-516`).
- **Body:** the question in weight 600, the options as a lettered list (`a`, `b`, `c`) in secondary ink, the correct option promoted to ink with a prussian marker, then the explanation below a soft rule (`site/src/pages/lessons/[id].astro:111-131`).
- **Contract:** the answer is not in the first viewport, not in the summary, and not reachable without the reader's own click. The page teaches; it does not grade.

### The prose block (signature)
- **Style:** the lesson's own markdown, rendered by the site's markdown pipeline and set in the world's grammar — headings, tables, code, lists, blockquotes and rules each get one rule, not a design of their own (`site/src/pages/lessons/[id].astro:309-424`).
- **Headings:** `h1` at the headline role and capped at 34ch; `h2` at 1.35rem with a 1px top rule and 2.6rem above it; `h3` at 1.05rem.
- **Tables:** mono micro uppercase header cells in tertiary ink over a 1px rule, rows separated by the soft rule.
- **Code:** inline code on the deep ground inside a 1px soft rule at 0.88em; a code block on the deep ground inside a 1px rule, scrolling sideways rather than wrapping.
- **Lists:** the marker is mono in tertiary ink, so the bullet reads as a plotted tick.
- **Blockquote:** a 1px rule on top and secondary ink — the same callout the plate uses inline with a figure, never a stripe down the side.

### Lesson navigation
- **Style:** a 1px rule on top, then a two-column row: previous on the left, next right-aligned, each an edge code (`previous` / `next`) above the lesson id and title (`site/src/pages/lessons/[id].astro:157-182`).

## Do's and Don'ts

### Do:
- **Do** set every number in IBM Plex Mono with tabular figures, and always beside the token counts or units that give it meaning.
- **Do** separate regions with a 1px rule in `--color-rule` (or `--color-rule-soft` for a row inside a list), and keep prose to a 58ch measure on the plate and 60ch in the reader.
- **Do** put provenance next to the data: the run id, the provider and the file path as edge codes, and the simulated-run note on the face of every plotted number.
- **Do** keep panel labels in the journal convention — `(a)` and `(b)`, set inline with the heading they belong to.
- **Do** use prussian tint as the fill under prussian text (a metric chip, a curriculum band) rather than inventing a new surface colour.
- **Do** give a chart a floor width and let it scroll sideways inside its own frame.
- **Do** write the edge code that names a data object in mono, uppercase, tracked, tertiary ink.
- **Do** render a reader surface from the repository's own file — the lesson body, the quiz and the curriculum are read, never restated — so the page cannot drift from the source.
- **Do** put the facts a reader needs before the first word in a reference strip above the title, and keep every label on it a measurement.

### Don't:
- **Don't** introduce a second accent hue, a gradient, a tinted overlay, or any fill other than the ground, the deep ground, the prussian tint or a prussian hatch.
- **Don't** add a shadow, a glow, a lifted card, a rounded corner, or a soft border to separate anything.
- **Don't** put a kicker, an eyebrow or a decorative label above a heading. A strip above a title is allowed only when its labels carry data — a phase, a reading time, a concept, a file path; the moment one of them stops carrying data it is an eyebrow, and an eyebrow is a defect.
- **Don't** number sections decoratively. The numeric indexes that exist are list positions (the measurement ordinal, the phase ids, the question ordinals) and every one of them carries information the reader needs.
- **Don't** build an icon system out of glyphs or emoji. The typographic characters the system uses are the arrow `→` and the disclosure's `+`/`-`, both set in the mono face, both meaning something a reader needs; anything else must be authored SVG.
- **Don't** squeeze a chart to fit, and don't stack competing numbers on one surface — one reading at a time, with the selected one in ink.
- **Don't** let a simulator number stand in for a model measurement, on the page or in a caption.
- **Don't** show an answer before the reader has attempted it, and don't put the key, the correct option or the explanation anywhere a reader can read it without opening the disclosure.

### Not canonized (known drift — do not inherit these as rules)
- **`--color-ink-70` and `--color-ink-45` are opaque, not alpha.** The names read like opacity steps, but both are solid hexes. Treat them as two named inks; do not compose them at 70% or 45% alpha over the ground.
- **Graphite is below the non-text contrast bar.** Graphite on the ground is 2.73:1, under the 3:1 threshold for meaningful graphics. It is used only for simulated, unselected series, and the selected series is always ink — but a future surface that plots live data in graphite would be repeating a legibility defect, not a rule.
- **The nav's translucent blur is the world's single reserved inversion, not a general treatment.** It is recorded here so that no future surface inherits glass as a system habit.
- **The reader's inline code is set at 0.88em while the base inline `code` is 0.92em** (`site/src/pages/lessons/[id].astro:361-366` against `site/src/styles/global.css:91-96`). Two sizes for one element; the reader's is the deliberate one inside a measured column, but a third surface should pick one rather than a third value.
- **The reader's two measures (58ch on the plate, 60ch in the reader) are a deliberate difference, not a scale.** They are recorded so that a future surface does not treat either as the system's measure and quietly introduce a third.
