"""Cross-repository source/Skill contract regression tests (stdlib data only)."""
import gzip
import hashlib
import json
import runpy
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
CONTRACT = runpy.run_path(str(HERE / "scripts/verify-site-contract.py"))
EXPORT = runpy.run_path(str(HERE / "scripts/export-readable-lexicon.py"))
validate = CONTRACT["validate"]
ContractError = CONTRACT["ContractError"]


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    site = tmp_path / "site"
    site.mkdir()
    source = site / "dictionary.json.gz"
    metadata = site / "data.json.gz"
    words = [
        {"id": "w1", "attestations": [
            {"id": "a1", "source": "brassett-2006", "term": "gaf", "zh": "吃", "en": "eat",
             "pos": "vt", "dialect": "北部", "locator": "p. 1"},
            {"id": "a2", "source": "south-test", "term": "ka35", "zh": "好", "en": "good",
             "dialect": "南部"},
        ]},
        {"id": "w2", "attestations": [
            {"id": "a3", "source": "brassett-2006", "term": "cog", "zh": "走", "en": "walk"}
        ]}
    ]
    def write_gzip(file, data):
        file.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False).encode()))
    write_gzip(source, {"words": words})
    write_gzip(metadata, {"sources": [{"id": "brassett-2006", "title": "Brassett"},
                                        {"id": "south-test", "title": "South"}],
                          "sourceVariants": [], "sourceAliases": {}})
    for name in EXPORT["CONVERTER_FILES"]:
        (site / name).write_text("// pinned module", encoding="utf-8")
    def fake_spellings(data, _root):
        return {att["id"]: {"accent": [{"text": "gá", "method": "test"}], "ipa": ["ka³⁵"]}
                for word in data["words"] for att in word["attestations"]}
    # The production exporter must run Node; only this tiny offline fixture
    # substitutes converter output. The full workflow uses the real converter.
    monkeypatch.setitem(EXPORT["build"].__globals__, "convert_display_forms", fake_spellings)
    output = tmp_path / "lexicon"
    manifest = EXPORT["build"](source, output, revision="1" * 40,
                               metadata_source=metadata, site_root=site)
    return source, metadata, site, output, words, manifest, write_gzip


def check(w, **kwargs):
    source, metadata, site, output, *_ = w
    return validate(source, metadata, site, output, **kwargs)


def test_full_static_export_passes_and_matches_public_contract(workspace, tmp_path):
    report = check(workspace)
    assert report["status"] == "verified"
    assert report["entries"] == 2 and report["attestations"] == 3
    f, _ = CONTRACT["fingerprints"](*workspace[:3])
    contract = {**f, "schema_version": 1, "producer": "luggroo/bizic-dictionary",
                "templates": CONTRACT["TEMPLATES"],
                "catalog_url": "https://tujia.biz/text/catalog.json"}
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    assert check(workspace, contract_file=contract_path)["attestations"] == 3
    contract["templates"]["entry"] = "https://tujia.biz/renamed/{entry_id}.html"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    with pytest.raises(ContractError, match="text routes changed"):
        check(workspace, contract_file=contract_path)


def test_changed_canonical_gzip_is_rejected(workspace):
    source, _, _, _, words, _, write_gzip = workspace
    write_gzip(source, {"words": words[:1]})
    with pytest.raises(ContractError, match="Source snapshot mismatch"):
        check(workspace, inputs_only=True)


def test_changed_site_converter_is_rejected(workspace):
    _, _, site, *_ = workspace
    with (site / "notation-ui.js").open("a", encoding="utf-8") as file:
        file.write("\n// breaking change")
    with pytest.raises(ContractError, match="site_converter_sha256"):
        check(workspace, inputs_only=True)


def test_corrupted_shard_is_rejected(workspace):
    _, _, _, output, _, manifest, _ = workspace
    filename = next(iter(manifest["buckets"].values()))[0]["path"]
    with (output / filename).open("a", encoding="utf-8") as file:
        file.write("trailing corruption")
    with pytest.raises(ContractError, match="checksum mismatch"):
        check(workspace)


def test_missing_witness_in_shards_is_rejected(workspace):
    _, _, _, output, *_ = workspace
    path = output / "manifest.json"
    data = json.loads(path.read_text())
    bucket = next(iter(data["buckets"]))
    data["index_keys"] -= sum(p["rows"] for p in data["buckets"][bucket])
    del data["buckets"][bucket]
    path.write_text(json.dumps(data))
    with pytest.raises(ContractError, match="Incomplete attestation coverage|Index key count"):
        check(workspace)


def test_forged_source_field_is_rejected_even_with_valid_shard_hash(workspace):
    _, _, _, output, _, manifest, _ = workspace
    part = next(iter(manifest["buckets"].values()))[0]
    file = output / part["path"]
    rows = [json.loads(line) for line in file.read_text().splitlines()]
    rows[0]["r"][2] = "forged-source-id"
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                      for row in rows).encode()
    file.write_bytes(payload)
    manifest["buckets"][next(iter(manifest["buckets"]))][0].update(
        bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    (output / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ContractError, match="Witness field changed"):
        check(workspace)


def test_unsupported_manifest_format_is_rejected(workspace):
    _, _, _, output, *_ = workspace
    path = output / "manifest.json"
    data = json.loads(path.read_text())
    data["format"] = 1
    path.write_text(json.dumps(data))
    with pytest.raises(ContractError, match="Unsupported static lexicon format"):
        check(workspace, inputs_only=True)


def test_missing_adapter_rebuild_is_rejected(workspace):
    _, _, _, output, *_ = workspace
    path = output / "manifest.json"
    data = json.loads(path.read_text())
    data["adapter_sha256"] = "0" * 64
    path.write_text(json.dumps(data))
    with pytest.raises(ContractError, match="adapter changed"):
        check(workspace, inputs_only=True)
