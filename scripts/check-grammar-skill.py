#!/usr/bin/env python3
"""Offline QA for the fast Tujia grammar router, references and packaged skill."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


NAMES = ("grammar-index.md", "event-linking.md", "clause-patterns.md",
         "aspect-modality.md", "notation-audit.md")


def run(root):
    skill_root = root / "skills" / "translate-tujia"
    main = skill_root / "SKILL.md"
    references = skill_root / "references"
    assert main.is_file(), "Missing main SKILL.md"
    main_text = main.read_text(encoding="utf-8")
    for name in NAMES:
        reference = references / name
        assert reference.is_file() and reference.read_text(encoding="utf-8").strip(), name
        assert f"references/{name}" in main_text or name == "notation-audit.md", (
            "Main skill lacks route for " + name)
    idx = (references / NAMES[0]).read_text(encoding="utf-8")
    for name in NAMES[1:]:
        assert name in idx, f"Missing index route to {name}"
    tam = (references / "aspect-modality.md").read_text(encoding="utf-8")
    for term in ("快要", "还在", "还没", "已经", "不再", "能", "会",
                 "可以", "必须", "想", "恐怕"):
        assert term in tam or term in idx, f"Missing semantic search route: {term}"
    for a in ('<a id="prospective">', '<a id="still">', '<a id="completion">',
              '<a id="ability">', '<a id="volition">', '<a id="south">'):
        assert a in tam, f"Missing index anchor: {a}"
    assert "No web search actions." in main_text
    assert "调号拼音 + IPA" in main_text
    assert "叶氏拼音" in main_text and "only when the user explicitly" in main_text

    subprocess.run([sys.executable, str(root / "scripts/lint-grammar-references.py"),
                    "--root", str(root)], cwd=root, check=True)
    with tempfile.TemporaryDirectory(prefix="qa-tujia-grammar-") as tmp:
        target = Path(tmp) / "package"
        subprocess.run([sys.executable, str(root / "scripts/package-translator.py"),
                        "--output", str(target)], cwd=root, check=True, capture_output=True)
        assert (target / "skills/translate-tujia/SKILL.md").is_file()
        for name in NAMES:
            assert (target / "skills/translate-tujia/references" / name).is_file(), (
                "Packaging lost reference " + name)
        assert not (target / "skills/translate-tujia/lexicon").exists(), (
            "Static lexicon must remain optional")
    print("Grammar router QA passed: all routes, notation rules and bundled references")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    run(args.root.resolve())
