"""The figures gate: every lesson must carry a story, a diagram and a picture.

    python tools/check_course_figures.py            # check
    python tools/check_course_figures.py --list     # what is missing, per lesson

This is the "never publish a broken lesson" rule applied to the illustrated
course. A figure with no description, a story that teaches nothing, or a
picture that was never downloaded is a promise the site cannot keep, so the
gate fails the commit.

Run it after changing lessons, figures or illustrations:

    python tools/check_course_figures.py
    python tools/course_check.py --check
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import course_lib as cl  # noqa: E402

FIGURES_DIR = os.path.join(REPO, "site", "src", "figures")
ILLUSTRATIONS_DIR = os.path.join(REPO, "site", "public", "illustrations")

STORY_HEADING = "The story"
STORY_MIN_WORDS = 120
STORY_MAX_WORDS = 220
MAX_IMAGE_BYTES = 400 * 1024

# The colours the site is allowed to draw with. A literal outside this set
# is drift, and drift is how a design system dies.
ALLOWED_COLOURS = {
    "#0b1218", "#45555f", "#5d6b76", "#cfd9e0", "#dfe7ec", "#0f3d6e",
    "#e2ebf4", "#f2f5f7", "#e7edf1", "#8a97a1",
}
COLOUR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
REMOTE_RE = re.compile(r"(https?:)?//(?!www\.w3\.org)", re.IGNORECASE)

# Constructs the site does not use. Each of these was found in a hand-written
# figure at some point, and each of them is invisible to a colour check.
BANNED_MARKUP = [
    (re.compile(r"<\s*linearGradient", re.IGNORECASE), "a gradient"),
    (re.compile(r"<\s*radialGradient", re.IGNORECASE), "a gradient"),
    (re.compile(r"\bfilter\s*=", re.IGNORECASE), "a filter"),
    (re.compile(r"drop-shadow", re.IGNORECASE), "a drop shadow"),
    (re.compile(r"\brx\s*[:=]", re.IGNORECASE), "a rounded corner"),
    (re.compile(r"\bon[a-z]+\s*=\s*[\"']", re.IGNORECASE), "an inline event handler"),
    (re.compile(r"<\s*script", re.IGNORECASE), "a script"),
]

# The story has to sit between the two sections that make it work: the naive
# story breaks, the story makes the real thing imaginable, then the real thing
# is named.
STORY_AFTER = "What breaks"
STORY_BEFORE = "The real thing"

MOTION_PRIMITIVE_RE = re.compile(r"\bm-(draw|rise|pulse|fade|sweep)\b")
TAG_RE = re.compile(r"<[^<>]*>")


def figure_path(lesson_id: str) -> str:
    return os.path.join(FIGURES_DIR, "%s.astro" % lesson_id)


def illustration_path(lesson_id: str) -> str:
    for ext in (".jpg", ".jpeg", ".png"):
        path = os.path.join(ILLUSTRATIONS_DIR, "%s%s" % (lesson_id, ext))
        if os.path.exists(path):
            return path
    return os.path.join(ILLUSTRATIONS_DIR, "%s.jpg" % lesson_id)


def check_figure(lesson_id: str, path: str) -> list[str]:
    """Return the problems with one figure component."""
    problems: list[str] = []
    if not os.path.exists(path):
        return ["no figure component at %s" % os.path.relpath(path, REPO)]

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    if "<title" not in src:
        problems.append("the figure has no <title> for the accessible name")
    if "<desc" not in src:
        problems.append("the figure has no <desc> describing the drawing")
    if "aria-labelledby" not in src:
        problems.append("the figure is not labelled by its title and desc")
    if "<figcaption" not in src:
        problems.append("the figure has no caption")
    if "<script" in src:
        problems.append("the figure contains a script")

    # The accessible name has to be real: the ids aria-labelledby names must
    # exist, and the title and desc must carry those ids. A figure can pass a
    # keyword check with an aria-labelledby that points at nothing.
    ids = set(re.findall(r'\bid="([^"]+)"', src))
    labelled = re.search(r'aria-labelledby="([^"]+)"', src)
    if labelled:
        for ref in labelled.group(1).split():
            if ref not in ids:
                problems.append("aria-labelledby names %r, and no element has that id" % ref)
    for tag in ("title", "desc"):
        found = re.search(r"<%s\b([^>]*)>" % tag, src)
        if found and 'id="' not in found.group(1):
            problems.append("the <%s> has no id for aria-labelledby to name" % tag)

    # The picture belongs inside the plate, before the diagram, and it needs
    # alt text: for a screen reader that alt text is the whole description.
    img = re.search(r'<img\b[^>]*class="[^"]*fig__picture[^"]*"[^>]*>', src)
    if not img:
        problems.append("the figure does not show its picture (no .fig__picture image)")
    else:
        alt = re.search(r'\balt="([^"]*)"', img.group(0))
        if not alt or not alt.group(1).strip():
            problems.append("the figure's picture has no alt text")
        if src.find("<svg") != -1 and img.start() > src.find("<svg"):
            problems.append("the picture comes after the diagram; it must come first")

    # The drawing has to move, and the motion has to be switchable.
    if not MOTION_PRIMITIVE_RE.search(src) and "@keyframes" not in src:
        problems.append("the figure has no motion")
    if "@keyframes" in src and "prefers-reduced-motion" not in src:
        problems.append("the figure has its own keyframes but no reduced-motion rule")

    # Every element that draws itself must say how long it is, or the stroke
    # is cut short at the end of the animation.
    for tag in TAG_RE.findall(src):
        if "m-draw" in tag and "--m-length" not in tag:
            problems.append("an .m-draw element does not author --m-length")
            break

    for pattern, what in BANNED_MARKUP:
        if pattern.search(src):
            problems.append("the figure uses %s" % what)

    view = re.search(r'viewBox="([^"]+)"', src)
    if not view:
        problems.append("the figure has no viewBox")
    else:
        parts = view.group(1).split()
        if len(parts) != 4:
            problems.append("the viewBox is not 'min-x min-y width height'")
        else:
            try:
                w, h = float(parts[2]), float(parts[3])
                if w < 200 or h < 120 or w > 2000 or h > 2000:
                    problems.append("the viewBox is an odd size: %s x %s" % (w, h))
            except ValueError:
                problems.append("the viewBox is not numeric")

    for match in REMOTE_RE.finditer(src):
        problems.append("the figure references something remote: %s" % match.group(0))

    for colour in set(COLOUR_RE.findall(src)):
        if colour.lower() not in ALLOWED_COLOURS:
            problems.append("the figure uses a colour outside the palette: %s" % colour)

    return problems


def check_story(lesson: dict) -> list[str]:
    """Return the problems with a lesson's story section."""
    problems: list[str] = []
    sections = lesson.get("_sections") or {}
    story = sections.get(STORY_HEADING)
    if not story or not story.strip():
        return ["the lesson has no '## %s' section" % STORY_HEADING]
    words = len(story.split())
    if words < STORY_MIN_WORDS or words > STORY_MAX_WORDS:
        problems.append("the story is %d words, and the band is %d-%d"
                        % (words, STORY_MIN_WORDS, STORY_MAX_WORDS))
    if re.search(r"\bTODO\b|\bTBD\b|\bXXX\b", story):
        problems.append("the story still has a placeholder in it")

    # The position is part of the teaching: the naive story breaks, the story
    # makes the real thing imaginable, and only then is the real thing named.
    order = list(sections.keys())
    if STORY_HEADING in order:
        at = order.index(STORY_HEADING)
        if STORY_AFTER in order and at < order.index(STORY_AFTER):
            problems.append("the story comes before '## %s'" % STORY_AFTER)
        if STORY_BEFORE in order and at > order.index(STORY_BEFORE):
            problems.append("the story comes after '## %s'" % STORY_BEFORE)
    return problems


def check_illustration(lesson_id: str) -> list[str]:
    """Return the problems with a lesson's generated picture."""
    path = illustration_path(lesson_id)
    if not os.path.exists(path):
        return ["no illustration at %s" % os.path.relpath(path, REPO)]
    size = os.path.getsize(path)
    if size == 0:
        return ["the illustration is empty"]
    if size > MAX_IMAGE_BYTES:
        return ["the illustration is %dKB, over the 400KB limit" % (size // 1024)]
    with open(path, "rb") as f:
        head = f.read(12)
    if not (head.startswith(b"\xff\xd8\xff") or head.startswith(b"\x89PNG")):
        return ["the illustration is not a JPEG or a PNG"]
    return []


def duplicate_pictures(lessons: list[dict]) -> dict:
    """Map each picture digest to the lessons that share it.

    Two lessons with the same picture are two lessons with the same scene,
    which means one of them was illustrated by mistake.
    """
    import hashlib

    by_digest: dict[str, list[str]] = {}
    for lesson in lessons:
        lid = lesson.get("id")
        path = illustration_path(lid)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        by_digest.setdefault(digest, []).append(lid)
    return {digest: ids for digest, ids in by_digest.items() if len(ids) > 1}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true",
                        help="print what each lesson is missing, without failing")
    args = parser.parse_args()

    lessons = cl.load_lessons()
    if not lessons:
        print("FAIL: no lessons found")
        return 1

    failures = 0
    for lesson in sorted(lessons, key=lambda m: m.get("id", "")):
        lid = lesson.get("id")
        problems = check_story(lesson)
        problems += check_figure(lid, figure_path(lid))
        problems += check_illustration(lid)
        if problems:
            failures += 1
            print("FAIL %s" % lid)
            for p in problems:
                print("       - %s" % p)

    for ids in duplicate_pictures(lessons).values():
        failures += 1
        print("FAIL %s" % ", ".join(sorted(ids)))
        print("       - these lessons share one picture: %s" % ", ".join(sorted(ids)))

    print()
    print("lessons checked      :", len(lessons))
    print("lessons with problems:", failures)
    if failures and not args.list:
        print("\n%d lesson(s) are not finished. See site/FIGURES.md." % failures)
        return 1
    if not failures:
        print("\nOK: every lesson has a story, a diagram and a picture.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
