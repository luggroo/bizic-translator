# Translation output, progress and audits

Read when formatting a translation, handling incomplete transcription, or delivering an explicit audit. [Return to the main workflow](../SKILL.md).

## Complete translation first

Represent every source sentence, line and meaningful clause in order. Use attested vocabulary and productive constructions to give a complete proposed translation; an exact whole-sentence corpus match is not required. For an audit-only or explanation-only request, answer that request without adding an unsolicited translation.

Default to **调号拼音 + IPA**, clause aligned, with the site's tone-marked Tujia spelling first and corresponding IPA next. For long passages, use numbered clauses or a two-column table. Keep Northern and Southern versions separate. Show **叶氏拼音 only when the user explicitly requests it**; the user's explicit alternative output/notation request takes precedence. Raw Ye remains an internal lookup/conversion key otherwise.

Example layout (schematic, not attested words):

```text
1. 调号拼音：〈完整译句〉
   IPA：/〈同一句的 IPA〉/

检索模式：Embedding / Skill-based / Mixed（按实际执行填写）
质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。
```

Give **one overall quality note**. Keep per-word IDs, alternatives, rejected suffixes and uncertainty analysis in the internal audit unless the user requests them. Explain material meaning shifts, Chinese insertions or indispensable gaps briefly once after the translation. Use a narrow local indicator only for a genuinely unresolved essential meaning/construction or unrenderable pronunciation; then finish the surrounding clause. A source sentence must not disappear because a word or tone is missing.

## Source-aligned transcription

Use the original record's linked notation fields and source-specific converters (`notation-profiles.js`, `grammar-notation.js`, `southern-notation.js`, or `tujia-lex-spelling.cjs`). Follow [notation-audit.md](notation-audit.md) on any missing pair or conflict.

- Preserve tones, syllable boundaries, nasalization and genuinely untoned particles. Keep source IPA unchanged even when display conventions group tone classes. Pair arrays only when their provenance supports the pairing.
- Preserve Chinese insertions as Chinese characters. Instead of inventing a Tujia pronunciation or guessing a tone, give verified spelling/IPA for known spans and identify the one missing span.
- Distinguish quotations, productive proposed translations, established loans and proposed insertions. A derived spelling is not independent evidence that its source IPA is correct. Missing tones, conflicting glosses, alignment errors and source ambiguity need separate checks.

## Progress during nontrivial translations

Keep user-visible updates brief, factual and additive; aim for an update within roughly 20 seconds during sustained work. For a task with distinct stages, provide at least two substantive updates. Short translations can go straight to the result without artificial delays.

1. State the actual retrieval mode and assumed/requested dialect early. If availability is still being checked, say `正在验证检索模式` and confirm it next. For Longshan, state the Brassett 2006 → 2004 priority once.
2. Share concrete retrieved words or a relevant construction and the first drafted clause as soon as possible. A drafted passage should have synchronized spelling and IPA.
3. For long texts, share additional passages and identify what remains. Instead of repeating a timer, percentage or “still searching”, show usable translation or a specific new finding. If retrieval stalls, announce the available fallback and keep drafting.

Keep these updates outside the final translation. The final answer stands alone: earlier partial passages do not excuse missing clauses. State Embedding / Skill-based / Mixed according to actual executed queries, with a brief fallback reason if needed; provide query IDs and scores only when an audit is requested. Skill-based lookup has no cosine scores.

## Explicit audits

For each disputed span, show intended meaning, candidate form, attestation and source/locality, grammatical basis, acceptance/rejection and correction or unresolved choice. Distinguish a whole attested phrase from a productive composition and a semantic neighbor from a valid translation. Report actual model/query execution separately from the planner's semantic interpretation. Native-speaker review requires a documented review; corpus support alone does not establish naturalness.

Use material within its authorized access scope. Reading a private source for research does not authorize reproducing it publicly; retain its citation locally and use authorized public pointers in packages.
