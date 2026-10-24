"""The measurement runner: calls providers, records raw evidence, enforces a spend cap.

Design rules borrowed from the only credible public harness in this field
(rmax-ai/jev-vs-clef):
  * every call is logged to JSONL with raw provider output
  * the run writes a meta.json with a timestamp, provider, and battery hash
  * a spend cap aborts the run
  * a dry-run mode prints what would happen without calling anything
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field

from . import metrics
from .providers import Provider


def battery_hash(cases: list[dict]) -> str:
    blob = json.dumps(cases, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def load_cases(path: str) -> list[dict]:
    """Load cases from a .json array file or a .jsonl file (one object per line)."""
    cases: list[dict] = []
    if path.endswith(".jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cases.append(json.loads(line))
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cases = data["cases"] if isinstance(data, dict) else data
    return cases


@dataclass
class RunResult:
    provider: str
    started_at: str
    finished_at: str
    meta: dict
    records: list[dict] = field(default_factory=list)
    scores: list[dict] = field(default_factory=list)
    cost_total: float = 0.0
    aborted: bool = False
    abort_reason: str = ""


def run_battery(provider: Provider, cases: list[dict], repeats: int = 1,
                spend_cap: float = 0.25, dry_run: bool = False,
                out_dir: str = "runs", label: str = "") -> RunResult:
    started = time.time()
    run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{provider.name.replace(':', '-')}"
    os.makedirs(out_dir, exist_ok=True)
    records: list[dict] = []
    scores: list[dict] = []
    cost = 0.0
    aborted = False
    reason = ""

    for case in cases:
        for rep in range(repeats):
            if cost >= spend_cap:
                aborted, reason = True, f"spend cap ${spend_cap} reached"
                break
            t0 = time.perf_counter()
            error = None
            answers: dict = {}
            try:
                if not dry_run:
                    answers = provider.decide(case["state"], case["questions"])
            except Exception as exc:  # keep the run alive, record the failure
                error = f"{type(exc).__name__}: {exc}"
            dt = time.perf_counter() - t0

            usage = getattr(provider, "_last_usage", {}) or {}
            call_cost = provider.estimate_cost(usage) if not dry_run else 0.0
            cost += call_cost

            rec = {
                "run_id": run_id,
                "case_id": case.get("id"),
                "group": case.get("group"),
                "case_class": case.get("class"),
                "repeat": rep,
                "ts": time.time(),
                "latency_s": round(dt, 4),
                "usage": usage,
                "cost_usd": round(call_cost, 8),
                "error": error,
                "answers": answers,
                "gold": case.get("gold"),
            }
            records.append(rec)

            if case.get("gold") and answers and not error:
                s = metrics.score_case(answers, case["gold"])
                s["case_id"] = case.get("id")
                s["group"] = case.get("group")
                scores.append(s)
        if aborted:
            break

    finished = time.time()
    meta = {
        "run_id": run_id,
        "provider": provider.name,
        "price_per_mtok": provider.price_per_mtok,
        "cases": len(cases),
        "repeats": repeats,
        "battery_hash": battery_hash(cases),
        "dry_run": dry_run,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(started)),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(finished)),
        "duration_s": round(finished - started, 2),
        "cost_usd": round(cost, 8),
        "spend_cap_usd": spend_cap,
        "uuid": str(uuid.uuid4()),
    }

    if not dry_run:
        with open(os.path.join(out_dir, f"{run_id}.jsonl"), "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, default=str) + "\n")
        with open(os.path.join(out_dir, f"{run_id}.meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    return RunResult(
        provider=provider.name, started_at=meta["started_at"], finished_at=meta["finished_at"],
        meta=meta, records=records, scores=scores, cost_total=cost,
        aborted=aborted, abort_reason=reason,
    )


# ------------------------------------------------------------ format friction
FORMAT_BUILDERS = {
    "prose": lambda payload: payload["prose"],
    "flat": lambda payload: payload["flat"],
    "nested": lambda payload: payload["nested"],
}


def run_format_friction(provider: Provider, cases: list[dict], formats=("prose", "flat", "nested"),
                         out_dir: str = "runs", label: str = "") -> dict:
    """Measure how much a probability moves when only the SHAPE of the state changes.

    Requires no labels. This is the cheapest experiment in the field.
    """
    os.makedirs(out_dir, exist_ok=True)
    run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-friction-{provider.name.replace(':', '-')}"
    rows = []
    for case in cases:
        variants = case.get("variants") or {}
        if not variants:
            continue
        per_format = {}
        for fmt in formats:
            state = FORMAT_BUILDERS[fmt](variants)
            t0 = time.perf_counter()
            answers = provider.decide(state, case["questions"])
            dt = time.perf_counter() - t0
            per_format[fmt] = {"answers": answers, "latency_s": round(dt, 4)}
        for qid in case["questions"]:
            vals = {}
            for fmt in formats:
                a = per_format[fmt]["answers"].get(qid)
                if not a:
                    continue
                if a["kind"] == "noul":
                    vals[fmt] = float(a["value"])
                else:
                    vals[fmt] = float(max((a["probabilities"] or {0: 0}).values(), default=0))
            if len(vals) < 2:
                continue
            spread = max(vals.values()) - min(vals.values())
            rows.append({
                "run_id": run_id, "case_id": case.get("id"), "question": qid,
                "kind": case["questions"][qid].get("type"),
                "values": {k: round(v, 4) for k, v in vals.items()},
                "spread": round(spread, 4),
                "flips_at_0.5": len({(v >= 0.5) for v in vals.values()}) > 1,
            })
    report = {
        "run_id": run_id, "provider": provider.name,
        "cases": len({r["case_id"] for r in rows}),
        "questions_measured": len(rows),
        "mean_spread": round(sum(r["spread"] for r in rows) / len(rows), 4) if rows else None,
        "max_spread": round(max((r["spread"] for r in rows), default=0), 4),
        "flips_at_0.5": sum(1 for r in rows if r["flips_at_0.5"]),
        "rows": rows,
    }
    with open(os.path.join(out_dir, f"{run_id}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report
