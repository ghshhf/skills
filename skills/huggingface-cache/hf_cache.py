#!/usr/bin/env python3
"""HuggingFace Cache Manager — scan, analyze, and clean local HF cache."""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/huggingface/hubs")
BYTES_GB = 1024**3
BYTES_MB = 1024**2


# ── Core scanning ────────────────────────────────────────────────────────

def scan_cache(cache_dir: str = DEFAULT_CACHE_DIR) -> List[dict]:
    """Scan HF cache and return list of cached repos with metadata."""
    repos = []
    if not os.path.isdir(cache_dir):
        return repos

    for entry in sorted(os.listdir(cache_dir)):
        full = os.path.join(cache_dir, entry)
        if not os.path.isdir(full):
            continue
        # Parse repo type and id from dir name: "models--org--name"
        parts = entry.split("--", 2)
        if len(parts) < 3:
            continue
        repo_type, org, name = parts[0], parts[1], parts[2]

        # Gather revision info
        revisions = _scan_revisions(full)
        total_size = sum(r["size"] for r in revisions)
        last_accessed = max((r["accessed"] for r in revisions), default=0)

        # Status: active if any revision has refs
        has_refs = any(r.get("has_refs") for r in revisions)
        status = "active" if has_refs else "detached"

        repos.append({
            "repo_id": f"{org}/{name}",
            "type": repo_type,
            "path": full,
            "size": total_size,
            "size_human": _human_size(total_size),
            "revisions": revisions,
            "revision_count": len(revisions),
            "last_accessed": last_accessed,
            "last_accessed_str": _time_ago(last_accessed) if last_accessed else "never",
            "status": status,
        })

    return repos


def _scan_revisions(repo_dir: str) -> List[dict]:
    """Scan revisions (snapshots) for a repo."""
    snapshots_dir = os.path.join(repo_dir, "snapshots")
    blobs_dir = os.path.join(repo_dir, "blobs")
    refs_dir = os.path.join(repo_dir, "refs")

    revisions = []
    if not os.path.isdir(snapshots_dir):
        # Fallback: check blobs directly
        if os.path.isdir(blobs_dir):
            blobs = _scan_blobs(blobs_dir)
            total = sum(b["size"] for b in blobs)
            revisions.append({
                "revision": "(blobs only)",
                "blobs": blobs,
                "size": total,
                "size_human": _human_size(total),
                "accessed": _max_blob_time(blobs),
                "has_refs": False,
            })
        return revisions

    # Get ref→blob mapping from refs
    ref_map = _parse_refs(refs_dir)

    for snap in sorted(os.listdir(snapshots_dir)):
        snap_dir = os.path.join(snapshots_dir, snap)
        if not os.path.isdir(snap_dir):
            continue
        blobs = _scan_blobs(snap_dir, blobs_dir)
        total = sum(b["size"] for b in blobs)
        accessed = _max_blob_time(blobs)
        has_refs = snap in ref_map

        revisions.append({
            "revision": snap,
            "blobs": blobs,
            "size": total,
            "size_human": _human_size(total),
            "accessed": accessed,
            "accessed_str": _time_ago(accessed) if accessed else "unknown",
            "has_refs": has_refs,
        })

    return revisions


def _scan_blobs(dir_path: str, blobs_base: str = None) -> List[dict]:
    """Scan blob files in a directory. If blobs_base is given, resolve symlinks there."""
    blobs = []
    try:
        for fname in sorted(os.listdir(dir_path)):
            fpath = os.path.join(dir_path, fname)
            if os.path.islink(fpath) and blobs_base:
                # Symlink in snapshot → real blob in blobs/
                real = os.path.realpath(fpath)
            else:
                real = fpath
            if os.path.isfile(real):
                st = os.stat(real)
                blobs.append({
                    "name": fname,
                    "size": st.st_size,
                    "size_human": _human_size(st.st_size),
                    "accessed": st.st_atime,
                })
    except PermissionError:
        pass
    return blobs


def _parse_refs(refs_dir: str) -> Dict[str, str]:
    """Parse ref files to map revision hash → blob hash."""
    ref_map = {}
    if not os.path.isdir(refs_dir):
        return ref_map
    for ref_name in sorted(os.listdir(refs_dir)):
        ref_path = os.path.join(refs_dir, ref_name)
        if os.path.isfile(ref_path):
            try:
                with open(ref_path) as f:
                    ref_map[ref_name] = f.read().strip()
            except (OSError, UnicodeDecodeError):
                pass
    return ref_map


def _max_blob_time(blobs: List[dict]) -> int:
    if not blobs:
        return 0
    return max(b["accessed"] for b in blobs if b["accessed"] > 0)


# ── Display ──────────────────────────────────────────────────────────────

def cmd_scan(args):
    repos = scan_cache(args.dir or DEFAULT_CACHE_DIR)
    if not repos:
        print("No cached models/datasets/spaces found.")
        return

    # Sort
    sort_key = args.sort or "size"
    repos.sort(key=lambda r: r.get(sort_key, 0) or 0, reverse=True)

    if args.limit:
        repos = repos[:args.limit]

    if args.json:
        print(json.dumps(repos, indent=2))
        return

    # Table output
    total_size = sum(r["size"] for r in repos)
    print(f"\n{'='*90}")
    print(f"  HF Cache Scan — {len(repos)} repos — total: {_human_size(total_size)}")
    print(f"  Directory: {args.dir or DEFAULT_CACHE_DIR}")
    print(f"{'='*90}")
    print(f"{'Repo':<40} {'Type':<9} {'Size':>8} {'Revs':>4} {'Last Used':>12} {'Status':>10}")
    print(f"{'-'*40} {'-'*9} {'-'*8} {'-'*4} {'-'*12} {'-'*10}")

    for r in repos:
        flags = ""
        if r["status"] == "detached":
            flags = " 🔴"
        print(f"{r['repo_id']:<40} {r['type']:<9} {r['size_human']:>8} {r['revision_count']:>4} {r['last_accessed_str']:>12} {r['status']+' '+flags:>10}")

    print(f"{'='*90}\n")


def cmd_info(args):
    repos = scan_cache(args.dir or DEFAULT_CACHE_DIR)
    target = next((r for r in repos if r["repo_id"] == args.repo_id), None)
    if not target:
        print(f"Repository '{args.repo_id}' not found in cache.")
        return

    print(f"\n  Repo: {target['repo_id']}")
    print(f"  Type: {target['type']}")
    print(f"  Size: {target['size_human']}")
    print(f"  Status: {target['status']}")
    print(f"  Last accessed: {target['last_accessed_str']}")
    print(f"  Revisions: {target['revision_count']}\n")

    for rev in target["revisions"]:
        print(f"  [{rev['revision']}]  {rev['size_human']}  {'(ref)' if rev.get('has_refs') else '(detached)'}")
        for blob in rev["blobs"][:5]:
            print(f"    {blob['name'][:60]:<62} {blob['size_human']:>8}")
        if len(rev["blobs"]) > 5:
            print(f"    ... and {len(rev['blobs']) - 5} more blobs")
        print()

    # Cross-revision deduplication insight
    all_blobs = {}
    for rev in target["revisions"]:
        for b in rev["blobs"]:
            all_blobs[b["name"]] = all_blobs.get(b["name"], 0) + 1
    shared = sum(1 for c in all_blobs.values() if c > 1)
    if shared:
        print(f"  {shared} blobs shared across multiple revisions (deduplicated in cache)\n")


def cmd_prune(args):
    cache_dir = args.dir or DEFAULT_CACHE_DIR
    repos = scan_cache(cache_dir)

    detached = [r for r in repos if r["status"] == "detached"]
    if not detached:
        print("No detached revisions found. Cache is clean.")
        return

    total_free = sum(r["size"] for r in detached)
    print(f"\n  Found {len(detached)} detached repos — {_human_size(total_free)} can be freed:")
    for r in detached:
        print(f"    {r['repo_id']:<40} {r['size_human']:>8}  (last used: {r['last_accessed_str']})")

    if args.dry_run:
        print(f"\n  [DRY RUN] Would free {_human_size(total_free)}. Use --yes to execute.")
        return

    if not args.yes:
        resp = input(f"\n  Delete {len(detached)} repos to free {_human_size(total_free)}? [y/N] ")
        if resp.lower() != "y":
            print("  Cancelled.")
            return

    for r in detached:
        try:
            shutil.rmtree(r["path"])
            print(f"  Deleted: {r['repo_id']} ({r['size_human']})")
        except Exception as e:
            print(f"  Failed: {r['repo_id']} — {e}")

    print(f"\n  Freed {_human_size(total_free)}.")


def cmd_rm(args):
    cache_dir = args.dir or DEFAULT_CACHE_DIR
    repos = scan_cache(cache_dir)

    if args.all_detached:
        targets = [r for r in repos if r["status"] == "detached"]
    else:
        # Match by repo_id: exact match or fuzzy (contains)
        targets = [r for r in repos if args.target.lower() in r["repo_id"].lower()]

    if not targets:
        print(f"No cached repos matching '{args.target}' found.")
        return

    total = sum(r["size"] for r in targets)
    print(f"\n  Will remove {len(targets)} repos ({_human_size(total)}):")
    for r in targets:
        note = ""
        if r["status"] == "active":
            note = " ⚠️ ACTIVE"
        print(f"    {r['repo_id']:<40} {r['size_human']:>8}{note}")

    if args.dry_run:
        print(f"\n  [DRY RUN] Would free {_human_size(total)}. Use --yes to execute.")
        return

    if not args.yes:
        resp = input(f"\n  Confirm delete? [y/N] ")
        if resp.lower() != "y":
            print("  Cancelled.")
            return

    for r in targets:
        try:
            shutil.rmtree(r["path"])
            print(f"  Deleted: {r['repo_id']}")
        except Exception as e:
            print(f"  Failed: {r['repo_id']} — {e}")

    print(f"\n  Freed {_human_size(total)}.")


def cmd_gc(args):
    cache_dir = args.dir or DEFAULT_CACHE_DIR
    repos = scan_cache(cache_dir)
    older_than = args.older_than or 30
    cutoff = time.time() - older_than * 86400

    old = [r for r in repos if 0 < r["last_accessed"] < cutoff]
    never = [r for r in repos if r["last_accessed"] == 0]
    targets = old + never

    if not targets:
        print(f"No repos unused for >{older_than} days.")
        return

    total = sum(r["size"] for r in targets)
    print(f"\n  {len(targets)} repos unused for >{older_than} days — {_human_size(total)} can be freed:")
    for r in targets:
        print(f"    {r['repo_id']:<40} {r['size_human']:>8}  ({r['last_accessed_str']})")

    if args.dry_run:
        print(f"\n  [DRY RUN] Would free {_human_size(total)}. Use --yes to execute.")
        return

    if not args.yes:
        resp = input(f"\n  Delete all {len(targets)} repos? [y/N] ")
        if resp.lower() != "y":
            print("  Cancelled.")
            return

    for r in targets:
        try:
            shutil.rmtree(r["path"])
            print(f"  Deleted: {r['repo_id']}")
        except Exception as e:
            print(f"  Failed: {r['repo_id']} — {e}")

    print(f"\n  Freed {_human_size(total)}.")


# ── Helpers ──────────────────────────────────────────────────────────────

def _human_size(size_bytes: int) -> str:
    if size_bytes >= BYTES_GB:
        return f"{size_bytes / BYTES_GB:.1f} GB"
    if size_bytes >= BYTES_MB:
        return f"{size_bytes / BYTES_MB:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def _time_ago(timestamp: float) -> str:
    diff = time.time() - timestamp
    if diff < 60:
        return "just now"
    if diff < 3600:
        return f"{int(diff / 60)}m ago"
    if diff < 86400:
        return f"{int(diff / 3600)}h ago"
    if diff < 604800:
        return f"{int(diff / 86400)}d ago"
    if diff < 2592000:
        return f"{int(diff / 604800)}w ago"
    return f"{int(diff / 2592000)}mo ago"


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="hf-cache",
        description="HuggingFace Cache Manager — scan, analyze, and clean local cache",
    )
    parser.add_argument("--dir", help="Cache directory (default: ~/.cache/huggingface/hubs)")

    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="List all cached repos")
    p_scan.add_argument("--sort", choices=["size", "accessed", "name"], default="size")
    p_scan.add_argument("--limit", type=int)
    p_scan.add_argument("--json", action="store_true")

    # info
    p_info = sub.add_parser("info", help="Detailed info for a cached repo")
    p_info.add_argument("repo_id")

    # prune
    p_prune = sub.add_parser("prune", help="Remove detached revisions")
    p_prune.add_argument("--dry-run", action="store_true")
    p_prune.add_argument("--yes", action="store_true")

    # rm
    p_rm = sub.add_parser("rm", help="Remove specific repos")
    p_rm.add_argument("target", help="Repo ID or glob pattern")
    p_rm.add_argument("--all-detached", action="store_true")
    p_rm.add_argument("--dry-run", action="store_true")
    p_rm.add_argument("--yes", action="store_true")

    # gc
    p_gc = sub.add_parser("gc", help="Garbage collect old caches")
    p_gc.add_argument("--older-than", type=int, default=30, help="Days (default: 30)")
    p_gc.add_argument("--dry-run", action="store_true")
    p_gc.add_argument("--yes", action="store_true")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "prune":
        cmd_prune(args)
    elif args.command == "rm":
        cmd_rm(args)
    elif args.command == "gc":
        cmd_gc(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
