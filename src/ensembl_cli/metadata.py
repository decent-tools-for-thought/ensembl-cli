from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any


@dataclass(frozen=True)
class Parameter:
    name: str
    type: str
    description: str
    default: str
    examples: tuple[str, ...]
    required: bool
    location: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Parameter":
        return cls(
            name=payload["name"],
            type=payload.get("type", ""),
            description=payload.get("description", ""),
            default=payload.get("default", ""),
            examples=tuple(payload.get("examples", [])),
            required=bool(payload.get("required", False)),
            location=payload.get("location", "query"),
        )


@dataclass(frozen=True)
class MessageFormat:
    content_type: str
    format: str
    example: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MessageFormat":
        return cls(
            content_type=payload.get("content_type", ""),
            format=payload.get("format", ""),
            example=payload.get("example", ""),
        )


@dataclass(frozen=True)
class Operation:
    operation_id: str
    cli_name: str
    cli_alias: str
    group: str
    method: str
    path: str
    doc_url: str
    description: str
    path_params: tuple[str, ...]
    params: tuple[Parameter, ...]
    message_formats: tuple[MessageFormat, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Operation":
        return cls(
            operation_id=payload["operation_id"],
            cli_name=payload["cli_name"],
            cli_alias=payload["cli_alias"],
            group=payload["group"],
            method=payload["method"],
            path=payload["path"],
            doc_url=payload["doc_url"],
            description=payload.get("description", ""),
            path_params=tuple(payload.get("path_params", [])),
            params=tuple(Parameter.from_dict(item) for item in payload.get("params", [])),
            message_formats=tuple(MessageFormat.from_dict(item) for item in payload.get("message_formats", [])),
        )


@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    data_path = resources.files("ensembl_cli").joinpath("data/operations.json")
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_operations() -> tuple[Operation, ...]:
    return tuple(Operation.from_dict(item) for item in load_metadata()["operations"])


@lru_cache(maxsize=1)
def operations_by_id() -> dict[str, Operation]:
    mapping: dict[str, Operation] = {}
    for operation in load_operations():
        mapping[operation.operation_id] = operation
        mapping[operation.cli_name] = operation
        mapping[operation.cli_alias] = operation
    return mapping


def get_operation(key: str) -> Operation:
    try:
        return operations_by_id()[key]
    except KeyError as exc:
        raise KeyError(f"Unknown operation: {key}") from exc
