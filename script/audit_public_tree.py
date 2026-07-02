"""Audit tracked files before publishing SpectraMatrix.

This script checks Git-tracked files, not every local ignored artifact. It is
intended to catch accidental commits of private data, diagnostics, local paths,
or AI-agent workspace traces before a push.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


BLOCKED_PATH_PARTS = (
    ".codex/",
    ".agents/",
    "AGENTS.md",
    "datasets/",
    "diagnostics/",
    "imports/",
    "logs/",
    "matrices/",
    "outputs/",
    "projects/",
    "results/",
    "examples/yam_sulfite/",
    "演示数据集/",
)

SENSITIVE_TEXT = re.compile(
    r"(/Users/|多设备共享|Final Project|03-数据分析|6617|"
    r"Codex|codex|ChatGPT|chatgpt|Claude|claude|"
    r"OpenAI|openai|gpt-source)",
)

TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".swift",
    ".toml",
    ".txt",
    ".command",
    ".ps1",
}

SKIP_TEXT_SCAN = {
    "packages/spectral_core/src/spectral_core/api/static/vendor/tabler-icons.min.css",
    "script/audit_public_tree.py",
}


def git_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True)
    return [line for line in result.stdout.splitlines() if line]


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def main() -> None:
    failures: list[str] = []
    for file_name in git_files():
        normalized = file_name.replace("\\", "/")
        for blocked in BLOCKED_PATH_PARTS:
            if normalized == blocked.rstrip("/") or normalized.startswith(blocked):
                failures.append(f"blocked tracked path: {file_name}")
        path = Path(file_name)
        if normalized not in SKIP_TEXT_SCAN and path.exists() and is_text_candidate(path):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            match = SENSITIVE_TEXT.search(text)
            if match:
                failures.append(f"sensitive text '{match.group(0)}' in {file_name}")

    if failures:
        print("Public tree audit failed:")
        for item in failures:
            print(f"- {item}")
        raise SystemExit(1)

    print("Public tree audit passed.")


if __name__ == "__main__":
    main()
