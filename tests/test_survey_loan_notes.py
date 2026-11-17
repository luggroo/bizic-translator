import gzip
import json
from tujia_lex.data import survey_records


def test_survey_notes_follow_public_word_ids_without_touching_source_rows(tmp_path):
    site = tmp_path / 'site'
    site.mkdir()
    name = 'survey.json.gz'
    (site / 'yubao-manifest.json').write_text(json.dumps([name]))
    raw = [['1', '甲', 'ka33', '原注'], ['2', '乙', 'pa21']]
    (site / name).write_bytes(gzip.compress(json.dumps({
        'point': '60756', 'dialect': '北部', 'words': raw,
        'sentences': [['1', '例句', 'ka33 pa21']],
    }).encode()))
    note = {'id': 'chinese-loan-yubao-60756-v-0001', 'donor': '甲'}
    lexical, sentences = survey_records(tmp_path, {'yubao-60756-v-0001': [note]})
    assert lexical[0]['editorial_notes'] == [note]
    assert lexical[1]['editorial_notes'] == []
    assert [r['raw_row'] for r in lexical] == raw
    assert lexical[0]['id'] == 'survey-word:60756:1'
    assert 'editorial_notes' not in sentences[0]
