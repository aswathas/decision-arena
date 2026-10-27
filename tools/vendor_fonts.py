"""Vendor the site's webfonts into the repository.

The site claims "no third-party dependencies", so it should not fetch its type
from fonts.googleapis.com on every view either - that is a runtime
dependency, and it is a render-blocking one on the page whose numbers are the
product.

    python tools/vendor_fonts.py

Downloads the latin-subset woff2 files for the families the site uses into
``site/public/fonts/`` and writes ``site/public/fonts/fonts.css`` with
@font-face rules pointing at the local files. The file it writes is committed;
re-run it only when the font set changes.

Stdlib only. Needs network access on first run.
"""
from __future__ import annotations

import os
import re
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "site", "public", "fonts")

# A modern browser UA is required or the API serves ttf instead of woff2.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

FAMILIES = [
    ("IBM Plex Sans", "400"),
    ("IBM Plex Sans", "500"),
    ("IBM Plex Sans", "600"),
    ("IBM Plex Mono", "400"),
    ("IBM Plex Mono", "500"),
]

CSS_URL = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600"
           "&family=IBM+Plex+Mono:wght@400;500&display=swap")

# The fonts are redistributed, so the licence travels with them. IBM Plex is
# under the SIL Open Font License 1.1, which requires the licence and the
# copyright notice to be bundled with the font files.
LICENSE_URL = "https://raw.githubusercontent.com/IBM/plex/master/LICENSE.txt"
LICENSE_NAME = "LICENSE-IBM-Plex.txt"


def fetch(url: str, ua: str = UA) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def slug(family: str, weight: str) -> str:
    return "%s-%s.woff2" % (family.lower().replace(" ", "-"), weight)


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    css = fetch(CSS_URL).decode("utf-8")

    # Each @font-face block carries a comment naming its subset.
    blocks = re.findall(r"/\*\s*([^*]+?)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    wanted = set((f, w) for f, w in FAMILIES)

    rules = []
    for subset, block in blocks:
        if subset.strip() != "latin":
            continue
        family = re.search(r"font-family:\s*'([^']+)'", block)
        weight = re.search(r"font-weight:\s*(\d+)", block)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if not (family and weight and url):
            continue
        key = (family.group(1), weight.group(1))
        if key not in wanted:
            continue
        name = slug(*key)
        path = os.path.join(OUT_DIR, name)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(fetch(url.group(1)))
            print("downloaded", name)
        rules.append("@font-face {\n"
                     "  font-family: '%s';\n"
                     "  font-style: normal;\n"
                     "  font-weight: %s;\n"
                     "  font-display: swap;\n"
                     "  src: url('/fonts/%s') format('woff2');\n"
                     "}" % (key[0], key[1], name))

    if not rules:
        print("no latin @font-face blocks matched - check the families or the API response")
        return 1

    out_css = os.path.join(OUT_DIR, "fonts.css")
    with open(out_css, "w", encoding="utf-8") as f:
        f.write("/* Vendored from Google Fonts by tools/vendor_fonts.py. Self-hosted on\n"
                "   purpose: the site claims no third-party dependencies, and a\n"
                "   render-blocking font request from a third party is one.\n"
                "   The font licence is bundled beside the files as %s. */\n\n"
                % LICENSE_NAME)
        f.write("\n\n".join(rules))
        f.write("\n")
    print("wrote %s with %d face(s)" % (out_css, len(rules)))

    license_path = os.path.join(OUT_DIR, LICENSE_NAME)
    if not os.path.exists(license_path):
        with open(license_path, "wb") as f:
            f.write(fetch(LICENSE_URL))
        print("downloaded", LICENSE_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
