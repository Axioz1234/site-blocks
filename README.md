# Site Blocks

A **T-numbered library of 177 website sections and UI patterns**, in two themes,
split into two sets (106 core, 71 e-commerce). Every block has a unique ID
(`T001`–`T399`) so you can tell a human or an AI exactly which one to use:
*"build the hero using T041, the product grid from T301."*

## Two themes

Every block is token-driven. No block contains a raw colour, font or radius: they
all read the custom properties in [`assets/base.css`](assets/base.css). One
attribute on `<html>` reskins the entire library.

| Theme | Attribute | Look |
|---|---|---|
| **Dark** (default) | none | Near-black surfaces, orange `#ff7f1f` accent, hard edges, Bai Jamjuree / Inter / JetBrains Mono. Extracted from a production Astro site design. |
| **Moonrite** | `data-theme="moonrite"` | Paper white, ink black, navy `#2A344E` signature with cream, light blue and yellow tints. Soft corners, pill buttons, Fraunces over Instrument Sans. Ported from the Moonrite storefront's Moon Tint Kit direction. |

The **Theme** switch at the top of every page flips between them and remembers
your choice. That switch is also the proof: if a block looks wrong in one theme,
it has a hardcoded value and needs fixing.

## Two sets

| Set | What it is |
|---|---|
| **Core** | The original library: foundations, elements, sections, patterns, animation, dev tools, social proof, content, navigation, forms, feedback, data, media. |
| **E-commerce** | The retail set: commerce basics, catalogue, product page, cart and checkout, merchandising and trust, account and post-purchase. |

The **Set** switch on [`index.html`](index.html) filters the index down to one or
the other. Each category page carries its set as a badge.

## View it locally

No build step, no server. Open [`index.html`](index.html) in a browser. It lists
every block with its T-number and links into the category pages under `pages/`,
where each pattern renders live with its ID badge.

## Using it in another project (for AIs)

1. **Look up the ID** in [`catalog.json`](catalog.json). It maps every T-number to
   `{ id, name, category, set, file, anchor, description }`.
2. **Open the file** (e.g. `pages/ecom-product.html#T321`) and copy:
   - the markup inside that pattern's `.tb-demo` wrapper,
   - the CSS rules its classes use from that page's `<style>` block,
   - any behaviour it needs from that page's `<script>` block.
3. **Bring the tokens.** Everything relies on the custom properties in
   [`assets/base.css`](assets/base.css). Either copy the token block into the
   target project, or re-point those variables at the target project's own
   palette. Re-pointing is the fast path: the block restyles instantly and
   correctly, because it never referred to a literal colour in the first place.
4. `.tb-pattern`, `.tb-tid`, `.tb-demo`, `.tb-header`, `.tb-toolbar` and anything
   else prefixed `tb-` is **viewer chrome**, not part of the pattern. Don't copy it.

A typical instruction to an AI in another repo:

> Clone https://github.com/Axioz1234/site-blocks (or read it locally). Build the
> product page using **T320**, **T321**, **T322** and **T329**, and the checkout
> using **T343** and **T347**, re-pointing `assets/base.css` tokens to this
> project's brand colours.

## T-number map

### Core set

| Range | Category | Page |
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

| Range | Category | Page |
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

Viewing needs nothing. These two exist so the derived files cannot drift and so
the rules stay enforced rather than remembered.

```bash
python tools/build.py    # rebuild catalog.json and index.html from catalog/*.json
python tools/check.py    # verify the whole library
```

`tools/check.py` fails on a raw colour in any page, an em dash, a page that is not
wired to the shared assets, a `var(--token)` that base.css does not define, and any
foreground/surface pair under 4.5:1. Contrast is walked **per theme**, so adding a
theme means clearing the bar on its own values, not inheriting someone else's pass.

Run `build.py` after editing anything under `catalog/`, then `check.py` before
committing.

## Notes

- Pages work from `file://`: relative paths only, no `fetch()`, no ES modules, no
  CDN scripts. Web fonts load from Google Fonts, so type falls back to system
  fonts when offline.
- Each page is self-contained (its own `<style>` and `<script>`). The only shared
  dependencies are `assets/base.css` (tokens), `assets/viewer.css` (chrome) and
  `assets/viewer.js` (the two switches).
- With JavaScript off, every page still renders, in Dark, unfiltered.
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
