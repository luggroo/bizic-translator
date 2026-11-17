from tujia_lex.loan_lookup import lookup,map_reading,assets

def test_whole_word_missing():
 r=lookup('百𰻞');assert r['ipa'] is None and r['romanization'] is None and r['display']=='百𰻞' and 'characters' not in r

def test_polyphones():
 assert lookup('难')['status']=='needs-selection'
 assert lookup('难',sense='困难')['ipa']=='lã²¹'
 assert lookup('难',sense='患难')['ipa']=='lã²⁴'
 assert lookup('难',choices={0:'lan5'})['ipa']=='lã²⁴'

def test_register():
 assert lookup('家',sense='家庭')['ipa']=='tɕia⁵⁵'

def test_north():
 assert lookup('百')['ipa']=='pei²¹'
 assert lookup('新')['ipa']=='ɕĩ⁵⁵'
 assert lookup('根')['ipa']=='kɜ̃⁵⁵'
 assert map_reading(['jishou','fu1','',''],'north')['romanization']=='hū'
 assert map_reading(['jishou','bi2','',''],'north')['ipa']=='pʰi²¹'

def test_north_i_keeps_l_and_n_distinct():
 assert lookup('李')['ipa']=='li⁵¹'
 assert lookup('李')['romanization']=='lì'
 assert lookup('李')['characters'][0]['reading']['source']=='jishou'
 assert lookup('梨')['ipa']=='li²¹'
 assert lookup('泥')['ipa']=='ɲi²¹'
 assert lookup('女')['ipa']=='ɲi⁵¹'

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
 assert lookup('令')['ipa']=='lɜ̃²⁴' # Jishou lin5 now follows the same rule
 assert lookup('凝',sense='凝固')['ipa']=='ɲĩ²¹'
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
 r=lookup('玩具');assert r['status']=='resolved' and all(x['reading']['source']=='jishou' for x in r['characters'])

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
 assert lookup('年')['ipa']=='ɲiã²¹'
 assert lookup('娘')['ipa']=='ɲiã²¹'
 assert map_reading(['jishou','tɕyan1','',''],'north')['ipa']=='tɕiã⁵⁵'
 assert map_reading(['jishou','tɕya1','',''],'north')['ipa']=='tɕia⁵⁵'
 assert map_reading(['jishou','tɕyei1','',''],'north')['ipa']=='tɕiɛ⁵⁵'

def test_north_all_ian_iang_yan_yang_merge_to_ia_nasal():
 for source,rimes in [('yongshun',['iɛn','iaŋ']),('jishou',['ian','iaŋ','yan','yaŋ'])]:
  for r in rimes:
   x=map_reading([source,'tɕ'+r+'1','',''],'north')
   assert x['ipa']=='tɕiã⁵⁵'
   assert x['romanization']=='jiān'
