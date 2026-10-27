# The message format

The house shape of a commit message in this repository. `tools/check_commit.py`
enforces the parts that can be checked by a machine; the rest is judgement.

```
<Prose subject: what changed, under 72 characters, no trailing period>

<One paragraph. What changed, and why a reader who has never opened this file
would care. Name the mechanism, not the file list.>

Workstream: <name> - <the bounded piece of work this commit carries>
Files: <n> files, <what they are, in a few words>

Gates:
  - <command> -> <what it printed>
```

## The subject

- Under 72 characters, so it survives a terminal and a GitHub list.
- Prose, not a label. "Teach the format-friction lesson" beats "feat(L61): add
  figure".
- No trailing period, no emoji, no ticket prefix.
- Not a placeholder: `wip`, `fix`, `update`, `temp`, `asdf`, `...`, `test`.

## The paragraph

One paragraph. Say what the change *does*, not what it *is*. "The friction
lesson now shows one ticket in three shapes crossing one threshold" says more
than "updated L61.md and added L61.astro".

If the change fixes a bug, say what was wrong and what it does now. If it
replaces something, say what the old thing got wrong.

## The Workstream line

Name the bounded piece of work. In this repository the workstreams are the
phases of the illustrated course (`A` to `H`), the named fixes
(`motion primitive`, `figure strokes`, `gate`), and the standalone pieces
(`release post skill`, `the site`).

This line is the index into `docs/figures-and-stories.md`, where the ownership
map says who owns which files. A future developer reading the history can jump
from the log to the ownership map and know exactly which agent's work this was.

## The Gates section

The commands you ran and what they printed. A reader must be able to re-run
them and get the same answer.

```
Gates:
  - python tools/check_course_figures.py -> 46 lessons, 0 problems
  - cd site && npm run build -> 48 pages
  - python tools/check_site_a11y.py -> 48 pages, 0 problems
```

One line per gate. If a gate is a long command, name the file it runs rather
than pasting the whole invocation.

## Worked examples

A workstream that produced a lesson's three artifacts:

```
Illustrate the format-friction lesson: a story, a diagram and a picture

The friction lesson is the course's centrepiece - one ticket, three shapes,
one threshold - and it was the one lesson that still had no picture. The
story builds the effect from a support desk, the diagram draws the three
serialisations arriving at one probability scale, and the picture is a desk
with three slips of paper on it.

Workstream: C - the illustrated course, phases 5 to 7
Files: 3 files - one lesson, one figure component, one illustration

Gates:
  - python tools/check_course_figures.py -> no problem for L61
  - cd site && npm run build -> 48 pages
  - python tools/check_site_a11y.py -> 48 pages, 0 problems
```

A fix found by an audit:

```
Give the motion primitive the delay it was missing

Every other primitive read --m-delay. .m-draw had no animation-delay line at
all, so 25 elements fired at once and seven figures whose <desc> said "the
arrows draw themselves in turn" showed them all arriving together. One line
fixes it, and the reduced-motion block now paints the whole stroke instead of
a dash-length fragment of it.

Workstream: motion primitive - the shared CSS
Files: 1 file - site/src/styles/global.css

Gates:
  - node site/scripts/measure_mdraw.mjs -> 25 elements, 0 short
  - cd site && npm run build -> 48 pages
```

## What the hook will reject

- a subject over 72 characters, or with a trailing period
- a placeholder subject
- a commit that touches lesson, figure or illustration files without a
  `Workstream:` line in the body
- a commit that touches more than three files without a `Gates:` section
- a body that says "Workstream:" with an empty name
