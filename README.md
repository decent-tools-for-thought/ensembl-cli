# ensembl-cli

[![Release](https://img.shields.io/github/v/release/decent-tools-for-thought/ensembl-cli?sort=semver)](https://github.com/decent-tools-for-thought/ensembl-cli/releases)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Self-documenting command-line client for the Ensembl REST API.

> [!IMPORTANT]
> This codebase is largely AI-generated. It is useful to me, I hope it might be useful to others, and issues and contributions are welcome.

## Why This Exists

- Expose the Ensembl REST surface as a discoverable CLI.
- Generate command help from a bundled documentation snapshot.
- Make ad hoc genomics API work easier from the shell.

## Install

```bash
python -m pip install .
ensembl --help
```

The package publishes both `ensembl` and `ensemble`; both invoke the same CLI.

For local development:

```bash
uv sync
uv run ensembl --help
```

## Quick Start

Discover operations:

```bash
ensembl explain
ensembl api operations --group Lookup
ensembl api show lookup
```

Make calls:

```bash
ensembl api call lookup ENSG00000157764
ensembl api call lookup_post --field 'ids=["ENSG00000157764","ENSG00000248378"]'
ensembl raw /info/ping
```

## Metadata Refresh

```bash
./scripts/prefetch_docs.sh .cache/ensembl-docs
uv run python scripts/update_metadata.py --source-dir .cache/ensembl-docs
```

## Development

```bash
uv run ruff check src tests
uv run mypy
uv run pytest
```

## Credits

This client depends on the Ensembl REST API and the Ensembl documentation set. Credit goes to the Ensembl project for the API design, data resources, and upstream docs this tool builds on.
