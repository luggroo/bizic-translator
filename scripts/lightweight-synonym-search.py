#!/usr/bin/env python3
"""Bounded skill-driven concept expansion + real static-dictionary exact lookup.

This tool does NOT use embeddings. It reports source-linked witnesses for candidate
queries; composing a phrase and judging synonyms remain translation decisions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tujia_lex.query_plan import plan, normalize
from tujia_lex.static import StaticLexicon, bucket_of

DEFAULT_LEXICON = ROOT / "skills/translate-tujia/lexicon"
DEFAULT_CONCEPTS = ROOT / "skills/tujia-synonym-lite/concepts.json"


def candidate_queries(query: str, concept_map: dict, related: str = "", max_queries: int = 10):
    if not 1 <= max_queries <= 12:
        raise ValueError("max_queries must be 1..12")
    concept = concept_map.get("concepts", {}).get(query, {})
    shared = plan(query, related=[x.strip() for x in related.split(",") if x.strip()],
                  max_queries=max_queries)
    return concept, [{"query": q.query, "relation": q.relation} for q in shared.queries]


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
        dialect: str = "north", max_queries: int = 10, limit_per_query: int = 4, *,
        lexicon: StaticLexicon | None = None):
    if not 1 <= limit_per_query <= 10:
        raise ValueError("limit_per_query must be 1..10")
    concepts = json.loads(concept_path.read_text(encoding="utf-8"))
    if not 1 <= max_queries <= 12:
        raise ValueError("max_queries must be 1..12")
    lexicon = lexicon if lexicon is not None else StaticLexicon(directory)
    manifest = lexicon.manifest
    fields = manifest["record_fields"]
    concept = concepts.get("concepts", {}).get(query, {})
    shared = plan(query, dialect=dialect, related=[x.strip() for x in related.split(",") if x.strip()],
                  max_queries=max_queries)
    queries = [{"query": q.query, "relation": q.relation} for q in shared.queries]
    results = []
    for candidate in queries:
        # Exact matching; lookup validates the SHA-256 and file sizes before returning rows.
        cached_rows = lexicon._bucket(bucket_of(candidate["query"]))
        raw_rows = cached_rows.get(normalize(candidate["query"]), [])[:100]
        matches = []
        for raw in raw_rows:
            row = dict(zip(fields, raw))
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
        "query_plan": shared.to_dict(),
        "concept_meaning": concept.get("meaning", ""),
        "concept_warning": concept.get("caution", ""),
        "dictionary_revision": manifest.get("revision", ""),
        "dialect_filter": dialect,
        "candidate_results": results,
        "warning": "Expanded queries are not guaranteed synonyms; candidate combination requires grammatical validation.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", nargs="+", help="One concept or a batch sharing verified shard reads")
    p.add_argument("--directory", type=Path, default=DEFAULT_LEXICON)
    p.add_argument("--concepts", type=Path, default=DEFAULT_CONCEPTS)
    p.add_argument("--related", default="", help="Comma-separated extra concept or paraphrase queries")
    p.add_argument("--dialect", choices=["north", "south", "any"], default="north")
    p.add_argument("--max-queries", type=int, default=10)
    p.add_argument("--limit-per-query", type=int, default=4)
    args = p.parse_args()
    lexicon = StaticLexicon(args.directory)
    results = [run(query, args.directory, args.concepts, args.related,
                   args.dialect, args.max_queries, args.limit_per_query, lexicon=lexicon)
               for query in args.query]
    result = results[0] if len(results) == 1 else {"mode": "skill_based", "results": results}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
