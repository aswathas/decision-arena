"""Markdown report generation for a DecisionArena run."""
from __future__ import annotations

import json
from collections import defaultdict

from . import metrics


def _table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def run_report(result) -> str:
    agg = metrics.aggregate(result.scores)
    lines = []
    if result.provider.startswith("mock"):
        lines += ["> [!] **SIMULATED RUN - `mock` provider.** These numbers come from an offline",
                  "> simulator that exists to test the harness. They are **not** a measurement of",
                  "> any real model and must never be quoted as evidence.", ""]
    lines += [
        f"# DecisionArena run - {result.provider}",
        "",
        f"- run id: `{result.meta['run_id']}`",
        f"- started: {result.meta['started_at']}  finished: {result.meta['finished_at']}",
        f"- battery hash: `{result.meta['battery_hash']}`  cases: {result.meta['cases']}  repeats: {result.meta['repeats']}",
        f"- cost: **${result.cost_total:.6f}** (cap ${result.meta['spend_cap_usd']})",
    ]
    if result.aborted:
        lines.append(f"- [!] **ABORTED**: {result.abort_reason}")
    lines += ["", "## Headline", ""]
    lines.append(_table(
        ["metric", "value"],
        [
            ["scored cases", agg["scored_cases"]],
            ["accuracy", metrics.fmt_pct(agg["accuracy"])],
            ["mean ECE", agg["mean_ece"] if agg["mean_ece"] is not None else "n/a"],
            ["mean Brier", agg["mean_brier"] if agg["mean_brier"] is not None else "n/a"],
        ]))

    lat = sorted(r["latency_s"] for r in result.records if r["latency_s"] is not None)
    if lat:
        def pct(p):
            return round(lat[min(int(len(lat) * p), len(lat) - 1)], 4)
        lines += ["", "## Latency", "",
                  _table(["p50", "p95", "max"],
                          [[pct(0.5), pct(0.95), round(lat[-1], 4)]])]

    errors = [r for r in result.records if r.get("error")]
    if errors:
        lines += ["", "## Errors", "",
                  _table(["case", "error"],
                          [[e["case_id"], e["error"][:120]] for e in errors])]

    by_group = defaultdict(list)
    for s in result.scores:
        by_group[s.get("group") or "?"].append(s)
    if by_group:
        lines += ["", "## By group", ""]
        rows = []
        for g, ss in sorted(by_group.items()):
            a = metrics.aggregate(ss)
            rows.append([g, a["scored_cases"], metrics.fmt_pct(a["accuracy"]),
                         a["mean_ece"], a["mean_brier"]])
        lines.append(_table(["group", "cases", "accuracy", "mean ECE", "mean Brier"], rows))

    # determinism: identical repeats of the same case
    det = []
    by_case = defaultdict(list)
    for r in result.records:
        if not r.get("error"):
            by_case[r["case_id"]].append(json.dumps(r["answers"], sort_keys=True))
    for cid, payloads in by_case.items():
        if len(payloads) > 1:
            det.append((cid, len(set(payloads)) == 1))
    if det:
        stable = sum(1 for _, ok in det if ok)
        lines += ["", "## Determinism", "",
                  f"**{stable}/{len(det)}** cases returned byte-identical answers across repeats."]
        if stable != len(det):
            lines += ["", _table(["case", "identical"],
                                  [[c, "yes" if ok else "no"] for c, ok in det if not ok])]
    return "\n".join(lines)


def friction_report(report: dict) -> str:
    lines = [
        f"# Format friction - {report['provider']}",
        "",
        f"- run id: `{report['run_id']}`",
        f"- cases: {report['cases']}   questions measured: {report['questions_measured']}",
        f"- **mean spread: {report['mean_spread']}**   max spread: {report['max_spread']}",
        f"- questions whose side of 0.5 flips across formats: **{report['flips_at_0.5']}**",
        "",
        "A large spread means the serialisation shape of your state is silently changing",
        "your decisions. This is measured with no outcome labels at all.",
        "",
        _table(["case", "question", "kind", "prose", "flat", "nested", "spread", "flips@0.5"],
               [[r["case_id"], r["question"], r["kind"],
                 r["values"].get("prose"), r["values"].get("flat"), r["values"].get("nested"),
                 r["spread"], "YES" if r["flips_at_0.5"] else ""]
                for r in report["rows"]]),
    ]
    return "\n".join(lines)


def swap_report(matrix: dict) -> str:
    lines = ["# Swap safety", ""]
    for pair, data in matrix.items():
        lines += [
            f"## {pair}",
            "",
            _table(["metric", "value"],
                   [["label agreement", metrics.fmt_pct(data["agreement"]["rate"])],
                    ["questions compared", data["agreement"]["compared"]],
                    ["mean probability gap (noul)",
                     data["probability_gap"]["mean_abs_gap"] if data["probability_gap"]["mean_abs_gap"] is not None else "n/a"],
                    ["max probability gap (noul)", data["probability_gap"]["max_abs_gap"]],
                    ["action change rate at threshold",
                     metrics.fmt_pct(data["action_change"]["action_change_rate"])],
                    ["actions changed", f"{data['action_change']['action_changes']}/{data['action_change']['compared']}"]]),
            "",
        ]
        changes = data["action_change"]["changes"]
        if changes:
            lines += ["### Decisions that would change", "",
                      _table(["case", "question", "A acts", "B acts", "A value", "B value"],
                             [[c["case_id"], c["question"], c["a_acts"], c["b_acts"],
                               c["a_value"], c["b_value"]] for c in changes]),
                      ""]
    return "\n".join(lines)
