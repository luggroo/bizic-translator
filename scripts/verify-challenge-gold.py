#!/usr/bin/env python3
"""Resolve preannotated semantic targets against the canonical source inventory.

Never uses model neighbors or planner output. The evidence file can be reviewed
before inference; unresolved senses remain qualitative, outside recall counts.
"""
import argparse
import json
import re
from pathlib import Path

from tujia_lex.data import lexical_records, source_catalog, survey_records
from tujia_lex.static import source_priority


def inventory_matches(record, target):
    zh = record['zh']
    # The source explicitly leaves these senses undivided: no verified noun target.
    if '原义未细分' in zh:
        return False
    keys = {s.strip() for s in re.split(r'[;；、/／，,\n]+', zh)} | {zh}
    if not keys.intersection(target['senses']):
        return False
    pos = (record.get('pos') or '').lower()
    if target['role'] == 'predicate' and (pos.startswith(('n','cl')) or 'suff' in pos):
        return False
    if target['role'] in {'patient','landmark','location','head','agent'} and (pos.startswith(('v','cl')) or 'suff' in pos):
        return False
    return record['dialect'] == 'north'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True)
    p.add_argument('--dataset', default='tests/data/semantic-compositional-challenge.json')
    a=p.parse_args()
    catalog,aliases=source_catalog(a.repo)
    records=lexical_records(Path(a.repo)/'site/dictionary.json.gz',catalog,aliases)
    records += survey_records(a.repo)[0]
    data=json.loads(Path(a.dataset).read_text())
    data['gold_scope']='Verified dictionary senses and separately identified survey elicitation records. Survey gold IDs are stable point:serial retrieval IDs, with original file/row citations; no claim of a merged dictionary entry ID.'
    for case in data['cases']:
        for target in case['expected_components']:
            matches=sorted([r for r in records if inventory_matches(r,target)], key=lambda r:(source_priority(r),r['id']))
            target['gold_status']='verified_inventory' if matches else 'pending_review'
            target['gold']=[{'entry_id':r['entry_id'], 'record_id':r['id'], 'zh':r['zh'],'en':r['en'],
                            'pos':r['pos'], 'forms':r['forms'], 'attestation_ids':([s['attestation_id'] for s in r['sources']] if r['record_type']=='lexical_sense' else [r['id']]),
                            'record_type':r['record_type'],'citation':r['citation'],
                            'raw_row':r.get('raw_row'),
                            'sources':r['sources'], 'dialect':r['dialect'], 'locations':r['locations']} for r in matches]
        case['gold_status']='verified_inventory' if all(t['gold'] for t in case['expected_components']) else 'partial_or_pending'
    Path(a.dataset).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    targets=[t for c in data['cases'] for t in c['expected_components']]
    print(json.dumps({'cases':len(data['cases']), 'verified_components':sum(bool(t['gold']) for t in targets),
                      'pending_components':[(c['expression'],t['senses']) for c in data['cases'] for t in c['expected_components'] if not t['gold']]},ensure_ascii=False))

if __name__=='__main__': main()
