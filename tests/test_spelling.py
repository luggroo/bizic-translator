import json
import subprocess
from pathlib import Path


def test_site_spelling_preserves_unresolved_text_and_missing_tones(repo):
    project = Path(__file__).resolve().parents[1]
    inputs = [
        {"mode": "ye", "text": "ngaf ⟦待核：词形⟧"},
        {"mode": "source", "source": "yubao-60757", "text": "xyz"},
        {"mode": "source", "source": "1EkBQ1pph-C7zHYTg9wuraMsM7cgCwnfE", "text": "ta4"},
    ]
    out = json.loads(subprocess.check_output(
        ["node", "scripts/tujia-lex-spelling.cjs", str(repo.resolve())],
        input=json.dumps(inputs, ensure_ascii=False), text=True, cwd=project,
    ))
    assert out[0]["accent"] == "ngá ⟦待核：词形⟧"
    assert "error" in out[1] and "rows" not in out[1]
    assert out[2]["rows"][0]["accent"] == "tà"
