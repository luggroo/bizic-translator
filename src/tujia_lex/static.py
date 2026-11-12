"""Cached, integrity-checked access to the existing FNV exact lexicon shards."""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path

from .query_plan import normalize


def bucket_of(query):
    h = 2166136261
    for byte in normalize(query).encode('utf-8'):
        h = ((h ^ byte) * 16777619) & 0xffffffff
    return f'{h >> 24:02x}'


class StaticLexicon:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.manifest = json.loads((self.directory / 'manifest.json').read_text())
        self.shard_reads = 0

    @lru_cache(maxsize=64)
    def _bucket(self, bucket):
        result = {}
        for info in self.manifest['buckets'].get(bucket, []):
            name = info['path']
            if '/' in name or '\\' in name or '..' in name:
                raise ValueError('Unsafe path in manifest')
            data = (self.directory / name).read_bytes()
            if len(data) != info['bytes'] or hashlib.sha256(data).hexdigest() != info['sha256']:
                raise ValueError(f'Shard checksum mismatch: {name}')
            self.shard_reads += 1
            for line in data.decode().splitlines():
                item = json.loads(line)
                result.setdefault(item['k'], []).append(item['r'])
        return result

    def search(self, query, top_k=20, dialect='north'):
        if not 1 <= len(normalize(query)) <= 120 or not 1 <= top_k <= 100:
            raise ValueError('invalid static query or limit')
        results = []
        for raw in self._bucket(bucket_of(query)).get(normalize(query), []):
            row = dict(zip(self.manifest['record_fields'], raw))
            original = str(row.get('dialect', ''))
            scope = 'north' if '北' in original and '南' not in original else ('south' if '南' in original and '北' not in original else 'unknown')
            if dialect not in (None, 'any') and scope != dialect:
                continue
            source = self.manifest.get('sources', {}).get(row['source'], {})
            aid = row['attestation_id']
            # Retain ALL exported fields, including the same-attestation notation map.
            results.append({**row, 'id': 'static:' + aid, 'kind': 'lexicon',
                'record_type': 'lexical_sense', 'static_record': row.copy(),
                'notations': {k:[{'text':text,'attestationIds':[aid]} for text in values] for k,values in row.get('notations',{}).items()},
                'dialect': scope, 'dialect_original': original,
                'locations': source.get('locations', []), 'forms': [row['term']],
                'attestations': [row.copy()], 'sources': [{
                    'id': row['source'], 'canonical_id': source.get('canonical_id', row['source']),
                    'title': source.get('title', ''), 'attestation_id': aid,
                    'locator': row.get('locator', ''), 'source_ref': row.get('source_ref', '')}],
                'citation': row.get('source_ref', ''), 'score': None, 'retrieval_mode': 'static_exact'})
        return sorted(results, key=lambda r: (source_priority(r), r['id']))[:top_k]


def source_priority(record):
    aliases = {s.get('canonical_id', s.get('id')) for s in record.get('sources', [])}
    return 0 if 'brassett-2006' in aliases else (1 if 'brassett-2004' in aliases else 2)
