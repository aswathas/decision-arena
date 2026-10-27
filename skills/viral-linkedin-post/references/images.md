# The image plan

Images are not decoration. On LinkedIn the first image is the difference
between a scroll-past and a stop.

## The rules

- **Three images maximum.** The first gets the weight, the third gets a
  glance, the fourth gets nothing.
- **Order matters.** Best first. The thumbnail in the feed is the first image.
- **Every image needs alt text.** Alt text is not for screen readers only, it
  is the caption that the platform shows under the image.
- **Caption names what is in the picture.** "The friction figure: one ticket,
  three prompt shapes, one decision threshold" beats "Check this out".
- **Never fake a screenshot.** Capture the real build. A reader can tell, and
  a fake screenshot is the one thing that makes a technical post untrustworthy.
- **No text baked into the image** unless it is a diagram label. The platform
  already shows the caption; text in the image is read twice and understood
  once.

## The three-image arc for a build or a course

| # | The image | What it must show |
|---|---|---|
| 1 | the hook | the thing that makes the reader stop - the number, the figure, the contradiction |
| 2 | the proof | evidence: the real output, the real chart, the real page |
| 3 | the invitation | the destination: the page, the index, the course |

## Sizes

- Feed image: **1200 x 627** (landscape) or **1200 x 1200** (square). Square
  takes more vertical room in the feed.
- Keep the file under 5MB; under 1MB is better.
- Screenshots at 2x device pixel ratio are fine; do not upload a 4K PNG.

## Capturing from this repo

The site builds to `site/dist` and the capture script drives a real browser:

```bash
cd site && npm run build
node site/scripts/capture.mjs index            # the landing page
node site/scripts/capture.mjs course           # the course index
node site/scripts/capture.mjs lessons/L22       # one lesson page
node site/scripts/capture.mjs index ".shapes"   # one element only
```

Screenshots land in `site/.impeccable/review/`. Copy the ones you want into
`docs/linkedin/media/` with a readable name (`01-hook.png`, `02-proof.png`,
`03-destination.png`) and point the spec's `images[].path` at them.

For the illustrated course the best first image is a lesson page with its
figure and its generated illustration visible - it shows the whole idea of the
post in one frame.

## Alt text that works

Bad: `image.png`, `screenshot`, `chart of results`.

Good: `Lesson page for L22 Attention, showing an animated figure of tokens
attending to one another, above the prose and a line-art illustration of a
transformer block.`

Say what is in the picture, in one sentence, for someone who cannot see it.
