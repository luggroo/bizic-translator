#!/usr/bin/env python3
"""Index directly labelled phonetic components for the Guangyun Division II velar/laryngeal survey."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from importlib.metadata import version
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
GY_SHA = "f2b66197355d4fbff0776ab34e4aece817363b00446fbcf08e2f1677a7ac0c5f"
MMH_REV = "bddc96d41bef78427ed0e034e9f7e31d71fd1b92"
MMH_SHA = "744bb05d5b0742e9ee35c37791f94d56a173349b3367569e7ca11e510364d203"
MMH_URL = f"https://github.com/skishore/makemeahanzi/blob/{MMH_REV}/dictionary.txt"
SW_SHA = "a3705e25dca84304069b35c4eecf97f486f1a2dacc7489375c8a4a6b4e3c8c4a"
SW_URL = "https://github.com/cjkvi/cjkvi-dict/blob/9b6e0a88bcccdfa36c6b96327a88fc900867276c/swjz.xml"
INITIALS = set("見溪羣疑影曉匣")
FIELDS = ["guangyun_head", "source_glyph", "glyph_match", "phonetic", "source_line", "source_url"]
HAN = r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U000323af]"
EXPLICIT_SOUND = re.compile(rf"(?:[。；，、]|[从從]{HAN})({HAN})(省聲|亦聲|聲)(?=[。；，、]|$)")


def verified(path, expected):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"{path}: expected {expected}, got {actual}")
    return path


def survey_heads(guangyun):
    raw = guangyun.read_bytes()
    if guangyun.suffix == ".gz":
        raw = gzip.decompress(raw)
    if hashlib.sha256(raw).hexdigest() != GY_SHA:
        raise ValueError(f"{guangyun}: unexpected Guangyun revision")
    return sorted({row["字頭"] for row in csv.DictReader(io.StringIO(raw.decode("utf-8")))
                   if row["音韻地位"][:1] in INITIALS and "二" in row["音韻地位"]})


def glyphs(head, converter):
    # qieyun-data's editorial sign A〈B〉 replaces A with B. IDS is left unresolved.
    correction = re.fullmatch(r".〈(.)〉", head)
    if correction:
        base, status = correction.group(1), "校订字"
    elif len(head) == 1:
        base, status = head, "原字形"
    else:
        return
    yield base, status
    modern = converter.convert(base)
    if len(modern) == 1 and modern != base:
        yield modern, status + "的简体"


def collect(gy_file, mmh_file):
    converter = OpenCC("t2s")
    if version("opencc-python-reimplemented") != "0.1.7":
        raise ValueError("Rebuild with opencc-python-reimplemented==0.1.7")
    phonetics = {}
    with verified(mmh_file, MMH_SHA).open(encoding="utf-8") as stream:
        for line, entry in enumerate(map(json.loads, stream), 1):
            etymology = entry.get("etymology") or {}
            if etymology.get("type") == "pictophonetic" and etymology.get("phonetic"):
                phonetics[entry["character"]] = (etymology["phonetic"], line)
    rows = []
    for head in survey_heads(gy_file):
        for graph, status in glyphs(head, converter):
            if graph in phonetics:
                phonetic, line = phonetics[graph]
                rows.append((head, graph, status, phonetic, line, f"{MMH_URL}#L{line}"))
    return rows


def shuowen_rows(gy_file, xml_file):
    """Keep only explicit phonetic claims for the current wordhead in the classical text."""
    verify = verified(xml_file, SW_SHA)
    # The pinned XML has one complete wordhead per line. Link to the exact passage
    # and retain its identifier even when distinct entries have the same headword.
    lines = {m[1]: n for n, line in enumerate(verify.read_text(encoding="utf-8").splitlines(), 1)
             if (m := re.search(r'<wordhead id="([^"]+)"', line))}
    attestations = {}
    for entry in ET.parse(verify).iter("shuowen"):
        head = None
        for child in entry:
            if child.tag == "wordhead":
                head = child
            elif child.tag == "explanation" and head is not None:
                text = "".join(child.itertext())
                if "从" not in text and "從" not in text:
                    continue
                for phonetic, label in EXPLICIT_SOUND.findall(text):
                    record = (phonetic, label, head.attrib["id"], lines[head.attrib["id"]])
                    attestations.setdefault(head.text, set()).add(record)
    converter = OpenCC("t2s")
    rows = []
    for raw in survey_heads(gy_file):
        base, status = next(glyphs(raw, converter), (None, None))
        for phonetic, label, ref, line in sorted(attestations.get(base, ())):
            rows.append((raw, base, status, phonetic, label, ref, line, f"{SW_URL}#L{line}"))
    return rows


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)
    print(f"{path.name}: {len(rows)} attestations for {len({r[0] for r in rows})} source headword fields")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guangyun", type=Path, help="fixed qieyun-data 韻書/廣韻.csv")
    parser.add_argument("dictionary", type=Path, help="fixed Make Me a Hanzi dictionary.txt")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data/loan-sources/velar-second/phonetic-components.tsv")
    parser.add_argument("--shuowen", type=Path, help="also index the separate, fixed CJKVI 說文解字注 XML")
    parser.add_argument("--shuowen-output", type=Path,
                        default=ROOT / "data/loan-sources/velar-second/phonetic-components-shuowen.tsv")
    args = parser.parse_args()
    write(args.output, FIELDS, collect(args.guangyun, args.dictionary))
    if args.shuowen:
        fields = [*FIELDS[:4], "wording", "source_id", *FIELDS[4:]]
        write(args.shuowen_output, fields, shuowen_rows(args.guangyun, args.shuowen))


if __name__ == "__main__":
    main()
