"""Render and check a LinkedIn post from a JSON spec.

    python tools/linkedin_post.py --spec docs/linkedin/specs/<slug>.json
    python tools/linkedin_post.py --spec <file> --check     # gates only, no write
    python tools/linkedin_post.py --spec <file> --out <file>

The spec is the source of truth. This tool renders the post, checks it against
the reach and honesty rules below, and refuses to write a post that fails.

Why a tool and not a prompt: the rules that matter (hook length, one idea per
line, hashtag count, alt text, evidence present, no banned hype) are checks,
not vibes. A script cannot be talked out of them.

Costs: file read and write only. No network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# LinkedIn's hard ceiling on a post body. Headlines get truncated well before
# this, but the limit is what the platform rejects at.
MAX_TOTAL = 3000

# The feed folds a post after roughly this many characters, so the hook has to
# survive on its own.
MAX_HOOK = 200

# A post that names three tags reads as a person; ten reads as a marketer.
MIN_TAGS = 3
MAX_TAGS = 5

# Banned hype words. Each one has been used to sell nothing by every founder
# on the platform, so they flatten the credibility of the real claim next to
# them. Matched case-insensitively on a word boundary.
BANNED = [
    "revolutionary", "game-changer", "game changer", "disruptive",
    "unleash", "unlock the power", "supercharge", "seamless", "seamlessly",
    "delve", "leverage", "cutting-edge", "next-level", "mind-blowing",
    "incredible journey", "we are excited to announce", "thrilled to announce",
]

# The house rule: a number must be able to name its source. A post that cites
# a file, a run id or a live URL passes this; a post that cites a vibe does not.
EVIDENCE_MARKERS = [
    "http://", "https://", "runs/", "docs/", "site/", "course/", "tools/",
    "commit ", "PR #", "issue #", ".md", ".json", ".astro",
]

TAG_RE = re.compile(r"^[A-Za-z0-9]+$")


def _fail(errors: List[str], message: str) -> None:
    errors.append(message)


def check_spec(spec: Dict[str, Any], base_dir: str) -> Tuple[List[str], str]:
    """Check a post spec. Returns (errors, rendered body)."""
    errors: List[str] = []

    hook = (spec.get("hook") or "").strip()
    if not hook:
        _fail(errors, "hook is empty")
    elif len(hook) > MAX_HOOK:
        _fail(errors, "hook is %d chars, must be <= %d (the feed folds it)" % (len(hook), MAX_HOOK))

    body_lines: List[str] = []
    for para in spec.get("body") or []:
        text = str(para).strip()
        if text:
            body_lines.append(text)
    if not body_lines:
        _fail(errors, "body is empty")
    for para in body_lines:
        if len(para) > 600:
            _fail(errors, "a body paragraph is %d chars; break it up (max 600)" % len(para))

    links = [l for l in (spec.get("links") or []) if l.get("url")]
    if not links:
        _fail(errors, "no link: a post with no destination gets no return visit")
    for link in links:
        if not str(link.get("url", "")).startswith("https://"):
            _fail(errors, "link %r is not https" % link.get("url"))

    tags = [t for t in (spec.get("hashtags") or []) if str(t).strip()]
    if not (MIN_TAGS <= len(tags) <= MAX_TAGS):
        _fail(errors, "%d hashtags, need %d-%d" % (len(tags), MIN_TAGS, MAX_TAGS))
    for tag in tags:
        if not TAG_RE.match(str(tag)):
            _fail(errors, "hashtag %r is not a plain word" % tag)

    images = spec.get("images") or []
    for image in images:
        path = image.get("path") or ""
        if not path:
            _fail(errors, "an image has no path")
            continue
        full = path if os.path.isabs(path) else os.path.join(base_dir, path)
        if not os.path.isfile(full):
            _fail(errors, "image not found: %s" % path)
        elif os.path.getsize(full) > 12 * 1024 * 1024:
            _fail(errors, "image is over 12MB: %s" % path)
        if not (image.get("alt") or "").strip():
            _fail(errors, "image %s has no alt text" % path)

    evidence = [e for e in (spec.get("evidence") or []) if str(e).strip()]
    if not evidence:
        _fail(errors, "no evidence lines: every claim needs a source")
    else:
        joined = " ".join(str(e) for e in evidence)
        if not any(marker in joined for marker in EVIDENCE_MARKERS):
            _fail(errors, "no evidence line names a source (a file, a run id or a URL)")

    haystack = " ".join([hook] + body_lines + [str(e) for e in evidence]
                        + [str(l.get("label", "")) for l in links]
                        + [str(t) for t in tags]).lower()
    for word in BANNED:
        if word in haystack:
            _fail(errors, "banned hype word: %r" % word)

    if not (spec.get("cta") or "").strip():
        _fail(errors, "no call to action")

    rendered = render(spec)
    if len(rendered) > MAX_TOTAL:
        _fail(errors, "rendered post is %d chars, over the %d limit" % (len(rendered), MAX_TOTAL))

    return errors, rendered


def render(spec: Dict[str, Any]) -> str:
    """Render the post body exactly as it should be pasted. No file IO."""
    lines: List[str] = []
    hook = (spec.get("hook") or "").strip()
    if hook:
        lines.append(hook)
    for para in spec.get("body") or []:
        text = str(para).strip()
        if text:
            lines.append("")
            lines.append(text)
    if spec.get("cta"):
        lines.append("")
        lines.append(str(spec["cta"]).strip())
    tags = [str(t).strip() for t in (spec.get("hashtags") or []) if str(t).strip()]
    if tags:
        lines.append("")
        lines.append(" ".join("#" + t for t in tags))
    return "\n".join(lines).strip()


def render_document(spec: Dict[str, Any], rendered: str, errors: List[str]) -> str:
    """Render the full artefact: the post, then the attachment plan."""
    out: List[str] = []
    out.append("---")
    out.append("slug: %s" % spec.get("slug", "post"))
    out.append("date: %s" % spec.get("date", ""))
    out.append("format: %s" % spec.get("format", "teaching-post"))
    out.append("status: %s" % ("draft" if errors else "ready"))
    out.append("---")
    out.append("")
    out.append("# %s" % (spec.get("title") or spec.get("slug", "LinkedIn post")))
    out.append("")
    out.append("## The post")
    out.append("")
    out.append(rendered)
    out.append("")
    first = (spec.get("first_comment") or "").strip()
    if first:
        out.append("## First comment")
        out.append("")
        out.append(first)
        out.append("")
    out.append("## Attachments")
    out.append("")
    for image in spec.get("images") or []:
        out.append("- `%s` - %s" % (image.get("path", ""), image.get("alt", "")))
        if image.get("caption"):
            out.append("  - caption: %s" % image["caption"])
    out.append("")
    out.append("## Links")
    out.append("")
    for link in spec.get("links") or []:
        out.append("- %s - %s" % (link.get("label", ""), link.get("url", "")))
    out.append("")
    out.append("## Evidence")
    out.append("")
    for item in spec.get("evidence") or []:
        out.append("- %s" % item)
    out.append("")
    out.append("## Checks")
    out.append("")
    if errors:
        for error in errors:
            out.append("- FAIL: %s" % error)
    else:
        out.append("- all checks pass (%d chars, %d tags, %d images)"
                   % (len(rendered), len(spec.get("hashtags") or []), len(spec.get("images") or [])))
    out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="linkedin_post",
                                 description="render and check a LinkedIn post spec")
    ap.add_argument("--spec", required=True, help="path to the JSON spec")
    ap.add_argument("--out", help="where to write the rendered post (default: stdout)")
    ap.add_argument("--check", action="store_true", help="check only, write nothing")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.spec):
        print("no such spec: %s" % args.spec)
        return 1
    with open(args.spec, "r", encoding="utf-8") as handle:
        spec = json.load(handle)

    base_dir = os.path.dirname(os.path.abspath(args.spec))
    errors, rendered = check_spec(spec, base_dir)

    if errors:
        print("post failed %d check(s):" % len(errors))
        for error in errors:
            print("  - %s" % error)
        if not args.check:
            print("\nNothing written. Fix the spec and run again.")
        return 1

    if args.check:
        print("post passes every check (%d chars)" % len(rendered))
        return 0

    document = render_document(spec, rendered, errors)
    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(REPO_ROOT, args.out)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(document)
        print("wrote %s" % out_path)
    else:
        print(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
