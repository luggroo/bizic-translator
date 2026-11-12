#!/usr/bin/env python3
"""Run the predeclared real-data case study, retaining candidate provenance."""
import argparse
import json
import platform
import subprocess
import time
from pathlib import Path

from tujia_lex.embedding import BGEEncoder
from tujia_lex.index import Index

QUERIES = ["猜忌", "诬陷", "心灵手巧", "纺织", "挑织", "守候", "悲痛", "追悔莫及", "嫁妆", "纪念", "化作", "鲜红", "杜鹃鸟", "白果树"]
CONSTRUCTIONS = ["用刀切肉，工具在动作前面", "对他说话，听话人和间接宾语", "学习做鞋子，动作作为宾语",
                "名词直接作谓语", "谁的书，领属关系", "先洗好再切菜，动作先后", "坐着吃饭，持续和伴随",
                "树木的量词", "否定和意愿的区别", "他比我高，比较句"]


def concise(r):
    keys = ["id", "record_type", "entry_id", "zh", "en", "pos", "forms", "score", "dialect", "locations", "point",
            "citation", "sources", "source", "ipa", "ye", "gloss", "title", "source_links", "original"]
    result = {k: r[k] for k in keys if k in r}
    if "sources" in result:
        result["sources"] = [{k:s[k] for k in ['id','canonical_id','attestation_id','locator'] if k in s} for s in result["sources"]]
    if "attestations" in r:
        result["attestation_ids"] = [a["id"] for a in r["attestations"]]
    return result


p = argparse.ArgumentParser()
p.add_argument("--index", required=True)
p.add_argument("--model-path", required=True)
p.add_argument("--output", default="docs/evaluation/retrieval-results.json")
a = p.parse_args()
start = time.monotonic()
index = Index(a.index)
encoder = BGEEncoder(a.model_path)
rows = []
for query in QUERIES:
    row = {"query": query}
    for mode, opts in [("exact", {}), ("substring", {"substring": True}), ("semantic", {})]:
        row[mode] = [concise(r) for r in index.search(query, mode="semantic" if mode == "semantic" else "exact",
                          encoder=encoder, top_k=10, **opts)]
    row["brassett_semantic"] = [concise(r) for r in index.search(query, encoder=encoder, source="brassett-2004", dialect="north", top_k=5)]
    row["brassett_2006_semantic"] = [concise(r) for r in index.search(query, encoder=encoder, source="brassett-2006", dialect="north", top_k=5)]
    rows.append(row)
construction = []
for query in CONSTRUCTIONS:
    construction.append({"query": query,
        "grammar": [concise(r) for r in index.search(query, encoder=encoder, kind="construction", dialect="north", record_type="grammar_section", top_k=3)],
        "60757": [concise(r) for r in index.search(query, encoder=encoder, kind="construction", point="60757", top_k=3)]})
result = {"model": index.manifest["model"], "index": index.manifest, "python": platform.python_version(),
          "queries": rows, "constructions": construction,
          "negative_controls": {q:[concise(r) for r in index.search(q,encoder=encoder,source='brassett-2004',top_k=5)]
                                for q in ['不聪明','不愿意','不能离开']},
          "seconds": round(time.monotonic() - start, 2)}
Path(a.output).parent.mkdir(parents=True, exist_ok=True)
Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({"output": a.output, "queries": len(rows), "construction_queries": len(construction), "seconds": result["seconds"]}))
