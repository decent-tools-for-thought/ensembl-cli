# ensembl-cli

`ensemble` / `ensembl` is a self-documenting command-line client for the Ensembl REST API.

The command surface is generated from the official Ensembl REST documentation snapshot bundled with this repository, so every documented operation is available via the CLI.

## Development

Set up a repo-local environment with `uv`:

```bash
uv sync
uv run ensemble --help
```

Run directly from the checkout:

```bash
uv run python -m ensembl_cli.cli explain
uv run python -m ensembl_cli.cli api operations
```

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
uv run python scripts/update_metadata.py --source-dir .cache/ensembl-docs
```

## Releases

Tagging `v<version>` triggers GitHub Actions to publish:

- `ensembl-cli-<version>.tar.gz`
- `ensembl_cli-<version>.tar.gz`
- `ensembl_cli-<version>-py3-none-any.whl`
- `SHA256SUMS`

You can build a release-style archive locally with:

```bash
./scripts/build-release-archive.sh dist
```
