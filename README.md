<div align="center">

# ensembl-cli

[![Release](https://img.shields.io/github/v/release/decent-tools-for-thought/ensembl-cli?sort=semver&color=0f766e)](https://github.com/decent-tools-for-thought/ensembl-cli/releases)
![Python](https://img.shields.io/badge/python-3.11%2B-0ea5e9)
![License](https://img.shields.io/badge/license-MIT-14b8a6)

Self-documenting command-line client for inspecting and calling the bundled Ensembl REST API surface from the terminal.

</div>

> [!IMPORTANT]
> This codebase is entirely AI-generated. It is useful to me, I hope it might be useful to others, and issues and contributions are welcome.

## Map
$$\color{#0EA5E9}Tool \space \color{#14B8A6}Map$$
- [Install](#install)
- [Functionality](#functionality)
- [Quick Start](#quick-start)
- [Metadata Refresh](#metadata-refresh)
- [Credits](#credits)

## Install

```bash
python -m pip install .
ensembl --help
```

The package publishes both `ensembl` and `ensemble`; both invoke the same CLI.

## Functionality
$$\color{#0EA5E9}Core \space \color{#14B8A6}Features$$

### CLI Discovery
- `ensembl explain`: print the CLI mental model and the recommended discovery workflow.
- `ensembl api operations`: list every documented operation from the bundled Ensembl metadata snapshot.
- `ensembl api operations --group ...`: filter the operation catalog by functional group.
- `ensembl api operations --method GET|POST`: filter the operation catalog by HTTP method.
- `ensembl api operations --json`: emit machine-readable operation listings.
- `ensembl api show <operation>`: inspect one operation with its path, docs URL, parameters, and message formats.
- `ensembl api show <operation> --json`: emit the operation description as JSON.

### Documented API Calls
- `ensembl api call <operation> ...`: invoke any bundled documented operation by CLI name.
- `ensembl api call`: supports path parameters and generated flags for documented query and body parameters.
- `ensembl api call`: supports boolean flags, repeated array parameters, JSON request bodies via `--body`, body files via `--body-file`, and top-level field assignment via `--field KEY=VALUE`.
- `ensembl api call`: supports extra headers, explicit `Accept`, explicit request `Content-Type`, compact JSON output, base URL overrides, and timeout control.

### Raw Requests
- `ensembl raw <path-or-url>`: call an arbitrary relative API path or full URL.
- `ensembl raw`: supports `GET` and `POST`, repeatable query parameters, raw JSON body input, body files, field-based JSON construction, extra headers, compact output, base URL overrides, and timeout control.

## Quick Start
$$\color{#0EA5E9}Quick \space \color{#14B8A6}Start$$

```bash
ensembl explain
ensembl api operations --group Lookup
ensembl api show lookup

ensembl api call lookup ENSG00000157764
ensembl api call lookup_post --field 'ids=["ENSG00000157764","ENSG00000248378"]'
ensembl raw /info/ping
```

## Metadata Refresh
$$\color{#0EA5E9}Metadata \space \color{#14B8A6}Refresh$$

```bash
./scripts/prefetch_docs.sh .cache/ensembl-docs
uv run python scripts/update_metadata.py --source-dir .cache/ensembl-docs
```

## Credits
$$\color{#0EA5E9}Project \space \color{#14B8A6}Credits$$

This client is built for the Ensembl REST API and is not affiliated with Ensembl.

Credit goes to the Ensembl project for the upstream API design, data resources, and documentation snapshot this tool builds on.
