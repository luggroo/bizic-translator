from pathlib import Path
import pytest

from tujia_lex.pronunciation import PronunciationLookup, load_static, parse


def record(form, meaning='test', aid='a', original=None):
    return {'entry_id': aid, 'attestation_id': aid, 'source': 'test',
            'canonical_source': 'brassett-2006', 'term': form,
            'source_term': original or form, 'dialect': '北部',
            'zh': meaning, 'en': '', 'notations': {'accent': [form]}}


@pytest.mark.parametrize('query,target', [('hxiē', 'yē'), ('yē', 'hxiē'),
                                          ('gī', 'gēi'), ('gēi', 'gī'),
                                          ('dā', 'dà'), ('dà', 'dā'),
                                          ('lǎdōng', 'ládōng'), ('ládōng', 'lǎdōng'),
                                          ('lánié', 'lániē'), ('lániē', 'lánié')])
def test_documented_variants(query, target):
    result = PronunciationLookup([record(target)]).search(query)
    assert result['whole'] and result['whole'][0]['changes']
    assert result['whole'][0]['matched_form'] == target


@pytest.mark.parametrize('query,target', [('tī', 'tēi'), ('dǎ', 'dá'), ('dā', 'dá'),
                                          ('hxiē', 'gī')])
def test_unlicensed_changes_are_not_general_tone_or_sound_erasure(query, target):
    assert not PronunciationLookup([record(target)]).search(query)['whole']


def test_affix_tones_need_explicit_option_and_bound_witness():
    lookup = PronunciationLookup([record('-hīcē', '不起')])
    assert not lookup.search('hěicé')['whole']
    hit = lookup.search('hěicé', affix=True)['whole'][0]
    assert hit['matched_form'] == '-hīcē'
    assert hit['notations']['accent'] == ['-hīcē']
    assert any('affix tone' in c for c in hit['changes'])
    assert not PronunciationLookup([record('hīcē')]).search('hěicé', affix=True)['whole']


def test_whole_word_does_not_suppress_word_boundary_alternatives():
    # Artificial forms and labels test search behavior, not Tujia vocabulary.
    lookup = PronunciationLookup([record('lǎmī', 'WHOLE', 'whole'),
                                  record('lā', 'PART_A', 'a'), record('mí', 'PART_B', 'b')])
    result = lookup.search('lami')
    assert result['whole'][0]['zh'] == 'WHOLE'
    assert any([h['zh'] for h in p['pieces']] == ['PART_A', 'PART_B']
               for p in result['segmentations'])


def test_actual_dictionary_recovers_a_source_tone_variant():
    directory = Path(__file__).resolve().parents[1]/'skills/translate-tujia/lexicon'
    if not directory.exists():
        pytest.skip('Optional static dictionary not packaged')
    lookup = PronunciationLookup(load_static(directory))
    result = lookup.search('soxtir', notation='ye')
    assert any(h['attestation_id'] == 'stedt-rn-453764' for h in result['whole'])
    assert result['embedding_run'] is False


def test_ipa_tones_preserve_unlisted_31_instead_of_erasing_it():
    data = record('xī')
    data['notations'] = {'ipa': ['ɕi³¹']}
    lookup = PronunciationLookup([data])
    assert lookup.search('ɕi³¹', 'ipa')['whole']
    assert not lookup.search('ɕi³³', 'ipa')['whole']


def test_source_tone_values_are_still_reported_within_a_tone_class():
    data = record('jiè')
    data['notations'] = {'ipa': ['tɕie⁵¹']}
    hit = PronunciationLookup([data]).search('tɕie⁵³', 'ipa')['whole'][0]
    assert 'source tone values 53/51' in hit['changes'][0]
    assert hit['matched_form'] == 'tɕie⁵¹'


def test_notation_is_explicit_and_inputs_are_bounded():
    assert [(s.body, s.tone) for s in parse('soxtir', 'ye')] == [('so', 'H'), ('ti', 'L')]
    with pytest.raises(ValueError):
        parse('soti', 'ye')
    lookup = PronunciationLookup([])
    with pytest.raises(ValueError):
        lookup.search('x'*121)
    with pytest.raises(ValueError):
        lookup.search('dā', limit=101)
    with pytest.raises(ValueError):
        parse("'ā")
