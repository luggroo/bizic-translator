"""Gold-only evaluation; annotations are never passed into retrieval/reranking."""
from __future__ import annotations


def evidence_ids(record):
    return {record['id']} | {a.get('id', a.get('attestation_id')) for a in record.get('attestations', [])} | {
        s.get('attestation_id') for s in record.get('sources', []) if s.get('attestation_id')}


def grade(case, result, composition):
    candidates = result['candidates']
    targets = case['expected_components']
    verified = [t for t in targets if t['gold']]
    gold_sets = [{aid for g in t['gold'] for aid in g['attestation_ids']} for t in verified]
    ranks = [next((n for n,r in enumerate(candidates,1) if evidence_ids(r) & gold), None) for gold in gold_sets]
    recalls = {str(k): sum(r is not None and r <= k for r in ranks) / len(ranks) if ranks else None for k in [1,5,10,20]}
    gold_entries = {g['entry_id'] for t in verified for g in t['gold']}
    entry_recalls = {str(k): len(gold_entries & {r.get('entry_id') for r in candidates[:k]}) / len(gold_entries) if gold_entries else None for k in [1,5,10,20]}
    first = min([r for r in ranks if r] or [0])
    a = result['plan']['analysis']
    feature_checks = {k: a['features'].get(k) == v for k,v in case.get('expected_features', {}).items()}
    role_checks = {k: a['roles'].get(k) == v for k,v in case.get('expected_roles', {}).items()}
    feature_ok, roles_ok = all(feature_checks.values()), all(role_checks.values())
    retrieved = sum(r is not None for r in ranks)
    full = len(verified) == len(targets) and retrieved == len(targets)
    relevant_ids = set().union(*gold_sets) if gold_sets else set()
    judged = [r for r in candidates if evidence_ids(r) & relevant_ids]
    # Only explicit negative controls are false-positive labels. Other neighbors
    # are unjudged, not automatically false merely because gold is incomplete.
    controls = [r for r in candidates if r.get('rejection')]
    selected = composition['selected']
    selected_supported = sum(any(v['attestation_id'] in {aid for g in t['gold'] for aid in g['attestation_ids']} or v['record_id'] in {aid for g in t['gold'] for aid in g['attestation_ids']} for v in selected.values()) for t in targets)
    lexical_target_count = len(targets)
    losses = bool(composition['meaning_losses'])
    return {'gold_target_count': len(verified), 'pending_target_count': len(targets)-len(verified),
        'recall': recalls, 'entry_recall': entry_recalls,
        'mrr': (1/first if first else 0) if ranks else None,
        'component_mrr': sum(1/r if r else 0 for r in ranks)/len(ranks) if ranks else None,
        'component_ranks': {t['key']:r for t,r in zip(verified,ranks)},
        'semantic_component_coverage': retrieved / len(verified) if verified else None,
        'all_required_components_retrieved': full,
        'construction_coverage': full and composition['construction_supported'] and feature_ok and roles_ok,
        'meaning_preservation': {'features': feature_checks, 'roles': role_checks,
            'family': a['family'] == case['family'],
            'frame_preserved': feature_ok and roles_ok and a['family'] == case['family'],
            'complete_meaning_supported': full and feature_ok and roles_ok and not losses,
            'generalization_loss': losses,
            'status': 'automatic frame/evidence proxy; no native-speaker grammaticality judgement'},
        'false_positive_controls_at20': len(controls),
        'judged_relevant_candidates': len(judged), 'unjudged_candidates': len(candidates)-len(judged)-len(controls),
        'selected_verified_lexical_targets': selected_supported,
        'source_lexeme_utilization': selected_supported / lexical_target_count,
        'native_vocabulary_utilization': None,
        'native_vocabulary_reason': 'lexicon has no systematic etymology labels; transcription does not prove native origin',
        'chinese_insertions': sum(any('\u3400' <= ch <= '\u9fff' for ch in v['term']) for v in selected.values()),
        'unresolved_lexical_slots': len(composition['missing_components']),
        'surface_complete': composition['surface_complete'],
        'missed_existing_components': [t['key'] for t,r in zip(verified,ranks) if not r]}


def aggregate(rows):
    def avg(values):
        vals = [x for x in values if x is not None]
        return sum(vals)/len(vals) if vals else None
    return {'cases':len(rows), 'gold_cases':sum(r['metrics']['gold_target_count'] > 0 for r in rows),
        'gold_targets':sum(r['metrics']['gold_target_count'] for r in rows),
        'recall':{str(k):avg([r['metrics']['recall'][str(k)] for r in rows]) for k in [1,5,10,20]},
        'entry_recall':{str(k):avg([r['metrics']['entry_recall'][str(k)] for r in rows]) for k in [1,5,10,20]},
        'mrr':avg([r['metrics']['mrr'] for r in rows]),
        'component_mrr':avg([r['metrics']['component_mrr'] for r in rows]),
        'component_coverage':avg([r['metrics']['semantic_component_coverage'] for r in rows]),
        'full_component_cases':sum(r['metrics']['all_required_components_retrieved'] for r in rows),
        'construction_cases':sum(r['metrics']['construction_coverage'] for r in rows),
        'frame_preserved_cases':sum(r['metrics']['meaning_preservation']['frame_preserved'] for r in rows),
        'meaning_supported_cases':sum(r['metrics']['meaning_preservation']['complete_meaning_supported'] for r in rows),
        'control_false_positives':sum(r['metrics']['false_positive_controls_at20'] for r in rows),
        'source_lexeme_utilization':avg([r['metrics']['source_lexeme_utilization'] for r in rows]),
        'native_vocabulary_utilization':None,
        'chinese_insertions':sum(r['metrics']['chinese_insertions'] for r in rows),
        'missed_existing_targets':sum(len(r['metrics']['missed_existing_components']) for r in rows),
        'cost':{k:sum(r['cost'][k] for r in rows) for k in ['query_count','engine_calls','query_encodings','candidate_count','unique_candidates','requested_candidates','seconds']}}
