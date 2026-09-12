#!/usr/bin/env bash
# Fase 2 del skill sugar-plugin-syntax-migration: deteccion de discriminador
# de sub-operacion (candidato a renombrar a "operator"). SOLO REPORTA, no
# escribe nada. La decision de aplicar el rename puntual queda para revision
# humana/manual por lo ambiguo que puede ser (ver SKILL.md, Fase 2).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
EXCLUDE_DIR="selenium_plugin"
CANDIDATES=(operator action command cmd mode type op method)

cd "$SRC_DIR"

printf "%-24s %-12s %-8s %s\n" "plugin" "discriminador" "conteo" "estado"
printf "%-24s %-12s %-8s %s\n" "------" "-------------" "------" "------"

for plugin_dir in */; do
  plugin="${plugin_dir%/}"
  [ "$plugin" = "$EXCLUDE_DIR" ] && continue
  [ "$plugin" = "docs" ] && continue

  manifest="$plugin/plugin.json"
  if [ -f "$manifest" ]; then
    main_rel=$(grep -oE '"main"\s*:\s*"[^"]+"' "$manifest" | head -1 | sed -E 's/.*"main"\s*:\s*"([^"]+)".*/\1/' || true)
  else
    main_rel=""
  fi

  if [ -n "$main_rel" ] && [ -f "$plugin/$main_rel" ]; then
    main_file="$plugin/$main_rel"
  else
    main_file=$(find "$plugin" -iname "*plugin.py" ! -path "*/tests/*" 2>/dev/null | head -1)
  fi

  if [ -z "$main_file" ] || [ ! -f "$main_file" ]; then
    printf "%-24s %-12s %-8s %s\n" "$plugin" "-" "-" "sin archivo principal detectado"
    continue
  fi

  exec_line=$(grep -n "def execute" "$main_file" | head -1 | cut -d: -f1 || true)
  if [ -z "$exec_line" ]; then
    printf "%-24s %-12s %-8s %s\n" "$plugin" "-" "-" "sin def execute en $main_file"
    continue
  fi

  window_end=$((exec_line + 15))
  window=$(sed -n "${exec_line},${window_end}p" "$main_file")

  found=""
  found_count=0
  for c in "${CANDIDATES[@]}"; do
    cnt=$(echo "$window" | grep -cE "config(\.get\(|\[)['\"]${c}['\"]" || true)
    if [ "$cnt" -gt 0 ]; then
      total_in_file=$(grep -cE "config(\.get\(|\[)['\"]${c}['\"]" "$main_file" || true)
      found="$found $c($cnt/$total_in_file)"
      found_count=$((found_count + 1))
    fi
  done

  if [ "$found_count" -eq 0 ]; then
    printf "%-24s %-12s %-8s %s\n" "$plugin" "-" "0" "ambiguo: sin candidato en despacho (revisar manual)"
  elif [ "$found_count" -eq 1 ]; then
    key=$(echo "$found" | sed -E 's/^\s*([a-z]+).*/\1/')
    if [ "$key" = "operator" ]; then
      printf "%-24s %-12s %-8s %s\n" "$plugin" "$key" "-" "OK: ya usa operator"
    else
      printf "%-24s %-12s %-8s %s\n" "$plugin" "$key" "$found" "candidato unico -> revisar y migrar puntualmente"
    fi
  else
    printf "%-24s %-12s %-8s %s\n" "$plugin" "-" "$found" "ambiguo: multiples candidatos (revisar manual)"
  fi
done
