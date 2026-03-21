from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from collections import defaultdict
from typing import Any

from . import __version__
from .client import DEFAULT_BASE_URL, EnsemblClient, EnsemblClientError
from .metadata import Operation, Parameter, get_operation, load_metadata, load_operations


def _param_flag(name: str) -> str:
    return f"--{name.replace('_', '-')}"


def _bool_type_name(type_name: str) -> bool:
    return "boolean" in type_name.lower()


def _array_type_name(type_name: str) -> bool:
    return "array" in type_name.lower()


def _format_param_help(parameter: Parameter) -> str:
    bits = []
    if parameter.description:
        bits.append(parameter.description)
    if parameter.type:
        bits.append(f"type: {parameter.type}")
    if parameter.default and parameter.default != "-":
        bits.append(f"default: {parameter.default}")
    if parameter.examples:
        bits.append(f"examples: {', '.join(parameter.examples)}")
    return " | ".join(bits).replace("%", "%%")


def _coerce_field_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _parse_field_assignments(values: list[str] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for item in values or []:
        if "=" not in item:
            raise ValueError(f"Expected KEY=VALUE, got: {item}")
        key, raw_value = item.split("=", 1)
        payload[key] = _coerce_field_value(raw_value)
    return payload


def _load_body(args: argparse.Namespace) -> Any:
    has_field = bool(getattr(args, "field", None))
    body_text = getattr(args, "body", None)
    body_file = getattr(args, "body_file", None)
    sources = sum(bool(item) for item in [has_field, body_text, body_file])
    if sources > 1:
        raise ValueError("Use only one of --body, --body-file, or --field")
    if body_text:
        return json.loads(body_text)
    if body_file:
        with open(body_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    if has_field:
        return _parse_field_assignments(args.field)
    return None


def _collect_extra_headers(header_items: list[str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in header_items or []:
        if ":" not in item:
            raise ValueError(f"Expected Header: Value, got: {item}")
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def _render_response(body: bytes, content_type: str, pretty: bool) -> str:
    text = body.decode("utf-8", errors="replace")
    lowered = (content_type or "").lower()
    if "json" in lowered:
        payload = json.loads(text)
        if pretty:
            return json.dumps(payload, indent=2, sort_keys=False)
        return json.dumps(payload, separators=(",", ":"))
    return text


def _build_common_call_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--accept", default="application/json", help="Response media type.")
    parser.add_argument(
        "--request-content-type",
        default="application/json",
        help="Request Content-Type header for payload submissions.",
    )
    parser.add_argument(
        "--header",
        action="append",
        help="Additional request header in the form 'Name: Value'. Repeatable.",
    )
    parser.add_argument(
        "--compact-output",
        action="store_true",
        help="Emit compact JSON instead of pretty-printed output.",
    )


def _build_operation_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser], operation: Operation) -> None:
    parser = subparsers.add_parser(
        operation.cli_name,
        aliases=[operation.cli_alias] if operation.cli_alias != operation.cli_name else [],
        help=f"{operation.method} {operation.path}",
        description=f"{operation.method} {operation.path}\n\n{operation.description}",
    )
    parser.set_defaults(handler=_handle_operation_call, operation=operation)
    for name in operation.path_params:
        parameter = next((item for item in operation.params if item.name == name), None)
        help_text = _format_param_help(parameter) if parameter else ""
        parser.add_argument(name, help=help_text)
    for parameter in operation.params:
        if parameter.location == "path":
            continue
        kwargs: dict[str, Any] = {
            "dest": parameter.name,
            "required": parameter.required,
            "help": _format_param_help(parameter),
        }
        if _bool_type_name(parameter.type):
            kwargs["action"] = argparse.BooleanOptionalAction
            kwargs["default"] = None
        elif _array_type_name(parameter.type):
            kwargs["nargs"] = "+"
        parser.add_argument(_param_flag(parameter.name), **kwargs)
    if operation.method == "POST" or operation.message_formats:
        parser.add_argument("--body", help="JSON payload literal.")
        parser.add_argument("--body-file", help="Path to a JSON payload file.")
        parser.add_argument(
            "--field",
            action="append",
            help="Top-level JSON field assignment in the form KEY=VALUE. VALUE is parsed as JSON when possible.",
        )
    _build_common_call_arguments(parser)


def build_parser() -> argparse.ArgumentParser:
    metadata = load_metadata()
    parser = argparse.ArgumentParser(
        description="Self-documenting command line client for the Ensembl REST API.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL.")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    explain = subparsers.add_parser("explain", help="Explain the CLI model and common workflows.")
    explain.set_defaults(handler=_handle_explain)

    api = subparsers.add_parser("api", help="Inspect or call the documented Ensembl REST operations.")
    api_subparsers = api.add_subparsers(dest="api_command")

    operations = api_subparsers.add_parser("operations", help="List all documented operations.")
    operations.add_argument("--group", help="Filter by group name.")
    operations.add_argument("--method", choices=["GET", "POST"], help="Filter by HTTP method.")
    operations.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    operations.set_defaults(handler=_handle_operations)

    show = api_subparsers.add_parser("show", help="Show one operation with parameters and message schema.")
    show.add_argument("operation")
    show.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    show.set_defaults(handler=_handle_show)

    call = api_subparsers.add_parser("call", help="Invoke a documented operation.")
    call_subparsers = call.add_subparsers(dest="operation_name")
    for operation in load_operations():
        _build_operation_parser(call_subparsers, operation)

    raw = subparsers.add_parser("raw", help="Call an arbitrary path or URL.")
    raw.add_argument("path", help="Relative API path or full URL.")
    raw.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method.")
    raw.add_argument(
        "--query",
        action="append",
        help="Query parameter in the form KEY=VALUE. Repeatable.",
    )
    raw.add_argument("--body", help="JSON payload literal.")
    raw.add_argument("--body-file", help="Path to a JSON payload file.")
    raw.add_argument(
        "--field",
        action="append",
        help="Top-level JSON field assignment in the form KEY=VALUE. VALUE is parsed as JSON when possible.",
    )
    _build_common_call_arguments(raw)
    raw.set_defaults(handler=_handle_raw)
    return parser


def _handle_explain(args: argparse.Namespace) -> int:
    lines = [
        "The CLI is generated from the official Ensembl REST documentation snapshot bundled with this package.",
        "",
        "Common workflows:",
        "  ensembl api operations",
        "  ensembl api show lookup",
        "  ensembl api call lookup ENSG00000157764",
        "  ensembl api call lookup_post --field ids='[\"ENSG00000157764\",\"ENSG00000248378\"]'",
        "  ensembl raw /lookup/id/ENSG00000157764",
        "",
        "Every documented operation is available under `ensembl api call <operation-id>`.",
        "Use `ensembl api operations` to discover operation IDs and `ensembl api show <operation-id>` to inspect parameters.",
    ]
    print("\n".join(lines))
    return 0


def _operation_to_dict(operation: Operation) -> dict[str, Any]:
    return {
        "operation_id": operation.operation_id,
        "cli_name": operation.cli_name,
        "cli_alias": operation.cli_alias,
        "group": operation.group,
        "method": operation.method,
        "path": operation.path,
        "doc_url": operation.doc_url,
        "description": operation.description,
        "path_params": list(operation.path_params),
        "params": [
            {
                "name": item.name,
                "type": item.type,
                "description": item.description,
                "default": item.default,
                "examples": list(item.examples),
                "required": item.required,
                "location": item.location,
            }
            for item in operation.params
        ],
        "message_formats": [
            {
                "content_type": item.content_type,
                "format": item.format,
                "example": item.example,
            }
            for item in operation.message_formats
        ],
    }


def _handle_operations(args: argparse.Namespace) -> int:
    operations = [
        operation
        for operation in load_operations()
        if (not args.group or operation.group.lower() == args.group.lower())
        and (not args.method or operation.method == args.method)
    ]
    if args.json:
        print(json.dumps([_operation_to_dict(item) for item in operations], indent=2))
        return 0
    grouped: dict[str, list[Operation]] = defaultdict(list)
    for operation in operations:
        grouped[operation.group].append(operation)
    for group in sorted(grouped):
        print(group)
        for operation in grouped[group]:
            print(f"  {operation.cli_name:<32} {operation.method:<4} {operation.path}")
    print(f"\n{len(operations)} operations")
    return 0


def _handle_show(args: argparse.Namespace) -> int:
    operation = get_operation(args.operation)
    if args.json:
        print(json.dumps(_operation_to_dict(operation), indent=2))
        return 0
    print(f"{operation.cli_name} ({operation.method} {operation.path})")
    print(operation.description)
    print(f"Group: {operation.group}")
    print(f"Docs: {operation.doc_url}")
    if operation.params:
        print("\nParameters:")
        for parameter in operation.params:
            required = "required" if parameter.required else "optional"
            print(f"  {parameter.name} [{parameter.location}, {required}]")
            details = _format_param_help(parameter)
            if details:
                print(f"    {details}")
    if operation.message_formats:
        print("\nMessage formats:")
        for item in operation.message_formats:
            print(f"  {item.content_type}: {item.format}")
            if item.example:
                print(f"    example: {item.example}")
    return 0


def _encode_path(path: str, values: dict[str, Any]) -> str:
    encoded = path
    for key, value in values.items():
        safe_value = urllib.parse.quote(str(value), safe=",:._-~")
        encoded = encoded.replace(f":{key}", safe_value)
    return encoded


def _build_query_from_namespace(operation: Operation, args: argparse.Namespace) -> dict[str, Any]:
    query: dict[str, Any] = {}
    for parameter in operation.params:
        if parameter.location == "path":
            continue
        value = getattr(args, parameter.name, None)
        if value is None:
            continue
        query[parameter.name] = value
    return query


def _make_client(args: argparse.Namespace) -> EnsemblClient:
    return EnsemblClient(base_url=args.base_url, timeout=args.timeout)


def _handle_operation_call(args: argparse.Namespace) -> int:
    operation: Operation = args.operation
    path_values = {name: getattr(args, name) for name in operation.path_params}
    query = _build_query_from_namespace(operation, args)
    body = _load_body(args)
    headers = _collect_extra_headers(args.header)
    client = _make_client(args)
    response = client.request(
        method=operation.method,
        path=_encode_path(operation.path, path_values),
        query=query,
        body=body,
        accept=args.accept,
        request_content_type=args.request_content_type,
        extra_headers=headers,
    )
    print(_render_response(response.body, response.content_type, pretty=not args.compact_output))
    return 0


def _parse_query_pairs(values: list[str] | None) -> dict[str, Any]:
    query: dict[str, Any] = {}
    for item in values or []:
        if "=" not in item:
            raise ValueError(f"Expected KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        query[key] = _coerce_field_value(value)
    return query


def _handle_raw(args: argparse.Namespace) -> int:
    client = _make_client(args)
    body = _load_body(args)
    headers = _collect_extra_headers(args.header)
    query = _parse_query_pairs(args.query)
    response = client.request(
        method=args.method,
        path=args.path,
        query=query,
        body=body,
        accept=args.accept,
        request_content_type=args.request_content_type,
        extra_headers=headers,
    )
    print(_render_response(response.body, response.content_type, pretty=not args.compact_output))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "api" and args.api_command is None:
        next(
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ).choices["api"].print_help()
        return 0
    if args.command == "api" and args.api_command == "call" and args.operation_name is None:
        api_parser = next(
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ).choices["api"]
        next(
            action
            for action in api_parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ).choices["call"].print_help()
        return 0
    try:
        return args.handler(args)
    except (EnsemblClientError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
