#!/usr/bin/env bash
set -euo pipefail

outdir="${1:-dist}"
mkdir -p "${outdir}"

version="$(
  python3 - <<'PY'
from pathlib import Path
import tomllib

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(data["project"]["version"])
PY
)"

archive_name="ensembl-cli-${version}.tar.gz"
prefix="ensembl-cli-${version}/"
tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT

file_list="${tmpdir}/files.txt"
raw_list="${tmpdir}/files.raw"
git ls-files --cached -z > "${raw_list}"
python3 - "${raw_list}" "${file_list}" "${outdir}" <<'PY'
from pathlib import Path
import sys

raw_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
outdir = Path(sys.argv[3]).resolve()
paths = [item for item in raw_path.read_bytes().split(b"\0") if item]
existing = sorted(
    Path(item.decode("utf-8"))
    for item in paths
    if Path(item.decode("utf-8")).exists()
    and not Path(item.decode("utf-8")).resolve().is_relative_to(outdir)
)
output_path.write_text("".join(f"{path.as_posix()}\n" for path in existing), encoding="utf-8")
PY

tar \
  --create \
  --gzip \
  --file "${outdir}/${archive_name}" \
  --directory . \
  --owner=0 \
  --group=0 \
  --numeric-owner \
  --mtime='UTC 1970-01-01' \
  --transform "s,^,${prefix}," \
  --files-from "${file_list}"

sha256sum "${outdir}/${archive_name}" > "${outdir}/SHA256SUMS"

printf '%s\n' "${outdir}/${archive_name}"
