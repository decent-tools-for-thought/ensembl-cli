#!/usr/bin/env bash
set -euo pipefail

root="${1:-.cache/ensembl-docs}"

mkdir -p "${root}/pages"
curl -sL https://rest.ensembl.org/documentation/ > "${root}/index.html"

python3 - "${root}" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
index = (root / "index.html").read_text(encoding="utf-8")
urls = sorted(set(re.findall(r'href="(https://rest\.ensembl\.org/documentation/info/[^"]+)"', index)))
(root / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
print(len(urls))
PY

while IFS= read -r url; do
  [ -n "${url}" ] || continue
  slug="${url##*/}"
  curl -sL "${url}" > "${root}/pages/${slug}.html"
done < "${root}/urls.txt"
