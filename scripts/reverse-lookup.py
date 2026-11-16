#!/usr/bin/env python3
"""Find original witnesses and alternative word boundaries in Northern Tujia."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from tujia_lex.pronunciation import PronunciationLookup, load_static


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--query', action='append', required=True,
                   help='Repeat for a batch; one local dictionary session is reused')
    p.add_argument('--notation', choices=('accent', 'ye', 'ipa'), default='accent')
    p.add_argument('--directory', type=Path, default=ROOT/'skills/translate-tujia/lexicon')
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--max-cost', type=float, default=2.)
    p.add_argument('--affix-tone', action='store_true',
                   help='Allow tone differences for entries explicitly marked as bound affixes')
    args = p.parse_args()
    if not 1 <= len(args.query) <= 32:
        p.error('Use batches of 1..32 spans')
    try:
        reader = PronunciationLookup(load_static(args.directory))
        results = [reader.search(q, args.notation, args.limit, args.max_cost, args.affix_tone)
                   for q in args.query]
    except (ValueError, OSError) as error:
        p.error(str(error))
    manifest = json.loads((args.directory/'manifest.json').read_text())
    print(json.dumps({'mode': 'Skill-based', 'embedding_run': False,
                      'dictionary_revision': manifest.get('revision'),
                      'dictionary_sha256': manifest.get('source_sha256'),
                      'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
