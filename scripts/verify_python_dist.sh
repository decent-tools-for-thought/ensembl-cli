#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade build
python -m build

wheel_path="$(python - <<'PY'
from pathlib import Path

candidates = sorted(Path("dist").glob("*.whl"))
assert len(candidates) == 1, candidates
print(candidates[0])
PY
)"

sdist_path="$(python - <<'PY'
from pathlib import Path

candidates = sorted(Path("dist").glob("ensembl_cli-*.tar.gz"))
assert len(candidates) == 1, candidates
print(candidates[0])
PY
)"

verify_artifact() {
  local artifact_path="$1"
  local env_dir="$2"

  python -m venv "$env_dir"
  # shellcheck disable=SC1090
  . "$env_dir/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install "$artifact_path"
  python -c "import ensembl_cli"
  ensembl --help
}

verify_artifact "$wheel_path" ".venv-wheel-verify"
verify_artifact "$sdist_path" ".venv-sdist-verify"
