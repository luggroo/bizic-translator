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

def test_rounded_and_unrounded_medials_stay_distinct():
 for raw,ipa in [('tɕia1','tɕia⁵⁵'),('tɕya1','tɕya⁵⁵'),('tɕian1','tɕiɛ̃⁵⁵'),('tɕyan1','tɕyɛ̃⁵⁵'),('tɕiei1','tɕiɛ⁵⁵'),('tɕyei1','tɕyɛ⁵⁵')]:
  r=map_reading(['jishou',raw,'',''],'north');assert r['ipa']==ipa
 assert map_reading(['jishou','tɕyan1','',''],'north')['romanization']=='jüān'
 assert map_reading(['jishou','y2','',''],'north')['ipa']=='i²¹'
 assert map_reading(['jishou','tɕiei1','',''],'south')['ipa']=='tɕie³³'
 assert map_reading(['jishou','tɕyei1','',''],'south')['ipa']=='tɕye³³'
