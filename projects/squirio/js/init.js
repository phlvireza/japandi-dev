/* Enable JavaScript-enhanced presentation before styles paint. */
document.documentElement.classList.remove('no-js');

/* Sends a returning visitor to the language they last chose, before anything
   paints. The alternates are read from the hreflang links already in <head>,
   so there is no second copy of those URLs to keep in step. A page with no
   hreflang - 404, which is noindex - simply never redirects.

   The click that stores the value is in /assets/js/shell.js; it writes before
   navigating, so the stored language always matches the page being opened and
   this can never bounce a visitor back and forth. */
(function () {
  try {
    var stored = localStorage.getItem('japandi-lang');
    /* Checked against the published locales rather than trusted: the value is
       about to be interpolated into an attribute selector. */
    if (stored !== 'en' && stored !== 'id') return;
    if (stored === document.documentElement.lang) return;
    /* Only ever redirect away from the x-default page. A URL that names a
       locale was asked for deliberately - a shared link, a search result - and
       honouring the stored preference there would break every Indonesian link
       for anyone who once clicked EN. */
    var xdefault = document.querySelector('link[rel="alternate"][hreflang="x-default"]');
    if (!xdefault || new URL(xdefault.href).pathname !== location.pathname) return;
    var alt = document.querySelector('link[rel="alternate"][hreflang="' + stored + '"]');
    /* Only the path is taken from the alternate. Its href is absolute, as
       hreflang requires, and following it verbatim would send a visitor on a
       staging or local origin over to production. replace() rather than
       assign() so the back button does not land them on the page they were
       just redirected away from. */
    if (alt) location.replace(new URL(alt.href).pathname);
  } catch (error) {
    /* localStorage throws in private mode and when site data is blocked.
       Staying on the requested page is the right fallback. */
  }
})();
