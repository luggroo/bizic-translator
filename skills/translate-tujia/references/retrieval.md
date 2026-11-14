# Retrieval modes and commands

Read when starting lexical retrieval, checking runtime availability, or diagnosing a missing word. Both engines use the [same semantic plan](semantic-decomposition.md). Source selection follows [evidence.md](evidence.md); ordinary output follows [output.md](output.md).

<a id="runtime-verification"></a>
## Choose the executable route

First perform the [environment and storage preflight](runtime-lifecycle.md). Installation/build is an outcome of that assessment, not a probe to discover whether the environment is suitable. Find existing assets and their registry before creating anything.

Retain observed checks, paths and reasons. Distinguish **not checked**, **missing but provisionable**, **verified usable**, and **blocked**; inspect installation resources and access for missing assets. A concrete capability/access/storage blocker is sufficient for direct static retrieval without a failed full setup. An explicit user choice of static retrieval overrides the BGE preference. Reassess only affected checks when access or assets change. Record zero matches from a successful scoped query as a retrieval result.

| Available environment | Action | Disclosure |
| --- | --- | --- |
| Webpage reader with no execution, or explicit webpage-only task | Read the [text dictionary and its actual links](web-evidence.md); keep coverage separate from access failure | 检索模式：Skill-based（网页静态词典；本地未执行） after successful lookup |
| Executable runtime with compatible existing model/index, including offline or read-only assets | Validate and query the existing installation; reuse loaded assets | 检索模式：Embedding（BGE 实际运行） |
| Missing assets; preflight confirms execution/resources/download access and durable storage | Provision only what is missing at the durable destination, register it, then query | 检索模式：Embedding only after successful current inference |
| Readable static export/supplied evidence, insufficient resources/access, or no durable destination for new setup | Use [synonym-lite](../../tujia-synonym-lite/SKILL.md) with an actually available lookup route, without first trying the full BGE pipeline | 检索模式：Skill-based after real lookup; identify supplied evidence separately |
| Both engines actually execute | Keep the engine and query provenance for each result | 检索模式：Mixed |

Verify availability before claiming a mode. Report the observed engine and current query result; mode placement and final presentation follow the output policy. Base the mode label on the current query result. If a later operation encounters an unforeseen blocker, stop at that stage and use static lookup; preserve reusable files and record the reason rather than restarting setup.

## Executable semantic plan

Commands below run from the **bizic-translator repository/package root**, not this reference directory. Obtain the application, canonical public data and pinned model using its [README setup](https://github.com/luggroo/bizic-translator#readme). Reuse the model/index after setup.

| Task | Command | Result |
| --- | --- | --- |
| Planned embedding retrieval | `tujia-lex plan EXPRESSION --route C --index INDEX --model-path MODEL` | Separate original and rewritten BGE queries; preserved raw baseline |
| Planned static lookup | `tujia-lex plan EXPRESSION --route D` | Same plan, exact shard witnesses; no cosine scores |
| Hybrid | `tujia-lex plan EXPRESSION --route E --index INDEX --model-path MODEL` | Both engines, candidate selection and construction checks |
| Literal baseline | `tujia-lex search '守候' --index INDEX --mode exact` | Whole-field match; `--substring` is a separately labeled baseline |
| Raw lexical BGE query | `tujia-lex search '守候' --index INDEX --model-path MODEL --dialect north` | Ranked neighbors; use `--source brassett-2006` or `brassett-2004` for source comparisons |
| Construction retrieval | `tujia-lex search '用刀切菜，工具在动作前面' --index INDEX --model-path MODEL --kind construction --dialect north` | Sentence blocks, extracted passages and grammar sections with distinct evidence levels |
| Original witness | `tujia-lex inspect --index INDEX RECORD_ID` | Forms, attestation links, source, locality and citation |

`src/tujia_lex/query_plan.py` supplies the reusable planner; `scripts/lightweight-synonym-search.py` shares it. Productive rules preserve new arguments and scoped negation/TAM. For an opaque or contextual meaning outside those rules, supply an explicit `Interpretation` with `--interpretation FILE.json`. Use `--context` to retain audit context and `--interpretation` to supply the semantic analysis. [concepts.json](../../tujia-synonym-lite/concepts.json) supplies example query plans.

For scoped `search` queries, `--point` selects a survey point, `--location` matches explicitly recorded locality, and `--pos` matches the source's own POS label rather than a universal category. Use `--record-type` to distinguish a lexical sense, survey sentence, grammar section or corpus passage; a bilingual paragraph or grammar summary has different evidential scope from an aligned sentence. Compare Brassett 2006 and 2004 at the individual-attestation level, resolving source aliases through [source selection](evidence.md#source-selection). Record each source's actual coverage, then compare supplementary local evidence.

Inspect the index manifest for the exact model/revision, pooling, dimensions, checksum, schema and source snapshot. Full coverage means all entries and attestations from that revision; grouping compatible senses must retain their witnesses. Both Chinese and English glosses receive semantic vectors. Forms, IPA, tones, notation links, locality and source remain in inspectable exact fields. Verify completeness through manifest counts and actual query records. For an incompatible index, first apply the preflight/storage gate; rebuild only the affected index when justified, retaining the working version until validation.

## Text-only dictionary lookup

For a URL-only reader, first use [published HTML](web-evidence.md). Coverage is limited to actual listings. Use the shard procedure below when a tool can resolve the bucket or its exact path has been supplied; otherwise report that route unavailable rather than inventing FNV results.

Use the [static manifest](../lexicon/manifest.json) and its UTF-8 shards when a text-only connector cannot decompress the canonical gzip. The UTF-8 shards provide the text-only lookup route. For an unfamiliar compound, first expand its sense through [synonym-lite](../../tujia-synonym-lite/SKILL.md).

1. Normalize the query with NFKC, casefold and trim.
2. Compute FNV-1a over its UTF-8 bytes: start at 2166136261; XOR each byte, multiply by 16777619 modulo 2^32; take the high byte as two hexadecimal digits.
3. Read only the files named by `manifest.buckets[hex]`. Match `k` exactly and decode `r` using `manifest.record_fields`.
4. Resolve `manifest.sources[r[2]].canonical_id`. Preserve entry ID, attestation ID, form, senses, POS, dialect, locator, source reference and same-attestation notations. An unmapped source has unknown scope.
**展示规则（format 2）：** `term` 已在导出时统一为站点调号拼音；不能完整转换的条目已改用同见证 `/IPA/`，两者皆缺则为局部读音缺口。`term_notation` 标明记音类型，`notations` 只含 `accent`／`ipa`。`source_term` 是来源原字面，供溯源，不用于译文展示；原拼写仍可作检索键。直接使用 `term`，无需在静态环境运行转换器。详见 [notation audit](notation-audit.md)。静态降级不另列 IPA 栏。

5. Deduplicate shard reads and cache results. If a shard is unreadable, retry the correct manifest/bucket or use an authorized local dictionary; report **lookup unavailable** until a query succeeds.

With a local runtime:

```sh
python scripts/lightweight-synonym-search.py '原词' --directory skills/translate-tujia/lexicon --related '候选1,候选2'
python scripts/export-readable-lexicon.py lookup --directory skills/translate-tujia/lexicon --query '好'
```

The export is versioned, not live by assumption. Check revision, SHA-256 and entry/attestation totals when coverage or freshness matters. Its source catalog comes from the same `site/data.json.gz` revision. Full attestations and corpus evidence remain in the canonical data/local index. If an optional packaged export is absent, use known-path reads of the public manifest/shards or an authorized local checkout.

<a id="read-grammar-section"></a>
## Read a linked grammar section

First read the relevant bundled grammar topic and reuse its cited rules and complete examples. Follow the matching tujia.biz link for a named missing condition or conflict; reading the original site again is not a prerequisite for using a compiled quotation. If the page is unreadable, retain that status and continue with supported bundled evidence. The [raw reference grammar](https://raw.githubusercontent.com/luggroo/bizic-dictionary/main/docs/reference-grammar.md) is a larger fallback for a specific anchor, not a default download for every sentence. Preserve its revision separately if known. A reader search miss or truncated excerpt does not prove that a construction is absent.

With a tool that can actually inspect serialized chapter data, [grammar-reviewed-data.js](https://tujia.biz/grammar-reviewed-data.js) is another route: `REVIEWED_GRAMMAR` groups chapters under `north` and `south`, and `GRAMMAR_ANCHORS` maps anchors to chapters. This is optional and does not require executing JavaScript in the webpage-only route. Reuse any successfully retrieved chapter.

## Misses, scores and cost

Separate a missed existing entry from a missing lexicalization: inspect full-index exact lookup, alternate source glosses and dictionary versus survey coverage. Expand a no-hit compound through its semantic field. For ordinary translation, use the best-supported native construction, then a minimal Chinese insertion under [borrowing rules](paraphrase-and-borrowing.md); complete the clause.

For an explicit audit, report original/rewritten queries, query-local scores, raw ranks, witness IDs, forms, senses, sources and accepted/rejected candidates. Label synonym, paraphrase, component, hypernym and example relations. Only actual embedding queries have cosine scores; RRF is a combination statistic. Use the CLI's source-notation draft and slot checks internally, then compose the Pinyin/IPA translation.

Keep each unfamiliar concept to one literal lookup and one bounded expansion batch (normally 8–12 deduplicated lite queries). Cover the relevant Chinese and English senses, components and continuous-text contexts within that budget; record coverage and [reconcile suitable candidates with the draft](evidence.md#retrieval-status-and-draft-reconciliation). For a grammar question, use one routed topic and one relevant contrast; expand for a specific unresolved role or scope conflict. Reuse manifests, loaded models, indexes and cached witnesses. [Recovery actions](recovery-playbook.md) supply the next step when a route fails.

For public serving, build embeddings and shards offline and serve bounded, cacheable artifacts. Move dictionary-wide scans, index building, gzip decompression and expensive inference to local/offline jobs instead of doing them per incoming public request. Use request limits; serve static assets through the provider’s caching and request controls.
