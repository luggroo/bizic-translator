#!/usr/bin/env python3
"""Download the pinned public BGE checkpoint; never commit the output directory."""
import argparse
import hashlib
import json
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

p = argparse.ArgumentParser()
p.add_argument("--output", default=".cache/models/bge-base-zh-v1.5")
p.add_argument("--revision", default="f03589ceff5aac7111bd60cfc7d497ca17ecac65")
a = p.parse_args()
model = "BAAI/bge-base-zh-v1.5"
info = HfApi().model_info(model, revision=a.revision)
files = {f.rfilename for f in info.siblings}
weights = "model.safetensors" if "model.safetensors" in files else "pytorch_model.bin"
if weights not in files:
    raise RuntimeError("No supported checkpoint in model revision")
dest = Path(snapshot_download(model, revision=info.sha, local_dir=a.output, max_workers=2,
            allow_patterns=["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.txt", weights]))
meta = {"model": model, "revision": info.sha, "weights": weights,
        "weights_sha256": hashlib.sha256((dest / weights).read_bytes()).hexdigest()}
(dest / "retrieval-model.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2), flush=True)
