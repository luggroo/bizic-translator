# Semantic decomposition with real BGE retrieval

This experiment tests whether words present in the dictionary can be recovered, and whether those words support a complete semantic frame. A component hit does not establish a complete translation.

Execution: **executed_fresh_real_BGE**. The run covers 60 expressions, 11 annotated families and 15 compositional holdouts. No historical BGE results were used.

[60 challenge candidates in Pinyin/IPA](challenge-translations.md), [Chinese findings](SUMMARY.zh.md), and [six worked anchors](worked-examples.md).

## Reproduction

Dictionary revision: `072046c39261cf536e0ce29f06779cd3eeb99219`. Model: `BAAI/bge-base-zh-v1.5` at `f03589ceff5aac7111bd60cfc7d497ca17ecac65`; weights SHA-256 `731cf5d88ed555a21ff2f2d9fa4db43b10489173ddd9178db3eecfd7a2bae044`.

Complete index: 9,297 dictionary entries, 19,577 attestations, 23,694 total records and 12,593 unique embedded texts. Static shards use the same source revision.

[Commands](commands.txt), [build log](build.log), [evaluation log](evaluation.log), [full model/index manifest and metrics](results.json), [test output](tests.log), [grammar QA](grammar-qa.log). Model weights and the generated full index are ignored local assets.

## Design and denominators

A = original literal exact lookup; B = original real BGE; C = shared plan with real BGE; D = shared plan with static exact shards; E = combined candidates with component, role and source checks. Planning sees the expression and context, never gold IDs. Productive rules parse new arguments, relative clauses, spatial frames, negation and TAM. Conventional opaque meanings use a small lexical bridge; an explicit Interpretation API handles other contextual or opaque meanings. The parser preserves ordinary context text but does not claim to understand arbitrary prose.

The dataset was independently annotated in Chinese and resolved against the canonical dictionary and survey inventory. An exploratory run prompted inclusion of separately identified survey records; gold was frozen again before the final comparison. Static D has dictionary witnesses only, so survey-only targets measure an asset-coverage limitation as well as retrieval. A verified component has one or more sense-linked dictionary attestation IDs or stable survey point/serial IDs with original file/row citations; matching any alternative counts as recovering that target. Recall@K below is macro recall of those verified component targets. Conventional entry-ID recall and component MRR are also in results.json. Unverified targets have no numerical recall denominator and still block a complete-construction claim. These are source-inventory judgments, not native-speaker judgments.

Meaning scores check frame features and semantic roles against independent annotations. Construction coverage additionally requires all required lexical components and compatible Northern source evidence. Neither score certifies fluent Tujia. Native origin cannot be inferred systematically from the available etymology fields: native vocabulary utilization is null, and the report gives verified source-lexeme utilization and explicit Chinese insertions separately. Missing lexical slots are counted, so zero Chinese insertions cannot conceal an incomplete draft.

The 15 holdouts are outside concepts.json and the planner’s expression bridges. They test compositional rule transfer within this task, not an externally blinded benchmark. Challenge cases were used to debug general rules; holdout limitations are reported.

## natural budget

each query returns Top-20; up to 10 planned queries (E two engines).

|Route|R@1|R@5|R@10|R@20|MRR|Complete components|Construction|Missed existing targets|Queries / encodings|Candidate rows|Seconds|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
|A|0.0%|0.0%|0.0%|0.0%|0.000|0|0|89|60 / 0|10|3.43|
|B|17.5%|33.3%|44.7%|57.2%|0.316|24|19|42|60 / 60|1200|9.53|
|C|37.5%|96.1%|97.5%|99.2%|0.717|56|42|1|245 / 245|4900|44.05|
|D|64.7%|95.3%|95.3%|95.3%|0.903|53|48|4|245 / 0|1264|0.26|
|E|75.6%|98.6%|99.4%|99.4%|0.992|56|50|1|490 / 245|6164|44.78|

|Family|Cases|Raw B R@20|C R@20|D R@20|E R@20|E construction|
|---|---:|---:|---:|---:|---:|---:|
|abstract_event|4|33.3%|100.0%|91.7%|91.7%|3|
|aspect_modality|6|91.7%|100.0%|100.0%|100.0%|6|
|event_agent|8|50.0%|100.0%|100.0%|100.0%|8|
|event_object|6|83.3%|100.0%|100.0%|100.0%|6|
|function_object|7|35.7%|92.9%|92.9%|100.0%|5|
|idiom_event|4|12.5%|100.0%|100.0%|100.0%|3|
|negative_ability|5|60.0%|100.0%|100.0%|100.0%|4|
|negative_relative|3|33.3%|100.0%|100.0%|100.0%|3|
|role_relative|6|75.0%|100.0%|100.0%|100.0%|3|
|semantic_generalization|5|60.0%|100.0%|60.0%|100.0%|5|
|spatial_composition|6|66.7%|100.0%|100.0%|100.0%|4|

Holdout R@20: A 0.0%, B 70.0%, C 96.7%, D 100.0%, E 100.0%.

## matched budget

same <=12 search calls and 20 requested candidate slots per route; B/A use all slots for the original query.

|Route|R@1|R@5|R@10|R@20|MRR|Complete components|Construction|Missed existing targets|Queries / encodings|Candidate rows|Seconds|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
|A|0.0%|0.0%|0.0%|0.0%|0.000|0|0|89|60 / 0|10|3.41|
|B|17.5%|33.3%|44.7%|57.2%|0.316|24|19|42|60 / 60|1200|10.01|
|C|29.2%|96.9%|96.9%|99.2%|0.669|56|41|1|245 / 245|1200|44.78|
|D|64.7%|95.3%|95.3%|95.3%|0.903|53|48|4|245 / 0|586|0.04|
|E|75.6%|99.4%|99.4%|99.4%|0.992|56|50|1|478 / 239|907|42.70|

|Family|Cases|Raw B R@20|C R@20|D R@20|E R@20|E construction|
|---|---:|---:|---:|---:|---:|---:|
|abstract_event|4|33.3%|100.0%|91.7%|91.7%|3|
|aspect_modality|6|91.7%|100.0%|100.0%|100.0%|6|
|event_agent|8|50.0%|100.0%|100.0%|100.0%|8|
|event_object|6|83.3%|100.0%|100.0%|100.0%|6|
|function_object|7|35.7%|92.9%|92.9%|100.0%|5|
|idiom_event|4|12.5%|100.0%|100.0%|100.0%|3|
|negative_ability|5|60.0%|100.0%|100.0%|100.0%|4|
|negative_relative|3|33.3%|100.0%|100.0%|100.0%|3|
|role_relative|6|75.0%|100.0%|100.0%|100.0%|3|
|semantic_generalization|5|60.0%|100.0%|60.0%|100.0%|5|
|spatial_composition|6|66.7%|100.0%|100.0%|100.0%|4|

Holdout R@20: A 0.0%, B 70.0%, C 96.7%, D 100.0%, E 100.0%.

## single_query budget

exactly one search and 20 slots; C/D compact rewrite; E uses the same BGE pool as C, grammar reranking only.

|Route|R@1|R@5|R@10|R@20|MRR|Complete components|Construction|Missed existing targets|Queries / encodings|Candidate rows|Seconds|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
|A|0.0%|0.0%|0.0%|0.0%|0.000|0|0|89|60 / 0|10|3.48|
|B|17.5%|33.3%|44.7%|57.2%|0.316|24|19|42|60 / 60|1200|10.90|
|C|33.3%|57.8%|69.4%|85.8%|0.507|44|28|17|60 / 60|1200|10.62|
|D|0.0%|0.0%|0.0%|0.0%|0.000|0|0|89|60 / 0|0|0.10|
|E|73.1%|85.3%|85.3%|85.8%|0.933|44|28|17|60 / 60|1200|13.00|

|Family|Cases|Raw B R@20|C R@20|D R@20|E R@20|E construction|
|---|---:|---:|---:|---:|---:|---:|
|abstract_event|4|33.3%|100.0%|0.0%|100.0%|0|
|aspect_modality|6|91.7%|91.7%|0.0%|91.7%|5|
|event_agent|8|50.0%|68.8%|0.0%|68.8%|4|
|event_object|6|83.3%|100.0%|0.0%|100.0%|5|
|function_object|7|35.7%|50.0%|0.0%|50.0%|0|
|idiom_event|4|12.5%|100.0%|0.0%|100.0%|2|
|negative_ability|5|60.0%|100.0%|0.0%|100.0%|4|
|negative_relative|3|33.3%|100.0%|0.0%|100.0%|0|
|role_relative|6|75.0%|83.3%|0.0%|83.3%|0|
|semantic_generalization|5|60.0%|100.0%|0.0%|100.0%|5|
|spatial_composition|6|66.7%|83.3%|0.0%|83.3%|3|

Holdout R@20: A 0.0%, B 70.0%, C 70.0%, D 0.0%, E 70.0%.

## Worked cases and errors

|Expression|Raw B R@20|C R@20|E R@20|E lexical slots / construction|Audit|
|---|---:|---:|---:|---|---|
|路人|50.0%|100.0%|100.0%|True / True|[c01](c01.md)|
|守门人|100.0%|100.0%|100.0%|True / True|[c02](c02.md)|
|送信人|100.0%|100.0%|100.0%|True / True|[c03](c03.md)|
|旁观者|0.0%|100.0%|100.0%|True / True|[c04](c04.md)|
|打鱼的人|0.0%|100.0%|100.0%|True / True|[c05](c05.md)|
|玩具|100.0%|100.0%|100.0%|True / True|[c06](c06.md)|
|饮料|100.0%|100.0%|100.0%|True / True|[c07](c07.md)|
|食物|0.0%|100.0%|100.0%|True / True|[c08](c08.md)|
|坐垫|100.0%|100.0%|100.0%|True / True|[c09](c09.md)|
|开瓶器|50.0%|100.0%|100.0%|True / False|[c10](c10.md)|
|清洁用品|0.0%|100.0%|100.0%|True / True|[c11](c11.md)|
|遮雨的东西|50.0%|100.0%|100.0%|True / False|[c12](c12.md)|
|储水容器|0.0%|100.0%|100.0%|True / True|[c13](c13.md)|
|取暖用的东西|100.0%|100.0%|100.0%|True / True|[c14](c14.md)|
|香味|100.0%|100.0%|100.0%|True / True|[c15](c15.md)|
|花香|0.0%|100.0%|100.0%|True / True|[c16](c16.md)|
|噪音|100.0%|100.0%|100.0%|True / True|[c17](c17.md)|
|潮气|0.0%|100.0%|100.0%|True / True|[c18](c18.md)|
|寒意|100.0%|100.0%|100.0%|True / True|[c19](c19.md)|
|令人费解|0.0%|100.0%|100.0%|True / False|[c20](c20.md)|
|难以置信|0.0%|100.0%|100.0%|True / True|[c21](c21.md)|
|无法忍受|100.0%|100.0%|100.0%|True / True|[c22](c22.md)|
|陌生人|0.0%|100.0%|100.0%|True / True|[c23](c23.md)|
|看不见的东西|100.0%|100.0%|100.0%|True / True|[c24](c24.md)|
|不认识的人|0.0%|100.0%|100.0%|True / True|[c25](c25.md)|
|经济损失|50.0%|100.0%|100.0%|True / True|[c26](c26.md)|
|财产损失|0.0%|100.0%|100.0%|True / True|[c27](c27.md)|
|债务|50.0%|100.0%|100.0%|True / True|[c28](c28.md)|
|收入减少|33.3%|100.0%|66.7%|False / False|[c29](c29.md)|
|河岸|50.0%|100.0%|100.0%|True / True|[c30](c30.md)|
|山脚|0.0%|100.0%|100.0%|True / True|[c31](c31.md)|
|门外|50.0%|100.0%|100.0%|True / True|[c32](c32.md)|
|两腿中间|100.0%|100.0%|100.0%|True / False|[c33](c33.md)|
|快要下雨|100.0%|100.0%|100.0%|True / True|[c34](c34.md)|
|还在吃|100.0%|100.0%|100.0%|True / True|[c35](c35.md)|
|尚未吃完|100.0%|100.0%|100.0%|True / True|[c36](c36.md)|
|刚刚回来|100.0%|100.0%|100.0%|True / True|[c37](c37.md)|
|画地为牢|0.0%|100.0%|100.0%|True / False|[c38](c38.md)|
|束手无策|0.0%|100.0%|100.0%|True / True|[c39](c39.md)|
|心里有数|0.0%|100.0%|100.0%|True / True|[c40](c40.md)|
|无路可走|50.0%|100.0%|100.0%|True / True|[c41](c41.md)|
|审判别人的人|100.0%|100.0%|100.0%|False / False|[c42](c42.md)|
|被别人审判的人|100.0%|100.0%|100.0%|False / False|[c43](c43.md)|
|被骂的人|100.0%|100.0%|100.0%|True / True|[c44](c44.md)|
|我画的画|50.0%|100.0%|100.0%|False / False|[c45](c45.md)|
|读书的人|100.0%|100.0%|100.0%|True / True|[c46](c46.md)|
|买鱼的人|50.0%|100.0%|100.0%|True / True|[c47](c47.md)|
|洗衣服的人|0.0%|100.0%|100.0%|True / True|[c48](c48.md)|
|穿的东西|100.0%|100.0%|100.0%|True / True|[c49](c49.md)|
|读的东西|100.0%|100.0%|100.0%|True / True|[c50](c50.md)|
|洗碗用的东西|50.0%|100.0%|100.0%|True / True|[c51](c51.md)|
|砍柴工具|0.0%|50.0%|100.0%|True / True|[c52](c52.md)|
|屋后面|100.0%|100.0%|100.0%|False / False|[c53](c53.md)|
|石头旁边|100.0%|100.0%|100.0%|True / True|[c54](c54.md)|
|还在睡|100.0%|100.0%|100.0%|True / True|[c55](c55.md)|
|快要开门|50.0%|100.0%|100.0%|True / True|[c56](c56.md)|
|不能读|100.0%|100.0%|100.0%|True / True|[c57](c57.md)|
|无法看见|100.0%|100.0%|100.0%|True / True|[c58](c58.md)|
|被你骂的人|50.0%|100.0%|100.0%|True / True|[c59](c59.md)|
|喜欢我的人|50.0%|100.0%|100.0%|True / True|[c60](c60.md)|

## Concrete retrieval changes

For 路人, the original BGE query ranks 修路工 (w1266, roadman) first at cosine 0.553560: a road worker is a false friend for a passerby. Component queries recover 走 (w949) and 路 (w1224), supporting the proposed productive agent expression là hxí mā /la⁵¹ ɣɨ²⁴ ma⁵⁵/. The incidental-passerby nuance remains broader in a general walker description.

For 经济损失, the original first hit is 经济 at 0.465071. The decomposed route retrieves money w2331 and the loss-event entry stedt-rn-454677 (吃亏；受损失); the 受损失 query scores that event at 0.569226. The draft therefore retains both money and loss. The recorded form qi²kui¹ is source vocabulary; romanization alone does not establish native etymology.

For 令人费解, the 理解 query retrieves stedt-rn-289131 at 0.665023, with other 懂／明白 alternatives. The plan supplies negative ability tā tī rather than substituting 不知道. Combining different Northern lexical and grammatical sources remains a separate compatibility check.

Agent/patient control: 审判别人的人 uses a human-agent ma template; 被别人审判的人 uses an agent-containing relative clause with an explicit patient head. The drafts differ, and the role graphs keep opposite gaps. A source-verified 审判 predicate is still pending, so neither full phrase is scored as an established translation.


## Limits and failure taxonomy

- A missing gold attestation can be a retrieval or selection miss. For 砍柴工具, C actually returns entry w1076 with the 柴火 sense, but the frozen target is the 柴/木 witness and the exact sense selector rejects the variant. This is an attestation/sense-selection failure, not evidence that BGE failed to retrieve the entry. Per-case missed_existing_components uses this strict witness-level convention.
- Sense ambiguity: the odor records glossed 气味／闻 have verbal POS or undivided senses. Incense and the act of smelling are rejected; the survey provides noun 气味 at points 60756 and 60823; its use in a Longshan phrase still requires a locality decision.
- Argument drift: letter 信 differs from believe 信, and classifier 瓶 cannot supply a bottle noun. Patient relatives keep a different gap from agent relatives; suffix choice alone does not encode voice.
- Incomplete event: money alone cannot cover financial loss; drink requires a drinking predicate and object construction rather than water alone; road alone cannot cover a passerby.
- Grammatical realization: source-compatible components can still lack a verified nominalizer tone, stem allomorph, recent-completion/state choice or numeral/classifier. Audit drafts expose these slots and retain the full semantic graph.
- Generalization: generic odor/sound drops pleasantness, floral origin or unwantedness. The plan records this drift even when lexical retrieval succeeds.
- Inventory uncertainty: absent verified gold means pending review, not proof that Tujia lacks an expression. The report does not turn model scores into evidence of grammaticality.

The per-case files contain the original Top-20, every decomposed BGE Top-20 with actual cosine scores, selected and rejected senses, dictionary and attestation IDs, source/locality/notation metadata, grammatical basis and all five routes under each budget.
