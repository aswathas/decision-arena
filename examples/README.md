# Examples

A learning path through the code. Each script is standalone, runnable from the
repo root, and uses only the standard library (plus numpy in example 04, where
it falls back to pure Python if numpy is missing).

```bash
cd decision-arena
python examples/00_read_the_code.py
```

Read them in order. Each one assumes the previous one.

| # | File | What it teaches | Self-quiz: answer before moving on |
|---|---|---|---|
| 00 | [`00_read_the_code.py`](00_read_the_code.py) | How the harness fits together: the wire protocol, the provider adapters, the runner, the metrics, the report | Why does `run_battery` write raw calls to JSONL *before* it writes any report — what would you lose otherwise? |
| 01 | [`01_softmax.py`](01_softmax.py) | Softmax from scratch: raw scores → exponentiate → normalise, plus the numerically stable variant | Why is softmax invariant to adding a constant to every logit, and why does that matter for training? |
| 02 | [`02_temperature.py`](02_temperature.py) | Temperature as a single knob that sharpens or flattens a distribution, and how it moves a thresholded *action* without moving the *ranking* | If temperature never changes the ranking, can it still change which action you take? (Check the thresholds in `cases/routing.json`.) |
| 03 | [`03_train_linear.py`](03_train_linear.py) | One neuron trained by gradient descent: forward pass, log loss, gradient, update — and the chain rule in action | Why is the gradient `p(1-p)` so small when the model is confident, and what does that mean for a model that is confidently wrong? |
| 04 | [`04_attention_numpy.py`](04_attention_numpy.py) | Single-head self-attention: query-key dot products, the `1/sqrt(d_k)` scaling, and the softmax over scores | A decision model's `choice` answer is a softmax over *options*. In the attention example, what plays the role of an option, and what plays the role of the state? |

## How these connect to the harness

The examples are not decoration — they are the maths underneath the repo:

- **Softmax** (`01`, `02`, `04`) is how every `choice` answer in
  `decisionarena/providers.py` becomes a `probabilities` dict.
- **Temperature** (`02`) is the deployment dial for over-confident models; the
  harness measures the result with `metrics._ece`.
- **Gradient descent** (`03`) is what a model vendor did before you ever call
  the API. The harness only measures the outcome.
- **Attention** (`04`) is the mechanism inside the model. The harness does not
  care about the mechanism — only about calibration and swap safety.

## Running the self-checks

Every example ends with `assert`-based self-checks. If a script exits `0`,
the checks passed. Run them all with:

```bash
for f in examples/0*.py; do python "$f" > /dev/null && echo "ok   $f" || echo "FAIL $f"; done
```

## A note on style

These scripts are deliberately verbose and print their intermediates. That is
the opposite of what you would write in production — the point here is that you
can see every number move. When you are done reading them, compare them with
`decisionarena/metrics.py`: same math, no prints, four decimal places.
