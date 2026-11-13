# Text dictionary evidence without a local runtime

Use this route when webpage reading is available and local execution is unavailable, or when the user explicitly requests webpage-only retrieval. Start at the designated [text dictionary](https://tujia.biz/text/). Shell, Python, Node, JavaScript execution and gzip decoding are not prerequisites. [Return to retrieval](retrieval.md).

## Discover published coverage

1. Open the directory once. Read its coverage statement and actual query links. The initial release covers **吃** and full witness pages for **w684** and **stedt-rn-43584**; this is a published subset, not a URL template for every word. Let the currently retrieved directory establish any wider coverage.
2. Follow a listed query URL for the intended sense. If link attributes disappear but a full URL remains in visible text, open that exact URL. Retain the observation that supplied it. Preserve case, percent encoding and opaque IDs; `stedt` must not become `stedT`.
3. Read candidate senses and dialect groups, then follow only advertised text-detail URLs. **Interactive entry (JavaScript)** does not establish that a matching `/text/entry/…html` exists. Keep those candidates as discovered but not yet inspected in this route.
4. Read complete witness blocks for promising candidates. Copy witness ID, entry ID, source ID, original form/scheme, senses, dialect, locality, locator and linked notation. Entry-wide spelling and dialect headings are navigation hints; each witness retains its own scope. Keep editorial gloss provenance and mixed-notation warnings.
5. Reuse directory, query and witness results within the task. The present two-dialect sample normally requires four cold document reads: directory, query, two details. This is a request budget, not a latency guarantee. Read independent details together when supported; reopen for a material conflict or requested freshness check.

If the directory is unavailable, use supplied evidence with its provenance or another actually available route. A partially extracted directory does not prove the website needs JavaScript. Do not synthesize links, calculate FNV buckets mentally, or substitute search snippets for witnesses. Known-path reads of designated references remain available when supported.

## Access, coverage and evidence

| Observation | Status | Next action |
| --- | --- | --- |
| Query and witness text actually read | `retrieved` | Select by sense and source under [evidence rules](evidence.md). |
| Complete directory explicitly limits coverage and omits the requested sense | `not_published` | Use an available local/static export or supplied evidence; otherwise retain that meaning as a marked Chinese insertion. This does not establish lexical absence from Tujia. |
| Only introduction, candidate summary or incomplete witness returned | `partial` | Use fields actually read; another explicitly supplied/read URL or evidence fragment may fill the gap. |
| Access error | `unavailable` | Retain exact error and time; do not call it zero matches or infer an HTTP code. |
| Retrieved query explicitly reports no matches in its stated scope | `no_match` | Apply bounded [semantic expansion](../../tujia-synonym-lite/SKILL.md) through available routes. |
| No reader and no supplied evidence | `not_executed` | Preserve source meaning with an evidence gap; do not manufacture Tujia forms. |

An unseen field remains unknown. A citation such as “STEDT rn …” is a witness ID only when the page explicitly identifies it that way. Unknown locality is not Longshan or Tanxi by default. Keep the Brassett priority and record each source actually checked; this subset cannot establish an exhaustive source search.

## Compact evidence record

Keep this internally and show it for an audit. Local and injected packs may use the same fields; unknown values stay null.

```json
{
  "task": {"source_text": "吃", "target_dialect": "north", "locality": null},
  "retrieval": {
    "mode": "Skill-based", "transport": "web", "status": "retrieved",
    "local_execution": "not_available", "embedding_run": false,
    "directory_url": "https://tujia.biz/text/", "query_url": null,
    "fetched_at": null, "data_version": null, "source_revision": null
  },
  "witnesses": [{
    "entry_id": null, "attestation_id": null, "source_id": null,
    "canonical_source_id": null, "dialect": null, "locality": null,
    "original_form": null, "original_scheme": null, "sense": null,
    "linked_notations": [], "url": null, "quote": null,
    "data_version": null, "entry_checksum": null
  }],
  "grammar": [],
  "conversion": {"execution": "not_executed"},
  "gaps": []
}
```

This is a template, not a completed lookup. Set the actual status and an empty witness array for failure/unexecuted retrieval. Use `local_execution: not_executed` when CLI exists but was deliberately unused. Record `transport: cli` for executed commands and `transport: supplied` for injected material; neither proves webpage-reader success.

Copy visible data versions and entry checksums where present. These identify a build/input, not automatically a repository commit or a checksum independently verified by the agent. Keep the bundled skill revision separate from live page versions. Compare mixed versions explicitly rather than claiming one snapshot. Grammar records retain the actual reference/anchor, quotation, source and rule scope; a word lookup supplies no sentence grammar.

## Compose from evidence

Use directly published, witness-linked spelling/IPA pairs. Preserve source/normalized/derived labels; mixed-origin notation metadata may not identify a separate origin for each witness. Without execution, conversion stays `not_executed`. If a target spelling or IPA is absent, retain the source form with a precise missing-notation label under [notation audit](notation-audit.md), without calculating a replacement.

For sentences, read available grammar evidence and match predicate class, roles, negation, modality and aspect. “不会开车” alone does not license “不会来”; “躺着/拴着” alone does not license “正在砍柴”; “肚子胀” alone does not license “气球胀起来”. Complete unsupported meanings as labeled Chinese spans or a Chinese structural draft when the construction itself lacks evidence.

After successful web lookup, report `检索模式：Skill-based（网页静态词典；本地未执行）`. Identify supplied evidence separately. With no successful retrieval, report `检索状态：未取得证据` and its actual reason. Follow the [ordinary output policy](output.md) and dialect separation; detailed packets belong to requested audits.
