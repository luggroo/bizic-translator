---
name: translate-tujia
description: 支持北部、南部土家语与汉语、英语及其他模型能力支持的语言双向翻译，以及译文审校和逐词 gloss。依据词典、语法和语料核对词义、词界、记音差异与句法。Translate in both directions between Tujia and languages the model understands.
---

# Translate Tujia · 土家语翻译

支持北部、南部土家语与汉语、英语及其他模型能力支持的语言双向翻译。

Translate in either direction, preserving participants, events, time, quantity, negation, modality, result, direction and register.

## Task defaults

Follow the requested source and target languages, dialect, locality, audience and register. When translating into Tujia without a dialect preference, use Northern/Longshan and state that basis once. When reading Tujia, identify its variety from the text and source. Prepare Northern and Southern versions separately when both are requested. Establish the task through [task setup](references/translation-workflow.md#establish-the-task). Use the designated dictionary, corpus and reference grammar at [tujia.biz](https://tujia.biz/), local tools and supplied materials under the [source rules](references/evidence.md).

按 [output policy](references/output.md) 交付：原文在上、译文在下。土家语译文默认用调号拼音，**没有固定声调的词缀与格助词可不标调**；用户要 IPA 时只用 IPA。gloss（含 PDF）固定按“拼音 → IPA → gloss”三行逐词对齐；叶式拼音仅在用户要求时参照 Feng 的规则或对应例句处理。

**先交付完整可读的译文。** 译入土家语时，用适合语境的词汇和能产构式；缺词时按[改写与借用](references/paraphrase-and-borrowing.md#complete-before-qualifying)用土家语改写或最小汉语插入。**Skill 里的语法规则写用法和例句；例外给具体来源例句及适用条件。** 只说明影响理解的具体问题；确有必要时在末尾合并说明一次。

无执行工具、环境检查确认本地检索不可用，或用户明确指定时，采用[静态降级](references/runtime-lifecycle.md)。

**从土家语译出：** 先按[反向翻译](references/reverse-translation.md)恢复可能的词界；整词和分词候选并列检查。精确查询无合适结果时，依次比较 hx 声母有无、舌根音后 i/ei、高调/降调、已识别词缀的异调及指定双音节调型。保留原记音与检索变体，结合语法和上下文选义，再用目标语言组织译文。

## Translation workflow

Apply the steps below when translating **other languages → Tujia**. For **Tujia → other languages**, use [source-text analysis](references/reverse-translation.md) to identify words and constructions, then express their meaning in the requested target language. In either direction, preserve the original source text and check meaning coverage. Chinese and English glosses are retrieval aids; the source and target languages follow the user’s request.

**Without execution:** take the [three-pass text route](references/web-evidence.md#three-passes). Reuse complete supplied or already-read evidence, read only the relevant grammar topic, and look up unresolved words in `tujia.biz/text/`. Do not read every reference or retry dynamic grammar links to validate an already cited rule. The checks below still apply; they are not five mandatory tool rounds.

1. **Analyze each clause.** Identify its participants, reference, time, quantity, negation, modality, result and direction. Internally anchor each noun phrase's head and classify its modifiers before choosing property-word forms or positions: direct adjective, property predicate, linked/relative clause, or noun modifier. Record the expected target order through [head anchoring](references/translation-workflow.md#head-anchoring). Distinguish event sequence, background, condition, purpose and manner; locate focus and question scope. Use [clause analysis](references/translation-workflow.md#scope-and-semantic-roles) for complex syntax.
2. **Retrieve by meaning.** Run [environment preflight](references/runtime-lifecycle.md). With webpage reading and no execution tool, use [text dictionary evidence](references/web-evidence.md): follow published links or templates and inspect source witnesses. With a compatible runtime, reuse assets and the loaded session through [retrieval](references/retrieval.md) or [synonym-lite](../tujia-synonym-lite/SKILL.md). Build the shared plan through [semantic decomposition](references/semantic-decomposition.md): original expression, ordinary paraphrase, predicates, participants and construction. Supply an explicit `Interpretation` for contextual senses.
3. **Choose words and constructions.** Enter the relevant [grammar topic](references/grammar-index.md), read its rules and examples, and follow matching site links when a specific unresolved question needs more context. Match predicate class, semantic roles, scope, attachment and order. For commands, prohibitions and exhortations, follow [directive selection](references/directives.md#choose) before adding predicate particles. Use the [verb index](references/source-lexical-notes.md) for basic word forms; preserve book-only findings through the source rules.
4. **Compose the complete predicate.** Follow [predicate economy](references/predicate-economy.md). Express every required meaning with a supported word or construction; complete remaining gaps through [native paraphrase or a Chinese insertion](references/paraphrase-and-borrowing.md). Apply productive constructions under their documented conditions.
5. **Check and deliver.** Verify [meaning coverage](references/sense-and-coverage.md), [candidate use](references/evidence.md#retrieval-status-and-draft-reconciliation), [reference alignment](references/reference-first-check.md) and modifier linkage. Apply [output policy](references/output.md): complete translation first, specific notes only when needed, and one optional gloss/PDF follow-up when the preference is unknown.

## Topic navigation

| Need | Reference |
| --- | --- |
| 土家语译其他语言、连写分词、异记音查询 | [反向翻译与记音容差](references/reverse-translation.md) |
| Webpage-only retrieval, published coverage and partial reads | [Text dictionary evidence](references/web-evidence.md) |
| Aspect, modality, direction, predicate combinations | [Grammar index](references/grammar-index.md) |
| Commands, requests, prohibitions, exhortations, bare imperatives | [Directive constructions](references/directives.md#choose) |
| Event sequence, manner, state, tools, time/condition and causal connectives | [Event linking](references/event-linking.md) |
| Negation, sentence types, property predicates, noun phrases and classifiers | [Clause patterns](references/clause-patterns.md) |
| Nominalization and independent reference | [nie and niexi](references/nie-niexi.md) |
| Spelling, IPA, tone or source-conversion conflict | [Notation audit](references/notation-audit.md) |
| A lookup, source or construction needs another route | [Recovery playbook](references/recovery-playbook.md) |
