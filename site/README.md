# site/ - the Decision Arena website

Astro 7 + Tailwind CSS 4, static output. The site is the public front door to
the harness and the course that live in the parent repository.

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
npm run preview  # serve the build
```

## The pages it ships

48 static pages, in three groups:

- `/` - the landing page: one figure plate with the measure door and the learn
  door, the friction field plotted from a committed run, and every number
  linked to its raw file.
- `/course/` - the course index: the ten phases, the 46 lessons with their
  minutes, concepts and prerequisites, and the three paths.
- `/lessons/<id>/` - one page per lesson: the lesson's own text, the file it
  asks the reader to write, and the quiz key behind a disclosure.

## Why it lives here

The site describes the repository, so its source is versioned with the thing
it describes. `src/data/friction.ts` holds the numbers the hero chart plots,
copied from the committed run `runs/20261027-212313-friction-mock.json`, whose
raw calls are committed beside it as `runs/20261027-212313-friction-mock.jsonl`
and whose metadata is `runs/20261027-212313-friction-mock.meta.json`;
`src/pages/index.astro` reads `course/curriculum.json` for the phase list, so
the curriculum on the page cannot drift from the course in the repo.

`src/data/course.ts` holds the same discipline for the course reader. It
imports `course/lessons/*.md` as markdown and `course/quizzes/*.json`
directly, so a lesson page **is** the lesson file - not a copy of it. A lesson
file that moves fails the build rather than publishing a stale page, and the
answers cannot drift from the explanations. The site still holds no copy of
the course.

The course reader teaches; it does not keep the record. Mastery is tracked per
concept by the tutor in `learning/progress.json`, and both the course index
and every lesson page say so.

## Rules this site holds itself to

1. **The mock is not evidence.** Every plotted number comes from the offline
   simulator, and the plot says so on its own face. No live-provider
   measurement exists yet, and the closing section says that plainly.
2. **Evidence before claims.** Every file the page links to is a real
   committed file in the repository.
3. **Stdlib only applies to the library**, not to this site. The site has one
   dependency tree: Astro and Tailwind.

## Review evidence

`../.impeccable/review/` holds the captures the impeccable finish review
reads (`desktop.png`, `mobile.png`, `plate.png`) and the detector's JSON.
Regenerate them with:

```bash
node scripts/capture.mjs               # the landing page
node scripts/capture.mjs course        # the course index
node scripts/capture.mjs lessons/L00   # one lesson
```

## Serving the build locally

A background `npm run preview` in this harness is reaped after one hour, which
breaks a long review session. Launch it detached instead, and it stays up:

```powershell
$site = "C:\Users\aswat\Downloads\Projects\decision-arena\site"
Start-Process -FilePath "C:\Program Files\nodejs\node.exe" `
  -ArgumentList "$site\node_modules\astro\bin\astro.mjs","preview","--port","4321" `
  -WorkingDirectory $site -WindowStyle Hidden `
  -RedirectStandardOutput "$site\preview.out.log" -RedirectStandardError "$site\preview.err.log"
```

Stop it with `Stop-Process -Id <pid>` after finding the listener:
`Get-NetTCPConnection -State Listen -LocalPort 4321`.

The design system this build produced is recorded in `../DESIGN.md` and
`../.impeccable/design.json`; the direction each surface was built against is
recorded in `../.impeccable/surfaces/`.
