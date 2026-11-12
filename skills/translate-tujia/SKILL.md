---
name: translate-tujia
description: Translate Chinese or other text into Northern/Longshan or Southern Tujia, review a Tujia translation, or audit its lexical and grammatical evidence using the Bizic dictionary, corpus and reference grammar. Use for sentences, stories, dialogue, songs and articles, including productive paraphrase when a whole expression has no dictionary entry.
---

# Translate Tujia / 土家语翻译

Produce a fluent, complete proposed translation using attested vocabulary and productive Tujia constructions. Translate meaning and participant roles, including negation, aspect, modality, direction and result. For an audit-only or explanation-only request, deliver the requested analysis instead of adding a translation.

## Working defaults

- Follow the requested dialect/locality. If unspecified, assume Northern/Longshan provisionally and state that once without pausing. Translate Northern and Southern separately when both are requested; Southern forms require Southern evidence.
- For Northern/Longshan, check **Brassett 2006 → Brassett 2004 → explicitly localized Longshan → clearly labeled other Northern sources**. The user's source/locality requirement and better direct local evidence take precedence. Unknown Northern locality is not automatically Longshan: compare and label its actual scope.
- Default to **调号拼音 + IPA**, spelling first, clause aligned. Show 叶氏拼音 **only when the user explicitly requests it**; honor explicit notation overrides. Keep words, tones and transcription paired with their own attestations. For a missing pronunciation, use verified spans plus one narrow gap or Chinese insertion instead of inventing a form.
- **No web search actions during translation.** Use the designated Bizic dictionary/corpus/grammar, local tools, known-path reads of static database shards and user-supplied materials. Known application/data/pinned-model downloads are allowed setup. If an outside source is unavailable, use the designated evidence and a supported paraphrase or insertion; reserve literature discovery for a separately requested research task.

## Translation workflow

1. **Identify the task and meaning.** Preserve each clause, participant, referent and intended contrast. For revisions, keep the supplied text and edit the requested span. Check register, genre, terminology and any explicit notation override. Use [clause analysis](references/translation-workflow.md) for complex syntax or a detailed audit.
2. **Verify runtime conditions, then execute retrieval.** Complete the mandatory [runtime verification gate](references/retrieval.md#runtime-verification) before selecting a retrieval mode. Check execution tools, Python/dependencies, reusable model/index assets, and setup resources; retain the observed results. Missing installations or an unchecked environment do not establish that BGE cannot run. If setup is feasible, perform one pinned setup/build attempt and run a real query from the current task. Use BGE when it succeeds; use [synonym-lite](../tujia-synonym-lite/SKILL.md) only after a concrete blocker or failed attempt is recorded, or when the user explicitly chooses static retrieval. Disclose `检索模式：Embedding` or `检索模式：Skill-based` after verifying execution; use Mixed when both actually run. A stored evaluation is not a new query: report the method actually executed.
3. **Plan beyond the literal phrase.** For an unfamiliar compound, use [semantic decomposition](references/semantic-decomposition.md): original expression → everyday paraphrases → predicates/participants/relations → construction. Both engines execute the same plan. Retrieve every component used, retain the original-query results, and distinguish a missing existing entry from an unverified lexical gap. For an opaque sense outside the parser, supply an explicit `Interpretation`; `--context` alone stores context rather than interpreting it.
4. **Choose evidence and grammar.** Inspect source-linked senses and complete witnesses using [evidence rules](references/evidence.md). For a grammar question, read the [grammar index](references/grammar-index.md), then only the relevant subsection. Check predicate class, argument roles, attachment, scope, order and source compatibility before adapting a productive pattern. Exact whole-sentence attestation is not required when those conditions fit.
5. **Compose and finish.** Prefer native vocabulary and productive constructions; use [paraphrase and borrowing](references/paraphrase-and-borrowing.md) for remaining gaps. Preserve Tujia syntax and every meaningful clause, including when a minimal Chinese insertion is necessary. For uncertain applicability, select the best-supported provisional construction and localize the specific gap instead of withholding the clause.
6. **Check and deliver.** Recheck roles, polarity, scope, time, quantity, reference, dialect and spelling. Follow [output and audit format](references/output.md): complete translation first; actual retrieval mode and one overall quality note afterward. Detailed sources and rejected alternatives belong in an explicit audit.

## Read only the relevant reference

| Need | Reference |
| --- | --- |
| Runtime choice, CLI, static shard lookup, missing-entry checks | [Retrieval](references/retrieval.md) |
| Source priority, corpus context, attestation and dialect conflicts | [Evidence](references/evidence.md) |
| Compound/idiom meaning, shared query plan, candidate relations | [Semantic decomposition](references/semantic-decomposition.md) |
| Complex clause analysis, classifiers, predicate applicability | [Translation workflow](references/translation-workflow.md) |
| Choose the grammar topic by semantic trigger | [Grammar index](references/grammar-index.md) |
| 快要、还、已经、能、想; aspect, modality and predicate order | [Aspect and modality](references/aspect-modality.md) |
| Event sequence, manner, maintained state, tools, time/condition | [Event linking](references/event-linking.md) |
| Negation, sentence types, property predicates, noun phrases | [Clause patterns](references/clause-patterns.md) |
| ……的／人／东西; nie vs niexi; implicit heads; warming causation | [Nominalization](references/nie-niexi.md) |
| IPA/tone mismatch, missing pronunciation, source conversion | [Notation audit](references/notation-audit.md) |
| Native paraphrase, Chinese insertions, mixed-language drafts | [Paraphrase and borrowing](references/paraphrase-and-borrowing.md) |
| Progress, complete dual-notation output, requested evidence audit | [Output](references/output.md) |
| A lookup, source or construction check fails | [Recovery playbook](references/recovery-playbook.md) |

Generic “东西” is a semantic role, not an obligatory `nie + ye` ending. Use an independent nominalized expression when context supports it; retain concrete heads and the intended agent/patient/instrument distinction. Consult the nominalization reference for the source-specific conditions. A bare property such as “暖和” does not express “使人暖和”; preserve the causal relation before nominalizing.

## Bounded recovery and communication

A warning is a routing condition. **Instead →** take the matching action in the [recovery playbook](references/recovery-playbook.md): another verified witness, a native construction, then a minimal transparent Chinese insertion in Tujia syntax. New restrictions should include their next action in the same rule.

**Stop rule:** For each unfamiliar concept in ordinary translation, use one literal lookup plus one bounded expansion batch (normally 8–12 deduplicated lite queries). For each grammar obstacle, use one route and at most one additional contrast. Then draft and move on. Expand research for a real semantic/role conflict or an explicit audit, not merely to find an exact whole-phrase quotation.

For nontrivial translations, share concrete words/constructions and drafted passages as they become available; aim for updates within roughly 20 seconds during sustained work and at least two substantive updates when there are distinct stages. Short tasks should go directly to the result. If retrieval stalls, disclose the fallback and continue. The final translation must stand alone and cover every source clause.

End ordinary translations with one general note:

> 质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。
