"""Navigation and export checks fail on real broken skill dependencies."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('grammar_qa', ROOT / 'scripts/check-grammar-skill.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def test_checked_in_skill_navigation():
    qa.validate_structure(ROOT)


def test_checked_in_runtime_lifecycle():
    qa.validate_runtime_lifecycle(ROOT)


@pytest.fixture
def runtime_tree(tmp_path):
    """Use the shipped instructions so removals exercise the real contract."""
    for relative in ('skills/translate-tujia/SKILL.md',
                     'skills/translate-tujia/references/retrieval.md',
                     'skills/translate-tujia/references/runtime-lifecycle.md'):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / relative).read_text())
    return tmp_path, tmp_path / 'skills/translate-tujia/references/runtime-lifecycle.md'


@pytest.mark.parametrize('removed', ['reuse-ready', 'provisionable', 'static-only',
                                    '.local/tujia-runtime.json'])
def test_runtime_contract_cannot_lose_an_outcome_or_registry(runtime_tree, removed):
    root, lifecycle = runtime_tree
    lifecycle.write_text(lifecycle.read_text().replace(removed, 'REMOVED'))
    with pytest.raises(AssertionError, match='Missing runtime outcome|runtime registry'):
        qa.validate_runtime_lifecycle(root)


@pytest.mark.parametrize('entry', ['SKILL.md', 'references/retrieval.md'])
def test_preflight_must_be_routed_before_execution(runtime_tree, entry):
    root, _ = runtime_tree
    path = root / 'skills/translate-tujia' / entry
    path.write_text(path.read_text().replace('runtime-lifecycle.md', 'removed.md'))
    with pytest.raises(AssertionError, match='Missing preflight route'):
        qa.validate_runtime_lifecycle(root)


@pytest.mark.parametrize('removed', [
    'before installing, downloading or building',
    'without loading model weights',
    'suitable durable destination are established',
    'temporary/unknown-lifetime storage',
    'scratch/probes/tests only',
    'Do not claim long-term retention',
    '`workspace_only` or `unknown`',
    'restore instructions',
])
def test_preflight_and_persistence_rules_cannot_silently_disappear(runtime_tree, removed):
    root, lifecycle = runtime_tree
    assert removed in lifecycle.read_text()
    lifecycle.write_text(lifecycle.read_text().replace(removed, 'REMOVED'))
    with pytest.raises(AssertionError, match='Missing runtime rule'):
        qa.validate_runtime_lifecycle(root)


@pytest.fixture
def skill_tree(tmp_path):
    main = tmp_path / 'skills/translate-tujia'
    lite = tmp_path / 'skills/tujia-synonym-lite'
    refs = main / 'references'
    refs.mkdir(parents=True)
    lite.mkdir(parents=True)
    header = '---\nname: test\ndescription: Test skill\n---\n'
    (main / 'SKILL.md').write_text(header + '[Topics](references/topics.md)\n'
                                '[Fallback](../tujia-synonym-lite/SKILL.md)\n')
    (refs / 'topics.md').write_text('[Aspect](aspect.md#still)\n')
    (refs / 'aspect.md').write_text('<a id="still"></a>\n# Still\n')
    (lite / 'SKILL.md').write_text(header)
    return tmp_path, refs


def test_transitive_routes_and_external_links(skill_tree):
    root, refs = skill_tree
    with (refs / 'topics.md').open('a') as file:
        file.write('[External](https://example.org/missing.md#unused)\n'
                   '```md\n[Example only](missing-example.md)\n```\n')
    assert len(qa.validate_structure(root)) == 4


def test_qa_requires_manifest_unless_slim_export_explicitly_selected(skill_tree):
    root, _ = skill_tree
    with pytest.raises(AssertionError, match='Missing static lexicon manifest'):
        qa.run(root)


@pytest.mark.parametrize('target,expected', [
    ('missing.md', 'Missing link target'), ('aspect.md#missing', 'Missing anchor')])
def test_broken_link_or_anchor_fails(skill_tree, target, expected):
    root, refs = skill_tree
    (refs / 'topics.md').write_text(f'[Broken]({target})\n')
    with pytest.raises(AssertionError, match=expected):
        qa.validate_structure(root)


def test_unrouted_reference_fails_even_when_file_exists(skill_tree):
    root, refs = skill_tree
    (refs / 'forgotten.md').write_text('# Important instructions\n')
    with pytest.raises(AssertionError, match='Unreachable.*forgotten.md'):
        qa.validate_structure(root)


def test_duplicate_anchor_fails(skill_tree):
    root, refs = skill_tree
    with (refs / 'aspect.md').open('a') as file:
        file.write('<a id="still"></a>\n')
    with pytest.raises(AssertionError, match='Duplicate explicit HTML anchor'):
        qa.validate_structure(root)


def test_unicode_headings_and_reference_links(skill_tree):
    root, refs = skill_tree
    (refs / 'aspect.md').write_text('# 时态与体貌\n')
    (refs / 'topics.md').write_text('[Aspect][tam]\n\n[tam]: aspect.md#时态与体貌\n')
    assert len(qa.validate_structure(root)) == 4


def test_unused_reference_definition_does_not_hide_orphan(skill_tree):
    root, refs = skill_tree
    (refs / 'topics.md').write_text('[unused]: aspect.md\n')
    with pytest.raises(AssertionError, match='Unreachable.*aspect.md'):
        qa.validate_structure(root)


def test_undefined_reference_link_fails(skill_tree):
    root, refs = skill_tree
    (refs / 'topics.md').write_text('[Aspect][missing]\n')
    with pytest.raises(AssertionError, match='Undefined reference link'):
        qa.validate_structure(root)


def test_lexicon_export_detects_missing_and_corrupt_shards(tmp_path):
    payload = b'{"k":"test","r":[]}\n'
    shard = tmp_path / '00-000.jsonl'
    shard.write_bytes(payload)
    (tmp_path / 'manifest.json').write_text(json.dumps({'buckets': {'00': [{
        'path': shard.name, 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}]}}))
    qa.validate_lexicon(tmp_path)
    shard.write_bytes(payload.replace(b'test', b'fail'))
    with pytest.raises(AssertionError, match='checksum'):
        qa.validate_lexicon(tmp_path)
    shard.unlink()
    with pytest.raises(AssertionError, match='Missing lexicon shard'):
        qa.validate_lexicon(tmp_path)


def test_directive_choice_contract():
    """Regression: directive constructions are meaning-led, not suffix-menu guesses."""
    root = ROOT / 'skills/translate-tujia'
    main = (root / 'SKILL.md').read_text(encoding='utf-8')
    index = (root / 'references/grammar-index.md').read_text(encoding='utf-8')
    directives = (root / 'references/directives.md').read_text(encoding='utf-8')
    assert 'references/directives.md#choose' in main
    assert 'directives.md#choose' in index
    for item in ('裸 `V`', '`V-gu`', '`V-do`', '`V-bo`',
                 '`V-xie`', '`V-lie(DIR)`', '`ta + V`'):
        assert item in directives, f'Directive selection lost {item}'
    for example in ('B06:90例110', 'B06:90例113', 'B06:135例190',
                    'B06:135例193', 'B06:137例200'):
        assert example in directives, f'Attested contrast missing {example}'
    assert '李启群等（2021）' in directives and 'ku⁵⁵' in directives
    assert '方向' in directives and 'speech_act' in directives
    assert '不从这些实例推出任意' in directives


def test_gu_is_not_an_automatic_fusion_rule():
    refs = ROOT / 'skills/translate-tujia/references'
    aspect = (refs / 'aspect-modality.md').read_text(encoding='utf-8')
    direction = (refs / 'direction-suffixes.md').read_text(encoding='utf-8')
    for candidate in ('lie＋gu → liao', 'di＋gu → diu', 'da＋gu → dao',
                      'ta＋gu → tao', 'ta ti＋gu → ta tiu'):
        assert candidate not in aspect, f'Obsolete productive derivation: {candidate}'
    assert '延续、当前相关、新情况' not in aspect
    assert '原书分析为`di²+gu²`' not in direction
    assert '[未然态合音](aspect-modality.md#predicate-fusion)' in direction
