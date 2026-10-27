// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// The site is a static build. `output: 'static'` is Astro's default, but it is
// stated here because the deployment target is a plain static host and the
// build must never need a server runtime.
//
// `base` is the sub-path the site is served from. It is empty for a root
// deployment (a domain of its own) and "/decision-arena" for the GitHub
// Pages project page, which lives under the repository's name. The build
// reads it from BASE_PATH so one source tree serves both, and every internal
// link is built from it - see src/data/urls.ts.
export default defineConfig({
  site: 'https://aswathas.github.io/decision-arena',
  base: process.env.BASE_PATH ?? '/',
  output: 'static',
  build: {
    format: 'directory',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
