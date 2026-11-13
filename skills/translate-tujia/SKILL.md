---
name: translate-tujia
description: Translate into Northern or Southern Tujia and review translations using source-linked dictionary, corpus and grammar evidence, including productive paraphrase for expressions without a whole dictionary entry.
---

# Translate Tujia

Translate the full meaning into readable Tujia, preserving participants, events, time, quantity, negation, modality, result, direction and register.

## Task defaults

Follow the requested dialect, locality, audience and register; otherwise use Northern/Longshan and state that basis once. Prepare Northern and Southern versions separately when both are requested. Establish the task through [task setup](references/translation-workflow.md#establish-the-task). Use the designated dictionary, corpus and reference grammar at [tujia.biz](https://tujia.biz/), local tools and supplied materials under the [source rules](references/evidence.md).

## Translation workflow

1. **Analyze each clause.** Identify its participants, reference, time, quantity, negation, modality, result and direction. Distinguish event sequence, background, condition, purpose and manner; locate focus and question scope. Use [clause analysis](references/translation-workflow.md#scope-and-semantic-roles) for complex syntax.
2. **Retrieve by meaning.** Run [environment preflight](references/runtime-lifecycle.md), reuse compatible assets and the loaded session, then execute [retrieval](references/retrieval.md) or [synonym-lite](../tujia-synonym-lite/SKILL.md). Build the shared plan through [semantic decomposition](references/semantic-decomposition.md): original expression, ordinary paraphrase, predicates, participants and construction. Supply an explicit `Interpretation` for contextual senses.
3. **Choose words and constructions.** Enter the relevant [grammar topic](references/grammar-index.md), read its rules and examples, and follow its matching site links. Match predicate class, semantic roles, scope, attachment and order. Use the [verb index](references/source-lexical-notes.md) for basic word forms; preserve book-only findings through the source rules.
4. **Compose the complete predicate.** Follow [predicate economy](references/predicate-economy.md). Express every required meaning with a supported word or construction; complete remaining gaps through [native paraphrase or a Chinese insertion](references/paraphrase-and-borrowing.md). Apply productive constructions under their documented conditions.
5. **Check and deliver.** Read the actual wording against every source clause. Check [meaning coverage](references/sense-and-coverage.md), [candidate use](references/evidence.md#retrieval-status-and-draft-reconciliation) and [reference alignment](references/reference-first-check.md), then deliver the complete translation under the single [output policy](references/output.md).

## Topic navigation

| Need | Reference |
| --- | --- |
| Aspect, modality, direction, predicate combinations | [Grammar index](references/grammar-index.md) |
| Event sequence, manner, state, tools, time/condition and causal connectives | [Event linking](references/event-linking.md) |
| Negation, sentence types, property predicates, noun phrases and classifiers | [Clause patterns](references/clause-patterns.md) |
| Nominalization and independent reference | [nie and niexi](references/nie-niexi.md) |
| Spelling, IPA, tone or source-conversion conflict | [Notation audit](references/notation-audit.md) |
| A lookup, source or construction needs another route | [Recovery playbook](references/recovery-playbook.md) |
