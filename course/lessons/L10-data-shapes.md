---
id: L10
phase: 0
order: 2
title: "Lists, dicts and floats - the shapes you handle all course"
minutes: 35
concepts: [python-data-shapes, dicts, lists, indexing]
prereqs: []
paths: [beginner, foundations]
exercise_file: exercises/L10_shapes.py
quiz: L10
---

# L10 - Lists, dicts and floats - the shapes you handle all course

## Why this matters

Before you can read a run file you need to know what a JSON object turns into
in Python, and how to pull the one value you want out of it. Everything in this
course - the questions, the answers, the probabilities, the case files - is
built out of exactly three things: **dicts**, **lists** and **floats**. Get
comfortable with them here and the rest of the course is bookkeeping.

## The naive story

JSON is the wire format. When you read a JSON file with `json.load(...)`,
you get Python objects back. The mapping is one-to-one and boring on purpose:

| JSON | Python |
|---|---|
| `{"a": 1}` | `dict` |
| `[1, 2]` | `list` |
| `1.5` | `float` |
| `"text"` | `str` |
| `true` / `false` | `bool` |
| `null` | `None` |

A dict is a labelled box: you open it by name. A list is a numbered row: you
open it by position. That is the whole difference, and it decides how you index
each one.

## What breaks

**Break 1 - the same key name means different things in different questions.**
In `cases/routing.json` the `team` question has `"criteria": {"billing": "...",
"technical": "..."}` - a **dict**, so the option names are the *keys*. The
`severity` question has `"criteria": ["No impact", "Minor", "Major",
"Critical"]` - a **list**, so the option names are the *positions*. Write
`question["criteria"]["billing"]` on the score question and you get a
`KeyError`; write `question["criteria"][0]` on the choice question and you get
the first *key*, which is a string, not the thing you wanted. Always check the
type of the value before you index it.

**Break 2 - dicts keep their order, but only in modern Python.** Python 3.7
guarantees that dicts preserve insertion order, so the teams come out
`billing, technical, sales, other` every time. That is why the repo can treat
the criteria dict as an ordered list of options without ever sorting it. If
you ever *do* need an explicit order, sort it yourself - but know that the
order is already there.

**Break 3 - a float is not the number you typed.** `0.1` cannot be written
exactly in binary. So `0.1 + 0.2` is `0.30000000000000004`, and
`0.1 + 0.2 == 0.3` is **False**. That is not a Python bug, it is the price of
base-2 floating point. Lesson L11 is entirely about this, and it will bite
you the moment you write an `assert` on a probability.

**Break 4 - a value can be missing.** `.get(key)` gives you `None` when the
key is absent; `dict[key]` raises `KeyError`. The repo uses both on purpose:
`normalise_answers()` uses `a.get("probabilities") or {}` so a provider that
omits the distribution still produces a valid answer, while
`metrics.collect_scored()` uses `answers_by_qid.get(qid)` and skips the
question if it is missing.

**Break 5 - not every state is a string.** In `cases/routing.json` the state
is a plain sentence. In `cases/format_variants.json` the state is a dict
(`"flat"`) or a dict of dicts (`"nested"`). The harness never converts it.
`MockProvider._detect_format()` branches on `isinstance(state, dict)` and
looks at the *values* to decide whether the shape is "flat" or "nested" - that
is how the format-friction experiment knows which shape it is looking at.

## The story

Imagine a warehouse with two kinds of shelf. The first is a set of labelled
drawers: you open a drawer by pulling the tab marked "billing", and you do
not care which drawer is highest. The second is a long numbered rail:
parcels stand in a row and you take the third by counting - the first is at
position 0, the second at 1, the third at 2.

Same shelf, two ways in. Pull the wrong tab on the rail and you get a
surprise: the first thing in the row comes back, a string, and nothing tells
you that was not what you wanted. Reach for a missing name and you get an
error and you stop. The quiet failure is the dangerous one.

The parcels also carry prices, and here the shelf lies a little. A tag
reading 0.1 grams and another reading 0.2 grams weigh 0.30000000000000004
grams together, not 0.3. Nothing is broken and no parcel is wrong; the
weighing machine just cannot hold those numbers exactly. So the warehouse
checks its totals against a tolerance it chose on purpose rather than
insisting the digits match.

Everything in this course is one of these two shelves, plus the numbers
printed on them. Learn to open each one the right way and the rest is
bookkeeping.

## The real thing

The three shapes, and how you get into them.

**Dict - open by name.**
```
questions = {"team": {"type": "choice", "criteria": {"billing": "...", "other": "..."}}}
questions["team"]                    -> the inner dict
questions["team"]["type"]           -> "choice"
questions["team"]["criteria"]["other"] -> "..."
questions.get("team", {})            -> the inner dict, or {} if absent
list(questions.keys())              -> ["team"]
for qid, q in questions.items(): ...  # iterate label and value together
```

**List - open by position, counting from zero.**
```
levels = ["No impact", "Minor", "Major", "Critical"]
levels[0]    -> "No impact"
levels[3]    -> "Critical"
levels[99]   -> IndexError
levels[-1]   -> "Critical"   (counting from the end)
levels[0:2]  -> ["No impact", "Minor"]   (a slice, end excluded)
```

**Float - a number with a memory limit.**
```
0.1 + 0.2            -> 0.30000000000000004
round(0.1 + 0.2, 4)  -> 0.3
abs(a - b) < 1e-9    -> the way this repo compares numbers
```

**The three shapes in the places you will meet them this course:**

| where | the shape |
|---|---|
| `questions` | dict of dicts, keyed by question id |
| `criteria` | dict for `choice`, list for `score` |
| `gold` | dict of bool / str / int, keyed by question id |
| `answers` (normalised) | dict of dicts with keys `kind`, `value`, `probabilities`, `confidence` |
| `probabilities` | dict of floats, keyed by option key (or by the *string* form of a score index) |
| `state` | a string, or a dict - it depends on the case file |

**One trap worth naming early:** for a `score` question the `probabilities` dict
is keyed by the **string** form of the index - `{"0": 0.1, "1": 0.1, "2": 0.7,
"3": 0.1}` - not by the number `2`. That is why `metrics.collect_scored()` does
`dist.get(str(int(gold_value)), 0.0)`. `dict.get(2)` will not find `dist["2"]`
... but `str(int(...))` will find it, and the try/except around it keeps a
weird gold value from crashing the run.

## In this repo

- `decisionarena/harness.py` - `load_cases()` shows the JSON-to-Python
  mapping in practice: a `.json` file is loaded with `json.load`, and if the
  top level is a dict it takes `data["cases"]`, otherwise the top-level list
  is used as-is.
- `cases/routing.json` - one case, all the shapes: `state` is a string,
  `questions` is a dict of three question types, `criteria` is a dict for
  `team` and a list for `severity`, `gold` holds a bool, a string and an int.
- `cases/format_variants.json` - `variants` holds the same content in three
  shapes: a string, a flat dict, and a nested dict.
- `decisionarena/providers.py` - `normalise_answers()` builds the normalised
  dict-of-dicts, and `MockProvider._detect_format()` uses `isinstance()` to
  tell the state shapes apart.
- `decisionarena/metrics.py` - `collect_scored()` is the best tour of the
  shapes in the repo: it reads `a["kind"]`, then either `a["value"]` or
  `a["probabilities"]`, and writes rows of plain dicts.
- `examples/00_read_the_code.py` - step 5 builds the three question types by
  hand and prints `a['kind']`, `a['value']` and `a['confidence']` for each.

## Your turn

Write a file `exercises/L10_shapes.py` that contains:

- a function `question_types(questions: dict) -> list[str]` that returns the
  sorted, unique list of the `type` values in a questions dict.
- a function `option_keys(questions: dict) -> dict[str, list[str]]` that, for
  every question whose `type` is `"choice"`, returns the option keys in the
  order they appear in the `criteria` dict. Questions of other types are not
  included in the result.
- a function `criteria_kind(question: dict) -> str` that returns `"dict"` if
  the question's `criteria` is a dict, `"list"` if it is a list, and `"none"`
  if it has no `criteria` at all.
- a function `nth_option(questions: dict, qid: str, n: int) -> str` that
  returns the n-th (zero-based) option key of a `choice` question, and raises
  `IndexError` when `n` is out of range.
- a function `gold_kind(gold: dict) -> dict[str, str]` that maps each
  question id to the **name of the Python type** of its gold value: `"bool"`,
  `"str"`, `"int"` or `"float"`.
- a `main()` that loads `cases/routing.json` with `json.load` (the file is a
  dict with a `"cases"` list) and prints:
  - the sorted question types
  - the option keys for every choice question
  - the `criteria_kind` of every question
  - the first and last option key of the `team` question
  - the gold kinds
- a self-check section using `assert` that fails loudly if:
  - the sorted question types are not exactly `["choice", "noul", "score"]`
  - the option keys of `team` are not exactly `["billing", "technical",
    "sales", "other"]`
  - `criteria_kind` of the `severity` question is not `"list"`
  - `gold_kind` of `is_billing` is not `"bool"`
  - calling `nth_option` with an out-of-range index does **not** raise
    `IndexError` (catch it and fail the assert instead)

Inputs: `cases/routing.json`. Expected output: the three type names, four
option keys for `team`, one `criteria_kind` per question, and three gold
kinds.

**Hint:** the type of the value inside `criteria` tells you how to index it,
and the type of the gold value tells you the question kind - `bool` is a
`noul`, `str` is a `choice`, `int` is a `score`. One trap when you write
`gold_kind`: in Python a `bool` **is** a subclass of `int`, so check for
`bool` before you check for `int`, or every yes/no gold will come back as an
integer. Dict iteration order is the order the keys were inserted, so the
option list needs no sorting.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why can you index the `criteria` of a `choice` question by key and the
   `criteria` of a `score` question by position, and what breaks if you mix
   them up?
2. What is the difference between `d["k"]` and `d.get("k")`, and which one
   does `normalise_answers()` use on `probabilities`?
3. Why is `0.1 + 0.2 == 0.3` False in Python? (You do not need the full
   binary explanation yet - L11 goes deeper.)

## Artifact

Write `docs/notes/L10-data-shapes.md` - under 250 words, aimed at someone who
knows Python but has never read this repo. It must contain:

- a small table mapping five shapes used in this repo (questions, criteria,
  gold, answers, probabilities) to the Python type they become
- one sentence on why `criteria` is sometimes a dict and sometimes a list
- one concrete snippet of real JSON from `cases/routing.json` and the Python
  value it turns into

Then commit it. The artifact is the proof that you can read a case file and
know what type every part is.
