import gzip
import json
from collections import Counter

import pytest

from tujia_lex.data import collect, lexical_records, longshan_records, read_json, source_catalog, survey_records


def test_real_dictionary_schema_and_all_attestation_links(repo):
    catalog, aliases = source_catalog(repo)
    path = repo / "site/dictionary.json.gz"
    records = lexical_records(path, catalog, aliases)
    words = read_json(path)["words"]
    assert len(words) == 9297  # Public pinned snapshot, not a fabricated miniature dictionary.
    original = {a["id"]: a for w in words for a in w["attestations"]}
    recovered = {a["id"]: a for r in records for a in r["attestations"]}
    assert recovered == original
    assert len(original) == 19577
    for r in records:
        aids = {a["id"] for a in r["attestations"]}
        assert aids == {s["attestation_id"] for s in r["sources"]}
        for ns in r["notations"].values():
            assert all(aids.intersection(n["attestationIds"]) for n in ns)


def test_merged_senses_cannot_leak_southern_notation_or_location(tmp_path):
    data = {"words": [{"id": "merged", "zh": "aggregate", "dialect": "北部", "attestations": [
        {"id": "n", "source": "ns", "term": "native-n", "zh": "好", "en": "good", "dialect": "北部", "pos": "v"},
        {"id": "s", "source": "ss", "term": "native-s", "zh": "坏", "en": "bad", "dialect": "南部", "pos": "n"}],
        "notations": {"ye": [{"text": "south-only", "attestationIds": ["s"]}]}}]}
    p = tmp_path / "dictionary.json"
    p.write_text(json.dumps(data))
    result = lexical_records(p, {"ns": {"locations": ["龙山"]}, "ss": {"locations": ["泸溪"]}})
    n, s = result
    assert (n["zh"], n["dialect"], n["locations"]) == ("好", "north", ["龙山"])
    assert n["notations"]["ye"] == []
    assert s["notations"]["ye"][0]["text"] == "south-only"
    assert s["pos"] == "n"


def test_missing_sense_cannot_inherit_aggregate_gloss(tmp_path):
    p = tmp_path / "dict.json"
    p.write_text(json.dumps({"words": [{"id": "e", "zh": "misleading", "attestations": [
        {"id": "a", "source": "s", "term": "t", "zh": ""}]}]}))
    with pytest.raises(ValueError, match="Missing Chinese sense"):
        lexical_records(p)


def test_real_survey_and_text_records_preserve_originals(repo):
    lex, sentences = survey_records(repo)
    first = read_json(repo / "site/yubao-60757-0.json")["sentences"][0]
    r = next(x for x in sentences if x["id"] == "sentence:60757:" + first[0])
    assert r["zh"] == first[1] and r["ipa"] == first[2] and r["gloss"] == first[3]
    assert r["point"] == "60757" and r["locations"] == ["龙山"] and r["dialect"] == "north"
    assert all(x["dialect"] == "south" for x in lex if x["point"] == "60824")
    original = read_json(repo / "site/longshan-texts.json")[0]
    b = longshan_records(repo)[0]
    assert b["zh"] == original["blocks"][0]["zh"]
    assert b["text"] != original["culturalNote"]


def test_real_collection_ids_types_and_unknown_localities(repo):
    records = collect(repo)
    assert len(records) == len({r["id"] for r in records})
    kinds = Counter(r["kind"] for r in records)
    assert kinds["lexicon"] > 20000 and kinds["construction"] > 700
    assert any(r["dialect"] == "unknown" for r in records)
    brassett = [r for r in records if any(s.get("canonical_id") == "brassett-2004" for s in r.get("sources", []))]
    assert brassett and all(r["locations"] == [] for r in brassett)


def test_construction_evidence_levels_and_grammar_scope(repo):
    from tujia_lex.data import grammar_records, corpus_records
    rules = grammar_records(repo)
    assert all("显示约定" not in r["title"] and "旧小节与新位置" not in r["title"] for r in rules)
    assert any(r["dialect"] == "north" for r in rules)
    assert any(r["dialect"] == "south" for r in rules)
    for r in rules:
        assert r["original"] and r["citation"].startswith("docs/reference-grammar.md:")
        assert r["evidence_level"].startswith("secondary")
    passages = corpus_records(repo)
    assert passages and all(r["original"] and r["alignment_status"] for r in passages)
    assert any(r["locations"] == ["靛房"] for r in passages)


def test_real_tree_classifier_is_not_chinese_small_plant_classifier(repo):
    rows=lexical_records(repo/'site/dictionary.json.gz')
    tree=next(r for r in rows if r['entry_id']=='w1575')
    small=next(r for r in rows if r['entry_id']=='w1750')
    assert tree['zh']=='棵' and tree['pos']=='cl.' and 'trees' in tree['en']
    assert small['zh']=='株' and 'small plants' in small['en']
    passages=[r for r in collect(repo) if r['id']=='corpus:c1.4:11']
    assert 'la2 mong1' in passages[0]['original']


def test_gzip_json_is_detected_by_content(tmp_path):
    p=tmp_path/'dictionary.json'
    expected={'words':[{'id':'compressed-without-gz-suffix'}]}
    p.write_bytes(gzip.compress(json.dumps(expected).encode()))
    assert read_json(p)==expected
