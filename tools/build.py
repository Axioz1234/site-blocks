#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site Blocks: catalog and index builder.

Viewing the library needs no build step: every page is static HTML you can
open off disk. This script exists only so the two derived files cannot drift
from the per-category fragments that agents and humans actually edit.

Reads:
    catalog/_categories.json   category order, titles, blurbs, set membership
    catalog/<slug>.json        one array of block entries per category

Writes:
    catalog.json               the merged lookup table
    index.html                 the viewer index, between the BUILD markers

Run from the repo root:
    python tools/build.py
"""

import io
import json
import os
import re
import sys

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
            for field in ('id', 'name', 'category', 'set', 'file', 'anchor', 'description'):
                if field not in e:
                    problems.append('%s %s: missing "%s"' % (frag_path, e.get('id', '?'), field))
            if e.get('set') != cat['set']:
                problems.append('%s %s: set is "%s", category says "%s"'
                                % (frag_path, e.get('id'), e.get('set'), cat['set']))
            if e.get('file') != cat['file']:
                problems.append('%s %s: file is "%s", category says "%s"'
                                % (frag_path, e.get('id'), e.get('file'), cat['file']))
            if e.get('anchor') != '#' + e.get('id', ''):
                problems.append('%s %s: anchor "%s" does not match id'
                                % (frag_path, e.get('id'), e.get('anchor')))
        cat['entries'] = entries
        merged.extend(entries)

    # Duplicate T-numbers are the one error that silently breaks a lookup.
    seen = {}
    for e in merged:
        if e['id'] in seen:
            problems.append('duplicate id %s in %s and %s'
                            % (e['id'], seen[e['id']], e['file']))
        seen[e['id']] = e['file']

    # Every id in a fragment must have a matching anchor in its page.
    for cat in categories:
        page = os.path.join(ROOT, cat['file'])
        if not os.path.exists(page):
            if cat['entries']:
                problems.append('missing page: %s' % cat['file'])
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
        'description': ('T-numbered library of website sections and UI patterns in two '
                        'themes. Look up an ID, open its file, copy the markup inside '
                        '.tb-demo plus the page <style> rules it uses, and bring the '
                        'tokens from assets/base.css.'),
        'themes': ['dark', 'moonrite'],
        'sets': {
            'core': 'The original AstroAnimate-derived library.',
            'ecommerce': 'The retail set: catalogue, product, checkout, merchandising, account.',
        },
        'count': len(merged),
        'countBySet': counts,
        'patterns': merged,
    }
    with io.open(os.path.join(ROOT, 'catalog.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')

    # ---- index.html ----
    jump = []
    body = []
    for set_id, set_title, set_blurb in SET_LABELS:
        cats = [c for c in categories if c['set'] == set_id]
        if not cats:
            continue
        n = sum(len(c['entries']) for c in cats)
        body.append(
            '    <div class="tb-setrule" data-set="%s">\n'
            '      <h2>%s <span class="tb-range">%d blocks</span></h2>\n'
            '      <p>%s</p>\n'
            '    </div>\n' % (set_id, esc(set_title), n, esc(set_blurb)))
        for c in cats:
            jump.append('      <a href="#%s" data-set="%s">%s</a>'
                        % (c['anchor'], set_id, esc(c['title'])))
            rows = []
            for e in c['entries']:
                rows.append(
                    '        <tr><td><a href="%s%s">%s</a></td>'
                    '<td class="tb-name">%s</td><td>%s</td></tr>'
                    % (c['file'], e['anchor'], e['id'], esc(e['name']), esc(e['description'])))
            body.append(
                '    <section class="tb-cat" id="%s" data-set="%s">\n'
                '      <h2>%s <span class="tb-range">%s</span></h2>\n'
                '      <p>%s &middot; <a class="tb-viewpage" href="%s">View page &rarr;</a></p>\n'
                '      <table class="tb-table">\n%s\n      </table>\n'
                '    </section>\n'
                % (c['anchor'], set_id, esc(c['title']), block_range(c['entries']),
                   esc(c['description']), c['file'], '\n'.join(rows)))

    generated = ('%s\n    <nav class="tb-jump">\n%s\n    </nav>\n%s\n%s'
                 % (START, '\n'.join(jump), '\n'.join(body).rstrip(), END))

    index_path = os.path.join(ROOT, 'index.html')
    with io.open(index_path, encoding='utf-8') as fh:
        html = fh.read()
    if START not in html or END not in html:
        problems.append('index.html has no BUILD:START / BUILD:END markers, not rewritten')
    else:
        html = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: generated,
                      html, flags=re.S)
        html = re.sub(r'(<span class="tb-range" data-tb-count>)[^<]*(</span>)',
                      lambda m: m.group(1) + ('%d blocks' % len(merged)) + m.group(2), html)
        with io.open(index_path, 'w', encoding='utf-8') as fh:
            fh.write(html)

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
