"""DecisionArena CLI.

    python -m decisionarena providers
    python -m decisionarena run --provider mock --battery routing
    python -m decisionarena run --provider jev --battery routing --repeats 3
    python -m decisionarena friction --provider clef:clef-flash
    python -m decisionarena swap --provider a=jev --provider b=clef:clef-flash
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import harness, metrics, providers, report

CASES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases")
BATTERIES = {
    "routing": "routing.json",
    "injection": "injection.json",
    "format": "format_variants.json",
    "all": None,
}


def _load_battery(name: str) -> list[dict]:
    cases: list[dict] = []
    if name == "all":
        for fn in ("routing.json", "injection.json"):
            cases += harness.load_cases(os.path.join(CASES_DIR, fn))
    else:
        cases = harness.load_cases(os.path.join(CASES_DIR, BATTERIES[name]))
    return cases


def cmd_providers(args):
    print(f"{'spec':<20}{'configured':<12}note")
    print("-" * 100)
    for spec, ok, note in providers.available_providers():
        print(f"{spec:<20}{('yes' if ok else 'no'):<12}{note}")
    print()
    print("Set credentials in the environment (see .env.example):")
    print("  TYPESAFE_API_KEY          for jev")
    print("  CLOUDFLARE_ACCOUNT_ID     + CLOUDFLARE_AUTH_TOKEN  for clef")
    print("  OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL     for oai (e.g. pplx-decider)")


def cmd_run(args):
    provider = providers.build_provider(args.provider)
    cases = _load_battery(args.battery)
    print(f"provider : {provider.name}")
    print(f"battery  : {args.battery}  ({len(cases)} cases, repeats={args.repeats})")
    print(f"price    : ${provider.price_per_mtok}/Mtok")
    if args.dry_run:
        print("DRY RUN - no calls will be made")
        for c in cases:
            print(f"  - {c['id']} [{c.get('class')}] questions={list(c['questions'].keys())}")
        return 0

    result = harness.run_battery(provider, cases, repeats=args.repeats,
                                 spend_cap=args.spend_cap, dry_run=False,
                                 out_dir=args.out_dir)
    text = report.run_report(result)
    print(text)
    out_md = os.path.join(args.out_dir, f"{result.meta['run_id']}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nreport written to {out_md}")
    print(f"raw evidence: {os.path.join(args.out_dir, result.meta['run_id'] + '.jsonl')}")
    return 0


def cmd_friction(args):
    provider = providers.build_provider(args.provider)
    cases = harness.load_cases(os.path.join(CASES_DIR, "format_variants.json"))
    print(f"provider : {provider.name}")
    print(f"cases    : {len(cases)}")
    rep = harness.run_format_friction(provider, cases, out_dir=args.out_dir)
    text = report.friction_report(rep)
    print(text)
    out_md = os.path.join(args.out_dir, f"{rep['run_id']}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"report written to {out_md}")
    print(f"raw evidence: {os.path.join(args.out_dir, rep['run_id'] + '.jsonl')}")
    return 0


def cmd_swap(args):
    # --provider a=jev  ->  label "a", provider spec "jev"
    specs = []
    for a in args.provider:
        label, sep, spec = a.partition("=")
        if not sep:
            label, spec = a, a
        specs.append((label.strip(), spec.strip()))
    if len(specs) != 2:
        print("swap needs exactly two providers: --provider a=jev --provider b=clef:clef-flash")
        return 2

    cases = _load_battery(args.battery)
    results = {}
    for label, spec in specs:
        p = providers.build_provider(spec)
        print(f"running {p.name} over {len(cases)} cases ...")
        results[label] = (p, harness.run_battery(p, cases, repeats=args.repeats,
                                                  spend_cap=args.spend_cap, out_dir=args.out_dir))

    (la, (pa, ra)), (lb, (pb, rb)) = list(results.items())
    key = f"{pa.name} vs {pb.name}"

    # per-question answers from the first repeat of each case
    first_a, first_b = {}, {}
    for x, y in zip(ra.records, rb.records):
        if x.get("error") or y.get("error"):
            continue
        for qid, av in x["answers"].items():
            first_a.setdefault(qid, av)
        for qid, bv in y["answers"].items():
            first_b.setdefault(qid, bv)

    thresholds = {}
    for c in cases:
        if c.get("thresholds"):
            thresholds = c["thresholds"]
            break

    agreement = metrics.label_agreement(first_a, first_b)
    gap = metrics.probability_gap(first_a, first_b)

    compared = changed = 0
    changes = []
    for x, y in zip(ra.records, rb.records):
        if x.get("error") or y.get("error"):
            continue
        case = next((c for c in cases if c["id"] == x["case_id"]), None)
        thr = (case or {}).get("thresholds") or thresholds
        per = metrics.action_change_rate(x["answers"], y["answers"], thr)
        for ch in per["changes"]:
            ch["case_id"] = x["case_id"]
        compared += per["compared"]
        changed += per["action_changes"]
        changes.extend(per["changes"])

    matrix = {key: {
        "agreement": agreement,
        "probability_gap": gap,
        "action_change": {
            "compared": compared,
            "action_changes": changed,
            "action_change_rate": round(changed / compared, 4) if compared else None,
            "changes": changes,
        },
    }}

    text = report.swap_report(matrix)
    print(text)
    out_md = os.path.join(args.out_dir, "swap-report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"report written to {out_md}")
    return 0


def main(argv=None):
    # Windows consoles default to cp1252; never crash on a unicode report line
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="decisionarena",
                                 description="Neutral benchmark harness for decision models")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("providers", help="list providers and whether they are configured")
    p.set_defaults(func=cmd_providers)

    p = sub.add_parser("run", help="run a battery against one provider")
    p.add_argument("--provider", required=True, help="jev | clef[:model] | mock | oai[:model]")
    p.add_argument("--battery", default="routing", choices=list(BATTERIES.keys()))
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--spend-cap", type=float, default=0.25)
    p.add_argument("--out-dir", default="runs")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("friction", help="measure state-format sensitivity (no labels needed)")
    p.add_argument("--provider", required=True)
    p.add_argument("--out-dir", default="runs")
    p.set_defaults(func=cmd_friction)

    p = sub.add_parser("swap", help="compare two providers: agreement, gap, action-change rate")
    p.add_argument("--provider", action="append", required=True,
                   help="repeat twice: a=jev b=clef:clef-flash")
    p.add_argument("--battery", default="routing", choices=list(BATTERIES.keys()))
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--spend-cap", type=float, default=0.25)
    p.add_argument("--out-dir", default="runs")
    p.set_defaults(func=cmd_swap)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
