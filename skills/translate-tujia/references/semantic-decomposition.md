# Semantic decomposition and constructional recomposition / 语义分解与构式重组

**Shared by BOTH routes:** real BGE embedding search and `tujia-synonym-lite` static lookup. The difference is the retrieval engine; the **query-planning strategy is identical**.

## A. Translate the underlying situation, not the source word shape

For an unfamiliar Chinese/English/Japanese expression, identify:
- What is being referred to: entity, person, action, instrument, substance, location, state, result, event, or judgment?
- Core predicates and their arguments: who acts, on what, where, for whom, with what instrument?
- What relations are essential (negation, possibility, modality, aspect, comparison, direction)?
- What information may safely be generalized, and what contrast must be preserved?

**Generate a compact, labeled query plan** before searching an unfamiliar compound: original expression → everyday paraphrase(s) → component predicates / heads / participants → required construction. Prefer a few discriminative queries. Source-word components are not themselves the translation.

| Operation | Chinese input | Semantic bridge | Candidate construction / test |
| --- | --- | --- | --- |
| Event → agent/participant nominalization | 路人 | 在路上走的人 | `la hxi ma` (user's proposed analysis: road + walk + person nominalizer) |
| Event → object or associated thing | 玩具 | 玩的东西 | `geci-xi`, play + broad nominalizer |
| Event → theme/object | 饮料 | 喝的东西 | `hu-ci`, drink + object nominalizer |
| Hypernym + optional differentiating property | 香味 | 气味（好的／香的） | retrieve 气味 first; add positive scent if required |
| Predicate + negative ability | 令人费解 | 人不能懂／理解 | understand + inability / negative potential |
| Abstract noun → material stake + loss event | 经济损失 | 钱／财物损失；损失的钱 | retrieve money, lose, compensation separately; preserve loss event |
| Idiom → ordinary event | 画地为牢 | 自己把自己关住 | reflexive + shut in + resultant state |
| Unfamiliar person label → negative relative clause | 陌生人 | 不认识的人 | know/recognize + negation + agent nominalization |
| Instrument noun → function | 开瓶器 | 打开瓶子的工具 | open + bottle + instrument/thing nominalization |
| Location relation → noun + spatial relation | 河岸 | 河的旁边 | river + side, using target-dialect phrase order |
| Property noun → property predicate | 寒意 | 冷的感觉／开始冷 | cold property, inchoative if needed |
| Temporal adverb → predicate morphology | 快要下雨 | 雨将下／正要下 | prospective/inchoative; see aspect-modality |
| Negative event → verb + scoped negation | 看不见 | 看＋不能 | distinguish inability from factual absence |

These are **candidate construction templates**, not memorized final translations. In particular, `-ma`, `-xi`, `-ci` have different argument/reference effects; consult the grammar once for the applicable construction, then use it productively. Do not turn such a distinction into repetitive user-facing disclaimers.

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

For **Embedding**: first run the raw original query. If no directly useful complete candidate appears, run the **same plan** through actual BGE query encoding and similarity search; retain raw results as baseline and display actual cosine scores only in test/debug mode. Combine **candidate sets**, not scores from unrelated search pipelines. For **Skill-based**: run the same labeled queries through FNV-sharded exact dictionary lookup and keep attestation IDs. Both modes inspect evidence and compose via the same grammar reference router. Do not hard-code all query plans: seed cases are examples; handle unseen compounds by deriving meaning and grammatical roles.

## C. Completion-first policy

In ordinary translation, output a fluent, complete **best-supported proposed translation** rather than a refusal or lengthy methodological preface. Trust an attested productive construction when its roles and meaning match. Prefer a native compositional paraphrase over leaving an abstract Chinese compound untranslated.

**One brief quality notice per finished translation is enough**, e.g. `质量说明：以下为基于现有词典及语法材料的拟译，尚未经母语者审校。` Do not repeat caveats after every word, suffix or line. Still preserve genuine source attribution and keep all scores/results inspectable in explicit audit or QA mode. Never invent pronunciations or claim a model/query ran when it did not.

## D. Retrieval evaluation principle

Compare raw-query embedding, decomposed-query embedding, the static skill route, and a combined route on the **same gold relevance targets**. Evaluate (1) source-supported lexical-component recall, (2) whether all required semantic roles are covered, (3) whether the chosen Tujia construction is licensed, and (4) meaning fidelity. A high cosine score, a vague thematic word, and a proposed but unverified assembled phrase are not interchangeable evidence.

## E. Executable shared plan

`src/tujia_lex/query_plan.py` supplies `plan(expression, context, dialect)` and a
structured `Interpretation` interface. Productive frames decompose new predicates
and arguments, relative heads, spatial relations and scoped TAM. Conventional
opaque meanings use a small lexical bridge. A translating agent can supply a new
interpretation without changing the planner or `concepts.json`; context text is
retained for inspection, not presented as automatically understood.

`tujia-lex plan EXPRESSION --route C --index INDEX --model-path MODEL` executes
that plan with real BGE. Route D uses the same queries with exact static shards;
route E combines them and checks components and source compatibility. The
lightweight script shares the planner. Curated concepts remain explanatory seeds,
not an exhaustive synonym dictionary. Raw `search` is available for baselines and
basic-word evidence checks.

The construction registry in `src/tujia_lex/constructions.py` cites a grammar
section for each family. Agent `ma`, object `ci`, broad `xi` and explicit
relative-head constructions have different roles. Candidate source notations stay
linked to their own attestations. Drafts retain lexical gaps and unresolved
surface choices in the evaluation; ordinary translations use complete proposed
Pinyin/IPA text and the one general quality note.

The 60-case challenge checks recoverability of verified existing words as well as
complete semantic frames. Dictionary and survey evidence have separate IDs and
scope; the static shards contain dictionary witnesses only. The report compares
natural, candidate-matched and one-query budgets, and excludes unverified targets
from recall denominators.
