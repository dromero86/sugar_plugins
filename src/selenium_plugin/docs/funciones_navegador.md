# Funciones del Navegador (Selenium Plugin)

> Este documento documentaba originalmente un plugin llamado `navigator_selenium`, con sintaxis `{"plugin": {"name": "navigator_selenium", "command": ..., "config": {...}}}`. Esa etapa quedó atrás: la especificación mutó hasta el plugin actual, `selenium_plugin` (v2.1.0), con la sintaxis unificada `{"selenium": {"operator": ..., ...}}`. Este documento está actualizado a esa versión actual.

Estas funciones permiten interactuar con un navegador web usando el plugin `selenium_plugin`.

## Plugin
`selenium_plugin` (comando: `selenium`)

## Uso

```json
{
    "task": [
        {
            "selenium": {
                "operator": "open",
                "url": "https://example.com",
                "result": "navigation_result"
            }
        }
    ]
}
```

## Sintaxis General

```json
{
  "selenium": {
    "operator": "nombre_del_operador",
    "...": "parámetros propios del operador",
    "result": "nombre_variable_resultado"
  }
}
```

Ver `docs/README.md` para la referencia completa de los 28 operadores disponibles. Los equivalentes directos de los comandos que documentaba `navigator_selenium` son:

| Comando `navigator_selenium` (histórico) | Operador `selenium_plugin` (actual) |
|---|---|
| `navigate` | `open` (o `navigate` para refresh/back/forward) |
| `click` | `click` |
| `input` | `type` |
| `wait` | `wait` |
| `screenshot` | `screenshot` |
| `javascript` | `javascript` |
| `http` | **No es parte de este plugin** — ver más abajo |

### Ejemplos de Uso

**Operaciones de Navegación:**
```json
{ "selenium": { "operator": "open", "url": "https://example.com", "result": "is_open" } }

{ "selenium": { "operator": "click", "selector": "#submit-button", "result": "click_result" } }

{ "selenium": { "operator": "type", "selector": "#username", "value": "user123", "result": "typed" } }
```

**Esperas:**
```json
{ "selenium": { "operator": "wait", "type": "element", "selector": ".dynamic-content", "result": "wait_result" } }
```

**Screenshot:**
```json
{ "selenium": { "operator": "screenshot", "file": "page_screenshot.png", "result": "screenshot_result" } }
```

## JAVASCRIPT

Ejecuta código JavaScript en la página actual.

### Operador
`javascript`

### Parámetros
- `from_string` (string): código JavaScript inline a ejecutar.
- `from_file` (string): ruta a un archivo `.js` a ejecutar.
- `result` (string): variable donde guardar el valor devuelto por el script.

### Ejemplos de Uso
```json
{
    "selenium": {
        "operator": "javascript",
        "from_string": "return document.title;",
        "result": "page_title"
    }
}
```

```json
{
    "selenium": {
        "operator": "javascript",
        "from_file": "./path/to/file.js",
        "result": "js_result"
    }
}
```

## HTTP

`selenium_plugin` **no implementa peticiones HTTP** — eso quedó fuera de su alcance (originalmente lo tenía `navigator_selenium`, que mezclaba HTTP + navegador en un solo plugin). Para hacer requests HTTP dentro de un script Sugar, usar la keyword `http` nativa de Sugar core o el plugin `request`, no `selenium`:

```json
{ "http": { "GET": "https://httpbin.org/get" } }
```

## Migración desde `navigator_selenium`

```json
// Antes (navigator_selenium)
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": { "code": "return document.title;", "result": "page_title" }
    }
}

// Ahora (selenium_plugin)
{
    "selenium": {
        "operator": "javascript",
        "from_string": "return document.title;",
        "result": "page_title"
    }
}
```

**Nota:** `code` pasó a llamarse `from_string` (o `from_file` para archivos), y el `config` anidado desapareció — los parámetros van directo dentro de `selenium`.
