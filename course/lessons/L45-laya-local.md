---
id: L45
phase: 4
title: "Laya - a local model on your own GPU"
minutes: 35
concepts: [laya, local-inference, latency, weights]
prereqs: [L40]
paths: [beginner, provider-live]
exercise_file: laya-lab/README.md
quiz: L45
---

# L45 - Laya: a local model on your own GPU

## Why this matters

The third backend is the one that changes the question. Jev and Clef are
services you rent; Laya is a model you **run yourself**. No key, no per-call
fee, no vendor in the loop - and a completely different cost structure
(electricity) and a completely different latency structure (your GPU, your
queue). If the harness only ever measured hosted APIs, it could never answer
the question a real buyer asks: *should I run this myself?*

## The naive story

A restaurant (hosted API) charges you per plate and cooks while you wait. A
food truck you own yourself (local model) has no per-plate bill, but you have
to buy the truck, park it, keep it stocked with fuel, and the cooking is as
slow as your truck is on that day.

Both serve the same dish. The interesting question is never "which is better
at cooking?" - it is "which one is better for *my* dinner party, on *my*
budget, with *my* reliability requirements?"

## What breaks

**Break 1 - "local" is not "free", it is "different".** No per-token price,
but the machine has a power bill, the weights have to live in VRAM, and if
your GPU is busy your latency becomes someone else's problem. The repo's
`laya-lab/README.md` is blunt about the hardware: 4 GB of VRAM is tight, and
the 27B model does not fit - you need the 9B flash variant.

**Break 2 - latency has a shape, not a number.** A hosted API's latency is
dominated by the network and the vendor's queue. A local model's latency has
a **cold start**: the first request after the server starts pays for loading
the weights. That is why the README recommends `LAYA_PRELOAD=1` - load the
weights *before* serving, so the first request is not a 40-second outlier.
Compare that with the repo's own latency reporting in `report.py`, which
prints p50, p95 and max: one slow outlier is invisible at p50 and obvious at
max, and both numbers are in the report for a reason.

**Break 3 - a local model can be *the same protocol*, which is the whole
point.** `laya-serve` exposes `POST /v1/systemone` - the same request and
response shape as TypeSafe Jev. So the harness's adapter does not need to
learn a new language. It only needs to be pointed at a different address.

## The story

Somebody in a small apartment does the laundry every week. She could carry
every bundle to the laundromat on the corner: they charge per wash, their
machine is always hot, and it takes about as long as a cup of coffee. Or she
could run her own machine at home, where nothing is billed per wash - but she
had to buy it, she has to feed it water and electricity, and it can only take
so much at a time. A bundle that does not fit does not get washed slowly; it
stops, and she runs it again.

That is the shape of running a decision model on your own GPU instead of
renting one. The hosted service has no machine to buy, but it bills you every
call. The local model has no per-token price at all - the cost is electricity
and your GPU time - but the model's stored numbers have to fit in the card
you own. A 9B model is about 18 GB of file; the 27B one does not fit a 4 GB
card. The first request after the server starts also has to load those numbers
into the card, a cold start the README puts at about 40 seconds. Load them
first, and later decisions land in the 236-276 ms range.

## The real thing

**What Laya is.** `laya-lab/README.md` describes Laya as the open-source
project that ships the **open-weight decision-model family** and a serve
layer that speaks the Jev wire format. The extras: `laya[serve]` adds the
HTTP server, `laya[mcp]` adds an MCP server, `laya[structured]` and
`laya[langchain]` are integration extras, and `laya[fast]` (TileLang) is
explicitly flagged as *not* to be assumed to work on Windows.

**Weights.** The **weights** are the trained parameters - the numbers inside
the model. For Laya they are published, so you can download them once and run
the model offline. A "9B" model has about 9 **billion** parameters, and
parameters are stored at 2 bytes each in 16-bit precision, so 9B parameters is
roughly 18 GB of file. That is why VRAM is the binding constraint and why the
9B variant is the realistic one on a 4 GB card.

**Serving it locally.** The README's setup, on Windows with Python 3.12:

```powershell
uv venv --python 3.12
uv pip install laya "laya[serve]" "laya[mcp]"
```

Then the smoke test, with no server at all:

```powershell
.\.venv\Scripts\python.exe -m laya "I was charged twice, please refund" --predict
```

And to serve:

```powershell
$env:LAYA_DEVICE = "cuda"
$env:LAYA_PRELOAD = "1"
.\.venv\Scripts\laya-serve.exe
```

`LAYA_DEVICE=cuda` uses the GPU; `LAYA_PRELOAD=1` loads the weights before
serving so the first request is not an outlier. Third-party measurements put
local Laya latency around **236-276 ms** per decision.

**Wiring it into the harness.** The README gives two options: point the
existing Jev adapter at the local server (it describes adding a `base_url`
parameter to `JevProvider` - note that the current adapter in
`decisionarena/providers.py` still has `URL` as a fixed class attribute, so
that parameter is a plan described in the README, not something you can use
today without changing the adapter), or write an in-process `LayaProvider`
that imports `laya` directly - but that drags torch into the environment the
stdlib-only `decisionarena/` package runs in, which the repo's rule 1
forbids. Option 1 is the default in the README for exactly that reason.

**The honest limits.** The README's upstream table is the most valuable part
of the file: the `noul` answer type is weak; negation flips the answer;
fine-grained sentiment is not solved; the answer depends on where the
evidence sits in the state; `act_probability` is not informative; calibration
needs a temperature fit (ECE 0.466 -> 0.081); and on classification-shaped
work the small model is far behind Jev (Banking77 0.425 vs 0.870). And the
row that is the whole product thesis: **Khmer 0.000 at 95.2 % confidence -
confidently wrong.**

## In this repo

- `laya-lab/README.md` - the setup, the smoke test, the serve commands, the
  hardware table, the two wiring options and the upstream limits table. This
  is the file you will add your observations to.
- `decisionarena/providers.py` - `JevProvider`, whose `URL` class attribute
  is the constant a local server would have to override.
- `decisionarena/harness.py` - `run_battery()`, which records
  `latency_s` for every call (the number you compare against 236-276 ms).
- `decisionarena/report.py` - `run_report()`, which prints p50, p95 and max
  latency, and the determinism section.
- `decisionarena/providers.py` - `MockProvider.__init__` takes a `price_per_mtok`
  default of `0.042` and no network at all - the shape of a local run with a
  cost of zero.

## Your turn

This lesson's exercise file is `laya-lab/README.md`. You will **add a
section** to that file recording what you observed. Do not rewrite or delete
anything that is already there - the repo never deletes.

**Variant A - you got the local server running.** Add a section titled
`## My local observations` to `laya-lab/README.md`. It must contain:

- the exact commands you ran, in order, including the Python version and
  whether `LAYA_DEVICE` was `cuda` or `cpu`
- the wall-clock latency you measured for at least three decisions (use the
  `latency_s` field from a run, or time the smoke-test command yourself), and
  whether the first request was slower than the rest
- the size of the model variant you ran (9B flash or 27B) and whether you
  hit a VRAM limit
- one decision the model got right and one it got wrong, with the exact text
  you fed it
- the peak VRAM you observed, if you measured it

**Variant B - the server will not run on your machine** (no GPU, the 2.5 GB
download failed, or you are not using this machine). Add the same section,
titled `## My local observations`, but instead of measurements write down
what you *could* establish from reading the README: the exact setup
commands, the model variant your hardware would require (check the hardware
table), the expected latency range the README quotes, and the two wiring
options with the trade-off the README gives for each. Start the section with
a line saying you ran the offline variant and why.

Either way the section must end with the four questions the README itself
asks under "What to actually measure here" - (1) does the local model
reproduce the format-friction effect, (2) is its probability distribution
calibrated the same way as the hosted ones, (3) what is the real per-decision
latency and the real per-decision cost, (4) does it hold the same decision as
Jev and Clef on the routing battery, and where it does not, why - each with
your answer or your honest "not yet measured".

**Hint:** the README's hardware table and the "What to actually measure here"
list already contain the two numbers you need (the VRAM budget and the
quoted latency range); the exercise is to record what *your* machine does
against them, not to rediscover them.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What does "open weights" let you do that a closed commercial API does
   not, and what does it cost you instead?
2. Why does the README insist on `LAYA_PRELOAD=1`, and which latency number
   in this repo's own report would expose the problem if you left it off?
3. The README says option 1 (point the Jev adapter at the local server) is
   the default. What repo rule would option 2 (an in-process `LayaProvider`)
   break?

## Artifact

The artifact is the new section in `laya-lab/README.md`: `## My local
observations`. It must be at least 150 words, must say which variant you
completed, must contain at least two concrete numbers (a latency figure and
the VRAM budget, or the quoted latency range plus the model size), and must
not contain anything that looks like a credential.

Then commit it.
