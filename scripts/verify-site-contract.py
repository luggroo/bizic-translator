#!/usr/bin/env python3
"""Fail-closed verification of the Skill's static lexicon against one pinned website source.

No model weights, network requests, or public query-time service required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
import sys
from pathlib import Path

EXPORTER = runpy.run_path(str(Path(__file__).with_name("export-readable-lexicon.py")))
FIELDS = ["entry_id", "attestation_id", "source", "term", "zh", "en",
          "pos", "dialect", "locator", "source_ref", "notations",
          "source_term", "term_notation", "accent_provenance"]
TEMPLATES = {
    "exact_zh": "https://tujia.biz/text/lookup/zh/{query}.html",
    "initial_zh": "https://tujia.biz/text/initial/zh/{initial}.html",
    "entry": "https://tujia.biz/text/entry/{entry_id}.html",
}


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    return sha(Path(path).read_bytes())


def ids_sha(values):
    return sha(("\n".join(sorted(values)) + "\n").encode("utf-8"))


def unique_ids(items, field):
    values = [item.get("id") for item in items]
    require(all(isinstance(value, str) and value for value in values),
            "Missing or invalid " + field)
    require(len(values) == len(set(values)), "Duplicate " + field)
    return values


def fingerprints(source, metadata_source, site_root):
    dictionary = EXPORTER["read_dictionary"](source)
    metadata = EXPORTER["read_gzip_json"](metadata_source)
    require(isinstance(metadata, dict) and isinstance(metadata.get("sources"), list),
            "Missing source metadata")
    words = dictionary["words"]
    entry_ids = unique_ids(words, "entry IDs")
    require(all(isinstance(entry.get("attestations"), list) for entry in words),
            "Missing attestation list")
    attestations = [(word["id"], att) for word in words for att in word["attestations"]]
    attestation_ids = unique_ids([att for _, att in attestations], "attestation IDs")
    source_ids = unique_ids(metadata.get("sources", []) + metadata.get("sourceVariants", []),
                            "source IDs")
    converter_hashes = {
        name: sha_file(site_root / name)
        for name in EXPORTER["CONVERTER_FILES"]
    }
    return {
        "source_sha256": sha_file(source),
        "metadata_source_sha256": sha_file(metadata_source),
        "dictionary_entries": len(entry_ids),
        "dictionary_attestations": len(attestation_ids),
        "entry_ids_sha256": ids_sha(entry_ids),
        "attestation_ids_sha256": ids_sha(attestation_ids),
        "attestation_sources_sha256": ids_sha(
            [att["id"] + "\t" + (att.get("source") or "") for _, att in attestations]),
        "source_ids_sha256": ids_sha(source_ids),
        "site_converter_sha256": converter_hashes,
    }, {(att["id"]): (entry_id, att) for entry_id, att in attestations}


def verify_inputs(manifest, fingerprints_):
    for field in ("source_sha256", "metadata_source_sha256",
                  "dictionary_entries", "dictionary_attestations", "site_converter_sha256"):
        require(manifest.get(field) == fingerprints_[field], "Source snapshot mismatch: " + field)
    require(manifest.get("format") == 2, "Unsupported static lexicon format")
    require(manifest.get("source") == "luggroo/bizic-dictionary/site/dictionary.json.gz",
            "Canonical source location changed")
    require(manifest.get("adapter_sha256") ==
            sha_file(Path(__file__).with_name("tujia-lex-spelling.cjs")),
            "Local site spelling adapter changed without rebuilding lexicon")
    require(manifest.get("record_fields") == FIELDS, "Shard record schema changed")
    require(isinstance(manifest.get("revision"), str) and
            bool(re.fullmatch(r"[0-9a-f]{40}", manifest["revision"])),
            "Lexicon must record one pinned source commit")


def verify_contract_file(contract, fingerprints_):
    require(contract.get("schema_version") == 1, "Unsupported website contract version")
    require(contract.get("producer") == "luggroo/bizic-dictionary",
            "Unexpected contract producer")
    require(contract.get("templates") == TEMPLATES, "Website text routes changed")
    require(contract.get("catalog_url") == "https://tujia.biz/text/catalog.json",
            "Website catalog location changed")
    for key, expected in fingerprints_.items():
        require(contract.get(key) == expected, "Website contract mismatch: " + key)


def validate(source, metadata_source, site_root, directory, *,
             inputs_only=False, contract_file=None):
    source, metadata_source, site_root, directory = (
        Path(source), Path(metadata_source), Path(site_root), Path(directory))
    fingerprints_, witnesses = fingerprints(source, metadata_source, site_root)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    verify_inputs(manifest, fingerprints_)
    require(manifest.get("sources") == EXPORTER["source_catalog"](metadata_source),
            "Source catalog or canonical source aliases changed")
    if contract_file:
        verify_contract_file(json.loads(Path(contract_file).read_text(encoding="utf-8")),
                             fingerprints_)
    if inputs_only:
        return {"status": "compatible", "revision": manifest["revision"],
                "entries": len({entry for entry, _ in witnesses.values()}),
                "attestations": len(witnesses)}
    buckets = manifest.get("buckets")
    require(isinstance(buckets, dict) and buckets, "Missing static lexicon buckets")
    limit = manifest.get("shard_limit_bytes")
    require(isinstance(limit, int) and 4096 <= limit <= 110000, "Unsafe shard size limit")
    observed = {}
    keys = {}
    count = 0
    for bucket, parts in buckets.items():
        require(bool(re.fullmatch(r"[0-9a-f]{2}", bucket)), "Bad shard bucket")
        require(isinstance(parts, list) and parts, "Empty bucket file list")
        for part in parts:
            name = part.get("path")
            require(isinstance(name, str) and
                    re.fullmatch(bucket + r"-[0-9]{3}\.jsonl", name) is not None,
                    "Unsafe or misplaced shard path")
            payload = (directory / name).read_bytes()
            require(len(payload) == part.get("bytes") and len(payload) <= limit and
                    sha(payload) == part.get("sha256"), "Shard checksum mismatch: " + name)
            lines = payload.decode("utf-8").splitlines()
            require(len(lines) == part.get("rows"), "Shard row count mismatch: " + name)
            for line in lines:
                item = json.loads(line)
                key, row = item["k"], item["r"]
                require(isinstance(key, str) and key == EXPORTER["normalize"](key) and
                        EXPORTER["bucket_of"](key) == bucket, "Wrong normalized lookup bucket")
                require(isinstance(row, list) and len(row) == len(FIELDS), "Invalid row schema")
                data = dict(zip(FIELDS, row))
                aid = data["attestation_id"]
                require(aid in witnesses, "Unknown attestation in static shard: " + str(aid))
                entry, att = witnesses[aid]
                require(data["entry_id"] == entry, "Attestation assigned to wrong entry: " + aid)
                for source_field, row_field in [
                    ("source", "source"), ("zh", "zh"), ("en", "en"),
                    ("pos", "pos"), ("dialect", "dialect"), ("locator", "locator"),
                    ("sourceRef", "source_ref"), ("term", "source_term")]:
                    require(data[row_field] == att.get(source_field, ""),
                            "Witness field changed: " + aid + " " + row_field)
                notation, forms = data["term_notation"], data["notations"]
                require(notation in ("accent", "ipa", "missing") and
                        isinstance(forms, dict), "Invalid pronunciation type")
                accent, ipa = forms.get("accent", []), forms.get("ipa", [])
                require(isinstance(accent, list) and isinstance(ipa, list),
                        "Invalid notation field")
                if notation == "accent":
                    require(bool(accent) and data["term"] == " / ".join(accent),
                            "Invalid accent display for " + aid)
                elif notation == "ipa":
                    require(not accent and bool(ipa) and
                            data["term"] == " / ".join("/" + v.strip("/") + "/" for v in ipa),
                            "Invalid IPA fallback for " + aid)
                else:
                    require(not accent and not ipa and data["term"] == "⟦待核：读音⟧",
                            "Invalid missing pronunciation marker")
                require(isinstance(data["accent_provenance"], list) and
                        all(isinstance(a, dict) and a.get("text") in accent
                            for a in data["accent_provenance"]),
                        "Wrong accent provenance: " + aid)
                prior = observed.setdefault(aid, row)
                require(prior == row, "Inconsistent witness across search keys: " + aid)
                keys.setdefault(aid, set()).add(key)
                count += 1
    require(set(observed) == set(witnesses), "Incomplete attestation coverage")
    require(count == manifest.get("index_keys"), "Index key count changed")
    for aid, (_, att) in witnesses.items():
        required = EXPORTER["search_keys"](att, [])
        require(required.issubset(keys[aid]),
                "Missing exact dictionary query keys for attestation: " + aid)
    return {"status": "verified", "revision": manifest["revision"],
            "entries": fingerprints_["dictionary_entries"],
            "attestations": len(witnesses), "lookup_rows": count,
            "shard_files": sum(map(len, buckets.values()))}


def verify_identity_stability(source, metadata_source, directory):
    """Block silent removals/reassignments of IDs when regenerating static shards.

    Editorial content changes or additive entries are permitted; changed identities
    require an explicit reviewed migration rather than an unattended scheduled push.
    """
    source, metadata_source, directory = map(Path, (source, metadata_source, directory))
    old_manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    require(old_manifest.get("format") == 2 and old_manifest.get("record_fields") == FIELDS,
            "Cannot verify previous ID schema")
    old_witnesses = {}
    for bucket, files in old_manifest["buckets"].items():
        for part in files:
            name = part["path"]
            require(bool(re.fullmatch(r"[0-9a-f]{2}-[0-9]{3}\.jsonl", name))
                    and name.startswith(bucket + "-"), "Unsafe previous shard path")
            payload = (directory / name).read_bytes()
            require(len(payload) == part["bytes"] and sha(payload) == part["sha256"],
                    "Previous shard cannot be trusted: " + name)
            lines = payload.decode("utf-8").splitlines()
            require(len(lines) == part["rows"], "Previous shard row count changed")
            for line in lines:
                row = json.loads(line)["r"]
                require(isinstance(row, list) and len(row) == len(FIELDS),
                        "Invalid previous witness row")
                attestation = row[1]
                identity = (row[0], row[2])
                if attestation in old_witnesses:
                    require(old_witnesses[attestation] == identity,
                            "Contradictory previous witness identity: " + str(attestation))
                old_witnesses[attestation] = identity
    require(bool(old_witnesses), "No prior witnesses available for migration check")
    new_dictionary = EXPORTER["read_dictionary"](source)
    new_records = {}
    for entry in new_dictionary["words"]:
        for a in entry["attestations"]:
            require(a["id"] not in new_records, "Duplicate new attestation ID")
            new_records[a["id"]] = (entry["id"], a.get("source", ""))
    deleted = set(old_witnesses) - set(new_records)
    require(not deleted, "Removing existing attestation IDs requires migration: " +
            ", ".join(sorted(deleted)[:5]))
    remapped = [aid for aid, identity in old_witnesses.items()
                if new_records[aid] != identity]
    require(not remapped, "Changed entry/source ownership requires migration: " +
            ", ".join(sorted(remapped)[:5]))
    old_entries = {entry for entry, _ in old_witnesses.values()}
    new_entries = {entry["id"] for entry in new_dictionary["words"]}
    require(old_entries.issubset(new_entries),
            "Removing existing entry IDs requires migration")
    previous_sources = old_manifest.get("sources", {})
    new_sources = EXPORTER["source_catalog"](metadata_source)
    removed_sources = set(previous_sources) - set(new_sources)
    require(not removed_sources, "Removing public source IDs requires migration: " +
            ", ".join(sorted(removed_sources)[:5]))
    changed_aliases = [sid for sid, old in previous_sources.items()
                       if old.get("canonical_id") != new_sources[sid].get("canonical_id")]
    require(not changed_aliases, "Changing canonical source aliases requires migration: " +
            ", ".join(sorted(changed_aliases)[:5]))
    return {"status": "additive-compatible", "old_attestations": len(old_witnesses),
            "new_attestations": len(new_records), "new_entries": len(new_entries)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--metadata-source", required=True)
    parser.add_argument("--site-root", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--inputs-only", action="store_true")
    parser.add_argument("--check-previous-identities", action="store_true")
    parser.add_argument("--contract-file", help="Optional published /text/contract.json")
    args = parser.parse_args()
    try:
        result = (verify_identity_stability(args.source, args.metadata_source, args.directory)
                  if args.check_previous_identities else
                  validate(args.source, args.metadata_source, args.site_root, args.directory,
                           inputs_only=args.inputs_only, contract_file=args.contract_file))
    except (ContractError, ValueError, KeyError, OSError, TypeError) as error:
        print("CONTRACT_MISMATCH: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
