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
  label:
    fontFamily: 'IBM Plex Mono, ui-monospace, "Cascadia Mono", monospace'
    fontSize: "0.6875rem"
    fontWeight: 400
    letterSpacing: "0.09em"
  numeric:
    fontFamily: 'IBM Plex Mono, ui-monospace, "Cascadia Mono", monospace'
    fontSize: "1rem"
    fontWeight: 400
    fontFeature: '"tnum" 1'
rounded:
  default: "0"
  focus: "1px"
spacing:
  tight: "0.45rem"
  label-gap: "0.6rem"
  hairline-inset: "0.85rem"
  block: "1.1rem"
  row: "1.35rem"
  column: "1.5rem"
  section: "2.4rem"
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
    typography: "{typography.label}"
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
---

# Design System: Decision Arena

## Overview

**Creative North Star: "The Analysis Chart"**

The site is a printed technical plot. Not a page *about* a plot — a plot. The lineage runs from the synoptic analysis chart through the contour map to the engineer's data plot, and the governing idea is that a measurement belongs on the sheet with its own axes, its own margin codes and its own run file named in the caption. Everything here is drawn from that world: cool plot-paper ground, ink with a blue cast, one committed data colour, hairline rules only, and tabular monospace for every number because the numbers are the product.

The page is a figure plate. One hairline frame, two panels divided by a single hairline rule in the journal convention, and panel labels `(a)` and `(b)` set inline with their headings (`site/src/pages/index.astro:127`, `site/src/pages/index.astro:149`). There is no card row, no split hero, no icon tile, no eyebrow above a heading, and no rounded anything. The two legitimate next moves — run the battery, or learn to read what it prints — are the same kind of object on the same sheet, so they are drawn with the same instruments: the same button style, the same caption rule, the same edge codes.

Depth is printed, not cast. There is not a single `box-shadow` in the artifact. Hierarchy comes from hairline rules, one tonal step of ground (`--color-ground-deep`), weight, size and the rare inversion of an inverted panel (`site/src/styles/global.css:8-29`, `site/src/pages/index.astro:536-541`). The single authored moment is the projection toggle in the friction field: one series is promoted to ink while the others fall back to graphite context, over 180ms (`site/src/components/FieldPlot.astro:495-517`).

**Key Characteristics:**
- Cool plot-paper ground, never cream, never warm; one committed data colour (prussian indigo).
- Hairline rules only — every border in the build is 1px, including every `border-left`.
- Zero corner radius on every surface; the only non-zero radius is a 1px focus-ring radius.
- Every number in IBM Plex Mono with tabular figures.
- One filled control on the page; everything else is a link or a hairline.
- Provenance printed in the margin: run ids, providers and file paths are set as edge codes next to the data they describe.

## Colors

A cold, printed, ten-value palette: one paper, one ink family, two rule weights, one data blue and one grey for data that must not be mistaken for real.

### Primary
- **Prussian Indigo** (`#0f3d6e`): the single committed data colour. It marks the decision threshold region (as a 45° hatch), the metric name in the measurement list, the file paths in the evidence section, the panel tags `(a)` and `(b)`, the focus ring, the selection highlight and the hover state of the primary button. If a second hue appears anywhere, a panel has failed.
- **Prussian Tint** (`#e2ebf4`): the pale ground for prussian-bearing chips and fills — the metric name chip in the measurement list, the curriculum bands in the course column, the capstone band's base fill. It is never used as a page background.

### Secondary
- **Graphite** (`#8a97a1`): reserved for simulated data. The two unselected series in the friction field and their markers are graphite, so a reader can see the shape of the other readings without mistaking them for the selected one. Graphite never carries body text and never appears in the type ramp.

### Neutral
- **Plot Ground** (`#f2f5f7`): the page. Cool, faintly blue, never cream. Also the background of the friction field's SVG canvas.
- **Deep Ground** (`#e7edf1`): the single tonal step, used for the command blocks and the one inverted section (the closing "start lesson one" band).
- **Ink** (`#0b1218`): near-black with a blue cast. Headings, body text, the filled button, the promoted series, the threshold rule.
- **Secondary Ink** (`#45555f`): supporting prose — ledes, captions, notes, nav links.
- **Tertiary Ink** (`#5d6b76`): edge codes, axis labels, station labels, and other measured-label text. This is the lightest tone allowed to carry text (5.01:1 on ground).
- **Rule** (`#cfd9e0`): the structural hairline. Section dividers, the plate frame, the panel divider, row separators, block tops.
- **Soft Rule** (`#dfe7ec`): the lighter hairline for row separators inside a list — measurements, phases — where the rule is subordinate to the data.

### Named Rules
**The One Colour Rule.** Prussian indigo is the only committed data colour on the page. A second accent hue is a defect, not an extension.

**The Graphite Means Simulated Rule.** Graphite is the colour of data that came from the offline simulator. It is never used for a real measurement and never used for text. If a future surface plots live-provider data, that series is ink or prussian, not graphite.

**The Cool Ground Rule.** The ground stays cool. No cream, no warm tint, no gradient, no texture overlay. A warm paper would make the prussian read as decorative instead of committed.

## Typography

**Display Font:** IBM Plex Sans (fallback `ui-sans-serif, system-ui, sans-serif`), self-hosted woff2 at weights 400/500/600 (`site/public/fonts/fonts.css:22-43`).
**Body Font:** IBM Plex Sans (same stack, same files).
**Label/Mono Font:** IBM Plex Mono (fallback `ui-monospace, "Cascadia Mono", monospace`), self-hosted woff2 at weights 400/500 (`site/public/fonts/fonts.css:5-20`).

**Character:** A technical grotesk with drafting character, paired with a plain mono that reads like a column of a data sheet. The pairing is deliberately unflattering: no serif anywhere, no display face, no optical sizing tricks. Headings are set at weight 600 with a tight line-height (1.08) and negative tracking (-0.021em), balanced by `text-wrap: balance` so no line is left ragged; body copy is set at 1.6 and measured at 58 characters (`site/src/styles/global.css:60-72`, `site/src/pages/index.astro:527`).

### Hierarchy
- **Display** (600, `clamp(2.05rem, 1.1rem + 2.6vw, 3.25rem)`, 1.08): the single `h1` — "Judge a decision model on your own workload." It is the title block of the plate, and nothing else on the page uses this size.
- **Headline** (600, `clamp(1.5rem, 1.05rem + 1.5vw, 2.15rem)`, 1.08): section headings and the closing call to action (`--text-section`).
- **Title** (600, `clamp(1.35rem, 1.05rem + 1vw, 1.75rem)`, 1.08): the two panel headings inside the plate, each preceded inline by its journal panel tag.
- **Lead** (400, `1.1875rem`, 1.5): the standfirst under the title and the lede opening each section — the one sentence that says what the section is for.
- **Body** (400, `1rem`, 1.6): all running prose, held to a 58ch measure. Never wider, never justified.
- **Label** (400, `0.6875rem`, 0.09em tracked, uppercase): the measured label — edge codes, nav links, metric chips, captions. The projection toggle tracks slightly wider at 0.11em.
- **Numeric** (400, `1rem`, IBM Plex Mono, `font-variant-numeric: tabular-nums`): every number on the page. Carried by the `.num` utility class, which is applied to stat values, file paths, run ids, metrics, station values and axis readings (`site/src/styles/global.css:98-103`).

### Named Rules
**The Tabular Number Rule.** Every numeral is set in IBM Plex Mono with tabular figures, so a column of readings aligns as a column. A number set in the sans face is a defect.

**The Measured Label Rule.** Small labels are mono, uppercase, tracked and set in tertiary ink — they are the labels a plot puts on its axes and its margin, not decorative captions. They carry measurement names, run ids, providers, file paths and station codes.

## Layout

The page is one 1440px-max column with fluid gutters (`clamp(1rem, 4vw, 3rem)`); every top-level block is the same width, so the sheet reads as one continuous figure rather than a stack of differently-sized sections (`site/src/pages/index.astro:506-510`, `site/src/pages/index.astro:607-612`).

**The plate.** The title block is capped at 64rem so the headline does not run the full 1440px; the frame beneath it is a two-column grid, `minmax(0, 1.5fr)` for panel (a) and `minmax(0, 1fr)` for panel (b), with a single 1px rule between them. Panel (a) is wider because it carries the chart; panel (b) carries the curriculum column. Inside a panel the order is fixed and identical: panel tag + heading, one-sentence promise, then the action and its command, then the demonstration — the actions sit above the demonstrations so both doors are actionable in the first viewport (`site/src/pages/index.astro:124-166`).

**Prose measure.** 58 characters, applied to the standfirst, panel bodies, section ledes, captions, caveats, the closing block and the command block. 58ch rather than the 65-75ch default because the plate is a technical document, and the tighter measure is what keeps a caption legible beside a chart.

**Grids inside sections.** The measurement list is a three-column grid (`3.2rem` index, `1fr` name, `1.1fr` metric and note). The phase list is `3.2rem / 1fr / 4.5rem` with the lesson count right-aligned. The command blocks, course paths and the closing two-column note all use `repeat(auto-fit, minmax(...))` — 19rem, 15rem and 20rem respectively — so they reflow by available width rather than by device (`site/src/pages/index.astro:639-646`, `site/src/pages/index.astro:796-803`, `site/src/pages/index.astro:684-689`).

**Breakpoints** (the only three in the build):
- `1080px` — the plate frame collapses to one column and the divider rule becomes a horizontal rule; the evidence section collapses to one column (`site/src/pages/index.astro:980-993`).
- `760px` — the friction plot takes a 680px floor width and scrolls sideways inside its own frame, with a "Scroll the chart sideways →" hint appearing above it (`site/src/components/FieldPlot.astro:401-409`).
- `720px` — the nav wraps, the mark's sub-line is dropped, and the measurement and phase grids compress their index columns (`site/src/pages/index.astro:995-1022`).

**Vertical rhythm.** Sections are separated by a 1px rule and padded `clamp(2.5rem, 6vw, 5rem)`. Blocks that begin with a hairline use a consistent 0.85rem inset beneath it; the standing gaps are 1.1rem between blocks, 1.35rem between rows, 1.5rem between columns and 2.4rem between a section head and its content.

### Named Rules
**The Plot Keeps Its Width Rule.** A chart is never squeezed to fit. It takes a floor width and scrolls sideways inside its own frame, because a nine-station plot rendered at four-pixel type is the same as an absent plot.

**The One Column Rule.** Sections are one column of full-width bands separated by hairlines. There is no two-column body layout and no sidebar.

## Elevation & Depth

There are no shadows anywhere in the artifact — `box-shadow` appears in no stylesheet. Depth is printed: a hairline rule separates one region from the next, one tonal step (`--color-ground-deep`) lifts the command blocks and the single inverted section, and weight and size carry the rest. The only translucency in the system is the sticky navigation bar, which mixes the ground to 92% over a 6px backdrop blur so the paper stays readable as content passes under it (`site/src/pages/index.astro:445-452`). Focus is the one overlay: a 2px prussian outline at 3px offset (`site/src/styles/global.css:85-89`).

### Shadow Vocabulary
- None. If a future surface needs separation, it uses a 1px rule in `--color-rule` or `--color-rule-soft`, or one step of ground. A shadow is a new token, not an extension of this one.

### Named Rules
**The Hairline Rule.** Separation is drawn with a 1px rule, never with a shadow, never with a soft border, never with a heavier stroke. Every `border-left` in the build is 1px.

**The One Inversion Rule.** The world has exactly one inverted surface: the sticky nav, which is the only translucent element. Ink-on-paper is used for the primary button, and the press state is prussian — that is the whole of the inversion vocabulary. Do not add glass, blur or lifted panels to anything else.

## Shapes

Zero radius, everywhere. Every surface is a square-edged rectangle defined by a 1px hairline; no corner rounding exists in any stylesheet, and no shadow substitutes for one. The single exception is the focus ring, which carries a 1px radius so it does not clip against a square edge (`site/src/styles/global.css:88`).

Fill is either the ground, the deep ground, the prussian tint, or a hatch. The two hatches are the system's only texture and both are 45° line patterns in prussian: a 7px pattern at 0.55 opacity marking the region where a decision crosses the 0.5 threshold (`site/src/components/FieldPlot.astro:127-137`), and a 6px pattern at 1.4 stroke marking the capstone band of the curriculum column (`site/src/components/CourseColumn.astro:87-98`). Hatching is how this world says "look here" without adding a colour.

## Components

### Buttons
- **Shape:** square (radius 0), 1px ink border.
- **Primary:** the only filled control on the page. Ink ground, ground-coloured mono label, padding `0.85rem 1.35rem`, mono at 0.8125rem. It is a link styled as a control, so it carries the action label and its own arrow.
- **Hover / Focus:** background and border cross-fade to prussian over 140ms with white text; the arrow slides 3px to the right over 180ms. Focus is the global 2px prussian outline at 3px offset.
- **Secondary / Ghost:** there is none. Every other call to action is a text link with a 1px underline in `--color-rule` that turns prussian on hover (`site/src/pages/index.astro:899-911`).

### Toggle options
- **Style:** hairline boxes, never pills. Transparent ground, 1px rule border, mono micro label uppercase at 0.11em tracking, tertiary ink.
- **State:** the pressed option inverts to ink ground with ground-coloured text; the unpressed options stay transparent. `aria-pressed` carries the state, and the same state is echoed in the chart and the readout.
- **Focus:** 2px prussian outline at 2px offset.

### Command block
- **Style:** the deep ground, a 1px rule, mono at 0.8125rem, padding `0.7rem 0.9rem`. A dimmed `$` prompt sits at the baseline ahead of the command; the command itself is `white-space: pre` and the block scrolls horizontally rather than wrapping.
- **Use:** only for a command the reader can copy, always immediately under an edge code that names what the command does.

### Edge code
- **Style:** the system's label primitive — mono, 0.6875rem, uppercase, 0.09em tracked, tertiary ink. It names a data object (`run 20261027-212313-friction-mock · provider mock`), a file (`raw calls`), a step (`1 - see what is configured on this machine`) or a figure.

### Metric chip
- **Style:** prussian on the prussian tint, mono micro, padding `0.2rem 0.5rem`. It names the metric that answers the question — `ECE + Brier`, `action_change_rate`.

### Stat readout
- **Style:** a 1px rule on top, then a tabular number at `clamp(2rem, 1.2rem + 2.4vw, 3rem)`, line-height 1, tracking -0.02em, then a label in secondary ink capped at 34ch.
- **Note:** a stat is a reading with a label, never the hero-metric template — there is no supporting-stat cluster and no accent behind it.

### Navigation
- **Style:** a sticky hairline bar, mark and links on one baseline. The mark is the wordmark in weight 600 plus a mono micro sub-line ("the neutral harness"); the links are mono micro uppercase in secondary ink with a 1px transparent underline that turns prussian on hover.
- **Mobile:** the bar wraps, the links wrap with it, and the mark's sub-line is dropped.

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
- **Style:** a 1px prussian left border with 1.1rem of left padding, secondary ink, 58ch, with the leading clause in ink weight 600. Inline with a figure, the same caveat loses the stripe and uses a 1px rule on top instead (`site/src/pages/index.astro:702-724`).

## Do's and Don'ts

### Do:
- **Do** set every number in IBM Plex Mono with tabular figures, and always beside the token counts or units that give it meaning.
- **Do** separate regions with a 1px rule in `--color-rule` (or `--color-rule-soft` for a row inside a list), and keep prose to a 58ch measure.
- **Do** put provenance next to the data: the run id, the provider and the file path as edge codes, and the simulated-run note on the face of every plotted number.
- **Do** keep panel labels in the journal convention — `(a)` and `(b)`, set inline with the heading they belong to.
- **Do** use prussian tint as the fill under prussian text (a metric chip, a curriculum band) rather than inventing a new surface colour.
- **Do** give a chart a floor width and let it scroll sideways inside its own frame.
- **Do** write the edge code that names a data object in mono, uppercase, tracked, tertiary ink.

### Don't:
- **Don't** introduce a second accent hue, a gradient, a tinted overlay, or any fill other than the ground, the deep ground, the prussian tint or a prussian hatch.
- **Don't** add a shadow, a glow, a lifted card, a rounded corner, or a soft border to separate anything.
- **Don't** put a kicker, an eyebrow or a decorative label above a heading. The edge code is for data objects and captions, never as a preamble to a title.
- **Don't** number sections decoratively. The two numeric indexes that exist are list positions (the measurement ordinal) and curriculum phase ids — both carry information the reader needs.
- **Don't** build an icon system out of glyphs or emoji. The one arrow in the system is a typographic `→` set in the mono face, meaning direction; anything else must be authored SVG.
- **Don't** squeeze a chart to fit, and don't stack competing numbers on one surface — one reading at a time, with the selected one in ink.
- **Don't** let a simulator number stand in for a model measurement, on the page or in a caption.

### Not canonized (known drift — do not inherit these as rules)
- **`--color-rule-soft` is duplicated and diverged.** The token is `#dfe7ec` (`site/src/styles/global.css:15`), but the friction field hard-codes a local `RULE_SOFT = '#e6edf1'` for its SVG grid lines (`site/src/components/FieldPlot.astro:33`). Two values are in play for one rule; this is drift, not a second rule, and it is not repaired here.
- **`--color-ink-70` and `--color-ink-45` are opaque, not alpha.** The names read like opacity steps, but both are solid hexes. Treat them as two named inks; do not compose them at 70% or 45% alpha over the ground.
- **Graphite is below the non-text contrast bar.** Graphite on the ground is 2.73:1, under the 3:1 threshold for meaningful graphics. It is used only for simulated, unselected series, and the selected series is always ink — but a future surface that plots live data in graphite would be repeating a legibility defect, not a rule.
- **The nav's translucent blur is the world's single reserved inversion, not a general treatment.** It is recorded here so that no future surface inherits glass as a system habit.
