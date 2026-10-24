# Decision log

Short, dated records of the decisions that shaped this repo — and, where it matters,
what the decision cost.

Format: date · decision · why · what it cost · what would change our mind.

---

## 2026-10-25 · Stdlib only, zero dependencies

**Decision.** `decisionarena/` imports nothing outside the Python standard library.

**Why.** The harness is meant to be re-run by anyone, on any machine, at any point
in the next two years. A dependency is a failure mode with a licence, a CVE feed and
a version matrix. `urllib` + `json` is enough to talk to every provider in the
field.

**Cost.** No `requests`, no `httpx`, no `pydantic`, no `numpy`. Provider payloads
are hand-built dicts. Roughly 300 extra lines across the provider layer.

**What would change our mind.** If the client library of a provider *is* the API
surface (e.g. a decision model that only exists as an SDK), or if JSON schema
validation by hand becomes the dominant bug source. Not yet.

---

## 2026-10-25 · The mock provider ships, and is loudly labelled

**Decision.** `MockProvider` is part of the library, is the default, and every
report it produces carries a warning banner.

**Why.** A harness you cannot run without credentials cannot be reviewed, forked or
taught. The mock exercises metrics, the swap matrix and the friction report with
zero spend.

**Cost.** Risk that someone quotes mock numbers as a result. Mitigated three ways:
a banner on every report, a `note` field on every provider row saying "proves
nothing about real models", and a hard rule in `AGENTS.md`.

**What would change our mind.** Nothing. This stays.

---

## 2026-10-25 · `noul` / `choice` / `score` as one canonical shape

**Decision.** Every provider answer is normalised to
`{qid: {kind, value, probabilities, confidence}}` at the adapter boundary.

**Why.** The wire formats differ — Vercel's AI Gateway calls the same boolean
`noul` and *rejects* the keyword `noul`. Normalising at the edge means the metrics
layer never knows which vendor it is looking at, which is exactly what makes
swap safety measurable.

**Cost.** A translation layer that a reader has to trust.

---

## 2026-10-25 · Raw run files are committed

**Decision.** `runs/*.jsonl`, `*.meta.json` and `*.md` are committed to git.

**Why.** The claim of this repo is that evidence should travel with the number.
A benchmark table without its raw calls is marketing.

**Cost.** Run files accumulate. Mitigated by one directory per run and a stable
naming scheme.

---

## 2026-10-25 · One client, three providers — the protocol is the product

**Decision.** `JevProvider` gains a `base_url` so it can point at a local
`laya-serve` instance, and an in-process `LayaProvider` is added. Same client, same
battery, three backends.

**Why.** This is the whole thesis: if the provider is a config value, then the
interesting measurement is *how much does swapping the provider change the
decision* — swap safety. A harness that can only talk to one vendor cannot measure
that.

**Cost.** Laya's `POST /v1/systemone` is wire-compatible with Jev, but not
byte-identical in every field. The adapter has to tolerate both.

---

## 2026-10-25 · Python 3.12 venv for Laya, not 3.14

**Decision.** `uv venv --python 3.12` for the Laya environment.

**Why.** Laya documents a Windows + Python 3.14 crash. 3.12 is the newest version
that is not affected. `laya[fast]` (TileLang) is not assumed to work on Windows, so
only `laya`, `laya[serve]` and `laya[mcp]` are installed.

**Cost.** One more Python on the machine.

---

## 2026-10-25 · The repo starts private and flips public on Day 5

**Decision.** `gh repo create aswathas/decision-arena --private` first. Flip to
public when a real (non-mock) run exists.

**Why.** A public repo with only mock output invites the exact misreading the mock
banner exists to prevent. A public repo with a real run against a real model is a
different artifact.

---

## 2026-10-25 · Selling an API is out; selling the evaluation is in

**Decision.** The product direction is *not* a decision-model API/SDK. It is
**paid audits** first, then **OSS as distribution**, then a **productised vertical**
chosen on Day 13 from the evidence.

**Why.** The category is roughly two months old. Cloudflare (open weights, Apache-2.0,
a fine-tuning platform, vision) and TypeSafe (a hosted model with a $0.042/Mtok
price and calibration claims) are both better funded and better tooled than a solo
builder can match on an API. The gap is not the model — it is the *measurement
layer*, and the *labelled vertical data* nobody has.

**Cost.** The moat is slow to build: an evaluation rig, a labelled dataset, and
reputation. That does not pay rent on Day 15.

**What would change our mind.** If a vertical turns up with accessible labelled
data and a buyer who cares more about the decision than about the model — that
becomes a product on Day 13. The decision is *deferred to evidence*, not made now.

**Note on Indic-language decision models.** Lumma-fev and friends are a real gap:
a decision model that works in the user's language. This is a **Day-13 candidate**,
not a Day-1 detour. English-first for the foundation.
