/* ==========================================================================
   Japandi Dev — script.js

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

  /* Matches the breakpoint at which the nav stops collapsing (see styles.css §7). */
  var DESKTOP_NAV = '(min-width: 62em)';
  var REDUCED_MOTION = '(prefers-reduced-motion: reduce)';
  var OPEN_CLASS = 'is-nav-open';
  var SCROLLED_CLASS = 'is-scrolled';
  var REVEALED_CLASS = 'is-revealed';

  /**
   * Small-screen navigation, built as an ARIA disclosure rather than a modal:
   * no focus trap, so there is no way to strand keyboard users inside it.
   */
  function initMobileNav(header, toggle, nav) {
    if (!header || !toggle || !nav) return;

    function isOpen() {
      return header.classList.contains(OPEN_CLASS);
    }

    function setOpen(open) {
      header.classList.toggle(OPEN_CLASS, open);
      toggle.setAttribute('aria-expanded', String(open));
    }

    function close(returnFocus) {
      if (!isOpen()) return;
      setOpen(false);
      if (returnFocus) toggle.focus();
    }

    toggle.addEventListener('click', function () {
      setOpen(!isOpen());
    });

    /* Escape closes the disclosure and returns focus to the control that opened it. */
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') close(true);
    });

    /* Following an in-page link should not leave the panel covering the target. */
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) close(false);
    });

    /* Growing past the breakpoint reveals the full nav, so drop the open state. */
    addMediaListener(window.matchMedia(DESKTOP_NAV), function (event) {
      if (event.matches) close(false);
    });
  }

  /**
   * Adds a scrolled state to the header once the sentinel at the top of the page
   * leaves the viewport. An observer avoids running work on every scroll frame.
   */
  function initHeaderScrollState(header, sentinel) {
    if (!header || !sentinel || !('IntersectionObserver' in window)) return;

    var observer = new IntersectionObserver(function (entries) {
      header.classList.toggle(SCROLLED_CLASS, !entries[0].isIntersecting);
    });

    observer.observe(sentinel);
  }

  /**
   * Marks the nav link for the section currently in view with aria-current, so the
   * state is exposed natively rather than by styling alone. Absent without JavaScript.
   */
  function initSectionHighlight(links) {
    if (!links.length || !('IntersectionObserver' in window)) return;

    var sections = [];
    var linkFor = {};

    links.forEach(function (link) {
      var href = link.getAttribute('href') || '';
      if (href.charAt(0) !== '#') return;
      var section = document.getElementById(href.slice(1));
      if (!section) return;
      sections.push(section);
      linkFor[section.id] = link;
    });
    if (!sections.length) return;

    var inView = {};

    /* The first section in document order that is inside the band wins, so
       overlapping sections never leave two links marked at once. */
    function update() {
      var current = null;
      for (var i = 0; i < sections.length; i++) {
        if (inView[sections[i].id]) {
          current = sections[i].id;
          break;
        }
      }
      sections.forEach(function (section) {
        var link = linkFor[section.id];
        if (section.id === current) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        inView[entry.target.id] = entry.isIntersecting;
      });
      update();
    }, { rootMargin: '-25% 0px -60% 0px' });

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

  /**
   * Reveals sections as they enter the viewport. Anything that cannot be
   * observed is shown immediately, so content is never left hidden.
   */
  function initRevealOnScroll(elements) {
    if (!elements.length) return;

    function revealAll() {
      elements.forEach(function (element) {
        element.classList.add(REVEALED_CLASS);
      });
    }

    if (window.matchMedia(REDUCED_MOTION).matches || !('IntersectionObserver' in window)) {
      revealAll();
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add(REVEALED_CLASS);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.1 });

    elements.forEach(function (element) {
      observer.observe(element);
    });
  }

  /** Keeps the footer copyright current; the HTML carries a working fallback. */
  function initCurrentYear(element) {
    if (!element) return;
    element.textContent = String(new Date().getFullYear());
  }

  /** Safari below 14 exposes addListener but not addEventListener on MediaQueryList. */
  function addMediaListener(mediaQuery, handler) {
    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handler);
      return;
    }
    mediaQuery.addListener(handler);
  }

  function toArray(nodeList) {
    return Array.prototype.slice.call(nodeList);
  }

  function init() {
    var header = document.querySelector('[data-site-header]');

    initMobileNav(
      header,
      document.querySelector('[data-nav-toggle]'),
      document.querySelector('[data-site-nav]')
    );
    initHeaderScrollState(header, document.querySelector('[data-scroll-sentinel]'));
    initSectionHighlight(toArray(document.querySelectorAll('[data-site-nav] .site-nav__list a')));
    initRevealOnScroll(toArray(document.querySelectorAll('[data-reveal]')));
    initCurrentYear(document.querySelector('[data-current-year]'));
  }

  init();
})();
