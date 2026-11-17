#!/usr/bin/env python3
"""Check generated gloss labels against the fixed Markdown inventory."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'skills/translate-tujia'
TABLE=ROOT/'references/output.md'
LABEL=re.compile(r'(?<![A-Za-z0-9])(?:[123](?:SG|PL)|[A-Z][A-Z0-9]*(?:\.[A-Z][A-Z0-9]*)*)(?![A-Za-z0-9])')
def inventory():
 text=TABLE.read_text().split('<!-- fixed-gloss-labels:start -->',1)[1].split('<!-- fixed-gloss-labels:end -->',1)[0]
 return {line.split('|')[1].strip() for line in text.splitlines() if line.startswith('|') and re.fullmatch(r'[A-Z0-9]+',line.split('|')[1].strip())}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('files',nargs='+',type=Path);args=ap.parse_args();allowed=inventory();errors=[];used=set()
 def check(label,where):
  used.add(label)
  for part in label.split('.'):
   if part not in allowed:errors.append({'location':where,'label':label,'unknown_part':part})
 for path in args.files:
  d=json.loads(path.read_text())
  for label in d.get('abbreviations',{}):check(label,str(path)+':abbreviations')
  for i,c in enumerate(d.get('clauses',[]),1):
   units=c.get('target_units',[c])
   for j,u in enumerate(units,1):
    for k,t in enumerate(u.get('tokens',[]),1):
     for label in LABEL.findall(t.get('gloss','')):
      if label=='I':continue  # English lexical first-person pronoun.
      check(label,f'{path}:{i}.{j}.{k}')
  declared=set(d.get('abbreviations',{}));used_here={x for c in d.get('clauses',[]) for u in c.get('target_units',[c]) for t in u.get('tokens',[]) for x in LABEL.findall(t.get('gloss','')) if x!='I'}
  for label in used_here-declared:errors.append({'location':str(path)+':abbreviations','label':label,'error':'used label missing from output abbreviation list'})
 print(json.dumps({'passed':not errors,'fixed_labels':len(allowed),'used':sorted(used),'errors':errors},ensure_ascii=False,indent=2))
 return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
