from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Any


INDEX_URL = "https://rest.ensembl.org/documentation/"
OUTPUT_PATH = Path("src/ensembl_cli/data/operations.json")


def fetch_url(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception:
        completed = subprocess.run(
            ["curl", "-sL", url],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout


def clean_text(value: str) -> str:
    text = value.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line and line != "-"]
    return "\n".join(lines).strip()


def extract_path_params(path: str) -> list[str]:
    return re.findall(r":([A-Za-z0-9_]+)", path)


def split_path(path: str) -> list[str]:
    return [segment for segment in path.strip().strip("/").split("/") if segment]


def normalize_path_from_example(path: str, example_path: str | None) -> str:
    if not example_path:
        return path
    path_segments = split_path(path)
    example_segments = split_path(example_path)
    if not path_segments or not example_segments:
        return path
    normalized: list[str] = []
    example_index = 0
    for segment in path_segments:
        if segment.startswith(":"):
            if example_index >= len(example_segments):
                continue
            normalized.append(segment)
            example_index += 1
            continue
        normalized.append(segment)
        if example_index < len(example_segments) and example_segments[example_index] == segment:
            example_index += 1
    if path.startswith("/"):
        return "/" + "/".join(normalized)
    return "/".join(normalized)


def parse_parameter_table(section: str, required: bool, path_params: set[str]) -> list[dict[str, Any]]:
    if "No required parameters" in section:
        return []
    table_match = re.search(r"<table[^>]*>(.*?)</table>", section, re.S)
    if not table_match:
        return []
    rows = re.findall(r"<tr>(.*?)</tr>", table_match.group(1), re.S)
    parameters: list[dict[str, Any]] = []
    for row in rows[1:]:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 5:
            continue
        name = clean_text(cells[0])
        if not name:
            continue
        parameters.append(
            {
                "name": name,
                "type": clean_text(cells[1]),
                "description": clean_text(cells[2]),
                "default": clean_text(cells[3]),
                "examples": clean_text(cells[4]).split("\n") if clean_text(cells[4]) else [],
                "required": required,
                "location": "path" if name in path_params else "query",
            }
        )
    return parameters


def parse_message_formats(page: str) -> list[dict[str, str]]:
    message_match = re.search(r"<h2>Message</h2>(.*?)(?:<h2>Example Requests</h2>|</div>\s*</div>)", page, re.S)
    if not message_match:
        return []
    table_match = re.search(r"<table[^>]*>(.*?)</table>", message_match.group(1), re.S)
    if not table_match:
        return []
    rows = re.findall(r"<tr>(.*?)</tr>", table_match.group(1), re.S)
    formats: list[dict[str, str]] = []
    for row in rows[1:]:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 3:
            continue
        formats.append(
            {
                "content_type": clean_text(cells[0]),
                "format": clean_text(cells[1]),
                "example": clean_text(cells[2]),
            }
        )
    return formats


def parse_example_request_path(page: str) -> str | None:
    match = re.search(r"<h2>Example Requests</h2>.*?<h3><a href=\"([^\"]+)\"", page, re.S)
    if not match:
        return None
    href = clean_text(match.group(1))
    return href.split("?", 1)[0]


def align_path_parameters(params: list[dict[str, Any]], path_params: list[str]) -> list[dict[str, Any]]:
    by_name = {item["name"]: index for index, item in enumerate(params)}
    required_indices = [index for index, item in enumerate(params) if item["required"]]
    required_index = 0
    consumed_indices: set[int] = set()
    aligned: list[dict[str, Any]] = []

    for placeholder in path_params:
        source_index: int | None = by_name.get(placeholder)
        if source_index is not None:
            item = dict(params[source_index])
        else:
            while required_index < len(required_indices) and required_indices[required_index] in consumed_indices:
                required_index += 1
            if required_index < len(required_indices):
                source_index = required_indices[required_index]
                required_index += 1
                item = dict(params[source_index])
                item["name"] = placeholder
            else:
                source_index = None
                item = {
                    "name": placeholder,
                    "type": "String",
                    "description": "",
                    "default": "",
                    "examples": [],
                    "required": True,
                    "location": "path",
                }
        item["location"] = "path"
        aligned.append(item)
        if source_index is not None:
            consumed_indices.add(source_index)

    remainder: list[dict[str, Any]] = []
    for index, item in enumerate(params):
        if index in consumed_indices:
            continue
        updated = dict(item)
        updated["location"] = "query"
        remainder.append(updated)
    return aligned + remainder


def parse_operation_page(page: str, fallback: dict[str, Any]) -> dict[str, Any]:
    title_match = re.search(r'<h1 id="title">(GET|POST)\s+([^<]+)</h1>', page)
    description_match = re.search(r'<div class="lead">\s*<p>(.*?)</p>', page, re.S)
    footer_match = re.search(r"Ensembl REST API \(Version ([^)]+)\).*?([A-Z][a-z]{2} \d{4})", page, re.S)
    method = fallback["method"]
    path = fallback["path"]
    if title_match:
        method = title_match.group(1).strip()
        path = clean_text(title_match.group(2))
    example_path = parse_example_request_path(page)
    path = normalize_path_from_example(path, example_path)
    path_params = extract_path_params(path)
    path_param_set = set(path_params)
    required_match = re.search(r"<h3>Required</h3>(.*?)(?:<h3>Optional</h3>|<h2>Message</h2>|<h2>Example Requests</h2>)", page, re.S)
    optional_match = re.search(r"<h3>Optional</h3>(.*?)(?:<h2>Message</h2>|<h2>Example Requests</h2>)", page, re.S)
    params = []
    if required_match:
        params.extend(parse_parameter_table(required_match.group(1), required=True, path_params=path_param_set))
    if optional_match:
        params.extend(parse_parameter_table(optional_match.group(1), required=False, path_params=path_param_set))
    params = align_path_parameters(params, path_params)
    return {
        "method": method,
        "path": path,
        "description": clean_text(description_match.group(1)) if description_match else fallback["description"],
        "doc_version": footer_match.group(1).strip() if footer_match else None,
        "doc_release": footer_match.group(2).strip() if footer_match else None,
        "path_params": extract_path_params(path),
        "params": params,
        "message_formats": parse_message_formats(page),
    }


def parse_index_page(index_html: str) -> tuple[list[dict[str, Any]], dict[str, str]]:
    footer_match = re.search(r"Ensembl REST API \(Version ([^)]+)\).*?([A-Z][a-z]{2} \d{4})", index_html, re.S)
    group_blocks = re.findall(
        r'<tr><td><h3 id="[^"]+">\s*(.*?)</h3></td><td></td></tr>.*?<tbody>(.*?)</tbody>',
        index_html,
        re.S,
    )
    operations: list[dict[str, Any]] = []
    for group_name, body in group_blocks:
        group = clean_text(group_name)
        rows = re.findall(r'<tr><td><a href="([^"]+)">(GET|POST)\s+([^<]+)</a>\s*</td><td>(.*?)</td></tr>', body, re.S)
        for doc_url, method, path, description in rows:
            operation_id = doc_url.rstrip("/").split("/")[-1]
            cli_alias = operation_id.replace("_", "-")
            operations.append(
                {
                    "operation_id": operation_id,
                    "cli_name": operation_id,
                    "cli_alias": cli_alias,
                    "group": group,
                    "method": method,
                    "path": clean_text(path),
                    "doc_url": doc_url,
                    "description": clean_text(description),
                }
            )
    metadata = {
        "docs_version": footer_match.group(1).strip() if footer_match else "",
        "docs_release": footer_match.group(2).strip() if footer_match else "",
    }
    return operations, metadata


def load_source_html(source_dir: Path | None) -> tuple[str, dict[str, str]]:
    if source_dir:
        index_html = (source_dir / "index.html").read_text(encoding="utf-8")
        pages: dict[str, str] = {}
        for path in (source_dir / "pages").glob("*.html"):
            pages[path.stem] = path.read_text(encoding="utf-8")
        return index_html, pages
    return fetch_url(INDEX_URL), {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh bundled Ensembl REST operation metadata.")
    parser.add_argument("--source-dir", type=Path, help="Read prefetched HTML from this directory instead of the network.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output JSON path.")
    args = parser.parse_args()

    index_html, cached_pages = load_source_html(args.source_dir)
    operations, index_metadata = parse_index_page(index_html)
    enriched: list[dict[str, Any]] = []
    for operation in operations:
        slug = operation["operation_id"]
        page = cached_pages.get(slug)
        if page is None:
            page = fetch_url(operation["doc_url"])
        page_metadata = parse_operation_page(page, operation)
        merged = {**operation, **page_metadata}
        enriched.append(merged)

    payload = {
        "metadata_version": "0.1.0",
        "source": INDEX_URL,
        "docs_version": index_metadata["docs_version"],
        "docs_release": index_metadata["docs_release"],
        "operation_count": len(enriched),
        "operations": enriched,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(enriched)} operations to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
