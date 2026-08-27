/* ==========================================================================
   Squirio site behaviour: scroll reveal.
   No dependencies, no build step.

   The header menu lives in js/japandi-shell.js, which owns the jd-* shell
   markup this page shares with the rest of japandi.dev.
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     Scroll reveal. Purely decorative, so anything that goes wrong should
     leave the content visible rather than hidden.
     ------------------------------------------------------------------ */
  var reveals = document.querySelectorAll('.reveal');

  if (!('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    Array.prototype.forEach.call(reveals, function (el) { el.classList.add('is-visible'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  Array.prototype.forEach.call(reveals, function (el) { io.observe(el); });
})();
