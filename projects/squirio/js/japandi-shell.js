/* Japandi Dev global navigation and scroll reveal for embedded project pages.

   The behaviour is the site-wide one in /assets/js/shell.js; this file only
   names the jd-* markup, the breakpoint the shell stylesheet collapses at, and
   this page's reveal class.
   There is no scroll sentinel on project pages, so the shell falls back to
   reading scrollY for the header's scrolled state.

   The links selector covers in-page anchors only. On the privacy policy page
   the nav points at other pages, so the shell leaves its static
   aria-current="page" alone. */
(function () {
  'use strict';

  if (!window.JapandiShell) return;

  window.JapandiShell.init({
    header: '[data-jd-header]',
    toggle: '[data-jd-nav-toggle]',
    nav: '[data-jd-nav]',
    links: '[data-jd-nav] .jd-nav__list a',
    desktop: '(min-width: 860px)',
    /* Scroll reveal, previously a second implementation of its own in
       js/main.js. Squirio keeps its own class name and tuning; only the
       algorithm is shared. */
    reveal: {
      selector: '.reveal',
      visibleClass: 'is-visible',
      rootMargin: '0px 0px -8% 0px',
      threshold: 0.08
    }
  });
})();
