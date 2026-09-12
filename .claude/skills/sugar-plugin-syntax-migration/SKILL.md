---
name: sugar-plugin-syntax-migration
description: Migra la sintaxis de todos los plugins de este repo a las convenciones del plugin modelo (selenium_plugin) — clave de captura "id" (no "result") y discriminador "operator". Solo reemplazos quirúrgicos vía grep/sed, nunca lectura completa de archivos ni de documentación interna de cada plugin.
---

# sugar-plugin-syntax-migration

## Objetivo

Alinear la sintaxis de TODOS los plugins de `src/` con las convenciones que ya
usa `selenium_plugin` (plugin modelo, fijado en SUGAR-29):

1. **Clave de captura de resultado**: `"id"`, nunca `"result"`. Es la
   convención real de Sugar core (`PluginInstructionNode.py:66`, `"id" in
   self.config`) — cualquier plugin que lea `config.get('result', ...)` tiene
   el mismo bug que tenía `selenium_plugin` antes de SUGAR-29: la variable
   nunca se captura en memoria de Sugar.
2. **Discriminador de sub-operación**: `"operator"` (`{"plugin": {"operator":
   "click", ...}}`), no `"action"`/`"command"`/`"cmd"`/`"mode"`/`"type"`/`"op"`
   a nivel del despacho principal de la instrucción.

## Reglas duras (por qué existe este skill así)

- **Prohibido leer archivos completos.** Solo `grep`/`sed`/`wc -l`/`py_compile`/
  `json.load` sobre líneas puntuales. Si hace falta contexto, `grep -n -A/-B`
  con pocas líneas — nunca `Read` de un archivo entero.
- **Prohibido leer documentación interna de cada plugin** (`README.md`,
  `docs/`, docstrings largos). No es el objetivo y quema tokens sin aportar a
  la migración de sintaxis. Los `.md` NO se tocan en este skill.
- **El objetivo NO es que cada plugin funcione** — es que la sintaxis quede
  migrada. No hace falta entender la lógica de negocio de cada plugin, ni
  correr sus tests con dependencias reales, ni validar semántica. Solo
  sintaxis + que el archivo siga siendo Python/JSON válido (compile-check,
  no ejecución).
- Excluir siempre `selenium_plugin` (ya migrado, es el modelo) y `docs/`
  (no es un plugin).

## Fase 1 — `result` → `id` (totalmente automatizada, aplicar siempre)

Dos reglas de reemplazo, cada una acotada para no tocar nada fuera de su
propósito:

**Regla A — lectura de config (todo `.py`, sin excepción, src y tests):**
solo el patrón exacto `config.get('result'` / `config["result"]` /
`self.config...` — nunca un `['result']` suelto sobre un objeto arbitrario
(evita romper aserciones de test tipo `response['result']` que chequean un
campo de salida propio del plugin, no la config de captura de Sugar).

**Regla B — clave literal de diccionario (`'result':` / `"result":`):**
solo en `.json` (siempre son configs de instrucción, nunca output) y en
`.py` dentro de `tests/` (fixtures que imitan la config de instrucción,
mismo patrón validado en `test_selenium_plugin.py`). **Nunca en `src/*.py`**
— ahí un `"result": algo` casi siempre es una clave fija del dict de
retorno del propio plugin (dato de negocio), no la config de Sugar; renombrar
eso no aporta a la migración y puede confundir.

Ejecutar: `scripts/01_migrate_result_to_id.sh --apply` (sin `--apply` hace
dry-run, solo lista qué tocaría).

Validación post-aplicación (barata, no lectura completa):
`python3 -m py_compile` sobre cada `.py` tocado, `python3 -c "import
json,sys; json.load(open(sys.argv[1]))"` sobre cada `.json` tocado.

## Fase 2 — `operator` como discriminador

**Hallazgo clave (2026-09-12):** el discriminador de sub-operación NO viaja
dentro de `config` en ningún plugin — llega como **parámetro posicional**
de `execute()`, puesto ahí por `PluginManager` (repo `sugar` core) a partir
de la propia clave de la instrucción. El JSON de instrucciones de casi
todos los plugins YA usa `"operator"` como clave (confirmado en `sqlite`,
`rar`, etc.) — la única inconsistencia real era el NOMBRE del parámetro en
la firma de `execute()`: 37 de 38 archivos usaban `def execute(self,
command: str, config...)`, solo `selenium_plugin` usaba `operator`. Es
decir: no hubo que tocar la forma del JSON en absoluto para esta fase, solo
alinear el nombre del parámetro Python con la convención ya vigente en los
datos.

Un primer intento de detección buscando `config.get('operator'/'action'/...)`
dentro de `execute()` (guardado en `scripts/02_detect_operator_discriminator.sh`,
dejado como referencia histórica) dio falsos "ambiguo" en case todos los
plugins porque buscaba en el lugar equivocado — el discriminador nunca se
lee de `config`, se recibe como argumento. No usar ese script para repetir
esta fase; usar `03_migrate_command_to_operator.sh`.

**Procedimiento aplicado (`scripts/03_migrate_command_to_operator.sh` +
`scripts/rename_param_scoped.py`):**

1. Ubicar cada archivo con `def execute(self, command: ...)` (grep, todo el
   repo, sin necesidad de saber cuál es el archivo "principal" de cada
   plugin — cubre también plugins con varios archivos con `execute()`, ej.
   `gnupg/src/GnuPG*.py`).
2. Descartar coincidencias que sean string-literal/comentario, no firma real
   (heurística: la línea no empieza con `'`/`"`/`#` tras quitar indentación
   — encontrado un caso real: `smb/test_smb_basic.py:76`, código de ejemplo
   embebido como texto, sin método `execute()` de verdad en ese archivo).
3. Delimitar el cuerpo de la función (desde `def execute` hasta el próximo
   `def ` con indentación igual o menor) y renombrar `command` -> `operator`
   con reemplazo de palabra completa (`\bcommand\b`) **solo dentro de ese
   rango de líneas** — nunca en todo el archivo, para no tocar un `command`
   homónimo y no relacionado en otro método de la misma clase.
4. Validar con `py_compile` cada archivo tocado.

No hizo falta tocar ningún `examples/*.json`: ya usaban `"operator"`.

## Fase 3 — verificación exhaustiva (solo lectura)

`scripts/04_verify_all.sh` corre sobre los 34 plugins (excluye
`selenium_plugin` como modelo, `docs/` y `hash_functions/` como no-plugins)
y reporta por plugin: `result` residual en accesos a `config` (.py),
`result` como clave literal residual (`.json` y `tests/*.py`), firmas
reales de `execute(self, command...)` sin migrar (descartando decoys tipo
`smb/test_smb_basic.py`), fallos de `py_compile`, JSON inválido, y
coherencia (`operator`+`result` nunca en el mismo dict de instrucción de un
`examples/*.json`). No escribe nada. Corrida sobre los 34 plugins
(2026-09-12): 33/33 OK (excluyendo el modelo) — la única "falla" al incluir
`selenium_plugin` en la corrida son sus 3 archivos
`examples/{Driver,Selenium,Browser}.py`, wrappers standalone de Selenium
con un método `execute()` propio ajeno al contrato `PluginBase` (no son
plugins de Sugar, es código de ejemplo empaquetado junto al plugin) —
correctamente fuera de alcance.

## Reporte final

Al terminar cada corrida, imprimir una tabla `plugin | resultado` con estados:
`migrado (result->id)`, `operator ya correcto`, `operator migrado`,
`operator ambiguo — sin tocar`. No hace falta prosa adicional por plugin.
