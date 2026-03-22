# ensembl-cli

`ensemble` / `ensembl` is a self-documenting command-line client for the Ensembl REST API.

The command surface is generated from the official Ensembl REST documentation snapshot bundled with this repository, so every documented operation is available via the CLI.

## Install

Install from a checkout:

```bash
python -m pip install .
ensembl --help
```

For isolated CLI installs, `pipx install .` also works.

The package publishes both `ensembl` and `ensemble` console scripts. The examples below use `ensembl`, but both names invoke the same CLI.

## Config

The CLI talks to `https://rest.ensembl.org` by default. Override the endpoint or timeout on any command:

```bash
ensembl --base-url https://rest.ensembl.org --timeout 10 api operations
```

Inspect the generated command model before making live requests:

```bash
ensembl explain
ensembl api show lookup
```

## Smoke Usage

Basic discovery and smoke checks:

```bash
ensembl api operations --group Lookup
ensembl api show lookup
ensembl raw /info/ping
```

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
ensembl api operations
ensembl api show lookup
ensembl api call lookup ENSG00000157764
ensembl api call lookup_post --field 'ids=["ENSG00000157764","ENSG00000248378"]'
ensembl raw /info/ping
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
