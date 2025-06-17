#!/usr/bin/env python3
"""
Script to collect all .py files in a project, excluding specified files and directories,
and write their names and contents to an output file in JSON format.
"""

import os
import fnmatch
import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect .py files from a project, excluding specified patterns."
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory of the project (default: current directory)."
    )
    parser.add_argument(
        "-o", "--output",
        default="collected_py_files.json",
        help="Output file to write the collected data (default: collected_py_files.json)."
    )
    parser.add_argument(
        "--exclude-files",
        nargs="*",
        default=["*.lock", "*~"],
        help="File patterns to exclude (default: ['*.lock', '*~'])."
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        default=["__pycache__", ".git", "node_modules", ".venv", "migrations"],
        help="Directory names to exclude (default: ['__pycache__', '.git', 'node_modules'])."
    )
    return parser.parse_args()


def should_exclude(name, patterns):
    """Check if a filename or directory matches any of the exclusion patterns."""
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def collect_py_files(root_dir, exclude_files, exclude_dirs):
    collected = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude specified directories in-place to avoid descending into them
        dirnames[:] = [d for d in dirnames if not should_exclude(d, exclude_dirs)]
        for filename in filenames:
            # Only .py files
            if not filename.endswith(".py"):
                continue
            # Skip excluded file patterns
            if should_exclude(filename, exclude_files):
                continue
            full_path = os.path.join(dirpath, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Warning: Could not read {full_path}: {e}")
                continue
            rel_path = os.path.relpath(full_path, root_dir)
            collected.append({
                "path": rel_path,
                "content": content
            })
    return collected


def main():
    args = parse_args()
    data = collect_py_files(args.root_dir, args.exclude_files, args.exclude_dirs)
    with open(args.output, "w", encoding="utf-8") as out_f:
        json.dump(data, out_f, ensure_ascii=False, indent=2)
    print(f"Collected {len(data)} .py files and wrote to {args.output}")


if __name__ == "__main__":
    main()
