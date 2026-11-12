# Sources, dialect and attestation evidence

Read when choosing a source, resolving conflicting witnesses, or investigating a lexical/corpus gap. [Return to the translation workflow](../SKILL.md). Retrieval commands are in [retrieval.md](retrieval.md).

Start with the committed, locally available repository materials and the designated Tujia retrieval database. User-supplied materials may also be used with their provenance and access restrictions. For any missing external source, use Bizic's designated dictionary/corpus/grammar, static shards, or user-provided authorized materials; continue with an attested native paraphrase or localized insertion rather than searching external sites during translation.

### Default source priority for Northern / Longshan (mandatory)

- **Check Brassett first for every Northern/Longshan translation**, including songs and short phrases. Consult Brassett et al. (2006) as the primary lexical and grammatical reference and Brassett (2004) as a supplementary witness **before** selecting forms from YuBao survey points, other Northern collections, or machine-generated glosses. This is the default, not an optional source preference. Explicit user source requirements and reliable evidence specific to the requested locality take precedence; do not silently mix different varieties.
- Search both Brassett sources for the actual intended sense, related senses, collocations, and example constructions, not merely a Chinese headword. Inspect attestation-linked spellings, original glosses, source citations, tone, and grammatical behavior. A high-ranked semantic match from another source must not displace an appropriate Brassett form without a concrete reason. If 2004 and 2006 differ, compare the original witnesses; favor the better-supported, more mature 2006 analysis rather than mechanically adopting an older transcription.
- Expand to explicitly localized Longshan evidence, continuous texts, and other Northern surveys **only after** Brassett has been checked or when they supply a better-documented local form or construction. Record which spans are Brassett-based and which come from another source; explain meaningful conflicts, gaps, and dialect differences. "Northern" without an attested locality is not automatically "Longshan".
- **Never manufacture a word from the apparent tail of a sentence or its gloss alignment.** An isolated symbol or segment such as /ɸ⁵⁵/ is not independently verified as a lexical syllable or a component of "love"; confirm the full source transcription, segment boundaries, and lexical meaning before reuse. If attestation, tone, or alignment remains doubtful, use a verified paraphrase or a clearly identified Chinese insertion; if even the structure is uncertain, provide a marked provisional rendering and localize the uncertainty in a note. Never leave the corresponding source clause without a proposed translation. Rhythmic constraints do not override this check.

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

When a likely source has broken extraction, inspect relevant original pages or images **if already locally available**; otherwise query other same-source attestations and the versioned static lexicon, then compose from verified components rather than fetching the scan via web search.

Common construction decisions should be resolved from the prechecked subskill before launching fresh database retrieval; reserve the latter for missing or conflicting evidence. Interleaved transcription and glosses may extract in the wrong order. Record the printed page and PDF page separately. In parallel texts, distinguish the original sentence, its word glosses, and its free translation; literary expansions in the free translation need not correspond to individual original words. Extract a construction with its arguments, predicate, suffixes, and immediate context, rather than collecting disconnected equivalents.

Check source scope and version. For a Northern source without locality, treat it as **provisional Northern evidence**; compare the matching Brassett/Longshan source form and attach the correct locality label before choosing it. A related legend can supply expressions for shared scenes while differing in names, relationships, causes, or ending. Preserve the requested version and identify which spans the comparison actually supports. Keep source transcriptions separate until locality and notation compatibility have been checked.
