"""Fast standard-data checks for readable shards and complete bilingual vectors."""
import gzip
import json

import numpy as np
import pytest

from tujia_lex.index import Index, build_index, semantic_texts

# The standalone exporter uses no model, network, or external data.
import importlib.util
from pathlib import Path


def exporter():
    path = Path(__file__).resolve().parents[1] / "scripts/export-readable-lexicon.py"
    spec = importlib.util.spec_from_file_location("readable_lexicon", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_export_includes_every_attestation_and_no_cross_source_notation(tmp_path):
    source = tmp_path / "dictionary.json.gz"
    words = [{"id": "w0", "attestations": [
        {"id": "a1", "source": "brassett-2006", "term": "gaf", "zh": "吃；吃饭",
         "en": "to eat; consume", "pos": "vt.", "dialect": "北部"},
        {"id": "a2", "source": "south-dictionary", "term": "gga", "zh": "吃", "en": "eat", "dialect": "南部"}
    ], "notations": {"ye": [
        {"text": "gaf", "attestationIds": ["a1"]},
        {"text": "gga", "attestationIds": ["a2"]}
    ]}}]
    source.write_bytes(gzip.compress(json.dumps({"words": words}, ensure_ascii=False).encode()))
    mod = exporter()
    output = tmp_path / "lexicon"
    manifest = mod.build(source, output, revision="test-commit", max_bytes=4096)
    assert manifest["dictionary_entries"] == 1
    assert manifest["dictionary_attestations"] == 2
    assert all(info["bytes"] <= 4096 for files in manifest["buckets"].values() for info in files)
    eaten = mod.lookup(output, "吃")
    assert {r[1] for r in eaten} == {"a1", "a2"}
    assert mod.lookup(output, "consume")[0][1] == "a1"
    assert mod.lookup(output, "GAF")[0][1] == "a1"
    assert mod.lookup(output, "  吃饭  ")[0][1] == "a1"
    assert mod.lookup(output, "gga")[0][10]["ye"] == ["gga"]
    assert mod.lookup(output, "gaf")[0][10]["ye"] == ["gaf"]
    assert mod.lookup(output, "nonexistent") == []


def test_static_export_checksum_detects_corruption(tmp_path):
    source = tmp_path / "dictionary.json.gz"
    source.write_bytes(gzip.compress(json.dumps({"words": [{"id": "a", "attestations": [
        {"id": "x", "source": "s", "term": "x", "zh": "好"}]}]}).encode()))
    mod = exporter()
    output = tmp_path / "lexicon"
    m = mod.build(source, output, max_bytes=4096)
    part = m["buckets"][mod.bucket_of("好")][0]["path"]
    (output / part).write_text("tampered\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        mod.lookup(output, "好")


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
