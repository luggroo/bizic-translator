---
name: tujia-synonym-lite
description: No-model, low-cost semantic-bridge retrieval for Tujia translation; expands difficult Chinese/English phrases into meaning-aware exact queries against versioned Bizic dictionary shards and documents actual witnesses.
---

# Tujia synonym-lite / 土家语轻量级近义概念检索

This subskill runs **Skill-based concept expansion + real dictionary exact lookup** when the BGE model cannot execute; disclose the retrieval mode once in the first update and once at the end. Its semantic decomposition technique is **shared with the Embedding route** via `../translate-tujia/references/semantic-decomposition.md`. Produce a confident complete translation; one overall quality note is enough. Only actual embedding runs may report vector scores.

## How it works

1. **Separate the sense from the characters.** Identify referent, predicate, roles, polarity, modality and context before querying. Expand *the intended sense* even if a compound has no literal entry.
2. **Generate a bounded candidate lattice, not an automatic synonym list** (see `concepts.json` for examples): (A) original phrase; (B) true paraphrase/near synonym; (C) hypernym or common specific examples, explicitly labeled; (D) components such as head noun, action, property, participant and result; (E) possible compositional Tujia construction. A specific example of a category is **not** a translation of the category.
3. **Look up each Chinese/English candidate in the actual Bizic static lexicon.** The authoritative export is at `../translate-tujia/lexicon/manifest.json` and its `XX-000.jsonl` shards. Read the manifest once; for each NFKC+casefold+trim query, compute FNV-1a over UTF-8 bytes (32-bit: start 2166136261; xor byte then multiply by 16777619 mod 2^32; take highest byte as two hex digits). Read only `buckets[hex]` named shard(s), compare each row's `k` exactly, and decode `r` using `manifest.record_fields`. **Never claim zero hits when a needed shard could not be read.** In a Python workspace with the files, use `python scripts/lightweight-synonym-search.py "query" --directory skills/translate-tujia/lexicon`; for an unfamiliar phrase, pass model-generated candidates through `--related "候选1,候选2"`.
4. **Select witnesses by meaning and source**, not just the match count. For Northern Longshan start with Brassett (2006), then 2004; broaden to attested Longshan/northern evidence with explicit provenance. Resolve the source alias using `manifest.sources[r[2]].canonical_id`. Never copy spellings across attestations, equate unspecified locality to Longshan, or silently reuse Southern forms.
5. **Compose with target-language grammar.** Read `../translate-tujia/references/semantic-decomposition.md` plus the relevant topic in `../translate-tujia/references/clause-patterns.md` or `aspect-modality.md`; determine the intended nominalized participant/object and confidently reuse productive syntax. Keep exact-attestation distinctions in the audit, not repeated beside the fluent translation.
6. **Deliver the translation first.** Maintain a compact internal query trace (expansions, hits, IDs, sources and senses). Show the detailed trace only when the user explicitly requests retrieval validation; in ordinary use, disclose the retrieval mode and give one overall quality note, not a disclaimer per constituent.
7. **Bound cost:** normally 8–12 targeted queries, deduplicated buckets and cached results. If no native equivalent emerges, paraphrase productively or use the smallest meaningful Chinese insertion. Never invent source citations, tones or embedding scores.

## Semantic decomposition → constructional recomposition

The shared algorithm is described once in [semantic-decomposition.md](../translate-tujia/references/semantic-decomposition.md); it applies to Embedding and Skill-based retrieval alike. Convert Chinese lexical concepts into ordinary events, participants and grammatical constructions **before** giving up on native vocabulary.

| Chinese expression | Semantic rewrite | Proposed composition | Transformation |
| --- | --- | --- | --- |
| 路人 | 走路的人 | `la hxi ma` | Event → participant nominalization |
| 香味 | 气味 | generic smell/odor | Controlled semantic generalization |
| 玩具 | 玩的东西 | `geci-xi` | Event → associated object |
| 饮料 | 喝的东西 | `hu-ci` | Event → object |
| 令人费解 | 不能懂得 | understand + inability | Predicate + negative ability |
| 经济损失 | 钱财的损失／损失的钱 | money + loss event | Abstract → concrete stake + event |
| 画地为牢 | 把自己关住 | self + shut + state | Idiom → ordinary event |

These are the user's **suggested productive patterns** and seed decompositions. Apply the appropriate target-dialect suffix and argument structure from grammar evidence, then write a complete proposed translation. Only a **single final quality notice** is shown to the user; record candidate source and sense distinctions in debug logs.

For a short input, query the original term, a plain paraphrase, the core predicate and a semantic head/participant. Prefer Brassett (2006) for Northern/Longshan, then 2004. Do not conflate broad superordinates (气味), category instances (水) and exact synonyms when selecting the final wording.

### Audit format

```text
检索模式：Skill-based（概念扩展＋词典精确查询；无 embedding/cosine）
原句／原词：...
扩展：q1 [exact]; q2 [paraphrase]; q3 [component_action]; q4 [component_head]
实测：q1 0条；q2 2条（entry/attestation/source/form）；... 
构式：...（已见证／可推拟／需核）
译文：...（完整自然的拟译；最后统一一条质量说明）
```

This subskill is a fallback **retrieval workflow**; `tujia-lex` BGE remains the preferred retrieval implementation whenever its model and compatible full index can genuinely run.
