# Participant-reported traces

These summaries retain the actual ordered operations reported by each participant. They are not an exported provider trace. `R` is `https://raw.githubusercontent.com/luggroo/bizic-translator/{revision}/skills/translate-tujia/`; bare reference filenames below are under `R/references/`. Each numbered row is one webpage-tool dispatch; one separate tool-name discovery preceded each run.

## Initial diagnostic

Agent `nojs_baseline`, revision `53c853a6d2eee3ecac7a6c119a56ab94efa71876`, attempted D1, D2 and D3. It reported 12 webpage dispatches, successful raw references, failed dictionary access and inaccessible original-book links. D1 produced a complete composed /ŋa²⁴ tsɿ²¹ ka²⁴/ from the compiled seated-eating example; rice's accent spelling was unresolved. D2 retained only the Southern pronoun with water/drink gaps. D3 retained the third-person form with predictive-arrival construction unresolved. This is a diagnostic, not the matched six-input comparison.

## Matched baseline

Agent `nojs_matched_baseline`, revision `53c853a6d2eee3ecac7a6c119a56ab94efa71876`.

| Call | Actual operations |
| --- | --- |
| 1 | open `R/SKILL.md` |
| 2 | open runtime-lifecycle, web-evidence, grammar-index, output, evidence, semantic-decomposition |
| 3 | open `https://tujia.biz/text/` (failed); clause-patterns, aspect-modality, source-lexical-notes, notation-audit, predicate-economy |
| 4 | open aspect-modality at lines100,180,210; retrieval; two tujia.biz grammar anchors for negation/property predicates (failed) |
| 5 | open retrieval line35; GitHub `bizic-dictionary/blob/main/docs/reference-grammar.md` (metadata only); tujia.biz volition/Southern anchors (failed); reference-first-check, sense-and-coverage |
| 6 | open `https://tujia.biz/grammar-reviewed-data.js` (failed); click observed GitHub Raw link (restricted) |
| 7 | open `https://raw.githubusercontent.com/luggroo/bizic-dictionary/main/docs/reference-grammar.md` |
| 8 | find in raw grammar: 你没有说话; 衣服脏; 我不想回家; 我会写字; 我在这里住了十年; 今天我要买猪 |
| 9 | find: 脏; 他不想回家; 我的衣服; north-6-2; south-notation |
| 10 | find: sībā; sǎ; ta⁵⁵ |

Reported totals: 10 webpage dispatches; 27 opens +1 click; 14 finds; 24 different URLs, 16 with body text, 1 metadata only, 7 failed. The reader returned a false negative for “衣服脏” before “脏” located the passage. No status code or elapsed time was obtained. N1/N3 accent spelling remained unresolved although paired forms exist in the bundled reference; the complete IPA clauses were retained. N2 additionally offered an explicitly rule-derived surface tone, separately from its source citation tones.

## Candidate 1 positives

Agent `nojs_candidate_1`, revision `207d3e31ac4c89a82c73dcb363656eaf26763a7c`.

| Call | Actual operations |
| --- | --- |
| 1 | open `R/SKILL.md` |
| 2 | open web-evidence, grammar-index, output, evidence |
| 3 | open clause-patterns, aspect-modality, notation-audit; `https://tujia.biz/text/` (failed) |
| 4 | open clause-patterns line89; aspect-modality lines95 and195; `https://tujia.biz/text/catalog.json` (failed) |

Totals: 4 webpage dispatches, 13 opens, 10 different URLs; 11 successful extraction operations, 2 failures. No find, click, local execution or conversion. The partial initial reference extractions were continued to the actual examples. Outputs and independent review are in [grammar-results.json](grammar-results.json).

## Candidate 1 challenges

Agent `nojs_adversarial_1`, same candidate revision. `G` is `https://raw.githubusercontent.com/luggroo/bizic-dictionary/4a9f521e7eaec4d5cea5b0bc82702da604a8ea39/docs/reference-grammar.md`.

| Call | Actual operations |
| --- | --- |
| 1 | open `R/SKILL.md` |
| 2 | open web-evidence, grammar-index, output |
| 3 | open aspect-modality, tujia catalog (failed), clause-patterns |
| 4 | open tujia text directory (failed), aspect-modality line84 |
| 5 | open aspect-modality line204, source-lexical-notes; exact Chinese queries 来, 冷, 胀, 明天 (all failed) |
| 6 | open G, paraphrase-and-borrowing, runtime-lifecycle |
| 7 | find in G: 明天; 两天; 胀; south-11; 预测; 持续 |
| 8 | find in G: 要做、快要做; 十年; 今天我要买猪; 长大; 将来; ʔdʑ |
| 9 | open G line2000, direction-suffixes |

Totals: 9 webpage calls, 20 opens, 12 finds. All six tujia URLs failed without status codes. All six target clauses remained precise structural gaps; the agent refused ability/planning as prediction, cooling as maintained cold and physiological bloating as balloon expansion. The extra failed queries and vague routing motivated candidate 2.

## Supplied dictionary relay

Agent `nojs_dictionary_relay`, skill revision207d3e3. Dictionary dependency rounds were catalog, six independent queries and seven independently selected details. Exact URL/time/hash records are in the 14 [fixtures](fixtures/).

It read query snapshots from revisiond37accd3 and detail snapshots from revision3ecafe77. These were host-captured original pages, not answer keys. All dictionary provenance is `supplied`. No direct tujia.biz access claim is made.

Reported reader calls: 8, including one unsupported `num_lines` argument error corrected to `lineno`. Seven successful calls contained 27 opens: 9 skill/reference opens and 18 snapshot opens including continuations. No expansion or whole-dialect table was needed. Tool-only durations exclude host publication, inference and waiting and are not used as an end-to-end latency metric. [Dictionary results](dictionary-results.json) include selected IDs and the independent review.

## Candidate 2 held-out and challenges

Agent `nojs_final_holdout`, revision `3ecafe77d2b276aa0ca3ba5330f80d9d22e8d848`.

| Call | Actual operations |
| --- | --- |
| 1 | open `R/SKILL.md` |
| 2 | open web-evidence, grammar-index, runtime-lifecycle, output |
| 3 | open aspect-modality, clause-patterns, notation-audit; catalog (failed) |
| 4 | open aspect-modality lines74,140,200; text directory (failed) |
| 5 | open source-lexical-notes, event-linking, paraphrase-and-borrowing |

Totals: 5 webpage calls, 16 opens, 13 different URLs; 14 reference extraction operations, 2 access failures. No further site attempts after the two failures. The aspect reference was covered in segments; the clause reference was read through line91 without a claim to have read its unseen tail. Results are in [holdout-results.json](holdout-results.json).
