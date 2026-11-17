# 汉借词读音映射表

最终成果为可直接查读音的表，运行时不需要知道来源、代查字或历时推导。

- [北部表](../data/loan-readings-north.tsv)：13,018 个汉字，含多音候选。
- [南部表](../data/loan-readings-south.tsv)：13,023 个汉字，含多音候选。
- 两表均为 UTF-8 TSV，列为“汉字、调号拼音、IPA、分义”；不含来源或推导列。
- CLI 读取同一份压缩 JSON 映射表，仅依赖 Python 标准库。多音候选的优先级已离线确定。

```bash
python3 scripts/lookup-loan.py 朵 --target north
python3 scripts/lookup-loan.py 珙 --target north
python3 scripts/lookup-loan.py 难 --target north --sense 患难
python3 scripts/lookup-loan.py 难 --target north --choices '{"0":"lán"}'
```

`resolved` 返回整词拼音和 IPA；`needs-selection` 返回最终读音候选，可按语境或 `--choices` 选择；`missing-character` 表示至少一字无映射，整词只保留汉字，不输出部分读音。`--choices` 选择最终拼音或 IPA，运行时不使用诸如 `lan5` 的来源记音。

## 离线整理

原有字音优先：北部永顺→吉首，南部解放岩→吉首；保留分义和文白等候选。北部 i/y 及其介音前保留 n/l，ian/iang/üan/üang 合并为 iã，t/tʰ/d/l 后的 in 对应 ɜ̃ 等既定规则均在构建时应用。运行时不执行这些规则。

缺字依次从下列同音组补齐：

| 资料 | 采用范围 |
| --- | --- |
| 小学堂《洪武正韵》 | 按声调、清浊及小学堂拟音分组；主表 14,561 条、10,591 种字形字符串，其中 10,575 个单字可直接作为 Unicode 字键。 |
| 韵典网《洪武正韵牋》 | 正文字头及小韵编号；不读取另列的古音、逸字和释义。 |
| 汉字音典《蒙古字韵》 | 完整拟音及调类；不把入声与同形阴声韵混为一组。 |
| 汉字音典《中原音韵》 | 第一套完整拟音及调类；不混合多套拟音方案。 |

只用原有表中已能明确选读的字作参照，不把本次补出的字继续当参照。参照字在相应韵书有多个读音组时，跳过该参照字，避免把“捶／揣”现代常读误用于其《洪武正韵》的都火切异读。相互独立的参照字多数一致时采用该音，票数相同则保留多个候选；保留原字的既有读音。

例如“朵”经《蒙古字韵》与直接记录的“朶”对应，得到北部 dò；“珙”以同组“拱、鞏”的一致读音得到 gòng。

小学堂官方提供的批量声韵下载按 PDM 发布。此构建使用保留其字号、主表、又音、又切及拟音表的公开 Excel 副本；官方原包因当前 IP 封锁未取得，未声称已逐字节比对。副本地址、版本、散列和各资料范围见 `data/loan-sources/historical-source-manifest.json`。原始方言字表的 MCPDict MIT 声明保留于 `UPSTREAM-LICENSE`。

## 构建与验证

```bash
python3 -m pip install -e '.[loan-build]'
python3 scripts/build-loan-table.py
python3 scripts/build-loan-readings.py
python3 -m pytest tests/test_loan_lookup.py -q
```

`loan_build.py`、`characters.json.gz` 和 `rules.json` 只用于离线构建。历史同音分组事实在 `historical-homophones.json.gz`，逐字整理记录在 `homophone-build-audit.json.gz`，数量和散列在 `compiled-readings-summary.json`。这些都不是运行依赖；运行只读取 `readings.json.gz`。

输出采用固定排序和 gzip 时间戳，可重复构建。CI 检查测试和生成表一致性。个人技能附带相同读音表及独立查询脚本。
