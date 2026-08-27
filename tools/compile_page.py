#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site Blocks: single-page compiler helpers.

The library is browsed as one scrollable document, but it is authored as one
self-contained file per category under pages/. Those files were written
independently, so merging them naively does not work:

  - 44 class names are shared between pages, and some carry DIFFERENT rules.
    `.sgx-preview` genuinely differs between animation.html and commerce.html.
  - 11 page scripts query generic state classes (`.is-active`, `.on`, `.is-on`),
    so one page's script would drive another page's blocks.
  - `@keyframes tbPulse` is declared in three pages.

So each source page is isolated at build time instead:

  CSS  every selector is prefixed with that page's scope class, `:root` rules are
       remapped onto the scope, and @keyframes are renamed and their references
       rewritten. A class is used rather than an id so the specificity bump stays
       at 10 and base.css theme overrides still win where they should.

  JS   the page's script is wrapped in a function whose `document` is shadowed by
       a scoped proxy: querySelector, querySelectorAll and friends only ever see
       that page's subtree. Everything else forwards to the real document, so
       createElement and body still behave.

Nothing in pages/ has to change, and a block copied out of the compiled page is
still the original markup.
"""

import re

# ---------------------------------------------------------------- CSS

def _split_top_level(css):
    """Yield (kind, prelude, body_or_None) for each top-level construct.

    Brace-aware and string-aware, so a `{` inside content:"..." or a comment
    does not desynchronise the parser.
    """
    out = []
    i = 0
    n = len(css)
    prelude_start = 0
    depth = 0
    body_start = None
    quote = None
    while i < n:
        ch = css[i]
        if quote:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in '"\'':
            quote = ch
            i += 1
            continue
        if css.startswith('/*', i):
            end = css.find('*/', i + 2)
            i = (end + 2) if end != -1 else n
            continue
        if ch == '{':
            if depth == 0:
                body_start = i
            depth += 1
            i += 1
            continue
        if ch == '}':
            depth -= 1
            if depth == 0:
                prelude = css[prelude_start:body_start]
                body = css[body_start + 1:i]
                out.append((prelude, body))
                prelude_start = i + 1
                body_start = None
            i += 1
            continue
        i += 1
    tail = css[prelude_start:].strip()
    if tail:
        out.append((tail, None))
    return out


def _prefix_selector_list(selectors, scope):
    parts = []
    for sel in selectors.split(','):
        s = sel.strip()
        if not s:
            continue
        if s.startswith(':root'):
            # A page-local custom property block. Bind it to the scope so the
            # override stays inside this category instead of going global.
            parts.append(scope + s[len(':root'):])
        elif s.split()[0] in ('html', 'body'):
            parts.append(scope + s[len(s.split()[0]):])
        elif s.startswith('@'):
            parts.append(s)
        else:
            parts.append('%s %s' % (scope, s))
    return ', '.join(parts)


def scope_css(css, scope, kf_prefix):
    """Prefix every selector with `scope` and namespace @keyframes."""
    keyframes = set()
    for m in re.finditer(r'@(?:-webkit-)?keyframes\s+([\w-]+)', css):
        keyframes.add(m.group(1))

    def render(constructs, indent=''):
        chunks = []
        for prelude, body in constructs:
            pre = prelude.strip()
            if body is None:
                if pre:
                    chunks.append(pre)
                continue
            low = pre.lower()
            if low.startswith('@keyframes') or low.startswith('@-webkit-keyframes'):
                name = re.split(r'\s+', pre, 1)[1].strip()
                chunks.append('%s %s-%s {%s}' % (re.split(r'\s+', pre, 1)[0],
                                                 kf_prefix, name, body))
            elif low.startswith('@media') or low.startswith('@supports') \
                    or low.startswith('@container') or low.startswith('@layer'):
                inner = render(_split_top_level(body))
                chunks.append('%s {\n%s\n}' % (pre, inner))
            elif low.startswith('@'):
                # @font-face, @page and friends: no selector to scope.
                chunks.append('%s {%s}' % (pre, body))
            else:
                chunks.append('%s {%s}' % (_prefix_selector_list(pre, scope), body))
        return '\n'.join(chunks)

    out = render(_split_top_level(css))

    # Rewrite references to the renamed keyframes, in `animation` shorthand and
    # in `animation-name`. Word-boundary matched so `spin` does not hit `spinner`.
    for name in sorted(keyframes, key=len, reverse=True):
        out = re.sub(r'(animation(?:-name)?\s*:[^;}]*?)\b%s\b' % re.escape(name),
                     lambda m: m.group(1) + '%s-%s' % (kf_prefix, name), out)
    return out


# ---------------------------------------------------------------- JS

SCOPE_RUNTIME = """
/* Site Blocks: per-category script isolation.
   Each page script below runs with `document` shadowed by a scoped proxy, so a
   query for a generic class such as .is-active cannot reach another category's
   blocks. Anything that is not a lookup forwards to the real document. */
(function () {
  var realDoc = document;
  window.__sbScopedDoc = function (root) {
    if (!root) return realDoc;
    function inScope(node) {
      return node && root.contains(node) ? node : null;
    }
    var overrides = {
      querySelector: function (s) { return root.querySelector(s); },
      querySelectorAll: function (s) { return root.querySelectorAll(s); },
      getElementsByClassName: function (c) { return root.getElementsByClassName(c); },
      getElementsByTagName: function (t) { return root.getElementsByTagName(t); },
      getElementById: function (id) {
        var esc = (window.CSS && CSS.escape) ? CSS.escape(id) : id;
        /* Ids are unique library-wide, so fall back to the real lookup rather
           than returning null for a legitimately global reference. */
        return root.querySelector('#' + esc) || inScope(realDoc.getElementById(id))
               || realDoc.getElementById(id);
      }
    };
    if (typeof Proxy !== 'function') {
      var plain = Object.create(realDoc);
      for (var k in overrides) plain[k] = overrides[k];
      return plain;
    }
    return new Proxy(realDoc, {
      get: function (target, prop) {
        if (Object.prototype.hasOwnProperty.call(overrides, prop)) return overrides[prop];
        var v = target[prop];
        return (typeof v === 'function') ? v.bind(target) : v;
      },
      set: function (target, prop, value) { target[prop] = value; return true; }
    });
  };
})();
"""


def wrap_script(js, root_id):
    """Run a page script against a scoped document.

    The root element is resolved in the outer scope and passed in, because
    `var document` is hoisted inside the wrapper: reading `document` on the
    same line that declares it would read undefined.
    """
    return (
        '(function (__sbRoot) {\n'
        '  var document = window.__sbScopedDoc(__sbRoot);\n'
        '%s\n'
        '})(window.document.getElementById(%r));' % (js.rstrip(), root_id))
