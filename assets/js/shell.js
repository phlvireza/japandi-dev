/* ==========================================================================
   Japandi Dev — shell.js

   The four behaviours every page's header needs: the small-screen menu, the
   scrolled state, the current-section marker, and the MediaQueryList fallback
   they all depend on. The homepage and the project pages used to carry their
   own copy of each; they now pass their own selectors to init() instead.

   Progressive enhancement only. Every link is reachable without this file, so
   anything that cannot be observed is left in its resting state rather than
   hidden. No globals beyond window.JapandiShell, no dependencies.
   ========================================================================== */

window.JapandiShell = (function () {
  'use strict';

  /** Safari below 14 exposes addListener but not addEventListener on MediaQueryList. */
  function addMediaListener(mediaQuery, handler) {
    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handler);
      return;
    }
    mediaQuery.addListener(handler);
  }

  /**
   * Small-screen navigation, built as an ARIA disclosure rather than a modal:
   * no focus trap, so there is no way to strand keyboard users inside it.
   */
  function initMobileNav(header, toggle, nav, openClass, desktopQuery) {
    if (!header || !toggle || !nav) return;

    function isOpen() {
      return header.classList.contains(openClass);
    }

    function setOpen(open) {
      header.classList.toggle(openClass, open);
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
    addMediaListener(window.matchMedia(desktopQuery), function (event) {
      if (event.matches) close(false);
    });
  }

  /**
   * Adds a scrolled state to the header. With a sentinel element an observer
   * does the work off the scroll thread; without one — the project pages have
   * no sentinel to spare — a passive scroll listener reads scrollY directly.
   */
  function initHeaderScrollState(header, sentinel, scrolledClass) {
    if (!header) return;

    if (sentinel && 'IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        header.classList.toggle(scrolledClass, !entries[0].isIntersecting);
      });
      observer.observe(sentinel);
      return;
    }

    var update = function () {
      header.classList.toggle(scrolledClass, window.scrollY > 8);
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  /**
   * Marks the nav link for the section currently in view with aria-current, so
   * the state is exposed natively rather than by styling alone. The value is
   * "location" — ARIA's token for the current item within a page — rather than
   * "page", which belongs to a link pointing at the page you are already on.
   * Links to other pages are skipped, so a static aria-current there survives.
   * Absent without JavaScript.
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
        if (section.id === current) link.setAttribute('aria-current', 'location');
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

  function toArray(nodeList) {
    return Array.prototype.slice.call(nodeList);
  }

  /**
   * config:
   *   header, nav, toggle   selectors for the three header parts
   *   links                 selector for the nav links to track (optional)
   *   sentinel              selector for a top-of-page sentinel (optional)
   *   openClass             class the header carries while the menu is open
   *   scrolledClass         class the header carries once the page is scrolled
   *   desktop               media query at which the nav stops collapsing
   */
  function init(config) {
    var header = document.querySelector(config.header);
    if (!header) return;

    initMobileNav(
      header,
      document.querySelector(config.toggle),
      document.querySelector(config.nav),
      config.openClass || 'is-nav-open',
      config.desktop
    );
    initHeaderScrollState(
      header,
      config.sentinel ? document.querySelector(config.sentinel) : null,
      config.scrolledClass || 'is-scrolled'
    );
    if (config.links) {
      initSectionHighlight(toArray(document.querySelectorAll(config.links)));
    }
  }

  return { init: init, addMediaListener: addMediaListener, toArray: toArray };
})();
