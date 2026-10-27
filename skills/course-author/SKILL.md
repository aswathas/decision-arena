---
name: course-author
description: >
  Maintain Decision Arena Academy - add a lesson, extend a phase, write a quiz,
  fix a broken lesson reference, or keep course/curriculum.json in sync with the
  lesson files. Use when the learner or another agent wants to change the
  course itself rather than study it: "add a lesson about X", "this lesson
  points at a file that moved", "the course check fails".
---

# Course Author - maintaining the Academy

The course is teaching material, so it is held to a higher standard than
ordinary docs: a broken lesson is worse than a missing one, because a learner
trusts it.

**Never delete a lesson.** Archive it (move it out of `course/lessons/` into
`course/archive/`) and leave a note. The repo rule - never delete, archive
only - applies to teaching material too.

## The one rule that is not negotiable

> **A lesson may never contain the implementation of its own exercise.**

The learner writes the code. If a lesson shows the answer, the lesson is
worthless and the learner learns nothing. If you author a lesson, you specify
the exercise; you do not solve it.

## Adding a lesson

1. **Pick the id.** `L` + the next free number in the phase, two digits
   (`L15`, not `L9`). The filename must start with the id: `L15-<slug>.md`.
2. **Pick the phase.** Read `PHASE_TITLES` in `tools/course_lib.py`. If the
   lesson does not fit any phase, add the phase there first, with a title.
3. **Pick the position.** Lessons sort by `(phase, order, filename)`. If the
   new lesson must come before an existing one inside the same phase, give
   both lessons an explicit `order` key rather than renaming ids.
4. **Write the front matter.** Use `course/FORMAT.md` as the contract. Every
   key is required. `prereqs` must point at lessons that exist **and come
   earlier in the order** - a lesson may never depend on a later one.
   `paths` must be a non-empty subset of `beginner`, `foundations`,
   `provider-live`.
5. **Write the body.** All eight sections, in order, with the Feynman arc:
   *Why this matters -> The naive story -> What breaks -> The real thing ->
   In this repo -> Your turn -> Check yourself -> Artifact*.
   - "In this repo" must cite **real** files and **real** function names.
     Read the code before you name it.
   - "Your turn" names the file, the functions, the inputs, the expected
     output, and ONE concept-level hint. No implementation.
6. **Write the quiz** in `course/quizzes/<id>.json`: 3 to 4 questions, a
   zero-based `answer` index, and an `explain` that says why the right answer
   is right **and** why the tempting wrong answer is wrong. Vary which index
   is correct - never always 0.
7. **Regenerate the index and run the gate:**

```bash
python tools/course_check.py --index
python tools/course_check.py --check
```

The gate fails on: missing front-matter keys, duplicate ids, unknown phases,
unknown paths, missing or empty sections, sections out of order, an
`exercise_file` that does not exist outside `exercises/` and `docs/notes/`, a
missing or malformed quiz, a prereq that does not exist or that comes later in
the order, and a stale `course/curriculum.json`.

## Changing an existing lesson

- **Do not delete a section.** If a concept is no longer taught here, say so
  in the section rather than removing it - a learner who read the old version
  keeps reading it.
- **Keep the ids stable.** Renaming `L12` breaks every prereq, every build-log
  entry and every progress record that mentions it.
- **After any edit:** `python tools/course_check.py --index` then
  `--check`.

## Voice rules

The learner is an absolute beginner who knows nothing about LLMs.

- No jargon without a definition in the same breath.
- Concrete numbers before general rules.
- Name a real file and a real function instead of "in the codebase".
- Say what the thing **costs** - the risk, the money, the effort. A beginner
  needs to know why a decision matters before the mechanics.
- Never state a fact about a provider (Jev, Clef, Laya), a price, or an API
  shape from memory. Read it out of the repo, or say it is uncertain.

## Adding a phase

1. Add the phase title to `PHASE_TITLES` in `tools/course_lib.py`.
2. Add at least one lesson in that phase.
3. Update `course/README.md` with the phase's one-line purpose.
4. Run the gate.

## The gate is the CI

`tools/course_check.py --check` must pass before any commit that touches
`course/`. It is the same discipline as the repo's link gate: a broken
reference is a build failure, not a warning.
