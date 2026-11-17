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
    p.add_argument('--choices', default='{}', help='Position to final Pinyin or IPA, e.g. {"0":"lán"}')
    a = p.parse_args()
    try:
        result = lookup(a.word, a.target, a.sense, json.loads(a.choices))
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
