#!/usr/bin/env python3
"""HTTP evidence harness, not a hosted-model or no-CLI execution test.

Seed only /text/; discover later URLs from visible main text. Keeps each
witness's fields/notations together and records every fetched document.
"""
import argparse
import contextlib
import concurrent.futures
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import re
import threading
import time
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.main = False
        self.text = []
        self.witnesses = []
        self.candidates = []
        self.record = None
        self.capture = None
        self.value = []
        self.label = None
        self.version = None
        self.feed(html)
        self.body_text = ' '.join(self.text)
        self.urls = list(dict.fromkeys(re.findall(r'https://tujia\.biz/[^\s<>]+', self.body_text)))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name') == 'prepared-data-version':
            self.version = attrs.get('content')
        if tag == 'main':
            self.main = True
        if tag == 'article':
            kind = 'witnesses' if 'witness' in attrs.get('class', '').split() else 'candidates'
            self.record = {'kind': kind, 'fields': {}, 'text': []}
        if self.record is not None and tag in ('dt', 'dd'):
            self.capture, self.value = tag, []

    def handle_data(self, text):
        if self.main and text.strip():
            self.text.append(text.strip())
        if self.record is not None and text.strip():
            self.record['text'].append(text.strip())
        if self.capture:
            self.value.append(text)

    def handle_endtag(self, tag):
        if tag == 'main':
            self.main = False
        if tag == self.capture:
            value = ''.join(self.value).strip()
            if tag == 'dt':
                self.label = value.split(' / ')[-1]
            else:
                self.record['fields'][self.label] = value
            self.capture = None
        if tag == 'article' and self.record is not None:
            self.record['text'] = ' '.join(self.record['text'])
            getattr(self, self.record.pop('kind')).append(self.record)
            self.record = None


def directory_status(page, query):
    # Only an explicit complete-list statement allows a not-published result.
    if 'All available text pages are listed below.' not in page.body_text:
        return 'partial'
    from urllib.parse import unquote
    return 'published' if any(unquote(urlsplit(u).path).endswith('/' + query + '.html') for u in page.urls) else 'not_published'


def run(directory, local_origin=None):
    trace = []
    def fetch(url, discovered_on):
        parsed = urlsplit(url)
        if discovered_on and (parsed.scheme != 'https' or parsed.netloc != 'tujia.biz'):
            raise AssertionError('Unexpected advertised origin')
        request_url = url
        if local_origin and discovered_on:
            request_url = local_origin + parsed.path
        start = time.monotonic()
        with urllib.request.urlopen(request_url, timeout=25) as response:
            raw = response.read()
            item = {'url': url, 'request_url': request_url, 'discovered_on': discovered_on,
                    'http_status': response.status, 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest(),
                    'seconds': round(time.monotonic() - start, 4)}
        trace.append(item)
        assert item['http_status'] == 200
        assert b'<script' not in raw.lower()
        return Page(raw.decode('utf-8'))

    index = fetch(directory, None)
    assert directory_status(index, '吃') == 'published'
    assert directory_status(index, '苹果') == 'not_published'
    query_urls = [u for u in index.urls if '/text/lookup/' in urlsplit(u).path]
    assert len(query_urls) == 1
    query = fetch(query_urls[0], directory)
    assert len(query.candidates) == 4
    details = [u for u in query.urls if urlsplit(u).path.startswith('/text/entry/')]
    interactive = [u for u in query.urls if urlsplit(u).query.startswith('id=')]
    assert len(details) == 2 and len(interactive) == 2
    witnesses = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pages = list(pool.map(lambda url: fetch(url, query_urls[0]), details))
    for url, page in zip(details, pages):
        assert page.version == index.version == query.version
        for record in page.witnesses:
            fields = record['fields']
            for name in ('Witness ID', 'Entry ID', 'Source ID', 'Witness locality', 'Original notation'):
                assert fields[name]
            assert 'stedT' not in fields['Witness ID']
            record.update(url=url, data_version=page.version)
            witnesses.append(record)
    counts = {entry: sum(w['fields']['Entry ID'] == entry for w in witnesses)
              for entry in {w['fields']['Entry ID'] for w in witnesses}}
    assert counts == {'w684': 18, 'stedt-rn-43584': 3}
    first = next(w for w in witnesses if w['fields']['Witness ID'] == 'w684')
    assert first['fields']['Source ID'] != first['fields']['Witness ID']
    assert first['fields']['Witness locality'] == '未记录 / Not recorded'
    assert len(trace) == 4
    assert directory_status(Page('<main><h1>词典文本索引</h1></main>'), '苹果') == 'partial'
    return {'result': 'PASS', 'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'transport': 'Python urllib HTTP harness', 'hosted_model_test': False,
            'seed': directory, 'data_version': index.version, 'requests': trace,
            'candidate_count': len(query.candidates), 'witness_counts': counts,
            'interactive_only_candidates': interactive,
            'negative_cases': {'苹果': 'not_published, not lexical absence',
                               'truncated_directory_fixture': 'partial, not zero matches'},
            'witnesses': witnesses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', default='https://tujia.biz/text/')
    parser.add_argument('--site', type=pathlib.Path, help='Serve a local built website for the same HTTP test.')
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    with contextlib.ExitStack() as stack:
        origin = None
        if args.site:
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.site.resolve()))
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            stack.callback(server.server_close)
            stack.callback(server.shutdown)
            origin = 'http://127.0.0.1:' + str(server.server_port)
            args.directory = origin + '/text/'
        report = run(args.directory, origin)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'witnesses'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
