"""Offline proposed-loan lookup. A missing character suppresses the whole word."""
from pathlib import Path
from functools import lru_cache
import argparse,gzip,json,re,unicodedata
D=Path(__file__).with_name('loan_data')
ORDER={'north':['yongshun','jishou'],'south':['jiefangyan','jishou']}
INITIALS=sorted('tɕʰ tsʰ tʂʰ pʰ tʰ kʰ dʑ dʐ dz tɕ tʂ ts ȵ ɲ ŋ ɡ g p b t d k m n l f s z ʂ ʐ ɕ ʑ x ɣ v w j ʔ'.split(),key=len,reverse=True)
SUP=str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹')
ON={'tɕʰ':'q','tsʰ':'c','pʰ':'p','tʰ':'t','kʰ':'k','tɕ':'j','ts':'z','p':'b','t':'d','k':'g','m':'m','n':'n','ɲ':'n','ŋ':'ng','l':'l','s':'s','z':'r','ɕ':'x','x':'h','ɣ':'hx','j':'y','w':'w','ʑ':'y','f':'hu','ʔ':"'",'':''}
NR={'i':'i','ɨ':'i','ɿ':'i','a':'a','ia':'ia','u':'u','ai':'ai','iau':'iao','au':'ao','ua':'ua','uai':'uai','ei':'ei','ɔ':'o','uɔ':'o','uei':'ui','iu':'iu','ou':'ou','iɛ':'ie','iɛ̃':'ian','ã':'an','uã':'uan','ĩ':'in','ɜ̃':'en','uɜ̃':'un','ɔ̃':'ong','iɔ̃':'iong','ya':'üa','yɛ':'üe','yɛ̃':'üan'}
SR={'i':'i','ɿ':'i','a':'a','ia':'ia','ai':'ai','ei':'ei','e':'e','au':'au','iau':'iau','ɯ':'eu','ĩ':'in','u':'u','ua':'ua','o':'o','io':'io','iã':'ian','uai':'uai','ẽ':'en','uei':'uei','õ':'on','ã':'an','uã':'uan','ya':'üa','iɯ':'ieu','uẽ':'uen','y':'ü','iõ':'ion','yã':'üan','ỹ':'ün','yẽ':'üen','ye':'üe','ie':'ie'}
@lru_cache(maxsize=1)
def assets():return json.loads(gzip.decompress((D/'characters.json.gz').read_bytes())),json.loads((D/'rules.json').read_text())
def romanize(o,r,t,target):
 ons=ON if target=='north' else dict(ON,b='bb',d='dd',g='gg',dz='zz',**{'dʑ':'jj','ɲ':'ni','f':'f'})
 rims=NR if target=='north' else SR
 if o not in ons or r not in rims:return None
 a,b=ons[o],rims[r]
 if o=='ɲ' and b.startswith('i'):a='n'
 if target=='north' and o=='f' and b.startswith('u'):a='h'
 if not o and b.startswith('i'):a='y'
 if not o and b.startswith('u'):a='w'
 if a=='y' and len(b)>1 and b[0]=='i' and b[1] in 'aeiouü':b=b[1:]
 if a=='w' and len(b)>1 and b[0]=='u' and b[1] in 'aeiouü':b=b[1:]
 if a in ['j','q','x','jj'] and not b.startswith(('i','ü')):b='i'+b
 marks={'55':'̄','24':'́','21':'̌','51':'̀'} if target=='north' else {'33':'','21':'̀','55':'̄','13':'̌'}
 ix=next((b.index(v) for v in 'aeo' if v in b),None)
 if ix is None:ix=next((i for i in range(len(b)-1,-1,-1) if b[i] in 'iuüı'),None)
 if ix is None:return None
 return unicodedata.normalize('NFC',a+b[:ix+1]+marks[t]+b[ix+1:])
def map_reading(row,target):
 source,raw,sense,hist=row;m=re.fullmatch(r'(.+?)([1-6])(?:[-=])?',raw)
 if not m:return None
 seg=unicodedata.normalize('NFC',m[1]);o=next((x for x in INITIALS if seg.startswith(x)),'');r=seg[len(o):];rules=assets()[1]
 if target=='north':
  mapping=rules['north_rimes'];new={'b':'pʰ','d':'tʰ','ɡ':'kʰ','dz':'tsʰ','dʑ':'tɕʰ','ȵ':'ɲ'}.get(o,o)
 else:
  mapping=rules['south_jiefangyan_rimes' if source=='jiefangyan' else 'south_jishou_rimes'];new={'ɡ':'g','ȵ':'ɲ','tʂ':'ts','dʐ':'dz','ʂ':'s','ʐ':'z','v':'w'}.get(o,o)
 rr=mapping.get(r)
 if rr is None:return None
 if target=='south' and source=='jiefangyan' and hist=='入' and r=='ɛi':rr='ei'
 if target=='north' and rr=='i':
  if new in ['ts','tsʰ','s','z']:rr='ɿ'
  elif new in ['k','kʰ','ŋ','x','ɣ']:rr='ɨ'
 tone=rules[target+'_tones'].get(m[2])
 if not tone:return None
 accent=romanize(new,rr,tone,target)
 if not accent:return None
 return dict(source=source,source_ipa=raw,sense=sense,historical_tone=hist or None,source_category=m[2],ipa=new+rr+tone.translate(SUP),romanization=accent,tone=tone,changes=[o+'→'+new,r+'→'+rr],method='proposed-loan-mapping')
def character_candidates(c,target):
 table=assets()[0];rows=[];seen=set()
 for canonical in table['aliases'].get(c,[c]):
  for row in table['entries'].get(canonical,[]):
   if row[0] in ORDER[target] and tuple(row) not in seen:rows.append((row,map_reading(row,target)));seen.add(tuple(row))
 # Northern Tujia distinguishes n/l before i. Yongshun merges some of these
 # characters as ȵi (李/梨 versus 泥); use the same character's Jishou li
 # witness to recover l, rather than changing every ȵi into li.
 recover_l = target=='north' and any(r[0]=='yongshun' and re.fullmatch(r'ȵi[1-6]',r[1]) for r,m in rows)
 preferred = [(r,m) for r,m in rows if recover_l and r[0]=='jishou' and re.fullmatch(r'li[1-6]',r[1]) and m]
 if preferred:
  for r,m in preferred:m['selection_reason']='i前保留n/l区别：吉首本字li校正永顺合流ȵi'
 return sorted(rows,key=lambda pair:-1 if pair in preferred else ORDER[target].index(pair[0][0]))
def sense_matches(c,sense,context):
 table=assets()[0]
 def canon(s):return ''.join(min(table['aliases'].get(x,[x])) for x in s)
 context=canon(context);expanded=canon(sense.replace('～',c).replace('~',c))
 return bool(context) and any(t in context or context in t for t in re.findall(r'[\u3400-\u9fff]{2,}',expanded))
def lookup(word,target='north',sense='',choices=None):
 if target not in ORDER:raise ValueError('target must be north or south')
 if not word or not all('\u3400'<=c<='\u9fff' or '\U00020000'<=c<='\U000323af' for c in word):raise ValueError('Pass one Han-character word')
 base=dict(word=word,target=target,ipa=None,romanization=None,display=word,method='proposed-loan-mapping');choices=choices or {};raw=[character_candidates(c,target) for c in word]
 missing=[dict(position=i,character=word[i]) for i,rs in enumerate(raw) if not rs]
 if missing:return dict(base,status='missing-character',missing=missing)
 details=[];selected=[];unresolved=[]
 for i,(c,rows) in enumerate(zip(word,raw)):
  available=[(r,m) for r,m in rows if m];choice=choices.get(i,choices.get(str(i)))
  if choice:available=[(r,m) for r,m in available if r[1]==choice]
  else:
   matches=[(r,m) for r,m in available if sense_matches(c,r[2],sense or word)]
   if matches:available=matches
  if not available:unresolved.append(i);details.append(dict(position=i,character=c,status='invalid-choice' if choice else 'unmapped-sound'));continue
  source=available[0][0][0];mapped=[m for r,m in available if r[0]==source]
  if len({m['ipa'] for m in mapped})!=1:unresolved.append(i);details.append(dict(position=i,character=c,status='ambiguous',candidates=mapped));continue
  chosen=dict(mapped[0],senses=sorted({m['sense'] for m in mapped if m['sense']}));selected.append(chosen);details.append(dict(position=i,character=c,status='resolved',reading=chosen))
 if unresolved:return dict(base,status='needs-selection',unresolved_positions=unresolved,characters=details)
 return dict(base,status='resolved',ipa=' '.join(x['ipa'] for x in selected),romanization=' '.join(x['romanization'] for x in selected),display=' '.join(x['romanization'] for x in selected),characters=details)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('word');p.add_argument('--target',choices=list(ORDER),default='north');p.add_argument('--sense',default='');p.add_argument('--choices',default='{}');a=p.parse_args()
 try:r=lookup(a.word,a.target,a.sense,json.loads(a.choices))
 except ValueError as e:p.error(str(e))
 print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
