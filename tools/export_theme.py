#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site Blocks: single-theme export.

Produces a standalone copy of the library locked to one theme, with the viewer's
Theme and Set switches removed. Use it to drop the library into a client site as
a design reference, where the other theme and the switching chrome would only be
confusing.

    python tools/export_theme.py --theme moonrite \\
        --out "C:/Projects/Moonrite/storefront/public/brand/blocks" \\
        --title "Moonrite block library" \\
        --back-href /brand --back-label "Back to the brand guide"

What changes versus index.html:
  - data-theme is hardcoded on <html>, so the theme cannot be switched
  - assets/viewer.js is dropped, which is what renders the two switches
  - the header copy stops talking about switches and gains a back link
  - robots noindex, since this is an internal reference, not shop content
  - the sticky category headers move to the top of the viewport, because the
    toolbar they used to sit under is gone

Everything else is byte-for-byte the compiled page: the same blocks, the same
scoped CSS and JS. Run tools/build.py first.
"""

import argparse
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def export(theme, out_dir, title, back_href, back_label, noindex=True):
    src = os.path.join(ROOT, 'index.html')
    html = io.open(src, encoding='utf-8').read()

    base_css = io.open(os.path.join(ROOT, 'assets', 'base.css'),
                       encoding='utf-8').read()
    if theme != 'dark' and ('[data-theme="%s"]' % theme) not in base_css:
        raise SystemExit('base.css declares no theme "%s"' % theme)

    # 1. Lock the theme on the root element.
    if theme == 'dark':
        html = html.replace('<html lang="en">', '<html lang="en">', 1)
    else:
        html = html.replace('<html lang="en">',
                            '<html lang="en" data-theme="%s">' % theme, 1)

    # 2. Drop the switcher. viewer.js is the only thing that renders the
    #    toolbar, so removing it removes both switches.
    html = html.replace('  <script src="assets/viewer.js"></script>\n', '')

    # 3. Title and robots.
    html = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, html,
                  flags=re.S)
    if noindex:
        html = html.replace(
            '  <meta name="viewport"',
            '  <meta name="robots" content="noindex, nofollow">\n'
            '  <meta name="viewport"', 1)

    # 4. Header: no switch instructions, plus a way back to the host site.
    back = ''
    if back_href:
        back = ('    <a class="tb-back" href="%s">&larr; %s</a>\n'
                % (back_href, back_label))
    header = (
        '  <header class="tb-header">\n'
        '%s'
        '    <p class="eyebrow">Block library</p>\n'
        '    <h1>%s <span class="tb-range" data-tb-count>0 blocks</span></h1>\n'
        '    <p class="tb-sub">Every block has a T-number. The list comes first, then '
        'every block in full below it: scroll, or use a T-number to jump straight to '
        'one.</p>\n'
        '    <p class="tb-lede">Nothing here hardcodes a colour. Every block reads the '
        'brand tokens, which is why the whole library renders in the brand without any '
        'block being rewritten.</p>\n'
        '  </header>' % (back, title))
    html = re.sub(r'<header class="tb-header">.*?</header>', lambda m: header,
                  html, flags=re.S, count=1)

    # Restore the real count, which lived in the header we just replaced.
    n = len(re.findall(r'<article class="tb-pattern" id="T\d+"', html))
    html = html.replace('data-tb-count>0 blocks<', 'data-tb-count>%d blocks<' % n)

    # The palette block's column classes are sg-hex-<short>, where the short
    # name is the theme id truncated to four characters.
    col = 'dark' if theme == 'dark' else theme[:4]
    other_col = 'moon' if theme == 'dark' else 'dark'

    # 4b. Copy that only made sense next to a switch.
    html = html.replace(
        'Every one is token-driven, so the theme switch above reskins the lot.',
        'Every one is token-driven, which is why they all render in this brand '
        'palette and type without a single block being rewritten.')

    # 5. The sticky category headers were offset under the toolbar.
    html = html.replace('  </style>\n  <!-- Compiled from pages',
                        '    /* No toolbar in the export, so the sticky category\n'
                        '       headers sit against the top of the viewport. */\n'
                        '    .tb-srchead { top: 0; }\n'
                        '    /* The palette block documents every theme side by side.\n'
                        '       Only one of them exists here, so the other column is\n'
                        '       noise: hide it and keep the active one. */\n'
                        '    .sg-val:has(.sg-hex-%s) { display: none; }\n' % other_col +
                        '    /* Clear the sticky category header, about 85px tall,\n'
                        '       so a jumped-to block is not hidden underneath it. */\n'
                        '    .tb-blocksrule, .tb-cat, .tb-srchead h2 { scroll-margin-top: 20px; }\n'
                        '    .tb-pattern { scroll-margin-top: 100px; }\n'
                        '  </style>\n  <!-- Compiled from pages', 1)

    # 6. Deep links. viewer.js is gone, and it carried the fix for the fact that
    #    offscreen blocks only estimate their height until they render, which
    #    makes a #T320 on first load land short. Inline the jump on its own.
    html = html.replace('</body>',
                        '  <script>\n'
                        '    (function () {\n'
                        '      function jump() {\n'
                        '        if (!window.location.hash) return;\n'
                        '        var el = document.getElementById(window.location.hash.slice(1));\n'
                        '        if (el) el.scrollIntoView();\n'
                        '      }\n'
                        '      window.addEventListener("load", function () {\n'
                        '        jump();\n'
                        '        window.setTimeout(jump, 120);\n'
                        '      });\n'
                        '    })();\n'
                        '  </script>\n</body>', 1)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    assets_out = os.path.join(out_dir, 'assets')
    if not os.path.isdir(assets_out):
        os.makedirs(assets_out)
    for name in ('base.css', 'viewer.css'):
        shutil.copyfile(os.path.join(ROOT, 'assets', name),
                        os.path.join(assets_out, name))

    with io.open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(html)

    # Guards: a silent failure here ships a switcher or the wrong theme.
    problems = []
    if 'viewer.js' in html:
        problems.append('viewer.js is still referenced, the switcher would render')
    if theme != 'dark' and 'data-theme="%s"' % theme not in html:
        problems.append('the theme attribute was not applied')
    if 'tb-seg-btn' in html:
        problems.append('switch markup found in the output')
    if n == 0:
        problems.append('no blocks in the output, run tools/build.py first')
    if ('sg-hex-%s' % col) not in html:
        problems.append('the palette block has no "%s" column, so hiding the other '
                        'one would leave no values at all' % col)
    return n, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--title', default='Block library')
    ap.add_argument('--back-href', default='')
    ap.add_argument('--back-label', default='Back')
    ap.add_argument('--index', action='store_true',
                    help='allow search engines to index the export')
    a = ap.parse_args()
    n, problems = export(a.theme, a.out, a.title, a.back_href, a.back_label,
                         noindex=not a.index)
    print('exported %d blocks, theme "%s" -> %s' % (n, a.theme, a.out))
    if problems:
        for p in problems:
            print('  - %s' % p)
        return 1
    print('clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
