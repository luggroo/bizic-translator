#!/usr/bin/env python3
"""Render the generic lexical/construction retrieval evaluation."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
d = json.loads((root/'docs/evaluation/retrieval-results.json').read_text())
m = d['model']
manifest = d['index']

def labels(rows):
    result, seen = [], set()
    for r in rows:
        if r['zh'] in seen:
            continue
        seen.add(r['zh'])
        result.append(r['zh'].replace('|','/') + (f" ({r['score']:.3f})" if r.get('score') is not None else ''))
        if len(result) == 4:
            break
    return '；'.join(result) or '无'

lines = ['# 真实词典语义检索评测', '',
    'BGE 已成功加载并编码完整公开字典，建立持久索引，返回带义项、见证和出处的候选。此报告比较字面与向量检索，并分别测试句子和语法构式检索；没有金标准或母语者评分，不报告准确率。', '',
    '## 数据与模型', '',
    '- 公开来源固定于 bizic-dictionary 提交 `bc3aadfbe877d83b723f6ad37dfc1d0df0b48198`。',
    '- 原始字典含 9,297 个合并词条、19,577 条见证；适配器保留各见证的中英义项、词性、方言、出处及关联记音，不把父条目的聚合释义套给所有来源。',
    '- 模型：`'+m['model']+'`；revision：`'+m['revision']+'`。',
    '- 权重 SHA-256：`'+m['weights_sha256']+'`；PyTorch '+m['torch']+'，Transformers '+m['transformers']+'；CPU、4 线程、768 维。',
    '- CLS 向量与 L2 归一化；查询前缀：`'+m['query_instruction']+'`。长记录使用重叠窗口，未用模拟向量、同义词表或关键词回退替代语义检索。',
    '- 当前索引记录 '+str(manifest['record_count'])+' 条，唯一编码文本 '+str(manifest['unique_texts'])+' 条；不同来源或调查点可以共享同一汉译向量，但仍是独立证据。',
    '- 类型计数：`'+json.dumps(manifest['record_types'],ensure_ascii=False)+'`。', '',
    '## 固定词汇查询', '',
    '精确基线采用 NFKC 后的整字段相等；另跑字面子串基线。向量查询编码原查询，不先改写同义词。下表节选真实候选，完整结果保留来源和见证标识。相似度只用于排序。', '',
    '| 查询 | 精确基线 | 向量近邻节选 |', '| --- | --- | --- |']
for row in d['queries']:
    lines.append('| '+row['query']+' | '+labels(row['exact'])+' | '+labels(row['semantic'])+' |')
lines += ['', '熟练灵巧、等候、红和杜鹃等是值得核对的候选。挑担义、地陷、融化、不同树种和昆虫名则说明共享字形或相关主题会产生误配。嫁妆的字面命中来自其他调查点，不能据此宣布找到了某个优先来源或特定村点的对应词。', '',
    '原词性和来源必须逐项核验。Northern 标签不自动补成 Longshan；空 locality 仍为空。只有 attestationIds 与当前义项相交的记音才能返回。树木量词应按原始类别说明和实句选择，不能按汉语量词逐字对应。', '',
    '## 否定控制', '', '| 查询 | 近邻 |', '| --- | --- |']
for query, rows in d['negative_controls'].items():
    lines.append('| '+query+' | '+labels(rows)+' |')
lines += ['', '相反极性的词仍可能出现在附近；后缀、自由动词、事实否定、意愿和能力也不能互换。语义检索不代替语法适用性核验。', '',
    '## 独立构式检索', '',
    '调查句保留原记音、汉译、逐词释义、点号及定位；文本块和抽取段落保留原文，文化说明只作背景。语法条目是二手描述，引用需回查原书。原始段落的页码表示章节起始页，不伪称每段都有精确页码。', '',
    '| 查询 | 语法结果 | 60757 句子结果 |', '| --- | --- | --- |']
for row in d['constructions']:
    grammar='；'.join('`'+r['id']+'`' for r in row['grammar'][:2])
    survey='；'.join('`'+r['id']+'`' for r in row['60757'][:2])
    lines.append('| '+row['query']+' | '+grammar+' | '+survey+' |')
lines += ['', '词汇与构式结果有不同的 record_type；相同场景不保证具有所需语法。工具、接受者、动作名物化、先后和伴随关系都应检索完整原段，再确认能否作词汇替换。', '',
    '## 执行与复现', '',
    '- [本次检索原始结果](evaluation/retrieval-results.json)',
    '- [完整真实编码的进度日志](evaluation/full-build.log)',
    '- [字典下载记录](evaluation/dictionary-fetch.json)',
    '- [实际执行命令](evaluation/commands.txt)',
    '- [测试结果](evaluation/tests.log)', '',
    'README 提供下载、建索引、过滤检索和测试命令。模型测试实际运行预训练推理，覆盖持久化、出处、范围、CLI 和长文本尾部；未提供模型路径时会明确跳过。', '',
    '首次下载已诊断并修正权重格式假设；该固定 revision 使用 pytorch_model.bin。模型和索引的 revision/checksum 会核验，长记录不再静默丢弃结尾。', '',
    '后续改进重点是补全可定位的源语例句、细化短释义与词性、人工审查反义及近邻误配，并在真实人工判定集合上比较模型。当前仅评测 BGE，未虚构其他模型或整篇翻译的效果。', '']
(root/'docs/semantic-retrieval-evaluation.md').write_text('\n'.join(lines))
