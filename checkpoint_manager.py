#!/usr/bin/env python3
"""
checkpoint_manager.py - Automated Project Checkpoint & Rollback Utility
AI-Based Network Intrusion Detection System

Enables instant, lossless rollbacks to any previous working state if newly
modified content or deployment configurations are unsatisfactory.
Integrates with Git tags, commits, and snapshot records.
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def run_cmd(args):
    """Executes a subprocess command in the project root."""
    try:
        res = subprocess.run(
            args,
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[!] Error executing {' '.join(args)}:\n{e.stderr.strip()}")
        return None

def save_checkpoint(name: str):
    """Saves the current project state into a tagged Git checkpoint."""
    clean_name = name.strip().replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_name = f"checkpoint_{clean_name}_{timestamp}"
    commit_msg = f"Checkpoint: {name} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"

    print(f"[*] Staging all changes for checkpoint: {tag_name}...")
    run_cmd(["git", "add", "."])

    # Check if anything changed to commit
    status = run_cmd(["git", "status", "--porcelain"])
    if status:
        run_cmd(["git", "commit", "-m", commit_msg])
        print(f"[+] Committed active changes: {commit_msg}")
    else:
        print("[*] No uncommitted file changes; tagging current commit.")

    run_cmd(["git", "tag", "-a", tag_name, "-m", commit_msg])
    print(f"[SUCCESS] Checkpoint saved successfully: {tag_name}")
    print(f"[*] To restore this checkpoint at any time, run:")
    print(f"    python checkpoint_manager.py rollback {tag_name}")

def rollback(checkpoint_tag: str):
    """Rolls back the entire project to the specified checkpoint tag or commit hash."""
    checkpoint_tag = checkpoint_tag.strip()
    print(f"[*] Initiating rollback to checkpoint: '{checkpoint_tag}'...")

    # Validate tag or commit exists
    verify = run_cmd(["git", "rev-parse", "--verify", checkpoint_tag])
    if not verify:
        print(f"[!] Checkpoint '{checkpoint_tag}' was not found.")
        print("[*] Run 'python checkpoint_manager.py list' to see all valid checkpoints.")
        return False

    # Force checkout the requested checkpoint
    out = run_cmd(["git", "checkout", "-f", checkpoint_tag])
    print(f"[SUCCESS] Successfully rolled back to: {checkpoint_tag}")
    print(out)
    return True

def list_checkpoints():
    """Lists all available checkpoints and tags in chronological order."""
    print("=" * 70)
    print("AI-BASED NIDS PLATFORM - AVAILABLE RECOVERY CHECKPOINTS")
    print("=" * 70)
    tags_output = run_cmd(["git", "tag", "-n9"])
    if not tags_output:
        print("[*] No custom checkpoints found.")
    else:
        for line in tags_output.splitlines():
            print(f" • {line}")

    print("\nRecent Git Commit History:")
    commits = run_cmd(["git", "log", "--oneline", "-n", "8"])
    if commits:
        for c in commits.splitlines():
            print(f"   {c}")
    print("=" * 70)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python checkpoint_manager.py save <checkpoint_name>")
        print("  python checkpoint_manager.py rollback <checkpoint_tag>")
        print("  python checkpoint_manager.py list")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "save":
        name = sys.argv[2] if len(sys.argv) > 2 else "manual_snapshot"
        save_checkpoint(name)
    elif cmd == "rollback":
        if len(sys.argv) < 3:
            print("[!] Please provide the checkpoint tag to roll back to.")
            list_checkpoints()
            sys.exit(1)
        rollback(sys.argv[2])
    elif cmd in ("list", "ls"):
        list_checkpoints()
    else:
        print(f"[!] Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
