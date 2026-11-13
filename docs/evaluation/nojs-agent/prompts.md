# Reproduce the no-execution trials

Use a fresh conversation for each run. The execution restriction used here was an instruction, not a reduced technical tool allowlist. Record the actual environment's capabilities; do not claim it lacks a tool merely because this trial prohibits using it.

## Participant prompt

```text
Use translate-tujia at this immutable revision:
https://raw.githubusercontent.com/luggroo/bizic-translator/3ecafe77d2b276aa0ca3ba5330f80d9d22e8d848/skills/translate-tujia/SKILL.md
Resolve relative skill references at the same commit.

Use only your actual webpage-reading tool and supplied text. Do not use shell,
Python, Node, local file reads, page JavaScript, gzip decoding, hash computation
or arbitrary REST calls. A tool wrapper may only dispatch the webpage reader;
it may not transform evidence or run a conversion. Do not read evaluation
results or other agents' answers.

Translate these independently:
N1 北部：你没有说话。
N2 北部：我不想回家。
N3 北部：我的衣服脏。
S1 南部：我会写字。（已经掌握的技能。）
S2 南部：我在这里住了十年。
S3 南部：今天我打算写字。

Return actual translations and precise gaps, if any. For each form and
construction record source, actual reference/section, quotation or rule,
changed slots, dialect/locality and notation provenance. Distinguish composed
sentences from source quotations, citation-tone notation from connected speech,
and compiled references from original publications. Do not invent missing
spelling or verification. Report the actual ordered URL/tool trace, successful
and failed reads, and call counts. No estimated elapsed time.
```

For the matched baseline use commit `53c853a6d2eee3ecac7a6c119a56ab94efa71876` with the same six inputs. Candidate 1 used `207d3e31ac4c89a82c73dcb363656eaf26763a7c`. Readable references and their tool extraction limits affect results; one comparison does not measure a latency distribution.

For the challenge lane, use H1–H3 from [cases.json](cases.json), each in both dialects. For a fresh held-out lane use HN/HS without exposing results. A challenge may pass through a justified translation or precise visible gaps; an all-Chinese draft cannot pass a supported positive.

## Supplied-page relay

Ask the participant to translate D1/D2 and request its own dictionary URLs. The host captures only those requested URLs with [capture.py](capture.py), then returns the actual page text and provenance. The participant chooses queries and IDs; the host does not suggest words or translations. Captures can be injected directly or read from immutable fixture URLs. Record dictionary transport as `supplied` either way.

This run used catalog → six query pages → seven selected entry pages, all with host HTTP200 and no page JavaScript. The [fixtures](fixtures/) preserve the texts and capture metadata. Their Raw URLs were evaluation containers, not a replacement production dictionary or a repair for blocked tujia.biz access.

## Reviewer prompt

Give an independent reviewer the inputs, actual outputs, evidence and the four frozen criteria in [cases.json](cases.json). Require it to inspect the referenced source passages and selected witness bindings. Award one point per criterion per supported positive. Reject fabricated sources, mismatched senses, unauthorized cross-dialect substitutions and unmarked unsupported morphology. Allow source-supported notation variants only with their provenance. Report conditional passes explicitly; do not equate compiled-reference agreement with a native-speaker judgment.

Fresh Gemini and DeepSeek runs must report their own real tools and results. These local agent trials do not certify either hosted platform.
