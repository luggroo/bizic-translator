#!/usr/bin/env python3
"""Offline QA for the fast Tujia grammar router, references and packaged skill."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


NAMES = ("grammar-index.md", "event-linking.md", "clause-patterns.md",
         "aspect-modality.md", "notation-audit.md")


def markdown_body(text):
    """Ignore fenced examples when validating navigable Markdown."""
    return re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)


def anchors(text):
    body = markdown_body(text)
    explicit = re.findall(r'<a\s+(?:[^>]*?\s)?(?:id|name)=[\"\']([^\"\']+)[\"\']', body)
    assert len(explicit) == len(set(explicit)), "Duplicate explicit HTML anchor"
    found = set(explicit)
    counts = {}
    for title in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", body):
        title = re.sub(r"<[^>]+>", "", title).strip().lower()
        slug = re.sub(r"[^\w\-\s]", "", title).replace(" ", "-")
        occurrence = counts.get(slug, 0)
        counts[slug] = occurrence + 1
        found.add(slug if occurrence == 0 else f"{slug}-{occurrence}")
    return found


def local_links(path):
    """Read inline links and reference-link definitions; external URLs stay offline."""
    body = markdown_body(path.read_text(encoding="utf-8"))
    targets = re.findall(r"\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", body)
    normalize_label = lambda label: ' '.join(label.split()).casefold()
    definitions = {normalize_label(label): target for label, target in re.findall(
        r"(?m)^\s*\[([^\]]+)\]:\s*(<[^>]+>|\S+)", body)}
    uses = re.findall(r"\[([^\]]+)\]\[([^\]]*)\]", body)
    for label, reference in uses:
        key = normalize_label(reference or label)
        assert key in definitions, f'Undefined reference link: {path} [{reference or label}]'
        targets.append(definitions[key])
    # A shortcut link is only a link when its label has a definition. Unused
    # definitions must not make a forgotten reference appear reachable.
    prose = re.sub(r"(?m)^\s*\[[^\]]+\]:.*$", '', body)
    for label in re.findall(r"\[([^\]]+)\](?![\[(])", prose):
        key = normalize_label(label)
        if key in definitions:
            targets.append(definitions[key])
    for raw in targets:
        url = urlsplit(raw.strip("<>"))
        if url.scheme or url.netloc:
            continue
        yield ((path.parent / unquote(url.path)).resolve() if url.path else path.resolve(),
               unquote(url.fragment))


def validate_structure(root, *, optional_lexicon=False):
    """Check links/anchors and ensure every skill document can be reached."""
    root = root.resolve()
    skill_dirs = [root / 'skills/translate-tujia', root / 'skills/tujia-synonym-lite']
    docs = {p.resolve() for folder in skill_dirs for p in folder.rglob('*.md')}
    graph = {}
    for path in sorted(docs):
        anchors(path.read_text(encoding='utf-8'))
        graph[path] = set()
        for target, fragment in local_links(path):
            assert target.is_relative_to(root), f"Link escapes package: {path} -> {target}"
            if (optional_lexicon and not (skill_dirs[0] / 'lexicon').exists()
                    and target.is_relative_to(skill_dirs[0] / 'lexicon')):
                continue
            assert target.is_file(), f"Missing link target: {path.relative_to(root)} -> {target.relative_to(root)}"
            if fragment:
                assert fragment in anchors(target.read_text(encoding='utf-8')), (
                    f"Missing anchor: {path.relative_to(root)} -> {target.relative_to(root)}#{fragment}")
            if target in docs:
                graph[path].add(target)
    entry = skill_dirs[0] / 'SKILL.md'
    reached, pending = set(), [entry]
    while pending:
        path = pending.pop()
        if path not in reached:
            reached.add(path)
            pending.extend(graph.get(path, set()))
    missing = docs - reached
    assert not missing, 'Unreachable skill documents: ' + ', '.join(str(p.relative_to(root)) for p in sorted(missing))
    for folder in skill_dirs:
        main = (folder / 'SKILL.md').read_text(encoding='utf-8')
        assert main.startswith('---\n'), f'Missing frontmatter: {folder}'
        frontmatter = main.split('---', 2)[1]
        assert re.search(r'^name:\s*\S', frontmatter, re.M), f'Missing skill name: {folder}'
        assert re.search(r'^description:\s*\S', frontmatter, re.M), f'Missing skill description: {folder}'
    return docs


def assert_preserved_files(source, target, paths):
    for path in paths:
        relative = path.relative_to(source)
        copied = target / relative
        assert copied.is_file(), f'Packaging lost {relative}'
        assert copied.read_bytes() == path.read_bytes(), f'Packaging altered {relative}'


def validate_lexicon(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    for shard in (s for values in manifest['buckets'].values() for s in values):
        path = directory / shard['path']
        assert path.is_file(), f'Missing lexicon shard: {path}'
        data = path.read_bytes()
        assert len(data) == shard['bytes'], f'Shard byte count changed: {path}'
        assert hashlib.sha256(data).hexdigest() == shard['sha256'], f'Shard checksum changed: {path}'


def validate_runtime_lifecycle(root):
    """Keep environment and storage decisions ahead of the retrieval pipeline.

    This checks the operational contract in the skill, not the persistence or
    readiness of the machine running QA. Those need actual environment evidence.
    """
    skill = root / 'skills/translate-tujia'
    lifecycle = (skill / 'references/runtime-lifecycle.md').resolve()
    assert lifecycle.is_file(), 'Missing runtime lifecycle reference'
    for entry in (skill / 'SKILL.md', skill / 'references/retrieval.md'):
        assert lifecycle in {target for target, _ in local_links(entry)}, (
            f'Missing preflight route in {entry.name}')
    text = lifecycle.read_text(encoding='utf-8').lower()
    for outcome in ('reuse-ready', 'provisionable', 'static-only'):
        assert outcome in text, f'Missing runtime outcome: {outcome}'
    assert '.local/tujia-runtime.json' in text, 'Missing reusable runtime registry'
    # These explicit contracts are scoped to the lifecycle reference. Matching
    # generic words anywhere in the package could hide a removed decision rule.
    rules = {
        'cheap preflight before expensive setup': ('before installing, downloading or building',
                                                  'without loading model weights'),
        'offline asset reuse': ('including offline', 'read the registry first'),
        'durable provisioning gate': ('suitable durable destination are established',
                                     'temporary/unknown-lifetime storage'),
        'no trial pipeline after a known blocker': ('do not download weights or build an index',),
        'temporary storage only for scratch': ('outside `/tmp`, `/var/tmp`',
                                              'scratch/probes/tests only'),
        'verified storage lifetime': ('does not by itself prove persistence',
                                      'do not claim long-term retention',
                                      '`workspace_only` or `unknown`'),
        'durable recovery path': ('environment-snapshot or artifact', 'restore instructions'),
        'bounded rebuild and real execution': ('rebuild only the incompatible index',
                                               'after a current real query succeeds'),
    }
    for name, fragments in rules.items():
        assert all(fragment in text for fragment in fragments), f'Missing runtime rule: {name}'
    return text


def run(root, *, without_static_lexicon=False):
    skill_root = root / "skills" / "translate-tujia"
    main = skill_root / "SKILL.md"
    references = skill_root / "references"
    assert main.is_file(), "Missing main SKILL.md"
    main_text = main.read_text(encoding="utf-8")
    manifest = skill_root / 'lexicon/manifest.json'
    assert manifest.is_file() or without_static_lexicon, (
        'Missing static lexicon manifest; use --without-static-lexicon only for an intentional slim export')
    docs = validate_structure(root, optional_lexicon=without_static_lexicon)
    validate_runtime_lifecycle(root)
    all_text = '\n'.join(path.read_text(encoding='utf-8') for path in sorted(docs))
    for name in NAMES:
        reference = references / name
        assert reference.is_file() and reference.read_text(encoding="utf-8").strip(), name
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
    assert any(rule in all_text.lower() for rule in ('no web search', 'do not invoke web search',
                                                    'do not use web search', '禁止网页搜索'))
    # Every prohibition is a routing cue; the master skill and lite mode must
    # expose alternatives before a translator begins a long exploration.
    recovery = references / "recovery-playbook.md"
    assert recovery.is_file(), "Missing blocker-to-action playbook"
    recovery_text = recovery.read_text(encoding="utf-8")
    assert "references/recovery-playbook.md" in main_text
    assert "Instead →" in all_text and "Stop rule" in all_text
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
    assert "one overall quality note" in all_text
    assert "检索模式：Embedding" in all_text and "检索模式：Skill-based" in all_text
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

    assert "调号拼音 + IPA" in all_text
    assert "叶氏拼音" in all_text and "only when the user explicitly" in all_text

    subprocess.run([sys.executable, str(root / "scripts/lint-grammar-references.py"),
                    "--root", str(root)], cwd=root, check=True)
    with tempfile.TemporaryDirectory(prefix="qa-tujia-grammar-") as tmp:
        target = Path(tmp) / "package"
        subprocess.run([sys.executable, str(root / "scripts/package-translator.py"),
                        "--output", str(target)], cwd=root, check=True, capture_output=True)
        assert_preserved_files(root, target, docs | {lite_root / 'concepts.json'})
        assert_preserved_files(root, target, {root / 'scripts' / name for name in
            ('check-grammar-skill.py', 'lint-grammar-references.py',
             'lightweight-synonym-search.py', 'tujia-lex-spelling.cjs')})
        validate_structure(target, optional_lexicon=True)
        assert not (target / "skills/translate-tujia/lexicon").exists(), (
            "Static lexicon must remain optional")
        if manifest.is_file():
            # The offline export must contain all manifest-verified shards.
            subprocess.run([sys.executable, str(root / "scripts/package-translator.py"),
                            "--output", str(target), "--update", "--include-static-lexicon"],
                           cwd=root, check=True, capture_output=True)
            validate_structure(target)
            validate_lexicon(target / 'skills/translate-tujia/lexicon')
            assert_preserved_files(root, target, set((skill_root / 'lexicon').glob('*')))
        else:
            print('Intentional slim export: static lookup and shard integrity not evaluated')
    print("Grammar router QA passed: all routes, notation rules and bundled references")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--without-static-lexicon', action='store_true',
                        help='Allow an intentionally slim exported package with no static dictionary')
    args = parser.parse_args()
    run(args.root.resolve(), without_static_lexicon=args.without_static_lexicon)
