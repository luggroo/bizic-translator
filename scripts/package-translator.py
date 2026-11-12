#!/usr/bin/env python3
"""Export the reusable application and its generic retrieval evaluation."""
import argparse
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--update', action='store_true')
p.add_argument('--include-static-lexicon', action='store_true',
               help='Include optional offline static dictionary text shards')
a = p.parse_args()
out = Path(a.output)
if out.exists() and not a.update:
    raise SystemExit('Output exists; choose a new directory or --update')
paths = [root / name for name in [
    '.gitignore', 'README.md', 'pyproject.toml', 'requirements-evaluation.txt',
    'skills/translate-tujia/SKILL.md', 'docs/semantic-retrieval-evaluation.md',
]]
for folder in ['src', 'tests', 'docs/evaluation', 'skills/translate-tujia/references'] + (
    ['skills/translate-tujia/lexicon'] if a.include_static_lexicon else []
):
    paths += [f for f in (root/folder).rglob('*') if f.is_file()
              and '__pycache__' not in f.parts
              and not any(s.endswith('.egg-info') for s in f.parts)]
for name in ['download-embedding-model.py', 'evaluate-semantic-retrieval.py',
             'fetch-dictionary.py', 'render-semantic-evaluation.py',
             'tujia-lex-spelling.cjs', 'package-translator.py', 'export-readable-lexicon.py']:
    paths.append(root/'scripts'/name)
for source in paths:
    target = out/source.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
print(out)
