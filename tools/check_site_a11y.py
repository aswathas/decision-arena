"""Quick accessibility sanity check on the built site.

Not a full audit - a smoke test for the things that break a static build:
duplicate ids, a missing h1, images without alt text, unlabelled SVGs, and
pages that drift from the shared chrome.

Every built page is checked, not just the landing page: the course reader
adds 47 more, and a broken one of those is just as broken as a broken landing
page. The landing page keeps its own summary, because that is the page a
reader lands on.

Usage:
    python tools/check_site_a11y.py
"""
from __future__ import annotations

import collections
import os
import re
import sys

DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "site", "dist")

ID_RE = re.compile(r'id="([^"]+)"')
IMG_NO_ALT_RE = re.compile(r"<img(?![^>]*alt=)")
SVG_NO_LABEL_RE = re.compile(r"<svg(?![^>]*(aria-labelledby|aria-label))")
HREF_RE = re.compile(r'href="(/[^"#?]*)"')
ANCHOR_RE = re.compile(r'href="#([^"]+)"')


def built_pages() -> list[str]:
    """Every built HTML page, relative to dist/."""
    pages = []
    for root, _dirs, files in os.walk(DIST):
        for name in files:
            if name.endswith(".html"):
                full = os.path.join(root, name)
                pages.append(os.path.relpath(full, DIST).replace("\\", "/"))
    return sorted(pages)


def check(path: str) -> list[str]:
    """Return the problems on one page. An empty list means it passed."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    problems: list[str] = []

    ids = ID_RE.findall(html)
    dupes = [k for k, v in collections.Counter(ids).items() if v > 1]
    if dupes:
        problems.append("duplicate ids: %s" % ", ".join(dupes))

    if html.count("<h1") != 1:
        problems.append("expected exactly one h1, found %d" % html.count("<h1"))

    if IMG_NO_ALT_RE.search(html):
        problems.append("an image has no alt attribute")

    if SVG_NO_LABEL_RE.search(html):
        problems.append("an svg has no label")

    if "Skip to content" not in html:
        problems.append("the skip link is missing")

    if not re.search(r'<html lang="[^"]+"', html):
        problems.append("the html element has no lang")

    if 'name="description"' not in html:
        problems.append("the meta description is missing")

    # An in-page link that lands on nothing is a dead end. The lesson rail
    # depends on the rendered heading ids, so this check is what proves the
    # rail's anchors and the markdown's ids agree.
    anchors = set(ANCHOR_RE.findall(html))
    if anchors:
        ids = set(ID_RE.findall(html))
        for anchor in sorted(anchors):
            if anchor not in ids:
                problems.append("an in-page link points at #%s, which is not on the page" % anchor)

    return problems


def site_base(links: dict[str, set[str]]) -> str:
    """The sub-path the site was built for.

    A root deployment serves "/" and a GitHub Pages project page serves
    "/decision-arena/". Every internal link carries it, so the common prefix
    of the page links is the base - and the base is what has to be stripped
    before a link can be resolved against the build directory.
    """
    page_links = [h for targets in links.values() for h in targets if h.endswith("/")]
    if not page_links:
        return "/"
    base = os.path.commonprefix(page_links)
    return base if base.endswith("/") else base + "/"


def resolves(target: str, base: str) -> bool:
    """Does an internal href point at something the build actually produced?

    A link with no extension is a page (`/course/` -> `course/index.html`);
    a link with an extension is an asset (`/fonts/fonts.css`).
    """
    if target.startswith(base):
        path = target[len(base):]
    else:
        path = target.lstrip("/")
    if not path:
        return os.path.isfile(os.path.join(DIST, "index.html"))
    path = path.replace("/", os.sep)
    if os.path.splitext(path)[1]:
        return os.path.isfile(os.path.join(DIST, path))
    if path.endswith(os.sep) or path == "":
        return os.path.isfile(os.path.join(DIST, path, "index.html"))
    return os.path.isfile(os.path.join(DIST, path))


def internal_links() -> dict[str, set[str]]:
    """Every internal link target on every page."""
    links: dict[str, set[str]] = {}
    for page in built_pages():
        full = os.path.join(DIST, page)
        with open(full, "r", encoding="utf-8") as f:
            html = f.read()
        links[page] = set(HREF_RE.findall(html))
    return links


def main() -> int:
    if not os.path.isdir(DIST):
        print("FAIL: no build at %s - run `cd site && npm run build`" % DIST)
        return 1

    pages = built_pages()
    if not pages:
        print("FAIL: no HTML pages in %s" % DIST)
        return 1

    problems = 0
    for page in pages:
        found = check(os.path.join(DIST, page))
        if found:
            problems += 1
            print("FAIL %s" % page)
            for p in found:
                print("       - %s" % p)

    # A link to something that was never built is a dead end for the reader.
    links = internal_links()
    base = site_base(links)
    for page, targets in links.items():
        for target in sorted(targets):
            if target.startswith("/_astro"):
                continue
            if not resolves(target, base):
                problems += 1
                print("FAIL %s links to %s, which was not built" % (page, target))

    print("site base            :", base)

    print()
    print("pages checked       :", len(pages))
    print("pages with problems :", problems)
    if problems:
        print("\n%d problem(s) found." % problems)
        return 1
    print("\nOK: every built page passes the smoke check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
