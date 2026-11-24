import csv
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "data/loan-sources/velar-second"


def load(stem):
    with (BASE / f"{stem}.tsv").open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_component_records_retain_their_own_source_and_graph():
    modern = load("phonetic-components")
    classical = load("phonetic-components-shuowen")
    modern_heads = {r["guangyun_head"] for r in modern}
    classical_heads = {r["guangyun_head"] for r in classical}
    assert (len(modern_heads), len(classical_heads), len(modern_heads | classical_heads)) == (336, 515, 659)
    assert len({(r["guangyun_head"], r["source_glyph"]) for r in modern}) == len(modern)
    for rows, filename in ((modern, "dictionary.txt"), (classical, "swjz.xml")):
        assert all(r["source_url"].endswith(f"/{filename}#L{r['source_line']}") for r in rows)
        assert all(len(r["source_glyph"]) == 1 and r["phonetic"] for r in rows)
    assert all(r["source_id"].startswith("w") and r["wording"] in {"聲", "省聲", "亦聲"} for r in classical)
    assert not {"閒", "⿰隺犬"}.intersection(modern_heads | classical_heads)


def test_distinct_graphs_and_classical_analysis_are_preserved():
    modern = {(r["guangyun_head"], r["source_glyph"]): r["phonetic"]
              for r in load("phonetic-components")}
    classical = {r["guangyun_head"]: (r["source_glyph"], r["phonetic"], r["wording"])
                 for r in load("phonetic-components-shuowen")}
    assert modern["架", "架"] == "加"
    assert modern["講", "講"] == "冓"
    assert modern["講", "讲"] == "井"
    assert modern["家", "家"] == "豕"
    assert classical["家"] == ("家", "豭", "省聲")
    assert classical["壓"] == ("壓", "厭", "聲")
    assert classical["𢱈〈椵〉"] == ("椵", "叚", "聲")
