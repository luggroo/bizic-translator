# Environment preflight and durable reuse

Read **before installing, downloading or building**. Decide from cheap environment checks; do not test suitability by running the entire setup pipeline. [Retrieval](retrieval.md) describes the queries after this decision.

## Preflight

1. Inspect available execution tools and the provider's environment/storage description. Check Python and installed dependencies without loading model weights. A text-only connector is sufficient for static lookup, not local inference.
2. Read an existing `.local/tujia-runtime.json` registry, if present, and inspect its paths. Otherwise check configured asset locations and the existing repository `.venv`, `.cache/models` and `.cache/bge-index`. Use file existence, model metadata and index manifest to identify reusable compatible assets before considering downloads. A registry is a discovery hint; validate its current files and versions.
3. Check CPU availability, available RAM, free disk and write permissions. Compare with the documented model/index requirements or measured footprint of existing assets, leaving room for dependencies, extraction and a new index. Missing GPU is not a blocker for the supported CPU model. Test required download access only if assets are missing; an offline environment can reuse a complete local installation.
4. Establish the storage lifecycle separately from writability. A writable path named `/workspace`, `.cache` or a user cache directory does not by itself prove persistence. Look for a provider-documented durable volume, persistent workspace, reusable environment snapshot, or an authorized artifact store with a restore path.

Retain commands/tool observations and distinguish unchecked, missing-but-installable, usable and blocked requirements. A failed GitHub request does not prove the model/package endpoints are inaccessible; check only the specific missing dependency's endpoint and reassess when an authorized route becomes available. If the user explicitly chooses static retrieval, honor that choice without inventing a blocker. A short translation alone is not evidence of an incapable environment.

| Decision | Next action |
| --- | --- |
| **reuse-ready**: execution works and compatible assets already exist | Use them in place, including offline. Validate through the loader and a current query; retain the loaded session for a batch. If their storage lifetime is unclear, record that and seek a durable destination without delaying this usable query. |
| **provisionable**: missing assets, but execution/resources/download access and a suitable durable destination are established | Install only missing dependencies, download only missing model/data, and build only a missing or incompatible index at that destination. Record paths and identity for later tasks. |
| **static-only**: execution is unsupported, a required resource/access check fails, or new setup would have only temporary/unknown-lifetime storage | Go directly to [synonym-lite](../../tujia-synonym-lite/SKILL.md). Do not download weights or build an index to confirm a known blocker. Seek durable storage separately if that would enable future BGE use. |

## Persistence and restoration

Prefer an existing verified durable root; reuse it instead of creating another installation. If none is available, inspect supported volume, environment-snapshot or artifact options. When choosing or enabling a destination requires user input, ask once for that specific storage decision and continue this translation with available retrieval. Do not claim long-term retention until the provider or user has established the destination's lifecycle.

Keep the application environment, pinned model, dictionary snapshot and complete index outside `/tmp`, `/var/tmp`, temporary directories and disposable container layers as their sole storage. **Temporary files are for scratch/probes/tests only.** A temporary restore is usable when a verified durable copy already exists; record that durable origin and the restore steps. Do not upload model weights or private source data to a public Git repository as a persistence shortcut.

Record a local `.local/tujia-runtime.json` registry (ignored by Git) with absolute application/Python/model/index/data paths, model revision and checksum, dictionary revision, index manifest identity, storage scope, persistence evidence and restore instructions. Use `workspace_only` or `unknown` when lifetime is unverified, not `durable`. Keep credentials out of the registry. Store a nonsecret restore pointer with the persistent workspace/environment configuration so a later agent can find the registry and assets; a pointer in a disposable checkout alone is insufficient.

Future tasks read the registry first, validate compatibility and reuse assets. Keep one encoder/index session across a query batch; on process restart reload existing files, not the download/build pipeline. Rebuild only the incompatible index when model/data/schema changes, preserving the known-good version until the replacement validates. If setup encounters an unforeseen blocker, stop at that stage, retain reusable assets, record the blocker and switch to static lookup.

Persistence makes assets reusable; it does not prove inference ran. Announce Embedding only after a current real query succeeds using an expression from the current task, following [output rules](output.md). Imports, model loading and planner output alone do not establish query execution; zero matches from a successful query do not mean the runtime failed.
