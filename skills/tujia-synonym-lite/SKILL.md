---
name: tujia-synonym-lite
description: No-model, low-cost semantic-bridge retrieval for Tujia translation; expands difficult Chinese/English phrases into meaning-aware exact queries against versioned Bizic dictionary shards and documents actual witnesses.
---

# Tujia synonym-lite / 土家语轻量级近义概念检索

Use this subskill **only when actual BGE vector retrieval is unavailable** (or when asked for a literal-vs-heuristic comparison). This is an LLM/skill-guided semantic decomposition + verified dictionary exact lookup; **not embedding, not a neural nearest-neighbor search**. Always disclose `检索模式：Skill-based 近义概念扩展＋静态词典精确检索（未运行 embedding）` in the user's first substantive update and final answer when this mode is used. No fake similarities or Top-K embeddings.

## How it works

1. **Separate the sense from the characters.** Identify referent, predicate, roles, polarity, modality and context before querying. Expand *the intended sense* even if a compound has no literal entry.
2. **Generate a bounded candidate lattice, not an automatic synonym list** (see `concepts.json` for examples): (A) original phrase; (B) true paraphrase/near synonym; (C) hypernym or common specific examples, explicitly labeled; (D) components such as head noun, action, property, participant and result; (E) possible compositional Tujia construction. A specific example of a category is **not** a translation of the category.
3. **Look up each Chinese/English candidate in the actual Bizic static lexicon.** The authoritative export is at `../translate-tujia/lexicon/manifest.json` and its `XX-000.jsonl` shards. Read the manifest once; for each NFKC+casefold+trim query, compute FNV-1a over UTF-8 bytes (32-bit: start 2166136261; xor byte then multiply by 16777619 mod 2^32; take highest byte as two hex digits). Read only `buckets[hex]` named shard(s), compare each row's `k` exactly, and decode `r` using `manifest.record_fields`. **Never claim zero hits when a needed shard could not be read.** In a Python workspace with the files, use `python scripts/lightweight-synonym-search.py "query" --directory skills/translate-tujia/lexicon`; for an unfamiliar phrase, pass model-generated candidates through `--related "候选1,候选2"`.
4. **Select witnesses by meaning and source**, not just the match count. For Northern Longshan start with Brassett (2006), then 2004; broaden to attested Longshan/northern evidence with explicit provenance. Resolve the source alias using `manifest.sources[r[2]].canonical_id`. Never copy spellings across attestations, equate unspecified locality to Longshan, or silently reuse Southern forms.
5. **Compose only with independently licensed grammar.** A candidate verb + noun does not prove the resulting phrase exists. Use `../translate-tujia/references/construction-choices.md`, `aspect-modality.md`, the existing reference grammar and original examples for SOV ordering, relative clause/nominalization, polarity, argument roles and suffix ordering. Label unverified combinations `拟构式`, not `词典已有`.
6. **Show the trace before translating:** query and relation for each expansion; actual matches / no hits; up to 3–5 useful witness IDs, source, original term, original sense; why each helps or is rejected. Then deliver *every* requested translated sentence even if some spans require explicit Chinese lexical insertions and localized uncertainty markers.
7. **Bound cost:** up to eight carefully chosen query strings for an ordinary short phrase (twelve for genuinely complex items), prioritize decompositions over unbounded exploration, reuse queried shards, never enumerate all buckets. If none of the tested candidates are attested, explain the limited evidence and use a clearly marked paraphrase/borrowing; do not invent Tujia words, tones, cosine scores or unattested source claims.

## Five diagnostic cases (verified static witness examples, not whole-phrase translations)

| Input | Candidate path | Attested example | Watch out for |
| --- | --- | --- | --- |
| 路人 | 行人→经过＋人／路 | Brassett 2006: `luo⁴`「人」 and `la⁴`「路」 | 路＋人 is only a proposed composition; passerby relation needs construction |
| 香味 | 香气→气味、闻、香 | Brassett 2006: `lang³`「闻」 | Brassett 2004 `xian1`「香」 is *incense*, not verified pleasant smell |
| 玩具 | 玩的东西→玩＋事物名物化 | Brassett 2006: `ge³ci²`「玩」; `ye³`「东西」 | 玩是活动，不是自动等于玩具 |
| 饮料 | 喝的东西→喝＋名物化 | Brassett 2006 `hu³`「喝」; 参考语法中「喝的东西」有 `ci` 名物化构式 | 水、茶、酒只是饮料下位例 |
| 令人费解 | 难懂→不明白→懂／知道＋否定或难度 | Brassett 2006: `ha¹tai²`「不知道」 | 「不知道」不等于「不理解」；必须检查极性及认知谓语 |

The table documents **components** and pitfalls, not complete accepted translations. These are existing witness spellings in their original source schemes, not automatically tone-marked Bizic romanization. Verify source-linked IPA/notation before using them in rendered translation.

### Audit format

```text
检索模式：Skill-based（概念扩展＋词典精确查询；无 embedding/cosine）
原句／原词：...
扩展：q1 [exact]; q2 [paraphrase]; q3 [component_action]; q4 [component_head]
实测：q1 0条；q2 2条（entry/attestation/source/form）；... 
构式：...（已见证／可推拟／需核）
译文：...（完整，保留未证实段的局部标记）
```

This subskill is a fallback **retrieval workflow**; `tujia-lex` BGE remains the preferred retrieval implementation whenever its model and compatible full index can genuinely run.
