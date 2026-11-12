"""Lightweight Tujia synonym lookup QA (no model, no network)."""
from __future__ import annotations

import importlib.util
import json
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/lightweight-synonym-search.py"
CONCEPTS = ROOT / "skills/tujia-synonym-lite/concepts.json"


def load_module():
    spec = importlib.util.spec_from_file_location("test_tujia_synonym_lite_impl", SCRIPT)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def test_five_targets_expand_without_embedding():
    mod = load_module()
    concepts = json.loads(CONCEPTS.read_text(encoding="utf-8"))
    expected = {
        "路人": ("路", "人"),
        "香味": ("气味", "闻"),
        "玩具": ("玩", "东西"),
        "饮料": ("喝的东西", "水"),
        "令人费解": ("不知道", "理解"),
        "经济损失": ("钱", "赔偿"),
    }
    for original, must_include in expected.items():
        _, choices = mod.candidate_queries(original, concepts, max_queries=12)
        queries = [x["query"] for x in choices]
        assert queries[0] == original
        for candidate in must_include:
            assert candidate in queries, (original, candidate, queries)


def test_source_priority_and_dialect():
    m = load_module()
    assert m.source_priority("brassett-2006") < m.source_priority("brassett-2004")
    assert m.source_priority("brassett-2004") < m.source_priority("other")
    assert m.is_in_dialect("北部", "north")
    assert not m.is_in_dialect("南部", "north")
    assert m.is_in_dialect("南部", "south")
    assert not m.is_in_dialect("未标明", "north")


def test_exact_lookup_and_provenance(tmp_path):
    mod = load_module()
    # A minimal manifest/shard fixture exercises actual FNV, shard integrity,
    # source alias sorting and structured outputs, without a BGE model.
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("bizic_static_shards", ROOT / "scripts/export-readable-lexicon.py")
    exp = module_from_spec(spec)
    spec.loader.exec_module(exp)
    key = "钱"
    bucket = exp.bucket_of(key)
    rows = [
        {"k": key, "r": ["w1", "a1", "s04", "tong", "钱", "money", "n", "北部", "", "", {}]},
        {"k": key, "r": ["w2", "a2", "s06", "tuan", "钱", "money", "n", "北部", "", "", {}]},
    ]
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()
    shard = f"{bucket}-000.jsonl"
    (tmp_path / shard).write_bytes(content)
    manifest = {
        "revision": "test",
        "record_fields": ["entry_id", "attestation_id", "source", "term", "zh", "en",
                          "pos", "dialect", "locator", "source_ref", "notations"],
        "sources": {
            "s04": {"canonical_id": "brassett-2004", "title": "Brassett 2004"},
            "s06": {"canonical_id": "brassett-2006", "title": "Brassett 2006"},
        },
        "buckets": {bucket: [{"path": shard, "bytes": len(content),
                              "sha256": hashlib.sha256(content).hexdigest()}]},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = mod.run("钱", tmp_path, CONCEPTS)
    assert result["mode"] == "skill_based" and not result["embedding_run"]
    assert result["candidate_results"][0]["dialect_filtered_hits"] == 2
    got = result["candidate_results"][0]["witnesses"]
    assert got[0]["canonical_source"] == "brassett-2006"
    assert got[0]["attestation_id"] == "a2"


def test_cli_five_examples_on_real_shards_if_present():
    manifest = ROOT / "skills/translate-tujia/lexicon/manifest.json"
    if not manifest.exists():
        return  # Bundle deliberately excludes optional 16 MB lexicon.
    for q in ("路人", "香味", "玩具", "饮料", "令人费解"):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), q, "--max-queries", "10",
             "--limit-per-query", "2"], capture_output=True, text=True, check=True
        )
        report = json.loads(run.stdout)
        assert report["mode"] == "skill_based"
        assert report["candidate_results"][0]["query"] == q
        assert report["embedding_run"] is False
