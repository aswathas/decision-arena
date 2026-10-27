---
id: L90
phase: 9
title: "Choosing a hypothesis worth testing"
minutes: 35
concepts: [hypothesis, novelty, kill-criteria, prior-work]
prereqs: [L61, L63]
paths: [beginner, provider-live]
exercise_file: docs/notes/L90-hypothesis.md
quiz: L90
---

# L90 - Choosing a hypothesis worth testing

## Why this matters

The previous phase built a machine for measuring things. This phase decides
*what to point it at*. That decision is the difference between a measurement
and a finding: a measurement is a number; a finding is a number plus a
statement about the world that could be wrong. Anyone can run the harness. The
skill is choosing an experiment that teaches you something even when the
answer is "no".

## The naive story

You have a harness. You have a battery. You have three providers and a format
battery that has never been run against a real model. So you run everything,
collect the numbers, and write up the most interesting one.

This is how a lot of measurement work turns into noise. The numbers you did
not expect get published; the numbers you expected get confirmed; and
nobody can tell afterwards which parts of the write-up were predictions and
which were just luck. The tool worked fine. The *question* was never chosen.

## What breaks

**Break 1 - the obvious hypothesis is already published.** The first thing
you want to test is "does the shape of the state change the model's answer?"
because the independent harness `rmax-ai/jev-vs-clef` did not get to it
first, and it is the axis this repo was built around. But that harness
**already measured it**. From the Claims Ledger in your vault, marked
VERIFIED: *"Format sensitivity on `noul`: same refund request -> `urgent`
**0.90** (prose) / **0.86** (flat JSON) / **0.09-0.10** (nested JSON);
`choice` and `score` stable across formats."*

So "state shape affects `noul` answers" is not a hypothesis any more - it is
**prior work**. Testing it again and reporting the same shape of result adds
one more data point to a known curve. Novelty is not about being first to
think of an idea; it is about being first to ask a question that is still
open.

**Break 2 - a hypothesis that cannot fail is a slogan.** "State shape matters
for decision quality" cannot be wrong, which means it teaches you nothing. A
falsifiable hypothesis has a stated condition that would prove it wrong. If
you cannot write that condition, you have a belief, not a hypothesis - and
beliefs do not deserve a spend cap.

**Break 3 - you set the kill criteria after you see the number.** This is
the failure everybody is tempted by, because it feels like flexibility. It is
not flexibility, it is the reason the number in your write-up is worth
anything. Once you have seen "mean spread 0.42", any threshold you pick is
chosen to keep that number. Write the kill criteria **first**, in the file,
before the run - then the run can teach you something, including that you
were wrong.

**Break 4 - the experiment costs more than the finding is worth.** A
hypothesis that needs a labelled dataset, three providers and 10,000 calls
will not get done. The cheapest experiments in this field are the good ones:
the format experiment needs **no labels at all**, because it measures how
far a probability *moves*, not whether it is right. Cheap experiments get
re-run, and re-running is how errors get caught.

**Break 5 - nobody has asked your question on your data.** The ledger's open
questions include: *"Is there an independent, reproducible accuracy comparison
on **real-world** (not synthetic) states? - none found; this is the gap."*
That is a gap with a name. The vendor tables use their own datasets; the
independent harness used synthetic tickets. A comparison on **your own**
production-shaped tickets is unpublished, cheap, and checkable.

## The story

Picture a map on a wall. The left-hand side is already covered in pins -
somebody has been here, and what they found is written in a ledger anyone can
read. The right-hand side is blank.

The first thing a person does at that wall is plant a pin in the blank part.
But the pins that matter are the ones in the part that is *slightly* crowded -
where somebody has measured something, and nobody has checked it on real
tickets.

So you read the ledger first. Its open questions come with their sources,
and one of them says, in effect: nobody has run an independent accuracy
comparison on real-world states rather than synthetic ones.

Then you write the sentence. Not a belief - a claim with a number in it and
a condition attached: the probability moves by more than this much between
these two shapes, and at least one ticket changes side.

And then the kill criteria, before you run anything. If the movement is
smaller than this, drop it. If the effect points the wrong way, drop it. A
threshold picked after you have seen the number is a threshold picked to
keep the number.

## The real thing

**Prior work** is the map of what is already known, and this repo keeps two
maps. The first is in your vault: `Learning/Decision Models/Research/Claims
Ledger.md`, where every material claim about Jev, Clef and the field carries a
source and a status. The second is in `AI-CONTEXT.md`, whose `verified_facts`
list records this repo's own confirmed facts with `claim`, `evidence` (a file
path) and `verified_on`.

Read the ledger's own open questions before you invent one. It lists five,
each marked "no source found" or "not tested by anyone":

1. Does RLCD-style calibration survive fine-tuning on a narrow domain? -
   *no source found*.
2. Why was Clef's observed latency ~90x the advertised figure, and is it
   region- or load-dependent? - *explicitly not isolated*.
3. Is `noul` format-fragility inherent to the architecture or fixable by
   training? - *no source found*.
4. Is there an independent, reproducible accuracy comparison on real-world
   (not synthetic) states? - *none found; this is the gap*.
5. Do the long-tail models actually differ in behaviour, or are they
   re-skins of the same base? - *not tested by anyone*.

**A hypothesis** in this repo is a sentence with three parts:

- **the claim** - what you believe about the world, stated so it could be
  wrong;
- **the evidence that would settle it** - a specific measurement, with a
  named metric, a named provider and model version, and a named case set;
- **the condition that would kill it** - the result that would make you drop
  the hypothesis.

The third part is what separates a hypothesis from a wish. Compare:

| not a hypothesis | a hypothesis |
|---|---|
| "format shape matters" | "On 20 real support tickets, the `noul` probability for `is_billing` moves by more than 0.10 between the prose and nested serialisations of the same ticket, and at least one ticket flips its side of 0.5" |
| "Clef is better" | "On our routing battery, Clef's action-change rate against our current provider is under 10% at the thresholds in `cases/routing.json`" |
| "batching saves money" | "Batching the three routing questions into one call reduces input tokens per ticket by at least 20% against three separate calls" |

Every right-hand cell can be wrong, and each names the measurement that would
show it.

**Novelty** is a positioning claim, and you make it by naming the closest
published work and the exact delta. The `rmax-ai/jev-vs-clef` harness is the
reference prior work: a 159-call battery in seven groups (A routing, B format
sensitivity, C guardrails, D scale, E determinism, F batching, G edges), with
spend and time guards, a `--dry-run` mode, committed raw `calls.jsonl` for two
dated runs, a delta table, and a vision demo at about $0.00042. Its published
results include the 0.90 / 0.86 / 0.09 format spread, labelled accuracy of
96% (Clef, n=24), 92%->83% (Jev) and 79% (clef-flash), 48-question agreement
of 90%/88% (Clef vs Jev) and 85%/83% (clef-flash vs Jev), observed latency of
about 0.3 s p50 for Jev against 18.7 s for Clef, and 6/6 injection probes
holding - all in both dated runs.

So your novelty statement must be a **delta**, not a topic. "Format
sensitivity on synthetic tickets" is done. "Format sensitivity on our own
production-shaped tickets, with the raw per-call probability for every
serialisation committed" is a delta, because the published number is measured
on the harness author's synthetic states.

**Kill criteria** are written before the run, in the same file, and they come
in three kinds:

- **a magnitude criterion** - "if the mean spread over my 20 tickets is below
  0.05, I drop the hypothesis";
- **a direction criterion** - "if the nested format is *more* confident than
  the prose format, my mechanism is wrong, because nesting adds structure
  that should dilute attention";
- **a scope criterion** - "if the effect appears only on `choice` questions and
  not on `noul`, then this is about the answer type, not about the state
  shape, and I will write it up that way instead".

Any of the three is a real finding. That is the point of pre-registration: a
null result still teaches you something, because you learn where the effect
is *not*.

**Cost: is this hypothesis cheap to test?** Do the arithmetic before you
write the hypothesis, using the formula from lesson L81. A format experiment
on 20 tickets, 3 serialisations, 3 repeats is 180 calls. At about 160 input
tokens each, that is about 28,800 tokens, roughly 0.03 Mtok - at $0.038/Mtok
that is **about $0.001**. The whole experiment costs a tenth of a cent, which
is why it fits inside the default $0.25 spend cap with room to spare. Cheap
means: you can re-run it, you can run it on a second provider, and you can
run it again when someone asks "are you sure?".

**One last discipline: name the version.** Your hypothesis must pin the
provider and model (`clef:clef-flash`, `jev:jev-1.14.0`) and the case set
(the battery file, and its hash). A hypothesis that says "the model" cannot
be falsified by next month's model.

## In this repo

- `AI-CONTEXT.md` - `verified_facts`: the repo's own confirmed claims, each
  with an `evidence` file path and a `verified_on` date. It also lists the
  next action this phase exists for: *"Format-friction finding: write it up
  and publish it."*
- `decisionarena/harness.py` - `run_format_friction(provider, cases,
  formats=("prose", "flat", "nested"), out_dir="runs")` is the cheapest
  experiment in the field: it needs no labels, it writes
  `runs/<run_id>.json`, and it records `values` per format plus `spread` and
  `flips_at_0.5` per question.
- `decisionarena/harness.py` - `FORMAT_BUILDERS` is the dict of the three
  serialisations (`"prose"`, `"flat"`, `"nested"`), so the shapes are code you
  can point at rather than folklore.
- `cases/format_variants.json` - the battery: three contents, each with a
  `variants` dict holding all three shapes, and **no `gold` key** anywhere.
- `decisionarena/providers.py` - `MockProvider.FORMAT_SHIFT` is
  `{"prose": 0.0, "flat": -0.04, "nested": -0.81}`: the mock is *built* to
  reproduce the shape of the published finding, which is why an offline
  friction result proves the harness works and nothing about any model.
- `decisionarena/harness.py` - `battery_hash(cases)` gives the 12-character
  fingerprint that belongs in your hypothesis note, so a reader can tell
  whether they ran the same questions you did.
- `decisionarena/cli.py` - `cmd_friction()` wires the experiment to one
  command, `python -m decisionarena friction --provider <spec>`.
- `docs/decision-log.md` - the log where a choice like "we will test the
  format effect on production-shaped tickets rather than synthetic ones"
  belongs, with its date, why, cost and what would change your mind.
- The vault's `Learning/Decision Models/Research/Claims Ledger.md` - the
  prior-work map, with the 0.90 / 0.86 / 0.09 format spread, the labelled
  accuracies, the agreement rates, the observed latencies, and the list of
  open questions with no source found.

## Your turn

Write a file `docs/notes/L90-hypothesis.md`. It is the hypothesis note you
would write **before** running anything, and it is the first half of a
publishable finding.

It must contain these sections, in this order:

- `## Hypothesis` - one sentence, falsifiable, with the numbers you will
  measure written into it (for example "the `noul` probability for
  `is_billing` moves by more than 0.10 between the prose and nested
  serialisations of the same ticket"). Name the provider and model version
  you will use, and the battery file you will run.
- `## Prior work` - the closest published work, with its actual numbers: the
  `rmax-ai/jev-vs-clef` 0.90 / 0.86 / 0.09 format spread, its labelled
  accuracy and agreement figures, and what it did **not** measure. Two or
  three sentences plus the numbers.
- `## What is new here` - the delta, in one or two sentences. This is the
  sentence that decides whether the experiment is worth running.
- `## Kill criteria` - at least three, of at least two different kinds: one
  magnitude, one direction, and one scope. Each written so that you could
  point at a number and say "this one fired".
- `## Measurement plan` - the metric names you will compute, the number of
  cases, the number of repeats, the battery file, and the `battery_hash` if
  you have one
- `## Cost` - the number of calls, the token estimate, the price per Mtok you
  will use, the resulting dollar cost, and whether it fits inside the
  default $0.25 spend cap
- `## If it is null` - one paragraph: what you will write if the hypothesis
  dies, and why that is still a result

Inputs: the vault's Claims Ledger, the open questions in `AI-CONTEXT.md`,
the format battery in `cases/format_variants.json`, and the prices in
`decisionarena/providers.py`.

Expected output: the seven sections above, 400-700 words, with every number
in the Prior work section copied from a source you can name.

**Hint:** the test of a good kill criterion is that you could read it six
months from now, without memory, and know whether it fired. And the test of
a good novelty statement is that it names something the published number did
*not* cover.

**Do not** run the experiment yet. This note comes before the spend.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. In your own words: what does the published 0.90 / 0.86 / 0.09 result
   already establish, and therefore what can no longer be your finding?
2. Why is "state shape matters" not a hypothesis, and what would you have to
   add to it to make it one?
3. Give one magnitude kill criterion, one direction kill criterion and one
   scope kill criterion for the format experiment.
4. What is the cost of your experiment, and why does that number matter for
   whether you will ever re-run it?

## Artifact

The artifact **is** `docs/notes/L90-hypothesis.md`. Read it back as if you
were the reviewer: could someone else run exactly this experiment from your
note, and would they know whether you were right or wrong?

Then commit it. The artifact is the proof that you chose a question worth
asking, not the proof that you found the answer.
