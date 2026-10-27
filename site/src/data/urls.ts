/**
 * Base-aware URLs.
 *
 * The site is published in two places: at the root of a domain, and under a
 * sub-path on GitHub Pages. A hard-coded "/course/" works in the first case
 * and breaks in the second, so every internal link is built from the base
 * Astro was built with.
 *
 * Astro exposes the base as `import.meta.env.BASE_URL`, always with a
 * trailing slash: "/" for a root deployment, "/decision-arena/" for the
 * project page. `url()` turns a root-relative path into a link that works in
 * both.
 */
const raw = import.meta.env.BASE_URL ?? '/';

/** The base path without its trailing slash: "" or "/decision-arena". */
export const BASE = raw.endsWith('/') ? raw.slice(0, -1) : raw;

/** Build a link to a path inside this site. */
export function url(path: string): string {
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${BASE}${suffix}`;
}

/** The site's own root URL, for the home link. */
export const HOME = BASE || '/';
