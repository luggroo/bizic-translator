from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

MODEL = "BAAI/bge-base-zh-v1.5"
REVISION = "f03589ceff5aac7111bd60cfc7d497ca17ecac65"
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class BGEEncoder:
    """Real BERT CLS pooling following the BGE v1.5 model card; no synonyms or fallback."""
    def __init__(self, model_path=MODEL, max_length=512, threads=4):
        import torch
        from transformers import AutoModel, AutoTokenizer
        if not 8 <= max_length <= 512:
            raise ValueError("BGE max_length must be in [8, 512]")
        torch.set_num_threads(threads)
        self.torch = torch
        self.model_path = str(model_path)
        self.max_length = max_length
        cache_meta = Path(model_path) / "retrieval-model.json"
        if Path(model_path).is_dir():
            if not cache_meta.is_file():
                raise ValueError("Local BGE model needs retrieval-model.json; use scripts/download-embedding-model.py")
            meta = json.loads(cache_meta.read_text())
            if meta.get("model") != MODEL or meta.get("revision") != REVISION:
                raise ValueError("Unsupported local model identity/revision")
            import hashlib
            actual = hashlib.sha256((Path(model_path) / meta["weights"]).read_bytes()).hexdigest()
            if actual != meta.get("weights_sha256"):
                raise ValueError("Model weight checksum mismatch")
        elif str(model_path) != MODEL:
            raise ValueError("Only BAAI/bge-base-zh-v1.5 is supported by this encoder")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, revision=REVISION, trust_remote_code=False)
        self.model = AutoModel.from_pretrained(model_path, revision=REVISION, trust_remote_code=False).to("cpu").eval()
        if self.model.config.model_type != "bert" or self.model.config.hidden_size != 768:
            raise ValueError("This encoder implements BGE-base-zh-v1.5 only; select a supported architecture")
        self.identity = {"model": MODEL, "model_path": str(model_path), "pooling": "CLS; normalized mean over overflow windows", "normalize": True,
                         "query_instruction": QUERY_INSTRUCTION, "max_length": max_length,
                         "revision": REVISION,
                         "torch": torch.__version__, "transformers": __import__("transformers").__version__,
                         "device": "cpu", "threads": threads}
        if cache_meta.is_file():
            self.identity.update(json.loads(cache_meta.read_text()))
        self.identity["config_commit"] = getattr(self.model.config, "_commit_hash", None)

    def encode(self, texts, batch_size=32, query=False):
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        texts = [QUERY_INSTRUCTION + t if query else t for t in texts]
        out = []
        start = time.monotonic()
        for i in range(0, len(texts), batch_size):
            tokens = self.tokenizer(texts[i:i + batch_size], padding=True, truncation=True,
                                    max_length=self.max_length, stride=min(64,self.max_length//4), return_overflowing_tokens=True,
                                    return_tensors="pt")
            mapping = tokens.pop("overflow_to_sample_mapping")
            with self.torch.inference_mode():
                vectors = self.model(**tokens).last_hidden_state[:, 0]
                vectors = self.torch.nn.functional.normalize(vectors, p=2, dim=1)
                # Every long record contributes all windows, not a truncated prefix.
                vectors = self.torch.stack([vectors[mapping == n].mean(dim=0)
                                            for n in range(len(texts[i:i + batch_size]))])
                vectors = self.torch.nn.functional.normalize(vectors, p=2, dim=1)
            out.append(vectors.cpu().numpy().astype("float32"))
            if not query and (i == 0 or i // batch_size % 20 == 0):
                print(json.dumps({"encoded": min(i + batch_size, len(texts)), "total": len(texts),
                                  "seconds": round(time.monotonic() - start, 2)}), file=sys.stderr, flush=True)
        return np.concatenate(out) if out else np.empty((0, 768), dtype="float32")
