---
id: L01
phase: 0
order: 3
title: "The three question types - noul, choice, score"
minutes: 30
concepts: [noul, choice, score, decision-types]
prereqs: [L00, L10]
paths: [beginner, provider-live]
exercise_file: exercises/L01_question_types.py
quiz: L01
---

# L01 - The three question types - noul, choice, score

## Why this matters

Every question in this repo is exactly one of three types, and each one is
measured differently. If you cannot tell a `noul` from a `choice` by looking at
a raw provider answer, you cannot read a run file, and you cannot tell whether
a number in a report means what you think it means.

## The naive story

Imagine you are building a form for a support desk. You need three things from
the model: a yes/no flag, a pick-one-from-a-list, and a severity. That feels
like three different features of three different systems, and you would
probably reach for three different APIs to get them.

But look at the actual question objects in `cases/routing.json`. They are all
the same *shape*: a `type`, an `instructions` string, and - where it makes
sense - a `criteria` list of the allowed options. The type is the only thing
that changes what the answer looks like.

## What breaks

**Break 1 - the names look like typos.** `noul` is not a misspelling of
"null", and it is not a typo for "no". It is the wire keyword this repo uses
for a yes/no judgement on some surfaces. The `decisionarena/providers.py`
docstring says it plainly: "`noul` is the wire keyword for a yes/no judgement
on some surfaces. The Vercel AI Gateway calls the same thing `boolean` and
rejects `noul`, so normalise_helpers() translates at the adapter boundary."

So the same idea has two names in the wild:

| our name | what it means | who else calls it |
|---|---|---|
| `noul` | yes / no judgement | TypeSafe Jev, Cloudflare Clef |
| `boolean` | yes / no judgement | the Vercel AI Gateway |

The harness always speaks `noul` internally. The adapter translates at the
boundary, so the metrics never have to care which vendor you paid.

**Break 2 - `choice` and `score` look identical from the outside and are not.**
Both are "pick one of N". The difference is in the **shape of the answer**:

- `choice` answers with a **label** - the string `"billing"` - plus a
  probability for every option.
- `score` answers with a **number** - `1.0` - which is the *index* into the
  ordered `criteria` list. In `cases/routing.json` the severity criteria are
  `["No impact", "Minor", "Major", "Critical"]`, so `1` means "Minor". The
  gold label for that question is also `1`.

The score's options are **ordered** (level 0 to level 3) and the model can be
"one step off". The choice's options are **unordered** and being wrong means
being wrong.

**Break 3 - the gold answer tells you the type, if you look at its Python
type.** In `cases/routing.json` the gold block for `routing-001` is
`{"is_billing": true, "team": "billing", "severity": 1}`. A `bool` gold is a
`noul`. A `str` gold is a `choice`. An `int` gold is a `score`. That is not a
coincidence - `metrics.collect_scored()` reads exactly that way.

## The real thing

Three question types, three answer shapes, one measurement path.

**`noul` - a yes/no judgement.**
Question: `{"type": "noul", "instructions": "Is this message about a payment,
invoice or refund?"}`.
Answer value: a **probability between 0 and 1**. `0.9` means "90% yes". The
threshold for calling it a yes is a *policy* choice, and in this repo it lives
next to the case: `"thresholds": {"is_billing": 0.5, ...}`.

**`choice` - pick exactly one option from a labelled set.**
Question: `{"type": "choice", "instructions": "Which team should handle this
request?", "criteria": {"billing": "Charges, invoices...", "technical":
"...", "sales": "...", "other": "..."}}`.
Note that `criteria` here is a **dict**: the key is the option you get back,
the value is the human-readable description of it. Answer value: the key
string, e.g. `"billing"`, plus `probabilities` mapping every option key to a
number.

**`score` - pick a level from an ordered list.**
Question: `{"type": "score", "instructions": "How severe is the customer
impact?", "criteria": ["No impact", "Minor", "Major", "Critical"]}`.
Here `criteria` is a **list**. Answer value: a float like `2.0`, which is the
index into that list. The probabilities dict for a score is keyed by the
**string** form of the index: `{"0": 0.1, "1": 0.1, "2": 0.7, "3": 0.1}`.

**How the harness turns each into a probability of being right**
(`decisionarena/metrics.py`, `collect_scored()`):

- `noul`: the probability *is* the model's answer. `p = float(a["value"])`, and
  the outcome is 1 if the gold is true.
- `choice`: look up the gold option inside the `probabilities` dict.
  `p = float(dist.get(gold_value, 0.0))`, and the outcome is 1 if the chosen
  label equals the gold label.
- `score`: look up the gold index inside the `probabilities` dict, and the
  outcome is 1 if the chosen level is within half a step of the gold level.

So all three collapse to the same pair: `(probability the answer was right,
was it right)`. That pair is what Brier score and ECE are computed from.

## In this repo

- `decisionarena/providers.py` - `NUL_KEYWORDS = ("noul", "boolean")`, and
  `normalise_answers()`, which folds `boolean` back into `noul` so the metrics
  only ever see one name. `normalise_questions(questions, wire_keyword)`
  translates our `noul` into the vendor's word on the way out.
- `cases/routing.json` - all three types side by side: `is_billing` is a
  `noul`, `team` is a `choice` with four criteria keys, `severity` is a
  `score` with four criteria entries.
- `cases/injection.json` - the same three types again, with different
  questions (`is_destructive`, `contains_pii`).
- `decisionarena/metrics.py` - `collect_scored()` is where the three kinds
  take three different branches and come out as one `(probs, outcomes)` pair.
- `examples/00_read_the_code.py` - step 5 builds one `noul`, one `choice` and
  one `score` question and scores them with `metrics.score_case()`.

## Your turn

Write a file `exercises/L01_question_types.py` that contains:

- a function `question_types(questions: dict) -> list[str]` that returns the
  **sorted, unique** list of the `type` values in a questions dict.
- a function `gold_kinds(gold: dict) -> dict[str, str]` that returns, for each
  question id, the kind implied by the *type of the gold value*: `bool` means
  `noul`, `str` means `choice`, `int` or `float` means `score`.
- a function `mismatches(questions: dict, gold: dict) -> list[str]` that
  returns the question ids where the question's declared `type` and the kind
  implied by its gold value disagree. It should be empty for a healthy case.
- a `main()` that loads the first case of `cases/routing.json` (read the file
  with `json`, it is a dict with a `"cases"` list), and prints:
  - the sorted question types,
  - the gold kinds per question id,
  - the mismatch list, and the word `MISMATCHES FOUND` if it is not empty
- a self-check section using `assert` that fails loudly if:
  - the sorted question types are not exactly `["choice", "noul", "score"]`
  - the mismatch list is not empty
  - the gold kind of `severity` is not `"score"`

Inputs: `cases/routing.json`. Expected output: the three type names, three
kind names keyed by question id, and an empty mismatch list.

**Hint:** the question's own `type` field tells you the type directly; the
gold value's *Python* type tells you the same thing from the other side. If
the two disagree, one of them is lying - that is what `mismatches` is for.
One trap: in Python a `bool` is a subclass of `int`, so test for `bool` first
or every yes/no gold will be classified as a `score`. For the "boolean is
also a `noul`" wrinkle, look at `NUL_KEYWORDS` in
`decisionarena/providers.py`.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A provider returns an answer of type `boolean` with the value `true`. What
   kind does the harness see, and which function does that translation?
2. Why does the `severity` question use a **list** for its criteria while the
   `team` question uses a **dict**?
3. The gold block for a `score` question is `2`. What question does that
   answer, and what does `2` mean?

## Artifact

Write `docs/notes/L01-question-types.md` - under 250 words, for someone who
has never seen this repo. It must contain:

- one sentence each for `noul`, `choice` and `score`, naming what the answer
  value actually is
- one sentence explaining that `boolean` and `noul` are the same idea with two
  names, and where the translation happens
- one concrete example taken from `cases/routing.json`

Then commit it. The artifact is the proof that you can tell the three types
apart without looking them up.
