"""Fast standard-data checks for readable shards and complete bilingual vectors."""
import gzip
import json

import numpy as np
import pytest

from tujia_lex.index import Index, build_index, semantic_texts

# Querying needs no model, network or JavaScript runtime. Exporting uses the
# matching site's converter; unit fixtures supply already-resolved spellings.
import importlib.util
from pathlib import Path


def exporter():
    path = Path(__file__).resolve().parents[1] / "scripts/export-readable-lexicon.py"
    spec = importlib.util.spec_from_file_location("readable_lexicon", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def display_exporter(tmp_path, monkeypatch):
    mod = exporter()
    site = tmp_path / 'site'
    site.mkdir()
    for name in mod.CONVERTER_FILES:
        (site / name).write_text('// fixture')

    def resolved(data, _site):
        result = {}
        for entry in data['words']:
            for att in entry['attestations']:
                linked = {k: [v for v in values if att['id'] in v['attestationIds']]
                          for k, values in entry.get('notations', {}).items()}
                result[att['id']] = {'accent': linked.get('accent', []),
                                     'ipa': [v['text'] for v in linked.get('ipa', [])]}
        return result

    monkeypatch.setattr(mod, 'convert_display_forms', resolved)
    return mod, site


def test_static_export_includes_every_attestation_and_no_cross_source_notation(tmp_path, display_exporter):
    source = tmp_path / "dictionary.json.gz"
    words = [{"id": "w0", "attestations": [
        {"id": "a1", "source": "brassett-2006", "term": "gaf", "zh": "吃；吃饭",
         "en": "to eat; consume", "pos": "vt.", "dialect": "北部"},
        {"id": "a2", "source": "south-dictionary", "term": "gga", "zh": "吃", "en": "eat", "dialect": "南部"}
    ], "notations": {"ye": [
        {"text": "gaf", "attestationIds": ["a1"]},
        {"text": "gga", "attestationIds": ["a2"]}
    ], 'accent': [
        {'text': 'gá', 'attestationIds': ['a1'], 'profile': 'north'},
        {'text': 'ggā', 'attestationIds': ['a2'], 'profile': 'south'}
    ], 'ipa': [{'text': 'ka²⁴', 'attestationIds': ['a1']}]
    }}]
    source.write_bytes(gzip.compress(json.dumps({"words": words}, ensure_ascii=False).encode()))
    mod, site = display_exporter
    output = tmp_path / "lexicon"
    manifest = mod.build(source, output, revision="test-commit", max_bytes=4096, site_root=site)
    assert manifest['format'] == 2
    assert manifest["dictionary_entries"] == 1
    assert manifest["dictionary_attestations"] == 2
    assert all(info["bytes"] <= 4096 for files in manifest["buckets"].values() for info in files)
    eaten = mod.lookup(output, "吃")
    assert {r[1] for r in eaten} == {"a1", "a2"}
    assert mod.lookup(output, "consume")[0][1] == "a1"
    assert mod.lookup(output, "GAF")[0][1] == "a1"
    assert mod.lookup(output, "  吃饭  ")[0][1] == "a1"
    north = dict(zip(manifest['record_fields'], mod.lookup(output, 'gaf')[0]))
    south = dict(zip(manifest['record_fields'], mod.lookup(output, 'gga')[0]))
    assert north['term'] == 'gá' and south['term'] == 'ggā'
    assert north['source_term'] == 'gaf' and south['source_term'] == 'gga'
    assert north['notations'] == {'accent': ['gá'], 'ipa': ['ka²⁴']}
    assert south['notations'] == {'accent': ['ggā']}
    assert north['term_notation'] == south['term_notation'] == 'accent'
    assert mod.lookup(output, 'gá')[0][1] == 'a1'
    assert mod.lookup(output, 'ggā')[0][1] == 'a2'
    assert mod.lookup(output, "nonexistent") == []


def test_static_export_checksum_detects_corruption(tmp_path, display_exporter):
    source = tmp_path / "dictionary.json.gz"
    source.write_bytes(gzip.compress(json.dumps({"words": [{"id": "a", "attestations": [
        {"id": "x", "source": "s", "term": "x", "zh": "好"}]}]}).encode()))
    mod, site = display_exporter
    output = tmp_path / "lexicon"
    m = mod.build(source, output, max_bytes=4096, site_root=site)
    part = m["buckets"][mod.bucket_of("好")][0]["path"]
    (output / part).write_text("tampered\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        mod.lookup(output, "好")


def test_static_ipa_fallback_and_missing_pronunciation(tmp_path, display_exporter):
    mod, site = display_exporter
    source = tmp_path / 'dictionary.json.gz'
    data = {'words': [{'id': 'w', 'attestations': [
        {'id': 'a', 'term': 'raw-a', 'zh': '甲'},
        {'id': 'b', 'term': 'raw-b', 'zh': '乙'}],
        'notations': {'ipa': [{'text': '/ɣa²¹/', 'attestationIds': ['a']}]}}]}
    source.write_bytes(gzip.compress(json.dumps(data).encode()))
    output = tmp_path / 'lexicon'
    m = mod.build(source, output, site_root=site)
    a = dict(zip(m['record_fields'], mod.lookup(output, '甲')[0]))
    b = dict(zip(m['record_fields'], mod.lookup(output, '乙')[0]))
    assert (a['term'], a['term_notation']) == ('/ɣa²¹/', 'ipa')
    assert (b['term'], b['term_notation']) == ('⟦待核：读音⟧', 'missing')
    assert m['display_counts'] == {'accent': 0, 'ipa': 1, 'missing': 1}


def test_legacy_static_data_requires_rebuild(tmp_path):
    from tujia_lex.static import StaticLexicon
    (tmp_path / 'manifest.json').write_text(json.dumps({'format': 1, 'buckets': {}}))
    with pytest.raises(ValueError, match='Rebuild static lexicon'):
        StaticLexicon(tmp_path)
    with pytest.raises(ValueError, match='Rebuild static lexicon'):
        exporter().lookup(tmp_path, '甲')


def test_real_site_conversion_and_complete_static_coverage(tmp_path, repo):
    site = repo / 'site'
    if not (site / 'dictionary.json.gz').exists():
        pytest.skip('Pass --data-root for the real versioned site converters')
    mod = exporter()
    output = tmp_path / 'lexicon'
    manifest = mod.build(site / 'dictionary.json.gz', output, site_root=site)
    source = mod.read_dictionary(site / 'dictionary.json.gz')
    expected = {a['id']: a for w in source['words'] for a in w['attestations']}
    actual = {}
    for files in manifest['buckets'].values():
        for info in files:
            for line in (output / info['path']).read_text().splitlines():
                row = dict(zip(manifest['record_fields'], json.loads(line)['r']))
                actual[row['attestation_id']] = row
    assert set(actual) == set(expected)
    for aid, row in actual.items():
        assert row['source_term'] == expected[aid]['term']
        assert set(row['notations']) <= {'accent', 'ipa'}
        if row['term_notation'] == 'accent':
            assert row['term'] == ' / '.join(row['notations']['accent'])
            assert not any(c.isdigit() for c in row['term'])
        elif row['term_notation'] == 'ipa':
            assert row['term'].startswith('/') and row['term'].endswith('/')
        else:
            assert row['term'] == '⟦待核：读音⟧'
    # Legacy source keys and the generated spelling must retrieve the same witness.
    sample = next(r for r in actual.values() if r['term_notation'] == 'accent'
                  and r['term'] != r['source_term'] and len(r['term']) < 40)
    assert sample['attestation_id'] in {r[1] for r in mod.lookup(output, sample['term'], limit=100)}
    assert sample['attestation_id'] in {r[1] for r in mod.lookup(output, sample['source_term'], limit=100)}
    from tujia_lex.static import StaticLexicon
    exposed = next(r for r in StaticLexicon(output).search(sample['source_term'], top_k=100, dialect='any')
                   if r['attestation_id'] == sample['attestation_id'])
    assert exposed['forms'] == [sample['term']]
    assert exposed['attestations'][0]['source_term'] == sample['source_term']

    # The real adapter must give each witness the same result when placed in a
    # merged Northern/Southern entry as when converted on its own.
    singles = []
    for dialect in ('北部', '南部'):
        aid = next(aid for aid, row in actual.items() if row['term_notation'] == 'accent'
                   and row['dialect'] == dialect)
        entry = next(w for w in source['words'] if any(a['id'] == aid for a in w['attestations']))
        singles.append({'id': 'mixed-fixture', 'attestations': [expected[aid]],
                        'notations': {k: [v for v in values if aid in v.get('attestationIds', [])]
                                      for k, values in entry.get('notations', {}).items()}})
    separate = mod.convert_display_forms({'words': singles}, site)
    merged = {'id': 'mixed-fixture', 'attestations': [w['attestations'][0] for w in singles],
              'notations': {k: [v for w in singles for v in w['notations'].get(k, [])]
                            for k in {k for w in singles for k in w['notations']}}}
    assert mod.convert_display_forms({'words': [merged]}, site) == separate


class TinyEncoder:
    identity = {"model": "tiny", "revision": "test", "weights_sha256": "dummy",
                "pooling": "CLS", "normalize": True, "query_instruction": "", "max_length": 128}

    def encode(self, texts, batch_size=32, query=False):
        vectors = []
        for text in texts:
            vectors.append([0.0, 1.0] if "wait" in text else [1.0, 0.0])
        return np.array(vectors, dtype="float32")


def test_english_and_chinese_get_independent_semantic_vectors(tmp_path):
    entry = {"id": "lex:e:1", "kind": "lexicon", "record_type": "lexical_sense",
             "entry_id": "e", "text": "等待", "zh": "等待", "en": "to wait", "pos": "v",
             "dialect": "north", "locations": [], "point": "",
             "attestations": [{"id": "a"}, {"id": "b"}],
             "sources": [{"id": "brassett-2006"}], "lexical_fields": ["等待", "to wait"]}
    assert semantic_texts(entry) == ["等待", "to wait"]
    m = build_index([entry], TinyEncoder(), tmp_path / "i")
    assert m["lexical_entry_count"] == 1
    assert m["lexical_attestation_count"] == 2
    assert m["unique_texts"] == 2
    assert m["semantic_fields"].startswith("all Chinese")
    index = Index(tmp_path / "i")
    assert len(index.records[0]["vector_rows"]) == 2
    result = index.search("wait", encoder=TinyEncoder())
    assert result[0]["score"] == 1.0
    assert index.search("to wait", mode="exact")[0]["entry_id"] == "e"
