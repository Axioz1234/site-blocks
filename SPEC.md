# TBlocks — extraction & page spec

TBlocks is a T-numbered library of dark-theme website sections and UI patterns,
extracted from the AstroAnimate site clone at `C:\Projects\Astro Animate Website Copy`.
Each pattern gets a unique ID (T001–T299) so humans and AIs can reference it exactly
("build the hero using T041").

## Page skeleton (every file in pages/ MUST use exactly this)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{Category} — TBlocks</title>
  <link rel="stylesheet" href="../assets/base.css">
  <link rel="stylesheet" href="../assets/viewer.css">
</head>
<body>
  <header class="tb-header">
    <a class="tb-back" href="../index.html">&larr; TBlocks index</a>
    <h1>{Category} <span class="tb-range">{Txxx}&ndash;{Tyyy}</span></h1>
    <p class="tb-sub">{one-line category description}</p>
  </header>
  <main class="tb-main">

    <article class="tb-pattern" id="T200" data-tid="T200">
      <header class="tb-pattern-head">
        <span class="tb-tid">T200</span>
        <div>
          <h2>{Pattern name}</h2>
          <p>{Pattern description}</p>
        </div>
      </header>
      <div class="tb-demo">
        <!-- extracted pattern markup, unmodified classes -->
      </div>
    </article>

    <!-- ...more tb-pattern articles... -->

  </main>
  <style>
    /* the source component's <style> block content, pasted as-is (minus any
       Astro-specific syntax), so the page is fully self-contained */
  </style>
  <script>
    /* the source component's <script> content, adapted to plain JS.
       Wrap in an IIFE. Scope queries to document — pages are standalone. */
  </script>
</body>
</html>
```

## Extraction rules

1. **Faithful extraction, no redesign.** Keep class names, markup structure, and
   CSS exactly as in the source. You are packaging, not improving.
2. **Expand all Astro template expressions** (`{items.map(...)}`, `{var}`,
   conditionals) into literal HTML using the actual data from the file's
   frontmatter. The output must contain zero `{}` template syntax.
3. **Strip Astro frontmatter and imports.** No `---` blocks in output.
4. **Replace `<Loader type="pulse" .../>`** with this static equivalent
   (include the CSS once per page if used):
   ```html
   <span class="tb-pulse" style="--pulse-color:#4ADE80; --pulse-size:24px;"></span>
   ```
   ```css
   .tb-pulse{display:inline-block;width:var(--pulse-size,24px);height:var(--pulse-size,24px);border-radius:50%;background:var(--pulse-color,#4ADE80);animation:tbPulse 1.6s ease-in-out infinite;}
   @keyframes tbPulse{0%,100%{transform:scale(.7);opacity:.5}50%{transform:scale(1);opacity:1}}
   ```
5. **Replace `<CodeBlockCard label="X" command="Y" />`** with static markup:
   ```html
   <div class="tb-codecard"><span class="tb-codecard-label">X</span><code>Y</code><button class="tb-codecard-copy" onclick="navigator.clipboard.writeText('Y')">COPY</button></div>
   ```
   ```css
   .tb-codecard{display:flex;align-items:center;gap:14px;border:1px solid var(--border-2);border-left:3px solid #ff7f1f;background:var(--bg-3);padding:14px 18px;font-family:'JetBrains Mono',monospace;font-size:14px;color:var(--text);}
   .tb-codecard-label{font-size:11px;letter-spacing:.1em;color:var(--text-4);}
   .tb-codecard-copy{margin-left:auto;background:none;border:1px solid var(--border-2);color:var(--text-3);font-family:inherit;font-size:11px;padding:4px 10px;cursor:pointer;}
   ```
6. **Scoped-style caveat:** source styles were Astro-scoped; extracted they are
   page-global. That's fine — each page is standalone — but do not rename classes.
7. **T-numbers:** number patterns sequentially from your assigned block start,
   in source document order. One `tb-pattern` article per named pattern
   (usually each `<h3>`-headed demo group in the source).
8. **Catalog fragment:** also write `catalog/{category}.json`:
   ```json
   [
     { "id": "T200", "name": "Input field library", "category": "Forms",
       "file": "pages/forms.html", "anchor": "#T200",
       "description": "One-line description." }
   ]
   ```
9. **Design tokens** come from `assets/base.css` (vars: `--bg`, `--bg-2`, `--bg-3`,
   `--border`, `--border-2`, `--border-3`, `--text`, `--text-2`, `--text-3`,
   `--text-4`; accent `#ff7f1f`). Don't redefine them in pages.
10. Pages must work opened directly from disk (file://) — relative paths only,
    no fetch(), no external JS.

## T-number block allocation

| Block | Category | Source |
|---|---|---|
| T001–T009 | Foundations (colour, type) | styleguide.astro |
| T010–T029 | Elements | styleguide.astro |
| T030–T039 | Library components | styleguide.astro |
| T040–T069 | Named sections (mini previews) | styleguide.astro |
| T070–T099 | Patterns | styleguide.astro |
| T100–T119 | Animation | SgAnimation.astro |
| T120–T139 | Dev tools | SgDevtools.astro |
| T140–T159 | Social proof | SgSocial.astro |
| T160–T179 | Content | SgContent.astro |
| T180–T199 | Navigation | SgNavigation.astro |
| T200–T219 | Forms | SgForms.astro |
| T220–T239 | Feedback | SgFeedback.astro |
| T240–T259 | Data | SgData.astro |
| T260–T279 | Commerce | SgCommerce.astro |
| T280–T299 | Media | SgMedia.astro |
