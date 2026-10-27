# The spec format

A post is a JSON file under `docs/linkedin/specs/`. The renderer
(`tools/linkedin_post.py`) reads it, checks it, and writes the artefact.

```json
{
  "slug": "illustrated-course",
  "date": "2026-10-28",
  "title": "The illustrated course",
  "format": "teaching-post",
  "hook": "46 lessons. 158 concepts. One battery run against four decision models.\n\nEvery vendor publishes a benchmark where they win.",
  "body": [
    "One paragraph, one idea.",
    "Another paragraph."
  ],
  "cta": "Read the first lesson: <link>",
  "hashtags": ["decisionmodels", "evals", "machinelearning"],
  "links": [
    {"label": "The course", "url": "https://aswathas.github.io/decision-arena/"}
  ],
  "images": [
    {"path": "media/01-hook.png", "alt": "one sentence describing the picture", "caption": "what the reader is looking at"}
  ],
  "first_comment": "The link again, in case the post swallowed it: https://...",
  "evidence": [
    "46 lesson files under course/lessons/, 158 unique concepts",
    "Live site: https://aswathas.github.io/decision-arena/"
  ]
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `hook` | yes | first two lines, <= 200 characters |
| `body` | yes | list of paragraphs, each <= 600 characters |
| `cta` | yes | one instruction, one verb |
| `hashtags` | yes | 3-5 plain words, no punctuation |
| `links` | yes | at least one https URL |
| `images` | yes (a post with images) | path, alt, optional caption |
| `evidence` | yes | each line names a source |
| `first_comment` | no | the link, repeated, for reach |
| `slug`, `date`, `title`, `format` | no | metadata for the artefact header |

## What the gate checks

1. hook present and <= 200 chars
2. body present, no paragraph over 600 chars
3. at least one https link
4. 3-5 hashtags, each a plain word
5. every image file exists, under 12MB, with alt text
6. at least one evidence line naming a source (a path, a run id or a URL)
7. no banned hype word anywhere
8. a CTA is present
9. the rendered post is under 3000 characters

## Paths

`images[].path` is relative to the spec file, so a spec in
`docs/linkedin/specs/` refers to `docs/linkedin/specs/media/...`. Put the media
in `docs/linkedin/media/` and either place the spec beside it or use a path
that resolves - the checker tries the path relative to the spec directory
first.

## Commands

```bash
python tools/linkedin_post.py --spec docs/linkedin/specs/<slug>.json --check
python tools/linkedin_post.py --spec docs/linkedin/specs/<slug>.json \
    --out docs/linkedin/<YYYY-MM-DD>-<slug>.md
```

`--check` prints the failures and writes nothing. Without `--check`, a spec
that fails also writes nothing - fix the spec first.
