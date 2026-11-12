"""Adapters for the public dictionary and separately attested constructions.

No location or spelling is propagated between witnesses of a merged entry.
"""
from __future__ import annotations

import gzip
import ast
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


def read_json(path):
    path = Path(path)
    raw = path.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def dialect(value):
    value = str(value or "")
    # Mixed/unspecified labels do not license either filter.
    if "北" in value and "南" not in value:
        return "north"
    if "南" in value and "北" not in value:
        return "south"
    return "unknown"


def locations(item):
    value = item.get("locations") or item.get("location") or []
    if isinstance(value, str) and value.startswith("["):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list) and all(isinstance(v, str) for v in parsed):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return [value] if isinstance(value, str) else list(value)


def source_catalog(repo):
    data = read_json(Path(repo) / "site/data.json.gz")
    catalog = {s["id"]: {k: v for k, v in s.items() if k != "text"}
               for s in data.get("sources", []) + data.get("sourceVariants", [])}
    return catalog, data.get("sourceAliases", {})


def lexical_records(dictionary, catalog=None, aliases=None):
    data = read_json(dictionary)
    if not isinstance(data, dict) or not isinstance(data.get("words"), list):
        raise ValueError("Expected dictionary object with a words array")
    catalog, aliases = catalog or {}, aliases or {}
    records = []
    seen_entries = set()
    for entry in data["words"]:
        eid = entry["id"]
        if eid in seen_entries:
            raise ValueError(f"Duplicate entry ID: {eid}")
        seen_entries.add(eid)
        attestations = entry.get("attestations")
        if not isinstance(attestations, list) or not attestations:
            raise ValueError(f"Entry {eid} has no attestation array")
        groups = defaultdict(list)
        for att in attestations:
            if not all(att.get(k) for k in ("id", "source", "term")):
                raise ValueError(f"Malformed attestation in {eid}")
            if not str(att.get("zh", "")).strip():
                raise ValueError(f"Missing Chinese sense in attestation {att['id']}; do not inherit a merged gloss")
            src = catalog.get(att["source"], {})
            loc = locations(att) or locations(src)
            d = dialect(att.get("dialect") or src.get("dialect"))
            # Preserve the verbatim bilingual sense and POS, not parent zhVariants.
            key = (att["zh"], att.get("en", ""), att.get("pos", ""), d, tuple(loc), str(att.get("point", "")))
            groups[key].append(att)
        for key, witnesses in groups.items():
            zh, en, pos, d, loc, point = key
            ids = {a["id"] for a in witnesses}
            notation = {scheme: [n for n in ns if ids.intersection(n.get("attestationIds", []))]
                        for scheme, ns in entry.get("notations", {}).items()}
            sources = []
            for a in witnesses:
                meta = catalog.get(a["source"], {})
                sources.append({"id": a["source"], "canonical_id": aliases.get(a["source"], a["source"]),
                                "title": meta.get("title", a.get("citation", a["source"])),
                                "url": meta.get("url", ""), "locator": a.get("locator", ""),
                                "attestation_id": a["id"], "source_ref": a.get("sourceRef", "")})
            records.append({"id": f"lex:{eid}:{digest(key)}", "kind": "lexicon", "record_type": "lexical_sense",
                            "entry_id": eid, "text": zh, "zh": zh, "en": en, "pos": pos,
                            "dialect": d, "dialect_original": witnesses[0].get("dialect", ""),
                            "locations": list(loc), "point": point,
                            "forms": list(dict.fromkeys(a["term"] for a in witnesses)),
                            "notations": notation, "attestations": witnesses, "sources": sources,
                            "citation": f"Dictionary entry {eid}; " + "; ".join(a["id"] for a in witnesses),
                            "lexical_fields": [zh, en] + [a["term"] for a in witnesses]})
    return records


def survey_records(repo):
    lexical, sentences = [], []
    for name in read_json(Path(repo) / "site/yubao-manifest.json"):
        path = Path(repo) / "site" / name
        d = read_json(path)
        point = str(d["point"])
        base = {"dialect": dialect(d["dialect"]), "dialect_original": d["dialect"],
                "locations": locations(d), "point": point, "source": f"yubao-{point}"}
        for row in d.get("words", []):
            serial, zh, ipa, *rest = row
            rid = f"survey-word:{point}:{serial}"
            lexical.append({**base, "id": rid, "kind": "lexicon", "record_type": "survey_lexeme",
                            "entry_id": rid, "text": zh, "zh": zh, "en": "", "pos": "",
                            "forms": [ipa], "ipa": ipa, "notations": {}, "attestations": [],
                            "annotation": rest[0] if rest else "", "raw_row": row,
                            "citation": f"{name}, words, {serial}", "sources": [{"id": base["source"],
                            "canonical_id": base["source"], "locator": f"{name}:words:{serial}"}],
                            "lexical_fields": [zh, ipa]})
        for row in d.get("sentences", []):
            serial, zh, ipa, *rest = row
            sentences.append({**base, "id": f"sentence:{point}:{serial}", "kind": "construction",
                              "record_type": "survey_sentence", "text": zh, "zh": zh, "ipa": ipa,
                              "gloss": rest[0] if rest else "", "raw_row": row,
                              "citation": f"{name}, sentences, {serial}", "path": f"site/{name}",
                              "lexical_fields": [zh, ipa, rest[0] if rest else ""]})
    return lexical, sentences


def longshan_records(repo):
    records = []
    for story in read_json(Path(repo) / "site/longshan-texts.json"):
        for i, block in enumerate(story.get("blocks", [])):
            # Cultural/editorial notes are context, never aligned translations.
            if not block.get("zh") or not (block.get("ipa") or block.get("ye")):
                continue
            records.append({"id": f"text:{story['id']}:{i}", "kind": "construction",
                            "record_type": "text_block", "text": block["zh"], "zh": block["zh"],
                            "ipa": block.get("ipa", ""), "ye": block.get("ye", ""),
                            "en": block.get("en", ""), "glosses": block.get("glosses", []),
                            "dialect": dialect(story.get("dialect")), "locations": locations(story),
                            "point": "", "source": story.get("source", ""), "title": story.get("title", ""),
                            "citation": f"{story['id']}, block {i}", "url": story.get("externalUrl", ""),
                            "context_note": story.get("culturalNote", ""),
                            "lexical_fields": [block["zh"], block.get("ye", ""), block.get("ipa", "")]})
    return records


def grammar_records(repo):
    """Section-sized rules with verbatim examples/citations; explicitly secondary evidence.

    Sections are bounded at headings; large sections get overlapping paragraphs,
    never silently truncated by the embedding tokenizer.
    """
    lines = (Path(repo) / "docs/reference-grammar.md").read_text().splitlines()
    sections, current, north = [], None, True
    for i, line in enumerate(lines, 1):
        if line.startswith("# 附录") or line.startswith("# 审阅说明"):
            break  # Editorial/publishing instructions are not grammatical evidence.
        if line.startswith("# 南部土家语"):
            north = False
        if re.match(r"#{2,4} ", line):
            if current:
                sections.append(current)
            current = {"title": line.lstrip("# "), "start": i, "lines": [], "dialect": "north" if north else "south"}
        if current:
            current["lines"].append(line)
    if current:
        sections.append(current)
    result = []
    for sec in sections:
        paras = "\n".join(sec["lines"]).split("\n\n")
        chunks, text = [], ""
        for p in paras:
            if len(text) + len(p) > 1100 and text:
                chunks.append(text)
                text = ""
            text += p + "\n\n"
        if text.strip():
            chunks.append(text)
        for j, chunk in enumerate(chunks):
            # Preserve full source text and links even when no aligned example exists.
            zh = " ".join(re.findall(r"[\u3400-\u9fff][\u3400-\u9fff，。；、：“”！？（）……\s\d\-]*", chunk))
            if not zh.strip():
                continue
            result.append({"id": f"grammar:{sec['start']}:{j}", "kind": "construction",
                           "record_type": "grammar_section", "text": sec["title"] + "。" + zh,
                           "zh": zh, "original": chunk, "title": sec["title"], "dialect": sec["dialect"],
                           "locations": [], "point": "", "source": "reference-grammar",
                           "citation": f"docs/reference-grammar.md:{sec['start']}; chunk {j}",
                           "source_links": re.findall(r"\]\(([^)]+)\)", chunk),
                           "evidence_level": "secondary grammar discussion; inspect original citations",
                           "lexical_fields": [sec["title"], chunk]})
    return result


def corpus_records(repo):
    data = read_json(Path(repo) / "site/data.json.gz")
    catalog, _ = source_catalog(repo)
    result = []
    for c in data.get("corpus", []):
        src = catalog.get(c.get("source"), {})
        scope = dialect(c.get("dialect") or src.get("dialect"))
        basis = "explicit corpus/source dialect metadata"
        # This public corpus has speaker introductions in Longshan/Yongshun;
        # its metadata omits a dialect field. This does NOT infer a survey point.
        if scope == "unknown" and c.get("source") == "15hgNztDGzK22XFSM26p2uJkftxyyG80I":
            scope = "north"
            basis = ("public Tujia Language Corpus: introductions identify Longshan (靛房、他砂、坡脚) "
                     "and Yongshun 大坝 speakers; paragraph speaker/locality requires source inspection")
        for i, original in enumerate(re.split(r"\n\s*\n", c.get("text", ""))):
            if not re.search(r"[a-z][a-z-]*[1-4]", original):
                continue
            zh = "\n".join(line for line in original.splitlines() if re.search(r"[\u3400-\u9fff]", line))
            if not zh:
                continue
            result.append({"id": f"corpus:{c['id']}:{i}", "kind": "construction", "record_type": "corpus_passage",
                           "text": zh, "zh": zh, "original": original, "dialect": scope, "scope_basis": basis,
                           "locations": locations(c), "point": "", "source": c.get("source", ""), "title": c.get("title", ""),
                           "citation": f"{c['id']}, extracted paragraph {i}; section starts at PDF page {c.get('page', '?')}",
                           "url": src.get("url", ""), "alignment_status": "extracted bilingual paragraph; verify line alignment against source",
                           "lexical_fields": [zh, original]})
    return result


def collect(repo, dictionary=None, include_surveys=True):
    repo = Path(repo)
    catalog, aliases = source_catalog(repo)
    lex = lexical_records(dictionary or repo / "site/dictionary.json.gz", catalog, aliases)
    survey_lex, sentences = survey_records(repo)
    records = lex + (survey_lex if include_surveys else []) + sentences + longshan_records(repo) + grammar_records(repo) + corpus_records(repo)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate retrieval record IDs")
    return records
