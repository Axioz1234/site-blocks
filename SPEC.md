# Site Blocks: spec

How the library is built, and the rules anything added to it has to satisfy.
Read this before adding a block, a category or a theme.

## 1. The one rule

**A block must never contain a raw colour, font family, radius or border width.**

Every one of those comes from a token in `assets/base.css`. This is what makes the
library reskinnable: the Theme switch works because no block ever referred to a
literal value. A single hardcoded `#ff7f1f` welds that block to one theme and
quietly breaks the promise for everyone who copies it.

`tools/check.py` enforces this. It fails on any hex or numeric `rgb()`/`rgba()`
inside a `<style>` block or a `style=` attribute. Hex printed as visible text is
allowed, which is how `foundations.html` documents token values.

Where you need transparency beyond the `--accent-line` and `--accent-faint`
tokens, use `color-mix(in srgb, var(--accent) 12%, transparent)`.

## 2. Token contract

Defined in `assets/base.css`, once per theme.

### Surfaces
`--bg-black` (page ground) · `--bg` (section ground) · `--bg-2` (raised panel,
card fill) · `--bg-3` (inset well, input fill, code block) · `--bg-card`

### Text
`--text` · `--text-2` · `--text-3` · `--text-4`. All four clear AA on every
surface token in every theme.

### Borders
`--border` (hairline) · `--border-2` (visible) · `--border-3` (strong)

### Accent
`--accent` (the signature colour: CTAs, eyebrows, active states) ·
`--accent-hover` · `--accent-deep` · `--accent-light` · `--accent-ink` ·
`--accent-wash` · `--accent-wash-2` · `--accent-line` · `--accent-faint`

**`--accent-ink` is the text colour that sits on an accent fill.** Never put
`--text` on an accent fill. Dark's accent is bright orange and Moonrite's is dark
navy, so a fixed light or dark foreground fails in one of them.

### Status
`--ok` `--warn` `--err` `--info`, each with a `-wash`, a `-deep`, a `-line` (low
alpha, for borders and rules) and a `-faint`, plus `--status-ink` for text on a
solid status fill.

Use these only when the colour **means** something: success, warning, error,
information. A status colour reads as its meaning, so borrowing one for decoration
is a bug, not a shortcut. Three tokens exist precisely so you do not have to:

| Token | For |
|---|---|
| `--sale` `--sale-ink` `--sale-wash` | Discounts and savings. A saving is not an error, and painting it in `--accent` makes it compete with the primary CTA. |
| `--rating` `--rating-empty` | Star ratings. A five-star review and a genuine warning should not be the same hue. |
| `--muted` `--muted-wash` | A neutral, meaning-free pill: an overflow count, a points debit. |

### Categorical
`--cat-1` through `--cat-5`. For charts, tag groups, legends and avatar tints,
where the colour carries **identity** rather than meaning. Chosen to stay clear of
the green and red that signal state, so a chart series is never mistaken for a
success or an error.

Note that `--cat-1` is the accent in both themes, by design: the first series in a
chart is the brand colour. If a block needs a hue that must NOT read as the accent,
start at `--cat-2`.

### Product swatches
`--swatch-cream` `--swatch-clay` `--swatch-sage` `--swatch-charcoal`
`--swatch-navy` `--swatch-rust` `--swatch-ochre` `--swatch-blush`
`--swatch-plum` `--swatch-slate` `--swatch-ironbark` `--swatch-saltbush`

These depict an **actual product colour**, so unlike everything else here they are
identical in both themes: "Sage" is sage whichever theme is on. Use them for colour
facets and variant swatches. Never use `--cat-*` for a product colour.

### Theme previews
`--preview-light` `--preview-light-ink` `--preview-dark` `--preview-dark-ink`

For UI that **depicts** a light or dark theme, such as a theme-picker card. Also
fixed in both themes: a "light mode" preview built from `--bg` and `--text` inverts
when the theme flips and stops demonstrating anything.

### Overlays, chrome and state
| Token | For |
|---|---|
| `--scrim` | The veil behind a `<dialog>` or slide-over. Never build one from `--bg-black`: that token is white in a light theme, so the scrim would lighten instead of dim. |
| `--shadow-overlay` | The one real elevation. `--shadow-card` and `--shadow-raised` are `none` in both themes, but a panel floating over the page must separate from it. |
| `--track` | The unfilled part of a progress, distribution or rating bar. |
| `--disabled-surface` `--disabled-ink` `--disabled-border` | Disabled controls. An `opacity` drop washes out a bordered card, so disabled state gets real tokens. |
| `--focus-ring` `--focus-offset` | `outline: var(--focus-ring); outline-offset: var(--focus-offset);` Use it everywhere so a new theme restyles focus in one place. |
| `--accent-light-ink` | Text on an `--accent-light` fill. `--accent-light` is bright orange in Dark and yellow in Moonrite, so no normal text token is safe on it. |

### Placeholder washes
`--wash-1a`/`--wash-1b` (warm) · `--wash-2a`/`--wash-2b` (cool) ·
`--wash-3a`/`--wash-3b` (neutral). Gradient pairs for product thumbs, media
posters and avatar tiles:

```html
<div class="x-thumb" style="background:linear-gradient(135deg,var(--wash-1a),var(--wash-1b))"></div>
```

### Type
`--font-display` · `--font-body` · `--font-mono` · `--font-eyebrow` · `--font-ui`,
plus `--heading-weight` `--heading-tracking` `--heading-transform`
`--eyebrow-tracking` `--eyebrow-transform` `--eyebrow-prefix` `--button-weight`
`--button-tracking` `--button-transform`.

Case and prefixes live in these tokens, never in the copy. Author labels and
button text in natural sentence case; the theme's `*-transform` tokens decide
the rendered case. `--eyebrow-prefix` is the Dark theme's `// ` code-comment
opener, painted via `.eyebrow::before` (add the same `::before` to a page-local
label class that needs it); Moonrite sets it to the empty string. Never type
`//` into a label.

`--font-ui` for buttons, labels, meta, prices, badges and table headers.
`--font-mono` only for genuine code, SKUs, order numbers and tracking IDs.

### Shape
`--radius-sm` · `--radius` · `--radius-card` · `--radius-pill` · `--line-weight`.
Use `--line-weight` in every `border:` shorthand, never a literal `1px`.

## 3. How the library is assembled

The library is **browsed as one page**, `index.html`, and **authored as one file
per category** under `pages/`. `tools/build.py` compiles the sources into the page.

Never hand-edit `index.html`, `catalog.json`, or anything between the
`<!-- BUILD:START -->` and `<!-- BUILD:END -->` markers. Edit a source page, then:

```bash
python tools/build.py && python tools/check.py
```

`check.py` fails if `index.html` is stale against the catalog, so a forgotten build
cannot ship.

### Why the compile scopes everything

The source pages were written independently, so merging them naively breaks them:
44 class names are shared and some carry different rules (`.sgx-preview` differs
between categories), 11 scripts query generic state classes such as `.is-active`,
and `@keyframes tbPulse` is declared in three pages. The compiler therefore wraps
each category in `.src-<slug>` and isolates it:

- **CSS** every selector is prefixed with the scope, `:root` blocks are remapped
  onto it, `@keyframes` are renamed and their references rewritten. A class scope
  rather than an id keeps the specificity bump at 10, so `base.css` theme
  overrides still win where they should.
- **JS** each script runs with `document` shadowed by a proxy scoped to that
  category's subtree. Lookups cannot escape it; everything else forwards to the
  real document.

This means **you do not have to worry about collisions when authoring**. Write a
page as if it were standalone. Prefixing your classes is still good manners, and
still required for anything you expect someone to copy out, but a collision will
not break the compiled page.

See `tools/compile_page.py`.

## 4. Page skeleton

Every file in `pages/` uses exactly this.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{Category} &middot; Site Blocks</title>
  <link rel="stylesheet" href="../assets/base.css">
  <link rel="stylesheet" href="../assets/viewer.css">
  <script src="../assets/viewer.js"></script>
</head>
<body data-page-set="core">
  <header class="tb-header">
    <a class="tb-back" href="../index.html">&larr; Site Blocks index</a>
    <h1>{Category} <span class="tb-range">{Txxx}&ndash;{Tyyy}</span></h1>
    <p class="tb-sub">{one-line category description}</p>
  </header>
  <main class="tb-main">

    <article class="tb-pattern" id="T200" data-tid="T200">
      <header class="tb-pattern-head">
        <span class="tb-tid">T200</span>
        <div>
          <h2>{Pattern name}</h2>
          <p>{What it is and when to reach for it.}</p>
        </div>
      </header>
      <div class="tb-demo">
        <!-- the block markup -->
      </div>
    </article>

    <!-- ...more tb-pattern articles, in T-number order... -->

  </main>
  <style>
    /* every rule the blocks on this page need */
  </style>
  <script>
    /* behaviour, in one IIFE, plain JS, scoped to document */
  </script>
</body>
</html>
```

`data-page-set` is `core` or `ecommerce`. `viewer.js` must load in `<head>` as a
classic script so the theme lands before first paint.

Anything prefixed `tb-` is viewer chrome, styled by `assets/viewer.css`. Never
style a `tb-` class from a page, and never use a `tb-` prefix for a block class.

## 5. Constraints

1. **Works from `file://`.** Relative paths only. No `fetch()`, no ES modules, no
   CDN scripts, no icon fonts. Google Fonts, loaded from `base.css`, is the one
   external dependency.
2. **Self-contained page.** Each page carries its own `<style>` and `<script>`.
   Page styles are global, so prefix every class on a page with that page's short
   prefix (`plp-`, `pdp-`, `chk-`, `mch-`, `acc-`).
3. **Degrades without JavaScript.** Prefer `<details>`, `<dialog>`, `:has()` and
   CSS-only patterns. If a block needs JS, it still renders sensibly without it.
4. **No browser dialogs.** Never `alert()`, `confirm()` or `prompt()`.
5. **Accessible.** Semantic elements, `<button type="button">`, labels tied to
   inputs, `aria-label` where an icon carries meaning, `aria-pressed` and
   `aria-expanded` on toggles, visible focus, 48px minimum tap targets.
6. **Responsive.** Grids collapse. Nothing overflows the 1080px viewer column.
7. **Contrast at least 4.5:1 in every theme.** Verified per theme, not once.
8. **No em dashes**, in copy or comments. Repunctuate: a colon before an
   explanation, a full stop between independent clauses, commas around an aside.
   En dashes in genuine numeric ranges (`$40–$60`) are correct and stay.

## 6. Catalog

Each category owns a fragment at `catalog/{slug}.json`, an array in T order:

```json
[
  { "id": "T300", "name": "Collection hero", "category": "Catalogue",
    "set": "ecommerce", "page": "index.html", "anchor": "#T300",
    "source": "pages/ecom-catalogue.html",
    "description": "One line saying what it is and when to reach for it." }
]
```

`page` + `anchor` is where a human looks at the block. `source` is the authoring
file it is compiled from, which is the easier one to lift code out of because its
CSS and JS are unscoped there.

`catalog/_categories.json` holds the category order, titles, blurbs and set
membership. `catalog.json` and the body of `index.html` are **generated**:

```bash
python tools/build.py
```

Never hand-edit `catalog.json`, or the region of `index.html` between the
`<!-- BUILD:START -->` and `<!-- BUILD:END -->` markers.

Descriptions must be theme-neutral. Write "accent fill", not "orange fill": the
same block is navy in the other theme.

## 7. Adding a block

1. Pick the next free T-number in that category's range.
2. Add the `tb-pattern` article to the **source page**, in T order.
3. Add its CSS to that page's `<style>`, using the page prefix and tokens only.
4. Add its entry to `catalog/{slug}.json`.
5. `python tools/build.py && python tools/check.py`.
6. Look at it in `index.html` in both themes before committing.

## 8. Adding a category

1. Claim a T range that does not collide (see the map in `README.md`).
2. Create `pages/{slug}.html` from the skeleton above.
3. Create `catalog/{slug}.json`.
4. Add an entry to `catalog/_categories.json` with its `set`. The compiler picks
   the new category up from there and gives it its own `.src-{slug}` scope.
5. `python tools/build.py && python tools/check.py`.

## 9. Adding a theme

1. Copy the `[data-theme="moonrite"]` block in `assets/base.css`, rename the
   attribute value, and re-point **every** token in it. A token you forget falls
   back to the Dark value, which is how a theme ends up half-broken.
2. Add it to the `THEMES` array in `assets/viewer.js`.
3. Run `python tools/check.py`. It walks the contrast pairs for your theme's own
   values. Clearing 4.5:1 is not inherited from another theme.
4. Page through both sets and look at every block.

## 10. Extraction rules (for packaging a new source design)

1. **Faithful extraction, then tokenise.** Keep class names, markup structure and
   layout exactly as in the source. You are packaging, not redesigning. The only
   change is literal values becoming tokens.
2. **Expand all template expressions** (`{items.map(...)}`, conditionals) into
   literal HTML using the real data from the source's frontmatter. The output must
   contain zero `{}` template syntax.
3. **Strip framework frontmatter and imports.** No `---` blocks in output.
4. **Scoped-style caveat:** source styles were component-scoped; extracted they are
   page-global. That is fine, each page is standalone, but do not rename classes.
   Prefix new classes you author yourself.
5. **T-numbers** run sequentially from the category's assigned start, in source
   document order. One `tb-pattern` article per named pattern.
6. When the source hardcodes a value that no token covers, add the token to
   **every** theme in `base.css` first, then use it. Never add a token to one theme.
