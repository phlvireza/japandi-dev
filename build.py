#!/usr/bin/env python3
"""Generate every localised static page on the site from _src/.

    python build.py [--check]

Reads each page's template plus one JSON file per locale and writes complete,
plain static HTML. There is no runtime dependency and nothing is rendered
client-side: what the build writes is exactly what the server sends.

Pass --check in CI to validate locale parity and confirm that every generated
HTML/CSS file is current without changing the working tree.

Run this after editing anything under a _src/ directory. Never hand-edit a
generated file - it is an output and the next build overwrites it. Every
generated file carries a banner saying so.

This used to live at projects/squirio/build.py and build one page in one
language. It now covers the root site as well, so both halves of japandi.dev
share one generator rather than one of them being hand-maintained HTML.
"""

import io
import html
import json
import os
import re
import sys
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))

# Every locale the site is published in. 'en' is the reference: it defines the
# set of keys every other locale must match, and it is what x-default points at.
LOCALES = ('en', 'id')

# One information source for Learn navigation, grouping, and contextual paths.
# Localized titles and summaries remain in learn.<locale>.json; the registry
# only owns relationships and stable identifiers.
SQUIRIO_LEARN_ARTICLES = (
    {'slug': 'personal-finance-app', 'topic': 'money_basics', 'featured': True,
     'card': 'personal', 'related': ('best-free-financial-tracker-apps', 'offline-finance-app', 'free-financial-tracker')},
    {'slug': 'how-to-track-daily-expenses', 'topic': 'financial_habits', 'featured': True,
     'card': 'tracking', 'related': ('how-to-create-a-monthly-budget', 'import-bank-transactions-csv', 'savings-goal-tracker')},
    {'slug': 'how-to-create-a-monthly-budget', 'topic': 'budgeting', 'featured': True,
     'card': 'budget', 'related': ('how-to-track-daily-expenses', 'savings-goal-tracker', 'debt-and-receivables-tracker')},
    {'slug': 'free-financial-tracker', 'topic': 'money_basics', 'featured': False,
     'card': 'free', 'related': ('best-free-financial-tracker-apps', 'financial-tracker-without-ads', 'offline-finance-app')},
    {'slug': 'best-free-financial-tracker-apps', 'topic': 'money_basics', 'featured': False,
     'card': 'best_free', 'related': ('personal-finance-app', 'free-financial-tracker', 'financial-tracker-without-ads')},
    {'slug': 'debt-and-receivables-tracker', 'topic': 'budgeting', 'featured': False,
     'card': 'debt', 'related': ('how-to-create-a-monthly-budget', 'how-to-track-daily-expenses', 'savings-goal-tracker')},
    {'slug': 'savings-goal-tracker', 'topic': 'saving', 'featured': False,
     'card': 'saving', 'related': ('how-to-create-a-monthly-budget', 'how-to-track-daily-expenses', 'debt-and-receivables-tracker')},
    {'slug': 'backup-and-restore-financial-data', 'topic': 'financial_habits', 'featured': False,
     'card': 'backup', 'related': ('import-bank-transactions-csv', 'offline-financial-tracker-security', 'offline-finance-app')},
    {'slug': 'offline-finance-app', 'topic': 'privacy_data', 'featured': False,
     'card': 'offline', 'related': ('offline-financial-tracker-security', 'backup-and-restore-financial-data', 'financial-tracker-without-ads')},
    {'slug': 'financial-tracker-without-ads', 'topic': 'privacy_data', 'featured': False,
     'card': 'no_ads', 'related': ('offline-finance-app', 'offline-financial-tracker-security', 'free-financial-tracker')},
    {'slug': 'offline-financial-tracker-security', 'topic': 'privacy_data', 'featured': False,
     'card': 'security', 'related': ('offline-finance-app', 'backup-and-restore-financial-data', 'financial-tracker-without-ads')},
    {'slug': 'import-bank-transactions-csv', 'topic': 'privacy_data', 'featured': False,
     'card': 'csv', 'related': ('how-to-track-daily-expenses', 'backup-and-restore-financial-data', 'offline-financial-tracker-security')},
)

LEARN_BY_SLUG = {article['slug']: article for article in SQUIRIO_LEARN_ARTICLES}
LEARN_TOPICS = ('money_basics', 'budgeting', 'saving', 'financial_habits', 'privacy_data')

# Keep CSS maintainable by responsibility, then emit one render-blocking file
# per Squirio template family. This preserves modular sources without making a
# mobile browser pay several request round trips before its first paint.
SQUIRIO_CSS_BUNDLES = {
    'projects/squirio/css/landing.bundle.css': (
        'fonts.css', 'tokens.css', 'base.css', 'components.css',
        'mockups.css', 'japandi-shell.css'),
    'projects/squirio/css/learn.bundle.css': (
        'fonts.css', 'tokens.css', 'base.css', 'components.css',
        'japandi-shell.css', 'content.css'),
    'projects/squirio/css/privacy.bundle.css': (
        'fonts.css', 'tokens.css', 'base.css', 'japandi-shell.css',
        'privacy.css'),
}


def squirio_learn_article(article):
    """Return the shared build configuration for one bilingual article."""
    slug = article['slug']
    return {
        'src': 'projects/squirio/_src',
        'template': 'content.html',
        'strings': '%s.{locale}.json' % slug,
        'shared_strings': 'content-ui.{locale}.json',
        'fragments': {'body': '%s.{locale}.body.html' % slug},
        'out': {
            'en': 'projects/squirio/en/learn/%s/index.html' % slug,
            'id': 'projects/squirio/id/learn/%s/index.html' % slug,
        },
        'learn_slug': slug,
    }


def card_markup(article, catalog, heading_level=3):
    """Render one localized card from the central registry and catalog."""
    prefix = article['card']
    values = {name: html.escape(str(catalog['%s_%s' % (prefix, name)]))
              for name in ('title', 'copy', 'time')}
    topic = html.escape(str(catalog['topic_%s' % article['topic']]))
    href = '%s%s/' % (catalog['learn_root'], article['slug'])
    return (
        '<a class="card guide-card" href="%s"><span class="eyebrow">%s</span>'
        '<h%d class="h3">%s</h%d><p>%s</p>'
        '<span class="guide-card__meta">%s</span></a>'
    ) % (html.escape(href, quote=True), topic, heading_level, values['title'],
         heading_level, values['copy'], values['time'])


def learn_sections(catalog):
    """Render Featured once, then the nine remaining articles by topic."""
    featured = ''.join(card_markup(item, catalog) for item in
                       SQUIRIO_LEARN_ARTICLES if item['featured'])
    groups = []
    for topic in LEARN_TOPICS:
        articles = [item for item in SQUIRIO_LEARN_ARTICLES
                    if item['topic'] == topic and not item['featured']]
        if not articles:
            continue
        group_id = topic.replace('_', '-')
        cards = ''.join(card_markup(item, catalog, 4) for item in articles)
        groups.append(
            '<section class="learn-topic" aria-labelledby="%s-heading">'
            '<div class="guide-group__head"><h3 class="h2" id="%s-heading">%s</h3>'
            '<p>%s</p></div><div class="guide-grid">%s</div></section>' % (
                group_id, group_id,
                html.escape(str(catalog['topic_%s' % topic])),
                html.escape(str(catalog['topic_%s_intro' % topic])), cards))
    return (
        '<section aria-labelledby="featured-heading"><div class="guide-group__head">'
        '<h2 class="h2" id="featured-heading">%s</h2><p>%s</p></div>'
        '<div class="guide-grid">%s</div></section>'
        '<section aria-labelledby="all-learning-heading"><div class="guide-group__head">'
        '<h2 class="h2" id="all-learning-heading">%s</h2><p>%s</p></div>'
        '<div class="learn-topics">%s</div></section>'
    ) % (html.escape(str(catalog['featured_heading'])),
         html.escape(str(catalog['featured_intro'])), featured,
         html.escape(str(catalog['all_learning_heading'])),
         html.escape(str(catalog['all_learning_intro'])), ''.join(groups))


def related_cards(slug, catalog):
    """Render the current article's three explicit learning-path successors."""
    related = LEARN_BY_SLUG[slug]['related']
    if slug in related or len(related) != len(set(related)):
        raise SystemExit('%s: invalid related-article mapping' % slug)
    return ''.join(card_markup(LEARN_BY_SLUG[item], catalog) for item in related)


# One entry per page.
#
#   src       directory holding the template and the locale JSON files
#   template  the template file inside src
#   strings   locale JSON filename pattern inside src; {locale} is substituted
#   out       output path per locale, relative to the repo root
#
# Root-site outputs mirror their public paths. Squirio additionally groups both
# locales into en/ and id/ on disk; its .htaccess serves en/ internally so the
# established English public URLs continue to omit a locale segment.
PAGES = (
    {
        'src': '_src',
        'template': 'index.html',
        'strings': 'index.{locale}.json',
        'out': {'en': 'index.html', 'id': 'id/index.html'},
    },
    {
        'src': '_src',
        'template': 'privacy.html',
        'strings': 'privacy.{locale}.json',
        'out': {'en': 'privacy.html', 'id': 'id/privacy.html'},
    },
    {
        'src': '_src',
        'template': '404.html',
        'strings': '404.{locale}.json',
        'out': {'en': '404.html', 'id': 'id/404.html'},
    },
    {
        'src': 'projects/squirio/_src',
        'template': 'template.html',
        'strings': '{locale}.json',
        'out': {'en': 'projects/squirio/en/index.html',
                'id': 'projects/squirio/id/index.html'},
    },
    {
        'src': 'projects/squirio/_src',
        'template': 'privacy.html',
        'strings': 'privacy.{locale}.json',
        'out': {'en': 'projects/squirio/en/privacy/index.html',
                'id': 'projects/squirio/id/privacy/index.html'},
    },
    {
        'src': 'projects/squirio/_src',
        'template': 'learn.html',
        'strings': 'learn.{locale}.json',
        'computed': 'learn_sections',
        'out': {'en': 'projects/squirio/en/learn/index.html',
                'id': 'projects/squirio/id/learn/index.html'},
    },
) + tuple(squirio_learn_article(article) for article in SQUIRIO_LEARN_ARTICLES)

BANNER = (
    '<!-- GENERATED FILE - do not edit.\n'
    '     Built by build.py from {src}/{template} + {src}/{strings}.\n'
    '     Edit those and re-run `python build.py`; this file is overwritten. -->\n'
)

# {{key}} or {{key|filter}}. The filter picks the escaping for the context the
# placeholder sits in; see apply_filter.
PLACEHOLDER = re.compile(r'\{\{(\w+)(?:\|(\w+))?\}\}')
CSS_COMMENT = re.compile(r'/\*.*?\*/', re.S)


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def apply_filter(value, name, key):
    """Escape a string for the context it is being substituted into.

    The FAQ answers appear twice on the Squirio page - once as visible copy and
    once inside the structured data, where the two have to stay byte-identical.
    JSON needs escaping that HTML does not. Doing it here rather than in the
    locale file is what lets one key serve both contexts, instead of two copies
    kept in step by hand.

      (none)  substituted verbatim - locale files already carry any entities
              the markup needs, e.g. "Food &amp; Dining"
      |json   for a JSON string body, e.g. inside the ld+json block
    """
    if name is None:
        return value
    if name == 'json':
        # dumps() returns a quoted JSON string; the template supplies the quotes.
        return json.dumps(value, ensure_ascii=False)[1:-1]
    raise SystemExit('%s: unknown filter |%s' % (key, name))


def check_parity(locales, label):
    """Every locale must define exactly the same keys.

    The app holds app_en.arb and app_id.arb at key parity for the same reason:
    a missing key is a page that silently renders a placeholder, and an extra
    one is dead weight nobody will ever notice.
    """
    reference = 'en' if 'en' in locales else next(iter(locales))
    base = set(locales[reference])
    ok = True
    for code, strings in locales.items():
        if code == reference:
            continue
        missing = base - set(strings)
        extra = set(strings) - base
        if missing:
            print('  %s %s: MISSING %d key(s): %s' % (
                label, code, len(missing), ', '.join(sorted(missing)[:8])),
                file=sys.stderr)
            ok = False
        if extra:
            print('  %s %s: UNKNOWN %d key(s): %s' % (
                label, code, len(extra), ', '.join(sorted(extra)[:8])),
                file=sys.stderr)
            ok = False
    return ok


def render(template, strings, code, banner):
    missing = []

    def sub(match):
        key, filter_name = match.group(1), match.group(2)
        if key not in strings:
            missing.append(key)
            return match.group(0)
        return apply_filter(strings[key], filter_name, key)

    out = PLACEHOLDER.sub(sub, template)
    if missing:
        raise SystemExit('%s: unresolved placeholder(s): %s'
                         % (code, ', '.join(sorted(set(missing)))))
    # Banner goes after the doctype so the doctype stays the first thing served.
    # The root pages spell it <!DOCTYPE html> and Squirio's <!doctype html>;
    # match either, and keep whichever casing the template already used.
    return re.sub(r'<!DOCTYPE html>\n', lambda m: m.group(0) + banner,
                  out, count=1, flags=re.I)


def main():
    args = sys.argv[1:]
    if args not in ([], ['--check']):
        raise SystemExit('usage: python build.py [--check]')
    check_only = args == ['--check']
    loaded = []

    print('key parity:')
    for page in PAGES:
        src = os.path.join(HERE, page['src'])
        label = '%s/%s' % (page['src'], page['template'])
        page_locales = page.get('locales', LOCALES)
        locales = {}
        for code in page_locales:
            strings = json.loads(load(os.path.join(
                src, page['strings'].format(locale=code))))
            if page.get('shared_strings'):
                shared = json.loads(load(os.path.join(
                    src, page['shared_strings'].format(locale=code))))
                overlap = set(strings) & set(shared)
                if overlap:
                    raise SystemExit('%s: duplicate shared key(s): %s' % (
                        label, ', '.join(sorted(overlap))))
                strings.update(shared)
            for key, fragment in page.get('fragments', {}).items():
                strings[key] = load(os.path.join(
                    src, fragment.format(locale=code)))
            # SEO alternates must be absolute, but visible language controls
            # must stay on the current origin so local and staging previews do
            # not jump to production. Derive the navigation paths from the
            # canonical alternate data instead of maintaining duplicate URLs.
            if 'alt_en' in strings and 'alt_id' in strings:
                strings['href_en'] = urlsplit(strings['alt_en']).path
                strings['href_id'] = urlsplit(strings['alt_id']).path
            if page.get('computed') == 'learn_sections':
                strings['learn_sections'] = learn_sections(strings)
            if page.get('learn_slug'):
                catalog = json.loads(load(os.path.join(
                    src, 'learn.%s.json' % code)))
                strings['related_cards'] = related_cards(
                    page['learn_slug'], catalog)
            locales[code] = strings
        if not check_parity(locales, label):
            raise SystemExit('locale files are not at key parity - aborting')
        print('  ok  %-38s %3d keys x %d locales'
              % (label, len(locales[next(iter(locales))]), len(page_locales)))
        loaded.append((page, locales,
                       load(os.path.join(src, page['template']))))

    processed = 0
    stale = []
    print('output check:' if check_only else 'output:')
    css_root = os.path.join(HERE, 'projects', 'squirio', 'css')
    for output, sources in SQUIRIO_CSS_BUNDLES.items():
        sections = []
        for source in sources:
            # Source comments stay in the maintainable files. Removing them
            # from the deployable bundle is safe and saves transfer bytes
            # without maintaining a second, hand-minified stylesheet.
            sections.append(CSS_COMMENT.sub(
                '', load(os.path.join(css_root, source))))
        bundled = ''.join(sections)
        path = os.path.join(HERE, output.replace('/', os.sep))
        if check_only:
            if not os.path.isfile(path) or load(path) != bundled:
                stale.append(output)
                print('  stale %-42s' % output)
            else:
                print('  ok    %-42s %6d bytes' % (
                    output, len(bundled.encode('utf-8'))))
        else:
            with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(bundled)
            print('  wrote %-42s %6d bytes' % (
                output, len(bundled.encode('utf-8'))))

    for page, locales, template in loaded:
        banner = BANNER.format(src=page['src'], template=page['template'],
                               strings=page['strings'].format(locale='<locale>'))
        for code in locales:
            rendered = render(template, locales[code], code, banner)
            path = os.path.join(HERE, page['out'][code].replace('/', os.sep))
            output = page['out'][code]
            if check_only:
                if not os.path.isfile(path) or load(path) != rendered:
                    stale.append(output)
                    print('  stale %-42s' % output)
                else:
                    print('  ok    %-42s %6d bytes'
                          % (output, len(rendered.encode('utf-8'))))
            else:
                parent = os.path.dirname(path)
                if parent and not os.path.isdir(parent):
                    os.makedirs(parent)
                with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(rendered)
                print('  wrote %-42s %6d bytes'
                      % (output, len(rendered.encode('utf-8'))))
            processed += 1

    if stale:
        raise SystemExit('%d generated file(s) are stale; run python build.py'
                         % len(stale))
    if check_only:
        print('%d generated HTML files and %d CSS bundles are current'
              % (processed, len(SQUIRIO_CSS_BUNDLES)))
    else:
        print('%d files written' % processed)


if __name__ == '__main__':
    main()
