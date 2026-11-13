# Semantic decomposition and constructional recomposition / 语义分解与构式重组

Use this shared query plan for BGE embedding search and `tujia-synonym-lite` static lookup. Execution, engine verification and query budgets belong to [retrieval](retrieval.md).

<a id="a-translate-the-underlying-situation-not-the-source-word-shape"></a>
## A. Identify the underlying situation

For an unfamiliar Chinese/English/Japanese expression, identify:
- What is being referred to: entity, person, action, instrument, substance, location, state, result, event, or judgment?
- Core predicates and their arguments: who acts, on what, where, for whom, with what instrument?
- What relations are essential (negation, possibility, modality, aspect, comparison, direction)?
- What information may safely be generalized, and what contrast must be preserved?

**Generate one compact, labeled query plan:** original expression and intended sense → everyday paraphrases → predicates, lexical heads and participants → relation words, sentence operators and required construction. Cover the source's question, assertion and focus relations as well as its content words. Search Chinese and English glosses with discriminative queries and retain the role each query serves. Check synonym candidates against their source-supported senses, argument frames and contextual range through [sense and coverage](sense-and-coverage.md); broader and narrower matches remain distinct from equivalents.

| Operation | Chinese input | Semantic bridge | Candidate construction / test |
| --- | --- | --- | --- |
| Event → agent/participant nominalization | 路人 | 在路上走的人 | `la hxi ma` (hypothesis: road + walk + person nominalizer) |
| Event → object or instrument | 玩具 | 玩的东西 | retrieve the attested noun first; compare [lexicalized ci and productive xi](nie-niexi.md) for a descriptive alternative |
| Event → theme/object | 饮料 | 喝的东西 | `hu-ci`, drink + object nominalizer |
| Hypernym + optional differentiating property | 香味 | 气味（好的／香的） | retrieve 气味 first; add positive scent if required |
| Predicate + negative ability | 令人费解 | 人不能懂／理解 | understand + inability / negative potential |
| Mental predicate + complement | 猜忌 | 嫉妒／怀疑／不相信（区分含义） | attested mental predicate + suitable complement |
| Idiom → realization and result | 追悔莫及 | 后悔＋伤心/心痛＋已经无法挽回 | realization + emotional/result clause; verify polarity and modality |
| Abstract noun → material stake + loss event | 经济损失 | 钱／财物损失；损失的钱 | retrieve money, lose, compensation separately; preserve loss event |
| Idiom → ordinary event | 画地为牢 | 自己把自己关住 | reflexive + shut in + resultant state |
| Unfamiliar person label → negative relative clause | 陌生人 | 不认识的人 | recognize + negation + patient-headed relative; the head is the person not recognized |
| Instrument noun → function | 开瓶器 | 打开瓶子的工具 | open + bottle + instrument/thing nominalization |
| Location relation → noun + spatial relation | 河岸 | 河的旁边 | river + side, using target-dialect phrase order |
| Property noun → property predicate | 寒意 | 冷的感觉／开始冷 | cold property, inchoative if needed |
| Temporal adverb → predicate morphology | 快要下雨 | 雨将下／正要下 | prospective/inchoative; see aspect-modality |
| Negative event → verb + scoped negation | 看不见 | 看＋不能 | distinguish inability from factual absence |

Use these templates as retrieval hypotheses, adapting the predicates, participants and construction to the intended situation. In particular, `-ma`, `-xi`, `-ci` have different argument/reference effects; validate them through [grammatical applicability](translation-workflow.md#validate-grammatical-applicability).

For explicit versus implicit heads, use [nie/niexi](nie-niexi.md). Retain specific noun meanings and preserve causal and result relations before nominalization. Check descriptive replacements through [noun descriptions](paraphrase-and-borrowing.md#noun-descriptions).

For literary imagery, include an expressive paraphrase in the semantic plan, retaining the central image, voice and emotional relation under [paraphrase choices](paraphrase-and-borrowing.md#express-the-intended-meaning).

## B. A single query plan for both engines

A suggested structured internal representation:

```json
{
  "source": "饮料",
  "meaning": "something meant to be drunk",
  "query_plan": [
    {"query": "饮料", "relation": "exact"},
    {"query": "喝的东西", "relation": "paraphrase"},
    {"query": "喝", "relation": "predicate"},
    {"query": "东西", "relation": "head"}
  ],
  "construction": {"family": "event_to_object_nominalization", "predicate": "喝", "nominalizer": "ci"}
}
```

Derive plans for new expressions from meaning and grammatical roles. Label query relations so exact matches, paraphrases, components and broader senses remain distinguishable. Execute the plan using the [retrieval routes](retrieval.md#executable-semantic-plan), then select witnesses through [sense and coverage](sense-and-coverage.md). Keep engine-specific result sets and scores distinguishable as described in [retrieval audits](retrieval.md#misses-scores-and-cost).

## C. Completion-first policy

Compose through [predicate economy](predicate-economy.md), resolving remaining gaps through [recovery](recovery-playbook.md). Delivery and localized uncertainty follow [output](output.md).

## D. Retrieval evaluation principle

For an explicit retrieval evaluation, compare routes against the same relevance targets. Assess source-supported lexical components, semantic-role coverage, constructional applicability and meaning fidelity separately. Scores rank retrieval candidates; attested forms and licensed constructions support translation choices.

## E. Executable shared plan

The planner's `plan(expression, context, dialect)` and structured `Interpretation`
interface represent predicates, arguments, relative heads, spatial relations and
scoped TAM. Supply an explicit `Interpretation` when the productive planner does not capture a contextual or opaque meaning; context text remains an audit record. Conventional opaque meanings use a small lexical bridge. Implementation
paths, CLI routes, context behavior and static lookup are documented in
[retrieval](retrieval.md#executable-semantic-plan).

The construction registry in `src/tujia_lex/constructions.py` cites a grammar
section for each family. Agent `ma`, object `ci`, broad `xi` and explicit
relative-head constructions have different roles. Dictionary and survey witnesses
have separate IDs and scope; static shards contain dictionary witnesses only.
