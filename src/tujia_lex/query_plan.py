"""Engine-independent, bounded meaning → query → construction planning.

The deterministic parser covers productive Chinese frames, not arbitrary language
understanding. An agent can supply an Interpretation for opaque/contextual senses;
that same plan is executable by either engine. Gold labels never enter planning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
import unicodedata


def normalize(text):
    return unicodedata.normalize('NFKC', text).strip().casefold()


@dataclass
class Component:
    key: str
    query: str
    role: str
    alternatives: list[str] = field(default_factory=list)
    required: bool = True


@dataclass
class Interpretation:
    meaning: str
    family: str
    components: list[Component]
    roles: dict[str, str] = field(default_factory=dict)
    features: dict[str, str] = field(default_factory=dict)
    paraphrases: list[str] = field(default_factory=list)
    losses: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value):
        return cls(**{**value, 'components': [Component(**c) for c in value['components']]})


@dataclass
class PlannedQuery:
    query: str
    relation: str
    component: str | None = None


@dataclass
class QueryPlan:
    original: str
    context: str
    dialect: str
    analysis: Interpretation
    queries: list[PlannedQuery]
    origin: str
    version: int = 1

    def to_dict(self):
        return asdict(self)


# Lexical sense bridges: finite conventional meanings of opaque words/idioms.
# Productive parsing below handles new arguments, heads, negative/TAM frames.
# This is deliberately separate from the evaluation set and gold IDs.
LEXICAL = {
    '路人': '走路的人', '玩具': '玩的东西', '饮料': '喝的东西', '食物': '吃的东西',
    '坐垫': '坐的东西', '陌生人': '不认识的人', '令人费解': '不能懂得',
    '难以置信': '不能相信', '旁观者': '看的人',
    '画地为牢': '把自己关住', '束手无策': '没有办法',
    '心里有数': '知道情况', '无路可走': '没有路可以走',
    '债务': '欠钱', '收入减少': '得到的钱减少',
}
# Verb lexical semantics, shared across every productive frame.
VERBS = {'清洁': ('洗', ['清洗']), '取暖': ('使人暖和', []),
         '遮': ('挡', ['遮挡']), '开': ('打开', ['开']),
         '懂得': ('懂', ['理解', '懂得', '明白']),
         '认识': ('认识', ['认', '认得']), '送': ('送', ['递']), '守': ('守', ['看守', '守卫']),
         '忍受': ('忍受', ['容忍']), '相信': ('相信', ['信']), '储': ('放', ['储存']),
         '失去': ('丢失', ['损失', '失去']), '亏损': ('丢失', ['损失', '亏损']),
         '回来': ('回来', ['回']), '下雨': ('下雨', ['落雨']),
         '打鱼': ('捉', ['捕', '打鱼']), '写字': ('写', ['写字'])}
# Longest-first predicate segmentation; the tail becomes an argument, never a synonym.
PREDICATES = sorted(set(VERBS) | {
    '审判', '忍受', '相信', '看见', '看', '听见', '听', '喜欢', '认识', '骂',
    '守', '送', '喝', '吃', '玩', '坐', '走', '开', '洗', '写', '读', '买', '卖',
    '捉', '关', '挡', '储', '放', '砍', '画', '欠', '知道', '得到', '减少', '睡', '跑',
}, key=lambda x: (-len(x), x))


def event(text):
    """Return predicate + its overt patient/location; no Hanzi-by-Hanzi synonymy."""
    text = text.removeprefix('用来').removeprefix('用以').removesuffix('用')
    causative = re.fullmatch(r'(?:使|让)(人|孩子|我|你|他)(.+)', text)
    if causative:
        causee, state = causative.groups()
        return event(state) + [Component('causee', causee, 'causee')]
    if text == '走路':
        return [Component('predicate', '走', 'predicate'), Component('location', '路', 'location')]
    if text == '打鱼':
        return [Component('predicate', '捉', 'predicate', ['捕']), Component('patient', '鱼', 'patient')]
    pred = next((p for p in PREDICATES if text.startswith(p)), text)
    tail = text[len(pred):].removeprefix('住')
    basic, alternatives = VERBS.get(pred, (pred, []))
    if basic.startswith(('使人', '让人')):
        return event(basic + tail)
    out = [Component('predicate', basic, 'predicate', alternatives)]
    if tail:
        out.append(Component('patient', tail, 'patient'))
    for c in out:
        if c.role == 'patient' and c.query == '瓶':
            c.alternatives = ['瓶子']
        if c.role == 'patient' and c.query == '雨':
            c.alternatives = ['雨水']
    return out


def interpret(expression):
    source = expression
    text = LEXICAL.get(source, source)
    family = 'direct'
    roles, features, losses, paraphrases = {}, {}, [], []
    components = []
    # TAM has scope over the full event; object arguments survive the rewrite.
    tam = re.fullmatch(r'(快要|就要|还在|仍在|尚未|还没|刚刚)(.+)', text)
    if tam:
        trigger, body = tam.groups()
        family = 'aspect_modality'
        components = event(body.removesuffix('完'))
        features = {'aspect': {'快要': 'imminent_onset', '就要': 'imminent_onset',
                    '还在': 'progressive_continuative', '仍在': 'progressive_continuative',
                    '尚未': 'not_yet', '还没': 'not_yet', '刚刚': 'recent_completed'}[trigger]}
        if trigger in {'尚未', '还没'}:
            features['negation'] = 'event'
            if body.endswith('完'):
                features['aspect'] = 'not_yet_completed'
        paraphrases = [body + '（' + trigger + '）']
    elif source in {'香味', '花香', '噪音', '寒意', '潮气'} or text.endswith(('香味', '噪声')):
        family = 'semantic_generalization'
        head = '声音' if source == '噪音' or text.endswith('噪声') else ('冷' if source == '寒意' else ('湿' if source == '潮气' else '气味'))
        components = [Component('head', head, 'head')]
        losses = ['generalization drops the differentiating property/origin']
        features['generalization'] = 'explicit'
    elif re.fullmatch(r'.+(岸|脚)', text) or re.fullmatch(r'.+(外|里面|下面|旁边|中间|上面|后面|前面)', text):
        family = 'spatial_composition'
        m = re.fullmatch(r'(.+?)(旁边|里面|下面|中间|上面|后面|前面|岸|脚|外)', text)
        landmark, relation = m.groups()
        relation = {'岸': '旁边', '脚': '下面', '外': '外面'}.get(relation, relation)
        features['spatial_relation'] = relation
        if landmark.startswith('两'):
            features['number'] = 'two'
            landmark = landmark[1:]
        components = [Component('landmark', landmark, 'landmark'), Component('relation', relation, 'relation')]
        paraphrases = [landmark + relation]
    elif text.endswith('损失'):
        family = 'abstract_event'
        resource = text[:-2]
        resource = '钱' if resource in {'经济', '财产', '财物'} else resource
        components = [Component('resource', resource, 'patient', ['财物'] if resource == '钱' else []),
                      Component('predicate', '丢失', 'predicate', ['损失', '失去', '亏损', '受损失'])]
        roles = {'patient': resource, 'event': 'loss'}
        paraphrases = [resource + '丢失']
    elif source in {'债务', '收入减少'}:
        family = 'abstract_event'
        if source == '债务':
            components = [Component('predicate', '欠', 'predicate'), Component('resource', '钱', 'patient')]
        else:
            components = [Component('predicate', '得到', 'predicate'), Component('resource', '钱', 'patient'),
                          Component('change', '减少', 'result')]
        paraphrases = [text]
    elif source in {'画地为牢', '束手无策', '心里有数', '无路可走'}:
        family = 'idiom_event'
        if source == '画地为牢':
            components = [Component('predicate', '关', 'predicate'), Component('reflexive', '自己', 'patient')]
            roles = {'agent': 'self', 'patient': 'self'}
            features = {'reflexive': 'yes', 'aspect': 'result_state'}
        elif source == '束手无策':
            components = [Component('head', '办法', 'head', ['方法'])]
            features = {'negation': 'existence'}
        elif source == '心里有数':
            components = [Component('predicate', '知道', 'predicate'), Component('patient', '情况', 'patient', ['事情'])]
        else:
            components = [Component('predicate', '走', 'predicate'), Component('location', '路', 'location')]
            features = {'negation': 'existence', 'modality': 'possibility'}
        paraphrases = [text]
    else:
        # Relative clauses: retain the argument gap. A patient head is not an agent.
        relative = re.fullmatch(r'(.+?)的(人|东西|画|书)', text)
        compact_agent = re.fullmatch(r'(.+?)(?:人|者)', text)
        function = re.fullmatch(r'(.+?)(?:工具|用品|容器|器)', text)
        if relative or compact_agent:
            body, head = relative.groups() if relative else (compact_agent.group(1), '人')
            function_thing = head == '东西' and (body.endswith('用') or body.startswith(('用来', '遮')))
            family = 'function_object' if function_thing else ('event_agent' if head == '人' else 'event_object')
            gap = 'agent' if head == '人' else 'patient'
            if source == '陌生人' or body.startswith('不认识') or '不见' in body:
                gap = 'patient'
                roles['agent'] = 'implicit observer'
            if body.startswith('被'):
                body = body[1:]
                gap = 'patient'
            participant = None
            for person in ['别人', '我', '他', '你']:
                if body.startswith(person):
                    participant, body = person, body[len(person):]
                    roles['agent'] = person
                    gap = 'patient'
                    break
                if body.endswith(person):
                    participant, body = person, body[:-len(person)]
                    roles['patient'] = person
                    break
            if body.startswith(('不', '没')) or '不见' in body:
                family = 'negative_relative'
                features['negation'] = 'predicate'
                if '不见' in body:
                    body = body.replace('不见', '见')
                    features['modality'] = 'ability'
                else:
                    body = body[1:]
            components = event(body)
            if participant:
                components.append(Component('participant', participant, 'agent' if gap == 'patient' else 'patient'))
            roles['head'] = 'instrument' if function_thing else gap
            roles.setdefault('agent', 'head' if gap == 'agent' else 'unspecified')
            roles.setdefault('patient', 'head' if gap == 'patient' else 'unspecified')
            features['nominalization'] = 'person' if head == '人' and gap == 'agent' else ('relative_patient' if gap == 'patient' and head == '人' else 'object')
            if function_thing:
                features['nominalization'] = 'purpose_object'
            components.append(Component('head', head, 'head', required=False))
            if (participant or (gap == 'patient' and head == '人')) and family != 'negative_relative':
                family = 'role_relative'
        elif function:
            family = 'function_object'
            roles = {'head': 'instrument', 'agent': 'generic user'}
            components = event(function.group(1))
            components.append(Component('head', '东西', 'head', required=False))
            features['nominalization'] = 'purpose_object'
        else:
            negative = re.fullmatch(r'(不能|无法|难以)(.+)', text)
            if negative:
                family = 'negative_ability'
                components = event(negative.group(2))
                features = {'negation': 'modal', 'modality': 'ability'}
                roles = {'experiencer': 'generic person', 'stimulus': 'source referent'}
                paraphrases = ['不能' + negative.group(2)]
            else:
                components = event(text) if text != source else [Component('head', text, 'head')]
    if source != text:
        paraphrases.insert(0, text)
    if family in {'function_object', 'role_relative', 'negative_relative'}:
        for c in components:
            if c.key == 'head':
                implicit = c.query == '东西' and family in {'function_object', 'negative_relative'}
                c.required = not implicit
                features['head_realization'] = 'implicit' if implicit else 'overt'
    if any(c.role == 'causee' for c in components):
        features['causative'] = 'yes'
        roles['causee'] = next(c.query for c in components if c.role == 'causee')
        if family == 'function_object':
            roles['head'] = 'causer'
            roles['causer'] = 'head'
            roles['experiencer'] = roles['causee']
            roles.pop('patient', None)
    return Interpretation(text, family, components, roles, features, list(dict.fromkeys(paraphrases)), losses)


def plan(expression, context='', dialect='north', *, interpretation=None, related=(), max_queries=10, seeds=None):
    """Use an explicit semantic interpretation when supplied, else productive parsing.

    `context` is preserved verbatim, not falsely presented as machine-understood.
    Opaque unseen meanings can enter via Interpretation without adding code or
    concepts.json entries. Extra queries never overwrite roles or polarity.
    """
    if not normalize(expression) or len(expression) > 120:
        raise ValueError('expression must be 1..120 characters')
    if dialect not in {'north', 'south', 'any'} or not 1 <= max_queries <= 12:
        raise ValueError('invalid dialect or query budget (1..12)')
    analysis = interpretation or interpret(expression.strip())
    if isinstance(analysis, dict):
        analysis = Interpretation.from_dict(analysis)
    if len(analysis.components) > 12 or analysis.family not in {
        'direct', 'event_agent', 'event_object', 'function_object', 'semantic_generalization',
        'negative_ability', 'negative_relative', 'abstract_event', 'spatial_composition',
        'aspect_modality', 'idiom_event', 'role_relative'}:
        raise ValueError('unsupported construction or too many components')
    queries = [PlannedQuery(expression, 'original')]
    # Critical components precede decorative paraphrases under bounded budgets.
    for c in sorted(analysis.components, key=lambda c: not c.required):
        queries.append(PlannedQuery(c.query, 'component_' + c.role, c.key))
    queries += [PlannedQuery(q, 'direct_synonym') for q in analysis.synonyms]
    queries += [PlannedQuery(q, 'paraphrase') for q in analysis.paraphrases]
    for c in analysis.components:
        queries += [PlannedQuery(q, 'component_alternative', c.key) for q in c.alternatives]
    queries += [PlannedQuery(q, 'contextual_expansion') for q in related]
    if seeds:
        concept = seeds.get('concepts', {}).get(expression, {})
        queries += [PlannedQuery(q['q'], q['relation']) for q in concept.get('candidates', [])]
    unique, seen = [], set()
    for q in queries:
        key = normalize(q.query)
        if key and key not in seen:
            if len(key) > 120:
                raise ValueError('planned query exceeds 120 characters')
            unique.append(q)
            seen.add(key)
    return QueryPlan(expression, context, dialect, analysis, unique[:max_queries],
                     'explicit_interpretation' if interpretation else 'productive_rules_with_lexical_bridges')
