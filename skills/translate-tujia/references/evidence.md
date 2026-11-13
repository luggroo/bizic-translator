# Sources, dialect and attestation evidence

Read when choosing a source, resolving conflicting witnesses, or investigating a lexical/corpus gap. [Return to the translation workflow](../SKILL.md). Retrieval commands are in [retrieval.md](retrieval.md).

Start with the committed, locally available repository materials and the designated Tujia retrieval database. Use user-supplied materials with their provenance and access scope. Complete ordinary translations with this evidence, supported native paraphrase and Chinese insertions; reserve outside literature discovery for a separately requested research task.

## Source selection for Northern / Longshan

1. **Retrieve Brassett 2006, then 2004.** Search the intended sense, related Chinese and English senses, collocations and example constructions in each source. Record useful candidates and the actual coverage of each search. Apply this order to songs and short phrases as well as prose. An explicit user source request sets a different priority; a locality request such as Longshan sets the target variety for this comparison.
2. **Resolve individual witnesses.** Inspect each candidate's `attestations`, original gloss, full form, linked notations, locality and source citation. For canonical data, resolve the witness source through `site/data.json.gz` and `sourceAliases`; for static shards, resolve `manifest.sources[r[2]].canonical_id`. Treat a merged entry's top-level source as entry metadata and inspect all relevant witnesses within it.
3. **Compare supplementary evidence.** After recording the Brassett findings, consult explicitly localized Longshan materials, continuous texts and other Northern surveys for remaining gaps or conflicting local usage. When a local witness fits better, record its concrete advantage in meaning, construction or locality and the corresponding Brassett comparison. Describe an unlocalized Northern witness at its recorded scope. If a Brassett source is inaccessible, retain that availability status and continue with the available evidence.
4. **Select a complete form or construction.** Prefer the supported 2006 analysis when the original witnesses justify it; retain source-specific differences when 2004 or localized evidence supplies a different form. Confirm syllable boundaries and lexical meaning from the full attestation. Use a verified paraphrase or plain Chinese insertion for an unresolved lexical slot, and finish the proposed clause with a concise note about essential construction uncertainty.

Keep a compact internal record per intended sense: **2006 evidence or search status; 2004 evidence or search status; supplementary evidence; selected attestation; reason for selection**. Reuse records for repeated senses and show this detail in requested audits.

In the standalone `bizic-translator` project, the paths below are relative to the public-data checkout supplied as `--repo` (normally `.cache/bizic-data`), rather than the application directory. Follow the README to fetch that fixed source snapshot.

For a story, craft, custom, or other identifiable topic, first locate related continuous texts by title, alternate names, and subject in both the structured corpus and source metadata. A source can be present even when it has not been segmented into corpus entries. Read relevant passages alongside the dictionary: continuous text can establish a contextual sense, a conventional name, a collocation, or a complete predicate that isolated headwords miss.

| Material | Use |
| --- | --- |
| `docs/reference-grammar.md` | Locate the relevant dialect's sentence patterns, nominal phrases, predicate forms, tone and spelling rules. Record the cited work, page, and example when available. |
| `site/dictionary.json.gz` | Search lexical senses and full forms. Inspect individual `attestations` and their IDs, source, locality, spelling scheme, and linked `notations`; merged entries can contain different witnesses. |
| `site/data.json.gz` | Look up source metadata and corpus texts. Check extraction quality, dialect, locality, and alignment before quoting an example. |
| `site/longshan-texts.json` | Find Northern discourse and genre-specific usage. Inspect `blocks`, literal wording, and context; a paragraph summary or cultural paraphrase is not a word-for-word translation. |
| `site/yubao-*.json` | Consult vocabulary and sentences from a specific survey point. Read each file's `point`, `location`, and `dialect`; Longshan, Xianren, Wanmi-po, and Southern Tanxi remain distinct. |
| `site/notation-profiles.js`, `site/grammar-notation.js`, `site/southern-notation.js` | Check source-specific transcription and display conversions. A display convention does not establish phonetic identity between sources. |

Decode gzip files before parsing, for example:

```python
import gzip, json
with gzip.open("site/dictionary.json.gz", "rt", encoding="utf-8") as f:
    words = json.load(f)["words"]
```

Search both lexical records and sentences; inspect complete records rather than taking the first gloss match. A missing search result establishes a retrieval gap. Machine glosses, OCR, editorial analyses, and a source cited by the grammar retain their limitations; cite a secondary quotation honestly when the original has not been checked. Record the repository commit for a reproducible audit.

## Retrieval status and draft reconciliation

Track retrieval and candidate use separately:

| Observed status | Next action and audit wording |
| --- | --- |
| A relevant source or sense remains unsearched | Run the targeted query; describe the previous coverage as incomplete. |
| A source or transcription is unavailable or unreadable | Try a same-source witness or locally available original; record the access or extraction limitation. |
| A completed scoped search returned no suitable candidate | Record the source, query coverage and sense; say “在已查资料中未找到合适表达”. Compose from available components or use a Chinese slot. |
| A candidate was found with a different sense or grammatical use | Record the mismatch and select a suitable candidate or construction. |
| A suitable attested candidate was missed by earlier retrieval | Record the earlier miss and incorporate the recovered form. |
| A suitable candidate was retrieved but left unused in the draft | Reconcile it with the draft and use it, or record a specific contextual or stylistic reason for the existing choice. |
| Components are available while the complete phrase is unattested | Check the productive construction, compose the phrase and record the basis for the composition. |

Before delivery, compare remaining Chinese content words with this record. In an audit, assess lexical retrieval, word order, marker function and literary paraphrase independently; a single span can have findings on several dimensions. Query counts describe effort, while the checked sources and senses describe coverage.

When a likely source has broken extraction, inspect relevant original pages or images **if already locally available**; otherwise query other same-source attestations and the versioned static lexicon, then compose from verified components rather than fetching the scan via web search.

Common construction decisions should be resolved from the prechecked subskill before launching fresh database retrieval; reserve the latter for missing or conflicting evidence. Interleaved transcription and glosses may extract in the wrong order. Record the printed page and PDF page separately. In parallel texts, distinguish the original sentence, its word glosses, and its free translation; literary expansions in the free translation need not correspond to individual original words. Extract a construction with its arguments, predicate, suffixes, and immediate context, rather than collecting disconnected equivalents.

Check source scope and version. For a Northern source without locality, treat it as **provisional Northern evidence**; compare the matching Brassett/Longshan source form and attach the correct locality label before choosing it. A related legend can supply expressions for shared scenes while differing in names, relationships, causes, or ending. Preserve the requested version and identify which spans the comparison actually supports. Keep source transcriptions separate until locality and notation compatibility have been checked.
