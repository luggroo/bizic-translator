<a id="blocker--next-action--禁止式规则的操作替代路线"></a>
# Recovery routes

Use this page to select the next action when retrieval, grammar or transcription needs another route. Apply it to the main Skill and the synonym-lite route.

**Fast path:** source meaning → Brassett 2006/2004 → BGE or synonym-lite → original witness → relevant grammar topic → complete clause. Reuse records and loaded assets throughout.

| Situation | Action | Continue with |
| --- | --- | --- |
| Webpage reading but no execution | Follow [text dictionary evidence](web-evidence.md) from its directory and actual URLs. | Inspected witnesses or a specific access/coverage gap; local execution remains unexecuted. |
| Partial directory, unpublished query, or interactive-only candidate | Distinguish `partial`, `not_published` and `unavailable`; use another available evidence source. | A supported phrase or visible Chinese span, without guessing static URLs or claiming zero matches. |
| Text-only tools with a gzip dictionary | Prefer [published text pages](web-evidence.md); read UTF-8 shards through [retrieval](retrieval.md) when their paths can actually be resolved. | Exact source-linked witnesses. |
| Source or web material unavailable | Read the matching local source record or authorized supplied material; inspect its citation and full attestation. | Available source-linked words and constructions. |
| Book-only grammar | Prepare a reference-grammar addition proposal or add a reusable skill entry with forms, conditions, examples and citations; follow [source maintenance](evidence.md#book-only-findings). | A rule future translations can use directly. |
| Missing BGE assets | Run [environment preflight](runtime-lifecycle.md), inspect existing assets and select reuse, setup or static retrieval. | The available retrieval engine. |
| Model/index identity | Check manifest, source revision, model metadata and a current query. | 检索模式：Embedding after inference; otherwise static lookup. |
| Reusable asset storage | Record paths and lifecycle in `.local/tujia-runtime.json`; use retained storage for reusable assets and temporary paths for scratch/tests. | Reused assets or static lookup while storage is arranged. |
| Compound or literary expression | Use [semantic decomposition](semantic-decomposition.md) to retrieve paraphrases, predicates, participants and results. | An equivalent native construction. |
| Broad semantic neighbor | Inspect meaning, semantic roles, context and any feature needing an extra modifier. | The candidate that preserves the intended meaning. |
| Locality selection | Compare Brassett 2006, 2004 and localized Longshan evidence; record the locality of selected spans. | A consistent target variety. |
| Conflicting witnesses | Inspect the full attestation, linked notation and adjacent text; prefer the better-supported local record. | A selected complete form with its source retained. |
| Related story or cultural summary | Retrieve continuous passages for matching events and participants. | The requested story's names, causes and ending. |
| New sentence | Apply a productive construction with matching event roles and predicate class. | A complete composed clause. |
| Chinese function word | Identify aspect, modality, direction, comparison, focus, negation or clause relation; follow [grammar-index.md](grammar-index.md). | Predicate morphology, particles or linked clauses. |
| `liex` / `mor` / `bor` selection | Compare whole events, manner and maintained background in [event-linking.md](event-linking.md). | The matching event relation. |
| Negation and modality | Determine scope, inspect positive/negative pairs and predicate-component order. | A supported combined predicate or two simpler clauses. |
| Property word | Inspect predicate, modifier and independent nominal forms in [clause-patterns.md](clause-patterns.md). | The form for the intended syntactic role. |
| Nominalization | Determine the referent, explicit head and argument gap; compare `-ma`, `-xi`, `-ci` and niexi examples. | A matching nominal construction. |
| Classifier choice | Search count phrases and original source glosses for the head noun's class. | A native classifier or a complete Chinese numeral–classifier phrase. |
| Optional marker or word order | Compare complete source sentences before and after the proposed change. | A supported argument and marker arrangement. |
| Chinese verb–object insertion | Separate object and predicate, arrange the selected Tujia frame and attach predicate morphology. | A grammatical Chinese insertion in Tujia syntax. |
| Lexical slot after bounded lookup | Try a productive native paraphrase, then a minimal Chinese content word. | A complete clause. |
| Short fragment in an alignment | Inspect the full word, syllable boundaries and same-attestation notations. | A verified whole form or paraphrase. |
| Tone or spelling conversion | Use [notation audit](notation-audit.md) and the original attestation's linked fields. | Source-aligned spelling and IPA; Chinese characters for selected insertions. |
| Variant readings | Compare their locality, phonological profile and attestation links. | The selected source-specific version. |
| New native composition | Check productive syntax, selection conditions and semantic roles. | A readable translation. |
| Sustained work | Share a usable word, construction or draft passage and continue with cached records. | Concrete progress and a complete final translation. |
| Claims about scores or review | Refer to command results, source metadata and review records. | Facts established by the work performed. |
| Public serving | Build embeddings and shards offline; serve cached static files with request limits. | Bounded public delivery. |
| Private source | Use it locally within its authorized scope; keep private citations and distribute authorized public pointers. | The translation and permitted artifacts. |

<a id="exploration-budget-and-escalation"></a>
## Retrieval budget

Follow the shared [retrieval budget](retrieval.md#misses-scores-and-cost). Expand an evidence audit for a named source, role or scope question and record how the result affects the choice.

Use [output.md](output.md) for the final format. Keep detailed retrieval, decision and verification records for requested reviews or evidence audits.

Source coverage and candidate use follow the [retrieval statuses](evidence.md#retrieval-status-and-draft-reconciliation); bilingual query scope and search budgets follow [retrieval](retrieval.md#misses-scores-and-cost).
