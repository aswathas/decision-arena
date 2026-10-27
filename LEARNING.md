# LEARNING.md — the curriculum this repo teaches

This is not a side quest. `decision-arena` is simultaneously a **product** and a
**textbook**, and you are the author of both. Every sprint day has a build task and
a learn task, and they are the same task.

**Who this is for:** Aswath — you vibe-code, you have shipped things, but you have
never been taught what a neural network is. That is fine. This document is the path
from "I use the tools" to "I can explain, from first principles, why this harness
reports what it reports" — and on to "I built a product somebody pays for."

## Start with the Academy

This 15-day sprint assumes you can already follow the maths. If you cannot
yet, the repo ships its own course: **Decision Arena Academy** in
[`course/`](course/README.md) — ten phases, forty-six lessons, from "what even
is this" to "here is a finding somebody else can check".

The Academy is the on-ramp; this sprint is the fast track. Run `/learn` in this
repo, or start from the command line:

```bash
python tools/learn_state.py init --learner <your-name> --path beginner
python tools/learn_state.py next
```

The Academy tracks mastery **per concept**, so when you arrive at Day 2 the
system already knows which ideas you own and which ones you are faking.

## How this actually works

You **write the code**. The AI explains, quizzes, reviews, and asks questions. It
does not write your exercises — if it does, you learn nothing and the illusion
becomes a liability. When you are stuck, say so and ask for a *hint*, not a solution.

Three modes, all available in your AI tooling:

| Skill | Use it when |
|---|---|
| `learn-by-doing` | Daily loop: read your code → explain → one micro-exercise → quiz → log |
| `teach-persona` | You want a concept explained a specific way (Feynman, Socratic, Napoleon, Dewey…) |
| `doubt-resolver` | You have one specific question and want it answered from *your* codebase |

The personas are teaching **moves**, not costumes. Feynman means "no jargon, then
compress it." Socrates means "I ask until you say it." It does not mean quoting
dead men.

## The loop, every day

1. **Read** the day's note in the vault (`Learning/Course - Decision Models/00 Course Map.md`).
2. **Read the code** — `examples/0N_*.py` — and explain it back to the AI in your own words.
3. **Write** one micro-exercise yourself. Commit it.
4. **Quiz**: answer the "questions to answer for yourself" at the top of the file.
5. **Log** the outcome in `Learning/Course - Decision Models/Build Log.md`.
6. **Publish one artifact.** A day without a public artifact is a wasted day.

Ten minutes of writing something you can explain beats two hours of reading.

## The sprint — 15 days

### Days 1–4 · Foundations (build: the harness reads the world)

| Day | You learn | You build | Public artifact |
|---|---|---|---|
| 1 | What a tensor is; your own codebase as the subject | `examples/00_read_the_code.py`; the AST graph of the repo | The repo, public, with a graph |
| 2 | Softmax, logits, temperature | `examples/01_softmax.py`, `examples/02_temperature.py` | A short "what is temperature, really" note |
| 3 | Gradient descent, the chain rule, loss | `examples/03_train_linear.py` | The loss curve, with the math explained |
| 4 | Attention, and what an LLM *is* | `examples/04_attention_numpy.py` | The attention matrix, annotated |

### Days 5–7 · Decision models (build: one client, three providers)

| Day | You learn | You build | Public artifact |
|---|---|---|---|
| 5 | What a "decision model" is and is not; the `noul`/`choice`/`score` wire protocol | `JevProvider` + `ClefProvider` on one battery; repo flips **public** | The harness with a real (non-mock) run |
| 6 | Calibration: ECE, reliability curves; why confidence ≠ probability | One client, three providers (Jev, Clef, local Laya) | A calibration comparison table |
| 7 | Local inference: weights, tokenizers, latency, batching | `laya-lab/` — Laya running on your RTX 2050 | Setup guide that actually works on Windows |

### Days 8–10 · The finding (build: something nobody has published)

| Day | You learn | You build | Public artifact |
|---|---|---|---|
| 8 | One client, many models: prompt/format invariance | The format-friction battery on real models | First numbers |
| 9 | Injection resistance; state vs instruction | The injection battery | A result |
| 10 | How to write a finding other people can check | The write-up | **The format-friction finding** — published |

### Days 11–12 · Fine-tune (build: your own weights)

| Day | You learn | You build | Public artifact |
|---|---|---|---|
| 11 | LoRA/QLoRA; what a checkpoint actually contains | Kaggle 2×T4 fine-tune of a small decision model | A training log |
| 12 | Evaluation of *your* checkpoint vs the base model | The eval; push to HuggingFace | **A checkpoint on HuggingFace under your name** |

### Days 13–15 · Product (build: the thing people pay for)

| Day | You learn | You build | Public artifact |
|---|---|---|---|
| 13 | Product selection from evidence, not taste | Choose the vertical; write the one-page spec | The spec |
| 14 | Packaging: pricing, API shape, docs | v1 of the product | A working product |
| 15 | Distribution: launch, write, sell | Launch | **Product live, under your name** |

## The rules that keep this honest

1. **Never delete.** Archive only. `Archive/` in the vault, git history in the repo.
2. **Evidence before claims.** A number without its raw `runs/*.jsonl` is marketing.
3. **The mock is not evidence.** It tests the harness. It never evaluates a model.
4. **Zero broken wikilinks.** `python tools/check_links.py` is the gate.
5. **Fundamentals are never cut.** If a day runs short, the sprint extends — a skipped
   foundation is the thing that makes the product unshippable.
6. **English first.** The build, the docs, the publish: English. Indic-language
   decision models are a real market gap, and a Day-13 candidate — not a Day-1 detour.

## What "done" looks like at Day 15

- A public repo with a real evaluation rig that anyone can re-run for under $1.
- A published finding that is checkable and was not already known.
- A fine-tuned checkpoint on HuggingFace in your name.
- A product you can demo, price, and explain — decided from evidence, not from taste.
- The ability to explain softmax, temperature, gradient descent, and attention without
  notes, because you wrote them.

## Where things live

| Thing | Path |
|---|---|
| Code | `C:\Users\aswat\Downloads\Projects\decision-arena` |
| Vault | `C:\Users\aswat\Aswaths Obsidian Den\Aswaths Mountain Den` |
| Course notes | `Learning/Course - Decision Models/` in the vault |
| Foundations notes | `Learning/Foundations/` in the vault |
| Decision-model notes | `Learning/Decision Models/` in the vault |
| Knowledge graph | `C:\Users\aswat\Downloads\Projects\graphify-vault` → `Learning/Graph/` |
| Current state for AI agents | `AI-CONTEXT.md` in this repo |
