# Sources, dialect and attestation evidence

Read when choosing a source, resolving conflicting witnesses, or investigating a lexical/corpus gap. [Return to the translation workflow](../SKILL.md). Retrieval commands are in [retrieval.md](retrieval.md).

Use the designated dictionary, corpus and reference grammar at [tujia.biz](https://tujia.biz/), the committed local materials, and the Tujia retrieval database. Enter through the relevant grammar topic, which groups the working rules, examples and matching site links; reuse retrieved records. Retain the provenance of user-supplied materials.

## Topic-based grammar lookup

Use the [grammar index](grammar-index.md) to select the construction's topic. Read its working rules and examples, then follow the site links at the relevant subsection for the matching discussion and context. Keep links beside the rule or choice they support. Text-only access to a linked section follows the [page-reading procedure](retrieval.md#read-grammar-section).

<a id="book-only-findings"></a>
### Preserve book-only findings

Choose a destination by the content's purpose:

- **Reference-grammar addition proposal:** use for language facts useful across tasks, such as a paradigm, construction, ordering rule or combination restriction. Identify the target grammar section and supply the proposed text.
- **Skill reference:** use for translation decisions, working tables and construction choices needed during execution. Add the entry to the relevant topic, alongside its examples and matching site links, and link that topic from the grammar index.

Keep lexical entries in the dictionary. The basic-verb index collects common forms attested in multiple independent contexts and points to their records; complete construction and fusion examples belong to the corresponding grammar topic.

Include the usable forms, meaning, predicate or phrase class, scope, attachment and order, relevant combination conditions, and a complete example. Preserve the source notation, provide the paired display notation through its converter, and cite the work, locality, page, table or example number. Record whether the passage was read directly or quoted through the reference grammar. Capture the general rule and its application conditions so future translations can use the entry directly.

<a id="source-selection"></a>
## Source selection for Northern / Longshan

1. **Retrieve Brassett 2006, then 2004.** Search the intended sense, related Chinese and English senses, collocations and example constructions in each source. Record useful candidates and the actual coverage of each search. Apply this order to songs and short phrases as well as prose. An explicit user source request sets a different priority; a locality request such as Longshan sets the target variety for this comparison.
2. **Resolve individual witnesses.** Inspect each candidate's `attestations`, original gloss, full form, linked notations, locality and source citation. For canonical data, resolve the witness source through `site/data.json.gz` and `sourceAliases`; for static shards, resolve `manifest.sources[r[2]].canonical_id`. Treat a merged entry's top-level source as entry metadata and inspect all relevant witnesses within it.
3. **Compare supplementary evidence.** After recording the Brassett findings, consult explicitly localized Longshan materials, continuous texts and other Northern surveys for remaining gaps or conflicting local usage. When a local witness fits better, record its concrete advantage in meaning, construction or locality and the corresponding Brassett comparison. Describe an unlocalized Northern witness at its recorded scope. If a Brassett source is inaccessible, retain that availability status and continue with the available evidence.
4. **Select a complete form or construction.** Prefer the supported 2006 analysis when the original witnesses justify it; retain source-specific differences when 2004 or localized evidence supplies a different form. Confirm syllable boundaries and lexical meaning from the full attestation. Use a verified paraphrase or plain Chinese insertion for an unresolved lexical slot, and finish the proposed clause with a concise note about essential construction uncertainty.

Keep a compact internal record per intended sense: **2006 evidence or search status; 2004 evidence or search status; supplementary evidence; selected attestation; reason for selection**. Reuse records for repeated senses and show this detail in requested audits.

In the standalone `bizic-translator` project, the paths below are relative to the public-data checkout supplied as `--repo` (normally `.cache/bizic-data`), rather than the application directory. Follow the README to fetch that fixed source snapshot.

For a story, craft, custom, or other identifiable topic, first locate related continuous texts by title, alternate names, and subject in both the structured corpus and source metadata. Inspect source metadata as well as segmented corpus entries. Read relevant passages alongside the dictionary: continuous text can establish a contextual sense, a conventional name, a collocation, or a complete predicate that isolated headwords miss.

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

Search lexical records and sentences. Read complete relevant records and source sections in bounded excerpts, continuing a truncated passage before judging its construction. A missing search result establishes a retrieval gap. Identify machine glosses, OCR, editorial analyses and secondary quotations by their actual provenance. Record the repository commit for a reproducible audit.

Assess semantic fit, construction support and pronunciation as separate evidence fields. Select the expression that preserves the meaning and participant relations, then resolve its source-specific pronunciation.

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

When a likely source has broken extraction, inspect the corresponding tujia.biz record, same-source attestations and relevant original pages or images. Preserve newly recovered book-only material through the procedure above, then compose from the verified components.

Resolve common construction decisions from the relevant skill topic or tujia.biz section and reuse the result. Retrieve additional examples for a missing construction or a concrete source conflict. Interleaved transcription and glosses may extract in the wrong order. Record the printed page and PDF page separately. In parallel texts, distinguish the original sentence, its word glosses, and its free translation; literary expansions in the free translation need not correspond to individual original words. Extract a construction with its arguments, predicate, suffixes, and immediate context, rather than collecting disconnected equivalents.

Check source scope and version. For a Northern source without locality, treat it as **provisional Northern evidence**; compare the matching Brassett/Longshan source form and attach the correct locality label before choosing it. A related legend can supply expressions for shared scenes while differing in names, relationships, causes, or ending. Preserve the requested version and identify which spans the comparison actually supports. Select compatible source transcriptions after checking locality and notation.

Use restricted materials within their authorized task scope and retain their citation or attestation ID. Public packages contain scripts and pointers to authorized public sources; reproducing restricted material requires explicit authorization.
