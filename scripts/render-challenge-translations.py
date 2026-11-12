#!/usr/bin/env python3
"""Render all measured hybrid drafts as reader-facing Pinyin/IPA audit candidates.

Uses the pinned source checkout's converter. Unsupported tones stay explicit;
original attestations/notations are never edited. These drafts are hypotheses.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from tujia_lex.query_plan import plan, Interpretation
from tujia_lex.constructions import compose, implicit_thing_head


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root',required=True)
    p.add_argument('--directory',default='docs/evaluation/compositional')
    a=p.parse_args();root=Path(a.directory)
    review_path=root/'candidate-reviews.json'
    reviews=json.loads(review_path.read_text()) if review_path.exists() else {}
    docs=[json.loads(path.read_text()) for path in sorted(root.glob('c[0-9][0-9].json'))]
    # Recompose only reviewed generic-head constructions from the recorded
    # candidate inventory. This is a grammar revision, never a new BGE run.
    revisions={}
    inventory=None
    for d in docs:
        r=next(r for r in d['routes'] if r['route']=='E' and r['budget']=='natural')
        reviewed_run=reviews.get(d['case']['id'],{}).get('reviewed_run')
        if reviewed_run:
            revisions[d['case']['id']]=r['composition']
            fresh=json.loads((root/reviewed_run).read_text())
            r['composition']=fresh['composition']
            r['plan']=fresh['plan']
            continue
        analysis=Interpretation.from_dict(r['plan']['analysis'])
        if not implicit_thing_head(analysis):
            continue
        if inventory is None:
            inventory={v['id']:v for v in map(json.loads,(root/'records.jsonl').read_text().splitlines())}
        revisions[d['case']['id']]=r['composition']
        candidates=[{**inventory[c['id']],**c} for c in r['candidates']]
        p=plan(r['expression'],dialect=r['plan']['dialect'],interpretation=analysis)
        r['composition']=compose(p,candidates)
    selected={v['record_id']:v for d in docs for r in d['routes'] if r['route']=='E' and r['budget']=='natural' for v in r['composition']['selected'].values()}
    keys=list(selected)
    requests=[{'mode':'source','source':selected[k]['source'].get('id',''),'text':selected[k]['term']} for k in keys]
    def convert(items):
        run=subprocess.run(['node','scripts/tujia-lex-spelling.cjs',a.data_root],input=json.dumps(items,ensure_ascii=False),text=True,capture_output=True,check=True)
        return json.loads(run.stdout)
    source=convert(requests)
    superscript=str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹')
    def ipa_text(text):
        return re.sub(r'[0-9]+',lambda m:m[0].translate(superscript),text)
    def supported_tones(text):
        return all(t in {'⁵⁵','²⁴','³⁵','²¹','⁵¹','⁵³'} for t in re.findall('[⁰¹²³⁴⁵⁶⁷⁸⁹]+',text))
    fallback=[];fallback_keys=[]
    rendered={}
    for key,result in zip(keys,source):
        v=selected[key]; rows=result.get('rows',[])
        if len(rows)==1 and not result.get('candidate') and not result.get('ambiguous') and rows[0].get('accent') and rows[0].get('ipa') and supported_tones(rows[0]['ipa']):
            rendered[key]={'pinyin':rows[0]['accent'],'ipa':rows[0]['ipa'],'method':'source-profile conversion','original_notations':v['notations']}
        else:
            original=(v['notations'].get('ipa') or [v['term']])[0]
            ipa=ipa_text(original)
            rendered[key]={'pinyin':v['term'],'ipa':ipa,'method':'original notation retained','original_notations':v['notations']}
            if supported_tones(ipa) and not any(x in ipa for x in ['~','～','∼']):
                fallback.append({'mode':'grammar','text':ipa});fallback_keys.append(key)
    for key,result in zip(fallback_keys,convert(fallback)):
        if result.get('accent') and not result.get('error'):
            rendered[key]['pinyin']=result['accent'];rendered[key]['method']='source IPA converted to display spelling'
    morph={
      'mā':('mā','ma⁵⁵'),'xí':('xí','ɕi²⁴'),'xi':('xí','ɕi²⁴'),
      'niě':('niě','ɲie²¹'),'niexi':('niexi','nie ɕi'),'tā tī':('tā tī','tʰa⁵⁵ tʰi⁵⁵'),
      'dá':('dá','ta²⁴'),'dǒ':('dǒ','tuɔ²¹'),'lā niē':('lā niē','la⁵⁵ ɲie⁵⁵'),
      'hǔ':('hǔ','xu²¹'),'jī dā niē':('jī dā niē','tɕi⁵⁵ ta⁵⁵ ɲie⁵⁵'),
      'tái':('tái','tʰai²⁴')}
    lines=['# 60 例挑战集：候选译式（含审阅更正）','',
      '审阅更正：开瓶器等八处泛称事物表达已改用 niexi 独立指称，不再机械补“东西”。niexi 保留来源的无调记音，调值尚未落实。c12 的 yǎn’gócě 是“雨水”，且“挡”来自仙仁；该草案未获确认。c42、c43 均缺“审判”谓词，只有结构骨架，不能当作完整翻译。c38 已补结果状态；审阅后的形式与原实验候选分别保存，检索分数未改。参见 [本次核读与更正](nie-niexi-review.md)。','',
      '下面是本次混合路线 E 在自然预算下选出的最终候选，供逐例判断。每行给出完整草案、IPA 和所表达的组合意思；未完成项直接保留在候选中。原词形、声调、见证及模型分数见对应审计。','',
      '“词汇齐全”只表示所需词汇槽位均有候选；“形态待核”表示词干、后缀、数量或来源搭配尚未落实。带 33 等当前转换器不能可靠区分的调值保留原记音，不把它改写成 21。泛化后的气味、声音不包含原文所有性质。','',
      '|编号／原文|最终候选（调号拼音；不能可靠转换的词保留原记音）|IPA|组合意思|核验状态|','|---|---|---|---|---|---|']
    all_rows=[]
    for d in docs:
        c=d['case'];r=next(r for r in d['routes'] if r['route']=='E' and r['budget']=='natural');co=r['composition']
        template=co['draft_source_forms']; tokens={}
        # Replace lexical tokens first, so grammatical ci cannot alter a root.
        for n,v in enumerate(sorted(co['selected'].values(),key=lambda v:-len(v['term']))):
            marker=f'⟪{n}⟫';template=template.replace(v['term'],marker);tokens[marker]=rendered[v['record_id']]
        pin=ipa=template
        local=dict(morph)
        predicates={x['query'] for x in r['plan']['analysis']['components'] if x['role']=='predicate'}
        if '喝' in predicates:local['ci']=('cǐ','tsʰi²¹')  # Tian:444 drink-object example
        elif '吃' in predicates:local['ci']=('cī','tsʰi⁵⁵')  # Tian:444 food-object example
        else:local['ci']=('ci〔调未定〕','tsʰi〔调未定〕')
        for key,(accent,phonetic) in sorted(local.items(),key=lambda item:-len(item[0])):
            pattern=r'(?<!\S)'+re.escape(key)+r'(?!\S)'
            pin=re.sub(pattern,lambda m:accent,pin);ipa=re.sub(pattern,lambda m:phonetic,ipa)
        for marker,v in tokens.items():
            pin=pin.replace(marker,v['pinyin']);ipa=ipa.replace(marker,v['ipa'])
        gaps={'[predicate]':'〔谓词未定〕','[head]':'〔中心词未定〕','[landmark]':'〔参照物未定〕',
              '[relation]':'〔方位词未定〕','[result predicate]':'〔结果谓词未定〕',
              '[recent completion/state choice]':'〔近期完成／结果状态形式未定〕','[two + classifier]':'〔二＋量词未定〕'}
        for key,val in gaps.items():pin=pin.replace(key,val);ipa=ipa.replace(key,val)
        status=[]
        if not co['lexical_complete']:status.append('未完成：'+','.join(co['missing_components']))
        else:status.append('词汇齐全')
        if co['unresolved_realization'] or '未定' in pin:status.append('形态／搭配待核')
        if co['meaning_losses']:status.append('有语义泛化')
        if any(v['method']=='original notation retained' for v in tokens.values()):status.append('含原记音')
        components=r['plan']['analysis']['components']; family=co['family']
        if family=='semantic_generalization':
            display_meaning='＋'.join(x['query'] for x in components if x['required'])+'（泛指）'
        elif family=='negative_ability':
            display_meaning='不能'+next(x['query'] for x in components if x['role']=='predicate')+'（能力否定）'
        elif family=='spatial_composition':
            display_meaning='＋'.join(x['query'] for x in components if x['required'])
        elif family in {'event_agent','event_object','function_object','role_relative','negative_relative','abstract_event'}:
            display_meaning='＋'.join(x['query'] for x in components if x['required'])
            if co['roles'].get('head'):display_meaning+='；中心词角色：'+{'agent':'施事','patient':'受事','instrument':'用途物'}.get(co['roles']['head'],co['roles']['head'])
            if co['features'].get('negation'):display_meaning+='；保留否定'
        else:display_meaning=r['plan']['analysis']['meaning']
        row={'id':c['id'],'expression':c['expression'],'pinyin_candidate':pin,'ipa_candidate':ipa,
             'meaning':display_meaning,'status':status,'roles':co['roles'],'features':co['features'],
             'audit':c['id']+'.md','selected_word_renderings':tokens,'grammar':co['grammar']}
        if c['id'] in revisions:
            row['original_measured_composition']=revisions[c['id']]
            row['reviewed_composition']=co
            row['review_basis']='泛称事物中心词改为独立名物化；使用原实验候选重新组合，未重新检索。niexi 保留无调形式，不跨来源补调。'
            row['meaning']=display_meaning.replace('＋东西','')
        if c['id'] in reviews:
            row['original_measured_candidate']={'pinyin':pin,'ipa':ipa}
            row.update(reviews[c['id']])
            pin,ipa,status=row['pinyin_candidate'],row['ipa_candidate'],row['status']
        all_rows.append(row)
        cells=[f"[{c['id']} {c['expression']}]({c['id']}.md)",pin,'/'+ipa+'/',row['meaning'],'；'.join(status)]
        lines.append('|'+ '|'.join(str(x).replace('|','／').replace('\n',' ') for x in cells)+'|')
    lines+=['','名词化的选择随语义角色而变：ma 指施事人；玩＋xi 指关联事物；喝＋ci 指动作涉及的事物。审判两例的词汇缺口仍在，但施事与受事草案已经采用不同构式。','',
       '本表的读音展示使用固定数据版本附带的来源转换器；词形来源和未转换的原始记音仍保存在 [rendered-candidates.json](rendered-candidates.json)。形态是构式拟用，不把整句当成词典原例。','',
       '质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。','']
    (root/'challenge-translations.md').write_text('\n'.join(lines))
    (root/'rendered-candidates.json').write_text(json.dumps({'source_revision':'072046c39261cf536e0ce29f06779cd3eeb99219','cases':all_rows},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
