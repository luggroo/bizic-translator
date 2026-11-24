from tujia_lex.loan_lookup import lookup
from tujia_lex.loan_build import map_reading, assets

def test_whole_word_missing():
 r=lookup('百𰻞');assert r['ipa'] is None and r['romanization'] is None and r['display']=='百𰻞' and 'characters' not in r

def test_polyphones():
 assert lookup('难')['status']=='needs-selection'
 assert lookup('难',sense='困难')['ipa']=='lã²¹'
 assert lookup('难',sense='患难')['ipa']=='lã²⁴'
 assert lookup('难',choices={0:'lán'})['ipa']=='lã²⁴'

def test_register():
 assert lookup('家',sense='家庭')['ipa']=='tɕia⁵⁵'

def test_register_sources_and_regional_priority():
 from tujia_lex.loan_lookup import local_readings
 def find(char, tag=None):
  return local_readings(char, tag)['characters'][0]['readings']
 frame = find('架')
 assert [(r['city'], r['source_reading'], r['register'], r['input_key']) for r in frame] == [
  ('吉首', 'ka5', '白', 'ga'), ('吉首', 'tɕia5', '文', 'jia')]
 assert frame[0]['page'] == frame[1]['page'] == 39
 assert frame[0]['note'] == '十字～儿' and frame[1]['note'] == '吵～'
 assert any('葡萄~' in w['note'] and w['source_url'].endswith('#L1703') for w in frame[0]['witnesses'])
 assert [(w['city'], w['register']) for w in frame[1]['witnesses']] == [('吉首','文'), ('重庆',None)]
 assert find('架', '文') == frame[1:]
 assert [(r['input_key'], r['note']) for r in find('稼') if r['city']=='吉首'] == [('ga','庄～'),('jia','庄～')]
 assert {r['source_reading'] for r in find('间') if r['page'] == 39} == {'kan1','kan5','tɕian1','tɕian5'}
 assert {'kai5', 'tɕiei3'} <= {r['source_reading'] for r in find('解', '文')}
 tooth = find('牙', '白')[0]
 assert {w['page'] for w in tooth['witnesses'] if w['source']=='li2002'} == {37,40}
 assert [r['input_key'] for r in find('夹', '白')] == ['ga']
 assert [r['input_key'] for r in find('夾', '文')] == ['jia']
 assert len(find('家')) == 2 and all(r['city'] == '吉首' for r in find('家'))
 assert find('提', '白')[0]['source_reading'] == 'tiaŋ1'
 assert find('漂', '白') == []  # “~白” is an example word.
 assert local_readings('架𰻞')['characters'][1]['readings'] == []

def test_north():
 assert lookup('百')['ipa']=='pei²¹'
 assert lookup('新')['ipa']=='ɕĩ⁵⁵'
 assert lookup('根')['ipa']=='kɜ̃⁵⁵'
 assert map_reading(['jishou','fu1','',''],'north')['romanization']=='hū'
 assert map_reading(['jishou','bi2','',''],'north')['ipa']=='pʰi²¹'

def test_north_i_keeps_l_and_n_distinct():
 assert lookup('李')['ipa']=='li⁵¹'
 assert lookup('李')['romanization']=='lì'
 assert 'source' not in lookup('李')['characters'][0]['reading']
 assert lookup('梨')['ipa']=='li²¹'
 assert lookup('泥')['ipa']=='ȵi²¹'
 assert lookup('女')['ipa']=='ȵi⁵¹'

def test_north_initial_conditioned_in_rime():
 # Baojing-type onset condition is adapted into Northern Tujia nasal vowels,
 # not copied as Chinese coda -n or rounded vowels.
 for initial,tone,expected in [
  ('tin1','55','tɜ̃⁵⁵'),
  ('tʰin1','55','tʰɜ̃⁵⁵'),
  ('din2','21','tʰɜ̃²¹'),
  ('lin2','21','lɜ̃²¹'),
  ('ȵin2','21','ɲĩ²¹'),
  ('pʰin2','21','pʰĩ²¹'),
 ]:
  x=map_reading(['jishou',initial,'',''],'north')
  assert x['tone']==tone and x['ipa']==expected
 assert lookup('亭')['ipa']=='tʰɜ̃²¹'
 assert lookup('停')['ipa']=='tʰɜ̃²¹'
 assert lookup('丁')['ipa']=='tɜ̃⁵⁵'
 assert lookup('零')['ipa']=='lɜ̃²¹' # Yongshun lɛn2 already maps this way
 assert lookup('灵')['ipa']=='lɜ̃²¹' # Jishou lin2
 assert lookup('令')['ipa']=='lɜ̃²⁴' # Jishou lin5 now follows the same rule
 assert lookup('宁')['ipa']=='ȵĩ²¹' # Traditional 寧 alias from Jishou ȵin2
 assert lookup('凝',sense='凝固')['ipa']=='ȵĩ²¹'
 assert lookup('平')['ipa']=='pʰĩ²¹'
 assert lookup('李')['ipa']=='li⁵¹'


def test_south():
 assert lookup('军','south')['ipa']=='tɕỹ³³'
 assert map_reading(['jiefangyan','tʰəɯ3','','上'],'south')['ipa']=='tʰɯ⁵⁵'
 assert map_reading(['jiefangyan','pɛi2','','入'],'south')['ipa']=='pei²¹'
 assert map_reading(['jiefangyan','tɛi4','','去'],'south')['ipa']=='tai¹³'
 for c,t in [('1','33'),('2','21'),('3','55'),('4','13')]:assert map_reading(['jiefangyan','ka'+c,'',''],'south')['tone']==t

def test_variants():
 assert lookup('军','south')['ipa']==lookup('軍','south')['ipa']

def test_backup():
 r=lookup('玩具');assert r['status']=='resolved' and all(set(x['reading']) == {'romanization', 'ipa', 'senses'} for x in r['characters'])

def test_inventory():
 for target,sources in [('north',['yongshun','jishou']),('south',['jiefangyan','jishou'])]:
  count=0
  for rows in assets()[0]['entries'].values():
   for row in rows:
    if row[0] not in sources:continue
    x=map_reading(row,target)
    if x:count+=1
    else:assert 'ɚ' in row[1] or 'ɛ˞' in row[1],row
  assert count>4000

def test_n_l_before_medials_but_y_still_unrounds():
 assert lookup('连')['ipa']=='liã²¹'
 assert lookup('脸')['ipa']=='liã⁵¹'
 assert lookup('年')['ipa']=='ȵiã²¹'
 assert lookup('娘')['ipa']=='ȵiã²¹'
 assert map_reading(['jishou','tɕyan1','',''],'north')['ipa']=='tɕiã⁵⁵'
 assert map_reading(['jishou','tɕya1','',''],'north')['ipa']=='tɕia⁵⁵'
 assert map_reading(['jishou','tɕyei1','',''],'north')['ipa']=='tɕiɛ⁵⁵'

def test_north_all_ian_iang_yan_yang_merge_to_ia_nasal():
 for source,rimes in [('yongshun',['iɛn','iaŋ']),('jishou',['ian','iaŋ','yan','yaŋ'])]:
  for r in rimes:
   x=map_reading([source,'tɕ'+r+'1','',''],'north')
   assert x['ipa']=='tɕiã⁵⁵'
   assert x['romanization']=='jiān'


def test_historical_homophones_fill_missing_graphs():
 assert lookup('朵')['romanization']=='dò'
 assert lookup('朵')['ipa']==lookup('朶')['ipa']
 assert lookup('珙')['romanization']=='gòng'
 assert lookup('女儿会')['status']=='resolved'

def test_only_compiled_table_is_required(tmp_path, monkeypatch):
 import shutil
 import tujia_lex.loan_lookup as runtime
 shutil.copy(runtime.D / 'readings.json.gz', tmp_path / 'readings.json.gz')
 monkeypatch.setattr(runtime, 'D', tmp_path)
 runtime.readings.cache_clear()
 try:
  assert runtime.lookup('珙')['romanization']=='gòng'
  assert runtime.lookup('难',sense='患难')['ipa']=='lã²⁴'
  assert runtime.lookup('百𰻞')['status']=='missing-character'
 finally:
  runtime.readings.cache_clear()

def test_runtime_table_has_no_provenance():
 from tujia_lex.loan_lookup import readings
 for target in ['north','south']:
  assert len(readings()[target])>12000
  for rows in readings()[target].values():
   for row in rows:
    assert set(row)=={'romanization','ipa','sense','priority'}

def test_final_reading_choices_and_orthography():
 assert lookup('难',choices={0:'lán'})['ipa']=='lã²⁴'
 assert lookup('难',choices={0:'lã²⁴'})['ipa']=='lã²⁴'
 assert lookup('難',sense='患難')['ipa']=='lã²⁴'
 assert lookup('难',choices={0:'missing'})['status']=='needs-selection'
