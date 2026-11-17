"""Default lookup works without ML dependencies; explicit routes remain opt-in."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / 'skills/translate-tujia/lexicon'


def cli(*args):
    # -S excludes site-packages, including numpy/torch/transformers.
    return subprocess.run([sys.executable, '-S', '-m', 'tujia_lex.cli', *args],
                          cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'src')},
                          capture_output=True, text=True)


def test_default_plan_is_static_without_ml_even_with_model_arguments():
    result = cli('plan', '饮料', '--model-path', '/missing-model', '--index', '/missing-index')
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['route'] == 'D'
    assert report['cost']['query_encodings'] == 0
    assert report['candidates']
    assert all(q['engine'] == 'static' for q in report['queries'])
    assert all(r['score'] is None and r['attestations'] for r in report['candidates'])


@pytest.mark.parametrize('route', ['A', 'B', 'C', 'E'])
def test_index_routes_validate_required_index_before_importing_ml(route):
    result = cli('plan', '饮料', '--route', route)
    assert result.returncode == 2
    assert '--index is required' in result.stderr
    assert 'Traceback' not in result.stderr


def test_explicit_embedding_plan_can_be_previewed_without_loading_ml():
    result = cli('plan', '饮料', '--route', 'C', '--dry-run')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['queries']


def test_batch_matches_single_queries_and_reuses_verified_shards():
    import importlib.util
    from tujia_lex.static import StaticLexicon
    spec = importlib.util.spec_from_file_location('batch_lite', ROOT / 'scripts/lightweight-synonym-search.py')
    lite = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lite)
    lexicon = StaticLexicon(LEXICON)
    first = lite.run('饮料', LEXICON, lite.DEFAULT_CONCEPTS, lexicon=lexicon)
    reads = lexicon.shard_reads
    assert first == lite.run('饮料', LEXICON, lite.DEFAULT_CONCEPTS, lexicon=lexicon)
    assert lexicon.shard_reads == reads > 0
    args = [sys.executable, '-S', str(ROOT / 'scripts/lightweight-synonym-search.py')]
    result = subprocess.run([*args, '饮料', '香味'], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    reports = json.loads(result.stdout)['results']
    assert reports[0] == first
    assert reports[1] == lite.run('香味', LEXICON, lite.DEFAULT_CONCEPTS)
