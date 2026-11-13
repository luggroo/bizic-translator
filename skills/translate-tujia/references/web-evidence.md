# Translation through a text reader

Use this route with webpage reading and no local execution, or an explicit webpage-only request. The dictionary at [tujia.biz/text/](https://tujia.biz/text/) serves text in HTML without page JavaScript. Execution, gzip decoding, hashing and arbitrary REST access are unnecessary. An access failure remains specific to the actual reader and URL; readable HTML cannot remove a platform access restriction.

<a id="three-passes"></a>
## Three passes

1. **Plan and reuse.** Identify dialect, participants, predicate, polarity, modality and aspect. Reuse complete evidence already supplied/read in this task. Read the relevant [grammar topic](grammar-index.md), not every reference. Basic order is in [clause patterns](clause-patterns.md#basic-order); Southern planning, skill and duration are in [Southern predicates](aspect-modality.md#south). A cited example/rule can supply both a word and its construction. Record it as a compiled reference, without claiming to have read the original book or dictionary witness.
2. **Fill unresolved slots.** Read the directory or [catalog](https://tujia.biz/text/catalog.json) once when dictionary discovery is needed. Batch independent query reads, then read the best candidates' complete witness blocks. For an unmatched sense, use one bounded expansion of up to four related Chinese keys, or one relevant index. A larger explicit evidence audit may expand for a named unresolved question. Retain source priority and exact evidence provenance.
3. **Compose and audit.** Apply the cited construction under its documented conditions. Check every participant, role, quantity, time, polarity, modality and result; then check source-linked notation. Deliver actual supported clauses. Use visible gaps only for unsupported spans or constructions. A blanket Chinese draft does not complete a translation when evidence supports a Tujia clause.

These are decision phases, not a fixed number of tool calls. For a simple cold lexical task the usual dependency chain is discovery → parallel queries → parallel details, plus the relevant grammar read. Cached complete evidence can remove any of those reads. Stop when the needed evidence is sufficient; fetch more for an identified conflict or missing condition. Record observed calls/latency, not a promised speedup.

## Dictionary routes

The current text export covers Brassett 2004/2006, the Longshan survey and the published Southern collections. Read the live directory/catalog for scope and version; this is a selected export, not every record on the website.

| Need | Route |
| --- | --- |
| Known Chinese sense | Use the catalog's `exact_zh` template: `https://tujia.biz/text/lookup/zh/{query}.html`. |
| Related Chinese keys or an unclear exact gloss | Use its `initial_zh` template: `https://tujia.biz/text/initial/zh/{initial}.html`, then select an actually listed key. |
| A particular source | Read its page from `catalog.sources[].page`; query pages group canonical sources separately. |
| English gloss search or export-wide presence check | Use `catalog.dialect_indexes.north.page` or `.south.page`. These complete, separate tables contain Chinese, English, source forms and entry IDs. Read only the requested dialect; they are larger than query pages. There is no advertised `/lookup/en/` route. |
| Full evidence for a discovered ID | Use the published `entry` template: `https://tujia.biz/text/entry/{entry_id}.html`. |

Constructing a URL from a **published template and an observed key/ID** is supported; inventing an entry ID is not. An ordinary Chinese query can be put directly into `exact_zh`; preserve characters and let the reader encode the URL. The catalog defines normalization and exceptions. If exact normalization/encoding cannot be established, follow a listed URL/key rather than calculating a hash or guessing a transformed spelling. Preserve case: `stedt` and `stedT` are different strings.

The complete dialect tables establish presence within their export when actually read to completion. They do not replace witness pages. A truncated extraction or reader `find` miss cannot establish absence. Query summaries and entry headings may aggregate sources; inspect each chosen witness's own meaning, original form, scheme, dialect, locality and citation. `Source ID`, canonical source ID, entry ID and attestation ID are different fields. Unknown locality stays unknown.

For Northern evidence, inspect Brassett 2006 then 2004 where available, followed by localized Longshan material for gaps/conflicts. Retain each source's search status. An already cited 2006 construction can be used directly; an unavailable comparison is a recorded limitation, not a reason to discard it. For Southern evidence, keep Tian, Chen, Xiang, Li and survey forms at their own recorded scope. A shared dialect label alone does not license mixing tones, pronouns or suffix allomorphs.

## Access and stopping rules

| Observation | Record | Continue with |
| --- | --- | --- |
| Actual query/detail/reference text read | `retrieved` | Fields and rules actually present. |
| Introduction, candidate summary or incomplete witness only | `partial` | An exact missing-field request or other available cited evidence. |
| Access error | `unavailable` | Exact error; supplied evidence or readable bundled references. No invented HTTP code or zero-match claim. |
| Complete retrieved scope explicitly lacks a key | `not_published` | A related key/source within budget; this is not absence from Tujia. |
| A successful scoped query explicitly returns zero matches | `no_match` | One bounded semantic expansion. |
| No applicable retrieval performed | `not_executed` | Already supplied evidence, or visible evidence gaps. |

Do not retry the same failed URL without a changed condition. If two distinct static endpoints fail in the same reader, stop this route for the task and use available reference/supplied evidence; this is a request budget, not proof of a domain-wide outage. If the reader reports the domain itself inaccessible, stop trying its dynamic anchors and archives immediately. Raw skill references already known to exist may still work. A generic failure of one path alone does not prove the whole domain is blocked. Preserve successful grammar/reference retrieval separately from failed dictionary access. Use source-specific statuses in the [evidence pack](evidence-pack.md).

When a tool returns only the start of a reference, open the relevant section/line range before declaring its example missing. Reader `find` can miss visible strings; inspect the routed section itself. Do not reread unrelated sections to compensate.

## Composition and notation

Reusing or recombining published forms is not transcription conversion. A new subject can fill a cited subject slot; a cited productive rule can combine compatible stems and markers. Record the changed slots, source forms, rule and conditions. Preserve recorded allomorphs. New sandhi, fusion, tone assignment or cross-profile spelling needs a cited complete realization or an actually executed converter; otherwise leave that realization unresolved. A new sentence is a **productive composition**, not an attested quotation.

Use published witness-linked spelling/IPA pairs or already paired reference examples. Keep original/derived labels; a reference's published derived spelling is usable with that attribution even though the current agent did not run a converter. Missing target spelling does not invalidate a complete supported IPA sentence: present the available notation as the main line and label the missing representation once. Follow [notation audit](notation-audit.md).

Match construction and meaning explicitly. “不会开车” alone does not license predictive “不会来”; “躺着/拴着” does not license dynamic progressive; physiological “肚子胀” does not establish “气球胀起来”. For insufficient evidence, retain the intended meaning in a precise gap, including whole-clause uncertainty where necessary.

Use the [ordinary output format](output.md). Report actual page reads, compiled references and supplied excerpts separately. Detailed packs belong to requested audits; no fake CLI, conversion, embedding, locality or original-book verification claims.
