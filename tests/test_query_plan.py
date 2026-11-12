"""Productivity, role safety, shared engines and independent inventory scoring."""
import json
from pathlib import Path

import pytest

from tujia_lex.query_plan import Component, Interpretation, plan
from tujia_lex.constructions import compose
from tujia_lex.evaluation import grade, aggregate
from tujia_lex.retrieval import RetrievalSession, rejected_reason, supports
from tujia_lex.static import StaticLexicon

ROOT=Path(__file__).resolve().parents[1]


def witness(zh, eid='test', *, pos='v', en='', source='brassett-2006'):
    return {'id':'lex:'+eid, 'entry_id':eid, 'zh':zh,'en':en,'pos':pos,'dialect':'north',
        'forms':['form:'+eid], 'notations':{}, 'locations':[],
        'sources':[{'id':source,'canonical_id':source,'attestation_id':eid}],
        'attestations':[{'id':eid,'term':'form:'+eid}], 'score':0.25}


def test_result_state_is_realized_not_only_recorded_in_plan():
    p=plan('画地为牢')
    result=compose(p,[witness('关','close'),witness('自己','self',pos='pron')])
    assert p.analysis.features['aspect']=='result_state'
    assert result['draft_source_forms'].endswith(' bǒ')
    assert any('maintained result state' in m['function'] for m in result['morphology'])


def test_generic_thing_heads_do_not_require_a_word_for_thing():
    # Uncurated purpose-object frames must work without retrieving 东西.
    for expression in ['洗鞋工具','洗衣服用品','开门用的东西','看不见的东西']:
        p=plan(expression)
        assert p.analysis.features['head_realization']=='implicit'
        records=[witness(c.query,c.key,pos='n' if c.role!='predicate' else 'v')
                 for c in p.analysis.components if c.role!='head']
        result=compose(p,records)
        assert result['lexical_complete']
        assert result['draft_source_forms'].endswith(' niexi')
        assert 'head' not in result['selected']
        if expression=='看不见的东西':
            assert 'tā tī niexi' in result['draft_source_forms']
            assert result['roles']['head']=='patient'
        p.analysis.features['head_realization']='overt'
        next(c for c in p.analysis.components if c.role=='head').required=True
        assert not compose(p,records)['lexical_complete']
    specific=compose(plan('我画的画'),[witness('我','agent',pos='pron'),witness('画','draw')])
    assert not specific['draft_source_forms'].endswith('niexi')
    assert '[head]' in specific['draft_source_forms']


def test_warming_requires_causation_not_bare_property_or_fire_synonym():
    for expression in ['取暖用的东西', '让孩子暖和用的东西', '使人干净用的东西']:
        p=plan(expression)
        assert p.analysis.features['causative']=='yes'
        assert p.analysis.roles['head']=='causer'
        records=[witness(c.query,c.key,pos='n' if c.role=='causee' else 'v')
                 for c in p.analysis.components if c.role!='head']
        result=compose(p,records)
        assert 'form:causee dǒ form:predicate niexi' in result['draft_source_forms']
        assert not compose(p,[r for r in records if r['entry_id']!='causee'])['lexical_complete']
    p=plan('取暖用的东西')
    pred=next(c for c in p.analysis.components if c.role=='predicate')
    assert not supports(witness('烤火'),pred)
    assert not compose(p,[witness('暖和')])['lexical_complete']


def test_new_frames_are_composed_from_arguments_not_expression_table():
    # Generated combinations absent from concepts.json AND the challenge data.
    for verb in ['买','卖','读','写']:
        for obj in ['诗','药','报纸']:
            p=plan(verb+obj+'的人')
            assert p.analysis.family=='event_agent'
            assert p.analysis.roles['head']=='agent'
            assert [c.query for c in p.analysis.components[:2]]==[verb,obj]
    p=plan('快要洗鞋')
    assert p.analysis.features['aspect']=='imminent_onset'
    assert {c.query for c in p.analysis.components}=={'洗','鞋'}


def test_explicit_semantic_interpretation_for_unseen_opaque_meaning():
    i=Interpretation('把困难推给别人','idiom_event',[
        Component('predicate','推','predicate'),Component('patient','困难','patient'),
        Component('recipient','别人','recipient')],roles={'agent':'topic','recipient':'别人'})
    p=plan('甩锅', '指推卸责任', interpretation=i)
    assert p.origin=='explicit_interpretation'
    assert p.analysis.roles['recipient']=='别人'
    assert '推' in [q.query for q in p.queries]
    assert plan('甩锅').analysis.family=='direct'  # no invented opaque analysis


def test_agent_patient_gap_and_negative_scope():
    a,b=plan('审判别人的人'),plan('被别人审判的人')
    assert a.analysis.roles['head']=='agent'
    assert a.analysis.roles['patient']=='别人'
    assert b.analysis.roles['head']=='patient'
    assert b.analysis.roles['agent']=='别人'
    p=plan('令人费解')
    assert p.analysis.features=={'negation':'modal','modality':'ability'}
    assert plan('尚未吃完').analysis.features=={'aspect':'not_yet_completed','negation':'event'}
    assert plan('还在吃').analysis.features['aspect']=='progressive_continuative'


def test_bounded_plan_prioritizes_critical_components_and_keeps_original():
    p=plan('经济损失',max_queries=3)
    assert [q.query for q in p.queries]==['经济损失','钱','丢失']
    for invalid in ['', ' '*4, '词'*121]:
        with pytest.raises(ValueError):plan(invalid)
    with pytest.raises(ValueError):plan('词',max_queries=13)


def test_negative_controls_and_nominalizer_role_checks():
    scent=plan('香味')
    for r in [witness('香',pos='n.',en='incense'),witness('闻',en='to smell')]:
        assert rejected_reason(r,scent)
        assert not any(supports(r,c) for c in scent.analysis.components)
    drink=plan('饮料')
    assert rejected_reason(witness('水',pos='n.',en='water'),drink)
    assert rejected_reason(witness('不知道'),plan('令人费解'))
    assert not supports(witness('信',pos='vt.',en='believe'),Component('patient','信','patient'))
    # The letter noun and classifier bottle are distinct from homographs.
    assert supports(witness('信',pos='n.',en='letter'),Component('patient','信','patient'))
    assert not supports(witness('瓶',pos='cl.'),Component('patient','瓶','patient'))
    assert not compose(plan('经济损失'),[witness('钱',pos='n.')])['lexical_complete']
    assert not compose(plan('路人'),[witness('路',pos='n.')])['lexical_complete']
    toy=compose(plan('玩具'),[witness('玩')]);beverage=compose(drink,[witness('喝')])
    agent=compose(plan('走的人'),[witness('走')])
    assert toy['morphology'][-1]['form']=='xí'
    assert beverage['morphology'][-1]['form']=='ci'
    assert agent['morphology'][-1]['form']=='mā'
    patient=compose(plan('被骂的人'),[witness('骂'),witness('人',pos='n.')])
    assert all(m['form']!='mā' for m in patient['morphology'])
    assert not compose(plan('走的人',dialect='south'),[witness('走')])['construction_supported']


def test_metric_denominators_partial_gold_and_existing_word_miss():
    p=plan('经济损失')
    case={'family':'abstract_event','expected_components':[
        {'key':'resource','gold':[{'entry_id':'money','attestation_ids':['money']}]},
        {'key':'predicate','gold':[]}], 'expected_features':{}, 'expected_roles':{}}
    candidates=[witness('钱','money',pos='n.')]
    result={'candidates':candidates,'plan':p.to_dict()}
    metrics=grade(case,result,compose(p,candidates))
    assert metrics['recall']['1']==1
    assert metrics['gold_target_count']==1 and metrics['pending_target_count']==1
    assert not metrics['all_required_components_retrieved']
    assert not metrics['construction_coverage']
    assert metrics['native_vocabulary_utilization'] is None
    result['candidates']=[]
    assert grade(case,result,compose(p,[]))['missed_existing_components']==['resource']


def test_same_plan_bge_static_full_index_and_query_cache(real_encoder):
    from tujia_lex.index import Index
    index_path=ROOT/'.cache/bge-index'
    if not index_path.exists():pytest.skip('Complete local index is an evaluation asset')
    idx=Index(index_path)
    lex=StaticLexicon(ROOT/'skills/translate-tujia/lexicon')
    session=RetrievalSession(idx,real_encoder,lex)
    p=plan('饮料')
    bge=session.run(p,'C'); static=session.run(p,'D')
    assert [q['query'] for q in bge['queries']]==[q['query'] for q in static['queries']]
    assert bge['plan']==static['plan']
    assert any(r['entry_id']=='w874' for r in bge['candidates'])
    assert any(r['entry_id']=='w874' for r in static['candidates'])
    assert all(r['score'] is None for r in static['candidates'])
    assert bge['raw_results'] and isinstance(bge['raw_results'][0]['score'],float)
    assert session.run(p,'C')['cost']['engine_calls']==0
    assert session.run(p,'C')['cost']['query_encodings']==0
    assert all(q['limit']>=1 for q in session.run(p,'C',budget='matched')['queries'])
    assert session.run(p,'C',budget='matched')['cost']['requested_candidates']==20
    first=lex.search('喝')[0]
    assert 'notations' in first and first['attestations'][0]['attestation_id']


def test_challenge_has_independent_verified_targets_and_holdouts():
    data=json.loads((ROOT/'tests/data/semantic-compositional-challenge.json').read_text())
    cases=data['cases'];concepts=json.loads((ROOT/'skills/tujia-synonym-lite/concepts.json').read_text())['concepts']
    assert len(cases)>=36 and len({c['family'] for c in cases})>=10
    holdout=[c for c in cases if c['split']=='holdout']
    assert len(holdout)>=12
    assert not set(c['expression'] for c in holdout)&set(concepts)
    assert all(t['gold_status']=='verified_inventory' for c in cases for t in c['expected_components'] if t['gold'])


def test_required_relative_heads_and_abstract_change_order():
    for phrase in ['被骂的人', '我画的画', '不认识的人']:
        p=plan(phrase)
        assert next(c for c in p.analysis.components if c.key=='head').required
    p=plan('收入减少')
    c=compose(p,[witness('得到','get'),witness('钱','money',pos='n.'),witness('减少','decrease')])
    assert c['draft_source_forms'].index('form:get') < c['draft_source_forms'].index('form:decrease')


def test_role_pair_is_not_collapsed_into_identical_surface_drafts():
    words=[witness('审判','judge'),witness('别人','other',pos='n.'),witness('人','person',pos='n.')]
    agent=compose(plan('审判别人的人'),words)
    patient=compose(plan('被别人审判的人'),words)
    assert agent['draft_source_forms'] != patient['draft_source_forms']
    assert agent['roles']['head']=='agent' and patient['roles']['head']=='patient'
    assert agent['morphology'][-1]['form']=='mā'
    assert patient['morphology'][-1]['form']=='niě'


def test_rendered_challenge_keeps_33_tones_and_distinct_role_candidates():
    path=ROOT/'docs/evaluation/compositional/rendered-candidates.json'
    if not path.exists():pytest.skip('Fresh evaluation previews not present')
    rows=json.loads(path.read_text())['cases']
    assert len(rows)>=36
    by_query={r['expression']:r for r in rows}
    smell=by_query['香味']
    assert '³³' in smell['ipa_candidate']
    assert '33' in smell['pinyin_candidate']  # original notation, not a false 21 accent
    a,b=by_query['审判别人的人'],by_query['被别人审判的人']
    assert a['pinyin_candidate']!=b['pinyin_candidate']
    assert a['roles']['head']=='agent' and b['roles']['head']=='patient'
