# Evidence shared by local and text-reader routes

Use this compact record internally; show it for a requested audit. It describes evidence actually read, not a prerequisite JSON task for the reader. Keep one source record per retrieved/supplied document and one witness per observed record. Empty fields stay null; do not manufacture IDs for book examples.

```json
{
  "schema_version": 1,
  "task": {"source_text": "…", "dialect": "north", "locality": null},
  "execution": {"local": "not_executed", "page_js": "not_executed", "conversion": "not_executed", "embedding": "not_executed"},
  "documents": [{
    "id": "doc1", "url": null, "transport": "supplied",
    "status": "retrieved", "extraction": "partial", "fetched_at": null,
    "skill_revision": null, "data_version": null,
    "observed_checksum": null, "checksum_verified_by_agent": false,
    "error": null
  }],
  "witnesses": [{
    "document": "doc1", "entry_id": null, "attestation_id": null,
    "source_id": null, "canonical_source_id": null,
    "dialect": null, "locality": null,
    "original_form": null, "original_scheme": null,
    "sense_zh": null, "sense_en": null, "citation": null,
    "linked_notations": [], "quote": null
  }],
  "grammar": [{
    "document": "doc1", "reference_anchor": null, "quote": null,
    "cited_work_locator": null, "evidence_kind": "compiled_reference",
    "rule_scope": null, "conditions_checked": []
  }],
  "compositions": [{
    "source_clause": null, "output": null,
    "kind": "productive_composition", "evidence": [],
    "changed_slots": [], "notation_origin": null
  }],
  "gaps": []
}
```

Choose `transport` per document: `web`, `cli` or `supplied`. Reading host-produced page text is `supplied`, even when the host used HTTP successfully. A mixed pack does not prove the webpage tool reached every site. Local execution is `not_available` only if no execution tool exists; deliberate restrictions use `not_executed`.

An absent attestation ID is compatible with a cited grammar example. Use its work, page/example number, actual reference location and quotation. Distinguish a compiled quotation from inspecting the original publication. Grammar must include the rule and relevant excerpt, not only a URL.

Linked notation records retain their exact witness IDs, scheme and derivation metadata. Aggregate titles and display spellings are discovery hints until a record/reference establishes the pairing. Canonical IDs resolve source aliases; they do not supply missing locality or replace attestation IDs.

Keep skill revision, live data version and document checksum separate. A copied checksum is observed provenance, not verification performed by this agent. Reuse compatible records during a task; when versions conflict, inspect the affected forms rather than silently calling the pack a single snapshot.

Report access status, translation completeness and grammatical support separately. A supported IPA-only clause can be complete in meaning with a missing display spelling. A Chinese structural draft preserves meaning but is not a completed Tujia translation.
