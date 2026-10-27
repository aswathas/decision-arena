---
version: 1
slug: "site-src-pages-index-astro"
primary_target: "site/src/pages/index.astro"
related_targets: []
---

# Surface brief - decision-arena site

**Scope.** The public site for the `decision-arena` repository. One entry
surface: the landing page at `site/src/pages/index.astro`. It is the front
door to two things that live in the same repo - the Decision Arena Academy
course and the measurement harness the course builds - and it must make both
legible in a single viewport.

**Visitor mode.** Persuade. The visitor must decide and act.

**Audience.** Engineers choosing between decision-model vendors (TypeSafe
Jev, Cloudflare Clef, local Laya). They are technical, they can run a
terminal, they are sceptical, and they have already seen two vendor
benchmark tables that disagree with each other. Their job: decide on
evidence, and be able to defend the decision.

**Job / action.** Two equal doors, because the reader's state is unknown on
arrival and both are legitimate next moves. **Door (a) - measure:** run the
battery yourself and get comparable evidence across providers; the action is
*run it now*, one command. **Door (b) - learn:** take the course and learn
to read what the harness prints; the action is *start lesson one*, ten
minutes, no credentials. Neither door is subordinate: each panel carries its
own promise, its own demonstration and its own primary action.

**Proof and content (all real, nothing invented).** The committed run files
in `runs/` - including a real friction run with mean spread 0.42, max
spread 0.9271 and 4 of 9 questions flipping at 0.5, produced by the offline
simulator and labelled as such on its face. The 46-lesson course with its
46 quizzes and a passing course gate. `docs/decision-log.md`. Vendor pricing
verified against vendor pages on 2026-10-25 (clef $0.24/Mtok, clef-flash
$0.038/Mtok, jev $0.042/Mtok). The claims ledger's VERIFIED / CLAIM /
UNCERTAIN / CONFLICT labelling. No live provider has been measured, and the
page says so in its own words rather than letting a simulator number stand
in for a model measurement.

**Constraints.** The library is stdlib-only, so the site is plain and
dependency-light; a reader must be able to reproduce a finding for under
$1. The mock is never evidence, and the site must never let a reader
confuse a simulator number with a model measurement. No secret, credential
or private path may appear - the repository is public. Apache-2.0. The site
makes no third-party runtime request: the two typefaces are self-hosted
woff2 files under `site/public/fonts/`, vendored by `tools/vendor_fonts.py`.

**Chosen direction.** *The Analysis Chart* - the printed technical plot, the
lineage from the synoptic analysis chart through the contour map to the
engineer's data plot. The site is a plot, not a brochure about a plot. The
product's one idea is a probability field that moves when you change nothing
but the shape of the input, and a technical plot is the honest form for that
idea; the reader can see the mechanism instead of being told about it.

**Memorable moment.** The projection toggle. One real support ticket, three
serialisations - prose, flat JSON, nested JSON - and the probability that
comes back. The chart cross-fades between them, and the region where the
decision actually crosses the threshold is filled with a hatch, so the
flip is visible rather than described. This is the only authored motion on
the page; everything else is still.

## Direction contract

**THESIS.** A vendor's benchmark table is a picture of the weather, not the
weather. This site opens on a figure plate carrying two panels, because
there are two honest next moves and the reader's state is unknown on
arrival: run the battery yourself, or learn to read what it prints. The
category default for a developer tool is a hero headline, three feature
cards and a button; this refuses that arrangement and makes the plate the
largest thing on the screen, with both offers and both actions carried
inside it.

**OWN-WORLD.** The printed technical plot. Ground: cool plot-paper white
with a faint blue cast - never cream, never warm. Ink: near-black with a
blue cast. One committed data colour (prussian indigo); graphite for
simulated data. Hairline rules only: no soft borders, no shadows on data,
no rounded cards, no icon tiles, no gradients. Prose in a technical grotesk
with drafting character; every number in tabular monospace, because the
numbers are the product. No serif anywhere. A figure plate: a hairline
frame, panel labels in the journal convention - (a), (b) - and a shared
caption rule, not two floating cards.

**STORY.** The visitor arrives holding two vendor tables that disagree. In
one viewport they see both ways forward. Panel (a) shows the mechanism
actually running: one ticket, three shapes, a probability that moves, and
the run file behind it - so they learn that the shape of your input is a
hidden hyperparameter, that it costs real decisions, and that a raw file is
the only honest proof. Panel (b) shows the other way: ten phases, forty-six
lessons, ending in a finding they published. Both are the same kind of
object on the same sheet, because the harness and the course are the same
artefact in this repo. The visitor leaves knowing the site is not asking
them to trust it.

**FIRST VIEWPORT.** One figure plate, hairline-framed, filling the width.
Above it a title block: the offer in one sentence, and one line naming the
two doors. Between the title block and the frame sits the shared caption
strip - a title strip, not a footer - carrying the two edge codes: (a) the
run id, the provider, and the three raw-evidence files in `runs/`; (b) the
lesson and quiz counts and the passing course gate. Inside the plate, two
panels divided by a single hairline rule, in the journal convention.
Panel (a), the wider, is the format-friction field for one real ticket -
three serialisations, a hairline threshold rule across the field, readings
in tabular monospace, and a printed note that the run is simulated; on a
narrow screen the plot keeps its width and scrolls sideways inside its own
frame instead of shrinking into illegibility. Panel (b), the narrower, is
the curriculum plotted as a stratigraphic column: ten bands, one per phase,
band thickness equal to its lesson count, labelled with the phase title,
ending in the capstone band that publishes a finding. In each panel the
order is fixed and the same: the panel label - (a) measure, (b) learn -
then the one-sentence promise, then the primary action and its command,
then the demonstration. The actions sit above the demonstrations, so both
doors are actionable and the caption is legible without scrolling at
1440x900. Both actions are set in the same ink-on-paper button style, so
the two doors are equal. No card row, no split hero, no eyebrow label above
the heading.

**FORM.** *The Analysis Chart*. Position 6 on my grounded list of seven
(evidence grading / formulary, audit ledger, referee's apparatus, shot
group dispersion, calibration institute, synoptic analysis chart, signal
trace). The roll assigned it: seed key `697188c0`, approved pool
`c3b204a1eed6`, assigned index 6. Challenger verdicts: the bench
instrument, the ikeda data field and the nixie counter are **competitive**
(alternate full cards, each holding one axis); game boy, 16mm film and the
indoor sun are **declined**. Raises folded into this direction, each named
by its donor: *ink purity* (from ikeda) - hairlines only, and one inversion
state reserved; *one reading at a time* (from the bench instrument) - each
metric is a single legible readout, never a field of competing numbers;
*edge codes* (from 16mm film) - every plotted value carries a small caption
naming the run file it came from, so provenance is printed in the margin;
*the mirror* (from the indoor sun) - the second provider's field is printed
as a reflection beneath the first, so a comparison is never a legend lookup.
Code-led build: no image generation is available on this machine, so the comp
round is skipped by contract and the ambition lives in the FIRST VIEWPORT
block and the named signature interaction.

**FINISH.** unreviewed and undocumented is unfinished; this build ends with
the finish review, the verdict, DESIGN.md, and every shipping raster
carrying its provenance

## Unresolved decisions

- Whether the site is deployed publicly is a separate decision, taken at
  deploy time, not here.
- The reader's job was confirmed as "evaluate vendors" while the site's
  centre of gravity was given loosely as a "course site". The brief resolves
  that as **two equal doors**: the course is the spine of the repository, the
  harness is its proof, and the landing page offers both on one sheet rather
  than making either the subordinate section.
