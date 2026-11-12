import json
import os
import subprocess
import sys

import numpy as np
import pytest

from tujia_lex.data import collect
from tujia_lex.index import Index, build_index


@pytest.mark.model
def test_actual_model_index_search_provenance_and_cli(repo, tmp_path, real_encoder):
    # Real public records and real embeddings, including both polarities.
    records = collect(repo)
    subset = [r for r in records if r["kind"] == "lexicon" and r["zh"] in {"好", "坏", "聪明", "等候", "织"}][:40]
    subset += [r for r in records if r.get("point") == "60757" and r["kind"] == "construction"][:6]
    target = tmp_path / "index"
    manifest = build_index(subset, real_encoder, target, batch_size=8)
    index = Index(target)
    assert manifest["dimension"] == 768
    assert np.allclose(np.linalg.norm(index.vectors, axis=1), 1, atol=1e-4)
    reused_path = tmp_path / "reused"
    reused = build_index(subset, real_encoder, reused_path, reuse_index=target)
    assert reused["encoded_embeddings"] == 0 and reused["reused_embeddings"] == manifest["unique_texts"]
    assert np.array_equal(Index(reused_path).vectors, index.vectors)
    exact = index.search("等候", mode="exact", top_k=40)
    assert exact and all(r["zh"] == "等候" for r in exact)
    semantic = index.search("守候", encoder=real_encoder, top_k=5)
    assert semantic and all(isinstance(r["score"], float) for r in semantic)
    assert all(r["sources"] for r in semantic)
    sentence = index.search("老师和学生玩", encoder=real_encoder, kind="construction", point="60757")
    assert sentence and all(r["point"] == "60757" and r["ipa"] for r in sentence)
    assert not index.search("老师", mode="exact", kind="construction", point="60824", substring=True)
    assert all(r["dialect"] == "north" for r in index.search("好", encoder=real_encoder, dialect="north"))
    filtered = index.search("守候", encoder=real_encoder, source="brassett-2004", pos="vt.")
    assert all(r["pos"] == "vt." and any(s["canonical_id"] == "brassett-2004" for s in r["sources"]) for r in filtered)
    result = subprocess.run([sys.executable, "-m", "tujia_lex.cli", "search", "守候", "--index", str(target),
                             "--model-path", real_encoder.model_path], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["results"][0]["retrieval_mode"] == "semantic"
    meta = dict(real_encoder.identity)
    real_encoder.identity["revision"] = "incompatible"
    try:
        with pytest.raises(ValueError, match="mismatch"):
            index.search("好", encoder=real_encoder)
    finally:
        real_encoder.identity = meta
    (target / "records.jsonl").write_text("tampered")
    with pytest.raises(ValueError, match="checksum"):
        Index(target)


def test_cli_errors_and_help():
    for args in [["--help"], ["search", "猜忌", "--index", "/missing"], ["search"]]:
        p = subprocess.run([sys.executable, "-m", "tujia_lex.cli", *args], capture_output=True, text=True)
        assert p.returncode == (0 if args == ["--help"] else 2)
        assert "Traceback" not in p.stderr


@pytest.mark.model
def test_long_construction_tail_is_encoded(real_encoder):
    prefix = "这是有关土家语的语法说明。" * 70
    a, b = real_encoder.encode([prefix + "开花织布。" * 40, prefix + "否定情态动词。" * 40], batch_size=2)
    assert np.linalg.norm(a - b) > 0.01
    assert np.isclose(np.linalg.norm(a), 1, atol=1e-4)


def test_fetch_schema_validation(tmp_path, monkeypatch):
    import gzip
    import io
    import urllib.request
    from tujia_lex.cli import fetch
    valid = gzip.compress(json.dumps({"words": [{"id": "actual-format"}]}).encode())
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: io.BytesIO(valid))
    p = tmp_path / "dictionary.json.gz"
    result = fetch("https://example.test/dictionary.json.gz", p)
    assert result["entries"] == 1 and p.read_bytes() == valid
    assert p.with_suffix(".gz.meta.json").exists()
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: io.BytesIO(gzip.compress(b'{"wrong": []}')))
    with pytest.raises(ValueError, match="not a Bizic dictionary"):
        fetch("https://example.test/bad", p)
    assert p.read_bytes() == valid  # A failed replacement preserves the prior download.
