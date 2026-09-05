"""Dependency-free release checks for the generated static site."""

import base64
import hashlib
import json
import os
import re
import unittest
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import build


ROOT = build.HERE
SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
              'xhtml': 'http://www.w3.org/1999/xhtml'}


class Page(HTMLParser):
    def __init__(self, relative_path):
        super().__init__()
        self.relative_path = relative_path
        self.attrs = []
        self.ids = set()
        self.links = []
        self.assets = []
        self.json_ld = []
        self.heading_levels = []
        self._json_buffer = None
        self._title_buffer = None
        self.title = ''

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        self.attrs.append((tag, data))
        if data.get('id'):
            self.ids.add(data['id'])
        if tag == 'a' and data.get('href'):
            self.links.append(data['href'])
        for key in ('src', 'poster'):
            if data.get(key):
                self.assets.append(data[key])
        if data.get('srcset'):
            self.assets.extend(item.strip().split()[0]
                               for item in data['srcset'].split(','))
        if tag == 'script' and data.get('type') == 'application/ld+json':
            self._json_buffer = []
        if tag == 'title':
            self._title_buffer = []
        if re.fullmatch(r'h[1-6]', tag):
            self.heading_levels.append(int(tag[1]))

    def handle_endtag(self, tag):
        if tag == 'script' and self._json_buffer is not None:
            self.json_ld.append(json.loads(''.join(self._json_buffer)))
            self._json_buffer = None
        if tag == 'title' and self._title_buffer is not None:
            self.title = ''.join(self._title_buffer).strip()
            self._title_buffer = None

    def handle_data(self, data):
        if self._json_buffer is not None:
            self._json_buffer.append(data)
        if self._title_buffer is not None:
            self._title_buffer.append(data)

    def tags(self, name):
        return [attrs for tag, attrs in self.attrs if tag == name]

    def meta(self, name):
        return [attrs.get('content', '') for attrs in self.tags('meta')
                if attrs.get('name') == name]

    def rel(self, value):
        return [attrs for attrs in self.tags('link')
                if value in attrs.get('rel', '').split()]


def generated_paths():
    paths = []
    for page in build.PAGES:
        for path in page['out'].values():
            if path not in paths:
                paths.append(path)
    return paths


def load_pages():
    pages = []
    for relative in generated_paths():
        parser = Page(relative)
        parser.feed(build.load(os.path.join(ROOT, relative.replace('/', os.sep))))
        pages.append(parser)
    return pages


PAGES = load_pages()
INDEXABLE = [page for page in PAGES if not page.meta('robots') or
             'noindex' not in page.meta('robots')[0].lower()]
BY_CANONICAL = {page.rel('canonical')[0]['href']: page for page in INDEXABLE}


class AccessibilitySemanticsTests(unittest.TestCase):
    def test_language_and_landmarks(self):
        for page in PAGES:
            with self.subTest(page=page.relative_path):
                html = page.tags('html')
                self.assertEqual(len(html), 1)
                self.assertIn(html[0].get('lang'), ('en', 'id'))
                self.assertEqual(len(page.tags('main')), 1)
                site_headers = [attrs for attrs in page.tags('header')
                                if 'data-site-header' in attrs or
                                'data-jd-header' in attrs]
                self.assertEqual(len(site_headers), 1)
                self.assertEqual(len(page.tags('footer')), 1)
                self.assertEqual(len(page.tags('h1')), 1)
                self.assertTrue(all(nav.get('aria-label') or
                                    nav.get('aria-labelledby')
                                    for nav in page.tags('nav')))

    def test_heading_levels_do_not_skip(self):
        for page in PAGES:
            with self.subTest(page=page.relative_path):
                self.assertTrue(page.heading_levels)
                self.assertEqual(page.heading_levels[0], 1)
                self.assertTrue(all(current <= previous + 1
                                    for previous, current in
                                    zip(page.heading_levels,
                                        page.heading_levels[1:])))

    def test_images_have_text_alternatives_and_dimensions(self):
        for page in PAGES:
            for number, image in enumerate(page.tags('img'), 1):
                with self.subTest(page=page.relative_path, image=number):
                    self.assertIn('alt', image)
                    self.assertTrue(image.get('width'))
                    self.assertTrue(image.get('height'))

    def test_control_names_and_aria_references(self):
        for page in PAGES:
            for tag, attrs in page.attrs:
                with self.subTest(page=page.relative_path, tag=tag):
                    for name in ('aria-controls', 'aria-labelledby',
                                 'aria-describedby'):
                        if attrs.get(name):
                            for target in attrs[name].split():
                                self.assertIn(target, page.ids)
                    if tag == 'button':
                        self.assertEqual(attrs.get('type'), 'button')
                        self.assertTrue(attrs.get('aria-label') or
                                        attrs.get('aria-labelledby') or
                                        attrs.get('aria-controls'))

    def test_skip_links_target_main_content(self):
        for page in PAGES:
            skips = [attrs for attrs in page.tags('a')
                     if 'skip' in attrs.get('class', '').split() or
                     'skip-link' in attrs.get('class', '')]
            with self.subTest(page=page.relative_path):
                self.assertEqual(len(skips), 1)
                self.assertIn(skips[0]['href'].lstrip('#'), page.ids)


class SeoTests(unittest.TestCase):
    def test_indexable_metadata_is_unique_and_complete(self):
        titles = []
        descriptions = []
        for page in INDEXABLE:
            with self.subTest(page=page.relative_path):
                self.assertTrue(page.title)
                self.assertEqual(len(page.meta('description')), 1)
                self.assertEqual(len(page.rel('canonical')), 1)
                self.assertEqual(len(page.meta('viewport')), 1)
                canonical = page.rel('canonical')[0]['href']
                self.assertTrue(canonical.startswith('https://japandi.dev/'))
                titles.append(page.title)
                descriptions.append(page.meta('description')[0])
        self.assertEqual(len(titles), len(set(titles)))
        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_404_pages_are_noindex_and_not_canonicalized(self):
        pages = [page for page in PAGES if page.relative_path.endswith('404.html')]
        self.assertEqual(len(pages), 2)
        for page in pages:
            self.assertIn('noindex', page.meta('robots')[0].lower())
            self.assertFalse(page.rel('canonical'))

    def test_html_hreflang_clusters_are_reciprocal(self):
        for page in INDEXABLE:
            alternates = {item.get('hreflang'): item.get('href')
                          for item in page.rel('alternate') if item.get('hreflang')}
            with self.subTest(page=page.relative_path):
                self.assertEqual(set(alternates), {'en', 'id', 'x-default'})
                self.assertEqual(alternates['x-default'], alternates['en'])
                for language in ('en', 'id'):
                    target = BY_CANONICAL[alternates[language]]
                    reverse = {item.get('hreflang'): item.get('href')
                               for item in target.rel('alternate')}
                    self.assertEqual(reverse, alternates)

    def test_sitemap_matches_canonicals_and_hreflang(self):
        root = ET.parse(os.path.join(ROOT, 'sitemap.xml')).getroot()
        entries = root.findall('sm:url', SITEMAP_NS)
        sitemap_urls = set()
        for entry in entries:
            location = entry.find('sm:loc', SITEMAP_NS).text
            sitemap_urls.add(location)
            page = BY_CANONICAL[location]
            sitemap_alternates = {
                item.attrib['hreflang']: item.attrib['href']
                for item in entry.findall('xhtml:link', SITEMAP_NS)}
            html_alternates = {item['hreflang']: item['href']
                               for item in page.rel('alternate')}
            self.assertEqual(sitemap_alternates, html_alternates)
            self.assertIn(location, sitemap_alternates.values())
        self.assertEqual(sitemap_urls, set(BY_CANONICAL))

    def test_json_ld_is_valid_and_uses_https_ids(self):
        self.assertTrue(any(page.json_ld for page in INDEXABLE))
        for page in INDEXABLE:
            for block in page.json_ld:
                serialized = json.dumps(block, ensure_ascii=False)
                self.assertNotIn('http://japandi.dev', serialized)
                nodes = block.get('@graph', [block])
                for node in nodes:
                    self.assertEqual(node.get('@context', 'https://schema.org'),
                                     'https://schema.org')

    def test_robots_allows_crawling_and_declares_sitemap(self):
        robots = build.load(os.path.join(ROOT, 'robots.txt'))
        self.assertRegex(robots, r'(?im)^User-agent:\s*\*$')
        self.assertRegex(robots, r'(?im)^Allow:\s*/$')
        self.assertRegex(robots, r'(?im)^Sitemap:\s*https://japandi\.dev/sitemap\.xml$')


class IntegrityTests(unittest.TestCase):
    def test_local_links_assets_and_fragments_resolve(self):
        for page in INDEXABLE:
            base = page.rel('canonical')[0]['href']
            for value in page.links:
                url = urllib.parse.urljoin(base, value)
                parsed = urllib.parse.urlsplit(url)
                if parsed.scheme not in ('http', 'https') or parsed.netloc != 'japandi.dev':
                    continue
                target_url = 'https://japandi.dev' + parsed.path
                with self.subTest(page=page.relative_path, href=value):
                    self.assertIn(target_url, BY_CANONICAL)
                    if parsed.fragment:
                        self.assertIn(parsed.fragment, BY_CANONICAL[target_url].ids)
            for value in page.assets:
                parsed = urllib.parse.urlsplit(urllib.parse.urljoin(base, value))
                if parsed.netloc != 'japandi.dev':
                    continue
                path = os.path.join(ROOT, parsed.path.lstrip('/').replace('/', os.sep))
                with self.subTest(page=page.relative_path, asset=value):
                    self.assertTrue(os.path.isfile(path), path)

    def test_root_inline_script_matches_csp_hash(self):
        policy = build.load(os.path.join(ROOT, '.htaccess'))
        hashes = set(re.findall(r"'sha256-([^']+)'", policy))
        self.assertTrue(hashes)
        for relative in ('index.html', 'privacy.html', '404.html',
                         'id/index.html', 'id/privacy.html', 'id/404.html'):
            html = build.load(os.path.join(ROOT, relative.replace('/', os.sep)))
            html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
            body = re.search(r'<script>(.*?)</script>', html, re.S).group(1)
            digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            self.assertIn(digest, hashes, relative)


if __name__ == '__main__':
    unittest.main()
