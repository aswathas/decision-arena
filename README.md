# DecisionArena

An open, neutral harness for measuring **decision models** (TypeSafe Jev, Cloudflare Clef / clef-flash, and the open-weight zoo) on the same battery — accuracy, calibration, cost, latency, determinism, injection resistance, and **swap safety**.

The point: every vendor published a benchmark table where they win, and the two headline tables disagree with each other. This repo exists so a third party can run the comparison.

## Start here

| File | What it is |
|---|---|
| [`AGENTS.md`](AGENTS.md) | The rules for this repo — for humans and for other AI agents |
| [`AI-CONTEXT.md`](AI-CONTEXT.md) | Machine-readable current state: what exists, what is verified, what is blocked |
| [`course/README.md`](course/README.md) | **Decision Arena Academy** — the beginner course, ten phases, forty-six lessons |
| [`LEARNING.md`](LEARNING.md) | The 15-day curriculum this repo teaches, day by day |
| [`docs/architecture-graph.md`](docs/architecture-graph.md) | The code graph — 188 nodes, 9 communities, with the interactive version alongside |
| [`docs/decision-log.md`](docs/decision-log.md) | Every decision that shaped this repo, and what it cost |
| [`examples/README.md`](examples/README.md) | The learning path: five runnable scripts that teach the maths |

## Learn it

The repo ships its own course. A beginner who knows nothing about LLMs works
through ten phases — from "what even is this" to "here is a finding somebody
else can check" — and an AI agent teaches each lesson, hands over one
micro-exercise, quizzes them, and tracks what they actually learned.

```bash
python tools/install_skills.py          # install the /learn skill into .claude/skills/
python tools/learn_state.py init --learner <your-name> --path beginner
python tools/learn_state.py next        # what to learn next, and why
```

Then run `/learn` in this repo. The course is the folder `course/`; the skills
are in `skills/`; the learner state is in `learning/`; and
`python tools/course_check.py --check` is the gate that keeps a broken lesson
from ever reaching a learner.

The website lives in [`site/`](site/README.md) - Astro and Tailwind, static
output, no server runtime. It is the public front door to both the harness and
the course:

```bash
cd site && npm install && npm run build
```


## Zero-install

Pure Python standard library. No `pip install`, no virtualenv, no dependencies.

```bash
cd decision-arena
python -m decisionarena providers          # what is configured on this machine
python -m decisionarena run --provider mock --battery routing --dry-run
python -m decisionarena run --provider mock --battery all
python -m decisionarena friction --provider mock
```

`mock` is an **offline simulator**. It exists to test the harness end to end (metrics, swap matrix, friction report) with zero API spend. It is not an evaluation of any real model, and its numbers must never be quoted as evidence.

## Going live

```bash
# TypeSafe Jev
setx TYPESAFE_API_KEY "..."

# Cloudflare Clef / clef-flash
setx CLOUDFLARE_ACCOUNT_ID "..."
setx CLOUDFLARE_AUTH_TOKEN "..."

# any OpenAI-compatible gateway (e.g. pplx-decider via OpenRouter)
setx OPENAI_BASE_URL "https://openrouter.ai/api/v1"
setx OPENAI_API_KEY "..."
setx OPENAI_MODEL "perplexity/pplx-decider-v1-27b"
```

Then:

```bash
python -m decisionarena run --provider jev --battery routing
python -m decisionarena run --provider clef:clef-flash --battery routing --repeats 3
python -m decisionarena friction --provider clef:clef-flash
python -m decisionarena swap --provider a=jev --provider b=clef:clef-flash
```

A full battery sweep costs **well under $1**. That is the whole point: the experiment is cheap enough to re-run on every model release.

## Commands

| Command | What it does |
|---|---|
| `providers` | List known providers and whether their credentials are present |
| `run` | Run a battery: routing / injection / format / all. Writes raw `calls.jsonl` + `meta.json` + a Markdown report |
| `friction` | Measure how far a probability moves when only the **shape** of the state changes (prose vs flat JSON vs nested JSON). Needs no labels |
| `swap` | Two providers, one battery: label agreement, probability gap, and the **action-change rate** at your thresholds |

## Batteries

| File | Cases | Labels? |
|---|---|---|
| `cases/routing.json` | 5 realistic support tickets (clear-cut, borderline, spam) | yes — swap in your own tickets |
| `cases/injection.json` | 3 adversarial states (urgency flip, route flip, PII) | no — outcome is "did the decision hold" |
| `cases/format_variants.json` | 3 contents in 3 serialisations | no — outcome is "how far did the probability move" |

## Output contract

Every run writes to `runs/`:

- `<run_id>.jsonl` — one line per call: raw provider answers, latency, token usage, cost, error
- `<run_id>.meta.json` — timestamp, provider, battery hash, spend, cap, uuid
- `<run_id>.md` — the human-readable report

Commit the raw evidence. A number without its raw calls behind it is marketing.

## What is deliberately NOT here yet

- a leaderboard site (this is the harness; the board is the next step)
- a labelling UI (needed before the battery can use your real tickets)
- vision cases (Clef image input) — the adapter accepts `images`, but no case set yet

## Examples

A learning path through the maths, in five runnable scripts — read the code,
then softmax, then temperature, then gradient descent, then attention.

```bash
python examples/00_read_the_code.py     # print the real source, with commentary
python examples/01_softmax.py           # softmax from scratch (stdlib only)
python examples/02_temperature.py       # how temperature reshapes a distribution
python examples/03_train_linear.py      # train a neuron with gradient descent
python examples/04_attention_numpy.py   # single-head self-attention
```

See [`examples/README.md`](examples/README.md) for what each one teaches and
the self-quiz questions to answer before moving on.

## Licence

Apache-2.0, matching the models it measures.
