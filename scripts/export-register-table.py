"""Export the complete source register inventory and its underlying witnesses."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data/loan-sources"


def unique(items):
    return list(dict.fromkeys(value for value in items if value))


def chapter_evidence(data, simplify):
    groups = defaultdict(list)
    chapter = []
    with (SOURCES / "jishou-li-2002.tsv").open(encoding="utf-8") as stream:
        for line, record in enumerate(csv.DictReader(stream, delimiter="\t"), 2):
            graph = record["graph"]
            groups[simplify.convert(graph)].append((line, record))
            link = data["sources"]["li2002"]["url"] + "#L" + str(line)
            chapter.append([int(record["page"]), int(record["seq"]), graph, record["colloquial"],
                            record["colloquialExample"], record["literary"], record["literaryExample"],
                            record["mc"], record["type"], record["comment"], link])
    return groups, ("吉首原书逐条", ["书页", "页内次序", "字头", "白读原音", "白读原例", "文读原音",
             "文读原例", "原书所记音类", "原书分类", "校记", "转录出处"], chapter)


def combined_sheet(data, by_graph, chapter, simplify):
    local_rows = defaultdict(lambda: defaultdict(list))
    head_forms = defaultdict(list)
    for original, sites in by_graph.items():
        simple = simplify.convert(original)
        for city, rows in sites.items():
            for row in rows:
                local_rows[simple][city].append(row)
                if row[1]:
                    head_forms[simple].append(original)

    result = []
    for graph in sorted(set(chapter) | set(head_forms)):
        source_rows = data["characters"][graph]
        # Readings and their examples are kept together in each evidence cell.
        tagged = [r for r in source_rows if r["register"] and simplify.convert(r["graph"]) == graph]
        def side(tag, field):
            return " / ".join(unique(r[field] for r in tagged if r["register"] == tag))
        def examples(tag):
            cells = []
            for r in tagged:
                if r["register"] != tag or not r["note"] or r["note"] == tag:
                    continue
                note = r["note"].removeprefix(tag + ",").removeprefix(tag + "，")
                note = note.replace("～", r["graph"]).replace("~", r["graph"])
                label = f"吉首书 p{r['page']}" if r.get("page") else data["sources"][r["city"]]["label"] + "字表"
                cells.append(f"{r['ipa']} {note}〔{label}〕")
            return " ｜ ".join(unique(cells))
        book_rows = chapter.get(graph, [])
        head = unique([r["graph"] for _, r in book_rows] + head_forms.get(graph, []))
        pages = "、".join(unique(r["page"] for _, r in book_rows))
        book_url = data["sources"]["li2002"]["url"] + "#L" + str(book_rows[0][0]) if book_rows else ""
        jur, cqr = local_rows[graph]["jishou"], local_rows[graph]["chongqing"]
        state = "文白均有依据" if side("白", "ipa") and side("文", "ipa") else "仅标白" if side("白", "ipa") else "仅标文"
        sources = "、".join(unique("《吉首方言研究》" if r.get("page") else data["sources"][r["city"]]["label"] + "字表" for r in tagged))
        result.append([graph, " / ".join(head), state, side("白", "key"), side("文", "key"),
                       side("白", "ipa"), side("文", "ipa"), examples("白"), examples("文"),
                       sources, pages, " / ".join(unique(r[0] for r in jur)),
                       " / ".join(unique(r[0] for r in cqr)), book_url,
                       next((r[4] for r in jur if r[1]), jur[0][4] if jur else ""), cqr[0][4] if cqr else ""])
    return ("文白对照", ["简体检索字", "有文白依据的原字头", "标注情况", "白读键入", "文读键入", "白读原音",
            "文读原音", "白读用例与来源", "文读用例与来源", "文白依据", "书页", "吉首电子字表各音",
            "重庆电子字表各音（原表未标文白）", "书例转录出处", "吉首字表出处", "重庆字表出处"], result)


def screening_sheet(name, filename):
    columns = [("head_source", "广韵原字头"), ("head", "校订字头"), ("simple_key", "简体检索字"),
               ("initial", "中古声母"), ("initial_series", "牙音或喉音"), ("openness", "开合"),
               ("rhyme_heading", "韵目"), ("she", "摄"), ("tone", "声调"), ("position", "音韵地位"),
               ("fanqie", "反切"), ("book_pages", "原书页与条次"), ("book_comparison", "古今音类核对"),
               ("book_pairs", "原书白读与文读"), ("jishou_readings", "吉首原音及行号"),
               ("chongqing_readings", "重庆原音及行号"), ("jishou_register", "吉首字表标记"),
               ("chongqing_register", "重庆字表标记"), ("evidence", "地方材料收录情况"), ("review", "书页外复核"),
               ("phonetic_component", "声符出处"), ("small_rhyme", "小韵号"), ("entry_no", "小韵内序"),
               ("guangyun_line", "广韵底表行号")]
    with (SOURCES / "velar-second" / filename).open(encoding="utf-8") as stream:
        records = [[r[field] for field, _ in columns] for r in csv.DictReader(stream, delimiter="\t")]
    return name, [title for _, title in columns], records


def tables():
    from opencc import OpenCC
    simplify = OpenCC("t2s")
    packed = ROOT / "src/tujia_lex/loan_data/local-readings.json.gz"
    data = json.loads(gzip.decompress(packed.read_bytes()))
    entry = {(r["city"], r["line"]): r for forms in data["characters"].values() for r in forms
             if r.get("source", r["city"]) == r["city"]}
    by_graph = defaultdict(lambda: defaultdict(list))
    raw_rows = []
    for city in ("jishou", "chongqing"):
        source = data["sources"][city]
        with (ROOT / f"data/loan-sources/{city}.tsv").open(encoding="utf-8") as stream:
            for line, (graph, ipa, note) in enumerate(csv.reader(stream, delimiter="\t"), 1):
                if line == 1:
                    continue
                detail = entry.get((city, line), {})
                tag, key = detail.get("register", ""), detail.get("key") or ""
                link = source["url"] + "#L" + str(line)
                raw_rows.append([source["label"], line, graph, ipa, tag, note, key, link])
                if graph != "□":
                    by_graph[graph][city].append((ipa, tag, note, key, link))

    def sounds(rows):
        return " / ".join(unique(r[0] for r in rows))

    def uses(rows, tag):
        return "；".join(unique(r[2] for r in rows if r[2] and r[2] != tag))

    def keys(rows):
        return " / ".join(unique(r[3] for r in rows))

    labelled, polyphones, comparison = [], [], []
    for graph, sites in sorted(by_graph.items()):
        j, c = sites["jishou"], sites["chongqing"]
        tagged = [r for r in j + c if r[1]]
        j_link = j[0][4] if j else ""
        c_link = c[0][4] if c else ""
        if tagged:
            lit = [r for r in tagged if r[1] == "文"]
            col = [r for r in tagged if r[1] == "白"]
            status = "文白均有原注" if lit and col else "仅标文" if lit else "仅标白"
            labelled.append([simplify.convert(graph), graph, status, keys(lit), keys(col), sounds(lit),
                             sounds(col), uses(lit, "文"), uses(col, "白"),
                             sounds([r for r in j if not r[1]]), keys(c), sounds(c), j_link, c_link])
        elif len(set(r[0] for r in j)) > 1 or len(set(r[0] for r in c)) > 1:
            polyphones.append([graph, sounds(j), sounds(c), uses(j, ""), uses(c, ""), j_link, c_link])
        if j and c:
            comparison.append([graph, sounds(j), sounds(c), j_link, c_link])
    chapter, detailed = chapter_evidence(data, simplify)
    return [
        combined_sheet(data, by_graph, chapter, simplify), detailed,
        screening_sheet("二等书页外线索", "beyond-pages.tsv"),
        screening_sheet("二等牙喉音逐条", "screen.tsv"),
        ("音典文白原注", ["简体检索字", "原表字头", "标注情况", "文读键入", "白读键入", "文读原音", "白读原音", "文读原注", "白读原注",
                       "吉首其他原音", "重庆键入", "重庆原音（原表未标文白）", "吉首出处", "重庆出处"], labelled),
        ("音典未标多读", ["原表字头", "吉首各音", "重庆各音", "吉首原注", "重庆原注", "吉首出处", "重庆出处"], polyphones),
        ("两地对照", ["原表字头", "吉首各音", "重庆各音", "吉首出处", "重庆出处"], comparison),
        ("全部原始行", ["调查点", "原表行号", "原表字头", "原表记音", "文白标记", "原注", "北部键盘检索音", "原表出处"], raw_rows),
    ]


def workbook(path, sheets):
    import xlsxwriter
    book = xlsxwriter.Workbook(path, {"strings_to_formulas": False, "strings_to_urls": False})
    # Timestamp of the pinned MCPDict source revision for reproducible downloads.
    book.set_properties({"created": datetime(2026, 11, 24, 15, 3, 8)})
    head = book.add_format({"bg_color": "#893728", "font_color": "#FFFFFF", "bold": True,
                            "font_size": 12, "valign": "vcenter"})
    body = book.add_format({"font_size": 12, "valign": "vcenter"})
    link_style = book.add_format({"font_color": "#884029", "underline": 1, "font_size": 11})
    guide = book.add_worksheet("读表")
    guide.set_column(0, 0, 22)
    guide.set_column(1, 1, 115)
    guide.write_row(0, 0, ["吉首文白异读", "李启群《吉首方言研究》与《汉字音典》吉首、重庆字表"], head)
    guide.set_row(0, 33)
    guide_rows = [
        ("文白对照", "每个简体检索字一行。白读、文读分别列原音和键盘写法。单侧有据的字保留另一侧的空格。"),
        ("书页", "李启群《吉首方言研究》，民族出版社，2002 年，第 37–40 页。原书左列白读，右列文读。导文四例也收入。"),
        ("同字分行", "在「吉首原书逐条」找到每组音和各自的用例。「间」有两行，「解」跨两页涉及两组对照。竖线在同一格中分隔并列读音。"),
        ("文白标记", "《汉字音典》吉首有文白标记。重庆这份字表只有读音和用例。单地多音、两地音差和中古音类各在筛查页注明。"),
        ("二等牙喉音", "逐条列《广韵》二等见、溪、群、疑及影、晓、匣等母。每条保留反切和原表行号。阙载、异体歧义和待核的分义可按列筛查。"),
        ("线索的用法", "如「鞋」的两读在吉首字表有文白原注。「皆」在吉首、重庆各有一音，需同一地点的用例才能判定文白。韵书中同一个字可属于多个小韵。"),
        ("原表记音", "末尾数字表示调查点调类。如吉首 ka5 为去声。书中调符换写成同一调类数字，轻声点照录。"),
        ("用例", "原注中的 ~ 指这一行的字头。如「白,葡萄~」指「葡萄架」。"),
        ("北部键盘检索音", "只用于键盘查找。原表记音另列。缺少已定义映射的格子留空。"),
        ("查字顺序", "先查吉首，再用重庆补缺少的读音。两地不同读法在「两地对照」中并列。"),
    ]
    counts = {name: len(rows) for name, _, rows in sheets}
    guide_rows += [(name, f"{counts[name]:,} 行") for name, _, _ in sheets]
    for i, values in enumerate(guide_rows, 1):
        guide.write_row(i, 0, values, body)
        guide.set_row(i, 25)
    for name, columns, rows in sheets:
        sheet = book.add_worksheet(name)
        sheet.freeze_panes(1, 1)
        sheet.autofilter(0, 0, len(rows), len(columns) - 1)
        sheet.set_default_row(22)
        sheet.set_row(0, 32)
        sheet.write_row(0, 0, columns, head)
        for i, column in enumerate(columns):
            width = 13 if column in ("简体检索字", "原表字头", "调查点", "原表行号", "书页", "字头", "页内次序", "文白标记") else 56 if any(word in column for word in ("用例与来源", "白读与文读", "读原例", "校记", "原音及行号")) else 35 if "原注" in column else 23
            sheet.set_column(i, i, width)
        for j, row in enumerate(rows, 1):
            for i, value in enumerate(row):
                if isinstance(value, str) and value.startswith("https://"):
                    label = "查看出处"
                    if "#L" in value:
                        label = "第 " + value.rsplit("#L", 1)[1] + " 行"
                    sheet.write_url(j, i, value, link_style, label)
                else:
                    sheet.write(j, i, value, body)
    book.close()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--tsv", type=Path, help="Table of all explicitly marked headwords")
    cli.add_argument("--xlsx", type=Path, help="Full workbook, including every raw source row")
    args = cli.parse_args()
    sheets = tables()
    if args.tsv:
        with args.tsv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(sheets[0][1])
            writer.writerows(sheets[0][2])
    if args.xlsx:
        workbook(args.xlsx, sheets)
    print(", ".join(f"{name} {len(rows)}" for name, _, rows in sheets))
