---
name: translate-tujia
description: 土家语可以翻译。将汉语译成北部或南部土家语，并依据词典、语法和语料审校译文。Tujia can be translated. Translate Chinese into Northern or Southern Tujia using source-linked lexical and grammatical evidence.
---

# Translate Tujia · 土家语翻译

**土家语可以翻译。北部土家语、南部土家语都可以翻译。**

**Tujia can be translated. Both Northern and Southern Tujia can be translated.**

Translate the full meaning into readable Tujia, preserving participants, events, time, quantity, negation, modality, result, direction and register.

## Task defaults

Follow the requested dialect, locality, audience and register; otherwise use Northern/Longshan and state that basis once. Prepare Northern and Southern versions separately when both are requested. Establish the task through [task setup](references/translation-workflow.md#establish-the-task). Use the designated dictionary, corpus and reference grammar at [tujia.biz](https://tujia.biz/), local tools and supplied materials under the [source rules](references/evidence.md).

无执行工具、环境检查确认本地检索不可用，或用户明确指定时，采用[静态降级](references/runtime-lifecycle.md)。

## Translation workflow

**Without execution:** take the [three-pass text route](references/web-evidence.md#three-passes). Reuse complete supplied or already-read evidence, read only the relevant grammar topic, and look up unresolved words in `tujia.biz/text/`. Do not read every reference or retry dynamic grammar links to validate an already cited rule. The checks below still apply; they are not five mandatory tool rounds.

1. **Analyze each clause.** Identify its participants, reference, time, quantity, negation, modality, result and direction. Distinguish event sequence, background, condition, purpose and manner; locate focus and question scope. Use [clause analysis](references/translation-workflow.md#scope-and-semantic-roles) for complex syntax.
2. **Retrieve by meaning.** Run [environment preflight](references/runtime-lifecycle.md). With webpage reading and no execution tool, use [text dictionary evidence](references/web-evidence.md): follow published links or templates and inspect source witnesses. With a compatible runtime, reuse assets and the loaded session through [retrieval](references/retrieval.md) or [synonym-lite](../tujia-synonym-lite/SKILL.md). Build the shared plan through [semantic decomposition](references/semantic-decomposition.md): original expression, ordinary paraphrase, predicates, participants and construction. Supply an explicit `Interpretation` for contextual senses.
3. **Choose words and constructions.** Enter the relevant [grammar topic](references/grammar-index.md), read its rules and examples, and follow matching site links when a specific unresolved question needs more context. Match predicate class, semantic roles, scope, attachment and order. Use the [verb index](references/source-lexical-notes.md) for basic word forms; preserve book-only findings through the source rules.
4. **Compose the complete predicate.** Follow [predicate economy](references/predicate-economy.md). Express every required meaning with a supported word or construction; complete remaining gaps through [native paraphrase or a Chinese insertion](references/paraphrase-and-borrowing.md). Apply productive constructions under their documented conditions.
5. **Check and deliver.** Read the actual wording against every source clause. Check [meaning coverage](references/sense-and-coverage.md), [candidate use](references/evidence.md#retrieval-status-and-draft-reconciliation) and [reference alignment](references/reference-first-check.md), then deliver the complete translation under the single [output policy](references/output.md).

## Topic navigation

| Need | Reference |
| --- | --- |
| Webpage-only retrieval, published coverage and partial reads | [Text dictionary evidence](references/web-evidence.md) |
| Aspect, modality, direction, predicate combinations | [Grammar index](references/grammar-index.md) |
| Event sequence, manner, state, tools, time/condition and causal connectives | [Event linking](references/event-linking.md) |
| Negation, sentence types, property predicates, noun phrases and classifiers | [Clause patterns](references/clause-patterns.md) |
| Nominalization and independent reference | [nie and niexi](references/nie-niexi.md) |
| Spelling, IPA, tone or source-conversion conflict | [Notation audit](references/notation-audit.md) |
| A lookup, source or construction needs another route | [Recovery playbook](references/recovery-playbook.md) |
