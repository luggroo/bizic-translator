---
name: tujia-synonym-lite
description: No-model, low-cost semantic-bridge retrieval for Tujia translation; expands difficult Chinese/English phrases into meaning-aware exact queries against versioned Bizic dictionary shards and documents actual witnesses.
---

# Tujia synonym-lite / 土家语轻量级近义概念检索

This subskill runs **Skill-based concept expansion + real dictionary exact lookup** when the BGE model cannot execute; disclose the retrieval mode once in the first update and once at the end. Its semantic decomposition technique is **shared with the Embedding route** via `../translate-tujia/references/semantic-decomposition.md`. Produce a confident complete translation; one overall quality note is enough. Only actual embedding runs may report vector scores.

Choose this route directly from the [environment preflight](../translate-tujia/references/runtime-lifecycle.md) when local inference or durable provisioning is unavailable; a failed BGE installation/build is not required first. If compatible BGE assets already exist, reuse them even offline. A capable environment missing assets should seek a verified durable destination and record reusable paths before provisioning.

Record the specific observed blocker or the user's explicit choice of static retrieval. Missing packages/model/index or an unchecked environment alone are not evidence of inability; inspect the relevant setup/storage conditions first. Reassess the affected condition if access or available assets change.

## Failure → recovery (follow before expanding search)

This subskill inherits [the translator's blocker-to-action router](../translate-tujia/references/recovery-playbook.md). Treat every *cannot / never / avoid / not* warning as a routing cue, with an executable next step.

| Trigger | Instead → |
| --- | --- |
| Environment preflight selects static-only | Use the [text dictionary route](../translate-tujia/references/web-evidence.md) when URL reading exists; otherwise use readable static/supplied evidence. Label actual lookup **Skill-based**, with no cosine score. Missing assets alone do not require fallback when capability and durable provisioning are established. |
| Original compound is absent | Query a plain paraphrase, predicate, participant/object head, and necessary relation using `--related` if not in `concepts.json`. |
| No static shard was readable | Recalculate the bucket from NFKC/casefold UTF-8 and inspect `manifest.json`; if the export is missing, use an authorized local dictionary/corpus checkout. Report **lookup unavailable**, rather than **zero matches**. |
| A hypernym or example loses meaning | Add the missing species/property/action as a modifier or a second clause, or reject the candidate and try another verified witness. |
| No matching source/locality | Filter Brassett 2006 → 2004 → explicitly local Longshan → source-labeled Northern; if no native exact expression fits, compose or use a minimal Chinese insertion. |
| `-ma/-xi/-ci`, particles or argument roles uncertain | Route once through `grammar-index.md` to the relevant nominalization/role or TAM section; select the matching source-backed construction. |
| Pronunciation, attestation or score is unsupported | Inspect the original record and `notation-audit.md`; output verified 调号拼音 only, falling back locally to source `/IPA/` when spelling is unavailable; mark a pronunciation gap only if both are missing, and omit vector scores. |
| More than 8–12 repeated queries are still returning broad related words | Stop expanding; compare the best verified candidates and deliver a complete native paraphrase or transparent Chinese insertion. |

## How it works

In a webpage-only environment, apply expansion through the [text dictionary route](../translate-tujia/references/web-evidence.md), using only advertised queries/details. The FNV procedure below applies when a tool resolves the bucket or an exact path is supplied. Keep unpublished coverage, failed access and a real zero-match response distinct; do not invent hashes or static URLs. No successful lookup means no claim of executed Skill-based retrieval.

1. **Separate the sense from the characters.** Identify referent, predicate, roles, polarity, modality and context before querying. Expand *the intended sense* even if a compound has no literal entry.
2. **Generate a bounded candidate lattice, not an automatic synonym list** (see `concepts.json` for examples): (A) original phrase; (B) true paraphrase/near synonym; (C) hypernym or common specific examples, explicitly labeled; (D) components such as head noun, action, property, participant and result; (E) possible compositional Tujia construction. A specific example of a category is **not** a translation of the category.
3. **Look up each Chinese/English candidate in the actual Bizic static lexicon.** The authoritative export is at `../translate-tujia/lexicon/manifest.json` and its `XX-000.jsonl` shards. Read the manifest once; for each NFKC+casefold+trim query, compute FNV-1a over UTF-8 bytes (32-bit: start 2166136261; xor byte then multiply by 16777619 mod 2^32; take highest byte as two hex digits). Read only `buckets[hex]` named shard(s), compare each row's `k` exactly, and decode `r` using `manifest.record_fields`. **If the shard is unreadable, recheck the manifest/bucket and use a local authorized dictionary checkout; label the result ‘lookup unavailable’ until a verified query completes.** In a Python workspace with the files, use `python scripts/lightweight-synonym-search.py "query" --directory skills/translate-tujia/lexicon`; for an unfamiliar phrase, pass model-generated candidates through `--related "候选1,候选2"`.
4. **Select witnesses by meaning and source**, not just the match count. For Northern Longshan start with Brassett (2006), then 2004; broaden to attested Longshan/northern evidence with explicit provenance. Resolve the source alias using `manifest.sources[r[2]].canonical_id`. Keep each spelling with its own attestation and source; check an explicitly Longshan or Brassett witness and label any Northern/Southern borrowing as such.
5. **Compose with target-language grammar.** Read `../translate-tujia/references/semantic-decomposition.md` plus the relevant topic in `../translate-tujia/references/clause-patterns.md` or `aspect-modality.md`; determine the intended nominalized participant/object and confidently reuse productive syntax. Keep exact-attestation distinctions in the audit, not repeated beside the fluent translation.
6. **Deliver the translation first.** 静态降级只写已核定的调号拼音；缺拼音的片段就地写来源 `/IPA/`，不另列整句 IPA。静态词典 v2 的 `term` 已统一为站点调号拼音或 `/IPA/`，直接使用；`source_term` 仅作来源见证，不得据此手拟拼音。采用主 skill 的[记音核验规则](../translate-tujia/references/notation-audit.md)。 Maintain a compact internal query trace (expansions, hits, IDs, sources and senses). Show the detailed trace only when the user explicitly requests retrieval validation; in ordinary use, disclose the retrieval mode and give one overall quality note, not a disclaimer per constituent.
7. **Bound cost:** normally 8–12 targeted queries, deduplicated buckets and cached results. If no native equivalent emerges, paraphrase productively or use the smallest meaningful Chinese insertion. For each citation, copy the retrieved witness ID; for missing tones use the source-aligned notation audit and mark the local missing span; for scores report ‘Skill-based (no embedding score)’.

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

For a short input, query the original term, a plain paraphrase, the core predicate and a semantic head/participant. Prefer Brassett (2006) for Northern/Longshan, then 2004. Label candidate relations as broad term / instance / synonym; keep the missing meaning with an attested modifier or another clause, or choose the closer witness.

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

## Shared executable planner

The lightweight script now calls `src/tujia_lex/query_plan.py`, the same planner as
`tujia-lex plan --route C`. `tujia-lex plan --route D` provides the complete static
route, including candidate selection and construction audit. `concepts.json`
remains a source of examples; the executable route uses productive frames and an
explicit `Interpretation` for new contextual meanings. Optional `--related`
queries add lookup candidates without changing semantic roles or polarity.

A no-hit compound is not a missing semantic field. Check the planned predicates
and arguments, source gloss variations and dictionary/survey coverage separately.
Keep the source-linked query trace internal during ordinary translation and give
the complete proposed translation first.
