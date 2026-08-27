# Site Blocks

A **T-numbered library of 177 website sections and UI patterns**, in two themes,
split into two sets (106 core, 71 e-commerce). Every block has a unique ID
(`T001`–`T399`) so you can tell a human or an AI exactly which one to use:
*"build the hero using T041, the product grid from T301."*

## One page

Open [`index.html`](index.html). The block list is at the top, and **every block
is inlined below it**: scroll and browse, nothing to click into. A T-number in the
list is an in-page anchor, so `index.html#T321` jumps straight to that block.

Each category keeps a sticky header as you scroll through it, so you always know
where you are, with a link back to the list.

## Two themes

Every block is token-driven. No block contains a raw colour, font or radius: they
all read the custom properties in [`assets/base.css`](assets/base.css). One
attribute on `<html>` reskins the entire library.

| Theme | Attribute | Look |
|---|---|---|
| **Dark** (default) | none | Near-black surfaces, orange `#ff7f1f` accent, hard edges, Bai Jamjuree / Inter / JetBrains Mono. Extracted from a production Astro site design. |
| **Moonrite** | `data-theme="moonrite"` | Paper white, ink black, navy `#2A344E` signature with cream, light blue and yellow tints. Soft corners, pill buttons, Fraunces over Instrument Sans. Ported from the Moonrite storefront's Moon Tint Kit direction. |

The **Theme** switch at the top flips between them and remembers your choice. That
switch is also the proof: if a block looks wrong in one theme, it has a hardcoded
value and needs fixing.

## Two sets

| Set | What it is |
|---|---|
| **Core** | The original library: foundations, elements, sections, patterns, animation, dev tools, social proof, content, navigation, forms, feedback, data, media. |
| **E-commerce** | The retail set: commerce basics, catalogue, product page, cart and checkout, merchandising and trust, account and post-purchase. |

The **Set** switch filters both the list and the blocks, so choosing E-commerce
hides the other 106 entirely.

## Using it in another project (for AIs)

1. **Look up the ID** in [`catalog.json`](catalog.json). It maps every T-number to
   `{ id, name, category, set, page, anchor, source, description }`.
2. **Open the source file.** `source` points at the authoring file
   (e.g. `pages/ecom-product.html`), where that block's CSS and JS sit unscoped and
   readable. That is the easier one to lift from. `page` + `anchor`
   (`index.html#T321`) is where a human looks at it.
3. **Copy** the markup inside that block's `.tb-demo` wrapper, the CSS rules its
   classes use from that page's `<style>`, and any behaviour from its `<script>`.
4. **Bring the tokens.** Everything relies on the custom properties in
   [`assets/base.css`](assets/base.css). Either copy the token block into the
   target project, or re-point those variables at the target project's own
   palette. Re-pointing is the fast path: the block restyles instantly and
   correctly, because it never referred to a literal colour in the first place.
5. `.tb-pattern`, `.tb-tid`, `.tb-demo`, `.tb-header`, `.tb-toolbar`, `.tb-src` and
   anything else prefixed `tb-` is **viewer chrome**, not part of the pattern.
   Don't copy it. Neither is the `.src-<slug>` wrapper, which only exists to keep
   the categories from colliding on one page.

A typical instruction to an AI in another repo:

> Clone https://github.com/Axioz1234/site-blocks (or read it locally). Build the
> product page using **T320**, **T321**, **T322** and **T329**, and the checkout
> using **T343** and **T347**, re-pointing `assets/base.css` tokens to this
> project's brand colours.

## How it is built

`index.html` is **generated**. The library is authored as one self-contained file
per category under `pages/`, and `tools/build.py` compiles those into the single
page. Edit the source files, never `index.html`.

The compile is not a concatenation. The source pages were written independently and
genuinely collide: 44 class names are shared between them and some carry different
rules (`.sgx-preview` differs between categories), 11 scripts query generic state
classes like `.is-active`, and `@keyframes tbPulse` is declared three times. So the
compiler isolates each one:

- **CSS** every selector is prefixed with that category's `.src-<slug>` scope,
  `:root` blocks are remapped onto it, and `@keyframes` are renamed with their
  references rewritten. A class is used rather than an id to keep the specificity
  bump small enough that `base.css` theme overrides still win.
- **JS** each script runs with `document` shadowed by a proxy scoped to that
  category's subtree, so a query for `.is-active` cannot reach another category.
  Everything that is not a lookup forwards to the real document.

See [`tools/compile_page.py`](tools/compile_page.py).

## T-number map

### Core set

| Range | Category | Source |
|---|---|---|
| T001–T003 | Foundations (tokens, type) | `pages/foundations.html` |
| T010–T016 | Elements | `pages/elements.html` |
| T030–T031 | Library components | `pages/components.html` |
| T040–T063 | Named sections | `pages/sections.html` |
| T070–T078 | Patterns | `pages/patterns.html` |
| T100–T106 | Animation | `pages/animation.html` |
| T120–T126 | Dev tools | `pages/devtools.html` |
| T140–T146 | Social proof | `pages/social.html` |
| T160–T166 | Content | `pages/content.html` |
| T180–T186 | Navigation | `pages/navigation.html` |
| T200–T206 | Forms | `pages/forms.html` |
| T220–T226 | Feedback | `pages/feedback.html` |
| T240–T245 | Data | `pages/data.html` |
| T280–T285 | Media | `pages/media.html` |

### E-commerce set

| Range | Category | Source |
|---|---|---|
| T260–T265 | Commerce (the original retail six) | `pages/commerce.html` |
| T300–T319 | Catalogue | `pages/ecom-catalogue.html` |
| T320–T339 | Product page | `pages/ecom-product.html` |
| T340–T359 | Cart & checkout | `pages/ecom-checkout.html` |
| T360–T379 | Merchandising & trust | `pages/ecom-merch.html` |
| T380–T399 | Account & post-purchase | `pages/ecom-account.html` |

Gaps between ranges are intentional: room to add blocks to a category without
renumbering. See [`SPEC.md`](SPEC.md) for the page skeleton, the token contract,
and the rules for adding a block, a category or a theme.

## Tools

```bash
python tools/build.py    # compile index.html and catalog.json from the sources
python tools/check.py    # verify the whole library
```

`tools/check.py` fails on a raw colour in any page, an em dash, a source page that
is not wired to the shared assets, a `var(--token)` that nothing defines, a palette
page that has drifted from `base.css`, an `index.html` that is stale against the
catalog, and any foreground/surface pair under 4.5:1. Contrast is walked **per
theme**, so adding a theme means clearing the bar on its own values, not inheriting
someone else's pass.

Run `build.py` after editing anything under `pages/` or `catalog/`, then `check.py`
before committing.

## Notes

- Everything works from `file://`: relative paths only, no `fetch()`, no ES
  modules, no CDN scripts. Web fonts load from Google Fonts, so type falls back to
  system fonts when offline.
- The only shared dependencies are `assets/base.css` (tokens), `assets/viewer.css`
  (chrome) and `assets/viewer.js` (the two switches).
- With JavaScript off, the page still renders, in Dark, unfiltered.
- Offscreen blocks use `content-visibility: auto`, so 177 live blocks on one page
  stay smooth. Find-in-page and anchor links still reach them.
- The source pages under `pages/` remain individually openable. They are the
  authoring format, not the way the library is meant to be browsed.
- The Dark theme is a faithful extraction, with these deliberate departures:
  - **`--accent-ink` is ink, not the source's near-white.** White on `#ff7f1f`
    measures 2.42:1 and failed AA on every primary CTA in the library. Reverting
    that one token restores the original.
  - **Card and panel radii collapsed to the shape tokens.** The source's stray
    4px, 6px, 8px and 10px corners now read `--radius-card` (0px in Dark) or
    `--radius-sm` (3px), so Moonrite can round them. Dark panels are squarer.
  - **`--cat-5` moved off the success green.** A five-series chart previously
    made its fifth series read as "success".
  - **A Warning callout takes `--warn`, not the brand accent**, and star ratings
    take `--rating`. Both were painted in the accent orange before.
  - Two hover fills (`#ff924a`, `#ff9d52`) resolved to the nearest role token.
- The Dark design was extracted from the AstroAnimate site clone, kept private for
  that reason.
