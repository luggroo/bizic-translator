# Retrieval modes and commands

Read when starting lexical retrieval, checking runtime availability, or diagnosing a missing word. Both engines use the [same semantic plan](semantic-decomposition.md). Source selection follows [evidence.md](evidence.md); ordinary output follows [output.md](output.md).

## Choose the executable route

Complete the runtime verification below before applying this table. An explicit user request for static retrieval takes precedence; record that choice as the reason for using Skill-based retrieval.

| Available environment | Action | Disclosure |
| --- | --- | --- |
| Python runtime with a compatible full index and BGE model, or feasible one-time setup | Follow the repository's pinned setup, run a current query, and reuse loaded assets | 检索模式：Embedding（BGE 实际运行） |
| Verification establishes a concrete execution/setup blocker, or the single feasible setup/query attempt fails | Record the blocker and use [tujia-synonym-lite](../../tujia-synonym-lite/SKILL.md) against versioned shards | 检索模式：Skill-based（概念扩展＋静态词典精确查询；没有运行 embedding） |
| Both engines actually execute | Keep the engine and query provenance for each result | 检索模式：Mixed |

Verify availability before claiming a mode. While checking, say `正在验证检索模式`; announce the actual mode at the first substantive update and again after the translation. A package installation, remembered synonym, static JSON file or historical evaluation is not a current embedding run; use the executable fallback when no current encoding/search succeeds. Keep model troubleshooting to one feasible setup attempt during ordinary translation.

<a id="runtime-verification"></a>
## Mandatory runtime verification before fallback

Perform these checks once per environment and reuse the evidence while conditions remain unchanged. Distinguish **not checked**, **missing but installable**, **verified usable**, and **blocked/failed**. Only the last state justifies an environment-based fallback.

1. **Execution and dependencies.** Inspect the available execution tools. With a shell, check Python and the repository's required dependency imports/versions. If no execution tool exists, record that tool limitation; do not claim an attempted model run. A missing Python package triggers the setup check, not immediate fallback.
2. **Reusable assets.** Check the repository's configured cache/model/index paths and any known reusable locations. Inspect existing model and index manifests for revision, schema, source coverage and compatibility. Missing weights, an absent index or incompatible assets trigger the setup check.
3. **Setup feasibility.** For missing requirements, check a writable environment/cache location, available disk and RAM against the setup requirements, and access to the specific pinned package/model/data downloads. CPU execution is supported; lack of a GPU is not a blocker. Offline access is not a blocker if compatible assets are already local. A failed GitHub request does not establish that every model/package endpoint is inaccessible. After an authorized network route succeeds, reassess the earlier access failure.
4. **One setup attempt when feasible.** Follow the README's pinned dependencies, model revision and source snapshot; install missing components in an isolated environment, obtain the model/data, and build or repair the compatible full index once. Continue without asking for permission for already authorized setup. If a concrete resource/access restriction prevents setup, record the observed restriction instead of starting an impossible download/build. Do not skip feasible setup merely because the translation is short or static lookup is easier.
5. **A current-task query.** Run a real BGE query using an expression from the user's current text. Check that query encoding and vector retrieval actually executed and returned a valid result with inspectable IDs/scores where matches exist. Imports, model loading, planner output and old evaluation files alone do not pass this check. Zero matches from a successful scoped query are a retrieval result, not an execution failure.
6. **Record the decision.** Retain commands/tool checks, relevant results, asset paths/revisions and the selected mode in the internal task trace. If falling back, name the specific failed check or setup/query error in one short progress update, then continue with Skill-based retrieval. Never describe an unattempted query as a failed run. If the user selected static retrieval, report that choice instead of inventing a runtime blocker.

Bound recovery to one feasible setup/build attempt; this limit does not waive the initial verification. If a material condition changes (for example, network access is restored or a compatible cache becomes available), reassess the affected check before reusing a fallback decision.

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

`src/tujia_lex/query_plan.py` supplies the reusable planner; `scripts/lightweight-synonym-search.py` shares it. Productive rules preserve new arguments and scoped negation/TAM. For an opaque or contextual meaning outside those rules, supply an explicit `Interpretation` with `--interpretation FILE.json`. `--context` stores text for audit; it does not make the deterministic parser understand arbitrary prose. [concepts.json](../../tujia-synonym-lite/concepts.json) contains examples, not an exhaustive synonym dictionary.

For scoped `search` queries, `--point` selects a survey point, `--location` matches explicitly recorded locality, and `--pos` matches the source's own POS label rather than a universal category. Use `--record-type` to distinguish a lexical sense, survey sentence, grammar section or corpus passage; a bilingual paragraph or grammar summary has different evidential scope from an aligned sentence. Compare source-filtered Brassett 2006 and 2004 witnesses before broadening Northern/Longshan selection.

Inspect the index manifest for the exact model/revision, pooling, dimensions, checksum, schema and source snapshot. Full coverage means all entries and attestations from that revision; grouping compatible senses must retain their witnesses. Both Chinese and English glosses receive semantic vectors. Forms, IPA, tones, notation links, locality and source remain in inspectable exact fields. A successful process exit alone does not prove completeness: compare manifest counts and the actual query records. Rebuild once with pinned compatible assets if feasible; otherwise use the static route.

## Text-only dictionary lookup

Use the [static manifest](../lexicon/manifest.json) and its UTF-8 shards when a text-only connector cannot decompress the canonical gzip. This is a known interface limitation, not an empty dictionary. For an unfamiliar compound, first expand its sense through [synonym-lite](../../tujia-synonym-lite/SKILL.md).

1. Normalize the query with NFKC, casefold and trim.
2. Compute FNV-1a over its UTF-8 bytes: start at 2166136261; XOR each byte, multiply by 16777619 modulo 2^32; take the high byte as two hexadecimal digits.
3. Read only the files named by `manifest.buckets[hex]`. Match `k` exactly and decode `r` using `manifest.record_fields`.
4. Resolve `manifest.sources[r[2]].canonical_id`. Preserve entry ID, attestation ID, form, senses, POS, dialect, locator, source reference and same-attestation notations. An unmapped source has unknown scope.
5. Deduplicate shard reads and cache results. If a shard is unreadable, retry the correct manifest/bucket or use an authorized local dictionary; report **lookup unavailable** until a query succeeds.

With a local runtime:

```sh
python scripts/lightweight-synonym-search.py '原词' --directory skills/translate-tujia/lexicon --related '候选1,候选2'
python scripts/export-readable-lexicon.py lookup --directory skills/translate-tujia/lexicon --query '好'
```

The export is versioned, not live by assumption. Check revision, SHA-256 and entry/attestation totals when coverage or freshness matters. Its source catalog comes from the same `site/data.json.gz` revision. Full attestations and corpus evidence remain in the canonical data/local index. If an optional packaged export is absent, use known-path reads of the public manifest/shards or an authorized local checkout.

## Misses, scores and cost

Separate a missed existing entry from a missing lexicalization: inspect full-index exact lookup, alternate source glosses and dictionary versus survey coverage. A no-hit compound is not a no-hit semantic field. For ordinary translation, use the best-supported native construction, then a minimal Chinese insertion under [borrowing rules](paraphrase-and-borrowing.md); complete the clause.

For an explicit audit, report original/rewritten queries, query-local scores, raw ranks, witness IDs, forms, senses, sources and accepted/rejected candidates. Label synonym, paraphrase, component, hypernym and example relations. Only actual embedding queries have cosine scores; RRF is a combination statistic. The CLI's source-notation draft and slot checks are internal aids, not a finished Pinyin/IPA translation.

Keep each unfamiliar concept to one literal lookup and one bounded expansion batch (normally 8–12 deduplicated lite queries). Reuse manifests, loaded models, indexes and cached witnesses. [Recovery actions](recovery-playbook.md) supply the next step when a route fails.

For public serving, build embeddings and shards offline and serve bounded, cacheable artifacts. Move dictionary-wide scans, index building, gzip decompression and expensive inference to local/offline jobs instead of doing them per incoming public request. Use request limits; static hosting reduces expensive amplification but does not guarantee protection against volumetric attacks.
