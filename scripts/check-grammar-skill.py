#!/usr/bin/env python3
"""Offline QA for the fast Tujia grammar router, references and packaged skill."""
import argparse
import json
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
    # Every prohibition is a routing cue; the master skill and lite mode must
    # expose alternatives before a translator begins a long exploration.
    recovery = references / "recovery-playbook.md"
    assert recovery.is_file(), "Missing blocker-to-action playbook"
    recovery_text = recovery.read_text(encoding="utf-8")
    assert "references/recovery-playbook.md" in main_text
    assert "Instead →" in main_text and "**Stop rule:**" in main_text
    assert len([line for line in recovery_text.splitlines()
                if line.startswith("| ") and " | " in line]) >= 20, (
        "Recovery playbook is missing action routes")
    for concept in ("BGE", "gzip", "nominal", "liex", "tone",
                    "web", "Longshan", "source", "Chinese insertion"):
        assert concept.lower() in recovery_text.lower(), (
            "Recovery playbook lacks action for " + concept)
    # The companion no-model semantic bridge must remain routable and honestly labeled.
    lite_root = root / "skills/tujia-synonym-lite"
    lite_text = (lite_root / "SKILL.md").read_text(encoding="utf-8")
    assert "translate-tujia/references/recovery-playbook.md" in lite_text
    assert "Instead →" in lite_text
    seed = json.loads((lite_root / "concepts.json").read_text(encoding="utf-8"))
    assert "../tujia-synonym-lite/SKILL.md" in main_text
    assert "references/semantic-decomposition.md" in main_text
    shared = (references / "semantic-decomposition.md").read_text(encoding="utf-8")
    assert "shared" in shared.lower() and "geci-xi" in shared and "hu-ci" in shared
    assert "semantic-decomposition.md" in lite_text
    assert "one overall quality note" in main_text
    assert "检索模式：Embedding" in main_text and "检索模式：Skill-based" in main_text
    for word, expected_form in (
        ("路人", "la hxi ma"), ("香味", "气味"), ("玩具", "geci-xi"),
        ("饮料", "hu-ci"), ("令人费解", "懂得 + 不能"),
    ):
        assert word in lite_text
        assert seed["concepts"][word]["proposed_composition"]["construction"].startswith(expected_form)
        if (root / "skills/translate-tujia/lexicon/manifest.json").is_file():
            completed = subprocess.run(
                [sys.executable, str(root / "scripts/lightweight-synonym-search.py"),
                 word, "--max-queries", "10", "--limit-per-query", "1"],
                cwd=root, check=True, capture_output=True, text=True
            )
            report = json.loads(completed.stdout)
            assert report["mode"] == "skill_based" and report["embedding_run"] is False
            assert report["candidate_results"][0]["query"] == word

    assert "调号拼音 + IPA" in main_text
    assert "叶氏拼音" in main_text and "only when the user explicitly" in main_text

    subprocess.run([sys.executable, str(root / "scripts/lint-grammar-references.py"),
                    "--root", str(root)], cwd=root, check=True)
    with tempfile.TemporaryDirectory(prefix="qa-tujia-grammar-") as tmp:
        target = Path(tmp) / "package"
        subprocess.run([sys.executable, str(root / "scripts/package-translator.py"),
                        "--output", str(target)], cwd=root, check=True, capture_output=True)
        assert (target / "skills/translate-tujia/SKILL.md").is_file()
        for name in (*NAMES, "semantic-decomposition.md", "recovery-playbook.md"):
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
