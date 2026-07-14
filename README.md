# Site Blocks

A **T-numbered library of dark-theme website sections and UI patterns** — 112 blocks
across 15 categories, each with a unique ID (`T001`–`T285`) so you can tell a human
or an AI exactly which block to use: *"build the hero using T041, pricing from T260."*

Extracted from a production-quality Astro site design (near-black surfaces, orange
`#ff7f1f` accent, Bai Jamjuree / Inter / JetBrains Mono type).

## View it locally

No build step, no server needed — just open [`index.html`](index.html) in a browser.
It lists every block with its T-number and links into the category pages under
`pages/`, where each pattern renders live with its ID badge.

## Using it in another project (for AIs)

1. **Look up the ID** in [`catalog.json`](catalog.json) — it maps every T-number to
   `{ name, category, file, anchor, description }`.
2. **Open the file** (e.g. `pages/forms.html#T204`) and copy:
   - the markup inside that pattern's `.tb-demo` wrapper,
   - the CSS rules its classes use from that page's `<style>` block,
   - any behavior it needs from that page's `<script>` block.
3. **Bring the tokens**: everything relies on the custom properties in
   [`assets/base.css`](assets/base.css) (`--bg`, `--bg-2`, `--bg-3`, `--border`,
   `--border-2`, `--border-3`, `--text`…`--text-4`, `--accent`). Copy the token
   block (or the whole file) into the target project — or re-map the variables to
   the target project's own palette to restyle the block instantly.
4. `.tb-pattern`, `.tb-tid`, `.tb-demo` etc. are **viewer chrome**, not part of the
   pattern — don't copy those.

A typical instruction to an AI in another repo:

> Clone https://github.com/Axioz1234/site-blocks (or read it locally). Build the
> pricing section using **T260** and the FAQ using **T056**, restyled to this
> project's brand colours.

## T-number map

| Range | Category | Page |
|---|---|---|
| T001–T003 | Foundations (colour, type) | `pages/foundations.html` |
| T010–T016 | Elements | `pages/elements.html` |
| T030–T031 | Library components | `pages/components.html` |
| T040–T063 | Named sections (24 site sections) | `pages/sections.html` |
| T070–T078 | Patterns | `pages/patterns.html` |
| T100–T106 | Animation | `pages/animation.html` |
| T120–T126 | Dev tools | `pages/devtools.html` |
| T140–T146 | Social proof | `pages/social.html` |
| T160–T166 | Content | `pages/content.html` |
| T180–T186 | Navigation | `pages/navigation.html` |
| T200–T206 | Forms | `pages/forms.html` |
| T220–T226 | Feedback | `pages/feedback.html` |
| T240–T245 | Data | `pages/data.html` |
| T260–T265 | Commerce | `pages/commerce.html` |
| T280–T285 | Media | `pages/media.html` |

Gaps between ranges are intentional — room to add new blocks to a category without
renumbering. See [`SPEC.md`](SPEC.md) for the page skeleton and extraction rules if
you add patterns.

## Notes

- Pages work from `file://` — relative paths only, no external JS. Web fonts load
  from Google Fonts, so type falls back to system fonts when offline.
- Each page is fully self-contained (own `<style>`/`<script>`); the only shared
  dependencies are `assets/base.css` (tokens) and `assets/viewer.css` (chrome).
- Design extracted from the AstroAnimate site clone — kept private for that reason.
