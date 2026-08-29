#!/usr/bin/env python3
"""Generate every localised static page on the site from _src/.

    python build.py

Reads each page's template plus one JSON file per locale and writes complete,
plain static HTML. There is no runtime dependency and nothing is rendered
client-side: what the build writes is exactly what the server sends.

Run this after editing anything under a _src/ directory. Never hand-edit a
generated file - it is an output and the next build overwrites it. Every
generated file carries a banner saying so.

This used to live at projects/squirio/build.py and build one page in one
language. It now covers the root site as well, so both halves of japandi.dev
share one generator rather than one of them being hand-maintained HTML.
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Every locale the site is published in. 'en' is the reference: it defines the
# set of keys every other locale must match, and it is what x-default points at.
LOCALES = ('en', 'id')

# One entry per page.
#
#   src       directory holding the template and the locale JSON files
#   template  the template file inside src
#   strings   locale JSON filename pattern inside src; {locale} is substituted
#   out       output path per locale, relative to the repo root
#
# The English output paths are the site's existing URLs and must not change -
# they are already indexed and linked. Indonesian pages take an /id/ segment at
# the level of the site they belong to, which is what makes each pair of URLs a
# clean hreflang cluster.
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
        'out': {'en': 'projects/squirio/index.html',
                'id': 'projects/squirio/id/index.html'},
    },
    {
        'src': 'projects/squirio/_src',
        'template': 'privacy.html',
        'strings': 'privacy.{locale}.json',
        'out': {'en': 'projects/squirio/privacy/index.html',
                'id': 'projects/squirio/id/privacy/index.html'},
    },
)

BANNER = (
    '<!-- GENERATED FILE - do not edit.\n'
    '     Built by build.py from {src}/{template} + {src}/{strings}.\n'
    '     Edit those and re-run `python build.py`; this file is overwritten. -->\n'
)

# {{key}} or {{key|filter}}. The filter picks the escaping for the context the
# placeholder sits in; see apply_filter.
PLACEHOLDER = re.compile(r'\{\{(\w+)(?:\|(\w+))?\}\}')


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
    reference = 'en'
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
    loaded = []

    print('key parity:')
    for page in PAGES:
        src = os.path.join(HERE, page['src'])
        label = '%s/%s' % (page['src'], page['template'])
        locales = {
            code: json.loads(load(os.path.join(
                src, page['strings'].format(locale=code))))
            for code in LOCALES
        }
        if not check_parity(locales, label):
            raise SystemExit('locale files are not at key parity - aborting')
        print('  ok  %-38s %3d keys x %d locales'
              % (label, len(locales['en']), len(LOCALES)))
        loaded.append((page, locales,
                       load(os.path.join(src, page['template']))))

    written = 0
    print('output:')
    for page, locales, template in loaded:
        banner = BANNER.format(src=page['src'], template=page['template'],
                               strings=page['strings'].format(locale='<locale>'))
        for code in LOCALES:
            rendered = render(template, locales[code], code, banner)
            path = os.path.join(HERE, page['out'][code].replace('/', os.sep))
            parent = os.path.dirname(path)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent)
            with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(rendered)
            print('  wrote %-42s %6d bytes'
                  % (page['out'][code], len(rendered.encode('utf-8'))))
            written += 1

    print('%d files written' % written)


if __name__ == '__main__':
    main()
