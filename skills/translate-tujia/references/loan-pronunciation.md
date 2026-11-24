# 汉借词读音：直接查最终映射表

先采用词库已有词项的记音。缺项、新拟借词和人名等直接查附带的南北映射表；运行时只需汉字、目标方言及必要的分义，不需要知道读音来自哪份字表或哪个同音字。

从仓库根目录运行：

```bash
python3 scripts/lookup-loan.py 珙 --target north
python3 scripts/lookup-loan.py 军 --target south
python3 scripts/lookup-loan.py 难 --target north --sense 患难
python3 scripts/lookup-loan.py 难 --target north --choices '{"0":"lán"}'
python3 scripts/lookup-loan.py 架 --local-readings
python3 scripts/lookup-loan.py 鞋 --register 白
```

个人安装的技能使用 `python3 <skill-root>/scripts/lookup-loan.py`，参数相同。命令只用 Python 标准库，直接读取附带的 `readings.json.gz` 或 `assets/loan-readings.json.gz`，不联网、不加载模型，也不在运行时推导字音。

查询文白用字时，`--local-readings` 读取随技能附带的 `local-readings.json.gz`。`input_key` 是北部键盘的无调检索音，`source_reading` 是当地记音。`witnesses` 逐一列出来源与用例。比如第 39 页「架」的吉首两读都有例词，分别是「十字架儿」和「吵架」。查询 `--register 文` 或 `--register 白` 可按明确的文白依据筛选。重庆的补读保留其当地原注。核查范围包括《吉首方言研究》第 37–40 页、《汉字音典》吉首和重庆两份字表。中古音类线索另页可筛查。[文白对照工作簿](https://github.com/luggroo/bizic-translator/blob/main/data/han-registers.xlsx)

| 返回状态 | 下一步 |
| --- | --- |
| `resolved` | 整词采用 `romanization`／`ipa`；按词合并内部音节，保留词界。 |
| `needs-selection` | 用当前语境的 `--sense` 选择分义；仍有多个候选时，以字位置和表中最终拼音／IPA 的 `--choices` 选读。例如“患难”选 `lán`，“困难”选 `lǎn`。 |
| `missing-character` | 任一字无映射时，整个词保留汉字，整词 IPA 和拼音留空。例如某词一字有音、一字无音时，不输出半个词的发音。 |

多音字的候选直接列最终读音；不用查询或解释来源。表中分义用于消歧，候选优先级已经在离线整理时确定。北部、南部各查自己的表，不相互套用。

人名按实际语境选择多音字读法；例如前缀“阿”的表内候选需按称谓／人名语境选择。将 `needs-selection` 与 `missing-character` 分开处理，前者已有候选，可继续选读。

完整 UTF-8 表格为[北部表](https://github.com/luggroo/bizic-translator/blob/main/data/loan-readings-north.tsv)、[南部表](https://github.com/luggroo/bizic-translator/blob/main/data/loan-readings-south.tsv)，列为“汉字、调号拼音、IPA、分义”。整理时先保留直接记录，再用小学堂《洪武正韵》、韵典网《洪武正韵牋》及汉字音典《蒙古字韵》《中原音韵》的同音组补缺；整理证据独立保存，不进入运行时查询。
