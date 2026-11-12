#!/usr/bin/env python3
"""Render the current fresh experiment; no saved historical scores are imported."""
import argparse
import json
from pathlib import Path


def cell(s):
    return str(s).replace('|',' / ').replace('\n',' ')


def pct(x):
    return '—' if x is None else f'{100*x:.1f}%'


def candidate_table(hits, catalog):
    lines=['|Rank|Sense / form|Entry / attestation IDs|Source / locality|Cosine|','|---:|---|---|---|---:|']
    for n,hit in enumerate(hits,1):
        r=catalog[hit['id']]
        aids=[a.get('id',a.get('attestation_id')) for a in r.get('attestations',[])]
        src=', '.join(dict.fromkeys(s.get('canonical_id',s.get('id','')) for s in r.get('sources',[])))
        score='exact' if hit.get('score') is None else f"{hit['score']:.7f}"
        lines.append('|'+ '|'.join(map(cell,[n,r.get('zh','')+' / '+', '.join(r.get('forms',[])),str(r.get('entry_id',''))+' / '+', '.join(aids),src+' / '+str(r.get('locations',[])),score]))+'|')
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',default='docs/evaluation/compositional');a=p.parse_args();root=Path(a.directory)
    meta=json.loads((root/'results.json').read_text())
    catalog={r['id']:r for r in map(json.loads,(root/'records.jsonl').read_text().splitlines())}
    docs=[]
    for path in sorted(root.glob('c[0-9][0-9].json')):
        data=json.loads(path.read_text());c=data['case'];rs=data['routes'];docs.append(data)
        natural={r['route']:r for r in rs if r['budget']=='natural'}
        e=natural['E']; comp=e['composition']; analysis=e['plan']['analysis']
        lines=[f"# {c['id']} {c['expression']}",'',c['meaning']+'.', '',
            f"Family: `{c['family']}`; split: `{c['split']}`; dictionary inventory status: `{c['gold_status']}`.",'',
            '## Semantic plan','',f"Meaning: {analysis['meaning']}",'',
            f"Components: {cell(analysis['components'])}",'',f"Roles: `{analysis['roles']}`; features: `{analysis['features']}`.",'',
            '## Proposed composition','',f"Audit draft (unchanged source lexical forms, labeled grammatical forms): **{comp['draft_source_forms']}**",'',
            f"Basis: [{comp['grammar']['citation']}]({comp['grammar']['url']}). {comp['grammar']['pattern']}.",'',
            f"Lexical slots complete: {comp['lexical_complete']}; construction supported: {comp['construction_supported']}; surface complete: {comp['surface_complete']}.",'',
            f"Unresolved lexical slots: `{comp['missing_components']}`. Realization checks: {comp['unresolved_realization']}. Meaning losses: {comp['meaning_losses']}.",'',
            '|Slot|Selected source form|Entry / attestation|Source|','|---|---|---|---|']
        for key,v in comp['selected'].items():
            lines.append('|'+ '|'.join(map(cell,[key,v['term'],str(v['entry_id'])+' / '+str(v['attestation_id']),v['source'].get('canonical_id','')]))+'|')
        lines+=['','## Five-route comparison','', '|Budget / route|R@1|R@5|R@10|R@20|MRR|Construction|Frame|Queries / candidates|Seconds|', '|---|---:|---:|---:|---:|---:|---|---|---|---:|']
        for r in rs:
            m=r['metrics'];cost=r['cost']
            lines.append('|'+ '|'.join(map(cell,[r['budget']+' / '+r['route'],*[pct(m['recall'][str(k)]) for k in [1,5,10,20]],f"{m['mrr']:.3f}" if m['mrr'] is not None else '—',m['construction_coverage'],m['meaning_preservation']['frame_preserved'],f"{cost['query_count']} / {cost['candidate_count']}",f"{cost['seconds']:.4f}"]))+'|')
        lines+=['','Existing dictionary targets missed by raw BGE: `'+str(natural['B']['metrics']['missed_existing_components'])+'`. Decomposed BGE: `'+str(natural['C']['metrics']['missed_existing_components'])+'`. Hybrid: `'+str(e['metrics']['missed_existing_components'])+'`.','',
            '## Original BGE Top-20','',candidate_table(natural['B']['raw_results'],catalog),'','## Decomposed BGE queries and results','']
        for trace in natural['C']['queries']:
            if trace['relation']=='original':continue
            lines += [f"### {trace['query']} ({trace['relation']})",'',candidate_table(trace['results'],catalog),'']
        lines+=['## Candidate selection','', '|Entry / sense|Decision|Reason / components|','|---|---|---|']
        chosen={v['record_id'] for v in comp['selected'].values()}
        for hit in e['candidates']+e['rejected_candidates']:
            r=catalog[hit['id']]
            status='accepted in composition' if hit['id'] in chosen else ('rejected' if hit.get('rejection') else 'unselected / unjudged')
            lines.append('|'+ '|'.join(map(cell,[str(r.get('entry_id'))+' / '+r.get('zh',''),status,hit.get('rejection') or str(hit.get('supported_components',[]))]))+'|')
        lines+=['','## Verified inventory targets','']
        for t in c['expected_components']:
            lines.append(f"- {t['key']}: {', '.join(t['senses'])}; {t['gold_status']}; entries: "+', '.join(sorted({g['entry_id'] for g in t['gold']})))
        lines+=['',f"[All exact lookup results, query-level provenance, scores, costs and metrics]({c['id']}.json). [Complete original records and linked notations](records.jsonl).",'']
        (root/(c['id']+'.md')).write_text('\n'.join(lines))
    lines=['# Semantic decomposition with real BGE retrieval','',
        'This experiment tests whether words present in the dictionary can be recovered, and whether those words support a complete semantic frame. A component hit does not establish a complete translation.','',
        f"Execution: **{meta['status']}**. The run covers {meta['cases']} expressions, {len({d['case']['family'] for d in docs})} annotated families and 15 compositional holdouts. No historical BGE results were used.",'',
        '[60 challenge candidates in Pinyin/IPA](challenge-translations.md), [Chinese findings](SUMMARY.zh.md), and [six worked anchors](worked-examples.md).','',
        '## Reproduction','',f"Dictionary revision: `{meta['index_manifest']['metadata']['repository_revision']}`. Model: `{meta['model']['model']}` at `{meta['model']['revision']}`; weights SHA-256 `{meta['model']['weights_sha256']}`.",'',
        f"Complete index: {meta['index_manifest']['lexical_entry_count']:,} dictionary entries, {meta['index_manifest']['lexical_attestation_count']:,} attestations, {meta['index_manifest']['record_count']:,} total records and {meta['index_manifest']['unique_texts']:,} unique embedded texts. Static shards use the same source revision.",'',
        '[Commands](commands.txt), [build log](build.log), [evaluation log](evaluation.log), [full model/index manifest and metrics](results.json), [test output](tests.log), [grammar QA](grammar-qa.log). Model weights and the generated full index are ignored local assets.','',
        '## Design and denominators','',
        'A = original literal exact lookup; B = original real BGE; C = shared plan with real BGE; D = shared plan with static exact shards; E = combined candidates with component, role and source checks. Planning sees the expression and context, never gold IDs. Productive rules parse new arguments, relative clauses, spatial frames, negation and TAM. Conventional opaque meanings use a small lexical bridge; an explicit Interpretation API handles other contextual or opaque meanings. The parser preserves ordinary context text but does not claim to understand arbitrary prose.','',
        'The dataset was independently annotated in Chinese and resolved against the canonical dictionary and survey inventory. An exploratory run prompted inclusion of separately identified survey records; gold was frozen again before the final comparison. Static D has dictionary witnesses only, so survey-only targets measure an asset-coverage limitation as well as retrieval. A verified component has one or more sense-linked dictionary attestation IDs or stable survey point/serial IDs with original file/row citations; matching any alternative counts as recovering that target. Recall@K below is macro recall of those verified component targets. Conventional entry-ID recall and component MRR are also in results.json. Unverified targets have no numerical recall denominator and still block a complete-construction claim. These are source-inventory judgments, not native-speaker judgments.','',
        'Meaning scores check frame features and semantic roles against independent annotations. Construction coverage additionally requires all required lexical components and compatible Northern source evidence. Neither score certifies fluent Tujia. Native origin cannot be inferred systematically from the available etymology fields: native vocabulary utilization is null, and the report gives verified source-lexeme utilization and explicit Chinese insertions separately. Missing lexical slots are counted, so zero Chinese insertions cannot conceal an incomplete draft.','',
        'The 15 holdouts are outside concepts.json and the planner’s expression bridges. They test compositional rule transfer within this task, not an externally blinded benchmark. Challenge cases were used to debug general rules; holdout limitations are reported.','']
    for budget,conf in meta['summary'].items():
        lines += [f'## {budget} budget','',meta['budgets'][budget]+'.','',
            '|Route|R@1|R@5|R@10|R@20|MRR|Complete components|Construction|Missed existing targets|Queries / encodings|Candidate rows|Seconds|',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|']
        for route,d in conf.items():
            m=d['overall'];cost=m['cost']
            lines.append('|'+ '|'.join(map(cell,[route,*[pct(m['recall'][str(k)]) for k in [1,5,10,20]],f"{m['mrr']:.3f}",m['full_component_cases'],m['construction_cases'],m['missed_existing_targets'],f"{cost['query_count']} / {cost['query_encodings']}",cost['candidate_count'],f"{cost['seconds']:.2f}"]))+'|')
        lines+=['','|Family|Cases|Raw B R@20|C R@20|D R@20|E R@20|E construction|','|---|---:|---:|---:|---:|---:|---:|']
        for family,entry in conf['B']['families'].items():
            lines.append('|'+ '|'.join(map(cell,[family,entry['cases'],*[pct(conf[r]['families'][family]['recall']['20']) for r in 'BCDE'],conf['E']['families'][family]['construction_cases']]))+'|')
        lines+=['', 'Holdout R@20: '+', '.join(f"{r} {pct(conf[r]['splits']['holdout']['recall']['20'])}" for r in 'ABCDE')+'.','']
    lines+=['## Worked cases and errors','', '|Expression|Raw B R@20|C R@20|E R@20|E lexical slots / construction|Audit|','|---|---:|---:|---:|---|---|']
    for d in docs:
        c=d['case'];rs={r['route']:r for r in d['routes'] if r['budget']=='natural'}
        comp=rs['E']['composition']
        lines.append('|'+ '|'.join(map(cell,[c['expression'],*[pct(rs[r]['metrics']['recall']['20']) for r in 'BCE'],f"{comp['lexical_complete']} / {comp['construction_supported']}",f"[{c['id']}]({c['id']}.md)"]))+'|')
    lines+=['','## Concrete retrieval changes','',
        'For 路人, the original BGE query ranks 修路工 (w1266, roadman) first at cosine 0.553560: a road worker is a false friend for a passerby. Component queries recover 走 (w949) and 路 (w1224), supporting the proposed productive agent expression là hxí mā /la⁵¹ ɣɨ²⁴ ma⁵⁵/. The incidental-passerby nuance remains broader in a general walker description.', '',
        'For 经济损失, the original first hit is 经济 at 0.465071. The decomposed route retrieves money w2331 and the loss-event entry stedt-rn-454677 (吃亏；受损失); the 受损失 query scores that event at 0.569226. The draft therefore retains both money and loss. The recorded form qi²kui¹ is source vocabulary; romanization alone does not establish native etymology.', '',
        'For 令人费解, the 理解 query retrieves stedt-rn-289131 at 0.665023, with other 懂／明白 alternatives. The plan supplies negative ability tā tī rather than substituting 不知道. Combining different Northern lexical and grammatical sources remains a separate compatibility check.', '',
        'Agent/patient control: 审判别人的人 uses a human-agent ma template; 被别人审判的人 uses an agent-containing relative clause with an explicit patient head. The drafts differ, and the role graphs keep opposite gaps. A source-verified 审判 predicate is still pending, so neither full phrase is scored as an established translation.', '']
    lines+=['','## Limits and failure taxonomy','',
        '- A missing gold attestation can be a retrieval or selection miss. For 砍柴工具, C actually returns entry w1076 with the 柴火 sense, but the frozen target is the 柴/木 witness and the exact sense selector rejects the variant. This is an attestation/sense-selection failure, not evidence that BGE failed to retrieve the entry. Per-case missed_existing_components uses this strict witness-level convention.',
        '- Sense ambiguity: the odor records glossed 气味／闻 have verbal POS or undivided senses. Incense and the act of smelling are rejected; the survey provides noun 气味 at points 60756 and 60823; its use in a Longshan phrase still requires a locality decision.',
        '- Argument drift: letter 信 differs from believe 信, and classifier 瓶 cannot supply a bottle noun. Patient relatives keep a different gap from agent relatives; suffix choice alone does not encode voice.',
        '- Incomplete event: money alone cannot cover financial loss; drink requires a drinking predicate and object construction rather than water alone; road alone cannot cover a passerby.',
        '- Grammatical realization: source-compatible components can still lack a verified nominalizer tone, stem allomorph, recent-completion/state choice or numeral/classifier. Audit drafts expose these slots and retain the full semantic graph.',
        '- Generalization: generic odor/sound drops pleasantness, floral origin or unwantedness. The plan records this drift even when lexical retrieval succeeds.',
        '- Inventory uncertainty: absent verified gold means pending review, not proof that Tujia lacks an expression. The report does not turn model scores into evidence of grammaticality.',
        '', 'The per-case files contain the original Top-20, every decomposed BGE Top-20 with actual cosine scores, selected and rejected senses, dictionary and attestation IDs, source/locality/notation metadata, grammatical basis and all five routes under each budget.','']
    (root/'README.md').write_text('\n'.join(lines))

if __name__=='__main__':main()
