#!/usr/bin/env bash
# Fase 1 del skill sugar-plugin-syntax-migration: result -> id
# Uso:
#   ./01_migrate_result_to_id.sh            # dry-run: solo lista archivos afectados
#   ./01_migrate_result_to_id.sh --apply    # aplica los reemplazos
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
APPLY="${1:-}"
EXCLUDE_DIR="selenium_plugin"

cd "$SRC_DIR"

echo "== Regla A: config.get('result'/[\"result\"]) -> id  (todo .py) =="
py_files=$(grep -rlE "config(\.get\(['\"]result['\"]|\[['\"]result['\"]\])|self\.config(\.get\(['\"]result['\"]|\[['\"]result['\"]\])" --include="*.py" . 2>/dev/null | grep -v "/$EXCLUDE_DIR/" || true)

for f in $py_files; do
  n=$(grep -cE "config(\.get\(['\"]result['\"]|\[['\"]result['\"]\])" "$f" || true)
  echo "  $f ($n ocurrencias)"
  if [ "$APPLY" = "--apply" ]; then
    sed -i \
      -e "s/config\.get('result'/config.get('id'/g" \
      -e 's/config\.get("result"/config.get("id"/g' \
      -e "s/config\['result'\]/config['id']/g" \
      -e 's/config\["result"\]/config["id"]/g' \
      "$f"
  fi
done

echo ""
echo "== Regla B: 'result': / \"result\": -> id  (.json en cualquier lado, .py solo en tests/) =="
json_files=$(grep -rlE "['\"]result['\"]\s*:" --include="*.json" . 2>/dev/null | grep -v "/$EXCLUDE_DIR/" || true)
test_py_files=$(grep -rlE "['\"]result['\"]\s*:" --include="*.py" . 2>/dev/null | grep "/tests/" | grep -v "/$EXCLUDE_DIR/" || true)

for f in $json_files $test_py_files; do
  n=$(grep -cE "['\"]result['\"]\s*:" "$f" || true)
  echo "  $f ($n ocurrencias)"
  if [ "$APPLY" = "--apply" ]; then
    sed -i \
      -e "s/'result':/'id':/g" \
      -e 's/"result":/"id":/g' \
      "$f"
  fi
done

if [ "$APPLY" != "--apply" ]; then
  echo ""
  echo "(dry-run — correr con --apply para aplicar los cambios)"
  exit 0
fi

echo ""
echo "== Validacion (compile-check, no lectura completa) =="
fail=0
for f in $py_files $test_py_files; do
  if ! python3 -m py_compile "$f" 2>/tmp/py_compile_err; then
    echo "  FALLO py_compile: $f"
    cat /tmp/py_compile_err
    fail=1
  fi
done
for f in $json_files; do
  if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/tmp/json_err; then
    echo "  FALLO json: $f"
    cat /tmp/json_err
    fail=1
  fi
done
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

if [ "$fail" = "0" ]; then
  echo "  OK: todos los archivos tocados compilan / son JSON valido."
else
  echo "  Hubo fallos, revisar arriba."
fi
