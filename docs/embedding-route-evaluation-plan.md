# Codex standalone task — Evaluate and improve the shared semantic-decomposition route

**Repositories:** application/skill: https://github.com/luggroo/bizic-translator ; canonical public linguistic data: https://github.com/luggroo/bizic-dictionary

**Read first:** `README.md`, `skills/translate-tujia/SKILL.md`, `skills/translate-tujia/references/semantic-decomposition.md`, `skills/tujia-synonym-lite/SKILL.md`, `skills/tujia-synonym-lite/concepts.json`, `src/tujia_lex/index.py`, `src/tujia_lex/embedding.py`, `scripts/evaluate-semantic-retrieval.py` and `docs/semantic-retrieval-evaluation.md`.

## Goal

Real BGE embedding search must use the **same meaning-to-construction decomposition** as the static fallback. Evaluate how much this improves finding useful Tujia words and constructions. Implement improvements and tests; do not merely describe them. Do not confuse a semantic-nearest-neighbor with a licensed final translation. Default translations must be complete, natural and assertively proposed, with **only one overall quality note**, not warnings after every suffix.

## Technical setup

Follow the exact README installation instructions and reuse its pinned `BAAI/bge-base-zh-v1.5` revision, model checksums and schema-v2 index. Pin `bizic-dictionary` at a recorded commit and build the index from that same snapshot; verify counts of **every dictionary entry and attestation** and include surveys, text blocks and constructions as documented. Log model revision, input digests, index manifest, Python versions and commands. No mock embeddings; prove that every semantic run calls real query encoding and returns real cosine scores. If setup is blocked, report the failure honestly and still implement executable tests with fixtures; never substitute historical evaluation as a fresh run.

## Implement shared query planning

Introduce a small reusable query-plan module (suggested `src/tujia_lex/query_plan.py`) with `plan(expression, context, dialect)` returning labeled candidate queries, semantic roles, a construction family and the meaning that must be preserved. Start with the shared reference and curated seeds, but ensure a way to create **new, unseen** query plans; do not merely match input strings against a lookup table. The BGE route should run **raw query + planned expansions** when appropriate; the static fallback should use the same plan with its own exact lookup. Reuse model/index in memory and cache repeated encoded query strings.

Preserve provenance: `entry_id`, `attestation_id`, `canonical_source`, `record_type`, `dialect`, `locations`, `forms`, `IPA`, `source citation`; rank Brassett (2006) before 2004 for Northern/Longshan **after semantic relevance**, then broaden as needed without conflating locations. Maintain source-spelling link integrity. No user-visible made-up phonetics or cosine scores.

## Anchor cases

Use six seed cases for debugging, not as sole final evaluation:
- 路人 → 在路上走的人 → 路 + 走 + 人/agent nominalizer (user-proposed `la hxi ma`).
- 香味 → 气味, optionally pleasant scent → actual smell *noun* vs incense/smell *verb* distinction.
- 玩具 → 玩的东西 → 玩 + object/associated-thing nominalizer (user-proposed `geci-xi`).
- 饮料 → 喝的东西 → 喝 + object nominalizer (user-proposed `hu-ci`).
- 令人费解 → 不能懂得/理解 → cognition predicate + negative ability (not simple 不知道).
- 经济损失 → 钱/财物 + 失去/亏损, or compensation as a related remedy, **not** 钱 alone.

Also include 画地为牢 → 自己把自己关住, and 被审判的人 → 受事关系从句, explicitly checking roles.

## Build a separate unseen challenge set (minimum 36 cases)

Create `tests/data/semantic-compositional-challenge.json` with at least **three independent cases in each family**:
1. Event → person: 守门人、打鱼的人、送信人、旁观者.
2. Event → artifact or patient: 食物、坐垫、清洁用品、写字工具.
3. Purpose/function → object: 开瓶器、储水容器、遮雨的东西、取暖用的东西.
4. Controlled hypernym: 花香、噪音、寒意、潮气.
5. Negative predicate / negative ability: 陌生人、难以置信、看不见、无法忍受.
6. Abstract-to-concrete: 财产损失、工钱、债务、收入减少.
7. Spatial relation: 河岸、山脚、门外、两腿中间.
8. Aspect/modality instead of separate adverb: 快要下雨、还在吃、尚未吃完、刚刚回来.
9. Figurative idiom paraphrase: 画地为牢、束手无策、心里有数、无路可走.
10. Role/focus/relative-clause: 被骂的人、我画的画、审判我的人、我被审判.

Above examples are *test prompts*; do NOT invent guaranteed Tujia equivalents. Add more diverse prompts until the minimum is met, and avoid counting trivial paraphrases of the same case as independent tests. Hold at least **12 genuinely unseen cases** outside the curated concept file, ideally stratified by family.

## Gold set and scoring

Annotate for each case:
- Original Chinese phrase, one disambiguating context sentence and target sense.
- Query decomposition: action/predicate, head noun, participant, location, property, negation, TAM and argument roles when applicable.
- Acceptable dictionary `entry_id` or specific attestation IDs **only after real evidence inspection**; otherwise a semantic-component description with `gold_status: pending_review` (not included in recall denominators).
- Expected construction family, possible forms of semantic drift, negative controls/false friends, locality and source priority.
- Grading rubric separating **retrieval hits** from a **compositional translation hypothesis**.

Compare at least:
A. exact literal lookup;
B. raw BGE embedding only;
C. decomposed BGE embedding queries;
D. Skill-based decomposed exact lookup;
E. hybrid reranking and construction-aware selection.

Report Recall@1/5/10/20, MRR where gold IDs exist, semantic-component coverage and full-frame coverage, role/negation/TAM preservation, false-positive rate, selected source agreement, native-lexeme utilization, unnecessary Chinese insertions, latency and actual query count. Report macro by operation and per-case details, not just overall averages. For B vs C, count compute cost fairly: number of expanded searches, total retrieved candidates and latency; compare under matched candidate budgets too.

Negative controls must include `香` meaning incense rather than pleasant odor; `闻` verb rather than odor noun; `水` as a kind of beverage rather than a universal equivalent; `钱` insufficient for economic loss; `不知道` not automatically unable to understand; `路` alone not an incidental passerby; polarity reversals (被审判的人 vs 审判别人的人) and `-xi/-ci/-ma` argument effects. Penalize false matches, even if ranked highly by BGE.

## Test the claim, not just the implementation

For each anchor and challenge item print:
1. Raw query and direct embedding top-20 with **real** cosine similarity, IDs and witness source.
2. Each expansion query, relation label, its top-20 real neighbors and model score.
3. Union/reranked candidates (show both query score and chosen candidate, avoid fabricated unified cosine).
4. Which components genuinely support a Tujia phrase and the proposed construction.
5. One concise comparison of why raw/expanded/static/hybrid succeeded or failed.

Save machine-readable logs in `artifacts/` or `docs/evaluation/`, a readable markdown report, failing-case taxonomy, and runnable regression tests. Ensure normal translation uses the **shared plan** in both modes. State explicitly whether embedding was actually used for this run.

## Efficiency and acceptance criteria

- Do not spin up any public endpoint. No query-time full dictionary decompression or whole-repo scans; cap expansion count and reuse cached artifacts. Keep model weights/index outside Git.
- No leaked holdout answers hard-coded into the planner; freeze the challenge labels before tuning where feasible, and evaluate on a separate holdout slice after changes.
- Actual end-to-end BGE executed with correct pinned manifest, original vs decomposed comparisons, provenance preserved.
- All six anchor cases tested; >=36 challenge cases across >=8 operation families with >=12 out-of-seed.
- Every metric has a stated denominator. If no gold labels, report qualitative results, not invented recall/accuracy.
- Run grammar skill QA, full existing pytest and new planner/evaluation tests; fix failures.
- Produce code changes plus a final concise markdown report with at least 10 worked examples, including false positives and remaining failure modes.
- **Translation style:** one general quality sentence at the end of a translation (`质量说明：译文依据现有词典和语法材料拟写，尚未经母语者审校。`); no repetitive parenthetical warnings per lexeme/suffix. Complete proposed translation first; model-internal validation remains strict.
