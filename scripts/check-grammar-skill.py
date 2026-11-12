#!/usr/bin/env python3
"""Fast dependency/packaging QA for the reusable translation grammar subskill."""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(root):
    skill_root = root / "skills" / "translate-tujia"
    main = skill_root / "SKILL.md"
    constructions = skill_root / "references" / "construction-choices.md"
    tam = skill_root / "references" / "aspect-modality.md"
    for path in (main, constructions, tam):
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise AssertionError(f"Missing or empty skill file: {path}")
    main_text = main.read_text(encoding="utf-8")
    con_text = constructions.read_text(encoding="utf-8")
    tam_text = tam.read_text(encoding="utf-8")
    assert "references/construction-choices.md" in main_text
    assert "references/aspect-modality.md" in main_text
    assert "aspect-modality.md" in con_text
    assert "Brassett" in con_text and "Brassett" in tam_text
    assert "[补充]" in tam_text and "[教学]" in tam_text
    assert "南部土家语" in tam_text
    # Common Chinese auxiliary/adverb ambiguities should be decidable from
    # a local example/reference, not an unbounded fresh web search.
    for cue in ("快要", "还在", "还没", "已经", "不再", "能", "会", "可以", "必须", "想", "恐怕"):
        assert cue in tam_text, f"Unaddressed aspect/modal ambiguity: {cue}"
    for marker in ("gafhur", "savlaxniex", "tɕi⁵⁵ ta⁵⁵", "niefbortaxdornief",
                   "tʰa⁵⁵ pie⁵⁵", "ɣie³⁵ha³⁵tsi²¹tsʰie⁵⁵"):
        assert marker in tam_text, f"Missing prechecked example: {marker}"
    assert "No web search actions." in main_text
    assert "../tujia-synonym-lite/SKILL.md" in main_text
    assert "检索模式：Embedding" in main_text and "检索模式：Skill-based" in main_text
    synonym_dir = root / "skills" / "tujia-synonym-lite"
    synonym_text = (synonym_dir / "SKILL.md").read_text(encoding="utf-8")
    concepts = (synonym_dir / "concepts.json").read_text(encoding="utf-8")
    for cue in ("路人", "香味", "玩具", "饮料", "令人费解", "经济损失"):
        assert cue in concepts, f"Missing semantic bridge: {cue}"
    assert "not embedding" in synonym_text.lower()


    with tempfile.TemporaryDirectory(prefix="qa-tujia-skill-") as tmp:
        target = Path(tmp) / "bundle"
        subprocess.run([sys.executable, str(root / "scripts/package-translator.py"),
                        "--output", str(target)], cwd=root, check=True, capture_output=True, text=True)
        for name in ("SKILL.md", "references/construction-choices.md", "references/aspect-modality.md"):
            path = target / "skills" / "translate-tujia" / name
            assert path.is_file(), f"Packaging lost required reference: {name}"
        assert (target / "scripts" / "export-readable-lexicon.py").is_file()
        assert (target / "scripts" / "lightweight-synonym-search.py").is_file()
        assert (target / "skills" / "tujia-synonym-lite" / "SKILL.md").is_file()
        assert (target / "skills" / "tujia-synonym-lite" / "concepts.json").is_file()
        assert not (target / "skills/translate-tujia/lexicon").exists(), (
            "Static lexicon is optional; avoid forcing 16 MB into every bundle"
        )
    print("Grammar subskill QA passed: references, bilingual trigger table, and minimal bundle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    run(args.root.resolve())
