#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site Blocks: catalog and page builder.

The library is browsed as ONE scrollable page. index.html carries the block list
and then every block inlined beneath it, so nothing has to be clicked into.

It is authored, though, as one self-contained file per category under pages/.
Those files are the source. This script compiles them into index.html, scoping
each one's CSS and JS so the categories cannot interfere with each other. See
tools/compile_page.py for why that scoping is necessary.

Reads:
    catalog/_categories.json   category order, titles, blurbs, set membership
    catalog/<slug>.json        one array of block entries per category
    pages/<slug>.html          the blocks themselves

Writes:
    catalog.json               the merged lookup table
    index.html                 the whole library, between the BUILD markers

Run from the repo root:
    python tools/build.py
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compile_page import scope_css, wrap_script, verify_scoped, SCOPE_RUNTIME

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = '<!-- BUILD:START -->'
END = '<!-- BUILD:END -->'

SET_LABELS = [
    ('core', 'Core library',
     'The original library extracted from the AstroAnimate site design: '
     'foundations, sections, patterns and UI. Every one is token-driven, so '
     'the theme switch above reskins the lot.'),
    ('ecommerce', 'E-commerce',
     'The retail set. Catalogue, product page, cart and checkout, '
     'merchandising and trust, account and post-purchase. Built for '
     'single-product and small-catalogue stores, not marketplaces.'),
]


def esc(s):
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;'))


def load(path):
    with io.open(os.path.join(ROOT, path), encoding='utf-8') as fh:
        return json.load(fh)


def block_range(entries):
    ids = sorted(e['id'] for e in entries)
    if not ids:
        return ''
    if ids[0] == ids[-1]:
        return ids[0]
    return '%s&ndash;%s' % (ids[0], ids[-1])


def read_source(path):
    """Pull the blocks, the styles and the script out of a source page."""
    html = io.open(path, encoding='utf-8').read()
    m = re.search(r'<main class="tb-main">(.*?)</main>', html, re.S)
    blocks = m.group(1).strip() if m else ''
    styles = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
    scripts = '\n'.join(
        re.findall(r'<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>', html, re.S))
    return blocks, styles, scripts


def main():
    categories = load('catalog/_categories.json')
    merged = []
    problems = []

    for cat in categories:
        frag_path = 'catalog/%s.json' % cat['slug']
        if not os.path.exists(os.path.join(ROOT, frag_path)):
            problems.append('missing fragment: %s' % frag_path)
            cat['entries'] = []
            continue
        entries = load(frag_path)
        for e in entries:
            for field in ('id', 'name', 'category', 'set', 'page', 'anchor',
                          'source', 'description'):
                if field not in e:
                    problems.append('%s %s: missing "%s"'
                                    % (frag_path, e.get('id', '?'), field))
            if e.get('set') != cat['set']:
                problems.append('%s %s: set is "%s", category says "%s"'
                                % (frag_path, e.get('id'), e.get('set'), cat['set']))
            if e.get('source') != cat['file']:
                problems.append('%s %s: source is "%s", category says "%s"'
                                % (frag_path, e.get('id'), e.get('source'), cat['file']))
            if e.get('anchor') != '#' + e.get('id', ''):
                problems.append('%s %s: anchor "%s" does not match id'
                                % (frag_path, e.get('id'), e.get('anchor')))
        cat['entries'] = entries
        merged.extend(entries)

    # Duplicate T-numbers are the one error that silently breaks a lookup, and
    # in a single document they also produce duplicate element ids.
    seen = {}
    for e in merged:
        if e['id'] in seen:
            problems.append('duplicate id %s in %s and %s'
                            % (e['id'], seen[e['id']], e.get('source')))
        seen[e['id']] = e.get('source')

    # Every id in a fragment must have a matching anchor in its source page.
    for cat in categories:
        page = os.path.join(ROOT, cat['file'])
        if not os.path.exists(page):
            if cat['entries']:
                problems.append('missing source page: %s' % cat['file'])
            continue
        with io.open(page, encoding='utf-8') as fh:
            html = fh.read()
        anchors = set(re.findall(r'id="(T\d+)"', html))
        ids = set(e['id'] for e in cat['entries'])
        for missing in sorted(ids - anchors):
            problems.append('%s: catalog lists %s but the page has no anchor for it'
                            % (cat['file'], missing))
        for orphan in sorted(anchors - ids):
            problems.append('%s: page has anchor %s but the catalog does not list it'
                            % (cat['file'], orphan))

    # ---- catalog.json ----
    counts = {}
    for e in merged:
        counts[e['set']] = counts.get(e['set'], 0) + 1
    catalog = {
        'name': 'site-blocks',
        'description': ('T-numbered library of website sections and UI patterns in '
                        'two themes, all on one page. Look up an ID, open '
                        'index.html at its anchor, and copy the markup inside that '
                        'block\'s .tb-demo wrapper plus the tokens from '
                        'assets/base.css. The "source" field is the authoring file '
                        'the block is compiled from, which carries its CSS and JS '
                        'unscoped and is the easier one to lift from.'),
        'themes': ['dark', 'moonrite'],
        'sets': {
            'core': 'The original AstroAnimate-derived library.',
            'ecommerce': ('The retail set: catalogue, product, checkout, '
                          'merchandising, account.'),
        },
        'page': 'index.html',
        'count': len(merged),
        'countBySet': counts,
        'patterns': merged,
    }
    with io.open(os.path.join(ROOT, 'catalog.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')

    # ---- index.html ----
    jump, listing, sections, styles, scripts = [], [], [], [], []

    for set_id, set_title, set_blurb in SET_LABELS:
        cats = [c for c in categories if c['set'] == set_id]
        if not cats:
            continue
        n = sum(len(c['entries']) for c in cats)
        listing.append(
            '    <div class="tb-setrule" data-set="%s">\n'
            '      <h2>%s <span class="tb-range">%d blocks</span></h2>\n'
            '      <p>%s</p>\n'
            '    </div>\n' % (set_id, esc(set_title), n, esc(set_blurb)))
        for c in cats:
            jump.append('      <a href="#%s" data-set="%s">%s</a>'
                        % (c['anchor'], set_id, esc(c['title'])))
            rows = []
            for e in c['entries']:
                # In-page anchors: the whole library is one document now.
                rows.append(
                    '        <tr><td><a href="%s">%s</a></td>'
                    '<td class="tb-name">%s</td><td>%s</td></tr>'
                    % (e['anchor'], e['id'], esc(e['name']), esc(e['description'])))
            listing.append(
                '    <section class="tb-cat" id="cat-%s" data-set="%s">\n'
                '      <h2>%s <span class="tb-range">%s</span></h2>\n'
                '      <p>%s &middot; <a class="tb-viewpage" href="#%s">'
                'Jump to the blocks &darr;</a></p>\n'
                '      <table class="tb-table">\n%s\n      </table>\n'
                '    </section>\n'
                % (c['anchor'], set_id, esc(c['title']), block_range(c['entries']),
                   esc(c['description']), c['anchor'], '\n'.join(rows)))

    # The blocks themselves, one scoped section per source page.
    for set_id, _title, _blurb in SET_LABELS:
        for c in [x for x in categories if x['set'] == set_id]:
            if not c['entries']:
                continue
            src = os.path.join(ROOT, c['file'])
            if not os.path.exists(src):
                continue
            blocks, css, js = read_source(src)
            scope = 'src-' + c['slug']
            if css.strip():
                styles.append('/* ===== %s (%s) ===== */\n%s'
                              % (c['title'], c['file'],
                                 scope_css(css, '.' + scope, c['slug'])))
            if js.strip():
                scripts.append('/* ===== %s ===== */\n%s'
                               % (c['title'], wrap_script(js, scope)))
            sections.append(
                '    <section class="tb-src %s" id="%s" data-set="%s">\n'
                '      <div class="tb-srchead">\n'
                '        <h2 id="%s">%s <span class="tb-range">%s</span></h2>\n'
                '        <p>%s</p>\n'
                '        <a class="tb-tolist" href="#cat-%s">Back to the list &uarr;</a>\n'
                '      </div>\n%s\n    </section>\n'
                % (scope, scope, set_id, c['anchor'], esc(c['title']),
                   block_range(c['entries']), esc(c['description']), c['anchor'],
                   blocks))

    generated = (
        START + '\n'
        '    <nav class="tb-jump">\n' + '\n'.join(jump) + '\n    </nav>\n'
        + '\n'.join(listing).rstrip() + '\n'
        '    <div class="tb-blocksrule" id="blocks">\n'
        '      <h2>The blocks</h2>\n'
        '      <p>Every block below, in T order. Nothing to click into: scroll, or '
        'use a T-number from the list above.</p>\n'
        '    </div>\n'
        + '\n'.join(sections).rstrip() + '\n' + END)

    index_path = os.path.join(ROOT, 'index.html')
    with io.open(index_path, encoding='utf-8') as fh:
        html = fh.read()
    if START not in html or END not in html:
        problems.append('index.html has no BUILD:START / BUILD:END markers, '
                        'not rewritten')
    else:
        html = re.sub(re.escape(START) + r'.*?' + re.escape(END),
                      lambda m: generated, html, flags=re.S)
        html = re.sub(r'(<span class="tb-range" data-tb-count>)[^<]*(</span>)',
                      lambda m: m.group(1) + ('%d blocks' % len(merged)) + m.group(2),
                      html)
        style_block = ('<style id="tb-compiled-css">\n%s\n  </style>'
                       % '\n\n'.join(styles))
        script_block = ('<script id="tb-compiled-js">\n%s\n%s\n  </script>'
                        % (SCOPE_RUNTIME, '\n\n'.join(scripts)))
        if '<style id="tb-compiled-css">' not in html:
            problems.append('index.html has no tb-compiled-css placeholder')
        if '<script id="tb-compiled-js">' not in html:
            problems.append('index.html has no tb-compiled-js placeholder')
        html = re.sub(r'<style id="tb-compiled-css">.*?</style>',
                      lambda m: style_block, html, flags=re.S)
        html = re.sub(r'<script id="tb-compiled-js">.*?</script>',
                      lambda m: script_block, html, flags=re.S)
        with io.open(index_path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        print('compiled index.html: %d scoped stylesheets, %d scoped scripts, %.2f MB'
              % (len(styles), len(scripts), len(html) / 1048576.0))

    print('%d blocks across %d categories (%s)'
          % (len(merged), len([c for c in categories if c['entries']]),
             ', '.join('%s %d' % (k, v) for k, v in sorted(counts.items()))))
    if problems:
        print('\n%d problem(s):' % len(problems))
        for p in problems:
            print('  - %s' % p)
        return 1
    print('clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
