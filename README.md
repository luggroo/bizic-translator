# Bizic Translator

`tujia-lex` retrieves Tujia lexical senses and attested constructions from Chinese queries. It combines literal lookup with a real BGE embedding model and keeps each result's source, dialect, locality, spelling and citation available for inspection.

Lexical similarity supplies candidates. Translation still requires checking meaning, predicate class, argument structure, modality, negation and source compatibility. The reusable [translate-tujia Skill](skills/translate-tujia/SKILL.md) describes that workflow.

## Install

Tested with Python 3.12.14, CPU PyTorch and four inference threads. Node.js 18+ supports the original site's spelling converters and their tests.

```bash
python -m venv .venv
.venv/bin/python -m pip install 'torch==2.7.1+cpu' --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements-evaluation.txt
.venv/bin/python -m pip install 'setuptools>=68'
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .

# Public source material remains an external, ignored dependency.
git clone https://github.com/luggroo/bizic-dictionary.git .cache/bizic-data
git -C .cache/bizic-data checkout bc3aadfbe877d83b723f6ad37dfc1d0df0b48198
.venv/bin/python scripts/download-embedding-model.py
.venv/bin/python scripts/fetch-dictionary.py \
  --url https://raw.githubusercontent.com/luggroo/bizic-dictionary/bc3aadfbe877d83b723f6ad37dfc1d0df0b48198/site/dictionary.json.gz \
  --output .cache/dictionary.json.gz
```

The model downloader pins `BAAI/bge-base-zh-v1.5` revision `f03589ceff5aac7111bd60cfc7d497ca17ecac65`, detects the published weight format and records its checksum. Weights, source downloads, environments and generated indexes stay outside Git.

## Index and query

```bash
.venv/bin/tujia-lex build --repo .cache/bizic-data --dictionary .cache/dictionary.json.gz \
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
