"""Evidence-backed construction families and a conservative compositional draft.

The draft is an audit artifact; lexical source forms stay verbatim. Normal prose
translation still uses the skill's source-specific Pinyin/IPA conversion workflow.
"""
from __future__ import annotations

from .retrieval import supports, rejected_reason
from .static import source_priority

BASE = 'https://github.com/luggroo/bizic-dictionary/blob/072046c39261cf536e0ce29f06779cd3eeb99219/docs/reference-grammar.md#'
REGISTRY = {
    'direct': ('north-nominal-forms', 'attested lexical sense', 'whole expression; no morphology inferred'),
    'event_agent': ('north-24-103', 'Brassett 2006:141–142 §8.1; Tian:443', 'arguments + V + ma /ma⁵⁵/; human agent gap'),
    'event_object': ('north-24-102', 'Tian:444; Lu et al. 2021:425; Brassett 2006:141–143', 'V + ci for consumed/affected object; xi for broader associated thing'),
    'function_object': ('north-25-101', 'Tian:623; Brassett 2006:142–147', '[arguments + V] + nie (xi) + object head; purpose need not be patient'),
    'semantic_generalization': ('north-6-3', 'property predication / semantic superordinate', 'lexical superordinate; differentiating property remains a recorded meaning loss'),
    'negative_ability': ('north-17-101', 'Brassett 2006:127–132', 'V + ta ti /tʰa⁵⁵ tʰi⁵⁵/; inability rather than factual da'),
    'negative_relative': ('north-relative-clauses', 'Brassett 2006:142–147; reference grammar §6.3', '[agent + patient + V + negation] + nie + head; preserve argument gap'),
    'role_relative': ('north-relative-clauses', 'Brassett 2006:142–147; reference grammar §6.3', '[overt arguments + V] + nie + head; agent/patient differ by gap, not a passive suffix'),
    'abstract_event': ('north-24-101', 'Brassett 2006:141–143; reference grammar §6.2', 'resource as event argument + loss/owing/change predicate; xi may nominalize event'),
    'spatial_composition': ('north-14-1', 'Brassett 2006:84,99,102,105', 'landmark + localizer; preserve numeral if present'),
    'aspect_modality': ('north-9-103', 'Brassett 2006:109–140; Tian:526; Lu et al. 2021:431–432', 'whole predicate TAM: onset hu; progressive la nie; completive ji + da nie; recent completion needs state distinction'),
    'idiom_event': ('north-xi-functions', 'reference grammar §§5–6; lexicalized Chinese interpretation', 'ordinary event with original reflexive/existence/modal scope'),
}


def lexical_form(record):
    """Pick an attestation, then only its own forms/notations (never array zip)."""
    sources = sorted(record.get('sources', []), key=lambda s: (0 if s.get('canonical_id') == 'brassett-2006' else (1 if s.get('canonical_id') == 'brassett-2004' else 2), s.get('attestation_id', '')))
    aid = sources[0].get('attestation_id') if sources else None
    if record.get('record_type') == 'survey_lexeme':
        aid = record['id']
    att = next((a for a in record.get('attestations', []) if a.get('id', a.get('attestation_id')) == aid), {})
    term = att.get('term') or record.get('forms', [''])[0]
    linked = {}
    for scheme, items in record.get('notations', {}).items():
        linked[scheme] = [n if isinstance(n, str) else n['text'] for n in items
                          if isinstance(n, str) or aid in n.get('attestationIds', [])]
    if record.get('ipa'):
        linked.setdefault('ipa', [record['ipa']])
    return {'term': term, 'attestation_id': aid, 'source': sources[0] if sources else {},
            'notations': {k:v for k,v in linked.items() if v}, 'entry_id': record.get('entry_id'),
            'dialect': record.get('dialect'), 'locations': record.get('locations', []),
            'record_id': record['id']}


def implicit_thing_head(analysis):
    """Generic thing heads may be nominalized; specific nouns remain overt.

    Explicit interpretations can request an overt head when context needs it.
    The default also applies to stored plans predating head_realization.
    """
    return (analysis.family in {'function_object', 'negative_relative'}
            and analysis.features.get('head_realization') != 'overt'
            and any(c.role == 'head' and c.query == '东西' for c in analysis.components))


def compose(plan, candidates):
    analysis = plan.analysis
    implicit_head = implicit_thing_head(analysis)
    selected, missing = {}, []
    for c in analysis.components:
        if implicit_head and c.role == 'head':
            continue
        options = [r for r in candidates if supports(r, c) and not rejected_reason(r, plan)]
        if options:
            selected[c.key] = lexical_form(min(options, key=lambda r: (source_priority(r), -r.get('rrf', 0), r['id'])))
        elif c.required:
            missing.append(c.key)
    anchor, citation, pattern = REGISTRY[analysis.family]
    # Northern morphology cannot be transferred into Southern records.
    dialect_supported = plan.dialect == 'north'
    terms = {k: v['term'] for k,v in selected.items()}
    pred = terms.get('predicate', '[predicate]')
    args = ' '.join(terms[c.key] for c in analysis.components
                    if c.key in terms and c.role not in {'predicate', 'head', 'result', 'causee'})
    f = analysis.features
    predicate = pred
    morphology = []
    def add(form, function):
        nonlocal predicate
        predicate += ' ' + form
        morphology.append({'form': form, 'function': function})
    if f.get('modality') == 'ability':
        add('tā tī', 'negative ability /tʰa⁵⁵ tʰi⁵⁵/; B06')
    elif f.get('negation') in {'predicate', 'event'} and f.get('aspect') != 'not_yet_completed':
        add('dá', 'factual negation /ta²⁴/; B06:90')
    if f.get('aspect') == 'progressive_continuative':
        add('lā niē', 'PROG+CONT; supplementary eating paradigm, not B06 full example')
    elif f.get('aspect') == 'imminent_onset':
        add('hǔ', 'INCH /xu²¹/; stem allomorphy must be checked')
    elif f.get('aspect') == 'not_yet_completed':
        add('jī dā niē', 'COMPL+NEG+CONT; Tian:526; other Northern locality')
    elif f.get('aspect') == 'recent_completed':
        add('[recent completion/state choice]', 'Lu et al. 2021:431–432; not a universal just suffix')
    elif f.get('aspect') == 'result_state':
        add('bǒ', 'maintained result state /pɔ²¹/; B06:90 exx.110–111; productive extension')
    family = analysis.family
    if f.get('causative') == 'yes':
        predicate = terms.get('causee', '[causee]') + ' dǒ ' + predicate
        morphology.append({'form': 'dǒ', 'function': 'CAUS /tuɔ²¹/ before embedded predicate; B06:155–156 ex.47; not postverbal necessity'})
    draft = ' '.join(x for x in [args, predicate] if x)
    if family == 'event_agent' or (family == 'role_relative' and analysis.roles.get('head') == 'agent' and f.get('nominalization') == 'person'):
        draft += ' mā'
        morphology.append({'form': 'mā', 'function': 'human agent NMLZ /ma⁵⁵/; not an object marker'})
    elif family == 'event_object':
        suffix = 'xí' if any(c.query in {'玩', '坐'} for c in analysis.components) else 'ci'
        draft += ' ' + suffix
        morphology.append({'form': suffix, 'function': 'associated thing xi' if suffix == 'xí' else 'object NMLZ /tsʰi/; lexical tone requires source-specific form'})
    elif family in {'role_relative', 'negative_relative', 'function_object'}:
        if implicit_head:
            draft += ' niexi'
            morphology.append({'form': 'niexi', 'function': 'independent LNK–NMLZ; Feng 2025:10 ex.27; Xiang 2026:14,16; role supplied by predicate/context; source tone pending'})
        else:
            head = terms.get('head', '[head]')
            draft += ' niě ' + head
            morphology.append({'form': 'niě', 'function': 'relative linker; head role retained in graph'})
    elif family == 'spatial_composition':
        draft = ' '.join(x for x in [terms.get('landmark', '[landmark]'),
                    '[two + classifier]' if f.get('number') else '', terms.get('relation', '[relation]')] if x)
    elif family in {'semantic_generalization', 'direct'}:
        draft = terms.get('head', '[head]')
    elif family == 'abstract_event':
        draft += ' xi'
        morphology.append({'form': 'xi', 'function': 'event nominalization; not substitution of resource for event'})
    if family == 'abstract_event' and any(c.role == 'result' for c in analysis.components):
        draft += ' ' + terms.get('change', '[result predicate]')
    if f.get('negation') == 'existence':
        draft = (terms.get('head', draft)) + ' tái'
        morphology.append({'form':'tái','function':'negative existence /tʰai²⁴/; B04 lexical tai2, distinct from factual negation'})
    source_ids = {s['source'].get('canonical_id') for s in selected.values()}
    compatible = source_ids <= {'brassett-2004', 'brassett-2006'}
    if family in {'direct', 'semantic_generalization'} and len(source_ids) == 1:
        compatible = True
    unresolved_features = []
    if implicit_head:
        unresolved_features.append('independent nominalization: source-specific tone and contextual role require review')
    if not dialect_supported:
        unresolved_features.append('Northern registry does not license Southern morphology')
    if not compatible:
        unresolved_features.append('source/locality compatibility needs review')
    if family == 'event_object' or f.get('aspect') in {'recent_completed', 'not_yet_completed', 'imminent_onset'}:
        unresolved_features.append('nominalizer tone or predicate-specific TAM realization needs review')
    if f.get('number'):
        unresolved_features.append('numeral/classifier realization needs review')
    if family == 'abstract_event' and any(c.key == 'change' and c.key not in terms for c in analysis.components):
        missing.append('change')
    # Complete surface claims require every lexical slot and every realization choice.
    lexical_complete = not missing
    licensed = lexical_complete and dialect_supported and compatible
    return {'family': family, 'draft_source_forms': draft, 'selected': selected,
        'missing_components': sorted(set(missing)), 'roles': analysis.roles, 'features': f,
        'morphology': morphology, 'grammar': {'url': BASE + anchor, 'citation': citation + ('; Feng 2025:10 ex.27; Xiang 2026:14,16' if implicit_head else ''), 'pattern': '[arguments + predicate] + niexi; implicit thing head' if implicit_head else pattern,
            'evidence_level': 'secondary reference grammar; productive application, not whole-phrase attestation'},
        'lexical_complete': lexical_complete, 'construction_supported': licensed,
        'surface_complete': licensed and not unresolved_features and '[' not in draft,
        'unresolved_realization': unresolved_features, 'meaning_losses': analysis.losses,
        'notation': 'audit uses unchanged lexical source forms + labeled morphology; not synchronized Pinyin/IPA output'}
