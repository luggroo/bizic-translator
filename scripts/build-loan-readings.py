"""Compile raw dialect data and historical homophones into final lookup tables."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import sys
from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tujia_lex import loan_build as seed

ORDER = ('hongwu-sinica', 'hongwu-jian', 'menggu', 'zhongyuan')
TO_SIMPLE, TO_TRAD = OpenCC('t2s'), OpenCC('s2t')

def variants(c):
    return {x for x in (c, TO_SIMPLE.convert(c), TO_TRAD.convert(c)) if len(x) == 1}

def direct_readings(target):
    table = {}
    for c in sorted(seed.assets()[0]['aliases']):
        rs = seed.character_candidates(c, target)
        ranks = {}
        out = []
        for raw, mapped in rs:
            if not mapped:
                continue
            rank = ranks.setdefault(raw[0], len(ranks))
            # Meanings are kept for lexical disambiguation, not as provenance.
            sense_forms = {raw[2], TO_SIMPLE.convert(raw[2]), TO_TRAD.convert(raw[2])} - {''}
            sense_forms |= {gloss.replace(alias, c) for gloss in list(sense_forms) for alias in variants(c)}
            senses = sorted(sense_forms)
            row = dict(romanization=mapped['romanization'], ipa=mapped['ipa'].replace('ɲ', 'ȵ'), sense='；'.join(senses), priority=rank)
            if row not in out:
                out.append(row)
        if out:
            table[c] = out
    return table

def anchors(target, table):
    out = {}
    for c in table:
        r = seed.lookup(c, target)
        if r['status'] == 'resolved':
            out[c] = (r['romanization'], r['ipa'].replace('ɲ', 'ȵ'))
    return out

def compile_target(target, books):
    table = direct_readings(target)
    original = set(table)
    direct = anchors(target, table)
    audit = {}
    stats = {'direct_characters': len(table), 'direct_unambiguous_anchors': len(direct)}
    for book in ORDER:
        votes = defaultdict(lambda: defaultdict(set))
        group_refs = defaultdict(set)
        memberships = defaultdict(set)
        for group_id, group in enumerate(books[book], 1):
            for c in group:
                memberships[c].add(group_id)
        for group_id, group in enumerate(books[book], 1):
            donors = {c: direct[c] for c in group if c in direct and len(memberships[c]) == 1}
            if not donors:
                continue
            for original_char in group:
                for c in variants(original_char):
                    if c in table:
                        continue
                    for donor, pronunciation in donors.items():
                        votes[c][pronunciation].add(donor)
                    group_refs[c].add(group_id)
        added, ambiguous = 0, 0
        for c, candidates in sorted(votes.items()):
            # Count independent character witnesses, rather than aliases or repeated rows.
            strongest = max(map(len, candidates.values()))
            winners = sorted(p for p, ds in candidates.items() if len(ds) == strongest)
            table[c] = [dict(romanization=p, ipa=ipa, sense='', priority=0) for p, ipa in winners]
            audit[c] = {'book': book, 'groups': sorted(group_refs[c]), 'candidates': [dict(romanization=p, ipa=ipa, donors=sorted(ds), votes=len(ds)) for (p, ipa), ds in sorted(candidates.items())], 'selected': [list(p) for p in winners]}
            added += 1
            ambiguous += len(winners) > 1
        stats[book] = {'added_characters': added, 'ambiguous_characters': ambiguous}
    stats['total_characters'] = len(table)
    stats['total_readings'] = sum(len({r['ipa'] for r in rows}) for rows in table.values())
    stats['added_characters'] = len(table) - len(original)
    return dict(sorted(table.items())), audit, stats

def build():
    source = ROOT / 'data/loan-sources/historical-homophones.json.gz'
    books = json.loads(gzip.decompress(source.read_bytes()))
    tables, audit, stats = {}, {}, {}
    for target in ('north', 'south'):
        tables[target], audit[target], stats[target] = compile_target(target, books)
        # A simple user/tool-readable table, with no source or derivation columns.
        with (ROOT / f'data/loan-readings-{target}.tsv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t', lineterminator='\n')
            writer.writerow(['汉字', '调号拼音', 'IPA', '分义'])
            for c, rows in tables[target].items():
                seen = set()
                for r in rows:
                    values = (c, r['romanization'], r['ipa'], r['sense'])
                    if values not in seen:
                        writer.writerow(values)
                        seen.add(values)
    encoded = json.dumps(tables, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(encoded, mtime=0)
    (ROOT / 'src/tujia_lex/loan_data/readings.json.gz').write_bytes(packed)
    bundle = ROOT / 'skills/translate-tujia'
    (bundle / 'assets').mkdir(exist_ok=True)
    (bundle / 'scripts').mkdir(exist_ok=True)
    (bundle / 'assets/loan-readings.json.gz').write_bytes(packed)
    standalone = (ROOT / 'src/tujia_lex/loan_lookup.py').read_text().replace("D = Path(__file__).with_name('loan_data')", "D = Path(__file__).resolve().parents[1] / 'assets'").replace("(D / 'readings.json.gz')", "(D / 'loan-readings.json.gz')")
    (bundle / 'scripts/lookup-loan.py').write_text(standalone)
    # Build-time evidence is deliberately separate; runtime never imports it.
    audit_file = ROOT / 'data/loan-sources/homophone-build-audit.json.gz'
    audit_file.write_bytes(gzip.compress(json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    report = {'source_order': list(ORDER), 'homophones_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'readings_sha256': hashlib.sha256(encoded).hexdigest(), 'targets': stats, 'policy': 'Direct readings first; same-tone historical homophones fill gaps. Exclude donors with multiple historical groups (a modern reading may belong to another historical sense). Use only original unambiguous anchors, never inferred donors. Independent donor majority; ties remain multiple candidates.'}
    (ROOT / 'data/loan-sources/compiled-readings-summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    build()
