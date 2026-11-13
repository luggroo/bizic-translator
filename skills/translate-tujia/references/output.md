# Translation output, progress and audits

Read when formatting a translation, handling incomplete transcription, or delivering an explicit audit. [Return to the main workflow](../SKILL.md).

## Complete translation first

Apply the [complete-version requirement](../SKILL.md#minimum-deliverable-a-complete-version): represent every source sentence, line and meaningful clause in order, using supported vocabulary, productive constructions and plain Chinese insertions for remaining lexical slots. Their script supplies the visual distinction; provide additional borrowing labels on request. For an audit-only or explanation-only request, present the requested analysis.

Default to **调号拼音 + IPA**, clause aligned, with the site's tone-marked Tujia spelling first and corresponding IPA next. For long passages, use numbered clauses or a two-column table. Keep Northern and Southern versions separate. Show **叶氏拼音 only when the user explicitly requests it**; the user's explicit alternative output/notation request takes precedence. Raw Ye remains an internal lookup/conversion key otherwise.

Example layout (schematic, not attested words):

```text
1. 调号拼音：〈完整译句〉
   IPA：/〈同一句的 IPA〉/

检索模式：Embedding / Skill-based / Mixed（按实际执行填写）
质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。
```

Give **one overall quality note**. Keep per-word IDs, alternatives, candidate decisions and uncertainty analysis in the internal audit, and show them when requested. Place any essential construction uncertainty or reader-relevant meaning change in a concise note after the completed translation. Evaluate literary paraphrase by its imagery, emotional force and the task's style; explain meaningful expressive choices in an explicit audit.

## Source-aligned transcription

Use the original record's linked notation fields and source-specific converters (`notation-profiles.js`, `grammar-notation.js`, `southern-notation.js`, or `tujia-lex-spelling.cjs`). Follow [notation-audit.md](notation-audit.md) on any missing pair or conflict.

- Preserve tones, syllable boundaries, nasalization and genuinely untoned particles. Keep source IPA unchanged even when display conventions group tone classes. Pair arrays only when their provenance supports the pairing.
- Preserve Chinese insertions as Chinese characters in both displays. Supply verified spelling/IPA for the Tujia spans and place any essential pronunciation uncertainty in the concise note.
- Record the evidence basis of quotations, productive proposed translations, established loans and proposed insertions. Verify the source IPA before applying its display conversion. Check missing tones, conflicting glosses, alignment and source scope separately.

## Progress during nontrivial translations

Keep user-visible updates brief, factual and additive; aim for an update within roughly 20 seconds during sustained work. For a task with distinct stages, provide at least two substantive updates. Short translations can go straight to the result without artificial delays.

1. State the actual retrieval mode and assumed/requested dialect early. If availability is still being checked, say `正在验证检索模式` and confirm it next. For Longshan, state the Brassett 2006 → 2004 priority once.
2. Share concrete retrieved words or a relevant construction and the first drafted clause as soon as possible. A drafted passage should have synchronized spelling and IPA.
3. For long texts, share additional passages and identify what remains. Instead of repeating a timer, percentage or “still searching”, show usable translation or a specific new finding. If retrieval stalls, announce the available fallback and keep drafting.

Keep these updates outside the final translation. Include every requested clause in the self-contained final answer. State Embedding / Skill-based / Mixed according to actual executed queries, with a brief fallback reason if needed. In a requested audit, provide query IDs and any actual embedding scores; describe Skill-based results through their exact matches and source witnesses.

## Explicit audits

For each disputed span, show intended meaning, candidate form, attestation and source/locality, grammatical basis, selection decision and correction or unresolved choice. Distinguish a whole attested phrase from a productive composition and identify each candidate's semantic relation. Report actual model/query execution separately from the planner's semantic interpretation. Attribute native-speaker review to its documented reviewer or record.

Organize findings on independent dimensions:

- **Lexical retrieval and use:** apply the [retrieval statuses](evidence.md#retrieval-status-and-draft-reconciliation), with Brassett 2006 and 2004 coverage before supplementary sources.
- **Word order and construction:** inspect participants, predicate class, modifier attachment, condition and clause linkage in the assembled sentence.
- **Morphology and particles:** identify the actual function—such as aspect, direction, negation, modality, nominalization or discourse mood—and compare its scope, position and source-specific form. Record tone or spelling differences separately.
- **Literary paraphrase:** describe how the wording carries the image, emphasis and emotional relation, and evaluate the task's intended degree of freedom. A successful paraphrase can coexist with a lexical or grammatical correction.

Use material within its authorized access scope. Reading a private source for research does not authorize reproducing it publicly; retain its citation locally and use authorized public pointers in packages.
