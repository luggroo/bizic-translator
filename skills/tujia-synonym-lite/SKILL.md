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

## Semantic decomposition → constructional recomposition (preferred over mechanical synonym replacement)

The goal is to recover **a semantically faithful, compositionally licensed Tujia expression**, not a Chinese synonym with the same word class. After a no-hit exact lookup, identify the underlying predicate, its arguments, and its possible nominalized roles; then search the **real** lexicon for each building block and grammar for the derivation. These are productive hypotheses, not automatic attested phrases. User-supplied proposals below are *candidate analyses for testing*, **not independently verified full-form attestations**.

| Chinese input | First semantic rewrite | Candidate Tujia construction | Operation | Must verify |
| --- | --- | --- | --- | --- |
| 路人 | 在路上走的人 / 走路的人 | `la hxi ma` = road + go/walk + human nominalizer | event → participant; locative / activity relative to agent | `la` is 'road', `hxi` is 'walk/go' in the selected variety; `-ma` nominalizes this intransitive predicate and means an incidental passerby rather than any walker |
| 香味 | 气味 | use verified generic 'smell/odor' sense before finding 'pleasant' modifier | semantic generalization to a superordinate | Generic odor includes bad smell; original favorable valence may need restoring; do not use incense or the verb 'smell' as if they were the noun fragrance |
| 玩具 | 用来玩的东西 / 玩的东西 | `geci-xi` = 'play' + nominalizer | event → associated object, with contextual object reading | `-xi` here can denote the plaything and not the act of playing or a person; verify actual word boundary and tone; **do not silently replace -xi with -ci** |
| 饮料 | 喝的东西 | `hu-ci` = 'drink' + object nominalizer | event → object/theme | `-ci` in this lexical/dialect context denotes something to drink; not water/tea/wine alone; identify actual phonology of the verb |
| 令人费解 | 不能懂得 / 不能理解 | cognitive predicate 'understand' + inability/negative potential | complex property → negative ability predicate | Keep ability vs factual 'not know', and distinguish experiencer from thing misunderstood; negation/ability order must be attested |

**These are four reusable transformations**, not five independent synonym recipes:

1. **Event/participant reconstruction:** turn a lexicalized entity label into a relative or agent-nominalized event (路人 → road + walk + person). A participant can be introduced by the predicate without a special stand-alone noun.
2. **Event-to-thing nominalization:** reduce artifacts and substances to their function (玩具 → something to play with; 饮料 → something to drink). Check the **specific** available nominalizer and reading in context: person `-ma`, generic `-xi`, object `-ci` are not freely interchangeable.
3. **Controlled semantic generalization:** look up a broader category when a marked concept has no exact sense (香味 → 气味), **record the lost feature** (pleasantness) and restore it with an attested modifier when needed.
4. **Predicate + modality/negation composition:** express a complex evaluative adjective via a simple predicate plus inability/negative potential (令人费解 → understand + cannot); check polarity, scope, argument structure, and actual modal morphology before composing.

**Query protocol:** for each source word, include the original phrase, semantic rewrite(s), the predicate, the head / participant, and the relevant nominalizer or ability pattern. Record each expansion relation as `paraphrase`, `superordinate`, `component_action`, `component_participant`, or `construction_proposal`. A construction proposal is not a lexical hit. Never represent a model's suggested phrase as found in the dictionary unless an attestation or quoted grammar example proves it.

**Diagnostics:** query `路人` + `路` + `走` + `人`, `香味` + `气味`, `玩具` + `玩` + `东西`, `饮料` + `喝` + `东西`, `令人费解` + `理解` + `不能`. Search the specific witness shards; then separately check relational/nominalization evidence from `../translate-tujia/references/construction-choices.md` and the reference grammar. Report whether the **full** construction is directly attested, safely compositional, or provisional.

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
