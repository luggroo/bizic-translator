---
name: translate-tujia
description: Translate Chinese or other text into Northern/Longshan or Southern Tujia, review a Tujia translation, or audit its lexical and grammatical evidence using the Bizic dictionary, corpus and reference grammar. Use for sentences, stories, dialogue, songs and articles, including productive paraphrase when a whole expression has no dictionary entry.
---

# Translate Tujia / 土家语翻译

Produce a fluent, complete proposed translation using attested vocabulary and productive Tujia constructions. Translate meaning and participant roles, including negation, aspect, modality, direction and result. For poetry and songs, use expressive paraphrase to carry the imagery, emotional force and voice. For an audit-only or explanation-only request, deliver the requested analysis.

## Minimum deliverable: a complete version

Deliver every requested sentence, line and meaningful clause. Use supported Tujia vocabulary and productive constructions first; after bounded retrieval, fill remaining lexical slots with Chinese words in the best-supported target-dialect arrangement and deliver the complete draft directly. **A complete version may retain Chinese content words in provisional Tujia syntax.** Write those words as plain Chinese characters; their script supplies the visual distinction. Add borrowing labels when the user requests them.

For an uncertain construction, provide the best-supported proposed rendering and place any essential explanation in a concise note. Keep pronunciation and tones tied to their source witnesses, and retain Chinese characters where pronunciation remains unavailable. Apply the [output format](references/output.md) to the completed text.

## Working defaults

- In Chinese-language explanations, use the full language name `汉语`, including `汉语—土家语对照` when relevant. Preserve original source quotations and bibliographic titles.
- Follow the requested dialect/locality. If unspecified, assume Northern/Longshan provisionally, state that once and proceed. Translate Northern and Southern separately when both are requested; use Southern evidence for Southern forms.
- For Northern/Longshan, check **Brassett 2006 → Brassett 2004 → explicitly localized Longshan → clearly labeled other Northern sources**. A requested locality sets the comparison target; an explicit source request sets the source priority. Inspect individual attestations and compare any stronger local evidence with the Brassett candidates before selecting a form. Follow the [source-selection steps](references/evidence.md).
- Default to **调号拼音 + IPA**, spelling first, clause aligned. Show 叶氏拼音 **only when the user explicitly requests it**; honor explicit notation overrides. Keep words, tones and transcription paired with their own attestations. Supply verified spelling and IPA for supported spans, and retain Chinese characters for a lexical slot whose pronunciation remains unavailable.
- Use the designated Bizic dictionary/corpus/grammar, local tools, known-path reads of static database shards and user-supplied materials for translation. Known application/data/pinned-model downloads support setup. Reserve web search and literature discovery for a separately requested research task; complete ordinary translations with available evidence, productive paraphrase and Chinese insertions.

## Translation workflow

1. **Identify the task and meaning.** Preserve each clause, participant, referent and intended contrast. For revisions, keep the supplied text and edit the requested span. Check register, genre, terminology and any explicit notation override. Use [clause analysis](references/translation-workflow.md) for complex syntax or a detailed audit.
2. **Assess the environment, then execute retrieval.** Run the cheap [environment preflight](references/runtime-lifecycle.md) before setup: inspect execution, existing assets, resources and persistence. Reuse compatible BGE assets first, even offline. Provision missing assets only when capabilities and durable storage are established; otherwise go directly to [synonym-lite](../tujia-synonym-lite/SKILL.md) and seek a durable destination for future use. Follow [retrieval commands](references/retrieval.md), keep a reusable asset registry, and use temporary storage only for scratch/tests. Disclose `检索模式：Embedding` or `检索模式：Skill-based` after actual queries; use Mixed when both run. A stored evaluation is not a new query.
3. **Plan beyond the literal phrase.** For an unfamiliar compound, use [semantic decomposition](references/semantic-decomposition.md): original expression → everyday paraphrases → predicates/participants/relations → construction. Search Chinese and English senses, components, examples and relevant continuous texts. Both engines execute the same plan. Retrieve every component used and retain the original-query results. For an opaque sense outside the parser, supply an explicit `Interpretation`; `--context` retains the context for inspection.
4. **Choose evidence and grammar.** Inspect source-linked senses and complete witnesses using [evidence rules](references/evidence.md). For Northern/Longshan, record the Brassett 2006 and 2004 coverage and each chosen candidate's attestation. For a grammar question, read the [grammar index](references/grammar-index.md), then the relevant subsection. Check predicate class, argument roles, attachment, scope, order and source compatibility; use a productive pattern when those conditions fit.
5. **Compose and finish.** Prefer native vocabulary and productive constructions; use [paraphrase and borrowing](references/paraphrase-and-borrowing.md) for remaining gaps. Preserve Tujia syntax and every meaningful clause, including when a minimal Chinese insertion is necessary. For uncertain applicability, complete the best-supported provisional construction and explain any essential uncertainty in a concise note.
6. **Check and deliver.** Match remaining Chinese content words against the retrieved candidates and use suitable Tujia expressions. Recheck the assembled clauses for roles, word order, marker function and scope, reference, dialect and spelling. Assess literary paraphrase by the intended imagery and emotional relation. Follow [output and audit format](references/output.md): complete translation first; actual retrieval mode and one overall quality note afterward. Detailed sources and candidate decisions belong in an explicit audit.

## Read only the relevant reference

| Need | Reference |
| --- | --- |
| Judge execution capability, find reusable assets, arrange durable storage | [Runtime lifecycle](references/runtime-lifecycle.md) |
| Runtime choice, CLI, static shard lookup, missing-entry checks | [Retrieval](references/retrieval.md) |
| Source priority, corpus context, attestation and dialect conflicts | [Evidence](references/evidence.md) |
| Compound/idiom meaning, shared query plan, candidate relations | [Semantic decomposition](references/semantic-decomposition.md) |
| Complex clause analysis, classifiers, predicate applicability | [Translation workflow](references/translation-workflow.md) |
| Choose the grammar topic by semantic trigger | [Grammar index](references/grammar-index.md) |
| 快要、还、已经、能、想; aspect, modality and predicate order | [Aspect and modality](references/aspect-modality.md) |
| Event sequence, manner, state, tools, time/condition; 所以、然后、不然 | [Event linking](references/event-linking.md) |
| Negation, sentence types, property predicates, noun phrases | [Clause patterns](references/clause-patterns.md) |
| ……的／人／东西; nie vs niexi; implicit heads; warming causation | [Nominalization](references/nie-niexi.md) |
| IPA/tone mismatch, missing pronunciation, source conversion | [Notation audit](references/notation-audit.md) |
| Native paraphrase, Chinese insertions, mixed-language drafts | [Paraphrase and borrowing](references/paraphrase-and-borrowing.md) |
| Progress, complete dual-notation output, requested evidence audit | [Output](references/output.md) |
| A lookup, source or construction check fails | [Recovery playbook](references/recovery-playbook.md) |

For generic “东西”, choose an independent nominalized expression or an explicit head according to the context and the source-specific conditions in the nominalization reference. Retain concrete heads and the intended agent/patient/instrument distinction. For “使人暖和”, express the causal relation before nominalizing.

## Bounded recovery and communication

Use the [recovery playbook](references/recovery-playbook.md) to choose the next useful action: inspect another witness, adapt a native construction, or fill a lexical slot with Chinese and complete the clause.

**Retrieval budget:** For each unfamiliar concept in ordinary translation, use one literal lookup plus one bounded expansion batch (normally 8–12 deduplicated lite queries). Within that budget, cover the relevant bilingual senses, components and contexts, then draft from the best-supported candidates. Record which sources and senses were actually checked. For each grammar question, use one route and one additional contrast when useful. Expand research for a substantive unresolved choice or an explicit audit.

For nontrivial translations, share concrete words/constructions and drafted passages as they become available; aim for updates within roughly 20 seconds during sustained work and at least two substantive updates when there are distinct stages. Short tasks should go directly to the result. If retrieval stalls, disclose the fallback and continue. The final translation must stand alone and cover every source clause.

End ordinary translations with one general note:

> 质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。

## Maintaining this skill

Write operational guidance as **situation → action → usable result**. Keep each detailed rule in its relevant reference and link to it from the main workflow. When updating the skill, validate the references and package, and report local changes, package creation and active-version verification as separate observed states.
