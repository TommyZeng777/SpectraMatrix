# Data Boundary And Privacy Model

This document defines how SpectraMatrix separates public source code from private laboratory assets.

## Core Rule

The GitHub repository should contain:

- source code
- import templates
- generic configuration templates
- documentation
- tiny synthetic examples that can be regenerated

The GitHub repository should not contain:

- real spectral CSV/NPZ files
- supervision labels from laboratory experiments
- generated task matrices
- project files that point to private paths
- model checkpoints or metrics produced from private data
- diagnostic logs
- local launcher logs
- app bundles or build caches

## Recommended Local Layout

Keep the public checkout and private assets as siblings:

```text
work/
├── SpectraMatrix/                  # public Git checkout
└── SpectraMatrix_PrivateAssets/     # never committed
    ├── datasets/
    ├── projects/
    ├── matrices/
    ├── results/
    └── diagnostics/
```

The public app can still read local files through browser import, CLI arguments, or local project files. The important rule is that those assets remain outside Git tracking.

## Repository Ignore Policy

The default `.gitignore` excludes common runtime folders:

```text
datasets/
diagnostics/
imports/
logs/
matrices/
outputs/
projects/
results/
演示数据集/
```

Private domain adapters and realistic-case configs are also excluded by default.

## Local Path Template

Use this file as a template when documenting local folders:

```text
configs/local_paths.example.json
```

Do not commit a copied config that points to private data. If a user needs a machine-specific local path file, place it under `projects/`, `imports/`, or another ignored folder.

## Public Audit Before Push

Run this before publishing:

```bash
python script/audit_public_tree.py
```

The audit checks Git-tracked files for blocked runtime folders, local absolute paths, internal project names, and agent-workspace traces.

For a manual check:

```bash
git status --short
git ls-files
git diff --cached --stat
```

## Sharing Data Privately

For collaboration, share private data through an approved private channel, for example:

- institutional storage
- private Git LFS repository
- encrypted archive
- private cloud folder with access control

Do not use the public GitHub repository as a data transport channel.

## Why This Matters

Spectral datasets are often small enough to upload accidentally but sensitive enough to create privacy, publication, or intellectual-property problems. Keeping data outside Git also makes clone, install, CI, and issue triage much faster for external users.
