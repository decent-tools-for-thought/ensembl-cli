from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://rest.ensembl.org"


class EnsemblClientError(RuntimeError):
    pass


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text())


class EnsemblClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        *,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: Any = None,
        accept: str = "application/json",
        request_content_type: str = "application/json",
        extra_headers: dict[str, str] | None = None,
    ) -> Response:
        query_params: list[tuple[str, str]] = []
        for key, value in (query or {}).items():
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                query_params.extend((key, self._stringify(item)) for item in value)
            else:
                query_params.append((key, self._stringify(value)))
        if accept and not any(key == "content-type" for key, _ in query_params):
            query_params.append(("content-type", accept))

        path_value = path if path.startswith("http://") or path.startswith("https://") else f"{self.base_url}/{path.lstrip('/')}"
        if query_params:
            path_value = f"{path_value}?{urllib.parse.urlencode(query_params, doseq=True)}"

        data: bytes | None = None
        headers = {
            "Accept": accept,
        }
        if extra_headers:
            headers.update(extra_headers)

        if body is not None:
            if isinstance(body, bytes):
                data = body
            elif isinstance(body, str):
                data = body.encode("utf-8")
            else:
                data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = request_content_type
        elif request_content_type:
            headers.setdefault("Content-Type", request_content_type)

        request = urllib.request.Request(
            path_value,
            data=data,
            headers=headers,
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return Response(
                    status=response.status,
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=response.read(),
                )
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            raise EnsemblClientError(
                f"{exc.code} {exc.reason}\n{payload.decode('utf-8', errors='replace')}"
            ) from exc
        except urllib.error.URLError as exc:
            raise EnsemblClientError(str(exc.reason)) from exc

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, bool):
            return "1" if value else "0"
        return str(value)
