# Translation execution state and reuse

Use one task record throughout translation and follow-ups. With file tools, save it in the task's writable artifact directory; with text-only tools, retain the same compact structured record in task context. Save complete evidence separately from the short working view. Ordinary translation uses static lookup; only an explicit embedding request enters [runtime lifecycle](runtime-lifecycle.md).

## Stages and completion

| Stage | Done when | Reuse / next action |
| --- | --- | --- |
| Fix evidence | Dialect, source snapshot/revision and notation are recorded; supplied evidence is identified | Reuse this snapshot throughout. Check freshness only for an explicit update or a concrete source conflict. |
| Analyze | Each clause has participants, scope, head/modifier relations and required semantic slots | Read the [matching grammar topic](grammar-index.md) and its cited template/example. Reopen a source only for a named unresolved condition. |
| Retrieve | Required lexical slots have suitable witnesses, or the shared budget is exhausted and a supported paraphrase/insertion is selected | Batch unresolved queries, retain statuses below, and reuse the manifest/reader. An unresolved gap goes to the [recovery playbook](recovery-playbook.md), not a fresh search loop. |
| Compose | Complete translation, segmentation, chosen senses, constructions and citations are saved | Run meaning, role, scope, source and notation checks once on this version; fix only affected clauses. |
| Deliver | Checked text and any requested formats are generated from the same saved version | Formatting changes reuse the linguistic analysis. Correcting meaning invalidates only dependent clauses and artifacts. |
| Publish, when requested | Remote content is fetched/opened and matches the intended version | Record the URL and observed verification. A local file or upload response alone leaves publication unverified. |

## Query ledger

For each concept, retain its intended sense, required slots, a maximum of 12 distinct query keys (normally 8–12), and queries already attempted. Count the original exact lookup and all paraphrase/component queries across scripts, tools and retries against the same concept budget. Set a smaller limit when sufficient; do not fill the budget after the completion condition is met.

A query key consists of normalized text, engine, dialect/source filters and source revision. Reuse results for the same key. A narrower source inspection of an existing witness reuses that witness; any fresh lexical query is recorded before execution. Shared queries can satisfy several concepts; retain their relation to each concept without repeating the tool call.

| Status | Meaning / next action |
| --- | --- |
| `pending` | Planned but not run; batch with other unresolved keys |
| `hit` | Successful lookup with witness IDs; select or reject each relevant sense |
| `zero` | Successful lookup with no scoped match; expand within the remaining budget |
| `unavailable` | Access/read/integrity failure; no inventory conclusion. Retry only after a concrete access/path change, using the same key |
| `resolved` | All required slots and the construction have support; stop retrieval for this concept |
| `exhausted` | Budget reached with named gaps; use supported productive paraphrase or minimal insertion and finish the clause |

The ledger belongs to the task, not an individual script invocation. CLI limits bound one call; they do not reset this cumulative budget. Do not rerun queries merely to reconstruct a log. Save the actual response or its witness IDs at first execution. Detailed JSON stays in the evidence artifact; the working view needs only query/status, selected IDs, missing slots and the next decision. Fetch a complete record only when the missing field affects that decision.

<a id="translation-record"></a>
## Structured translation record

Keep these fields for every checked sentence. Preserve source IPA, spelling and morpheme boundaries verbatim in evidence; the display spelling follows the [output policy](output.md).

```json
{
  "version": 1,
  "source_snapshot": {"revision": "", "manifest_sha256": ""},
  "dialect": "north",
  "sentences": [{
    "id": "s1",
    "source": "",
    "translation": "",
    "tokens": [{
      "surface": "", "ipa": "", "gloss": "",
      "sense": "", "entry_id": "", "attestation_id": "",
      "source_id": "", "locator": ""
    }],
    "roles": {}, "scope": {}, "constructions": [],
    "open_issues": [], "checked_version": 1
  }],
  "query_ledger": [],
  "artifacts": []
}
```

Record word boundaries, selected senses and available paired pronunciation during composition. Fill an IPA/gloss gap only when needed and supported; leave a named gap instead of inventing a value. A later gloss/PDF request uses these tokens and citations. For a missing field, inspect that witness alone. Generate text, HTML and PDF from the same checked version and apply [output alignment](output.md); do not independently retranslate for each format. Rendering or layout changes update artifacts without invalidating lexical or grammar decisions.

An independent blind evaluation, when requested, is separate from production reuse: preserve its independence, test inputs, outputs and judgments. Its cost does not justify skipping required checks or substituting an evaluation on already reviewed examples.
