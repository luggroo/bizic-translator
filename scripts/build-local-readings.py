"""Package modern Jishou readings and additional Chongqing readings with source rows."""
import csv
import gzip
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tujia_lex.loan_build import map_reading

SOURCES = ROOT / "data/loan-sources"
TONE_MARKS = frozenset("\u0300\u0301\u0304\u030c")


def keyboard_forms(city, ipa):
    segment = ipa.rstrip("0123456789")
    tone = ipa[len(segment):]
    segment = segment.lstrip("·")
    if city == "chongqing":
        segment = segment.replace("ɑ", "a")
    mapped = map_reading([city, segment + "1", "", ""], "north")
    if not mapped:
        return None, None
    decomposed = unicodedata.normalize("NFD", mapped["romanization"])
    key = unicodedata.normalize("NFC", "".join(c for c in decomposed if c not in TONE_MARKS))
    toned = map_reading([city, segment + tone, "", ""], "north") if tone else None
    return key, toned["romanization"] if toned else None


def book_rows(path):
    with path.open(encoding="utf-8") as stream:
        for line, row in enumerate(csv.DictReader(stream, delimiter="\t"), 2):
            for register, column in (("白", "colloquial"), ("文", "literary")):
                readings = row[column].split("|")
                examples = row[column + "Example"].split("|")
                for i, ipa in enumerate(readings):
                    # A second reading without a separate aligned example does
                    # not inherit one unless the author gives a common use.
                    note = examples[i] if i < len(examples) else ""
                    yield dict(city="jishou", source="li2002", line=line, page=int(row["page"]),
                               graph=row["graph"], ipa=ipa, register=register, note=note,
                               comment=row["comment"])


def build():
    simple, traditional = OpenCC("t2s"), OpenCC("s2t")
    sources = json.loads((SOURCES / "register-sources.json").read_text(encoding="utf-8"))
    characters = defaultdict(list)
    def add(row):
        graph = row["graph"]
        row["key"], row["north_spelling"] = keyboard_forms(row["city"], row["ipa"])
        for char in {graph, simple.convert(graph), traditional.convert(graph)}:
            if len(char) == 1:
                characters[char].append(row)

    book = SOURCES / "jishou-li-2002.tsv"
    if hashlib.sha256(book.read_bytes()).hexdigest() != sources["li2002"]["sha256"]:
        raise ValueError("Transcribed book evidence differs from its manifest")
    for row in book_rows(book):
        add(row)
    for city in ("jishou", "chongqing"):
        path = SOURCES / (city + ".tsv")
        if hashlib.sha256(path.read_bytes()).hexdigest() != sources[city]["sha256"]:
            raise ValueError(f"Source snapshot mismatch for {city}")
        with path.open(encoding="utf-8") as stream:
            for line, fields in enumerate(csv.reader(stream, delimiter="\t"), 1):
                graph = fields[0]
                if len(graph) != 1 or graph == "□":
                    continue
                ipa, note = fields[1:3]
                tagged = re.search(r"(?:^|[,，;；])([文白])(?:读|讀|音)?(?=$|[,，;；:：])", note)
                register = tagged[1] if tagged else ""
                add(dict(city=city, source=city, graph=graph, ipa=ipa, register=register,
                         note=note, line=line))
    payload = dict(sources=sources, characters=characters)
    packed = gzip.compress(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8"), mtime=0)
    for parent in (ROOT / "src/tujia_lex/loan_data", ROOT / "skills/translate-tujia/assets"):
        (parent / "local-readings.json.gz").write_bytes(packed)
    print(f"{len(characters)} character keys, {len(packed)} bytes")


if __name__ == "__main__":
    build()
