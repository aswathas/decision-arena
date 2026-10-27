"""Quick accessibility sanity check on the built landing page.

Not a full audit - a smoke test for the things that break a static build:
duplicate ids, a missing h1, images without alt text, and unlabelled SVGs.
"""
from __future__ import annotations

import collections
import os
import re

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "site", "dist", "index.html")


def main() -> int:
    with open(PATH, "r", encoding="utf-8") as f:
        html = f.read()

    ids = re.findall(r'id="([^"]+)"', html)
    dupes = [k for k, v in collections.Counter(ids).items() if v > 1]
    img_no_alt = re.findall(r"<img(?![^>]*alt=)", html)
    svg_no_label = re.findall(r"<svg(?![^>]*(aria-labelledby|aria-label))", html)

    print("duplicate ids      :", dupes or "none")
    print("h1 count           :", html.count("<h1"))
    print("h2 count           :", html.count("<h2"))
    print("svg role=img       :", html.count('role="img"'))
    print("svg without a label:", len(svg_no_label))
    print("img without alt    :", len(img_no_alt))
    print("buttons            :", html.count("<button"))
    print("aria-pressed       :", html.count("aria-pressed"))
    print("skip link present  :", "Skip to content" in html)
    lang = re.search(r'<html lang="([^"]+)"', html)
    print("html lang          :", lang.group(1) if lang else "MISSING")
    print("meta description   :", 'name="description"' in html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
