// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// The site is a static build. `output: 'static'` is Astro's default, but it is
// stated here because the deployment target is a plain static host and the
// build must never need a server runtime.
export default defineConfig({
  site: 'https://aswathas.github.io',
  output: 'static',
  build: {
    format: 'directory',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
