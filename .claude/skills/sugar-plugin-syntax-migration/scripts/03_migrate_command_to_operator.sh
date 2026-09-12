#!/usr/bin/env bash
# Fase 2 (revisada) del skill sugar-plugin-syntax-migration:
# renombra el parametro posicional de execute(self, command: ...) a
# execute(self, operator: ...) -- SOLO dentro del cuerpo de esa funcion
# (rango de lineas acotado por rename_param_scoped.py), nunca en todo el
# archivo. command/operator llegan como parametro posicional desde
# PluginManager (ver hallazgo en SKILL.md); el JSON de instrucciones ya usa
# "operator" como clave en casi todos los plugins -- esto solo alinea el
# nombre del parametro Python con esa convencion.
#
# Uso:
#   ./03_migrate_command_to_operator.sh            # dry-run (detecta, no escribe)
#   ./03_migrate_command_to_operator.sh --apply    # aplica
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
APPLY="${1:-}"
EXCLUDE_DIR="selenium_plugin"

cd "$SRC_DIR"

files=$(grep -rlE "def execute\(self,\s*command\s*:" --include="*.py" . | grep -v "^\./$EXCLUDE_DIR/" | sort)

count=0
for f in $files; do
  count=$((count + 1))
  if [ "$APPLY" = "--apply" ]; then
    python3 "$SCRIPT_DIR/rename_param_scoped.py" "$f"
  else
    grep -n "def execute(self,\s*command" "$f" || true
    echo "  (dry-run) tocaria: $f"
  fi
done

echo ""
echo "Total archivos candidatos: $count"

if [ "$APPLY" != "--apply" ]; then
  echo "(dry-run -- correr con --apply para aplicar)"
  exit 0
fi

echo ""
echo "== Validacion (compile-check) =="
fail=0
for f in $files; do
  if ! python3 -m py_compile "$f" 2>/tmp/py_compile_err_op; then
    echo "  FALLO py_compile: $f"
    cat /tmp/py_compile_err_op
    fail=1
  fi
done
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

if [ "$fail" = "0" ]; then
  echo "  OK: todos los archivos tocados compilan."
else
  echo "  Hubo fallos, revisar arriba."
fi
