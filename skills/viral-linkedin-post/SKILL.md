---
name: viral-linkedin-post
description: >
  Turns something you built into a LinkedIn post that people actually read and
  click: a hook that survives the fold, one idea per line, a concrete mechanism
  instead of adjectives, an image plan with alt text, the link, a call to action
  and three to five hashtags. Use when the user says "post this", "write a
  LinkedIn post", "make this viral", "share the site", "announce the release",
  or wants to attach images and links to a post about work in a repo or a
  product. Enforces the evidence rule: every number in the post names its
  source, and no claim is inflated to win a click.
---

# Viral LinkedIn Post - from a build to a post people finish reading

The feed is not a place to describe what you did. It is a place to give the
reader one idea worth their attention, prove it, and point somewhere useful.

Reach comes from three things, in this order:

1. **The fold.** LinkedIn truncates a post after roughly 200 characters and
   three lines. Whatever is not above the fold is invisible. The hook carries
   the whole post.
2. **The line breaks.** One idea per line. A wall of text is a wall nobody
   crosses. Short paragraphs, blank lines between them, no nested bullets.
3. **The proof.** A number, a mechanism, a screenshot. Adjectives are invisible;
   specifics are what a reader screenshots and sends to a colleague.

Reach is not a trick. A post that is engineered to be *read* will outlast a post
engineered to be *clicked*, because the click happens after the read.

## The workflow

### 1. Gather the facts before you write a word

Do not start from adjectives. Start from what is true and provable.

```bash
git log --oneline -20                     # what shipped
git diff --stat HEAD~5                    # how much changed
python tools/check_course_figures.py      # repo gates, if they apply
python tools/check_site_a11y.py            # the site is accessible
```

Collect:

- **one claim** the post is about (not three)
- **the number** that proves it, with its source path
- **the mechanism** - why it works, in one sentence a non-expert can follow
- **the link** the reader lands on
- **the images** that show it

If the number has no source, it is not a claim yet. Find the source or drop
the number. In this repo a number without its `runs/*.jsonl` behind it is
marketing, and a mock simulator is never a model measurement.

### 2. Pick the format

| Format | Shape | Best for |
|---|---|---|
| `teaching-post` | one concept taught from first principles, then the thing you built | a course, a repo, a lesson |
| `build-in-public` | the problem, the constraint, the decision, the result | shipped work, numbers |
| `launch-post` | what it is, what it does, who it is for, the link | a release, a site, a tool |
| `correction-post` | what you got wrong and what the data says now | research, findings |

One format per post. Mixing them halves the read.

### 3. Write the hook

The hook is the first two lines and it alone decides whether the post is read.
Rules:

- **Under 200 characters.** It must survive the fold on a phone.
- **Concrete over clever.** A number, a contradiction, or a specific scene
  beats a pun every time.
- **No hype words.** See the banned list in `tools/linkedin_post.py`.
- **No "I am excited to share".** Nobody is.
- **One idea.** The hook must promise exactly what the post delivers.

See `references/hooks.md` for the hook library and the rewrite loop.

### 4. Write the body - one idea per line

The body is a sequence of short paragraphs, each one line of the argument:

- the concrete mechanism, in plain words
- the specific thing that was surprising or hard
- what a reader can do with it (this is the part people skip, and it is the
  part that makes a post worth bookmarking)

Rules:

- One idea per paragraph, one blank line between paragraphs.
- A paragraph over 600 characters is a paragraph that needs splitting.
- Name the hard part. A post that admits a real difficulty is more credible
  than one that claims everything went smoothly.
- No bullet-point walls, no emoji spam (three at most, and never mid-sentence),
  no "excited to announce", no fake humility ("I know this is just a small
  project, but").

### 5. Attach the images

LinkedIn gives the first image the most weight; images after the third barely
register. See `references/images.md` for the plan.

- **3 images maximum**, ordered best first.
- Every image needs alt text - it is also the caption's job.
- Captions name what the reader is looking at, not what they should feel.
- Capture from the real build; never fake a screenshot.

For this repo:

```bash
cd site && npm run build
node site/scripts/capture.mjs index          # the landing page
node site/scripts/capture.mjs course         # the course index
node site/scripts/capture.mjs lessons/L22     # one lesson
```

### 6. Place the link, the CTA and the tags

- **One link in the post.** A second link splits the click.
- Put the link where the reader has already decided to want it - after the
  payoff, not in the hook.
- Keep the link in the **first comment** too if the post is long: the visible
  post stays clean, the comment carries the URL, and the platform does not
  down-rank a link-bearing post. Paste the same link in both places.
- **CTA**: one instruction, one verb. "Read the lesson" beats "let me know
  what you think".
- **3-5 hashtags**, plain words, no punctuation, no `camelCase`.

### 7. Render and gate it

The spec is a JSON file. The tool renders it and refuses to write a post that
fails a check.

```bash
python tools/linkedin_post.py --spec docs/linkedin/specs/<slug>.json --check
python tools/linkedin_post.py --spec docs/linkedin/specs/<slug>.json \
    --out docs/linkedin/<YYYY-MM-DD>-<slug>.md
```

The gates are: hook length, paragraph length, one https link, hashtag count,
every image present with alt text, at least one evidence line naming a source,
no banned hype words, a CTA present, and the whole post under 3000 characters.

### 8. Publish - and know where you stand

This skill **generates** posts. It does not publish them.

Check whether a LinkedIn connector is connected before promising anything:

```bash
mcode-tools connector tools --keyword linkedin
```

If there is no LinkedIn connector, the post is finished when the file is
written: the user pastes it. Say that plainly rather than implying it was
posted. If there is a connector, inspect its schema with
`mcode-tools connector tool <name>`, confirm the exact account and visibility
with the user, then call it.

## The honesty rules

These are not style preferences. They are the reason a post is worth reading
twice.

1. **Every number names its source.** In the post, in the evidence list, and
   in the file behind the post.
2. **Never publish a mock result as a model measurement.** If the number came
   from a simulator, say so in the post.
3. **Never inflate.** If the accuracy is 0.93 on one station and not on the
   battery, the post says "one station", not "93% accurate".
4. **No engagement bait.** No "comment YES and I'll send you the guide", no
   fake giveaways, no "tag 3 people". It does not work and it costs the
   account trust.
5. **The link must work.** Open the URL before posting. A dead link in a post
   that promised a click is worse than no post.

## Files

- `references/hooks.md` - the hook library and the rewrite loop
- `references/images.md` - the image plan, alt text rules, capture commands
- `references/spec.md` - the JSON spec format, field by field
- `tools/linkedin_post.py` - the renderer and the gate
