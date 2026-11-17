# Static retrieval latency and default route

Ordinary translation uses static semantic decomposition and exact witness lookup. Embedding code remains available through explicit `plan --route B/C/E` or `search --mode semantic`. Existing model files or a static miss do not enable inference. Default static planning imports neither NumPy nor model/index modules; ML dependencies are in the optional `embedding` extra.

## Local measurements

Measured on 2026-11-17 against commit `b24a06d`, in the same workspace and Python environment. Each comparison alternated execution order. These timings cover local commands and retrieval, not model generation, network reads, PDF rendering or an entire translation task.

| Measurement | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| New CLI process, `plan 饮料 --route D`, median of 9 runs | 146.6 ms | 74.0 ms | 49.5% |
| 60 concepts through lite, median of 5 runs | 1.534 s, separate reader per concept | 0.828 s, shared verified reader | 46.0% |

The CLI comparison uses the same explicit static route on both versions. Batch savings require one process/shared reader; the lightweight CLI accepts several positional concepts and shares its reader. Single-concept JSON output retains its original shape; multi-concept output contains a `results` list.

The existing 60-case `tests/data/semantic-compositional-challenge.json` was run before and after the change. Planned candidates, provenance, query traces and construction outputs were identical after excluding timing/cache/cost telemetry. All 60 lite reports were identical, including witness order and source metadata; the shared-reader batch also matched those reports. This establishes static-output preservation for these cases. It does not establish new translation accuracy, embedding/static equivalence or an independent blind-test result. A preliminary whole-suite retrieval timing showed no stable single-query improvement; the measured gains above are startup and batch reuse.

## Reproduce the comparison

Extract baseline `src/` and `scripts/` with `git archive b24a06d src scripts` into a scratch directory. Run each version's `python -m tujia_lex.cli plan 饮料 --route D --lexicon PATH/TO/CURRENT/LEXICON`, setting `PYTHONPATH` to that version's `src`. Time fresh subprocesses, alternating order, and compare medians.

For the batch comparison, load the challenge expressions and call `scripts/lightweight-synonym-search.py`'s `run` for each. Compare fresh readers with a shared `StaticLexicon` supplied via `lexicon=reader`. Keep the lexicon, dialect, query limit and output checks identical.

The skill's [execution state](../skills/translate-tujia/references/execution-state.md) specifies cumulative budgets and reusable translation records. These are task-level operating rules; the CLI does not persist or enforce a cross-process ledger. Gloss/PDF follow-ups reuse the saved linguistic record, while an actual renderer still follows its own format checks.
