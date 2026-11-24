import csv
import gzip
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
PRODUCTS = SOURCE / "velar-second"


def table(name):
    with (PRODUCTS / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_all_scoped_guangyun_entries_keep_edition_and_number():
    raw = gzip.decompress((PRODUCTS / "guangyun.csv.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == "f2b66197355d4fbff0776ab34e4aece817363b00446fbcf08e2f1677a7ac0c5f"
    original = list(csv.DictReader(io.StringIO(raw.decode())))
    # Independent coverage check without using the builder's regex or its normalization.
    heads = enumerate(original, start=2)
    expected = {str(line): r for line, r in heads if r["音韻地位"].startswith(tuple("見溪羣疑影曉匣云")) and "二" in r["音韻地位"]}
    rows = table("screen.tsv")
    assert len(rows) == len(expected) == 1573
    assert set(expected) == {r["guangyun_line"] for r in rows}
    for r in rows:
        entry = expected[r["guangyun_line"]]
        assert (r["small_rhyme"], r["entry_no"], r["head_source"], r["position"], r["rhyme_heading"], r["fanqie"]) == (
            entry["小韻號"], entry["小韻字號"], entry["字頭"], entry["音韻地位"], entry["韻目原貌"], entry["反切"])
    bad_head = next(r for r in rows if r["head_source"] == "膠〈𥉾〉")
    assert bad_head["head"] == "𥉾" and not bad_head["jishou_readings"]
    assert any(r["head"] == "⿰隺犬" and not r["chongqing_readings"] for r in rows)
    assert Counter(r["initial"] for r in rows) == {"見":450, "溪":205, "疑":117, "影":209, "曉":175, "匣":417}


def test_book_sources_preserve_sound_register_and_head_senses():
    rows = table("focus.tsv")
    focus = {(r["query"], r["head"], r["position"]):r for r in rows}
    assert len({r["query"] for r in rows}) == 46 and all(r["guangyun_line"] for r in rows)
    frame = focus["架","架","見開二麻去"]
    assert "白 ka5（十字～儿）" in frame["book_pairs"] and "文 tɕia5（吵～）" in frame["book_pairs"]
    assert "tɕia5" not in frame["jishou_readings"] and "另一层待查" in frame["jishou_register"]
    assert "tɕia5" in frame["chongqing_readings"] and "原表未标文白" in frame["chongqing_register"]
    assert "咸开二见母" in focus["谏","諫","見開二刪去"]["book_comparison"]
    assert "音类不同" in focus["虾","蝦","匣開二麻平"]["book_comparison"]
    assert "相合" in focus["确","確","溪二江入"]["book_comparison"]
    assert "相合" not in focus["确","确","匣二江入"]["book_comparison"]
    assert "按义异体" in focus["咬","齩","疑開二肴上"]["glyph_link"]
    assert "相合" in focus["咬","齩","疑開二肴上"]["book_comparison"]
    assert "相合" not in focus["咬","咬","見開二肴平"]["book_comparison"]
    for tone, seq in (("平",21), ("去",22)):
        row = focus["间","閒","見開二山" + tone]
        assert "按义异体" in row["glyph_link"] and "閑" not in row["jishou_readings"]
        assert f"p39#{seq} 山开二见母｜书注声母、等第、摄相合（古释与书例相应）" in row["book_comparison"]


def test_modern_wordlist_and_component_metadata_trace_to_individual_rows():
    rows = table("screen.tsv")
    details = json.loads(gzip.decompress((PRODUCTS / "observations.json.gz").read_bytes()))
    dialects = {}
    for city in ("jishou","chongqing"):
        with (SOURCE / (city + ".tsv")).open() as stream:
            dialects[city] = list(csv.reader(stream, delimiter="\t"))
    for r, item in zip(rows, details, strict=True):
        assert r["position"] == item["position"] and r["head"] == item["head"]
        for city, source in dialects.items():
            for record in item[city]:
                assert source[record["line"] - 1][:3] == [record["graph"],record["ipa"],record["note"]]
                if city == "chongqing":
                    assert record["register"] == ""
        for component in item["components"]:
            assert component["source_url"].endswith("#L" + str(component["source_line"]))
    new = table("beyond-pages.tsv")
    assert all(not r["book_pairs"] and r["review"] for r in new)
    assert {r["head"] for r in new if "双标" in r["review"]} == set("鞋懈虹跨")
    assert any(r["head"] == "角" and "元~分" in r["jishou_readings"] and "同点两组声形" in r["review"] for r in new)
    assert any(r["head"] == "瞎" and "跨点" in r["review"] for r in new)
    assert any(r["head"] == "家" and re.search("豭省聲〔說文", r["phonetic_component"]) for r in rows)
    lecture = next(r for r in rows if r["head"] == "講")["phonetic_component"]
    assert "講→冓" in lecture and "讲→井" in lecture
