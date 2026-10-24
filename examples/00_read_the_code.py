"""Example 00 - Read the code.

WHAT THIS TEACHES
    DecisionArena is small enough to read end to end. This script imports the
    real modules and prints the actual source of the functions and classes that
    matter, so you can read the code that RUNS rather than a copy of it.

WHAT TO LOOK AT FIRST
    The printed order below. It goes: protocol -> provider -> runner -> metric
    -> report. That is the order data flows through the harness.

QUESTIONS TO ANSWER FOR YOURSELF
    1. In `normalise_answers`, what three shapes of answer come back from a
       provider, and why is the wire keyword "noul" turned into "noul"?
    2. Why does `run_battery` write raw calls to JSONL before it writes any
       report? What would you lose if it did not?
    3. `action_change_rate` compares two providers at a threshold. What would
       the "agreement rate" be if the two models agreed on the label but their
       probabilities sat on opposite sides of the threshold?

Run:  python examples/00_read_the_code.py
"""
from __future__ import annotations

import inspect
import os
import sys

# The repo root is the parent of examples/. When you run
#   python examples/00_read_the_code.py
# Python puts examples/ on sys.path, NOT the repo root, so `import
# decisionarena` would fail. Add the root explicitly (same trick as
# tests/test_metrics.py uses).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from decisionarena import harness, metrics, providers, report  # noqa: E402


def show(obj, label: str) -> None:
    """Print one function/class: its name, its docstring, its real source.

    `inspect.getsource` reads the .py file on disk and returns the source
    lines exactly as written. That is why this example is worth running: you
    see the repository's real code, not a paraphrase of it.
    """
    print("=" * 78)
    print(f"{label}: {obj.__name__}")
    print("=" * 78)
    doc = inspect.getdoc(obj)
    if doc:
        print(f'docstring: """{doc}"""\n')
    else:
        print("(no docstring)\n")
    try:
        src = inspect.getsource(obj)
    except (OSError, TypeError) as exc:
        # Builtins and C extensions have no Python source - never crash a
        # teaching script on that.
        print(f"(source unavailable: {exc})\n")
        return
    for i, line in enumerate(src.rstrip().splitlines(), start=1):
        print(f"{i:>4} | {line}")
    print()


def show_attr(module, name: str, label: str) -> None:
    """Print a module-level attribute (a class) by name."""
    obj = getattr(module, name, None)
    if obj is None:
        print(f"{label}: {name} (not found)\n")
        return
    show(obj, label)


def main() -> int:
    print("DecisionArena - reading the real code\n")
    print("Everything below is printed straight out of the repo's .py files.")
    print("Read in this order; each step feeds the next.\n")

    # ---------------------------------------------------------------- 1
    print("#" * 78)
    print("# STEP 1 - the wire protocol (providers.py)")
    print("#" * 78)
    print("# Two providers, one protocol. normalise_questions translates OUR")
    print("# question types into a vendor's keyword; normalise_answers flattens")
    print("# whatever comes back into one comparable shape.\n")
    show(providers.normalise_questions, "providers.py")
    show(providers.normalise_answers, "providers.py")
    show_attr(providers, "Provider", "providers.py")
    show_attr(providers, "MockProvider", "providers.py")

    # ---------------------------------------------------------------- 2
    print("#" * 78)
    print("# STEP 2 - the runner (harness.py)")
    print("#" * 78)
    print("# run_battery is the loop: for every case, call the provider, log the")
    print("# raw answer, score it. It also enforces the spend cap.\n")
    show(harness.load_cases, "harness.py")
    show(harness.run_battery, "harness.py")

    # ---------------------------------------------------------------- 3
    print("#" * 78)
    print("# STEP 3 - the metrics (metrics.py)")
    print("#" * 78)
    print("# The four numbers that matter: accuracy, ECE, Brier, and the")
    print("# swap-safety numbers. _ece is the interesting one - read it twice.\n")
    show(metrics.score_case, "metrics.py")
    show(metrics._ece, "metrics.py")
    show(metrics.label_agreement, "metrics.py")
    show(metrics.action_change_rate, "metrics.py")

    # ---------------------------------------------------------------- 4
    print("#" * 78)
    print("# STEP 4 - the report (report.py)")
    print("#" * 78)
    print("# Pure formatting. No measurement lives here - if you want to change")
    print("# a NUMBER, you change metrics.py, never report.py.\n")
    show_attr(report, "run_report", "report.py")

    # ---------------------------------------------------------------- 5
    print("#" * 78)
    print("# STEP 5 - a live round trip")
    print("#" * 78)
    print("# Use the offline MockProvider so nothing calls the network. This is")
    print("# the shape every provider returns, so it is worth seeing once.\n")
    p = providers.MockProvider()
    questions = {
        "is_billing": {"type": "noul", "instructions": "Is this about a payment?"},
        "team": {
            "type": "choice",
            "instructions": "Which team?",
            "criteria": {"billing": "Charges", "technical": "Errors", "other": "Triage"},
        },
        "severity": {"type": "score", "instructions": "How severe?",
                     "criteria": ["No impact", "Minor", "Major", "Critical"]},
    }
    state = "I was charged twice for my subscription this month. Please refund the extra charge."
    answers = p.decide(state, questions)
    for qid, a in answers.items():
        print(f"  {qid:<12} kind={a['kind']:<6} value={a['value']!r:<12} "
              f"conf={a['confidence']!r}")
    print()
    score = metrics.score_case(answers, {"is_billing": True, "team": "billing", "severity": 1})
    print(f"  scored -> accuracy={score['accuracy']} ece={score['ece']} brier={score['brier']}")
    print()

    # ---------------------------------------------------------------- 6
    print("=" * 78)
    print("READ THIS NEXT")
    print("=" * 78)
    order = [
        "examples/01_softmax.py      - the distribution behind every probability",
        "examples/02_temperature.py  - how one knob reshapes that distribution",
        "examples/03_train_linear.py - gradients, loss, and the chain rule",
        "examples/04_attention_numpy.py - the softmax, again, inside attention",
        "decisionarena/providers.py  - read the wire format one more time",
        "decisionarena/metrics.py     - read _ece and action_change_rate",
    ]
    for i, step in enumerate(order, start=1):
        print(f"  {i}. {step}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
