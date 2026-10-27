# Lesson format - the contract for every lesson in the Academy

Every lesson is **one markdown file** in `course/lessons/`, named
`<id>-<slug>.md`, plus **one quiz file** in `course/quizzes/<id>.json`.

The lesson file is the source of truth. `course/curriculum.json` is generated
from the lesson files by `python tools/course_check.py --index`, and
`python tools/course_check.py --check` fails the build if the two disagree.

## Front matter

```markdown
---
id: L12
phase: 1
title: "Softmax - from raw scores to probabilities"
minutes: 30
concepts: [logits, softmax, normalisation, numerical-stability]
prereqs: [L10, L11]
paths: [beginner, foundations]
exercise_file: exercises/L12_softmax.py
quiz: L12
---
```

| key | meaning |
|---|---|
| `id` | `L` + a number, unique, and the filename must start with this id |
| `phase` | 0-9, must be a known phase (see `PHASE_TITLES` in `tools/course_lib.py`) |
| `order` | optional. Position **within** the phase. Lessons sort by `(phase, order, filename)`, so without it they sort by id. Use it when a phase teaches a concept out of id order - Phase 0 puts the data-shapes lesson (`L10`) second, before the wire protocol, because you cannot read a JSON contract before you know what a dict is |
| `title` | one line, plain language, no jargon in the title |
| `minutes` | a positive integer - the honest estimate for the learner |
| `concepts` | the concept names this lesson teaches. These are the unit of mastery tracking |
| `prereqs` | lesson ids that must come first. They must exist, and they must come **earlier in the order** - a lesson may never depend on a later one |
| `paths` | any of `beginner`, `foundations`, `provider-live` - at least one |
| `exercise_file` | where the learner writes. Either an existing repo file, or a new path under `exercises/` or `docs/notes/` |
| `quiz` | must equal the lesson id |

## Body sections - all eight, in this order

The order is not decoration. It is the Feynman shape: hook the learner with
why it matters, give a story they can hold, show the story break, give the
real thing, point at where the repo uses it, then hand over the pen.

| section | what goes in it |
|---|---|
| `## Why this matters` | 2-4 sentences tying this to the repo or the product. Never "this is important because it is important". |
| `## The naive story` | A story, analogy or worked intuition a total beginner can picture. No equations here. |
| `## What breaks` | 2-3 named breaks: where the naive story fails, and what the failure looks like in practice |
| `## The real thing` | The precise definition. Equations are allowed here, walked through step by step. |
| `## In this repo` | Concrete `file` and `function` pointers. Name the real code. |
| `## Your turn` | The exercise spec: the file, the function names, the inputs, the expected output, one hint |
| `## Check yourself` | 3-4 questions the learner answers in their own words, with no answers shown |
| `## Artifact` | The one thing the learner publishes. A file path and what it must contain |

## The optional `## The story` section

The illustrated course adds one section, between `## What breaks` and
`## The real thing`: the naive story breaks, the story makes the real thing
imaginable, and then the real thing gets named.

- **120 to 220 words.**
- **First principles.** Start from something the learner already understands
  and build the concept out of it. Never "in machine learning, we...".
- **A person or a thing doing something.** "A support desk", "a scale with a
  needle", "a door with a threshold" count. Abstract nouns do not.
- **No new claims.** Every fact in the story is already true somewhere in the
  lesson or the repo.
- **No invented numbers.** If you need a number, it is already in the lesson.

The gate checks that the eight required sections are present and in order.
It does not forbid extra sections, and `## The story` is the one that
belongs. `python tools/check_course_figures.py` checks the story's word band
and the lesson's diagram and picture; see `site/FIGURES.md` for those rules
and `docs/figures-and-stories.md` for the commands.

## The hard rule on exercises

**Never write the learner's exercise implementation.** Not in the lesson, not
in the quiz, not in an example. The `## Your turn` section states the file,
the function names, the inputs, the expected output and one hint. It stops
there.

A hint points at the *concept*, never at the code. "The stable version
differs from the naive version by exactly one line, placed before the
exponentials" is a good hint. "Write `shifted = [x - max(x) for x in scores]`"
is not - that is the answer.

## Quiz files

```json
{
  "lesson_id": "L12",
  "title": "Softmax - from raw scores to probabilities",
  "questions": [
    {
      "id": "L12.q1",
      "concept": "numerical-stability",
      "prompt": "Why does the stable softmax subtract the maximum score?",
      "options": ["wrong", "right", "wrong", "wrong"],
      "answer": 1,
      "explain": "Because ... and here is why the other three are wrong."
    }
  ]
}
```

Rules the gate enforces:

- at least 3 questions
- `answer` is a **zero-based index** into `options`
- every question has a non-empty `prompt` and `explain`
- every question's `concept` is listed in the lesson's `concepts`
- no duplicate options in one question
- the correct option must not always be in the same position - vary it

The `explain` is the teaching moment: it must say **why the right answer is
right**, and ideally why the tempting wrong answer is wrong. A learner who
fails a question and reads the explanation should be able to answer it
correctly next time.

## Answer isolation

The quiz's `answer` index must never reach the learner before they have
answered. Two mechanisms enforce this:

1. the agent asks all questions first, then calls
   `python tools/learn_state.py grade <id> --answers 1,0,2`
2. `grade` prints the verdicts and explanations only after every answer has
   been submitted

## Paths

- `beginner` - the absolute-beginner route. Assumes no LLM knowledge at all.
  Starts from "what even is this".
- `foundations` - the maths route. Softmax, temperature, attention, training.
- `provider-live` - the hands-on route. Real providers, real cost, real
  evidence.

A lesson may be in more than one path. Every lesson must be in at least one.
