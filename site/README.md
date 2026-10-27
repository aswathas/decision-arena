# site/ - the Decision Arena website

Astro 7 + Tailwind CSS 4, static output. The site is the public front door to
the harness and the course that live in the parent repository.

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
npm run preview  # serve the build
```

## Why it lives here

The site describes the repository, so its source is versioned with the thing
it describes. `src/data/friction.ts` holds the numbers the hero chart plots,
copied from the committed run `runs/20261027-212313-friction-mock.json`, whose
raw calls are committed beside it as `runs/20261027-212313-friction-mock.jsonl`
and whose metadata is `runs/20261027-212313-friction-mock.meta.json`;
`src/pages/index.astro` reads `course/curriculum.json` for the phase list, so
the curriculum on the page cannot drift from the course in the repo.

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
node scripts/capture.mjs     # needs the preview server running
```

The design system this build produced is recorded in `../DESIGN.md` and
`../.impeccable/design.json`; the direction it was built against is recorded
in `../.impeccable/surfaces/site-src-pages-index-astro.md`.
