/* ============================================================
   Site Blocks: viewer.js
   Viewer chrome only. Nothing here is part of a block: never copy
   it into a target project.

   Two switches:
     THEME  Dark (default) / Moonrite   -> data-theme on <html>
     SET    All / Core / E-commerce     -> filters index.html

   Load it as a classic script in <head>, before the stylesheets
   are used, so the theme lands before first paint:

     <script src="../assets/viewer.js"></script>

   Relative classic scripts run from file://, so pages still work
   opened straight off disk. With JavaScript off, everything
   renders in Dark and nothing is filtered.
   ============================================================ */
(function () {
  'use strict';

  var THEMES = [
    { id: 'dark', label: 'Dark', attr: null },
    { id: 'moonrite', label: 'Moonrite', attr: 'moonrite' }
  ];
  var SETS = [
    { id: 'all', label: 'All' },
    { id: 'core', label: 'Core' },
    { id: 'ecommerce', label: 'E-commerce' }
  ];
  var THEME_KEY = 'siteblocks:theme';
  var SET_KEY = 'siteblocks:set';

  /* localStorage is unavailable or throws on some file:// origins.
     Fall back to in-memory so the switches still work per page. */
  var mem = {};
  function read(k, fallback) {
    try {
      var v = window.localStorage.getItem(k);
      return v === null ? (k in mem ? mem[k] : fallback) : v;
    } catch (e) {
      return k in mem ? mem[k] : fallback;
    }
  }
  function write(k, v) {
    mem[k] = v;
    try { window.localStorage.setItem(k, v); } catch (e) { /* no-op */ }
  }

  function themeById(id) {
    for (var i = 0; i < THEMES.length; i++) if (THEMES[i].id === id) return THEMES[i];
    return THEMES[0];
  }

  /* ---- 1. Apply the theme now, before paint ---- */
  var current = themeById(read(THEME_KEY, 'dark'));
  function applyTheme(t) {
    current = t;
    if (t.attr) document.documentElement.setAttribute('data-theme', t.attr);
    else document.documentElement.removeAttribute('data-theme');
    write(THEME_KEY, t.id);
  }
  applyTheme(current);

  /* ---- 2. Build the toolbar once the header exists ---- */
  function seg(name, options, activeId, onPick) {
    var wrap = document.createElement('div');
    wrap.className = 'tb-seg';
    var lab = document.createElement('span');
    lab.className = 'tb-seg-label';
    lab.textContent = name;
    wrap.appendChild(lab);
    var group = document.createElement('div');
    group.className = 'tb-seg-group';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', name);
    options.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'tb-seg-btn';
      b.textContent = o.label;
      b.dataset.value = o.id;
      b.setAttribute('aria-pressed', String(o.id === activeId));
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(group.children, function (c) {
          c.setAttribute('aria-pressed', String(c === b));
        });
        onPick(o);
      });
      group.appendChild(b);
    });
    wrap.appendChild(group);
    return wrap;
  }

  function applySet(id) {
    write(SET_KEY, id);
    var cats = document.querySelectorAll('[data-set]');
    Array.prototype.forEach.call(cats, function (el) {
      if (el === document.body) return;
      var match = id === 'all' || el.getAttribute('data-set') === id;
      el.hidden = !match;
    });
    var count = document.querySelector('[data-tb-count]');
    if (count) {
      var n = 0;
      Array.prototype.forEach.call(document.querySelectorAll('.tb-cat[data-set]'), function (s) {
        if (!s.hidden) n += s.querySelectorAll('.tb-table tr').length;
      });
      count.textContent = n + ' blocks';
    }
  }

  function init() {
    var header = document.querySelector('.tb-header');
    if (!header) return;

    var bar = document.createElement('div');
    bar.className = 'tb-toolbar';
    var inner = document.createElement('div');
    inner.className = 'tb-toolbar-inner';

    inner.appendChild(seg('Theme', THEMES, current.id, function (o) {
      applyTheme(o);
    }));

    /* The set switch only filters a page that has sets to filter,
       which is the index. A category page instead states which set
       it belongs to, read from <body data-page-set="...">. */
    var isIndex = !!document.querySelector('.tb-cat[data-set]');
    if (isIndex) {
      var activeSet = read(SET_KEY, 'all');
      inner.appendChild(seg('Set', SETS, activeSet, function (o) {
        applySet(o.id);
      }));
      applySet(activeSet);
    } else {
      var ps = document.body.getAttribute('data-page-set');
      if (ps) {
        var badge = document.createElement('span');
        badge.className = 'tb-set-badge tb-set-' + ps;
        badge.textContent = ps === 'ecommerce' ? 'E-commerce set' : 'Core set';
        inner.appendChild(badge);
      }
    }

    bar.appendChild(inner);
    document.body.insertBefore(bar, header);
  }

  /* ---- 3. Deep links ----
     Offscreen blocks use content-visibility, so their height is an estimate
     until they render. A #T320 in the URL therefore lands short on first load.
     Re-run the jump once layout has settled. In-page clicks are unaffected. */
  function jumpToHash() {
    if (!window.location.hash) return;
    var el = document.getElementById(window.location.hash.slice(1));
    if (el) el.scrollIntoView();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  window.addEventListener('load', function () {
    jumpToHash();
    window.setTimeout(jumpToHash, 120);
  });
})();
