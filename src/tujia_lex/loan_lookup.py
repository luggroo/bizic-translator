"""Look up final Tujia loan readings; runtime needs only the compiled table."""
from pathlib import Path
from functools import lru_cache
import argparse
import gzip
import json
import re

D = Path(__file__).with_name('loan_data')

@lru_cache(maxsize=1)
def readings():
    return json.loads(gzip.decompress((D / 'readings.json.gz').read_bytes()))

@lru_cache(maxsize=1)
def local_table():
    return json.loads(gzip.decompress((D / 'local-readings.json.gz').read_bytes()))

def local_readings(word, register=None):
    """Look up character witnesses. Each distinct reading prefers Jishou, then Chongqing."""
    if not word or not all('\u3400' <= c <= '\u9fff' or '\U00020000' <= c <= '\U000323af' for c in word):
        raise ValueError('Pass one Han-character word')
    if register not in (None, '文', '白'):
        raise ValueError('register must be 文 or 白')
    table = local_table()
    results = []
    for position, char in enumerate(word):
        choices, readings_by_ipa = [], {}
        for row in table['characters'].get(char, []):
            readings_by_ipa.setdefault(row['ipa'], []).append(row)
        for ipa, rows in readings_by_ipa.items():
            # A matching Chongqing sound can corroborate an IPA form. Register
            # and usage belong to the source that actually identifies them.
            local = [r for r in rows if r['city'] == 'jishou'] or rows
            tags = list(dict.fromkeys(r['register'] for r in local if r['register'])) or ['']
            for tag in tags:
                if register and tag != register:
                    continue
                primary = next(r for r in local if r['register'] == tag)
                witnesses = []
                for r in rows:
                    if r['city'] == primary['city'] and r['register'] not in ('', tag):
                        continue
                    source_id = r.get('source', r['city'])
                    source = table['sources'][source_id]
                    witnesses.append(dict(city=source['label'], source=source_id,
                                          title=source.get('title', '《汉字音典》' + source['label'] + '字表'),
                                          page=r.get('page'), graph=r['graph'], register=r['register'] or None,
                                          note=r['note'], comment=r.get('comment', ''),
                                          source_url=source['url'] + '#L' + str(r['line'])))
                primary_source = table['sources'][primary.get('source', primary['city'])]
                choices.append(dict(city=primary_source['label'], source_graph=primary['graph'],
                                    source_reading=ipa, register=tag or None, note=primary['note'],
                                    input_key=primary['key'], north_spelling=primary['north_spelling'],
                                    page=primary.get('page'), witnesses=witnesses,
                                    source_url=primary_source['url'] + '#L' + str(primary['line'])))
        results.append(dict(position=position, character=char, readings=choices))
    return dict(word=word, register=register, characters=results)

def sense_matches(character, gloss, context):
    expanded = gloss.replace('～', character).replace('~', character)
    return bool(context) and any(
        token in context or context in token
        for token in re.findall(r'[\u3400-\u9fff]{2,}', expanded)
    )

def lookup(word, target='north', sense='', choices=None):
    if target not in ('north', 'south'):
        raise ValueError('target must be north or south')
    if not word or not all('\u3400' <= c <= '\u9fff' or '\U00020000' <= c <= '\U000323af' for c in word):
        raise ValueError('Pass one Han-character word')
    base = dict(word=word, target=target, ipa=None, romanization=None, display=word)
    choices = choices or {}
    table = readings()[target]
    missing = [dict(position=i, character=c) for i, c in enumerate(word) if c not in table]
    if missing:
        return dict(base, status='missing-character', missing=missing)
    selected, details, unresolved = [], [], []
    for i, c in enumerate(word):
        candidates = table[c]
        choice = choices.get(i, choices.get(str(i)))
        if choice:
            candidates = [r for r in candidates if choice in (r['romanization'], r['ipa'])]
        else:
            matches = [r for r in candidates if sense_matches(c, r.get('sense', ''), sense or word)]
            if matches:
                candidates = matches
        if candidates:
            priority = min(r.get('priority', 0) for r in candidates)
            candidates = [r for r in candidates if r.get('priority', 0) == priority]
        pairs = {(r['romanization'], r['ipa']) for r in candidates}
        visible = [dict(romanization=p, ipa=ipa, senses=sorted({r.get('sense', '') for r in candidates if r['ipa'] == ipa} - {''})) for p, ipa in sorted(pairs)]
        if len(pairs) != 1:
            unresolved.append(i)
            details.append(dict(position=i, character=c, status='invalid-choice' if choice else 'ambiguous', candidates=visible))
            continue
        chosen = visible[0]
        selected.append(chosen)
        details.append(dict(position=i, character=c, status='resolved', reading=chosen))
    if unresolved:
        return dict(base, status='needs-selection', unresolved_positions=unresolved, characters=details)
    return dict(base, status='resolved', ipa=' '.join(r['ipa'] for r in selected),
                romanization=' '.join(r['romanization'] for r in selected),
                display=' '.join(r['romanization'] for r in selected), characters=details)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('word')
    p.add_argument('--target', choices=['north', 'south'], default='north')
    p.add_argument('--sense', default='')
    p.add_argument('--local-readings', action='store_true', help='Look up modern character readings in Jishou and Chongqing')
    p.add_argument('--register', choices=['文', '白'], help='Only include explicitly labelled literary or colloquial readings')
    p.add_argument('--choices', default='{}', help='Position to final Pinyin or IPA, e.g. {"0":"lán"}')
    a = p.parse_args()
    try:
        result = (local_readings(a.word, a.register) if a.local_readings or a.register else
                  lookup(a.word, a.target, a.sense, json.loads(a.choices)))
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
