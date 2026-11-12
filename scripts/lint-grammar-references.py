#!/usr/bin/env python3
"""QA tone-marked Tujia Pinyin + IPA example tables, with provenance preserved.

This checks display-tone class agreement and reference structure. It cannot
verify underlying IPA phonetics or source transcription without independent
witnesses. Crucially, it never silently edits IPA to match orthography.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
MARKS = {"\u0304": "H", "\u0301": "R", "\u030c": "L", "\u0300": "F"}
NORTH = {"55": "H", "44": "H", "24": "R", "35": "R", "325": "R",
         "13": "R", "21": "L", "214": "L", "31": "L", "33": "L",
         "51": "F", "53": "F", "54": "F"}
# Source-specific Southern mappings from site/grammar-notation.js and
# site/southern-notation.js. Unmarked 33/31 are non-visible in the display.
SOUTH = {"55": "H", "53": "H", "51": "H", "35": "R",
         "21": "F", "13": "L", "33": "", "31": ""}

EXAMPLE_FILES = ("event-linking.md", "clause-patterns.md", "aspect-modality.md")


def cells(line: str) -> list[str]:
    return [x.strip() for x in line.strip().strip("|").split("|")]


def pinyin_tones(text: str) -> list[str]:
    return [MARKS[c] for c in unicodedata.normalize("NFD", text)
            if c in MARKS]


def ipa_tones(text: str, *, southern=False) -> list[str]:
    scheme = SOUTH if southern else NORTH
    out = []
    for match in re.findall(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", text):
        value = "".join(str(SUP.index(c)) for c in match)
        if value not in scheme:
            raise ValueError(f"Unmapped IPA tone {value} in {text!r}")
        if scheme[value]:
            out.append(scheme[value])
    return out


def lint(root: Path) -> tuple[int, int]:
    refs = root / "skills/translate-tujia/references"
    expected = ("grammar-index.md", "event-linking.md", "clause-patterns.md",
                "aspect-modality.md", "notation-audit.md")
    for name in expected:
        if not (refs / name).is_file():
            raise AssertionError(f"Missing grammar reference: {name}")
    if (refs / "construction-choices.md").exists():
        raise AssertionError("Old, unsorted construction-choices.md must be removed")
    problems = []
    examples = 0
    provisional = 0
    for name in EXAMPLE_FILES:
        lines = (refs / name).read_text(encoding="utf-8").splitlines()
        southern = False
        column_indices = None
        for i, line in enumerate(lines, 1):
            if name == "aspect-modality.md" and '<a id="south">' in line:
                southern = True
            if not line.startswith("|"):
                column_indices = None
                continue
            parts = cells(line)
            if any(p.startswith("IPA") for p in parts):
                if not any(p.startswith("调号拼音") for p in parts):
                    problems.append(f"{name}:{i}: IPA example table lacks tone-marked Pinyin column")
                    continue
                pi = next(j for j, p in enumerate(parts) if p.startswith("调号拼音"))
                ia = next(j for j, p in enumerate(parts) if p.startswith("IPA"))
                provisional_table = any("拟转写" in p or "待独立核" in p for p in parts)
                column_indices = (pi, ia, provisional_table)
                continue
            if column_indices is None or all(re.fullmatch(r":?-+:?", c) for c in parts):
                continue
            pi, ia, provisional_table = column_indices
            if len(parts) <= max(pi, ia):
                problems.append(f"{name}:{i}: unaligned example table row")
                continue
            p, ipa = parts[pi], parts[ia]
            if not p or not ipa or not ipa.startswith("/"):
                problems.append(f"{name}:{i}: missing Pinyin or IPA: {line[:130]}")
                continue
            examples += 1
            if provisional_table or "待独立核" in p or "待核" in p:
                provisional += 1
            a, b = pinyin_tones(p), ipa_tones(ipa, southern=southern)
            if a != b:
                problems.append(f"{name}:{i}: tone classes disagree: Pinyin {a}, IPA {b}: {line[:180]}")
            if len(parts) > 3 and not any(
                re.search(r"(B06|陈康|Brassett|田志慧|李敬忠|向亮|简志|补充|Feng|土家语|鲁曼)", c)
                for c in parts
            ):
                problems.append(f"{name}:{i}: missing explicit source provenance")
    if problems:
        raise AssertionError("\n".join(problems))
    if examples < 65:
        raise AssertionError(f"Too few example pairs: {examples}")
    return examples, provisional


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    count, provisional = lint(args.root.resolve())
    print(f"Notation audit passed: {count} tonal Pinyin/IPA example pairs; "
          f"{provisional} independently unverified. "
          "Passing tone-class QA does NOT validate IPA phoneme accuracy.")


if __name__ == "__main__":
    main()
