/* ==========================================================================
   Japandi Dev — script.js

   Homepage behaviour. The header itself (menu, scrolled state, current-section
   marker) and the scroll reveal are shared with the project pages and live in
   shell.js; this file supplies the selectors and adds the one thing only these
   pages need.

   Progressive enhancement only. Every piece of content on this site is present
   and reachable in the HTML; this file improves navigation and presentation.
   Loaded with `defer`, so the DOM is already parsed when init() runs.

   No globals, no dependencies, no third-party requests. Text is written with
   textContent rather than innerHTML so no markup is ever parsed from a string.
   ========================================================================== */

(function () {
  'use strict';

  /* Tells the inline snippet in <head> that this file ran. If it never does, that
     snippet drops the `js` class on load and the no-JavaScript layout applies. */
  document.documentElement.dataset.enhanced = 'true';

  /** Keeps the footer copyright current; the HTML carries a working fallback. */
  function initCurrentYear(element) {
    if (!element) return;
    element.textContent = String(new Date().getFullYear());
  }

  function init() {
    /* The desktop query matches the breakpoint at which the nav stops
       collapsing (see styles.css §7); change both together. */
    window.JapandiShell.init({
      header: '[data-site-header]',
      toggle: '[data-nav-toggle]',
      nav: '[data-site-nav]',
      links: '[data-site-nav] .site-nav__list a',
      sentinel: '[data-scroll-sentinel]',
      desktop: '(min-width: 62em)',
      /* The algorithm lives in shell.js; the selector, class and tuning are
         this site's own. */
      reveal: {
        selector: '[data-reveal]',
        visibleClass: 'is-revealed',
        rootMargin: '0px 0px -40px 0px',
        threshold: 0.1
      }
    });

    initCurrentYear(document.querySelector('[data-current-year]'));
  }

  init();
})();
