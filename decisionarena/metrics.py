"""Metrics for decision-model evaluation.

The four that matter: accuracy, ECE (calibration), Brier (probability quality),
and agreement/swap-safety between providers.
"""
from __future__ import annotations

import math
from collections import defaultdict


def _brier(probs: list[float], outcomes: list[int]) -> float | None:
    if not probs:
        return None
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(probs)


def _ece(probs: list[float], outcomes: list[int], bins: int = 10) -> float | None:
    """Expected calibration error: mean |confidence - accuracy| weighted by bucket size."""
    if not probs:
        return None
    buckets: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for p, o in zip(probs, outcomes):
        b = min(int(p * bins), bins - 1)
        buckets[b].append((p, o))
    total = len(probs)
    err = 0.0
    for bucket in buckets.values():
        conf = sum(p for p, _ in bucket) / len(bucket)
        acc = sum(o for _, o in bucket) / len(bucket)
        err += (len(bucket) / total) * abs(conf - acc)
    return err


def reliability_bins(probs: list[float], outcomes: list[int], bins: int = 10):
    """Rows for a reliability diagram: (lo, hi, n, mean_confidence, accuracy)."""
    out = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(p, o) for p, o in zip(probs, outcomes) if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if not sel:
            continue
        out.append({
            "bin": f"{lo:.1f}-{hi:.1f}",
            "n": len(sel),
            "confidence": round(sum(p for p, _ in sel) / len(sel), 4),
            "accuracy": round(sum(o for _, o in sel) / len(sel), 4),
        })
    return out


def collect_scored(answers_by_qid: dict, gold: dict):
    """Pull (probability, outcome) pairs for questions that have a gold label.

    gold values may be:
      - bool  -> noul question
      - str   -> choice question (option key)
      - int/float -> score question (level index)
    """
    probs, outcomes, rows = [], [], []
    for qid, gold_value in gold.items():
        a = answers_by_qid.get(qid)
        if not a:
            continue
        kind = a["kind"]
        if kind == "noul":
            p = float(a["value"])
            o = int(bool(gold_value))
            probs.append(p)
            outcomes.append(o)
            rows.append({"question": qid, "kind": kind, "predicted": p, "gold": gold_value,
                         "correct": abs(p - o) < 0.5})
        elif kind == "choice":
            dist = a["probabilities"] or {}
            p = float(dist.get(gold_value, 0.0))
            o = int(a["value"] == gold_value)
            probs.append(p)
            outcomes.append(o)
            rows.append({"question": qid, "kind": kind, "predicted": a["value"],
                         "p_gold": round(p, 4), "gold": gold_value, "correct": bool(o)})
        elif kind == "score":
            dist = a["probabilities"] or {}
            try:
                p = float(dist.get(str(int(gold_value)), 0.0))
            except (TypeError, ValueError):
                p = 0.0
            o = int(abs(float(a["value"]) - float(gold_value)) < 0.5)
            probs.append(p)
            outcomes.append(o)
            rows.append({"question": qid, "kind": kind, "predicted": a["value"],
                         "p_gold": round(p, 4), "gold": gold_value, "correct": bool(o)})
    return probs, outcomes, rows


def score_case(answers_by_qid: dict, gold: dict) -> dict:
    probs, outcomes, rows = collect_scored(answers_by_qid, gold)
    return {
        "accuracy": round(sum(outcomes) / len(outcomes), 4) if outcomes else None,
        "brier": round(_brier(probs, outcomes), 4) if probs else None,
        "ece": round(_ece(probs, outcomes), 4) if probs else None,
        "rows": rows,
    }


def label_agreement(a: dict, b: dict) -> dict:
    """How often do two providers give the same label for the same question?"""
    shared = set(a) & set(b)
    if not shared:
        return {"compared": 0, "agree": None, "rate": None}
    agree = 0
    for qid in shared:
        av, bv = a[qid]["value"], b[qid]["value"]
        if a[qid]["kind"] == "noul":
            # compare the side of 0.5 the probability falls on
            agree += int((float(av) >= 0.5) == (float(bv) >= 0.5))
        elif a[qid]["kind"] == "score":
            agree += int(abs(float(av) - float(bv)) < 0.5)
        else:
            agree += int(av == bv)
    return {"compared": len(shared), "agree": agree, "rate": round(agree / len(shared), 4)}


def probability_gap(a: dict, b: dict) -> dict:
    """Mean absolute probability difference on shared questions (noul only)."""
    shared = [q for q in set(a) & set(b) if a[q]["kind"] == "noul"]
    if not shared:
        return {"compared": 0, "mean_abs_gap": None, "max_abs_gap": None}
    gaps = [abs(float(a[q]["value"]) - float(b[q]["value"])) for q in shared]
    return {
        "compared": len(shared),
        "mean_abs_gap": round(sum(gaps) / len(gaps), 4),
        "max_abs_gap": round(max(gaps), 4),
    }


def action_change_rate(a: dict, b: dict, thresholds: dict) -> dict:
    """Swap-safety: at a decision threshold, how often does the ACTION change?

    thresholds maps question id -> probability needed to act.
    A question acts when its top probability (or noul probability) clears it.
    """
    compared = changed = 0
    changes = []
    for qid, thr in thresholds.items():
        if qid not in a or qid not in b:
            continue
        compared += 1
        aa, bb = a[qid], b[qid]
        if aa["kind"] == "noul":
            act_a = float(aa["value"]) >= thr
            act_b = float(bb["value"]) >= thr
        else:
            pa = max((aa["probabilities"] or {0: 0}).values(), default=0)
            pb = max((bb["probabilities"] or {0: 0}).values(), default=0)
            act_a, act_b = pa >= thr, pb >= thr
        if act_a != act_b:
            changed += 1
            changes.append({
                "question": qid,
                "a_acts": act_a, "b_acts": act_b,
                "a_value": aa["value"], "b_value": bb["value"],
            })
    return {
        "compared": compared,
        "action_changes": changed,
        "action_change_rate": round(changed / compared, 4) if compared else None,
        "changes": changes,
    }


def aggregate(case_scores: list[dict]) -> dict:
    """Roll per-case metrics into one summary."""
    accs = [c["accuracy"] for c in case_scores if c["accuracy"] is not None]
    eces = [c["ece"] for c in case_scores if c["ece"] is not None]
    briers = [c["brier"] for c in case_scores if c["brier"] is not None]
    n = len(accs) or 1
    return {
        "cases": len(case_scores),
        "scored_cases": len(accs),
        "accuracy": round(sum(accs) / n, 4) if accs else None,
        "mean_ece": round(sum(eces) / (len(eces) or 1), 4) if eces else None,
        "mean_brier": round(sum(briers) / (len(briers) or 1), 4) if briers else None,
    }


def fmt_pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"
