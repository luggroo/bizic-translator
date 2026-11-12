# 取暖用品：从性质改为使暖事件

撤销 `lò niexi`。该式仅以“暖和”作为性质，未表达谁变暖、什么使其变暖。一般取暖用品应分解为“使人暖和的”。

修订候选：**lò dǒ lò niexi**，/luɔ⁵¹ tuɔ²¹ luɔ⁵¹ nie ɕi/。两处 lò 同音异义，依次为“人”和“暖和”；niexi 保留无调形式。这是依据语法的生产性拟译，仍需审校实际搭配。

- 人：w1421，见证 stedt-rn-453974，Brassett 2006，词汇定位2.5，原形 luo⁴。
- 暖和：stedt-rn-454769，Brassett 2006，词汇定位6.1，原形 luo⁴。
- 使役：Brassett 2006:155–156，例47“妈妈让孩子睡觉”，受影响者后、谓词前使用 /tuɔ²¹/。使暖表达按此结构拟用；该例并非取暖原句。
- 烤火：词库确有 w2327 和 w1545，以及“围火取暖”stedt-rn-454359。这些词增加火源限制，不再与一般“暖和”列为无条件替代候选。

原 c14 的金标准把“暖和”和“烤火”并列为可替代组件，未检查使役关系，因此原指标不能证明取暖用途已保留。本次保留历史实验文件，将修订计划、角色、候选、实际分数与成本单独存入 [新运行结果](c14-causative-rerun.json)，不将旧结果改写成新实验。

实际执行：使用既有完整索引 `.cache/bge-index`，模型 BAAI/bge-base-zh-v1.5，固定版本 f03589ceff5aac7111bd60cfc7d497ca17ecac65；词典固定版本 072046c39261cf536e0ce29f06779cd3eeb99219。本次仅重跑 c14 的混合 E 路线；未重跑全挑战集，也未重报总体指标。

```sh
.venv/bin/tujia-lex plan '取暖用的东西' --route E --index .cache/bge-index --model-path .cache/models/bge-base-zh-v1.5 > docs/evaluation/compositional/c14-causative-rerun.json
.venv/bin/python scripts/render-challenge-translations.py --data-root /workspace/bizic-dictionary
```

## 原查询 BGE Top-20（本次实际运行）

|排名|释义|原词形|词条 ID|余弦相似度|
|---|---|---|---|---|
|1|烤火取暖|thu⁵³|stedt-rn-212235|0.6208926|
|2|烤火取暖|thu⁵⁵wu²¹|stedt-rn-289038|0.6208926|
|3|围火取暖|mi⁴tu⁴|stedt-rn-454359|0.5714390|
|4|暖水瓶|ze33sui33phiŋ55|survey-word:60756:0350|0.5515570|
|5|暖水瓶|tshɤ33khai55sui31tshu55tshɿ55|survey-word:60823:0350|0.5515570|
|6|暖被窝|eŋ55naŋ33lɔ53|survey-word:60756:2633|0.4947718|
|7|暖被窝|sɿ55lan55lo55|survey-word:60757:2633|0.4947718|
|8|暖被窝|nie55phũ55lo55|survey-word:60823:2633|0.4947718|
|9|暖的那个|sa²gi¹|stedt-rn-454925|0.4939873|
|10|暖和|lo⁵⁵|stedt-rn-289284|0.4845978|
|11|暖和|lo⁵⁵xo⁵⁵xui⁵⁵|stedt-rn-399851|0.4845978|
|12|暖和|luo⁴|stedt-rn-454769|0.4845978|
|13|暖和|luo4 / lov|w1422|0.4845978|
|14|暖和|luo3 / luo4|w1422|0.4845978|
|15|暖和|lɔ35tsha53|survey-word:60756:0991|0.4845978|
|16|暖和|lo55xo22|survey-word:60757:0991|0.4845978|
|17|暖和|lo55xo55xuai33|survey-word:60823:0991|0.4845978|
|18|炉子|lu33tsɿ33|survey-word:60756:1798|0.4679655|
|19|炉子|mi53lo33tshɿ55|survey-word:60823:1798|0.4679655|
|20|暖；热|gi³|stedt-rn-454881|0.4535668|

分解查询“暖和”的第3名为 stedt-rn-454769（0.7285879）；“人”的第4名为 w1421（0.6884712）。使役关系及 dǒ 来自规划和语法，不是向量搜索返回的完整句子。挑战集当前 c14 金标准已剔除烤火替代项，并新增受使者“人”和使役要求；历史报告仍采用当时标签，不与修订标签直接比较。
