# Bizic Translator

`tujia-lex` retrieves Tujia lexical senses and attested constructions from Chinese queries. It combines literal lookup with a real BGE embedding model and keeps each result's source, dialect, locality, spelling and citation available for inspection.

Lexical similarity supplies candidates. Translation still requires checking meaning, predicate class, argument structure, modality, negation and source compatibility. The reusable [translate-tujia Skill](skills/translate-tujia/SKILL.md) describes that workflow.

## Translation grammar cache (TAM and constructions)

The [translate-tujia Skill](skills/translate-tujia/SKILL.md) now starts with a **query-first grammar router**: [grammar-index.md](skills/translate-tujia/references/grammar-index.md). Search by Chinese semantic trigger (e.g. 快要、还在、不能、做完、用……切、定语) and read **only one relevant topic**:

- [aspect-modality.md](skills/translate-tujia/references/aspect-modality.md): aspect, prospective, still/not-yet, ability, permission, obligation, negation of modals; includes Northern source contrasts and Southern-specific examples.
- [event-linking.md](skills/translate-tujia/references/event-linking.md): `liex` vs `mor` vs `bor`, events and sequences, manner, states, instruments, background and condition clauses.
- [clause-patterns.md](skills/translate-tujia/references/clause-patterns.md): predicate forms, negation/prohibition, nominalization, property words, classifiers and noun phrase order.
- [notation-audit.md](skills/translate-tujia/references/notation-audit.md): how to check **tone-marked Pinyin against IPA**, keep source IPA unchanged when inconsistent, and register missing tones or source conflicts.

For example, Chinese "还" in "还在吃", "还没吃", "还没吃完" and "还不必睡" need **different whole-predicate constructions**, not a universal adverb. The reference distinguishes direct published examples, other Northern localities, supplemental unpublished speech data and teaching combinations. It is a translation aid, not a license to combine all suffixes freely.

Packaging includes **both Markdown references by default**, without forcing an extra 16 MB of dictionary shards into every install:

```bash
python scripts/package-translator.py --output /tmp/bizic-translator-package
# For offline exact dictionary lookup in the packaged output:
python scripts/package-translator.py --output /tmp/bizic-translator-with-static --include-static-lexicon
```

The small local grammar QA is `python scripts/check-grammar-skill.py`; it runs `scripts/lint-grammar-references.py` to compare **tone-marked Pinyin + IPA** for every standardized example, verify source labels, and test that all topic files ship in the packaged Skill. GitHub Actions runs it on reference/packager changes.

## Shared semantic decomposition for both retrieval modes

**Both BGE and the static skill route use [the same semantic decomposition and constructional recomposition rules](skills/translate-tujia/references/semantic-decomposition.md).** The only difference is whether planned queries are sent to real BGE cosine retrieval or to the versioned exact-match shards. In normal translation, give a fluent complete draft, with one overall quality note at the end. The dedicated [Codex evaluation plan](docs/embedding-route-evaluation-plan.md) specifies reproducible baselines, withheld challenges and failure analysis.

## Two retrieval modes (always disclose which ran)

`translate-tujia` chooses **real BGE embedding retrieval** in a local/Codex environment that can actually provision Python, the pinned model and a full schema-compatible index. The first run may install/build according to this README, but subsequent queries should **reuse** those assets. A real model query must return actual scores, IDs and source witnesses.

When the environment cannot run/install BGE, it invokes the separate [tujia-synonym-lite skill](skills/tujia-synonym-lite/SKILL.md), backed by [a bounded concept-expansion map](skills/tujia-synonym-lite/concepts.json) and the existing static dictionary shards. This is **human/skill guided near-synonym/paraphrase/component expansion plus exact attestation lookup**, never embedding. Both the first substantive progress update and final translation explicitly say which retrieval mode was used.

Run the lightweight mode locally, without ML dependencies:

```bash
python scripts/lightweight-synonym-search.py '经济损失' --dialect north
python scripts/lightweight-synonym-search.py '路人' --dialect north
python scripts/lightweight-synonym-search.py '香味' --dialect north
python scripts/lightweight-synonym-search.py '玩具' --dialect north
python scripts/lightweight-synonym-search.py '饮料' --dialect north
python scripts/lightweight-synonym-search.py '令人费解' --dialect north
# Non-curated phrase: add contextual candidate meanings, not just string segmentation
python scripts/lightweight-synonym-search.py '困难的想法' --related '难懂,理解,想,难'
```

The static shard files must be present (they are tracked in this repo; the default small package excludes them unless `--include-static-lexicon` is passed). A text-only GitHub agent can run the same skill by reading the manifest and only the FNV-1a-selected JSONL shards. Each result includes actual witness IDs, source aliases, original forms and senses; no fake cosine similarities. In particular, `经济损失` should expand to `钱`, `赔偿`, `经济` and other related candidates before deciding whether a Chinese lexical insertion is necessary.



## Install

Tested with Python 3.12.14, CPU PyTorch and four inference threads. Node.js 18+ supports the original site's spelling converters and their tests.

```bash
python -m venv .venv
.venv/bin/python -m pip install 'torch==2.7.1+cpu' --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements-evaluation.txt
.venv/bin/python -m pip install 'setuptools>=68'
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .

# Public source material remains external and ignored.
# HEAD/main includes the full current public dictionary, surveys, and grammar.
# For a reproducible run, pin a single source commit when cloning and use its
# site/dictionary.json.gz and other files together; do not mix snapshots.
git clone https://github.com/luggroo/bizic-dictionary.git .cache/bizic-data
git -C .cache/bizic-data rev-parse HEAD
.venv/bin/python scripts/download-embedding-model.py
```

The model downloader pins `BAAI/bge-base-zh-v1.5` revision `f03589ceff5aac7111bd60cfc7d497ca17ecac65`, detects the published weight format and records its checksum. Weights, source downloads, environments and generated indexes stay outside Git.

## Index and query

```bash
.venv/bin/tujia-lex build --repo .cache/bizic-data \
  --model-path .cache/models/bge-base-zh-v1.5 --output .cache/bge-index --batch-size 32 --threads 4

# Literal lookup; --substring provides a separate literal substring baseline.
.venv/bin/tujia-lex search 守候 --index .cache/bge-index --mode exact

# Real semantic candidates within a preferred source collection.
.venv/bin/tujia-lex search 守候 --index .cache/bge-index \
  --model-path .cache/models/bge-base-zh-v1.5 --source brassett-2004 --dialect north

# Construction retrieval is a distinct result type.
.venv/bin/tujia-lex search '用刀切肉，工具在动作前面' --index .cache/bge-index \
  --model-path .cache/models/bge-base-zh-v1.5 --kind construction --dialect north

# A specific survey point.
.venv/bin/tujia-lex search '用刀切肉' --index .cache/bge-index \
  --model-path .cache/models/bge-base-zh-v1.5 --kind construction --point 60757

.venv/bin/tujia-lex inspect --index .cache/bge-index
.venv/bin/tujia-lex inspect --index .cache/bge-index 'sentence:60757:0079'
```

`--source` accepts a source ID or a documented canonical alias such as `brassett-2004` or `brassett-2006`. `--point` selects a survey point, `--location` matches explicitly recorded locality metadata, and `--pos` matches the original source POS label. A Northern record with no locality is not automatically assigned to Longshan.

`--record-type` separates lexical senses, survey lexemes, survey sentences, text blocks, extracted bilingual passages and secondary grammar sections. Original transcriptions are retained. Cultural notes remain context rather than aligned translations; extracted paragraphs require alignment checks.

## Whole-dictionary coverage (checked at build time)

The selected `site/dictionary.json.gz` is fully enumerated: **every dictionary entry ID and every attestation ID must appear in the lexical records**, or `tujia-lex build` raises an error before model inference. Survey lexemes, survey sentences, Longshan text blocks, extracted corpus passages, and grammar sections are added through `collect`, with original source metadata preserved. Counts are in `manifest.json` (`lexical_entry_count`, `lexical_attestation_count`, `metadata.source_dictionary_entries` and `metadata.source_dictionary_attestations`). The manifest also records the exact source commit and file digests. A successful build is complete **for its selected source revision**, not a promise that upstream never changes.

Each dictionary sense now embeds *both* its Chinese and English gloss as separate vectors; retrieval takes the best score per sense and keeps its evidence. Original Tujia spellings, IPA, source IDs, locality, tone and notation are **retained and exact-searchable**, not embedded as though phonetic strings were semantic definitions. Records sharing a gloss may reuse a vector without losing attestation links. **Index schema v2 requires a rebuild from schema v1**.

## Text-only GitHub fallback (no dynamic search server)

The original dictionary gzip is small on disk but unreadable through GitHub's UTF-8-only text connector. A scheduled GitHub Action exports a bounded, read-only index from a versioned public source commit:

- `skills/translate-tujia/lexicon/manifest.json`: source revision, source checksum, entries, attestation count, field order and shard checksums
- `skills/translate-tujia/lexicon/XX-000.jsonl`: one directly readable text shard per FNV-1a UTF-8 query bucket, currently all under 110 KB
- `scripts/export-readable-lexicon.py`: standalone generator and lookup; Python stdlib only

```bash
python scripts/export-readable-lexicon.py lookup \
  --directory skills/translate-tujia/lexicon --query '守候' --limit 20

# Rebuild without hosting a public API (from the matching source checkout):
python scripts/export-readable-lexicon.py build \
  --source .cache/bizic-data/site/dictionary.json.gz \
  --output skills/translate-tujia/lexicon \
  --revision "$(git -C .cache/bizic-data rev-parse HEAD)"
```

For an agent with GitHub text reads but no mounted Python data, read only the manifest and matching shard (not all shards); match normalized `k`. Row `r` is a compact array ordered by the manifest's `record_fields`: entry ID, attestation ID, source, Tujia form, Chinese/English sense, POS, dialect, locator, source reference and same-attestation notation. The full original witness is still in the canonical gzip and local semantic index. This text fallback is an **exact-lookup** resource and cannot be mislabeled as an embedding run.

**DDoS protection:** there is deliberately no public per-query compute, gzip decompression, database scan, or embedding-inference endpoint. GitHub serves immutable/cacheable static files; translation routines cap the number of shard reads and reuse results. Generating/updating the assets is a scheduled offline job, with maximum input and decompressed sizes, maximum output file size and integrity hashes. This reduces origin work and abusive query amplification, though CDN services still need their provider's network-level anti-DDoS protection.

## Persistence and provenance

The persistent index consists of checksummed JSONL records, normalized float32 NumPy vectors and a model/input manifest. Search computes cosine nearest neighbors after scope filters. Identical Chinese texts share a vector row while sense and witness records remain distinct.

Merged entries are split using each attestation's own Chinese/English sense, POS and scope. Spellings are returned only where their attestation links intersect that sense. Unknown scope, original source qualifications and editorial translations remain visible.

BGE uses CLS vectors and its model-card Chinese query instruction. Long records use overlapping windows instead of silent prefix truncation. There is no synonym-list or keyword fallback for semantic search. A model/index mismatch or missing checkpoint raises an error. Builds do not overwrite existing directories; `--reuse-index` reuses checked, identical-text vectors from the same model.

## Evaluation and tests

```bash
.venv/bin/python scripts/evaluate-semantic-retrieval.py \
  --index .cache/bge-index --model-path .cache/models/bge-base-zh-v1.5
.venv/bin/python -m pytest tests --data-root .cache/bizic-data \
  --model-path .cache/models/bge-base-zh-v1.5 -q
.venv/bin/python scripts/render-semantic-evaluation.py
```

The tests exercise real-data schema handling, attestation links, source/locality/POS filters, persistent indexing, actual model inference, CLI behavior, long-text coverage and source-specific spelling. Model tests are explicitly skipped when `--model-path` is absent.

See [the retrieval evaluation](docs/semantic-retrieval-evaluation.md) and [execution records](docs/evaluation/). These are qualitative retrieval checks; they do not establish a translation accuracy score.

## Romanization

The original site's source-specific conversion rules are reused from the external data checkout:

```bash
printf '%s' '[{"mode":"ye","text":"ngaf"}]' | node scripts/tujia-lex-spelling.cjs .cache/bizic-data
```

The result is `ngá`. For an original witness, provide `mode: "source"`, its profile ID as `source`, and its unchanged spelling as `text`. Ambiguous and incomplete mappings remain explicit. Missing tones are not filled by guessing.
