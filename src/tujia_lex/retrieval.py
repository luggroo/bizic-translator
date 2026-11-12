"""Execute the same semantic plan with real BGE or static exact lookup.

Scores remain engine/query-local. RRF is a ranking statistic, never a cosine.
Raw original-query neighbors remain available even after construction filtering.
"""
from __future__ import annotations

from collections import OrderedDict
import re
import time

from .query_plan import QueryPlan, normalize
from .static import source_priority


def sense_keys(record):
    return {normalize(s) for text in [record.get('zh', ''), record.get('en', '')]
            for s in [text, *re.split(r'[;；、/／，,\n]+', text)] if s.strip()}


def supports(record, component):
    keys = sense_keys(record)
    wanted = {normalize(component.query), *map(normalize, component.alternatives)}
    if not keys.intersection(wanted):
        return False
    pos = (record.get('pos') or '').lower()
    # Homographs/classifiers/suffixes cannot silently serve as free lexical heads.
    if component.role == 'head' and (pos.startswith('v') or 'suff' in pos):
        return False
    if component.role == 'predicate' and (pos.startswith(('n', 'cl')) or 'suff' in pos):
        return False
    if component.role in {'patient', 'landmark', 'location'} and (pos.startswith(('cl', 'v')) or 'suff' in pos):
        return False
    return True


def candidate_key(record):
    # Merge route duplicates by same entry/sense/scope; do not drop witness IDs.
    return (record.get('entry_id', record['id']), record.get('zh', ''), record.get('en', ''),
            record.get('pos'), record.get('dialect'), tuple(record.get('locations') or []))


def rejected_reason(record, plan):
    keys = sense_keys(record)
    a = plan.analysis
    if any(c.query == '气味' for c in a.components):
        if keys.intersection({'incense', '香', '闻', 'to smell'}):
            return 'incense/perception verb does not denote odor'
    if a.family == 'event_object' and any(c.query == '喝' for c in a.components) and keys.intersection({'水', 'water', '茶', '酒'}):
        return 'beverage instance cannot replace drink nominalization'
    if a.family == 'negative_ability' and keys.intersection({'不知道', '不知', 'not know', '奇怪'}):
        return 'ignorance/strangeness does not express negative ability'
    return None


class RetrievalSession:
    def __init__(self, index=None, encoder=None, static=None, cache_size=512):
        self.index, self.encoder, self.static = index, encoder, static
        self.cache, self.cache_size = OrderedDict(), cache_size
        self.engine_calls = 0

    def search(self, query, engine, top_k, dialect, **filters):
        key = (query, engine, top_k, dialect, tuple(sorted(filters.items())))
        start = time.perf_counter()
        cached = key in self.cache
        if cached:
            result = self.cache[key]
            self.cache.move_to_end(key)
        else:
            if engine == 'static':
                if self.static is None:
                    raise ValueError('Static route needs verified lexicon shards')
                result = self.static.search(query, top_k=top_k, dialect=dialect)
            else:
                if self.index is None:
                    raise ValueError('Index route needs a compatible index')
                result = self.index.search(query, mode=engine, encoder=self.encoder,
                    top_k=top_k, dialect=None if dialect == 'any' else dialect, **filters)
            self.engine_calls += 1
            self.cache[key] = result
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
        return result, {'cache_hit': cached, 'seconds': time.perf_counter() - start}

    def run(self, plan: QueryPlan, route='C', *, budget='natural', top_k=20, candidate_budget=20, hybrid_static=True):
        if route not in 'ABCDE' or len(route) != 1 or budget not in {'natural', 'matched'}:
            raise ValueError('invalid route or budget')
        if not 1 <= top_k <= 100 or not 1 <= candidate_budget <= 1000:
            raise ValueError('invalid result or candidate budget')
        start = time.perf_counter()
        queries = plan.queries if route in 'CDE' else plan.queries[:1]
        engines = ['semantic', 'static'] if route == 'E' and hybrid_static else (["semantic"] if route == 'E' else [{'A': 'exact', 'B': 'semantic', 'C': 'semantic', 'D': 'static'}[route]])
        tasks = [(q, e) for q in queries for e in engines]
        # Equal hard limits: <=12 searches, exactly candidate_budget requested slots.
        # Baselines use one query with the full slot allowance; no padded calls.
        if budget == 'matched':
            tasks = tasks[:min(12, candidate_budget)]
        traces, union, call_start = [], {}, self.engine_calls
        enc_start = getattr(self.encoder, 'query_encodings', 0)
        for n, (q, engine) in enumerate(tasks):
            k = top_k if budget == 'natural' else candidate_budget // len(tasks) + (n < candidate_budget % len(tasks))
            hits, timing = self.search(q.query, engine, k, plan.dialect)
            traces.append({'query': q.query, 'relation': q.relation, 'component': q.component,
                           'engine': engine, 'limit': k, **timing, 'results': hits})
            for rank, r in enumerate(hits, 1):
                key = candidate_key(r)
                provenance = {'query': q.query, 'relation': q.relation, 'component': q.component,
                    'engine': engine, 'rank': rank, 'score': r.get('score'), 'record_id': r['id']}
                if key not in union:
                    union[key] = {**r, 'notations': {k:list(v) for k,v in r.get('notations',{}).items()}, 'provenance': [], 'rrf': 0.0}
                item = union[key]
                # Repeated raw baseline slots do not inflate RRF.
                if provenance not in item['provenance']:
                    item['provenance'].append(provenance)
                    item['rrf'] += 1 / (60 + rank)
                for field, id_field in [('attestations', 'id'), ('sources', 'attestation_id')]:
                    current = {x.get(id_field) for x in item.get(field, [])}
                    item[field] = item.get(field, []) + [x for x in r.get(field, []) if x.get(id_field) not in current]
                for scheme, values in r.get('notations', {}).items():
                    current = item.setdefault('notations', {}).setdefault(scheme, [])
                    for value in values:
                        if value not in current:
                            current.append(value)
        candidates = list(union.values())
        for r in candidates:
            r['supported_components'] = [c.key for c in plan.analysis.components if supports(r, c)]
            r['rejection'] = rejected_reason(r, plan)
            r['selection_status'] = 'rejected' if r['rejection'] else ('component_evidence' if r['supported_components'] else 'unresolved_neighbor')
        # A/B preserve original ordering. C balances queries, without gold-aware reranking.
        if route in 'CD':
            candidates.sort(key=lambda r: (min(p['rank'] for p in r['provenance']),
                min(i for i,t in enumerate(traces) if any(p['query'] == t['query'] for p in r['provenance'])), -r['rrf'], r['id']))
        elif route == 'E':
            candidates.sort(key=lambda r: (bool(r['rejection']), not bool(r['supported_components']),
                                           -r['rrf'], source_priority(r), r['id']))
            # Meaning-relevant source preference after support, plus component diversity.
            front, chosen = [], set()
            for c in plan.analysis.components:
                options = [r for r in candidates if c.required and c.key in r['supported_components'] and not r['rejection']]
                if options:
                    best = min(options, key=lambda r: (source_priority(r), -r['rrf'], r['id']))
                    if best['id'] not in chosen:
                        front.append(best)
                        chosen.add(best['id'])
            candidates = front + [r for r in candidates if r['id'] not in chosen]
        return {'route': route, 'budget': budget, 'plan': plan.to_dict(), 'queries': traces,
            'raw_results': traces[0]['results'], 'candidates': candidates[:top_k],
            'rejected_candidates': [r for r in candidates if r['rejection']],
            'cost': {'query_count': len(tasks), 'unique_queries': len({q.query for q,e in tasks}),
                'engine_calls': self.engine_calls - call_start,
                'query_encodings': getattr(self.encoder, 'query_encodings', 0) - enc_start,
                'requested_candidates': sum(t['limit'] for t in traces),
                'candidate_count': sum(len(t['results']) for t in traces), 'unique_candidates': len(candidates),
                'seconds': time.perf_counter() - start}}
