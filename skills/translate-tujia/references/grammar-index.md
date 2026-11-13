# 土家语翻译：语法检索入口 / Grammar lookup index

按原文语义选择专题，读取相应规则与例句，复用已核对的常见构式。规则与完整例句足够时可直接组句；仅为具体缺项或来源冲突补读对应 tujia.biz 章节。简单陈述先看[基本语序](clause-patterns.md#basic-order)；无需逐篇读完所有专题。

## 按语义定位

| 语义触发 | 专题 | 主要区分 |
| --- | --- | --- |
| 快要、就要、将要、马上、正要、开始、快……完 | [体貌与情态 → 将然／临近](aspect-modality.md#prospective) | 将来意图、动作将开始、接近终点 |
| 还、仍、还在、还没、尚未、还不必、仍能 | [体貌与情态 → 还](aspect-modality.md#still) | CONT、否定与情态作用域 |
| 了、了……了、V了多久 | [体貌与情态 → “了”的选形](aspect-modality.md#le-selection) | 事件、状态变化、参照时点、持续与终点 |
| 已经、过、刚刚、做完、曾经、不再 | [体貌与情态 → 完成与结果](aspect-modality.md#completion) | PFV、COMPL、PRF、EXP、结果状态、停止 |
| 会、能、可以、得、没空、来不及 | [体貌与情态 → 能力](aspect-modality.md#ability) | 一般能力、熟练、体力、时间、许可 |
| 想、愿意、必须、该、不必、不许、恐怕 | [体貌与情态 → 意愿／必要](aspect-modality.md#volition) | 意愿、义务、允许、判断、推测、否定 |
| 来去、上下、进出、往返、携物移动 | [趋向后缀](direction-suffixes.md) | 移动者、路径、立足点、动作阶段与肯否定；来源分别选择 |
| 多个谓词后成分、情态与否定连用 | [谓词成分组合](aspect-modality.md#predicate-slots) | 位置、互斥与高层否定 |
| -i的去义、位移、将行与过去用法 | [-i用法](aspect-modality.md#i-functions) | 位移／位移兼将行／纯将行，及作用域 |
| 连读55／21、助词前调变化 | [助词变调](aspect-modality.md#particle-sandhi) | 引用基记与语流实现，成分所属组 |
| 词干变化、缩合、合音 | [谓词合音](aspect-modality.md#predicate-fusion) | 构形分析与记录的完整词形 |
| 也、还、再、另外的追加义 | [追加与焦点](clause-patterns.md#addition) | 追加事件／数量与持续意义分别处理 |
| 一边……一边、……着……、……后、接着、然后、用…… | [事件与从句链接](event-linking.md) | 完整事件、方式、持续背景与工具 |
| 因为、所以、因此、然后、不然、否则；本土连接词 | [事件链接 → 连接词](event-linking.md#connectives) | āimǒ因果、āiliē先后、āitā否定条件；建议另核 |
| 当……时、如果……就、虽然……但是 | [小句关系](event-linking.md#event-relations) | 时间、条件、让步与焦点背景 |
| 不、没、别、不是、没有、禁止 | [否定](clause-patterns.md#negation) | 事实／意愿否定、禁止、否定判断、存在否定 |
| 是、有、在、宾语、话题、SOV | [句型](clause-patterns.md#clause-types) | 判断、存在、事件与论元关系 |
| 红、好、漂亮、长、大的、吃的、那只 | [性质词与名词化](clause-patterns.md#nominalization) | 状态谓词、定语形式与名词化 |
| 给谁、对谁、从哪儿、向哪儿、谁的、格助词 | [关系标记](clause-patterns.md#case-frames) | 语义角色、短语边界与标记位置 |
| 数词、量词、一个、一件 | [数量短语](clause-patterns.md#classifiers) | 名词类别、数词量词组合与语序 |
| 更、比、很、程度、相差多少 | [程度与比较](clause-patterns.md#comparison) | 比较项、基准、程度与差量 |
| 吗、谁、什么、几、怎么、还是 | [疑问句](clause-patterns.md#questions) | 是非问、选择问与疑问词位置 |
| ……的、……的人／东西、工具、取暖用品 | [nie、niexi 与独立指称](nie-niexi.md) | 中心词、参与者角色、性质与使役用途 |
| 南部持续、经历、计划、能力 | [南部体貌与情态](aspect-modality.md#south) | 泸溪材料的相应构式与时长表达 |
| 调号拼音／IPA 不合、缺调、来源不同 | [转写与核验](notation-audit.md) | 同一 attestation 的音形、地点与原始调值 |

优先匹配已有完整例句的语义、谓词类别和组合条件，再检索新的词项；为新构式或具体来源冲突补查例句。常用规则的来源页码与例号保存在对应专题，网站链接放在其支持的规则旁。

## 例句与来源

规范化例句表使用 `调号拼音 | IPA | 汉义 | 出处`，每行按同一 attestation 配对，保留地点、页码和例号。来源原引文保留原记音；派生展示记录转换方法，缺失音调进入记音核验。分别标明 Brassett 2006、其他北部、南部、未刊补充材料及生产性组句。

专题分别维护体貌与情态、事件链接、句型与名词短语、名物化的选择规则；词汇与词形存入 `lexicon/manifest.json` 所指的来源记录，记音冲突由 notation audit 核验。
