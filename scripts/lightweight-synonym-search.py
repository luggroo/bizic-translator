#!/usr/bin/env python3
"""Bounded skill-driven concept expansion + real static-dictionary exact lookup.

This tool does NOT use embeddings. It reports source-linked witnesses for candidate
queries; composing a phrase and judging synonyms remain translation decisions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEXICON = ROOT / "skills/translate-tujia/lexicon"
DEFAULT_CONCEPTS = ROOT / "skills/tujia-synonym-lite/concepts.json"

# Reuse the existing FNV sharding, hash verification, and exact-match lookup.
_spec = importlib.util.spec_from_file_location(
    "bizic_export_readable_lexicon", ROOT / "scripts/export-readable-lexicon.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Missing static lexicon reader")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
lookup = _module.lookup
normalize = _module.normalize


def candidate_queries(query: str, concept_map: dict, related: str = "", max_queries: int = 10):
    if not 1 <= max_queries <= 12:
        raise ValueError("max_queries must be 1..12")
    key = normalize(query)
    if not key:
        raise ValueError("query cannot be empty")
    concept = concept_map.get("concepts", {}).get(query) or concept_map.get("concepts", {}).get(key, {})
    items = [{"q": query, "relation": "exact"}] + concept.get("candidates", [])
    if related:
        items += [{"q": x.strip(), "relation": "user_or_skill_generated"} for x in related.split(",")]
    selected, seen = [], set()
    for item in items:
        q = item["q"].strip()
        norm = normalize(q)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        selected.append({"query": q, "relation": item.get("relation", "related")})
        if len(selected) >= max_queries:
            break
    return concept, selected


def source_priority(canonical: str) -> int:
    if canonical == "brassett-2006":
        return 0
    if canonical == "brassett-2004":
        return 1
    return 2


def is_in_dialect(value: str, wanted: str | None) -> bool:
    if wanted in (None, "any"):
        return True
    if wanted == "north":
        return "北" in value and "南" not in value
    if wanted == "south":
        return "南" in value and "北" not in value
    raise ValueError("unknown dialect")


def run(query: str, directory: Path, concept_path: Path, related: str = "",
        dialect: str = "north", max_queries: int = 10, limit_per_query: int = 4):
    if not 1 <= limit_per_query <= 10:
        raise ValueError("limit_per_query must be 1..10")
    concepts = json.loads(concept_path.read_text(encoding="utf-8"))
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    fields = manifest["record_fields"]
    required = ("entry_id", "attestation_id", "source", "term", "zh", "en", "pos", "dialect",
                "locator", "source_ref")
    field_idx = {field: fields.index(field) for field in required}
    concept, queries = candidate_queries(query, concepts, related, max_queries)
    results = []
    for candidate in queries:
        # Exact matching; lookup validates the SHA-256 and file sizes before returning rows.
        raw_rows = lookup(directory, candidate["query"], limit=100)
        matches = []
        for raw in raw_rows:
            row = {name: raw[i] for name, i in field_idx.items()}
            if not is_in_dialect(str(row["dialect"]), dialect):
                continue
            meta = manifest.get("sources", {}).get(row["source"], {})
            row["canonical_source"] = meta.get("canonical_id", row["source"])
            row["source_title"] = meta.get("title", "")
            row["source_locations"] = meta.get("locations", [])
            matches.append(row)
        matches.sort(key=lambda r: (source_priority(r["canonical_source"]),
                                    str(r["entry_id"]), str(r["attestation_id"])))
        results.append({
            **candidate,
            "raw_exact_hits": len(raw_rows),
            "dialect_filtered_hits": len(matches),
            "witnesses": matches[:limit_per_query],
        })
    return {
        "mode": "skill_based",
        "retrieval": "semantic-bridge candidate expansion + verified static dictionary exact match",
        "embedding_run": False,
        "cosine_similarity": None,
        "query": query,
        "concept_meaning": concept.get("meaning", ""),
        "concept_warning": concept.get("caution", ""),
        "dictionary_revision": manifest.get("revision", ""),
        "dialect_filter": dialect,
        "candidate_results": results,
        "warning": "Expanded queries are not guaranteed synonyms; candidate combination requires grammatical validation.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query")
    p.add_argument("--directory", type=Path, default=DEFAULT_LEXICON)
    p.add_argument("--concepts", type=Path, default=DEFAULT_CONCEPTS)
    p.add_argument("--related", default="", help="Comma-separated extra concept or paraphrase queries")
    p.add_argument("--dialect", choices=["north", "south", "any"], default="north")
    p.add_argument("--max-queries", type=int, default=10)
    p.add_argument("--limit-per-query", type=int, default=4)
    args = p.parse_args()
    result = run(args.query, args.directory, args.concepts, args.related,
                 args.dialect, args.max_queries, args.limit_per_query)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
