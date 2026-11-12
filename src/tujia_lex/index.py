from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

SCHEMA_VERSION = 1


def normalized(text):
    return unicodedata.normalize("NFKC", text).strip().casefold()


def build_index(records, encoder, output, batch_size=32, metadata=None, reuse_index=None):
    output = Path(output)
    if output.exists():
        raise ValueError(f"Index already exists: {output}; choose a new output directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".index-", dir=output.parent))
    start = time.monotonic()
    try:
        texts = list(dict.fromkeys(r["text"] for r in records))
        cached = None
        cache_rows = {}
        if reuse_index:
            cached = Index(reuse_index)
            for field in ["model", "revision", "weights_sha256", "pooling", "normalize", "query_instruction", "max_length"]:
                if cached.manifest["model"].get(field) != encoder.identity.get(field):
                    raise ValueError(f"Embedding cache model mismatch: {field}")
            cache_rows = {r["text"]: r["vector_row"] for r in cached.records}
        missing = [t for t in texts if t not in cache_rows]
        fresh = encoder.encode(missing, batch_size=batch_size)
        fresh_rows = {t:i for i,t in enumerate(missing)}
        embeddings = np.stack([cached.vectors[cache_rows[t]] if t in cache_rows else fresh[fresh_rows[t]] for t in texts])
        if embeddings.ndim != 2 or len(embeddings) != len(texts) or not np.isfinite(embeddings).all():
            raise ValueError("Invalid model embedding output")
        norms = np.linalg.norm(embeddings, axis=1)
        if not np.allclose(norms, 1, atol=1e-4):
            raise ValueError("Expected normalized model embeddings")
        offsets = {t: i for i, t in enumerate(texts)}
        with (stage / "records.jsonl").open("w") as stream:
            for r in records:
                stream.write(json.dumps({**r, "vector_row": offsets[r["text"]]}, ensure_ascii=False) + "\n")
        np.save(stage / "vectors.npy", embeddings, allow_pickle=False)
        files = {name: hashlib.sha256((stage / name).read_bytes()).hexdigest() for name in ["records.jsonl", "vectors.npy"]}
        manifest = {"schema_version": SCHEMA_VERSION, "record_count": len(records), "unique_texts": len(texts),
                    "dimension": embeddings.shape[1], "record_types": dict(Counter(r["record_type"] for r in records)),
                    "model": encoder.identity, "files_sha256": files, "metadata": metadata or {},
                    "reused_embeddings": len(texts) - len(missing), "encoded_embeddings": len(missing),
                    "build_seconds": round(time.monotonic() - start, 2),
                    "warning": "Cosine similarity ranks candidates; it does not establish synonymy or grammaticality."}
        (stage / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        os.replace(stage, output)
        return manifest
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


class Index:
    def __init__(self, path, verify=True):
        path = Path(path)
        self.manifest = json.loads((path / "manifest.json").read_text())
        if self.manifest["schema_version"] != SCHEMA_VERSION:
            raise ValueError("Unsupported index schema; rebuild the index")
        if verify:
            for name, expected in self.manifest["files_sha256"].items():
                if hashlib.sha256((path / name).read_bytes()).hexdigest() != expected:
                    raise ValueError(f"Index checksum mismatch: {name}")
        self.records = [json.loads(line) for line in (path / "records.jsonl").read_text().splitlines()]
        self.vectors = np.load(path / "vectors.npy", mmap_mode="r", allow_pickle=False)
        if len(self.records) != self.manifest["record_count"] or self.vectors.shape != (self.manifest["unique_texts"], self.manifest["dimension"]):
            raise ValueError("Index size mismatch")

    def search(self, query, mode="semantic", encoder=None, kind="lexicon", top_k=10,
               dialect=None, location=None, point=None, source=None, substring=False, pos=None, record_type=None):
        if not query.strip():
            raise ValueError("Query must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if mode not in {"exact", "semantic"} or kind not in {"lexicon", "construction"}:
            raise ValueError("Invalid retrieval mode or result kind")
        selected = []
        for r in self.records:
            if r["kind"] != kind or (dialect and r["dialect"] != dialect):
                continue
            if pos and r.get("pos") != pos:
                continue
            if record_type and r["record_type"] != record_type:
                continue
            if location and not any(location == loc for loc in r.get("locations", [])):
                continue
            if point and str(point) != r.get("point"):
                continue
            srcs = {r.get("source", "")} | {s["id"] for s in r.get("sources", [])} | {s.get("canonical_id", "") for s in r.get("sources", [])}
            if source and source not in srcs:
                continue
            selected.append(r)
        if mode == "semantic":
            if encoder is None:
                raise ValueError("Semantic retrieval needs a real model encoder")
            for field in ["model", "pooling", "normalize", "query_instruction", "max_length", "revision"]:
                if encoder.identity.get(field) != self.manifest["model"].get(field):
                    raise ValueError(f"Model/index mismatch: {field}; use the indexing model")
            q = encoder.encode([query], query=True)[0]
            rows = np.array([r["vector_row"] for r in selected], dtype=int)
            scores = self.vectors[rows] @ q
            ordered = sorted(zip(selected, scores.tolist()), key=lambda x: (-x[1], x[0]["id"]))
        else:
            q = normalized(query)
            def matches(r):
                for f in r.get("lexical_fields", [r["text"]]):
                    f = normalized(f)
                    if (q in f if substring else q == f):
                        return True
                return False
            ordered = [(r, None) for r in selected if matches(r)]
        # Similar witnesses cannot crowd out all other candidate meanings.
        seen, results = set(), []
        for r, score in ordered:
            key = (r.get("entry_id", r["id"]), r["zh"], r.get("en", ""), r.get("pos", ""), r["dialect"], tuple(r.get("locations", [])), r.get("point", ""))
            if key in seen:
                continue
            seen.add(key)
            results.append({**r, "score": score, "retrieval_mode": mode})
            if len(results) == top_k:
                break
        return results
