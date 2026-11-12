# Skill structure and preservation review

Baseline: `b7918d28e067ff127025ad38af9b76b409b27b6d`. This review compares the reorganization with that committed version, independently of the document authoring pass. The main entry point moves from 55,118 to 8,082 UTF-8 bytes; size reduction is a navigation improvement, not a translation-quality metric.

## Organization

The entry point now owns task defaults, a six-step translation workflow, reference routing, bounded recovery and the final quality note. Runtime commands, source policy, complex clause analysis, paraphrase/borrowing and output/audit details each have a named reference. Existing grammar topics and evidence tables retain stable filenames. The separate synonym-lite skill remains callable; runtime implementation stays in `src/`, maintenance commands in `scripts/`, and experiment artifacts in `docs/evaluation/`.

## Behavior and evidence coverage

| Baseline requirement | Location after reorganization | Review result |
| --- | --- | --- |
| Complete every meaningful clause; audit-only task exception | `SKILL.md`, `references/output.md` | Preserved |
| Tone-marked Pinyin before aligned IPA; Ye only on explicit request; honor output override | `SKILL.md`, `output.md`, `notation-audit.md` | Preserved |
| One general quality note; detailed sources only for audits; narrow essential phonetic gaps | `SKILL.md`, `output.md` | Preserved; conflicting blanket per-word warning removed from grammar index |
| Actual current Embedding / Skill-based / Mixed disclosure; historical scores are not new runs | `retrieval.md`, `output.md` | Preserved |
| Real BGE with pinned complete compatible index; one feasible setup attempt; cached bounded fallback | `retrieval.md`, `recovery-playbook.md` | Preserved |
| Shared semantic planning, productive frames and explicit Interpretation; context alone is not understanding | `semantic-decomposition.md`, `retrieval.md` | Preserved |
| Existing-word retrieval miss versus lexical gap; survey versus static coverage | `retrieval.md`, `semantic-decomposition.md` | Preserved |
| B06 → B04 → localized Longshan → labeled Northern; user locality override; Southern separate | `SKILL.md`, `evidence.md`, grammar references | Preserved |
| Same-attestation forms, tones, source, dialect and notation links; no invented syllable fragments | `evidence.md`, `output.md`, `notation-audit.md` | Preserved |
| Continuous texts, variant story scope, original versus free translation, OCR/alignment and secondary evidence | `evidence.md`, `translation-workflow.md` | Preserved |
| Predicate-class and combination restrictions; scope of aspect, modality and negation | `translation-workflow.md`, grammar references | Preserved |
| Tujia classifier classes and order; supported native paraphrase before Chinese insertion; loans in Tujia syntax | `translation-workflow.md`, `paraphrase-and-borrowing.md` | Preserved |
| Progress with concrete translated passages; short tasks avoid artificial delays | `SKILL.md`, `output.md` | Preserved |
| Designated database and user materials during translation; permitted known-path setup; no exploratory web search | `SKILL.md`, `evidence.md`, `recovery-playbook.md` | Preserved |
| Generic thing heads may use independent nominalization; concrete heads/roles remain | `SKILL.md`, `nie-niexi.md`, `semantic-decomposition.md` | Preserved |
| Feng/Xiang differences, original untoned examples, productive versus original attestations | `nie-niexi.md`, `notation-audit.md`, `grammar-index.md` | Preserved verbatim in detailed reference; display scope clarified in index |
| Warming requires causation; fire-specific 烤火 is not a general synonym; resultant state in 画地为牢 | `nie-niexi.md`, `aspect-modality.md` | Preserved |
| Read access does not authorize reproducing restricted sources; public serving is bounded/offline | `output.md`, `retrieval.md`, `recovery-playbook.md` | Preserved |

The review identified and corrected a pre-existing role error: the semantic-decomposition table called 陌生人 an agent nominalization. It now explicitly treats the person as the patient of recognition, consistent with the implemented planner. A pre-existing `event-linking.md#time` link lacked its target; the anchor is now present. The grammar index now routes directly to nie/niexi, and distinguishes normalized dual-notation tables from quotations whose original source omits tones.

## Unchanged linguistic data

All baseline table rows containing superscript source-tone digits remain byte-for-byte present in their original files. This selects 81 rows, including two notation-audit comparisons and analytical rows; it is distinct from the grammar linter's count of 74 paired examples.

| Reference | Selected rows preserved | SHA-256 of selected rows joined by LF |
| --- | ---: | --- |
| `aspect-modality.md` | 48/48 | `38f82d948e751ebe64f188573ecb1fbfa98f2df39399b5986dfcc2c8e6685af1` |
| `notation-audit.md` | 2/2 | `b86b0681cc379906b112d4401552f76e51b0de707914b2a6806121e184781bd9` |
| `clause-patterns.md` | 13/13 | `79ebe8af19a0f15aa1478890049c3bf68e280213d22dc6de42f95ec12ffc1ec3` |
| `event-linking.md` | 18/18 | `9ce630f060e8871966bee55a7fd4298ad82f19d7a07977bc08cb45e811b4a5a7` |

The full `nie-niexi.md` reference remains unchanged. It retains the user's recent corrections and the checked Feng/Xiang examples, including their scope and missing-tone limitations.

| Unchanged inventory | Files | Aggregate SHA-256 |
| --- | ---: | --- |
| `skills/translate-tujia/lexicon/` | 257 | `97c71a7e7a82af77de59287d40c21fcd46c2c02528efa934e38eaa934cebd52b` |
| `skills/tujia-synonym-lite/` | 2 | `74b43dd96cfbfb8b9afa7ccba942f6f9e95fdc952e38a0cac1af21f307c8aca7` |
| `src/tujia_lex/` | 10 | `eecbbd5ec63f37413f9e144c7e9150ed4fbf9c1a9cc65a14a112e52da62cf4ab` |

Aggregate hash definition: SHA-256 of UTF-8 lines `relative_path + " " + file_sha256`, sorted by path and joined with LF, without a trailing LF. The static inventory contains its manifest and all 256 shards. No planner, retrieval, construction, model, dictionary or notation-conversion behavior was changed by this reorganization.

## Checks and limits

The independent review ran `python scripts/check-grammar-skill.py` successfully after reorganization. The notation linter still reports 74 paired examples, with 20 explicitly lacking independent verification. Reference navigation, local anchors, packaged references and bounded static lookup checks passed. The new structural test suite covers broken/missing routes, missing anchors, duplicate anchors, Unicode/reference links and absent/corrupt lexicon shards; the parent validation run records the complete test outcome.

These checks establish preservation of inspected instructions, source examples, executable behavior and package dependencies. They do not establish native-speaker accuracy, independently validate every IPA value, or prove that every future model response will be identical. No new linguistic claims or re-scored retrieval benchmark are inferred from the smaller entry point. Behavioral confidence comes from preserved constraints and unchanged runtime/data, with existing grammar and real-model tests run separately.

## Final execution results

- `.venv/bin/python -m pytest tests --data-root /workspace/bizic-dictionary --model-path .cache/models/bge-base-zh-v1.5 -q`: **46 passed in 21.25s**, including actual BGE inference and the 11 structural regression cases.
- `.venv/bin/python scripts/check-grammar-skill.py`: passed; all reference routes and both export modes checked; 74 paired examples, 20 independently unverified, unchanged from baseline.
- QA was also executed from a full exported package, and from an intentionally slim export with `--without-static-lexicon`; both passed. Slim mode explicitly reports that static lookup/hash checks were not evaluated. Default repository QA continues to require the manifest and valid shards.
- `git diff --check`: passed. Runtime modules, static lexicon and synonym-lite files have no diff from the baseline.
- CI now runs structural failure tests and grammar/package QA on relevant pushes and pull requests. This report records successful local execution; remote CI status is separate.

For future maintenance, add a reference through the entry point or an existing topic route, keep linguistic example rows source-linked, and run both the grammar QA and structural tests. A file merely being present in the package no longer suffices: unreachable instructions and broken anchors fail QA.
