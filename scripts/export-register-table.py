"""Export the complete source register inventory and its underlying witnesses."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unique(items):
    return list(dict.fromkeys(value for value in items if value))


def tables():
    from opencc import OpenCC
    simplify = OpenCC("t2s")
    packed = ROOT / "src/tujia_lex/loan_data/local-readings.json.gz"
    data = json.loads(gzip.decompress(packed.read_bytes()))
    entry = {(r["city"], r["line"]): r for forms in data["characters"].values() for r in forms}
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
    return [
        ("文白原注", ["简体检索字", "原表字头", "标注情况", "文读键入", "白读键入", "文读原音", "白读原音", "文读原注", "白读原注",
                       "吉首其他原音", "重庆键入", "重庆原音（原表未标文白）", "吉首出处", "重庆出处"], labelled),
        ("其他多读", ["原表字头", "吉首各音", "重庆各音", "吉首原注", "重庆原注", "吉首出处", "重庆出处"], polyphones),
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
    guide.set_column(1, 1, 94)
    guide.write_row(0, 0, ["文白异读", "《汉字音典》吉首、重庆调查点"], head)
    guide.set_row(0, 33)
    guide_rows = [
        ("原表字头", "按原表字形汇总。繁简、异体可在 translate-tujia 查字。"),
        ("文白标记", "只有原注标明文或白的读音进入对应栏。重庆本次所用字表未标文白。"),
        ("原表记音", "末尾数字是各调查点的声调类别。如 ka5 是原表记音，5 表示调类。"),
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
            width = 13 if column in ("原表字头", "调查点", "原表行号", "文白标记") else 38 if "原注" in column else 24
            sheet.set_column(i, i, width)
        for j, row in enumerate(rows, 1):
            for i, value in enumerate(row):
                if isinstance(value, str) and value.startswith("https://"):
                    sheet.write_url(j, i, value, link_style, "查看原表第 " + value.rsplit("#L", 1)[1] + " 行")
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
