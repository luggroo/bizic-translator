# Translation output, progress and audits

Use this page for the final format, transcription and progress updates. [Return to the main workflow](../SKILL.md).

## Deliver the requested result

For an audit-only or explanation-only task, present the requested analysis. For a translation, follow the user's requested format; otherwise alternate **one Tujia sentence, then its source-language sentence** throughout the text. Preserve the source wording and order; the second line is the original, not a back-translation. Keep the source sentence together if its translation needs several shorter clauses. Number sentence pairs in longer passages and separate Northern and Southern versions, each with its own source lines. Show **叶氏拼音 only when the user explicitly requests it**.

非静态模式保留 **调号拼音 + IPA**：土家语行用调号拼音，来源对应的 IPA 作为附加行置于每组土家语／源语言句子之后。用户明确的记音要求优先。

**静态降级（Skill-based，含网页检索）覆盖上述记音默认：土家语行只交已核定调号拼音；缺拼音处就地写来源 `/IPA/`，不另列整句 IPA。** 整句只有 IPA 时直接写 `/〈原句 IPA〉/`。两者皆缺才标局部读音待核，不能手拟拼音。用户明确的记音要求优先。

以下逐句示意用于非静态模式；静态模式按上面的记音规则处理土家语行并省略附加 IPA 行：

```text
1. 土家语：〈完整译句，调号拼音〉
   源语言：〈对应的原文句子〉
   IPA：/〈土家语对应 IPA〉/

2. 土家语：〈下一句译文，调号拼音〉
   源语言：〈下一句原文〉
   IPA：/〈土家语对应 IPA〉/

检索模式：Embedding / Skill-based / Mixed
```

In Chinese-language explanations, use the full name 汉语, including 汉语—土家语对照 labels. Preserve original quotations and bibliographic titles.

## Optional word-by-word gloss and aligned PDF

每次翻译任务中，若用户尚未说明 gloss 偏好，询问一次：“需要每个词的 gloss（词义和语法标注）吗？需要的话，也可以排成逐词对齐的 PDF。”可在开始翻译时询问并继续翻译，或在交付逐句对照译文后询问；不因等待这一可选回答而停下翻译。沿用本任务中已说明的偏好，用户已要求或拒绝时不再重复询问。

用户需要 gloss 时，保留编号后的完整源语言原文，随后按 **调号拼音 → IPA → gloss** 三行逐词／词素对齐。拼音只在对齐行出现一次；不在上方另抄整句拼音。此 gloss 格式适用于静态与非静态检索，优先于上方普通逐句译文的记音默认。IPA 使用与拼音相连的来源见证，保留原始调值；缺可靠 IPA 的单元标“IPA 待核”，其余单元继续对齐。引用基记与连读实现按下方[来源对应记音](#source-aligned-transcription)区分。

覆盖词汇义和语法成分，只在材料支持词素切分时细分；拼音、IPA 和 gloss 保持相同的单位及边界标记。固定词保持整体。用“与格、否定、使役、人量词、起始”等简短语法标签，必要解释集中放入注释；使用英文缩写时附简短释义表。gloss 标实际词义或语法功能，原文的意译、近义替换及组合疑点另作注释，避免用预期译义填充标注。源语言原文保持原有措辞与语序。

### 论文式逐词排版

用户选择 PDF 时，默认采用简洁的语言学论文版式：

- 使用黑白、衬线字体、常规页边距和页码，标题只保留文档名称与方言。例句用 `(1)`、`(2)` 连续编号；采用无底纹、无框线的三行对齐，不另加彩色栏目、装饰标题或页脚品牌。
- 拼音用斜体，IPA 与 gloss 用正体。每个单位独立成列，三行左对齐；列宽容纳该列最宽的一行，防止词形、声调或短语法标签在单元内部折行。用无边框表格或独立对齐单元实现，避免靠连续空格对齐。
- 长句按完整词／词素组分行，每组始终保留拼音、IPA、gloss 三行。原文与对应例句相邻，三行组不跨页拆散；保持正文可读字号，通过自然换行和分页容纳内容。
- 注释放在相应例句后或文末，集中说明记音、语法疑点和来源。检索模式及执行过程放在交付说明中，PDF 保留与阅读和核实语言材料有关的信息。

格式示例（Brassett 等 2006:101，例70；IPA 为来源基记）：

(1) 我要小的。

| *ngá* | *bíkuī* | *dì* |
| --- | --- | --- |
| ŋa²⁴ | pi²⁴kʰuei⁵⁵ | ti⁵¹ |
| 我 | 小的 | 要 |

聊天中可用表格表达对齐；PDF 中隐藏表格边框，保留同一列的三行对应。

### PDF 字体与交付检查

使用覆盖汉字、调号、组合字符及 IPA 的字体，并验证实际导出的 PDF，而不只检查生成过程中的预览。保存并关闭文件后，在新进程中重新打开，逐页渲染检查；可用时再用另一渲染器复核。确认汉字与 IPA 完整、声调和词素边界清楚、三行对齐且未跨页拆散。文字提取成功不能替代显示检查。

出现缺字、错字或字体子集映射错误时，先改用完整嵌入字体并关闭引起重映射的子集压缩；仍有兼容问题时，从已正确渲染的源 PDF 将字形转为矢量轮廓，再重新打开检查。保留可编辑源文件，交付可正常显示的成品；只在生成并检查后提供 PDF 链接。

Report 检索模式：Embedding after current BGE inference, 检索模式：Skill-based after static lookup, or Mixed when both ran. Keep scores, rejected alternatives and verification logs for requested translation reviews or evidence audits.

For [webpage-only evidence](web-evidence.md), disclose the evidence actually used: `Skill-based（网页静态词典；本地未执行）`, `Skill-based（技能参考；本地未执行）`, or `Skill-based（提供的页面文本；本地未执行）`. Combine these descriptions when appropriate. Keep failed dictionary access separate from successfully read grammar. If no applicable evidence was obtained, report `检索状态：未取得证据` with the access/coverage gap. Follow [complete-before-qualifying](paraphrase-and-borrowing.md#complete-before-qualifying): compose every clause, place minimal Chinese insertions in Tujia word order, and explain specific remaining uncertainties after the translation. Keep the completed provisional wording in the translation and identify its evidence limits in a note. Label newly composed constructions as productive drafts and distinguish them from attested quotations.

Explain a material paraphrase or Chinese insertion briefly when it helps the reader understand the translation. Write selected Chinese insertions directly in Chinese characters. For an unsupported lexical choice, use an attested synonym, productive native paraphrase or Chinese insertion. Present findings established by the materials and the work performed.

When the user requests a quality statement or a specific limitation affects use, give **one overall quality note** with the relevant facts. Ordinary translations follow the format above.

## Source-aligned transcription

Keep quotations in their source notation. Form new surface words from source-linked stems and licensed morphological rules, marking rule-derived forms separately from recorded quotations. Follow [notation audit](notation-audit.md).

Without conversion, a complete source-supported IPA clause may stand as the main output when target spelling is missing. Label the missing representation once; do not call the whole translation incomplete solely for that display gap. Reusing published paired/derived spellings does not claim a conversion was executed in this task. Preserve their attribution in the [evidence pack](evidence-pack.md).

Identify citation-tone notation separately from connected-speech realization. If a composition simply retains source forms, label its IPA as `来源基记` and, where relevant, state `连读实现未核`. A published example's base tone is not a claim of verified surface pronunciation. Check documented sandhi/fusion conditions before offering a surface reading; in the no-execution route, follow the realization limits in [web evidence](web-evidence.md#composition-and-notation).

- Preserve source tones, phonemes, syllable boundaries, nasalization and untoned particles. For future `i`, render the source-licensed surface form with an untoned **-i** boundary after its verb stem or DIR host, preserving the source's [fusion](aspect-modality.md#predicate-fusion), syllabification and tones. Original quotations retain their notation.
- Pair spelling and IPA through their attestation links. Use verified forms for the translated spans and Chinese characters for selected insertions.
- Keep original quotations, derived spellings, productive compositions and established loans identifiable in the evidence record.

## Progress updates

During sustained work, share a retrieved word or construction and a usable draft passage. State the target dialect and actual retrieval mode once they are established. Continue with new findings, decisions or passages as work progresses. Keep progress messages outside the final translation.

## Requested reviews and evidence audits

For each disputed span, show intended meaning, candidate form, source/locality, grammatical basis, decision and correction. Record actual model queries separately from semantic interpretation. Describe review, source freshness and test results from the work actually performed.

Organize requested findings on independent dimensions:

- **Lexical retrieval and use:** apply the [retrieval statuses](evidence.md#retrieval-status-and-draft-reconciliation), retaining each source's coverage and candidate decisions.
- **Word order and construction:** inspect participants, predicate class, attachment, conditions and clause linkage in the assembled sentence.
- **Morphology and particles:** identify function, scope, position and source-specific form; record tone and spelling differences separately.
- **Literary paraphrase:** apply the [image and voice criteria](paraphrase-and-borrowing.md#express-the-intended-meaning); a successful image can coexist with lexical or grammatical corrections.

Use material within its authorized scope. Keep private-source citations locally and use authorized public pointers in distributed packages.
