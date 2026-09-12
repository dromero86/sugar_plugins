#!/usr/bin/env python3
"""
Renombra un identificador (por defecto: command -> operator) SOLO dentro del
rango de lineas de la funcion execute(self, <old>: ...) de un archivo dado.
No lee/imprime el contenido del archivo -- solo reporta rango y conteo.
Uso: rename_param_scoped.py <archivo.py> [old] [new]
"""
import re
import sys


def process(path, old="command", new="operator"):
    with open(path, "r") as f:
        lines = f.readlines()

    start = None
    sig_re = re.compile(rf"def execute\(self,\s*{re.escape(old)}\b")
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(("'", '"', "#")):
            continue  # string literal / comment, no una firma real
        if sig_re.search(line):
            start = i
            break
    if start is None:
        return False, "sin coincidencia de firma execute(self, %s...) real (no string/comentario)" % old

    indent = len(lines[start]) - len(lines[start].lstrip())
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].lstrip()
        if not stripped:
            continue
        cur_indent = len(lines[j]) - len(stripped)
        if stripped.startswith("def ") and cur_indent <= indent:
            end = j
            break

    word_re = re.compile(rf"\b{re.escape(old)}\b")
    changed = 0
    for k in range(start, end):
        new_line, n = word_re.subn(new, lines[k])
        if n:
            lines[k] = new_line
            changed += n

    if changed == 0:
        return False, "firma encontrada pero 0 reemplazos (raro, revisar)"

    with open(path, "w") as f:
        f.writelines(lines)

    return True, f"lineas {start + 1}-{end}, {changed} ocurrencias renombradas"


if __name__ == "__main__":
    path = sys.argv[1]
    old = sys.argv[2] if len(sys.argv) > 2 else "command"
    new = sys.argv[3] if len(sys.argv) > 3 else "operator"
    ok, msg = process(path, old, new)
    status = "OK" if ok else "SKIP"
    print(f"{status}: {path} -- {msg}")
