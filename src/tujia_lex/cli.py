from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

from .data import collect, read_json
from .index import Index, build_index


def fetch(url, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = urllib.request.urlopen(url, timeout=120).read()
    tmp = path.with_name(path.name + ".download.gz")
    tmp.write_bytes(raw)
    try:
        data = read_json(tmp)
        if not isinstance(data, dict) or not isinstance(data.get("words"), list) or not data["words"]:
            raise ValueError("Download is not a Bizic dictionary")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    result = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "entries": len(data["words"])}
    path.with_suffix(path.suffix + ".meta.json").write_text(json.dumps(result, indent=2))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Tujia lexical and construction retrieval. Similarity is a candidate ranking, not a translation.")
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fetch-dictionary")
    f.add_argument("--url", default="https://luggroo.github.io/bizic-dictionary/dictionary.json.gz")
    f.add_argument("--output", default=".cache/dictionary.json.gz")
    b = sub.add_parser("build")
    b.add_argument("--repo", default=".")
    b.add_argument("--dictionary")
    b.add_argument("--output", required=True)
    b.add_argument("--model-path", default="BAAI/bge-base-zh-v1.5")
    b.add_argument("--batch-size", type=int, default=32)
    b.add_argument("--threads", type=int, default=4)
    b.add_argument("--reuse-index", help="Reuse checked same-model embeddings by identical text; metadata is rebuilt")
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--index", required=True)
    s.add_argument("--mode", choices=["exact", "semantic"], default="semantic")
    s.add_argument("--kind", choices=["lexicon", "construction"], default="lexicon")
    s.add_argument("--model-path", default="BAAI/bge-base-zh-v1.5")
    s.add_argument("--dialect", choices=["north", "south", "unknown"])
    s.add_argument("--location")
    s.add_argument("--point")
    s.add_argument("--source")
    s.add_argument("--pos", help="Exact source POS label; no automatic cross-source POS equivalence")
    s.add_argument("--record-type", choices=["lexical_sense", "survey_lexeme", "survey_sentence", "text_block", "grammar_section", "corpus_passage"])
    s.add_argument("--top-k", type=int, default=10)
    s.add_argument("--substring", action="store_true", help="Literal substring baseline, only with --mode exact")
    i = sub.add_parser("inspect")
    i.add_argument("--index", required=True)
    i.add_argument("record_id", nargs="?")
    args = parser.parse_args(argv)
    try:
        if args.command == "fetch-dictionary":
            out = fetch(args.url, args.output)
        elif args.command == "build":
            from .embedding import BGEEncoder
            records = collect(args.repo, args.dictionary)
            encoder = BGEEncoder(args.model_path, threads=args.threads)
            dictionary = Path(args.dictionary or Path(args.repo) / "site/dictionary.json.gz")
            repo = Path(args.repo)
            paths = [dictionary, repo / "site/data.json.gz", repo / "site/longshan-texts.json",
                     repo / "docs/reference-grammar.md", repo / "site/yubao-manifest.json"]
            paths += [repo / "site" / f for f in read_json(repo / "site/yubao-manifest.json")]
            hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True)
            out = build_index(records, encoder, args.output, args.batch_size,
                              {"dictionary_sha256": hashlib.sha256(dictionary.read_bytes()).hexdigest(),
                               "input_files_sha256": hashes, "repository_revision": revision.stdout.strip()}, args.reuse_index)
        else:
            index = Index(args.index)
            if args.command == "inspect":
                out = index.manifest if args.record_id is None else next((r for r in index.records if r["id"] == args.record_id), None)
                if out is None:
                    raise ValueError(f"Unknown record ID: {args.record_id}")
            else:
                if args.substring and args.mode != "exact":
                    raise ValueError("--substring is a lexical baseline, not semantic retrieval")
                encoder = None
                if args.mode == "semantic":
                    from .embedding import BGEEncoder
                    encoder = BGEEncoder(args.model_path)
                out = {"query": args.query, "kind": args.kind, "mode": args.mode,
                       "results": index.search(args.query, mode=args.mode, encoder=encoder, kind=args.kind,
                       dialect=args.dialect, location=args.location, point=args.point, source=args.source,
                       top_k=args.top_k, substring=args.substring, pos=args.pos, record_type=args.record_type)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"tujia-lex: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
