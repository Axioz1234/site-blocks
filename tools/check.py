#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site Blocks: library checker.

Enforces the rules that keep the library reskinnable, and the ones that keep it
readable in every theme it declares. Run from the repo root:

    python tools/check.py

Checks
  1. No raw colour in any page. A hex or a numeric rgb()/rgba() inside a CSS
     declaration or a style attribute means that block is welded to one theme.
     Hex printed as visible text is allowed: foundations.html lists token values
     on purpose.
  2. No em dashes anywhere.
  3. Every page is wired: base.css, viewer.css, viewer.js, and a data-page-set.
  4. Every token a page uses actually exists in base.css.
  5. Contrast, per theme rather than once: every foreground token is walked
     against every surface token it is allowed to sit on, and anything under
     4.5:1 fails. A new theme has to clear this on its own values.
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Foreground token -> the surfaces it is allowed to sit on.
CONTRAST_PAIRS = [
    (['--text', '--text-2', '--text-3', '--text-4', '--accent'],
     ['--bg', '--bg-black', '--bg-2', '--bg-3', '--bg-card']),
    (['--accent-ink'], ['--accent', '--accent-deep']),
    (['--status-ink'], ['--ok', '--warn', '--err', '--info']),
    # Status and categorical colours land on inset wells and card fills as often
    # as on the page ground, so --bg-3 and --bg-card are walked too. Moonrite's
    # --bg-3 is cream, which erodes a colour tuned only for white.
    (['--ok'], ['--ok-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--warn'], ['--warn-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--err'], ['--err-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--info'], ['--info-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--cat-1', '--cat-2', '--cat-3', '--cat-4', '--cat-5'],
     ['--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--rating'], ['--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--sale'], ['--sale-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
    (['--sale-ink'], ['--sale']),
    (['--accent-light-ink'], ['--accent-light']),
    (['--muted'], ['--muted-wash', '--bg', '--bg-2', '--bg-3', '--bg-card']),
]
MIN_RATIO = 4.5


def parse_themes(css):
    """Return {theme_name: {token: hex}} for every :root block in base.css.

    Comments are stripped first. A comment that mentions a token by name, as in
    "not derived from --bg-black: that token is white...", otherwise parses as a
    declaration and overwrites the real value with prose, which silently drops
    that token's pairs from the contrast walk instead of failing loudly.
    """
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    themes = {}
    for m in re.finditer(r':root(\[data-theme="([a-z0-9-]+)"\])?\s*\{(.*?)\n\}', css, re.S):
        name = m.group(2) or 'dark'
        body = m.group(3)
        vals = themes.setdefault(name, {})
        for tok, val in re.findall(r'(--[a-z0-9-]+)\s*:\s*([^;]+);', body):
            vals[tok] = val.strip()
    # Every theme inherits anything it does not restate from dark.
    base = dict(themes.get('dark', {}))
    for name in themes:
        if name == 'dark':
            continue
        merged = dict(base)
        merged.update(themes[name])
        themes[name] = merged
    return themes


def srgb(hex_str):
    h = hex_str.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) == 8:      # ignore alpha for the ratio
        h = h[:6]
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    except ValueError:
        return None


def luminance(rgb):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def main():
    problems = []
    notes = []

    base_path = os.path.join(ROOT, 'assets', 'base.css')
    css = io.open(base_path, encoding='utf-8').read()
    themes = parse_themes(css)
    known_tokens = set()
    for vals in themes.values():
        known_tokens.update(vals)

    # ---- 1 to 4: per page ----
    pages = sorted(f for f in os.listdir(os.path.join(ROOT, 'pages')) if f.endswith('.html'))
    targets = [('index.html', 'index.html')] + [('pages/' + f, f) for f in pages]

    for rel, label in targets:
        path = os.path.join(ROOT, rel)
        html = io.open(path, encoding='utf-8').read()

        # Raw colours, but only where they would actually paint something.
        css_regions = re.findall(r'<style[^>]*>(.*?)</style>', html, re.S)
        css_regions += re.findall(r'style="([^"]*)"', html)
        for region in css_regions:
            for hexval in re.findall(r'#[0-9a-fA-F]{3,8}\b', region):
                problems.append('%s: raw colour %s in a style rule' % (label, hexval))
            for rgbval in re.findall(r'rgba?\(\s*\d', region):
                problems.append('%s: raw %s...) in a style rule' % (label, rgbval.strip()))

        if u'—' in html:
            problems.append('%s: contains an em dash' % label)

        if rel != 'index.html':
            for need in ('assets/base.css', 'assets/viewer.css', 'assets/viewer.js'):
                if need not in html:
                    problems.append('%s: not wired to %s' % (label, need))
            if not re.search(r'<body[^>]*data-page-set="(core|ecommerce)"', html):
                problems.append('%s: <body> has no valid data-page-set' % label)

        # A page may declare its own custom properties, for per-element values
        # like --pulse-color or a loop index --i. Those are local and fine. Only
        # a var() that resolves to nothing at all is a bug.
        # Scan the style regions, not the whole file: prose legitimately shows
        # var(--token) as a documentation example, and that is not a usage.
        local = set(re.findall(r'(--[a-z0-9-]+)\s*:', html))
        used = set()
        for region in css_regions:
            used.update(re.findall(r'var\((--[a-z0-9-]+)', region))
        for tok in used:
            if tok not in known_tokens and tok not in local:
                problems.append('%s: uses %s, which neither base.css nor the page defines'
                                % (label, tok))

    # ---- 4b: the palette page's static snapshot must not drift ----
    # foundations.html re-reads token values from the live stylesheet on load,
    # but it also ships a static snapshot as the JavaScript-off fallback. That
    # snapshot is what goes stale, so it is what gets checked. Theme class to
    # theme name, so a new theme's column has to be registered here too.
    SNAPSHOT_CLASSES = {'sg-hex-dark': 'dark', 'sg-hex-moon': 'moonrite'}
    fpath = os.path.join(ROOT, 'pages', 'foundations.html')
    if os.path.exists(fpath):
        fhtml = io.open(fpath, encoding='utf-8').read()
        documented = 0
        swatches = re.findall(r'data-token="(--[a-z0-9-]+)"(.*?)</div>\s*</div>', fhtml, re.S)
        if not swatches:
            problems.append('foundations.html: no data-token swatches found, so the palette '
                            'drift check is verifying nothing. Update tools/check.py to the '
                            'markup the page now uses.')
        for tok, rest in swatches:
            for cls, theme in SNAPSHOT_CLASSES.items():
                for val in re.findall(r'%s">([^<]+)</span>' % cls, rest):
                    actual = themes.get(theme, {}).get(tok)
                    if actual is None:
                        problems.append('foundations.html: documents %s, which base.css [%s] '
                                        'does not define' % (tok, theme))
                    elif actual.strip().lower() != val.strip().lower():
                        problems.append('foundations.html: %s [%s] snapshot says %s, base.css '
                                        'says %s' % (tok, theme, val.strip(), actual.strip()))
                    else:
                        documented += 1
        notes.append('palette page: %d snapshot values verified against base.css' % documented)

    # ---- 5: contrast, per theme ----
    for theme in sorted(themes):
        vals = themes[theme]
        checked = 0
        for fgs, bgs in CONTRAST_PAIRS:
            for fg in fgs:
                for bg in bgs:
                    fv, bv = vals.get(fg), vals.get(bg)
                    if not fv or not bv:
                        continue
                    f, b = srgb(fv), srgb(bv)
                    if not f or not b:
                        continue
                    checked += 1
                    r = ratio(f, b)
                    if r < MIN_RATIO:
                        problems.append('contrast [%s]: %s on %s is %.2f:1 (%s on %s)'
                                        % (theme, fg, bg, r, fv, bv))
        notes.append('contrast [%s]: %d pairs walked' % (theme, checked))

    print('themes: %s' % ', '.join(sorted(themes)))
    print('pages checked: %d' % len(targets))
    for n in notes:
        print(n)
    if problems:
        print('\n%d problem(s):' % len(problems))
        for p in problems:
            print('  - %s' % p)
        return 1
    print('\nclean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
