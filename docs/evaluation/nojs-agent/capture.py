#!/usr/bin/env python3
"""Host-only HTTP capture for supplied-text agent tests; never an agent tool.

Keep raw HTML locally and hash it. Commit only the JSON observation/text. This
does not simulate a successful hosted webpage-reader call or execute page JS.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if not self.hidden and tag in ('h1', 'h2', 'h3', 'p', 'pre', 'li', 'br', 'section'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden -= 1
        if not self.hidden and tag in ('h1', 'h2', 'h3', 'p', 'pre', 'li', 'section'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def capture(url, output):
    split = urlsplit(url)
    if split.scheme != 'https' or split.netloc != 'tujia.biz' or not split.path.startswith('/text/'):
        raise ValueError('Only the authorized static dictionary route is captured')
    encoded = urlunsplit((split.scheme, split.netloc, quote(split.path, safe='/%'), split.query, ''))
    observation = {'url': url, 'request_url': encoded,
                   'fetched_at': datetime.now(timezone.utc).isoformat(),
                   'host_transport': 'python_urllib_https',
                   'participant_transport': 'supplied', 'page_js': 'not_executed'}
    try:
        with urlopen(Request(encoded, headers={'User-Agent': 'TujiaSkillEvidenceQA/1.0'}), timeout=30) as response:
            raw = response.read()
            observation.update(http_status=response.status, content_type=response.headers.get('Content-Type'),
                               bytes=len(raw), html_sha256=hashlib.sha256(raw).hexdigest())
        output.with_suffix('.html').write_bytes(raw)
        if split.path.endswith('.json'):
            text = raw.decode('utf-8')
            json.loads(text)
        else:
            parser = Text()
            parser.feed(raw.decode('utf-8'))
            text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
        observation.update(status='retrieved', extraction='host_visible_text', text=text,
                           text_sha256=hashlib.sha256(text.encode()).hexdigest())
    except Exception as error:
        observation.update(status='unavailable', error=str(error))
    output.write_text(json.dumps(observation, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in observation.items() if k != 'text'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    capture(args.url, args.output)
