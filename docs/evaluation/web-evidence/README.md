# Webpage evidence experiment

Historical four-page prototype. The current agent-based skill iterations and expanded dictionary evidence are recorded in [nojs-agent](../nojs-agent/README.md). Coverage, artifacts and counts below describe this earlier snapshot.

This experiment adds a URL-reader route to `translate-tujia` while preserving
the existing CLI/BGE routes. It starts at `https://tujia.biz/text/`, discovers
published queries and detail URLs, and retains witness-specific evidence.

The deployed four-document HTTP chain and the JavaScript-disabled browser
checks passed. The current conversation's webpage reader still fails on the
directory, so its end-to-end status is blocked. Skill structure/packaging checks
passed, with 44 related tests passing and one model-dependent test skipped.
Fresh Gemini/DeepSeek runs with this skill remain outstanding.

The website change is commit `1e527796a62f4ef2ed95a9e9991dafed5f938656`
in `luggroo/bizic-dictionary`. The skill experiment starts from translator
commit `ae6d20e70078a700799b836f3056f219a97faf4c`. The separately installed
cloud skill is an older package and was not replaced.

## What is measured

| Layer | Method | Scope |
| --- | --- | --- |
| Browser end to end | JavaScript disabled, desktop/mobile, directory → query → detail links | Real browser navigation and 21 source witnesses |
| Flattened links | Read visible main text and discover exact URLs, without link attributes | One supplied directory; later URLs discovered |
| HTTP evidence | `probe.py`, four document reads and per-witness extraction | Deterministic Python harness, not a hosted model |
| Skill walkthrough | Apply the new instructions to the retrieved evidence and constrained missing-evidence cases | Agent review; no independent Gemini/DeepSeek inference |
| Existing CLI | Current exact lookup and structural/query-plan tests | No BGE inference; one model-dependent test skipped |

See `results.json` for the final execution statuses and `live-http.json` for
document provenance. A failure of the conversation's webpage reader is recorded
separately from successful HTTP/browser tests. Reported results from another
platform do not establish that this reader recovered.

## Findings from the skill walkthrough

The controlled lexical task is: inspect **吃** in Northern and Southern Tujia
using the retrieved pages; preserve source forms without executing a spelling
converter. The evidence was supplied by the HTTP harness, so the walkthrough's
transport is **supplied**, not a successful hosted webpage-reader run.

| Scope | Accepted evidence | Output limit |
| --- | --- | --- |
| Northern, Brassett 2006 | Entry `w684`, witness `stedt-rn-454305`, source `stedt-39f4cd9a6b`, canonical `brassett-2006`; original `ga²`; linked IPA `ka²⁴` | Witness locality stays unknown. Keep the IPA record's derived/mixed-origin warning. |
| Southern, Tian 86 | Entry/witness `stedt-rn-43584`, source `stedt-cb523fc3dc`; original and linked IPA `ɣɨe³⁵` | Locality stays unknown; the Chinese gloss is editorially supplied from the English gloss. |

A source-aligned lexical draft therefore retains **ga²** and **ɣɨe³⁵** with
their notation labels. The requested tone-marked spelling remains pending:
the visible headline forms `gá` and `hxé` have no witness IDs in the prepared
summary. The experiment does not attach either headline to a particular IPA
record or claim that a converter ran. This is a useful evidence gap, not a
completed dual-notation translation.

Additional checks:

- **苹果:** the complete directory does not publish this query. Record
  `not_published`, not zero matches or a missing Tujia lexeme. With no other
  evidence allowed in this constrained case, preserve `⟦汉语插入：苹果⟧`.
- **Interactive-only candidates:** the two YuBao candidates expose actual
  JavaScript routes. Their static detail URLs are not guessed or fetched.
- **Partial directory fixture:** an introduction without the complete-list
  statement yields `partial`; absence of an extracted link does not establish
  unpublished coverage. This is an injected fixture, not a live site failure.
- **Source and witness identifiers:** preserve lowercase `stedt`; source IDs
  remain separate from witness IDs, and missing locality does not inherit the
  source-wide geography.
- **Unsupported sentence evidence:** with only these lexical pages supplied,
  “不会来”“正在砍柴”“气球胀起来” remain complete Chinese meaning/structure
  drafts with the specific lexical and construction gaps. The contrary
  examples in the rules cannot supply their negation/aspect/result morphology.
  This constrained test does not assert that the full grammar lacks those rules.

## Reproduce

```sh
# Directory is the only seed; no detail URLs are supplied to the harness.
python3 docs/evaluation/web-evidence/probe.py --output web-http.json

# Test a locally built website using the same discovery procedure.
python3 docs/evaluation/web-evidence/probe.py \
  --site /path/to/built/site --output web-local.json

python3 scripts/check-grammar-skill.py
python3 scripts/check-grammar-skill.py --without-static-lexicon
python3 -m pytest tests/test_skill_structure.py \
  tests/test_lightweight_synonym_search.py tests/test_query_plan.py -q
```

The harness uses Python's HTTP client with inherited proxy/CA settings and TLS
verification enabled. It does not run webpage JavaScript or a language model.
The four-read trace measures HTTP work; it cannot establish model latency or a
speedup over the earlier skill.

The CLI smoke query used static dictionary revision
`072046c39261cf536e0ce29f06779cd3eeb99219` (12 raw exact hits, nine Northern
hits, two witnesses printed by the requested limit). The webpage build reports
data version `22cb01c6881a6922`. These identifiers describe different snapshots;
the experiment does not claim equal hit counts or identical merged entry IDs
between CLI and web results.

## Hosted-model follow-up

Load the experimental skill and its references, then give Gemini/DeepSeek only
the task below. Save actual tool calls, returned text, timing and final output.

> Use the supplied translate-tujia experiment. With webpage reading only, start
> at https://tujia.biz/text/ and inspect 吃 for Northern and Southern Tujia.
> Discover query/detail URLs from retrieved pages; preserve each selected
> witness's original form, source, locality and notation evidence. Then assess
> whether this directory can supply 苹果 and explain the precise remaining gap.
> Do not use local commands, guess detail URLs, or label headline spelling as a
> verified witness pair. Report actual access separately from coverage.

Accept only a recorded directory → query → witness trace or an honestly
reported access/coverage blocker. Model-specific completion and latency remain
unverified until those fresh runs occur. The website still publishes one query
and two full details; this experiment does not provide general dictionary coverage.
