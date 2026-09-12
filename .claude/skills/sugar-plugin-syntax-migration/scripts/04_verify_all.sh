#!/usr/bin/env bash
# Fase 3 del skill sugar-plugin-syntax-migration: verificacion exhaustiva
# de las Fases 1 y 2 sobre TODOS los plugins. Solo lectura -- no escribe
# nada. Reporta OK/FALLA por plugin con el detalle puntual (grep, sin
# lectura completa de archivos).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
EXCLUDE=(selenium_plugin docs hash_functions)

cd "$SRC_DIR"

is_excluded() {
  local p="$1"
  for e in "${EXCLUDE[@]}"; do
    [ "$p" = "$e" ] && return 0
  done
  return 1
}

total=0
ok=0
fail=0

for plugin_dir in */; do
  plugin="${plugin_dir%/}"
  is_excluded "$plugin" && continue
  total=$((total + 1))
  issues=()

  # 1) result residual en .py (config access)
  hits=$(grep -rnE "config(\.get\(['\"]result['\"]|\[['\"]result['\"]\])" --include="*.py" "$plugin" 2>/dev/null || true)
  [ -n "$hits" ] && issues+=("result-en-config-access: $(echo "$hits" | head -3 | tr '\n' ' | ')")

  # 2) result residual como clave literal en .json y en tests/*.py
  hits=$(grep -rlE "['\"]result['\"]\s*:" --include="*.json" "$plugin" 2>/dev/null || true)
  hits2=$(grep -rlE "['\"]result['\"]\s*:" --include="*.py" "$plugin" 2>/dev/null | grep "/tests/" || true)
  all_hits="$hits"$'\n'"$hits2"
  all_hits=$(echo "$all_hits" | grep -v '^$' || true)
  [ -n "$all_hits" ] && issues+=("result-como-clave: $(echo "$all_hits" | head -3 | tr '\n' ' | ')")

  # 3) command residual en firma real de execute() (descartando decoys string/comentario)
  candidates=$(grep -rnE "def execute\(self,\s*command\s*:" --include="*.py" "$plugin" 2>/dev/null || true)
  real_command_hits=""
  if [ -n "$candidates" ]; then
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      file="${line%%:*}"
      rest="${line#*:}"
      lineno="${rest%%:*}"
      content=$(sed -n "${lineno}p" "$file" | sed -E 's/^[[:space:]]*//')
      case "$content" in
        \'*|\"*|\#*) ;; # decoy, ignorar
        *) real_command_hits="${real_command_hits}${line}\n" ;;
      esac
    done <<< "$candidates"
  fi
  [ -n "$real_command_hits" ] && issues+=("command-residual-en-execute: $(echo -e "$real_command_hits" | head -3 | tr '\n' ' | ')")

  # 4) compilacion python
  py_files=$(find "$plugin" -name "*.py" 2>/dev/null || true)
  compile_fail=""
  for f in $py_files; do
    python3 -m py_compile "$f" 2>/tmp/verify_pyc_err
    if [ $? -ne 0 ]; then
      compile_fail="${compile_fail}${f}: $(tr '\n' ' ' < /tmp/verify_pyc_err) | "
    fi
  done
  [ -n "$compile_fail" ] && issues+=("py_compile: $compile_fail")

  # 5) json valido
  json_files=$(find "$plugin" -name "*.json" 2>/dev/null || true)
  json_fail=""
  for f in $json_files; do
    err=$(python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>&1)
    if [ $? -ne 0 ]; then
      json_fail="${json_fail}${f}: $(echo "$err" | tail -1) | "
    fi
  done
  [ -n "$json_fail" ] && issues+=("json-invalido: $json_fail")

  # 6) coherencia result+operator en el mismo dict de instruccion (examples/*.json)
  coherence_fail=$(python3 - "$plugin" <<'PYEOF'
import json, sys, glob, os

plugin = sys.argv[1]
problems = []

def walk(obj, path):
    if isinstance(obj, dict):
        if "operator" in obj and "result" in obj:
            problems.append(f"{path}: dict con 'operator' y 'result' a la vez")
        for k, v in obj.items():
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]")

for f in glob.glob(os.path.join(plugin, "examples", "*.json")):
    try:
        data = json.load(open(f))
    except Exception:
        continue
    walk(data, f)

if problems:
    print(" | ".join(problems[:3]))
PYEOF
)
  [ -n "$coherence_fail" ] && issues+=("operator+result-juntos: $coherence_fail")

  if [ "${#issues[@]}" -eq 0 ]; then
    ok=$((ok + 1))
    printf "%-24s OK\n" "$plugin"
  else
    fail=$((fail + 1))
    printf "%-24s FALLA\n" "$plugin"
    for i in "${issues[@]}"; do
      printf "    - %s\n" "$i"
    done
  fi
done

find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "== Resumen: $ok/$total OK, $fail con hallazgos =="
