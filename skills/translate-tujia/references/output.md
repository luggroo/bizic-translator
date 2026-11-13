# Translation output, progress and audits

Use this page for the final format, transcription and progress updates. [Return to the main workflow](../SKILL.md).

## Deliver the requested result

For an audit-only or explanation-only task, present the requested analysis. For a translation, present every source sentence, line and meaningful clause in order. Put the complete translation first. Follow the user's requested format; otherwise use **调号拼音 + IPA**, clause aligned. Use numbering or a two-column table for longer passages and separate Northern and Southern versions. Show **叶氏拼音 only when the user explicitly requests it**.

```text
1. 调号拼音：〈完整译句〉
   IPA：/〈对应 IPA〉/

检索模式：Embedding / Skill-based / Mixed
```

In Chinese-language explanations, use the full name 汉语, including 汉语—土家语对照 labels. Preserve original quotations and bibliographic titles.

Report 检索模式：Embedding after current BGE inference, 检索模式：Skill-based after static lookup, or Mixed when both ran. Keep scores, rejected alternatives and verification logs for requested translation reviews or evidence audits.

For [webpage-only evidence](web-evidence.md), distinguish actual page reads from CLI checks or supplied excerpts: `检索模式：Skill-based（网页静态词典；本地未执行）`. If no retrieval succeeded, report `检索状态：未取得证据` with the access/coverage gap. Keep unsupported spans visible as `⟦汉语插入：…⟧` or `⟦待核：…⟧`; if the whole construction is unsupported, label the complete Chinese structural draft rather than implying a completed Tujia translation.

Explain a material paraphrase or Chinese insertion briefly when it helps the reader understand the translation. Write selected Chinese insertions directly in Chinese characters. For an unsupported lexical choice, use an attested synonym, productive native paraphrase or Chinese insertion. Present findings established by the materials and the work performed.

When the user requests a quality statement or a specific limitation affects use, give **one overall quality note** with the relevant facts. Ordinary translations follow the format above.

## Source-aligned transcription

Keep quotations in their source notation. Form new surface words from source-linked stems and licensed morphological rules, marking rule-derived forms separately from recorded quotations. Follow [notation audit](notation-audit.md).

- Preserve source tones, phonemes, syllable boundaries, nasalization and untoned particles. For future `i`, render the source-licensed surface form with an untoned **-i** boundary after its verb stem or DIR host, preserving the source's [fusion](aspect-modality.md#predicate-fusion), syllabification and tones. Original quotations retain their notation.
- Pair spelling and IPA through their attestation links. Use verified forms for the translated spans and Chinese characters for selected insertions.
- Keep original quotations, derived spellings, productive compositions and established loans identifiable in the evidence record.

## Progress updates

During sustained work, share a retrieved word or construction and a usable draft passage. State the target dialect and actual retrieval mode once they are established. Continue with new findings, decisions or passages as work progresses. Keep progress messages outside the final translation.

## Requested reviews and evidence audits

For each disputed span, show intended meaning, candidate form, source/locality, grammatical basis, decision and correction. Record actual model queries separately from semantic interpretation. Describe review, source freshness and test results from the work actually performed.

Organize requested findings on independent dimensions:

- **Lexical retrieval and use:** apply the [retrieval statuses](evidence.md#retrieval-status-and-draft-reconciliation), retaining each source's coverage and candidate decisions.
- **Word order and construction:** inspect participants, predicate class, attachment, conditions and clause linkage in the assembled sentence.
- **Morphology and particles:** identify function, scope, position and source-specific form; record tone and spelling differences separately.
- **Literary paraphrase:** apply the [image and voice criteria](paraphrase-and-borrowing.md#express-the-intended-meaning); a successful image can coexist with lexical or grammatical corrections.

Use material within its authorized scope. Keep private-source citations locally and use authorized public pointers in distributed packages.
