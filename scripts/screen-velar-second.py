#!/usr/bin/env python3
"""Cross-index attested Guangyun readings against two survey points and the supplied book pages."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from importlib.resources import files
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/loan-sources"
OUT = SOURCE / "velar-second"
GY_SHA = "f2b66197355d4fbff0776ab34e4aece817363b00446fbcf08e2f1677a7ac0c5f"
INITIALS = "見溪羣疑影曉匣云"
SHE = {"麻": "假", "耕": "梗", "庚": "梗", "皆": "蟹", "佳": "蟹", "夬": "蟹", "肴": "效",
       "刪": "山", "山": "山", "江": "江", "咸": "咸", "銜": "咸"}
FOCUS = "家加架嫁稼解介教窖觉减鉴谏夹甲艰间讲降确敲牙芽哑桠压咬颜眼雁虾下狭陷衔项巷行街鞋阶皆界瞎匣角"
COLS = ("guangyun_line", "small_rhyme", "entry_no", "head_source", "head", "simple_key", "initial", "initial_series",
        "openness", "division", "rhyme_heading", "rhyme_class", "she", "tone", "position", "fanqie", "old_gloss",
        "phonetic_component", "book_pages", "book_comparison", "book_pairs", "jishou_readings", "chongqing_readings",
        "jishou_register", "chongqing_register", "evidence", "review")
REGISTER = re.compile(r"(?:^|[,，;；])([文白])(?:读|讀|音)?(?=$|[,，;；:：])")
POSITION = re.compile(r"^([見溪羣疑影曉匣云])([開合]?)二(.)[平上去入]$")
BOOK_CLASS = re.compile(r"^(.)([开合]?)二(.)母$")
TRAD = str.maketrans("见晓群云开", "見曉羣云開")


def tsv_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def grouped(rows, key):
    out = defaultdict(list)
    for row in rows:
        out[row[key]].append(row)
    return out


class Graphs:
    """Direct and reversible traditional/simplified spellings; ambiguous folds are leads only."""
    def __init__(self):
        resources = files("opencc").joinpath("dictionary")
        self.tables = {}
        for name in ("TS", "ST"):
            rows = resources.joinpath(name + "Characters.txt").read_text(encoding="utf-8").splitlines()
            self.tables[name] = {r[0]: tuple(r[1].split()) for line in rows if line and not line.startswith("#")
                                 if len(r := line.split("\t")) == 2}
        self.reverse = defaultdict(set)
        for source, alternatives in self.tables["TS"].items():
            for target in alternatives:
                if len(source) == len(target) == 1:
                    self.reverse[target].add(source)

    def simple(self, head):
        return self.tables["TS"].get(head, (head,))[0]

    def options(self, head):
        if len(head) != 1:
            return {head: "同字"}
        simple = self.simple(head)
        names = {head, simple, *self.tables["TS"].get(head, ()), *self.tables["ST"].get(simple, ()), *self.reverse[simple]}
        result = {}
        for name in names:
            if len(name) != 1:
                continue
            if name == head:
                result[name] = "同字"
            elif any(simplified in self.tables["TS"].get(traditional, ()) and
                     (self.reverse[simplified] | set(self.tables["ST"].get(simplified, ()))) == {traditional}
                     for simplified, traditional in ((head, name), (name, head))):
                result[name] = "简繁单一对应"
            else:
                result[name] = "简繁歧义线索"
        return result

    def reading_options(self, head, position):
        if head == "閒" and position in {"見開二山平", "見開二山去"}:
            # Guangyun #556 "中閒", #2685 "隔也". See also MOE/Guoyu Cidian, 閒 (jiān/jiàn).
            # Modern 閑/闲 'idle' is a different lexical correspondence, despite its OpenCC key.
            return {"閒": "同字", "間": "按义异体（中间、间隔）", "间": "按义异体（中间、间隔）"}
        if head == "齩" and position == "疑開二肴上":
            # MOE Revised Mandarin Dictionary: 齩 is a variant of 咬. Guangyun: 齩 "齧也".
            return {"齩": "同字", "咬": "按义异体（用齿咬）"}
        return self.options(head)


def corrected_head(raw):
    # Upstream build.py: replace the mistaken character before 〈〉 by its correction.
    return re.sub(r".〈([^〈〉]+)〉", r"\1", raw)


def source_records(city):
    result = defaultdict(list)
    with (SOURCE / (city + ".tsv")).open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream, delimiter="\t")
        next(rows)
        for no, row in enumerate(rows, 2):
            head, ipa, note = row[:3]
            if len(head) == 1 and head != "□":
                m = REGISTER.search(note)
                result[head].append(dict(line=no, graph=head, ipa=ipa, note=note, register=m[1] if m else ""))
    return result


def cross(index, options):
    rows = [dict(row, match=how) for name, how in options.items() for row in index.get(name, ())]
    return sorted(rows, key=lambda r: (int(r.get("page", 0)), int(r.get("seq", r.get("line", 0)))))


def certain(rows):
    return [r for r in rows if r["match"] != "简繁歧义线索"]


def reg_summary(rows):
    rows = certain(rows)
    lit = {r["ipa"] for r in rows if r["register"] == "文"}
    col = {r["ipa"] for r in rows if r["register"] == "白"}
    if any(a != b for a in lit for b in col):
        return "同一地点字表分别标文、白（音异）"
    if lit and col:
        return "同一地点字表分别标文、白（同记音）"
    if lit or col:
        return "字表标" + ("文" if lit else "白") + "；另一层待查"
    n = len({r["ipa"] for r in rows})
    return "同地多音，原表未标文白" if n > 1 else "单音，原表未标文白" if n else ""


def onset(ipa):
    if ipa.startswith(("k", "ɡ", "g", "ŋ", "x", "ɣ")):
        return "后部声母"
    if ipa.startswith(("tɕ", "dʑ", "ɕ", "ʑ", "ȵ")):
        return "舌面音"
    if ipa.startswith(("i", "y", "j", "ɥ")):
        return "前高元音或介音起首"
    return "其他"


def alternates(rows):
    classes = {onset(r["ipa"]) for r in certain(rows)}
    return "后部声母" in classes and bool(classes & {"舌面音", "前高元音或介音起首"})


def match_book(row, info):
    if not row["mc"]:
        return "书中未注中古音类"
    match = BOOK_CLASS.fullmatch(row["mc"])
    if not match:
        return "书注另一个等第或音类"
    she, openness, initial = (s.translate(TRAD) for s in match.groups())
    if initial != info["initial"] or she != info["she"]:
        return "书注与此小韵音类不同"
    if info["openness"] in {"開", "合"} and openness and openness != info["openness"]:
        return "书注开合与此小韵不同"
    if row["match"] == "简繁歧义线索":
        return "书注声母、等第、摄相合（简繁多指，须对字义）"
    if row["graph"] == "间" and info["head"] == "閒":
        for phrase, tone in (("中～", "平"), ("～隔", "去")):
            if phrase in (row["colloquialExample"], row["literaryExample"]):
                return ("书注声母、等第、摄相合（古释与书例相应）" if info["tone"] == tone
                        else "书注音类可合，本书用例宜对同字另读")
    return "书注声母、等第、摄相合"


def compact_readings(rows):
    return " ｜ ".join(f"{r['graph']} {r['ipa']}" + ("（" + r["note"] + "）" if r["note"] else "") +
                      f"〔L{r['line']}，{r['match']}〕" for r in rows)


def screen(gy, dialects, book, components, graphs):
    output, details = [], []
    for line, word in enumerate(gy, 2):
        pos = word["音韻地位"]
        m = POSITION.fullmatch(pos)
        if not m:
            continue
        initial, openness, rhyme = m.groups()
        source_head = word["字頭"]
        head = corrected_head(source_head)
        options = graphs.reading_options(head, pos)
        info = dict(guangyun_line=line, small_rhyme=word["小韻號"], entry_no=word["小韻字號"], head_source=source_head,
                    head=head, simple_key=graphs.simple(head), initial=initial, initial_series="牙音" if initial in "見溪羣疑" else "喉音",
                    openness=openness, division="二", rhyme_heading=word["韻目原貌"], rhyme_class=rhyme, she=SHE[rhyme],
                    tone=pos[-1], position=pos, fanqie=word["反切"], old_gloss=word["釋義"])
        local = {city: cross(idx, options) for city, idx in dialects.items()}
        js, cq = local["jishou"], local["chongqing"]
        brackets = cross(book, options)
        for row in brackets:
            row["class_comparison"] = match_book(row, info)
        js_reg, cq_reg = reg_summary(js), reg_summary(cq)
        outside = not brackets
        review = ""
        if outside:
            if any(reg.startswith("同一地点字表分别标文、白（音异") for reg in (js_reg, cq_reg)):
                review = "书页之外：单点有文白双标"
            elif alternates(js) or alternates(cq):
                review = "书页之外：同点两组声形，可分义复核"
            elif certain(js) and certain(cq) and alternates(js + cq):
                review = "书页之外：跨点声形对照，需同点复核"
            elif any(reg.startswith("字表标") for reg in (js_reg, cq_reg)):
                review = "书页之外：单点仅标一层"
        attested = [city for city, rows in (("吉首", js), ("重庆", cq)) if certain(rows)]
        evidence = "、".join(attested) + "字表有录" if attested else "无确切同形测点记录"
        if brackets:
            evidence += "；吉首书页有例（音类见对照栏）"
        phonic = components.get(source_head, ())
        component_text = []
        for r in phonic:
            label = r["phonetic"] + r.get("wording", "")
            component_text.append(f"{r['source_glyph']}→{label}〔{r['source']} L{r['source_line']}〕")
        info.update(phonetic_component=" ｜ ".join(component_text),
                    book_pages="；".join(f"p{r['page']}#{r['seq']} {r['graph']}" for r in brackets),
                    book_comparison="；".join(f"p{r['page']}#{r['seq']} {r['mc'] or '未注'}｜{r['class_comparison']}" for r in brackets),
                    book_pairs=" ｜ ".join(f"p{r['page']}#{r['seq']} 白 {r['colloquial']}（{r['colloquialExample']}）；文 {r['literary']}（{r['literaryExample']}）" for r in brackets),
                    jishou_readings=compact_readings(js), chongqing_readings=compact_readings(cq),
                    jishou_register=js_reg, chongqing_register=cq_reg, evidence=evidence, review=review)
        output.append(info)
        details.append(dict(guangyun_line=line, head=head, position=pos, book=brackets, **local, components=phonic))
    return output, details


def write_table(rows, columns):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def compress_json(records):
    target = io.BytesIO()
    with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as stream:
        stream.write(json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode())
    return target.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare all generated files with the checked-in versions")
    args = parser.parse_args()
    raw = gzip.decompress((OUT / "guangyun.csv.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != GY_SHA:
        raise SystemExit("Unexpected Guangyun edition")
    gy = list(csv.DictReader(io.StringIO(raw.decode())))
    graphs = Graphs()
    dialects = {city: source_records(city) for city in ("jishou", "chongqing")}
    book = grouped(tsv_rows(SOURCE / "jishou-li-2002.tsv"), "graph")
    components = defaultdict(list)
    for name, source in (("phonetic-components-shuowen.tsv", "說文"), ("phonetic-components.tsv", "MMH")):
        for item in tsv_rows(OUT / name):
            components[item["guangyun_head"]].append(dict(source=source, **item))
    rows, details = screen(gy, dialects, book, components, graphs)
    extra = [r for r in rows if r["review"]]
    source_index = grouped(gy, "字頭")
    focus_index = defaultdict(list)
    for row in rows:
        for graph, link in graphs.reading_options(row["head"], row["position"]).items():
            focus_index[graph].append((row, link))
    focus = []
    for query in FOCUS:
        options = graphs.options(query)
        selected = focus_index[query]
        if selected:
            for r, link in selected:
                focus.append(dict(query=query, glyph_link=link, **r))
        else:
            classes = sorted({w["音韻地位"] for char in options for w in source_index.get(char, ())})
            rec = dict.fromkeys(COLS, "")
            rec.update(head=query, position="；".join(classes), evidence="未匹配此组二等小韵")
            focus.append(dict(query=query, glyph_link="字形检索", **rec))
    count = dict(source_rows=len(gy), rows=len(rows), source_heads=len({r["head_source"] for r in rows}),
                 corrected_heads=len({r["head"] for r in rows}), initials={c:sum(r["initial"] == c for r in rows) for c in INITIALS},
                 dialects={c:len({d["head"] for d in details if certain(d[c])}) for c in dialects},
                 dialect_graphs_in_both=len({d["head"] for d in details if all(certain(d[c]) for c in dialects)}),
                 direct_book_class=sum("书注声母、等第、摄相合" in r["book_comparison"] for r in rows),
                 external=dict(sorted(Counter(r["review"] for r in extra).items())),
                 external_heads={typ: sorted({r["head"] for r in extra if r["review"] == typ})
                                 for typ in sorted({r["review"] for r in extra})}, focus_queries=len(FOCUS),
                 phonetic_heads=len({r["head_source"] for r in rows if r["phonetic_component"]}))
    products = {"screen.tsv":write_table(rows, COLS), "beyond-pages.tsv":write_table(extra, COLS),
                "focus.tsv":write_table(focus, ("query", "glyph_link", *COLS)),
                "observations.json.gz":compress_json(details),
                "summary.json":(json.dumps(count, ensure_ascii=False, indent=2) + "\n").encode()}
    for name, payload in products.items():
        path = OUT / name
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                raise SystemExit(f"Out of date: {name}")
        else:
            path.write_bytes(payload)
    print(json.dumps(count, ensure_ascii=False))


if __name__ == "__main__":
    main()
