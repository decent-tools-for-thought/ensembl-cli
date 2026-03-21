# ensembl-cli

`ensemble` / `ensembl` is a self-documenting command-line client for the Ensembl REST API.

The command surface is generated from the official Ensembl REST documentation snapshot bundled with this repository, so every documented operation is available via the CLI.

## Development

Run directly from the checkout:

```bash
PYTHONPATH=src python -m ensembl_cli.cli explain
PYTHONPATH=src python -m ensembl_cli.cli api operations
```

## Arch package

This repository ships a `PKGBUILD` that installs from GitHub release artifacts:

```bash
makepkg -si
```

Release tarballs are published by GitHub Actions and consumed by the package definition in [PKGBUILD](/home/morty/Software/ensemble-cli/PKGBUILD).

## Usage

```bash
ensemble api operations
ensemble api show lookup
ensemble api call lookup ENSG00000157764
ensemble api call lookup_post --field 'ids=["ENSG00000157764","ENSG00000248378"]'
ensemble raw /info/ping
```

## Metadata refresh

Refresh the bundled Ensembl docs snapshot:

```bash
./scripts/prefetch_docs.sh .cache/ensembl-docs
python scripts/update_metadata.py --source-dir .cache/ensembl-docs
```

## Releases

Tagging `v<version>` triggers GitHub Actions to build:

- `ensembl-cli-<version>.tar.gz`
- `SHA256SUMS`

The release archive is deterministic and can be reproduced locally with:

```bash
./scripts/build-release-archive.sh dist
```
