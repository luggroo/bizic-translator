#!/usr/bin/env python3
"""Export public Bizic dictionary attestations into small, directly readable text shards.

No API server, decompression at query time, database scan, or embedding model.
One fixed-size static bucket is selected for each normalized query; each row
retains attestation provenance. The original gzip remains the canonical source.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path

MAX_COMPRESSED = 12_000_000
MAX_DECOMPRESSED = 200_000_000
MAX_SHARD_BYTES = 110_000
MAX_QUERY_CHARS = 120


def normalize(value):
    return unicodedata.normalize("NFKC", str(value or "")).strip().casefold()


def bucket_of(query):
    """Portable FNV-1a, highest byte. No secret hashes or server side computation."""
    h = 2166136261
    for b in normalize(query).encode("utf-8"):
        h = ((h ^ b) * 16777619) & 0xffffffff
    return f"{h >> 24:02x}"


def search_keys(att, spellings):
    result = set()
    for value in [att.get("zh", ""), att.get("en", ""), att.get("term", ""), *spellings]:
        value = normalize(value)
        if not value:
            continue
        result.add(value)
        # Split enumerations of dictionary meanings, not ordinary spaces.
        for part in re.split(r"[;；、/／，,\n]+", value):
            if part.strip():
                result.add(part.strip())
    return {s for s in result if 0 < len(s) <= MAX_QUERY_CHARS}


def read_dictionary(path):
    path = Path(path)
    if path.stat().st_size > MAX_COMPRESSED:
        raise ValueError("Compressed dictionary exceeds safety size limit")
    with gzip.open(path, "rb") as handle:
        raw = handle.read(MAX_DECOMPRESSED + 1)
    if len(raw) > MAX_DECOMPRESSED:
        raise ValueError("Decompressed dictionary exceeds safety size limit")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("words"), list):
        raise ValueError("Expected Bizic dictionary with words")
    return data


def build(source, output, revision="", max_bytes=MAX_SHARD_BYTES):
    source, output = Path(source), Path(output)
    if not 4_096 <= max_bytes <= MAX_SHARD_BYTES:
        raise ValueError("max_bytes outside safe bounds")
    data = read_dictionary(source)
    buckets = defaultdict(list)
    attestation_ids = set()
    entry_ids = set()
    for entry in data["words"]:
        entry_id = entry["id"]
        if entry_id in entry_ids:
            raise ValueError(f"Duplicate entry: {entry_id}")
        entry_ids.add(entry_id)
        notations = entry.get("notations", {})
        for att in entry["attestations"]:
            aid = att["id"]
            if aid in attestation_ids:
                raise ValueError(f"Duplicate attestation: {aid}")
            attestation_ids.add(aid)
            # Never attach another witness's notation to the present attestation.
            matched = {scheme: [n.get("text", "") for n in values if aid in n.get("attestationIds", [])]
                       for scheme, values in notations.items()}
            matched = {k: v for k, v in matched.items() if v}
            # Compact source-backed preview: original full fields remain in the
            # canonical gzip and complete semantic-index inspection records.
            # Fixed positional arrays avoid repeating large field names
            # 81k+ times in the GitHub-text-readable fallback.
            record = [entry_id, aid, att.get("source", ""), att.get("term", ""),
                      att.get("zh", ""), att.get("en", ""), att.get("pos", ""),
                      att.get("dialect", ""), att.get("locator", ""),
                      att.get("sourceRef", ""), matched]
            all_spellings = [s for values in matched.values() for s in values]
            for key in search_keys(att, all_spellings):
                buckets[bucket_of(key)].append({"k": key, "r": record})
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".static-lexicon-", dir=output.parent))
    manifest = {"format": 1, "source": "luggroo/bizic-dictionary/site/dictionary.json.gz",
                "revision": revision, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "dictionary_entries": len(entry_ids), "dictionary_attestations": len(attestation_ids),
                "index_keys": sum(len(v) for v in buckets.values()),
                "algorithm": "FNV-1a(normalized UTF-8), top byte; NFKC + casefold + strip",
                "shard_limit_bytes": max_bytes,
                "record_fields": ["entry_id", "attestation_id", "source", "term", "zh", "en",
                                  "pos", "dialect", "locator", "source_ref", "notations"],
                "buckets": {}}
    try:
        for bucket, rows in sorted(buckets.items()):
            rows.sort(key=lambda x: (x["k"], x["r"][0], x["r"][1]))
            index, buf, size = 0, [], 0
            files = []
            def write_shard(index, buf):
                name = f"{bucket}-{index:03d}.jsonl"
                payload = "".join(buf).encode("utf-8")
                (stage / name).write_bytes(payload)
                files.append({"path": name, "bytes": len(payload),
                              "sha256": hashlib.sha256(payload).hexdigest(),
                              "rows": len(buf)})
            for row in rows:
                line = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                encoded = line.encode("utf-8")
                if len(encoded) > max_bytes:
                    raise ValueError("One attestation exceeds a shard's maximum size")
                if size + len(encoded) > max_bytes and buf:
                    write_shard(index, buf)
                    index += 1
                    buf, size = [], 0
                buf.append(line)
                size += len(encoded)
            if buf:
                write_shard(index, buf)
            manifest["buckets"][bucket] = files
        (stage / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        if output.exists():
            shutil.rmtree(output)
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return manifest


def lookup(directory, query, limit=20):
    """Read only the matching static bucket (no full dictionary decompression)."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    key = normalize(query)
    if not key or len(key) > MAX_QUERY_CHARS:
        raise ValueError("query must be 1..120 characters")
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    files = manifest["buckets"].get(bucket_of(key), [])
    result = []
    for info in files:
        name = info["path"]
        if "/" in name or "\\" in name or ".." in name:
            raise ValueError("Unsafe path in manifest")
        data = (directory / name).read_bytes()
        if len(data) != info["bytes"] or hashlib.sha256(data).hexdigest() != info["sha256"]:
            raise ValueError(f"Shard checksum mismatch: {name}")
        for line in data.decode("utf-8").splitlines():
            row = json.loads(line)
            if row["k"] == key:
                result.append(row["r"])
                if len(result) == limit:
                    return result
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", required=True)
    b.add_argument("--output", required=True)
    b.add_argument("--revision", default="")
    b.add_argument("--max-bytes", type=int, default=MAX_SHARD_BYTES)
    q = sub.add_parser("lookup")
    q.add_argument("--directory", required=True)
    q.add_argument("--query", required=True)
    q.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if args.command == "build":
        manifest = build(args.source, args.output, args.revision, args.max_bytes)
        print(json.dumps({k: manifest[k] for k in ("dictionary_entries", "dictionary_attestations", "index_keys")}))
    else:
        print(json.dumps(lookup(args.directory, args.query, args.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
