# Japandi Dev

The personal website behind <https://japandi.dev>.

Japandi Dev is an **anonymous personal developer identity** — a place to share applications,
experiments and ideas made through code. It is not a company, an organization, an agency, a team or
a studio, and the site is written in the first person throughout.

It is a static site: semantic HTML5, one stylesheet, one small vanilla-JavaScript file. No
framework, no build step, no server-side runtime, no database, and **zero third-party requests at
runtime**. Deploying it means copying files into a document root.

The first featured project is **Squirio**, a personal finance tracker
("Track your money, not your stress"), which links out to <https://squirio.japandi.dev>.

---

## Table of contents

- [The anonymity requirement](#the-anonymity-requirement)
- [Folder structure](#folder-structure)
- [Local preview](#local-preview)
- [Deploying to Biznet Gio](#deploying-to-biznet-gio)
- [Automatic deploys from GitHub](#automatic-deploys-from-github)
- [Cloudflare](#cloudflare)
- [Connecting japandi.dev](#connecting-japandidev)
- [Clean URLs](#clean-urls)
- [Security headers](#security-headers)
- [Regenerating the CSP hash](#regenerating-the-csp-hash)
- [The logo](#the-logo)
- [Squirio artwork](#squirio-artwork)
- [Adding a project](#adding-a-project)
- [Opening the waitlist](#opening-the-waitlist)
- [The brand email](#the-brand-email)
- [Adding a brand GitHub account](#adding-a-brand-github-account)
- [Page metadata](#page-metadata)
- [Structured data](#structured-data)
- [The Open Graph image](#the-open-graph-image)
- [Design system](#design-system)
- [Documentation consulted](#documentation-consulted)
- [Test results](#test-results)
- [SEO checklist](#seo-checklist)
- [Accessibility checklist](#accessibility-checklist)
- [Privacy and anonymity checklist](#privacy-and-anonymity-checklist)
- [Manual accessibility testing](#manual-accessibility-testing)
- [Lighthouse testing](#lighthouse-testing)
- [Pre-launch checklist](#pre-launch-checklist)
- [Remaining placeholders](#remaining-placeholders)

---

## The anonymity requirement

Anonymity is a hard constraint, not a preference. Before publishing any change, make sure none of
the following has crept in:

- A real name, initials, photograph, age, gender, employer, job title, education or biography.
- An exact location. (The footer says "Built with clarity and care." precisely so it does not have
  to say where.)
- Personal social accounts. The site links to no social profile at all.
- A personal email address. Only a brand address is used.
- Identifying data inside **image metadata** — see [The logo](#the-logo).
- Identifying data inside code comments, JSON-LD, meta tags, or file and folder names.

There is no `Person` and no `Organization` structured data anywhere, deliberately: one would invent
a person, the other would misrepresent this as a company. See
[Structured data](#structured-data).

A scan you can re-run any time:

```bash
grep -rniE "your-name|your-initials|@gmail|@yahoo|linkedin|instagram|facebook|whatsapp" \
  --include="*.html" --include="*.css" --include="*.js" --include="*.md" --include="*.svg" .
```

---

## Folder structure

```text
japandi-dev/
├── index.html                              Single-page personal site
├── privacy.html                            Privacy policy (placeholder text)
├── 404.html                                Custom error page (root-relative paths)
├── robots.txt
├── sitemap.xml
├── .htaccess                               404 routing, security headers, caching
├── README.md
└── assets/
    ├── css/
    │   └── styles.css                      All styles, token-driven
    ├── js/
    │   └── script.js                       Progressive enhancement only
    ├── fonts/
    │   ├── fraunces-latin-var.woff2        Display serif  (67 KB)
    │   └── karla-latin-var.woff2           Body sans      (24 KB)
    └── images/
        ├── japandi-dev-logo.png            MASTER — the supplied logo, metadata stripped
        ├── japandi-dev-logo-192.png        Display/icon derivative (2x)
        ├── japandi-dev-logo-96.png         Display derivative (1x)
        ├── favicon-32.png
        ├── apple-touch-icon.png            180 × 180
        ├── og-image.png                    1200 × 630 social share card
        ├── og-image-placeholder.svg        Editable layout template for the above
        ├── squirio-icon-placeholder.svg    PLACEHOLDER
        └── squirio-screenshot-placeholder.svg  PLACEHOLDER
```

### Two deliberate departures from the suggested file list

1. **There is no `favicon-placeholder.svg`.** The brief says to use the logo as the favicon *if* it
   contains a suitable standalone symbol, and to create a placeholder otherwise. It does contain one
   — a self-contained circular badge — so real favicons are generated from it, and shipping an
   unused placeholder would only be dead weight. If you would rather have the file present anyway,
   say so and it can be added.
2. **`.htaccess` was added.** Without `ErrorDocument 404 /404.html` the host serves its own generic
   error page and `404.html` is never reached. It also carries the security headers and the
   clean-URL rules described under [Clean URLs](#clean-urls).

---

## Local preview

No build step and no dependencies. Serve the folder over HTTP — opening `index.html` via `file://`
breaks the root-relative paths in `404.html` and can block font loading. Note that `.htaccess` is
not read by either server below, so the extensionless links resolve only under `serve`, which
happens to apply the same rule; under `python -m http.server` a link to `/privacy` will 404.

```bash
# Python 3
python -m http.server 8765

# or Node
npx --yes serve .
```

Then open <http://127.0.0.1:8765/>.

Note that a plain local server does **not** send the headers from `.htaccess`, so the CSP is not
exercised locally by default. See [Security headers](#security-headers) for how it was verified.

---

## Deploying to Biznet Gio

Biznet Gio NEO Web Hosting is cPanel-based and runs LiteSpeed, which reads `.htaccess` the same way
Apache does.

1. **Log in to cPanel** from your Biznet Gio portal (usually `https://<your-server>:2083`).
2. **Open File Manager** and go to the document root for the domain — `public_html` for a primary
   domain, or `public_html/japandi.dev` if you added it as an addon domain.
3. **Upload the contents of this folder, not the folder itself.** `index.html` must sit directly in
   the document root. The simplest route is to zip the project contents locally, upload the zip, and
   use cPanel's *Extract*.
4. **Confirm `.htaccess` uploaded.** It is a dotfile, so enable *Settings → Show Hidden Files* in
   File Manager. Without it there is no custom 404 and no security headers.
5. **Check permissions** — `644` for files, `755` for directories. cPanel usually gets this right.

SFTP works equally well; upload to the same document root.

---

## Automatic deploys from GitHub

The repository lives at `github.com/phlvireza/japandi-dev` and is **private** — deliberately. The
site claims an anonymous identity, and a public repository under a personal handle would tie that
handle to `japandi.dev` no matter what the site itself says. Commits are authored as
`japandi-dev <hello@japandi.dev>` for the same reason. Keep both when you add collaborators or
mirror the repo.

`.github/workflows/deploy.yml` syncs the working tree to the document root over FTPS on every push
to `main`. The action keeps a state file in the document root and uploads only changed files, so a
routine deploy moves kilobytes, not the whole bundle.

### One-time setup

Add four repository secrets under **Settings → Secrets and variables → Actions**:

| Secret | Where to find it | Value |
|---|---|---|
| `FTP_SERVER` | the hosting server's own hostname | `web6-cpn.neohosting.id` |
| `FTP_USERNAME` | cPanel → FTP Accounts, the **full** username including `@japandi.dev` | `deploy@japandi.dev` |
| `FTP_PASSWORD` | the password you set when creating that account | |
| `FTP_SERVER_DIR` | see below — depends on how the FTP account is scoped | `./` |

**`FTP_SERVER` must be the server hostname, not `ftp.japandi.dev`.** `japandi.dev` is proxied
through Cloudflare, and Cloudflare proxies HTTP only — it has no FTP listener, so a proxied record
sends the deploy to an edge that cannot answer it. `web6-cpn.neohosting.id` bypasses Cloudflare
entirely, which is what an origin-side deploy wants. It is also the hostname on the certificate
Pure-FTPd presents, which is why the workflow can run `security: strict`; a bare IP or any other
name would fail the handshake.

Verified against the live server: port 21 answers `220 Welcome to Pure-FTPd [privsep] [TLS]`, so
explicit FTPS on port 21 is the correct protocol. Port 990 (implicit FTPS, `ftps-legacy`) is
closed — do not use it.

Create a dedicated FTP account in cPanel rather than reusing the main cPanel login. Scope its
**Directory** to the document root, so a leaked secret cannot reach the rest of the account.

`FTP_SERVER_DIR` is then relative to **wherever that account lands after login**, not an absolute
path — and the two settings interact:

| FTP account | Lands in | `FTP_SERVER_DIR` |
|---|---|---|
| Sub-account, Directory scoped to `public_html` | inside `public_html` | `./` |
| Main cPanel account, unscoped | `/home/<user>` | `public_html/` |

Scoping the account *and* writing `public_html/` here gives `public_html/public_html/`. Either way,
drop the `/home/<user>` prefix that cPanel shows under Domains → Document Root, and keep the
trailing slash.

This is the most expensive of the four to get wrong, because it fails silently: the files upload
successfully to a folder the domain does not point at, and the symptom — a directory listing or the
host's placeholder — looks identical to not having deployed at all. **Run once with `dry-run: true`
and read the paths in the Actions log before the first real deploy.**

### Verifying a deploy

Run it once with `dry-run: true` added under `with:` before trusting it against the live document
root. The Actions log then lists what *would* change without touching the server.

After a real deploy, purge the Cloudflare cache — the origin has new files but the edge may still
answer from the old ones.

### What is not uploaded

`exclude` in the workflow drops `.git*`, `node_modules`, `README.md` and `.gitattributes`.
`.htaccess` is deliberately **not** excluded: without it there is no 404 page, no security headers
and no clean URLs. `.ftp-deploy-sync-state.json`, which the action writes into the document root, is
denied in `.htaccess` — it lists every file and its hash, which is a free map of the site.

---

### Enable HTTPS

In cPanel go to **Security → SSL/TLS Status** and run **AutoSSL** (Let's Encrypt) for `japandi.dev`
and `www.japandi.dev`. Wait until the certificate is issued and `https://japandi.dev` loads cleanly.

**Only then** open `.htaccess` and uncomment the `mod_rewrite` block that forces HTTPS and the bare
domain. Enabling it earlier redirects visitors to a URL the server cannot yet serve. `.dev` is on
the HSTS preload list, so **`.dev` domains only work over HTTPS at all** — get the certificate
issued before announcing anything.

---

## Cloudflare

The site is a plain static bundle with no server runtime and no provider-specific APIs, so it sits
behind Cloudflare's proxy without modification. Recommended settings:

| Setting | Where | Value |
|---|---|---|
| Proxy status | DNS → your A records | **Proxied** (orange cloud) |
| SSL/TLS mode | SSL/TLS → Overview | **Full (strict)** |
| Always Use HTTPS | SSL/TLS → Edge Certificates | On |
| Brotli | Speed → Optimization | On |
| Auto Minify | Speed → Optimization | Off — the files are already small and minifying can break the CSP hash |
| Web Analytics | Analytics & Logs → Web Analytics | **Off** — injects a script the CSP blocks, and contradicts the privacy page |
| Browser Insights | Speed → Optimization | **Off** — the same script under a different name |

**Full (strict) matters.** *Flexible* would make Cloudflare talk to your origin over plain HTTP
while showing visitors a padlock, which is worse than no TLS at all. Issue the origin certificate
via cPanel AutoSSL first, then set Full (strict).

**Do not enable Cloudflare's Auto Minify for HTML.** It rewrites inline scripts, which changes the
bytes the CSP hash covers, and the inline snippet would then be blocked — silently disabling the
mobile menu.

**Do not enable Cloudflare Web Analytics or Browser Insights.** Both make Cloudflare append its
own tag to every HTML response as it passes through the proxy:

```html
<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v…" data-cf-beacon='…'></script>
```

The origin has already sent the CSP header by the time that injection happens, and Cloudflare does
not rewrite the header to match, so the browser blocks the script it was just handed. The console
error is unmistakable:

```
loading the script 'https://static.cloudflareinsights.com/beacon.min.js/v…' violates the
following Content Security Policy directive: "script-src 'self' 'sha256-…'"
```

Nothing in this repository loads that script — if you see it, the toggle is on at the zone. Turn it
off under **Analytics & Logs → Web Analytics** (remove the site) and **Speed → Optimization**
(Browser Insights), then purge the cache; HTML has a one-hour edge TTL, so cached copies keep the
injected tag until you do. Note that the rest of the site is unaffected: the hashed inline snippet
still runs, and the mobile menu still works.

Beyond the console noise, the tag is a promise broken. `privacy.html` tells visitors this site
"includes no analytics, no advertising, no tracking", and the beacon is all three.

*If you ever do decide to run Web Analytics*, two directives have to change, not one — the beacon
also reports to `https://cloudflareinsights.com/cdn-cgi/rum`, which `connect-src 'none'` blocks:

```
script-src 'self' 'sha256-…' https://static.cloudflareinsights.com;
connect-src https://cloudflareinsights.com;
```

Update `privacy.html` in the same change, or the page will be lying to its readers.

**Headers.** `.htaccess` already sets them at the origin and Cloudflare passes them through. If you
would rather manage them at the edge, use **Rules → Transform Rules → Modify Response Header** and
remove the `<IfModule mod_headers.c>` block from `.htaccess` so they are not set twice. If you turn
on Cloudflare's HSTS (SSL/TLS → Edge Certificates), leave the HSTS line in `.htaccess` commented —
sending it from both places is redundant and easy to get inconsistent.

**Caching.** The `Expires` rules in `.htaccess` give CSS, JS, fonts and images a one-year TTL and
HTML one hour. After deploying a change, **purge the Cloudflare cache** (Caching → Configuration →
Purge Everything) or the old CSS may persist at the edge.

---

## Connecting japandi.dev

1. Find your hosting IP in cPanel (*Shared IP Address* in the right sidebar).
2. At your registrar, either point nameservers at Cloudflare (if using it) or at Biznet Gio's
   nameservers, or keep your registrar's DNS and create:

   | Type | Name  | Value           |
   |------|-------|-----------------|
   | A    | `@`   | your hosting IP |
   | A    | `www` | your hosting IP |

3. Wait for propagation (minutes to a few hours). Verify with `nslookup japandi.dev`.
4. Issue the certificate, then enable the redirect block in `.htaccess`.

### Later: the Squirio subdomain

When Squirio is ready, add `squirio.japandi.dev` in cPanel (**Domains → Create A New Domain**),
which creates the DNS record and a document root for it. If Cloudflare is in front, add a matching
proxied A record there too. The "Discover Squirio" button already points there, so nothing in this
repository needs to change.

---

## Clean URLs

Pages are served without the `.html` suffix: `/privacy`, not `/privacy.html`. Three rules in
`.htaccess` do this, and they only work together:

1. A **301 redirect** sends anyone who asks for `/privacy.html` to `/privacy`, and `/index.html`
   to `/`. This matches `THE_REQUEST` — the literal request line the browser sent — so it fires
   only for real requests and never for the internal rewrite below.
2. A **trailing-slash redirect** sends `/privacy/` to `/privacy`. This one is not cosmetic:
   `index.html` and `privacy.html` link their assets with *relative* paths, so a page served at
   `/privacy/` would resolve them against `/privacy/assets/...` and every image would break.
3. An **internal rewrite** serves `/privacy` from `privacy.html`, guarded by a `-f` test so it
   only applies when the file exists. Nothing moves on disk; the files keep their `.html` names.

Consequences worth knowing:

- Every internal link, canonical URL, `og:url`, JSON-LD `url`/`@id` and `sitemap.xml` entry uses
  the extensionless form. If you add a page, link it as `/newpage`, never `/newpage.html`.
- The redirect is permanent and browsers cache it hard. That is what you want in production, but
  it means a mistake here is slow to undo.
- `mod_rewrite` is required. LiteSpeed on Biznet Gio supports it; if the host ignores `.htaccess`
  entirely the site still works, just with `.html` back in the address bar.
- **Local preview:** `python -m http.server` does not read `.htaccess`, so `/privacy` returns 404
  there. Use `npx --yes serve .`, which resolves extensionless paths the same way, if you want the
  preview to match production.

---

## Security headers

Set in `.htaccess` and **verified working** — the site was served locally with these exact headers
and the browser console reported zero violations, with fonts, styles and both scripts all loading.

| Header | Value | Why |
|---|---|---|
| `Content-Security-Policy` | see below | The site loads only its own assets |
| `X-Content-Type-Options` | `nosniff` | Stops MIME-type guessing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits what leaks in the Referer header |
| `Cross-Origin-Opener-Policy` | `same-origin` | Isolates the browsing context |
| `Permissions-Policy` | all features `()` | The site uses no camera, mic, geolocation or sensors |
| `Strict-Transport-Security` | **commented out** | Enable only once HTTPS is confirmed |

The policy:

```
default-src 'self'; script-src 'self' 'sha256-XHOQ0kIsWBoBByPYfUPSgQSssYKkXPWpDVfHvX+ryM8=';
style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; base-uri 'none';
form-action 'none'; frame-ancestors 'none'; object-src 'none'; upgrade-insecure-requests
```

**HSTS is deliberately left commented.** Browsers cache it for `max-age` seconds and it cannot be
withdrawn quickly; enabling it while HTTPS is misconfigured makes the site unreachable for a year.
Turn it on after `https://japandi.dev` is confirmed working.

Other security properties of the build: the one outbound link carries `rel="noopener noreferrer"`;
JavaScript writes text with `textContent` and never uses `innerHTML`, so no markup is ever parsed
from a string; there are no secrets, keys, analytics, trackers or third-party embeds; and there is
no cookie banner because the site sets no cookies.

That last point is true of what this repository ships, but it can be undone from outside it:
Cloudflare's Web Analytics injects a tracking beacon at the edge that no file here can see. See
**Cloudflare** above — keep it off.

## Regenerating the CSP hash

There is exactly one inline `<script>` on the site, repeated identically in all three pages. It sets
a `js` class so the collapsed navigation does not flash, and removes it again if `script.js` never
ran, so a failed download falls back to the no-JavaScript layout.

It is an inline **block** rather than an `onerror` **attribute** on purpose: a block can be
authorised by a `sha256` hash, whereas an inline event attribute would require `'unsafe-hashes'`,
which weakens the policy for every script on the page.

**If you edit those lines by even one character, the hash changes and the script stops running** —
which silently disables the mobile menu. Regenerate it:

```bash
python - <<'PY'
import re, io, hashlib, base64
html = re.sub(r'<!--.*?-->', '', io.open('index.html', encoding='utf-8').read(), flags=re.S)
body = re.search(r'<script>(.*?)</script>', html, re.S).group(1)
print("sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode())
PY
```

Paste the result into the `script-src` directive in `.htaccess`. Keep the snippet byte-identical
across all three pages, or each will need its own hash.

---

## The logo

`assets/images/japandi-dev-logo.png` is the supplied logo. It is never cropped, stretched, rotated,
recoloured, masked or filtered anywhere on the site.

| Property | Value |
|---|---|
| Dimensions | 1254 × 1254 |
| Pixel format | 24-bit RGB — **no alpha channel** |
| Background | Flat cream `#F3E8D1` |
| Brand green | `#4C6956` |
| Mark size | 976 × 1010 — about 78% of the canvas |

**The logo has no transparency.** That single fact drives the header, footer and share-card design.
Because it cannot sit invisibly on an arbitrary background, it is always rendered inside a
`.brand-mark` tile filled with its own `#F3E8D1`. The rounded corner is on **the tile**; the image
keeps its own square corners, and the tile's padding is sized so those corners stay inside the
rounded silhouette. Nothing is clipped. Do not add `border-radius`, `clip-path` or
`overflow: hidden` to the `<img>` itself.

### Metadata that was removed

The supplied file carried a **24,910-byte `caBX` chunk** — a C2PA provenance manifest containing a
generation UUID (`urn:c2pa:…`), an instance ID (`xmp:iid:…`), the generating software's name and
version, timestamps and certificate data. Those are persistent unique identifiers, so under the
anonymity requirement they were stripped.

Only that chunk was removed. `IHDR`, every `IDAT` and `IEND` were copied through untouched, and this
was **verified**: the `IHDR` and the concatenated `IDAT` streams are byte-identical before and
after, all chunk CRCs validate, and the image decompresses to exactly the expected
`1254 × (1 + 1254 × 3)` bytes. **Not one pixel changed.** The file went from 1,444,179 to 1,419,257
bytes.

### One limitation you should know about

The removed manifest declared `c2pa.watermarked.unbound`, which indicates an **invisible watermark
embedded in the pixel data itself**. Stripping metadata does not remove that, and removing it would
mean altering the logo's pixels, which the brief forbids. If that matters to you, the fix is to
obtain a logo from a source that does not watermark — ideally a vector original, which would also
let you drop the tile background entirely.

The generated derivatives (96, 192, 180 and 32 px, and the OG image) were produced by re-encoding
and carry no metadata beyond `sRGB`, `gAMA` and `pHYs` colour/density chunks. Verify at any time:

```bash
python - <<'PY'
import struct, glob
for p in sorted(glob.glob('assets/images/*.png')):
    d = open(p,'rb').read(); i = 8; chunks = []
    while i < len(d):
        ln = struct.unpack('>I', d[i:i+4])[0]; t = d[i+4:i+8].decode('latin-1')
        if t != 'IDAT': chunks.append(t)
        i += 12 + ln
        if t == 'IEND': break
    print("%-44s %s" % (p, ' '.join(chunks)))
PY
```

### Replacing the logo

1. Overwrite `assets/images/japandi-dev-logo.png`.
2. Regenerate the derivatives at 96, 192, 180 and 32 px, keeping the same filenames. Scale the
   **whole canvas** uniformly — never crop.
3. If the new background colour differs, update `--logo-field` in `assets/css/styles.css` to match
   exactly, or set it to `transparent` if the new file has an alpha channel.
4. Strip metadata from whatever you add, and regenerate `og-image.png`.

### Alternative text

In the header and footer the logo carries `alt=""`. That is deliberate: the visible text "Japandi
Dev" sits immediately beside it inside the same link, so a non-empty `alt` would make a screen
reader announce the name twice. If you ever use the logo as a link *without* adjacent text, give it
`alt="Japandi Dev"`.

---

## Squirio artwork

Two files are placeholders, visibly marked as such (dashed terracotta borders, and the words
"Screenshot placeholder" on the larger one) so they cannot be mistaken for final artwork.

**App icon** — replace `assets/images/squirio-icon-placeholder.svg`, referenced once in `index.html`:

```html
<img class="product__icon" src="assets/images/squirio-icon-placeholder.svg"
     width="64" height="64" alt="" decoding="async">
```

Rename to `squirio-icon.png` (or `.svg`) and update the `src`. Keep `width="64" height="64"` so the
layout cannot shift. `alt=""` is correct — the heading "Squirio" beside it already names it.

**Screenshot** — replace `assets/images/squirio-screenshot-placeholder.svg`:

```html
<img src="assets/images/squirio-screenshot-placeholder.svg"
     width="440" height="560" loading="lazy" decoding="async"
     alt="Placeholder image standing in for a screenshot of the Squirio app.">
```

Set `width` and `height` to the real pixel dimensions — they must match the file's true aspect ratio
or the image distorts. Keep `loading="lazy"`. Write a real `alt` describing what the screen shows,
for example *"The Squirio dashboard, showing a monthly balance and spending by category."*
**Check screenshots for identifying content** before publishing — real account numbers, names or
locations in a demo screen would undo the anonymity everywhere else.

---

## Adding a project

Project cards are plain HTML on purpose — no CMS, no config file, no rendering layer.

In `index.html`, find the comment `FEATURED PROJECT CARD`, copy the whole `<article class="product">`
block, paste it below, and edit the text. Then:

- Change `aria-labelledby="squirio-name"` and the matching `id` on the `<h3>` to something unique.
- Update the icon `src`, the links, and the status pill.
- If the project has shipped, reword or delete the `<p class="pill">`.

No CSS or JavaScript changes are needed. If you add a second card, wrap them in a
`<div class="projects">` and give that class a grid — or let them stack, which already works.

Once a project has its own page, add it to `sitemap.xml`.

---

## Opening the waitlist

There is no waitlist provider yet, so the site does not pretend there is one. The control is a real
disabled button with a visible explanation beside it, rather than a link pointing nowhere:

```html
<button class="button button--ghost" type="button" disabled aria-describedby="waitlist-note">Join the Waitlist</button>
<p class="product__note" id="waitlist-note">The waitlist is not open yet. It opens closer to launch.</p>
```

When you have a provider, swap the button for an anchor with the same classes and delete the note:

```html
<a class="button button--ghost" href="https://your-waitlist-url" rel="noopener noreferrer">Join the Waitlist</a>
```

Remove the `aria-describedby` attribute along with the note paragraph it points at. If the provider
embeds a form, remember it becomes a third party: update the privacy policy, and add its origin to
the CSP or the form will be blocked.

---

## The brand email

`hello@japandi.dev` is a **placeholder**. Create the mailbox before launch or replace it. Use a
brand address only — never a personal one, and never one built from a real name.

It appears in `index.html` (the Get in Touch button, the contact list and the footer),
`privacy.html` (the Questions section and the footer) and `404.html` (the footer). Find them all:

```bash
grep -rn "hello@japandi.dev" *.html
```

It is deliberately **not** in the structured data, because the WebSite and WebPage types have no
appropriate property for it.

## Adding a brand GitHub account

No GitHub link ships, because linking an account that carries commit history, an email address or a
real name would defeat the anonymity requirement in one click. Add one only when you have a
dedicated account with no identifying information.

When you do, add it to the contact list in `index.html`:

```html
<li>
  <span class="contact__label">GitHub</span>
  <a href="https://github.com/YOUR-BRAND-ACCOUNT" rel="noopener noreferrer">github.com/YOUR-BRAND-ACCOUNT</a>
</li>
```

and to the "More" column of the footer on all three pages. Before publishing it, check the account's
public profile, its commit author names and emails, and any pinned repositories — commit metadata is
the most common way an anonymous account stops being anonymous.

Structured data still should not gain a `sameAs`: that property belongs to `Organization` and
`Person`, neither of which this site declares.

---

## Page metadata

Each page carries its own title, description, canonical URL and Open Graph set. Keep them in
agreement when editing.

| Page | Title | Canonical |
|---|---|---|
| `index.html` | Japandi Dev — Coding with Simplicity and Purpose | `https://japandi.dev/` |
| `privacy.html` | Privacy — Japandi Dev | `https://japandi.dev/privacy` |
| `404.html` | Page Not Found — Japandi Dev | *(none — carries `noindex`)* |

Notes:

- Open Graph tags use `property=`; Twitter tags use `name=`. Not interchangeable.
- `og:locale` is `en_ID`. `<html lang="en">` stays `en` — the language is English regardless of
  country, and no location is stated anywhere in the content.
- `404.html` has **no** canonical, **no** structured data, and is **not** in `sitemap.xml`.
- No `author` meta tag, anywhere. It would name a person.
- If you add a page, add it to `sitemap.xml` and update `lastmod` (`YYYY-MM-DD`).

---

## Structured data

`index.html` carries one JSON-LD block with a **WebSite** and a **WebPage**, linked by `@id`.
`privacy.html` carries a **WebPage** whose `isPartOf` points back at the same WebSite.

Every property used was checked against the live schema.org vocabulary and is valid for its type.
What is deliberately absent, and why:

| Omitted | Reason |
|---|---|
| `Organization` | Japandi Dev is not a company. Declaring one would be false. |
| `Person` | Would require naming or describing a real individual. |
| `author`, `creator`, `publisher` | Each resolves to a Person or Organization. |
| `sameAs` | Belongs to Person/Organization, and there are no profiles to list. |
| `logo`, `email` | `Organization` properties — they have no home on `WebSite`. |
| `SearchAction` | There is no site search, so it would be untrue. |

Validate any change at <https://validator.schema.org/> and Google's
[Rich Results Test](https://search.google.com/test/rich-results). Note that neither WebSite nor
WebPage produces a rich result on its own — they are there to state the site's identity accurately,
not to win search decoration.

---

## The Open Graph image

`assets/images/og-image.png` (1200 × 630) is the card shown when the site is shared. It is generated
from the real logo plus the site's own typefaces and is ready to use.

`og-image-placeholder.svg` is the **editable layout template** — open it in a vector editor to art
direct a replacement. It marks where the logo sits.

**Always export to PNG or JPEG at 1200 × 630.** Social platforms do not render SVG previews, which is
why the meta tags point at the PNG and never the SVG.

Keep the filename and dimensions, and keep `og:image:width` / `og:image:height` in sync across all
pages. Update `og:image:alt` to describe the new artwork, and strip metadata from whatever you
export. Platforms cache aggressively — re-scrape after changing it.

---

## Design system

Everything visual is driven by custom properties at the top of `assets/css/styles.css`.

The palette is sampled from the logo rather than imposed on it. The suggested starting palette had a
cooler background (`#F8F5EF`), which made the logo tile read as a grey patch against the page, so
the neutrals were warmed to sit with the logo's `#F3E8D1` field.

| Token | Value | Role |
|---|---|---|
| `--bg` | `#F7F2E8` | Page background |
| `--surface` | `#FCFAF4` | Cards |
| `--surface-alt` | `#F2ECDE` | Alternating sections |
| `--logo-field` | `#F3E8D1` | Brand tile only — the logo's own background |
| `--ink` | `#2C2925` | Primary text |
| `--ink-soft` | `#6E6A60` | Secondary text |
| `--pine` | `#4C6956` | Brand green, from the logo |
| `--pine-deep` | `#38503F` | Hover states, footer background |
| `--terracotta` | `#B66A42` | Decorative accent |
| `--terracotta-ink` | `#A0552F` | Accent for text and small marks |
| `--sand` | `#E6DAC4` | Soft fills |
| `--line` | `#E0D5C0` | Decorative rules and card edges |
| `--line-strong` | `#94886F` | Boundaries of interactive controls |

### Dark theme

`:root` declares `color-scheme: light dark`, and a `@media (prefers-color-scheme: dark)`
block in section 2 re-points every token above. Declaring `color-scheme` is not cosmetic:
it is what stops Chrome on Android from force-inverting the site with Auto Dark Theme,
which is a light-only page's default fate and which used to make the header flash white
when the mobile menu opened.

| Token | Dark | Note |
|---|---|---|
| `--bg` | `#1B1917` | Warm near-black, never a cold blue-grey |
| `--surface` | `#2E2820` | Cards, raised 1.20:1 above `--bg` |
| `--surface-alt` | `#231F18` | Alternating sections |
| `--logo-field` | `#F3E8D1` | **Unchanged** — the logo's own ground |
| `--ink` | `#EDE6D8` | 14.12:1 on `--bg` |
| `--ink-soft` | `#B0A794` | 7.35:1 on `--bg` |
| `--pine` | `#8FB39A` | 7.58:1 on `--bg` |
| `--pine-deep` | `#A8C6B1` | Hover fill |
| `--pine-contrast` | `#16211A` | 7.17:1 on `--pine` |
| `--terracotta` | `#D08A5E` | 6.24:1 on `--bg` |
| `--terracotta-ink` | `#E0A177` | 7.96:1 on `--bg` |
| `--sand` | `#3E362A` | `--ink` on it is 9.58:1 |
| `--line` | `#35302A` | Decorative rules and card edges |
| `--line-strong` | `#8C8371` | 4.67:1 on `--bg` |
| `--footer-bg` | `#1F2B24` | Raised 1.19:1 above `--bg` |
| `--footer-ink` | `#EDE6D8` | 11.83:1 on `--footer-bg` |
| `--footer-ink-soft` | `#C2CFC4` | 9.11:1 on `--footer-bg` |
| `--footer-line` | `#35473A` | 1.48:1 on `--footer-bg` |

Three tokens invert their role, which reads as a mistake without the explanation:

- **`--pine` and `--pine-deep` get *lighter* than their light values.** The accent has to
  rise off a dark ground, so "deep" means a lighter hover, not a darker one.
- **`--pine-contrast` flips from cream to a near-black ink**, because it labels a button
  whose fill is now light.
- **`--footer-bg` becomes a *raised* plane.** Elevation runs lighter in dark UI, and there
  is no room below `--bg` to recede into without the footer reading as the page ending.

Two rules need more than a colour and live in section 10, after the rules they override:

- **The header brand tile comes back.** Section 5 strips it because the header uses the
  transparent logo PNG; on a dark ground ~70% of that mark is the logo's own dark pine,
  which measures 2.72:1 and reads as half erased. On the cream field it is 5.36:1. The
  logo itself is still never cropped, recoloured, masked or filtered.
- **The Squirio images keep their pixels** — dimming a product shot shows people an app
  that does not exist. Only the 1px frame moves to `--line-strong`, which is visible
  against both the dark card and the image's own cream.

Everything else re-themes from the tokens alone, including the inline SVG artwork (it
fills entirely from `var(--…)`) and the six `--product-*` aliases.

Both themes carry a `theme-color` meta, light first so a UA that ignores `media=` keeps
today's behaviour.

Two carry constraints worth respecting:

- **`--terracotta` is 3.63:1 on the page background.** Fine for large text, icons and borders; it
  fails the 4.5:1 requirement for body text. Use `--terracotta-ink` (4.82:1) for accent-coloured text.
- **`--line` and `--line-strong` are not interchangeable.** WCAG 2.2 SC 1.4.11 wants 3:1 on the
  boundaries of interactive controls but not on decorative rules. `--line-strong` exists for the
  first case; `--line` on a button border would be 1.3:1.

### Typography

Two self-hosted variable fonts, latin subset, so the site makes **zero third-party requests**:
**Fraunces** for display, **Karla** for body. Both preloaded, `font-display: swap`. Type scales with
`clamp()`, which is what lets the layout survive 320 px reflow and 200% zoom without extra
breakpoints.

### JavaScript

`assets/js/script.js` is one IIFE with a single `init()` wiring five independent functions: the
mobile navigation, the header's scrolled state, the current-section indicator, the reveal-on-scroll
animation and the footer year. No globals, no dependencies.

**It is enhancement only.** With scripting off, or if `script.js` fails to load, the navigation
renders open and stacked, every section is visible, the footer shows a hardcoded fallback year, and
the current-section indicator is simply absent. No page content is ever rendered by JavaScript.

The current-section indicator sets `aria-current="true"`, so the state is exposed to assistive
technology natively and is shown with a dot plus weight change, never colour alone.

---

## Documentation consulted

Researched through **Context7 MCP**:

| Source | Context7 ID | Used for |
|---|---|---|
| ARIA Authoring Practices Guide | `/w3c/wai-aria-practices` | Disclosure pattern for the mobile navigation |
| Google Search Central | `/websites/developers_google_search` | `rel="canonical"`, robots.txt, sitemap format |
| Google Search structured data | `/websites/developers_google_search_appearance_structured-data` | Structured-data property support |

Retrieved directly from the primary source where Context7 had no entry:

| Source | Used for |
|---|---|
| [W3C — What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) | The new AA criteria, and that 4.1.1 Parsing is obsolete |
| [The Open Graph protocol](https://ogp.me/) | Required properties and exact `property=` syntax |
| [web.dev — Core Web Vitals](https://web.dev/articles/vitals) | Current LCP / INP / CLS thresholds |
| [schema.org vocabulary](https://schema.org/version/latest/schemaorg-current-https.jsonld) | Machine-validating every JSON-LD property |

### Findings that changed the code

- **A nav toggle is a disclosure, not a modal.** The APG pattern uses `aria-expanded` +
  `aria-controls` with no focus trap. A trap would risk stranding keyboard users, so there isn't
  one; Escape closes and returns focus to the toggle.
- **SC 2.4.11 Focus Not Obscured (new in 2.2, AA).** A sticky header hides anchor targets when you
  tab or jump to them. Fixed with `scroll-padding-top` on `html` — the criterion most commonly
  missed on sticky-header sites.
- **SC 2.5.8 Target Size (new in 2.2, AA)** requires 24 × 24 CSS px. Targets here are 44–48 px.
- **SC 4.1.1 Parsing was removed in WCAG 2.2**, so duplicate-ID lint is no longer an accessibility
  criterion — though the HTML still validates cleanly.
- **FID was retired in favour of INP** (200 ms at p75).
- **A CSP `sha256` hash cannot authorise an inline event attribute** — only a `<script>` block. That
  is why the load-failure fallback lives inside the hashed block instead of an `onerror` attribute.

---

## Test results

Run against a local server. Automated results and manual review are reported **separately**, and
**automated testing does not prove WCAG conformance** — it catches a subset of issues. The manual
checks are also not a substitute for testing with real assistive technology and real users.

### Automated

| Check | Tool | Result |
|---|---|---|
| HTML validity | W3C Nu validator (API) | **0 errors, 0 warnings** on all three pages |
| Accessibility | axe-core 4.10.2, WCAG 2.0/2.1/2.2 A+AA + best-practice | **0 violations** on all three pages |
| Colour contrast | Custom script over every real foreground/background pair, **both themes** | **all pass** |
| Link integrity | Custom script | **0 broken** local references; 0 `href="#"`; outbound link carries `rel` |
| Structured data | Checked against the live schema.org vocabulary | **0 unsupported properties** |
| `sitemap.xml` | XML parse, namespace and `lastmod` format | Valid |
| `robots.txt` | Directive parse | Valid, absolute `Sitemap:` URL |
| CSP | Site served with the real headers | **0 violations**; inline script accepted by hash |
| Logo metadata strip | IHDR/IDAT byte comparison + CRC + decompression | **Pixel data byte-identical** |
| Identity leak scan | grep across every shipped file | No name, email, path, location or social profile |
| Unused code | Custom script | 0 unused CSS classes, 0 orphan custom properties |
| Lighthouse | Lighthouse 12.8.2 | See below |

### Manual, in Chromium

| Check | Result |
|---|---|
| Console errors | None on any page |
| Third-party requests | **Zero** |
| Keyboard: menu open → Escape | Closes, focus returns to the toggle |
| `aria-expanded` / `aria-controls` | Toggle correctly, target exists |
| Current-section indicator | Correct section for all five, never two at once |
| Reflow at 320 px | No horizontal scrolling, no overflowing elements |
| Reflow at 640 px (≈200% zoom of 1280) | No horizontal scrolling |
| Text spacing (SC 1.4.12 override) | No overflow, nothing clipped |
| Anchor offset under sticky header | Target headings clear the header |
| Touch targets | No interactive element under 24 × 24 |
| Heading structure | Exactly one `<h1>` per page, no skipped levels |
| JavaScript disabled | Nav open with all links, all sections visible, toggle hidden |

### Not tested

- No screen-reader testing (NVDA / JAWS / VoiceOver).
- No testing on real Safari, Firefox or physical mobile hardware — Chromium only.
- Field Core Web Vitals cannot be measured before launch; Lighthouse numbers are lab data.
- The `.htaccess` directives were exercised by replaying the same headers from a local server, not
  on LiteSpeed itself. Confirm them against the live site after deploying.

---

## SEO checklist

- [x] Unique, descriptive `<title>` per page
- [x] Unique meta description per page
- [x] Self-referencing canonical on indexable pages; none on `404.html`
- [x] `<meta name="viewport">` on every page
- [x] Complete Open Graph set (`property=`) incl. `og:image:width/height/alt` and `og:locale`
- [x] Twitter `summary_large_image` (`name=`)
- [x] Real 1200 × 630 share image
- [x] Favicon and apple-touch-icon
- [x] One `<h1>` per page, logical heading order
- [x] All content in crawlable HTML — nothing rendered by JavaScript
- [x] Descriptive link text (no "click here")
- [x] Descriptive image filenames and meaningful `alt`
- [x] Explicit `width`/`height` on every image
- [x] Valid `robots.txt` pointing at the sitemap
- [x] Valid `sitemap.xml` excluding the 404 page
- [x] Custom 404 with `noindex`, wired up via `.htaccess`
- [x] WebSite + WebPage JSON-LD, only supported properties
- [x] No keyword stuffing, hidden text, fake reviews or unnecessary `hreflang`
- [ ] Submit the sitemap in Google Search Console (after launch)

## Accessibility checklist

Target: **WCAG 2.2 Level AA**.

- [x] Skip link to main content
- [x] `header` / `nav` / `main` / `footer` landmarks, `aria-label` on both navs
- [x] One `<h1>`, no skipped heading levels
- [x] Native HTML preferred over ARIA throughout
- [x] `aria-expanded` and `aria-controls` on the menu button
- [x] Escape closes the menu and restores focus (SC 2.1.2 — no keyboard trap)
- [x] `aria-current` on the active nav link, with a non-colour cue
- [x] Visible `:focus-visible` indicator, 2 px + offset, ≥3:1 everywhere
- [x] No positive `tabindex`
- [x] 4.5:1 for body text, 3:1 for large text and control boundaries
- [x] Status conveyed by text *and* a dot, never colour alone
- [x] Decorative images `alt=""`; decorative SVG `aria-hidden="true" focusable="false"`
- [x] Interactive targets ≥24 × 24 CSS px (SC 2.5.8)
- [x] Anchor targets not obscured by the sticky header (SC 2.4.11)
- [x] Reflow at 320 px with no horizontal scrolling (SC 1.4.10)
- [x] Usable at 200% zoom (SC 1.4.4)
- [x] Survives the SC 1.4.12 text-spacing override
- [x] `prefers-reduced-motion` honoured in both CSS and JavaScript
- [x] No autoplaying animation, nothing flashing
- [x] `lang="en"` on every page
- [x] Content fully available without JavaScript
- [ ] Screen-reader pass with NVDA or VoiceOver — **still to do**

## Privacy and anonymity checklist

- [x] No real name, initials, photograph, age, gender, employer, job title or education
- [x] No exact location anywhere in content or metadata
- [x] No personal social profiles; no social links at all
- [x] No personal email — brand address only
- [x] No `Person` or `Organization` structured data
- [x] No `author` meta tag
- [x] No analytics, trackers, pixels, session recording or fingerprinting
- [x] No third-party embeds; zero external requests at runtime
- [x] No cookie banner, because no cookies are set
- [x] C2PA/EXIF metadata stripped from the master logo; derivatives carry none
- [x] No personal information in code comments, filenames or JSON-LD
- [x] No local filesystem paths anywhere in the deliverable
- [ ] Check the domain's public WHOIS record — enable registrar privacy if it exposes you
- [ ] Check MX/mail headers if you self-host `hello@japandi.dev`
- [ ] Review Squirio screenshots for identifying content before publishing
- [ ] Vet any brand GitHub account's commit author names and emails before linking it

Two things outside this repository that can undo all of the above: **domain WHOIS records** and
**email headers**. Both are worth checking before launch.

---

## Manual accessibility testing

Worth doing yourself; automated tools miss most of this.

**Keyboard only.** Unplug the mouse. From the top of the page press <kbd>Tab</kbd>:

1. First stop should be "Skip to main content", appearing at the top left.
2. <kbd>Enter</kbd> should move focus into the main content.
3. Every link and button should show a clear green focus ring.
4. Focus order should follow visual order, top to bottom.
5. Narrow the window below 992 px. <kbd>Tab</kbd> to "Menu", press <kbd>Enter</kbd>, check the links
   appear. Press <kbd>Escape</kbd> — the menu closes and focus returns to "Menu".
6. Confirm you can always <kbd>Tab</kbd> back out. Nothing should trap you.

**Zoom and reflow.** <kbd>Ctrl</kbd>+<kbd>+</kbd> to 200%, then 400%. Nothing cut off, no sideways
scrolling. Then narrow the window to 320 px and check again.

**Text spacing.** In DevTools, add this and confirm nothing overlaps or clips:

```css
* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; }
p { margin-bottom: 2em !important; }
```

**Reduced motion.** DevTools → *Rendering → Emulate CSS media feature prefers-reduced-motion:
reduce*. Reload. Sections appear instantly with no sliding.

**Without JavaScript.** DevTools → *Settings → Debugger → Disable JavaScript*, reload. The
navigation should be visible and stacked and every section readable.

**Screen reader.** NVDA on Windows, VoiceOver on macOS (<kbd>Cmd</kbd>+<kbd>F5</kbd>). Listen for:
the brand link announced once as "Japandi Dev", not twice; the menu button announcing its expanded
state; the current section announced as "current"; and the disabled waitlist button announcing as
unavailable with its explanation.

## Lighthouse testing

In Chrome DevTools open the **Lighthouse** panel, tick Performance / Accessibility / Best Practices
/ SEO, and run it. Or:

```bash
npx --yes lighthouse@12 https://japandi.dev/ \
  --only-categories=performance,accessibility,seo,best-practices --view
```

Test the **deployed** site, not the local server — compression, caching and TLS all affect the
result. Run mobile as well as desktop; mobile is throttled and much stricter.

A perfect score is not the goal. Real usability, accessibility, privacy and correctness matter more,
and a 100 does not mean the site is accessible.

---

## Pre-launch checklist

- [ ] Create `hello@japandi.dev`, or replace it everywhere
- [ ] Replace the Squirio icon and screenshot placeholders
- [ ] Write the real privacy policy and delete the placeholder notice
- [ ] Decide on the waitlist provider and swap in a real link
- [ ] Confirm `.htaccess` uploaded (show hidden files in File Manager)
- [ ] Run AutoSSL and confirm `https://japandi.dev` loads
- [ ] Enable the HTTPS / bare-domain redirect block in `.htaccess`
- [ ] Verify the security headers on the live site (`curl -I https://japandi.dev/`)
- [ ] Enable HSTS only after HTTPS is confirmed
- [ ] If using Cloudflare: SSL/TLS **Full (strict)**, Auto Minify **off**, Web Analytics **off**, purge cache
- [ ] Confirm `/privacy` loads, and that `/privacy.html` and `/privacy/` both 301 to it
- [ ] Visit a nonsense URL and confirm `404.html` is served
- [ ] Check `/robots.txt` and `/sitemap.xml` load
- [ ] Update `lastmod` in `sitemap.xml` to the launch date
- [ ] Run the Rich Results Test on the live URL
- [ ] Preview the share card in a social debugger
- [ ] Run Lighthouse against the live site, mobile and desktop
- [ ] Do the keyboard and screen-reader passes above
- [ ] Enable registrar WHOIS privacy for `japandi.dev`
- [ ] Set up Google Search Console and submit the sitemap

---

## Remaining placeholders

Each is marked in the source with a `PLACEHOLDER` comment — `grep -rn "PLACEHOLDER" *.html` lists
them all.

| # | Placeholder | Current value | Where |
|---|---|---|---|
| 1 | Brand email | `hello@japandi.dev` | all three pages |
| 2 | Waitlist destination | disabled button + explanatory note | `index.html` |
| 3 | Brand GitHub | omitted entirely | — |
| 4 | Squirio app icon | `squirio-icon-placeholder.svg` | `index.html` |
| 5 | Squirio screenshot | `squirio-screenshot-placeholder.svg` | `index.html` |
| 6 | Privacy policy text | marked placeholder, needs review | `privacy.html` |
| 7 | Open Graph image | generated and launch-ready; replace for custom art | `og-image.png` |

Not placeholders, but worth checking before launch: `https://squirio.japandi.dev` does not resolve
yet, and the technology list in the About section should say what you actually build with.

---

Built with clarity and care.
