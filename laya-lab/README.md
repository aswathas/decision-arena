# laya-lab — running a decision model on your own GPU

**Day 7 of the sprint.** This directory is where the third provider comes from: a
decision model that runs **locally**, with no API key and no per-decision cost.

Everything here is **experimental** and lives in its own virtualenv. The library
`decisionarena/` stays stdlib-only; this directory is allowed to be heavy.

---

## What Laya is

Laya is the open-source project that ships the **open-weight decision-model family**
and a **serve layer that speaks the Jev wire format**.

- `laya-serve` exposes `POST /v1/systemone` — the same request/response shape as
  TypeSafe Jev. That is the whole reason it matters here: the same client, the
  same battery, three backends.
- `laya[serve]` adds the HTTP server.
- `laya[mcp]` adds the MCP server (so Claude Code / mcode can call a local
  decision model as a tool).
- `laya[structured]`, `laya[langchain]` — integration extras.
- `laya[fast]` (TileLang) — **do not assume this works on Windows.**

---

## Setup (Windows, Python 3.12)

Laya documents a Windows + Python 3.14 crash, so pin 3.12.

```powershell
cd C:\Users\aswat\Downloads\Projects\decision-arena
uv venv --python 3.12
uv pip install laya "laya[serve]" "laya[mcp]"
.\.venv\Scripts\python.exe -I -c "import laya; print(laya.__version__)"
```

`-I` (isolated mode) avoids picking up the ambient `site-packages` and the
`PYTHONHOME`/`PYTHONPATH` weirdness that Windows venvs sometimes hit.

Expect a large download: **~2.5 GB of torch** plus the checkpoint.

---

## Smoke test (no server)

```powershell
.\.venv\Scripts\python.exe -m laya "I was charged twice, please refund" --predict
```

If that prints a sensible decision, the model works locally.

---

## Serve

```powershell
$env:LAYA_DEVICE = "cuda"
$env:LAYA_PRELOAD = "1"
.\.venv\Scripts\laya-serve.exe
```

- `LAYA_DEVICE=cuda` uses the GPU. On this machine (RTX 2050, 4 GB VRAM) you need
  the **flash** (9B) variant, not the 27B one.
- `LAYA_PRELOAD=1` loads the weights before serving, so the first request is not
  a 40-second outlier.

Third-party measurements put local Laya latency around **236–276 ms** per decision.

---

## Wiring it into the harness

The harness talks to Jev over `POST https://api.typesafe.ai/v1/systemone`. The
local server speaks the same shape on localhost. Two ways to connect:

1. **Point the existing adapter at it** — `JevProvider` gains a `base_url`
   parameter, so `JevProvider(base_url="http://127.0.0.1:8080")` hits the local
   server instead of the cloud.
2. **In-process** — a `LayaProvider` that imports `laya` and calls it directly.
   No HTTP hop, but it drags torch into the venv that `decisionarena/` runs in.

Option 1 is the default: it keeps the library dependency-free and it exercises the
*real* wire format, which is what the harness is meant to measure.

---

## Your hardware, honestly

| | |
|---|---|
| GPU | RTX 2050, 4 GB VRAM |
| RAM | 15.8 GB |
| CPU | Ryzen 7 7435HS, 16 threads |
| Disk free | ~51 GB |

4 GB VRAM is tight. Plan for the **9B flash model** and expect to be near the
limit. If VRAM runs out, fall back to CPU and accept ~seconds per decision —
still fine for calibration work, too slow for latency claims.

---

## What to actually measure here (Day 7 deliverables)

1. Does the local model reproduce the format-friction effect (Day 8's battery)?
2. Is the local model's probability distribution **calibrated** the same way the
   hosted ones are? Compare ECE against the Day 6 table.
3. What is the real per-decision latency and the real per-decision cost
   (electricity, not API)?
4. Does it hold the same decision as Jev and Clef on the routing battery — and
   where it does not, why?

Those four answers are worth more than any "we ran a 9B model locally" blog post.

---

## Fine-tuning (Days 11–12)

Laya ships a Kaggle notebook and a fine-tuning guide. The upstream reference run
reports top-1 improving from **0.10 → 0.66** and success rate **0 → 62 %**, with a
published checkpoint at `cklxx/laya-browser`.

Read the upstream limits honestly before trusting them:

| Reported limit | Meaning |
|---|---|
| #156 `noul` | the `noul` answer type is weak |
| #377 negation | negation in the state flips the answer |
| SST-5 = 0.372 | fine-grained sentiment is not solved |
| #131 position bias | the answer depends on where the evidence sits in the state |
| #185 `act_probability` | that field is not informative |
| ECE 0.466 → 0.081 | calibration needs a temperature fit, out of the box it is badly calibrated |
| Banking77 0.425 vs Jev 0.870 | the small model is far behind on classification-shaped work |
| Khmer 0.000 @ 95.2 % conf | **confidently wrong** on an Indic language — this is the Day-13 opportunity |

That last row is the whole product thesis in one line: a decision model that is
**confidently wrong** in your language is a real, purchasable problem.
