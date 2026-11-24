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
    if city == "chongqing":
        segment = segment.replace("ɑ", "a")
    mapped = map_reading([city, segment + "1", "", ""], "north")
    if not mapped:
        return None, None
    decomposed = unicodedata.normalize("NFD", mapped["romanization"])
    key = unicodedata.normalize("NFC", "".join(c for c in decomposed if c not in TONE_MARKS))
    toned = map_reading([city, segment + tone, "", ""], "north") if tone else None
    return key, toned["romanization"] if toned else None


def build():
    simple, traditional = OpenCC("t2s"), OpenCC("s2t")
    sources = json.loads((SOURCES / "register-sources.json").read_text(encoding="utf-8"))
    characters = defaultdict(list)
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
                key, marked = keyboard_forms(city, ipa)
                row = dict(city=city, graph=graph, ipa=ipa, register=register,
                           note=note, key=key, north_spelling=marked, line=line)
                for char in {graph, simple.convert(graph), traditional.convert(graph)}:
                    if len(char) == 1:
                        characters[char].append(row)
    payload = dict(sources=sources, characters=characters)
    packed = gzip.compress(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8"), mtime=0)
    for parent in (ROOT / "src/tujia_lex/loan_data", ROOT / "skills/translate-tujia/assets"):
        (parent / "local-readings.json.gz").write_bytes(packed)
    print(f"{len(characters)} character keys, {len(packed)} bytes")


if __name__ == "__main__":
    build()
