# No-execution translation trials

The skill now routes short text-reader tasks through evidence reuse, bounded dictionary lookup and composition checks. It uses the published tujia.biz catalog and URL templates, keeps Northern and Southern sources separate, and permits source-supported IPA when a display spelling is unavailable. Existing CLI routes remain available.

The trials produced complete supported clauses for six fixed examples, two dictionary-based compositions and two held-out inputs. This is a small compiled-reference evaluation, not evidence of unrestricted translation accuracy or native-speaker approval. Six harder meaning-sensitive cases remained incomplete with specific gaps.

## Revisions and isolation

| Revision | Role |
| --- | --- |
| `53c853a6d2eee3ecac7a6c119a56ab94efa71876` | Frozen baseline skill |
| `207d3e31ac4c89a82c73dcb363656eaf26763a7c` | Candidate 1: three-pass route, source evidence reuse, compact basic order and shared evidence pack |
| `d37accd3045229dc3e1d9ad11547284101e544b1` | Host-captured query snapshots; skill unchanged from candidate 1 |
| `3ecafe77d2b276aa0ca3ba5330f80d9d22e8d848` | Candidate 2: explicit prediction route, narrower Southern duration scope, citation-tone labels, two-failure request budget; complete witness snapshots |

Each translation participant began without parent conversation history or other agents' answers. A separate reviewer inspected source evidence and outputs. The evaluator and participants used the available inherited model; no Gemini/DeepSeek session or native speaker was involved. No model identifier, seed or reasoning configuration was recorded.

Participants were instructed not to use shell, Python, Node, local files, page JavaScript, archive decoding, arbitrary REST or transcription conversion. This was an **instruction-enforced simulation**, not a physically reduced tool allowlist. The platform's JavaScript tool wrapper only dispatched the permitted webpage reader and displayed its response; it did not run lookup, parsing or conversion logic. Their execution status is `not_executed`, not a claim that those tools were technically absent.

Cases and acceptance criteria were fixed before candidate runs in [cases.json](cases.json). The supported set includes source quotations and new compositions, so blanket abstention cannot pass. See [prompts.md](prompts.md) for replication and [traces.md](traces.md) for participant-reported tool sequences. The traces are retained summaries, not a provider-exported execution transcript.

## Observed results

| Lane | Result | Evidence limit |
| --- | --- | --- |
| Matched baseline, six inputs | Six complete IPA clauses; two requested accent-spelling lines left unresolved; 10 webpage calls | One run; no wall-clock measurement |
| Candidate 1, same six inputs | Six complete paired outputs; independent review 24/24 | Three are compositions, three reproduce compiled examples |
| Dictionary relay, two inputs | Two complete IPA compositions; independent review 8/8 | Actual page captures supplied to the participant; no direct website-reader success |
| Candidate 2, two held-out inputs | Complete negative-wanting and planning clauses; independent review 8/8 | One novel subject substitution and one planning paraphrase of a cited example |
| H1–H3, each in both dialects | Independent review passed all six scoped gap responses | Gap handling, not six completed translations |
| Current hosted webpage reader → tujia.biz | Still unavailable on tested static endpoints | No HTTP status or root cause provided by this tool |
| Host HTTP → 14 agent-selected dictionary URLs | 14 HTTP200 responses | Python HTTPS capture, no page JavaScript; separate transport |

The matched positive trial used **10 → 4 webpage-tool calls**, and **28 → 13 document-read attempts**. This single comparison indicates fewer round trips. It is not a latency distribution or a controlled claim about provider caches, reasoning time, platform speed, or long documents. The baseline already produced six complete IPA clauses; the observed improvements are more direct evidence retrieval, recovered published accent spellings and fewer calls.

## Actual translations

The IPA below retains source citation forms. It is not independently checked connected speech. Published derived notation and new compositions keep those labels in the linked result files.

| Input | Dialect | Output | Basis |
| --- | --- | --- | --- |
| 你没有说话。 | Northern | ní sǎ lǐ dá · /ɲi²⁴ sa²¹ li²¹ ta²⁴/ | B06:90 ex116, compiled example |
| 我不想回家。 | Northern | ngá cū hxí cá dá · /ŋa²⁴ tsʰu⁵⁵ ɣɨ²⁴ tsʰa²⁴ ta²⁴/ | B06:129–130, subject substitution |
| 我的衣服脏。 | Northern | ngá niě sībā hxēsē · /ŋa²⁴ ɲie²¹ sɿ⁵⁵pa⁵⁵ ɣɤ⁵⁵sɤ⁵⁵/ | B06 possessive/property construction |
| 我会写字。（技能） | Southern | ngo mcǐ wāggè · /ŋo³¹ m³³tsʰɿ¹³ wa⁵³ge²¹/ | Xiang 2017:98, compiled example |
| 我在这里住了十年。 | Southern | jjiàdiè ngo hì niú 'údùdù · /dʑia²¹tie²¹ ŋo³³ hi²¹ ȵiu³⁵ ʔu³⁵tu²¹tu²¹/ | Li 2000:116, compiled example |
| 今天我打算写字。 | Southern | mùniàn ngo mcǐ wāddè · /mu²¹ȵian²¹ ŋo³¹ m³³tsʰɿ¹³ wa⁵³de²¹/ | Same-source planning composition |
| 我吃饭。 | Northern | /ŋa²⁴ jɤ²¹ ka²⁴/ | Three selected B06 dictionary witnesses + SOV |
| 你喝水。 | Southern | /ni³³ tsʰe³⁵ dzʉ⁵⁵/ | Three selected Tanxi survey witnesses + SOV |
| 你不想回家。 | Northern | ní cū hxí cá dá · /ɲi²⁴ tsʰu⁵⁵ ɣɨ²⁴ tsʰa²⁴ ta²⁴/ | Held-out subject substitution |
| 今天我打算买猪。 | Southern | mùniàn ngo zzìlòn pūddè · /mu²¹ȵian²¹ ŋo³¹ dzɿ²¹loŋ²¹ pʰu⁵³de²¹/ | Held-out planning paraphrase, Xiang 2017:96 |

[Grammar results](grammar-results.json) retain citations and review qualifications. [Dictionary results](dictionary-results.json) retain exact entry, source and witness IDs; [fixtures](fixtures/) contain original captured text and host metadata. [Held-out results](holdout-results.json) retain the final trial and all six unresolved cases.

The negative-wanting examples preserve citation `dá /ta²⁴/`; the reference separately describes its connected-speech tone after a preceding 24 tone. The new planning predicate `wāddè` is licensed as a narrow composition in the compiled material; its complete spoken realization has not been independently inspected. These qualifications are part of the acceptance decision.

## What changed after review

Candidate 1 removed obsolete two-entry coverage assumptions and broad mandatory site rereads. Complete grammar examples can supply their own lexical evidence, and only unresolved slots trigger dictionary lookup. The new basic-order section avoids downloading the full reference grammar for a simple clause. Published derived spellings remain usable with attribution; reusing them does not claim a converter ran.

The first adversarial run still spent requests on four dictionary queries after catalog/directory failures. Candidate 2 stops that route after two distinct static endpoint failures, without claiming a domain-wide outage. The final run obeyed that budget. It also routes predictive “会” separately from ability, limits Southern residence-duration generalization, and distinguishes source citation tones from verified connected speech.

The relay recovered B06 first-person evidence from the merged `w1585` detail even though exact “我” showed no B06 query group. Exact-query omissions therefore cannot establish source-wide absence. It kept source geography separate from unrecorded witness locality, retained mixed notation provenance and avoided borrowing display forms from unrelated witnesses.

## Validation and deployment scope

- Repository tests: **58 passed, 3 skipped**. The skipped cases require the real pretrained encoder/model assets; no BGE inference was claimed.
- Both full and `--without-static-lexicon` grammar checks passed. The packaged slim export passed its check; its static shard integrity is intentionally outside that mode.
- Existing notation QA checked 105 published pairs and reports **30 independently unverified**. Its tone-class check does not validate IPA phoneme accuracy; this trial does not change that status.
- [CI on candidate 2](https://github.com/luggroo/bizic-translator/actions/runs/43529628303) passed.
- Changes are in the [skill experiment PR](https://github.com/luggroo/bizic-translator/pull/2). The separately installed cloud skill has not been replaced; the available tools expose no skill-package update operation.

Fresh DeepSeek/Gemini runs remain necessary to measure those platforms' actual access and latency. Full stories, native naturalness, broad lexical recall, sentence-level phonology and unavailable-source constructions remain outside this small acceptance set. The supplied-text relay demonstrates the reasoning workflow with real dictionary content; it does not fix or conceal the hosted reader's access failure.
