"""Local, bounded pronunciation candidates for reading Northern Tujia.

Costs rank transcription edits, not semantic similarity or translation accuracy.
Original spellings, tones, witnesses and word-boundary alternatives stay visible.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import re
import unicodedata

ACCENTS = {'\u0304': 'H', '\u0301': 'R', '\u030c': 'L', '\u0300': 'F'}
YE_TONES = {'x': 'H', 'f': 'R', 'r': 'L', 'v': 'F'}
IPA_TONES = {'55': 'H', '51': 'F', '53': 'F', '35': 'R', '24': 'R', '21': 'L'}
SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
SYLLABLE = re.compile(r"(?:[bcdfghjklmnpqrstvwxyz]{1,3})?[aeiouıü]+(?:(?:ng|n)(?![aeiouıü]))?")


@dataclass(frozen=True)
class Syllable:
    body: str
    tone: str | None
    raw_tone: str | None = None


def parse(text, notation='accent'):
    """Require the caller's notation; do not infer Ye tone letters from bare text."""
    text = text.strip().casefold().strip('/').strip()
    if notation == 'ipa':
        text = re.sub(r'\s+', '', text.translate(SUPERSCRIPTS))
        parts = re.findall(r'([^0-9]+)([0-9]+)', text)
        if not parts or ''.join(a+b for a, b in parts) != text:
            raise ValueError('IPA input needs explicit tone digits on every syllable')
        return tuple(Syllable(a, IPA_TONES.get(b, b), b) for a, b in parts)
    if notation == 'ye':
        text = re.sub(r"[\s\-·]", '', text)
        parts = re.findall(r"([a-z]*?[aeiouıü][a-z]*?)([xfrv])", text)
        if not parts or ''.join(a+b for a, b in parts) != text:
            raise ValueError('Unsupported or incompletely tone-marked Ye input; supply accent or IPA')
        return tuple(Syllable(a, YE_TONES[b]) for a, b in parts)
    if notation != 'accent':
        raise ValueError('notation must be accent, ye or ipa')
    chunks = [x for x in re.split(r'[\s\-·]+', text) if x]
    if len(chunks) > 1:
        return tuple(unit for chunk in chunks for unit in parse(chunk, notation))
    text = text.strip('-')
    base, marks = '', {}
    for char in unicodedata.normalize('NFD', text):
        if char in ACCENTS:
            if not base or len(base)-1 in marks:
                raise ValueError('Invalid tone-mark placement')
            marks[len(base)-1] = ACCENTS[char]
        elif char == '\u0308' and base.endswith('u'):
            base = base[:-1] + 'ü'
        elif unicodedata.category(char) == 'Mn':
            raise ValueError('Unsupported diacritic; keep the original and use IPA')
        elif char in ' -·':
            continue
        else:
            base += char
    parts = list(SYLLABLE.finditer(base))
    if not parts or ''.join(m.group() for m in parts) != base:
        raise ValueError('Unsupported spelling; supply an explicitly supported notation')
    result = []
    for match in parts:
        tones = [v for k, v in marks.items() if match.start() <= k < match.end()]
        if len(tones) > 1:
            raise ValueError('Ambiguous syllable boundary; insert spaces or supply IPA')
        result.append(Syllable(match.group(), tones[0] if tones else None))
    return tuple(result)


def zero_onset(body):
    # Only spelling conventions for initial i/u; this is not a change to source data.
    if body.startswith('yi'):
        return body[1:]
    if body.startswith('y') and len(body) > 1 and body[1] in 'aeou':
        return 'i' + body[1:]
    if body.startswith('wu'):
        return body[1:]
    if body.startswith('w') and len(body) > 1 and body[1] in 'aeio':
        return 'u' + body[1:]
    return body


def body_variants(body, ipa=False):
    result = {body: ()}
    base = body if ipa else zero_onset(body)
    if base != body:
        result[base] = ('zero-onset spelling',)
    for form, history in list(result.items()):
        onset = 'ɣ' if ipa else 'hx'
        if form.startswith(onset) and len(form) > len(onset):
            result.setdefault(form[len(onset):], history + ('hx onset absent',))
        elif form and form[0] in ('aeiouɨɯɛ' if ipa else 'aeiouıü'):
            result.setdefault(onset+form, history + ('hx onset present',))
        velar = r'^(kʰ|k|g|ŋ|x|ɣ)(i|ei)$' if ipa else r'^(ng|hx|g|k|h)(i|ei)$'
        match = re.fullmatch(velar, form)
        if match:
            other = match[1] + ('ei' if match[2] == 'i' else 'i')
            result.setdefault(other, history + ('i/ei after velar',))
    return result


def tone_changes(query, candidate, affix=False):
    pair_positions = set()
    for i in range(len(query)-1):
        a = tuple(x.tone for x in query[i:i+2])
        b = tuple(x.tone for x in candidate[i:i+2])
        if {a, b} in ({('L', 'H'), ('R', 'H')}, {('R', 'R'), ('R', 'H')}):
            pair_positions.update(j for j in (i, i+1) if query[j].tone != candidate[j].tone)
    cost, changes = 0., []
    for i, (left, right) in enumerate(zip(query, candidate)):
        if left.tone == right.tone:
            if left.raw_tone and right.raw_tone and left.raw_tone != right.raw_tone:
                cost += .1
                changes.append(f'syllable {i+1}: source tone values {left.raw_tone}/{right.raw_tone}')
            continue
        if left.tone is None or right.tone is None:
            cost += .25
            changes.append(f'syllable {i+1}: tone unspecified')
        elif {left.tone, right.tone} == {'H', 'F'}:
            cost += .5
            changes.append(f'syllable {i+1}: high/falling tone')
        elif i in pair_positions:
            cost += .6
            changes.append(f'syllable {i+1}: 21-55/35-55 or 35-35/35-55 pattern')
        elif affix:
            cost += .8
            changes.append(f'syllable {i+1}: attested affix tone candidate')
        else:
            return None
    return cost, changes


def load_static(directory):
    """One local scan per session; no public query-time endpoint or changed shards."""
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest.get('format') != 2:
        raise ValueError('Expected format-2 static dictionary')
    records, seen = [], set()
    for infos in manifest['buckets'].values():
        for info in infos:
            name = info['path']
            if Path(name).name != name or '..' in name:
                raise ValueError('Unsafe shard path')
            data = (directory/name).read_bytes()
            if len(data) != info['bytes'] or hashlib.sha256(data).hexdigest() != info['sha256']:
                raise ValueError('Shard checksum mismatch: '+name)
            for line in data.decode().splitlines():
                record = dict(zip(manifest['record_fields'], json.loads(line)['r']))
                aid = record['attestation_id']
                if aid in seen:
                    continue
                seen.add(aid)
                source = manifest.get('sources', {}).get(record['source'], {})
                records.append({**record, 'canonical_source': source.get('canonical_id', record['source'])})
    return records


class PronunciationLookup:
    def __init__(self, records):
        self.index = {'accent': {}, 'ipa': {}}
        self.unsupported_forms = 0
        for record in records:
            if '北' not in record.get('dialect', '') or '南' in record.get('dialect', ''):
                continue
            for notation in self.index:
                for form in record.get('notations', {}).get(notation, []):
                    if isinstance(form, dict):
                        form = form['text']
                    for variant in re.split(r'\s*[/~～]\s*', form.strip('/')):
                        try:
                            units = parse(variant.lstrip('-'), notation)
                        except ValueError:
                            self.unsupported_forms += 1
                            continue
                        if not 1 <= len(units) <= 8:
                            continue
                        bodies = tuple(u.body if notation == 'ipa' else zero_onset(u.body) for u in units)
                        item = (units, variant, record)
                        self.index[notation].setdefault(bodies, []).append(item)

    def search(self, text, notation='accent', limit=30, max_cost=2., affix=False):
        if not 1 <= len(text) <= 120 or not 1 <= limit <= 30 or not 0 <= max_cost <= 3:
            raise ValueError('Invalid query, result limit or edit budget')
        units = parse(text, notation)
        if len(units) > 8:
            raise ValueError('Split the input into spans of at most eight syllables')
        kind = 'ipa' if notation == 'ipa' else 'accent'

        @lru_cache(maxsize=64)
        def pieces(start, end):
            query = units[start:end]
            found = []
            variants = [body_variants(u.body, kind == 'ipa') for u in query]
            combinations = sorted(itertools.product(*(list(v.items()) for v in variants)),
                                  key=lambda combo: sum(bool(history) for body, history in combo))
            for combo in combinations[:64]:
                bodies = tuple(body if kind == 'ipa' else zero_onset(body) for body, history in combo)
                edits = [f'syllable {i+1}: {change}' for i, (body, history) in enumerate(combo) for change in history]
                base_cost = .4 * len(edits)
                for target, form, record in self.index[kind].get(bodies, []):
                    bound = str(record.get('term', '')).startswith('-') or str(record.get('source_term', '')).startswith('-')
                    tones = tone_changes(query, target, affix=affix and bound)
                    if tones is None:
                        continue
                    cost, tone_edits = tones
                    if base_cost+cost > max_cost:
                        continue
                    found.append({'cost': round(base_cost+cost, 3), 'changes': edits+tone_edits,
                                  'matched_form': form, 'entry_id': record['entry_id'],
                                  'attestation_id': record['attestation_id'], 'source': record['source'],
                                  'canonical_source': record.get('canonical_source', record['source']),
                                  'zh': record.get('zh', ''), 'en': record.get('en', ''),
                                  'pos': record.get('pos', ''), 'source_term': record.get('source_term', ''),
                                  'notations': record.get('notations', {}), 'locator': record.get('locator', '')})
            found.sort(key=lambda r: (r['cost'], source_priority(r), r['attestation_id']))
            unique, seen = [], {}
            for hit in found:
                key = (hit['entry_id'], hit['matched_form'])
                if key in seen:
                    primary = seen[key]
                    used = {primary['attestation_id']} | {
                        x['attestation_id'] for x in primary.get('alternative_witnesses', [])}
                    if hit['attestation_id'] not in used:
                        primary.setdefault('alternative_witnesses', []).append(hit)
                else:
                    unique.append(hit); seen[key] = hit
            return unique[:limit]

        # Preserve whole-entry and multi-entry analyses, even if a whole entry exists.
        paths = {0: [{'cost': 0., 'pieces': [], 'boundaries': []}]}
        for end in range(1, len(units)+1):
            options = []
            for start in range(end):
                for path in paths.get(start, []):
                    if len(path['pieces']) >= 4:
                        continue
                    for hit in pieces(start, end):
                        cost = path['cost'] + hit['cost'] + (.15 if start else 0)
                        if cost <= max_cost:
                            options.append({'cost': round(cost, 3), 'pieces': path['pieces']+[hit],
                                            'boundaries': path['boundaries']+[end]})
            options.sort(key=lambda r: (r['cost'], sum(source_priority(h) for h in r['pieces']), len(r['pieces'])))
            # Keep each meaning/source combination; do not equate a match with a translation.
            paths[end] = options[:max(24, limit*3)]
        segmented = [p for p in paths.get(len(units), []) if len(p['pieces']) > 1]
        return {'query': text, 'notation': notation, 'mode': 'static_pronunciation_candidates',
                'embedding_run': False, 'max_cost': max_cost, 'unsupported_forms': self.unsupported_forms,
                'whole': pieces(0, len(units)), 'segmentations': segmented[:limit],
                'notice': '候选须结合句法、词义和上下文选择；保留原记音，不自动改写原文。'}


def source_priority(hit):
    return {'brassett-2006': 0, 'brassett-2004': 1}.get(hit['canonical_source'], 2)
