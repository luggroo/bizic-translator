"""Regression checks for the fixed output-label contract."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check(tmp_path,gloss,abbreviations):
 p=tmp_path/'draft.json';p.write_text(json.dumps({'clauses':[{'target_units':[{'tokens':[{'gloss':gloss}]}]}],'abbreviations':abbreviations},ensure_ascii=False))
 r=subprocess.run([sys.executable,str(ROOT/'scripts/check_gloss_labels.py'),str(p)],capture_output=True,text=True)
 return r.returncode,json.loads(r.stdout)
def test_lexical_meanings_with_grammatical_labels(tmp_path):
 code,result=check(tmp_path,'我 GEN 衣服-PFV',{'GEN':'genitive','PFV':'perfective'})
 assert code==0 and result['passed']
def test_invented_connection_subtype_is_rejected(tmp_path):
 code,result=check(tmp_path,'CONN.SEQ',{'CONN.SEQ':'sequential connective'})
 assert code!=0 and any(e.get('unknown_part')=='SEQ' for e in result['errors'])
def test_removed_lexical_label_is_rejected(tmp_path):
 code,result=check(tmp_path,'COP',{'COP':'copula'})
 assert code!=0 and any(e.get('unknown_part')=='COP' for e in result['errors'])
def test_used_label_requires_abbreviation_entry(tmp_path):
 code,result=check(tmp_path,'缝-PFV',{})
 assert code!=0 and any(e.get('error')=='used label missing from output abbreviation list' for e in result['errors'])
