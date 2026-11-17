from pathlib import Path
import json,gzip,csv,re,hashlib
from opencc import OpenCC
R=Path(__file__).resolve().parents[1];S=R/'data/loan-sources';O=R/'src/tujia_lex/loan_data'
def build():
 a,b=OpenCC('s2t'),OpenCC('t2s');entries={};aliases={}
 def add(c,row):
  if len(c)!=1 or c=='□':return
  if row not in entries.setdefault(c,[]):entries[c].append(row)
  for v in sorted({c,a.convert(c),b.convert(c)}):
   if len(v)==1:aliases.setdefault(v,set()).add(c)
 for name in ['yongshun','jishou']:
  for l in (S/(name+'.tsv')).read_text().splitlines():
   if not l or l.startswith('#'):continue
   r=l.split('\t');add(r[0],[name,r[1],r[2] if len(r)>2 else '', ''])
 for label,raw,hist in json.loads((S/'jiefangyan.json').read_text()):
  c=re.split('[（(]',label)[0]
  for v in sorted({c,a.convert(c)}):add(v,['jiefangyan',raw,label if c!=label else '',hist])
 obj={'entries':entries,'aliases':{k:sorted(v) for k,v in aliases.items()},'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(S / name for name in ('yongshun.tsv', 'jishou.tsv', 'jiefangyan.json', 'UPSTREAM-LICENSE'))}}
 raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();(O/'characters.json.gz').write_bytes(gzip.compress(raw,mtime=0));print(len(entries),len(gzip.compress(raw,mtime=0)))
if __name__=='__main__':build()
