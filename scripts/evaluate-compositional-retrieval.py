#!/usr/bin/env python3
"""Fresh A–E evaluation of verified inventory, components and constructions."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import time

from tujia_lex.constructions import compose, REGISTRY
from tujia_lex.embedding import load_encoder
from tujia_lex.evaluation import grade, aggregate
from tujia_lex.index import load_index
from tujia_lex.query_plan import plan, PlannedQuery
from tujia_lex.retrieval import RetrievalSession
from tujia_lex.static import StaticLexicon


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--index',required=True)
    p.add_argument('--model-path',required=True)
    p.add_argument('--lexicon',default='skills/translate-tujia/lexicon')
    p.add_argument('--dataset',default='tests/data/semantic-compositional-challenge.json')
    p.add_argument('--output',default='docs/evaluation/compositional')
    a=p.parse_args()
    output=Path(a.output);output.mkdir(parents=True,exist_ok=True)
    dataset=json.loads(Path(a.dataset).read_text());cases=dataset['cases']
    # This evaluation requires a complete, matching dictionary snapshot for ALL routes.
    start=time.perf_counter(); index=load_index(a.index);encoder=load_encoder(a.model_path)
    static=StaticLexicon(a.lexicon)
    if index.manifest['metadata']['repository_revision'] != static.manifest['revision']:
        raise ValueError('Static/BGE source revisions differ; rebuild matching static shards')
    for key, source_key in [('lexical_entry_count','source_dictionary_entries'),('lexical_attestation_count','source_dictionary_attestations')]:
        if index.manifest[key] != index.manifest['metadata'][source_key]:
            raise ValueError('Incomplete BGE dictionary coverage')
    all_aids={att['id'] for r in index.records for att in r.get('attestations',[])} | {r['id'] for r in index.records if r['record_type']=='survey_lexeme'}
    for case in cases:
        for target in case['expected_components']:
            if any(not set(g['attestation_ids']) <= all_aids for g in target['gold']):
                raise ValueError('Gold contains an unverified attestation')
    load_seconds=time.perf_counter()-start
    catalog={}
    def pack(record):
        # Catalog retains full original records. Query-local scores stay in traces.
        key=record['id']
        original={k:v for k,v in record.items() if k not in {'score','retrieval_mode','provenance','rrf','supported_components','rejection','selection_status'}}
        catalog[key]=original
        return {k:v for k,v in record.items() if k in {'id','score','retrieval_mode','provenance','rrf','supported_components','rejection','selection_status'}}
    rows=[]
    for case in cases:
        # No gold components or labels are passed to the planner.
        shared=plan(case['expression'],case['context'],case['dialect'])
        case_rows=[]
        for budget in ['natural','matched','single_query']:
            for route in 'ABCDE':
                # Warm model/index, cold query cache for each independent route;
                # this prevents a route from receiving free baseline encodings.
                encoder.query_cache.clear()
                session=RetrievalSession(index,encoder,static)
                actual=shared
                run_budget=budget
                if budget=='single_query':
                    # Exactly ONE search, <=20 candidates for each route. C/D use
                    # a compact semantic rewrite; E uses BGE, so no free exact calls.
                    if route in 'CDE':
                        rewrite=' '.join([shared.analysis.meaning,*[c.query for c in shared.analysis.components if c.required]])
                        actual=replace(shared,queries=[PlannedQuery(rewrite[:120],'compact_semantic_frame')])
                    run_budget='natural'
                result=session.run(actual, route, budget=run_budget, hybrid_static=budget!='single_query')
                result['route']=route;result['budget']=budget
                composition=compose(shared,result['candidates'])
                metrics=grade(case,result,composition)
                if budget=='single_query':
                    result['raw_results_note']='Raw original Top-20 is stored in natural B for this case; compact frame consumes the single query budget.'
                for trace in result['queries']:
                    trace['results']=[pack(r) for r in trace['results']]
                result['raw_results']=[pack(r) for r in result['raw_results']]
                result['candidates']=[pack(r) for r in result['candidates']]
                result['rejected_candidates']=[pack(r) for r in result['rejected_candidates']]
                result.update(case_id=case['id'],expression=case['expression'],family=case['family'],split=case['split'],
                              metrics=metrics,composition=composition)
                rows.append(result);case_rows.append(result)
        (output/(case['id']+'.json')).write_text(json.dumps({'case':case,'routes':case_rows},ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'case':case['id'],'expression':case['expression'],'routes':len(case_rows),'seconds':round(time.perf_counter()-start,2)},ensure_ascii=False),flush=True)
    summaries={}
    for budget in ['natural','matched','single_query']:
        summaries[budget]={}
        for route in 'ABCDE':
            subset=[r for r in rows if r['budget']==budget and r['route']==route]
            summaries[budget][route]={'overall':aggregate(subset),
                'families':{f:aggregate([r for r in subset if r['family']==f]) for f in sorted({r['family'] for r in subset})},
                'splits':{s:aggregate([r for r in subset if r['split']==s]) for s in ['anchor','challenge','holdout']}}
    # Explicit production reuse test with real model calls in THIS execution.
    encoder.query_cache.clear(); cached_session=RetrievalSession(index,encoder,static)
    cp=plan('饮料');cold=cached_session.run(cp,'C');warm=cached_session.run(cp,'C')
    with (output/'records.jsonl').open('w') as stream:
        for key in sorted(catalog): stream.write(json.dumps(catalog[key],ensure_ascii=False)+'\n')
    meta={'status':'executed_fresh_real_BGE', 'finished_at_utc':datetime.now(timezone.utc).isoformat(),
        'command':[sys.executable,*sys.argv], 'python':platform.python_version(),
        'translator_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'implementation_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*Path('src/tujia_lex').glob('*.py'),Path(__file__)]},
        'dataset_sha256':hashlib.sha256(Path(a.dataset).read_bytes()).hexdigest(),
        'index_manifest':index.manifest,'static_manifest':{k:v for k,v in static.manifest.items() if k!='buckets'},
        'model':encoder.identity,'model_index_load_seconds':load_seconds,
        'elapsed_seconds':time.perf_counter()-start,'cases':len(cases),'runs':len(rows),
        'cache_probe':{'cold':cold['cost'],'warm':warm['cost']},
        'budgets':{'natural':'each query returns Top-20; up to 10 planned queries (E two engines)',
                  'matched':'same <=12 search calls and 20 requested candidate slots per route; B/A use all slots for the original query',
                  'single_query':'exactly one search and 20 slots; C/D compact rewrite; E uses the same BGE pool as C, grammar reranking only'},
        'metric_definitions':{
            'recall':'macro per case: recovered verified component gold groups / verified component groups; alternate IDs are disjunctive',
            'entry_recall':'macro recall of the union of verified alternative entry IDs (also reported for conventional ID recall)',
            'mrr':'macro reciprocal rank of first verified gold hit per case',
            'component_mrr':'reciprocal rank averaged over verified components, then cases',
            'pending':'unverified components excluded from recall/MRR denominators; still block full construction coverage',
            'meaning':'automatic plan frame preservation and lexical coverage proxy; no native-speaker accuracy claim',
            'false_positive':'explicitly adjudicated negative controls only; other neighbors remain unjudged',
            'latency':'warm model/index, cold encoder/result query caches for each route; static buckets warm across cases; load reported separately',
            'native':'not numerically estimable without etymology annotations; sourced lexeme utilization reported separately'},
        'summary':summaries}
    (output/'results.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
