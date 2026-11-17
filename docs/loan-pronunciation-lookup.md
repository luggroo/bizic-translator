# 汉借词离线补音

先查询土家语词库，已有词项采用原记音。本工具用于词库缺项、新拟汉借词的补音，不表示该借词已在土家语中得到记录。

```
python3 scripts/lookup-loan.py 圆珠笔 --target north
python3 scripts/lookup-loan.py 军 --target south
python3 scripts/lookup-loan.py 难 --target north --sense 患难
python3 scripts/lookup-loan.py 难 --target north --choices '{"0":"lan5"}'
```

运行只需Python标准库，无网络或模型依赖。北部用永顺→吉首，南部用解放岩→吉首。保留原音、来源、分义及转换记录；按语境提示匹配原表分义，也可用从0开始的字位置和原始记音明确选读。未注明意义的多音不按第一条猜读。

只要一字在两表均缺，整词只留汉字，ipa和romanization均为null；不标部分字音。多音未定、声韵无法映射时同样不输出整词发音，候选只作内部消歧。

## 对应约定

- 北部调类阴平／阳平／上声／去声→55／21／51／24；南部→33／21／55／13。吉首去声编号5，解放岩编号4。
- 北部浊塞音、浊塞擦音改送气，y→i，an/aŋ合并为ã；in与ɛn/ən分为ĩ与ɜ̃；永顺ɛ→ei；io→iau，整韵匹配。
- 北部f/hu拼写统一hu，源IPA仍保留，不把原f一律伪写为x。
- 南部解放岩ɛi→ai，古入声字取ei；əɯ统一ɯ；军对应ỹ；保留浊音及y。
- 完整映射在src/tujia_lex/loan_data/rules.json。此前两候选条目未另指定的，以首个候选作补音默认。ɚ与ɛ˞尚无唯一对应，保留未解决状态。

## 来源与构建

永顺、吉首原表取MCPDict提交1f0809e2e16804de703300d00fb544971bbccb6e，随附原许可证。解放岩仅提取[用户提供比较表](https://docs.google.com/spreadsheets/d/14fu7gGShQaebYwx2KkqXhttrqw7yZNpM/edit)中的字、解放岩读音、中古声调。原始数据在data/loan-sources。用户授权将这些提取数据发布到本公开仓库。

重建：python3 scripts/build-loan-table.py。仅重建需要opencc-python-reimplemented生成简繁别名；运行时不需要。压缩表包含输入SHA256；固定排序和gzip时间戳保证可复现。
