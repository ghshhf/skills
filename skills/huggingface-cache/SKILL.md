---
TERMUX_PKG_NAME: huggingface-cache
TERMUX_PKG_DESCRIPTION: "Scan, analyze, and clean Hugging Face cache. Lists cached models/datasets with size & last-used info, prunes detached revisions, and frees disk space safely"
TERMUX_PKG_HOMEPAGE: https://huggingface.co/docs/huggingface_hub/guides/manage-cache
TERMUX_PKG_MAINTAINER: "@huggingface"
TERMUX_PKG_VERSION: 1.0.0
TERMUX_PKG_LICENSE: MIT
TERMUX_PKG_DEPENDS: hf-cli
TERMUX_PKG_CATEGORY: tools
---

# HuggingFace Cache Manager

Manage local Hugging Face cache to free disk space without breaking active environments.

## Core workflow

1. **Scan** — Analyze `~/.cache/huggingface/` to list all cached repos with size and last-accessed time.
2. **Identify waste** — Flag detached revisions (no refs pointing to them) and repos unused for N days.
3. **Clean** — Remove specific repos/revisions or prune all detached blobs.

## Cache directory structure

```
~/.cache/huggingface/
├─ hubs/
│  ├─ models--org--model-name/
│  │  ├─ blobs/         # Actual files (sha256-named)
│  │  ├─ refs/           # Refs pointing to blobs
│  │  └─ snapshots/      # Snapshot hashes → blob refs
│  ├─ datasets--org--dataset-name/
│  └─ spaces--org--space-name/
└─ .locks/
```

## Commands

### `hf-cache scan` — List all cached repos with details

```bash
hf-cache scan [--dir CACHE_DIR] [--sort {size,accessed,name}] [--limit N] [--json]
```

Output columns: Name, Type, Size, Revisions, Last Accessed, Status.

Status indicators:
- `active` — has current refs pointing to blobs
- `detached` — no refs (safe to prune)
- `partial` — some refs missing blobs

### `hf-cache info REPO_ID` — Show details for a specific cached repo

```bash
hf-cache info mistralai/Mistral-7B-Instruct-v0.1
```

Shows: total size, each revision with blob count and individual sizes, last-accessed timestamps.

### `hf-cache prune` — Remove detached revisions system-wide

```bash
hf-cache prune [--dir CACHE_DIR] [--dry-run] [--yes]
```

Safely removes only blobs that no revision points to. Use `--dry-run` to preview first.

Equivalent to `hf cache prune` but with richer output and size estimation.

### `hf-cache rm TARGET` — Remove specific repos or revisions

```bash
hf-cache rm mistralai/Mistral-7B-Instruct-v0.1
hf-cache rm mistralai/Mistral-7B-Instruct-v0.1 --revision main
```

Accepts: repo IDs, glob patterns (`gpt2*`), or `--all-detached`.

### `hf-cache gc` — Garbage collect old caches

```bash
hf-cache gc [--older-than DAYS] [--dry-run]
```

Removes repos not accessed in N days (default 30). Shows affected repos and total space before confirmation.

## Quick reference

| Command | What it does | Safe? |
|---------|-------------|-------|
| `hf-cache scan` | List everything | ✅ Read-only |
| `hf-cache info <repo>` | Detail one repo | ✅ Read-only |
| `hf-cache prune` | Remove detached blobs | ✅ Only unreferenced data |
| `hf-cache rm <id>` | Delete specific repo | ⚠️ Confirm first |
| `hf-cache gc --older-than 30` | Remove old caches | ⚠️ Confirm first |

## Examples

```bash
# What's eating my disk?
hf-cache scan --sort size --limit 10

# Any junk to clean?
hf-cache prune --dry-run

# Yes, clean it
hf-cache prune --yes

# Remove models I haven't touched in 60 days
hf-cache gc --older-than 60 --dry-run
hf-cache gc --older-than 60

# Remove a specific model
hf-cache rm meta-llama/Llama-3.1-8B-Instruct
```
