# 《广韵》见系二等字头的声旁

查这 1,380 个字头的声旁时，可以按《广韵》字头查两张表，再看该行引用的实际字形。现代字形资料覆盖 336 个字头，段注本《说文》覆盖 515 个。两表重合 192 个，合计 659 个。其余 721 个在本次选用的字段和原文句式中未查到。声旁能帮助比较同一组字的构形，方言读音和文白用法还要逐字查测点记录。

| 表 | 取证范围 | 怎么读 |
| --- | --- | --- |
| [现代字形](phonetic-components.tsv) | Make Me a Hanzi 的形声字条目明确标出声旁 | 一行对应一个有出处的字形。「講」标冓，「讲」标井。查到简体时，另列简体那条资料的行号。 |
| [段注本《说文》](phonetic-components-shuowen.tsv) | CJKVI《說文解字注》所载《说文》正文明确写出某字「聲」「省聲」或「亦聲」 | 保留字头、声符、原文用语与条目编号。「家」条作「豭省聲」，可与现代字形资料标出的「豕」分别查阅。 |

每行的 `guangyun_head` 保留《广韵》数据原有的校订符号。例如「𢱈〈椵〉」按校订字「椵」查到「叚聲」。`source_glyph` 是所引资料实收的字形。`source_url` 可定位到现代字形记录或段注本条目，古籍中的具体说解紧随字头。段注本表依据每个字头自己的正文提取，另字的说解、段玉裁注文和「读若」另有用途。[《广韵》校订数据](https://github.com/nk2028/tshet-uinh-data/tree/21585e22c8a730ca2fd175112f4d18e16d5ce578) · [「家」现代字形记录](https://github.com/skishore/makemeahanzi/blob/bddc96d41bef78427ed0e034e9f7e31d71fd1b92/dictionary.txt#L1811) · [段注本「家」](https://github.com/cjkvi/cjkvi-dict/blob/9b6e0a88bcccdfa36c6b96327a88fc900867276c/swjz.xml#L36064)

「中间」「间隔」的「间」另有字形依据。段注本「閒」训「隙」，以门、月会意。教育部《異體字字典》A04378-001 记载了「閒」与「間」在间隙义的关系。这里可以按义对照古今字，声旁仍应留空。[段注本「閒」](https://github.com/cjkvi/cjkvi-dict/blob/9b6e0a88bcccdfa36c6b96327a88fc900867276c/swjz.xml#L60898-L60905) · [《異體字字典》「閒（間）」](https://dict.variants.moe.edu.tw/dictView.jsp?ID=48012&la=0)

## 重建

在仓库根目录运行以下命令。脚本会逐份核验源文件摘要。OpenCC 只用于寻找可能的简体字形，声旁仍须能在来源中查到。

```sh
python3 -m pip install 'opencc-python-reimplemented==0.1.7'
curl -fL https://raw.githubusercontent.com/skishore/makemeahanzi/bddc96d41bef78427ed0e034e9f7e31d71fd1b92/dictionary.txt -o /tmp/mmh-dictionary.txt
curl -fL https://raw.githubusercontent.com/cjkvi/cjkvi-dict/9b6e0a88bcccdfa36c6b96327a88fc900867276c/swjz.xml -o /tmp/cjkvi-swjz.xml
python3 scripts/build-velar-components.py data/loan-sources/velar-second/guangyun.csv.gz /tmp/mmh-dictionary.txt --shuowen /tmp/cjkvi-swjz.xml
```

Make Me a Hanzi 字典数据采用 LGPL-3.0-or-later，CJKVI《說文解字注》XML 数据采用 GPL-2.0。后者据日本学术振兴会项目 14510494 的部分成果整理。两份摘录分别随附对应授权文件。[现代字形资料授权](phonetic-components-LICENSE.txt) · [CJKVI 资料授权](phonetic-components-shuowen-LICENSE.txt) · [CJKVI 项目说明](https://github.com/cjkvi/cjkvi-dict/blob/9b6e0a88bcccdfa36c6b96327a88fc900867276c/README.md)
