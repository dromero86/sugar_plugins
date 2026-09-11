# Selenium Plugin (antes "Navigator Plugin")

> Este documento documentaba originalmente un plugin llamado `navigator_selenium`, con sintaxis `{"plugin": {"name": "navigator_selenium", "command": ..., "config": {...}}}`. La especificación mutó hasta el plugin actual, `selenium_plugin` (v2.1.0), con la sintaxis unificada `{"selenium": {"operator": ..., ...}}`. Este documento está actualizado a esa versión actual — para la referencia completa de los 28 operadores ver `docs/README.md`.

El plugin `selenium_plugin` proporciona funcionalidades de navegación web y automatización usando Selenium WebDriver.

## Instalación

El plugin es autocontenido: trae sus propias dependencias (`selenium`, `webdriver-manager`, `requests`) vía un `venv` propio o uno compartido en la raíz del proyecto de plugins — ver "Instalación y Uso" en `docs/README.md`.

## Uso Básico

### JavaScript Execution

```json
{
    "task": [
        {
            "selenium": {
                "operator": "javascript",
                "from_string": "return document.title;",
                "result": "page_title"
            }
        }
    ]
}
```

### HTTP Requests

`selenium_plugin` **no hace peticiones HTTP** — eso no es parte de su alcance (a diferencia del viejo `navigator_selenium`, que mezclaba HTTP y navegador). Para eso usar la keyword `http` nativa de Sugar o el plugin `request`:

```json
{ "http": { "GET": "https://httpbin.org/get", "headers": { "User-Agent": "Sugar/1.0" }, "result": "response" } }
```

## Operadores Disponibles

Referencia completa en `docs/README.md`. Los que se usan en los ejemplos de este documento:

### Navegar

```json
{
    "selenium": {
        "operator": "open",
        "url": "https://example.com",
        "result": "navigation_result"
    }
}
```

### Clic en elemento

```json
{
    "selenium": {
        "operator": "click",
        "selector": "#submit-button",
        "result": "click_result"
    }
}
```

### Escribir texto

```json
{
    "selenium": {
        "operator": "type",
        "selector": "#username",
        "value": "myuser",
        "result": "input_result"
    }
}
```

### Esperar

```json
{
    "selenium": {
        "operator": "wait",
        "type": "element",
        "selector": ".loading-spinner",
        "result": "wait_result"
    }
}
```

### Screenshot

```json
{
    "selenium": {
        "operator": "screenshot",
        "file": "screenshot.png",
        "result": "screenshot_result"
    }
}
```

### Ejecutar JavaScript

```json
{
    "selenium": {
        "operator": "javascript",
        "from_string": "return document.querySelector('h1').textContent;",
        "result": "heading_text"
    }
}
```

```json
{
    "selenium": {
        "operator": "javascript",
        "from_file": "script.js",
        "result": "file_result"
    }
}
```

## Selectores

Todos los operadores que reciben `selector` aceptan CSS (por defecto) o XPath — se detecta automáticamente si el selector empieza con `//`, `.//` o `(`, o se puede forzar con el prefijo `xpath=`. No hay un parámetro separado `type`/`selector_type`: es el propio texto del selector el que decide.

## Configuración

La configuración del navegador va en `meta`, no en un comando `init` separado:

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",
    "headless": true,
    "timeout": 10,
    "implicit_wait": 5
  },
  "task": [ ]
}
```

- **browser**: `chrome`, `firefox` o `edge` (Safari/Opera/IE no están soportados)
- **headless**: ejecutar navegador en modo headless (por defecto: `false`)
- **timeout**: timeout por defecto para esperas explícitas, en segundos (por defecto: `10`)
- **implicit_wait**: espera implícita para búsqueda de elementos, en segundos (por defecto: `5`)

## Ejemplos Complejos

### Automatización de Formulario

```json
{
    "meta": { "mode": "selenium", "browser": "firefox", "headless": true },
    "task": [
        {
            "selenium": {
                "operator": "open",
                "url": "https://httpbin.org/forms/post"
            }
        },
        {
            "selenium": {
                "operator": "type",
                "selector": "input[name='custname']",
                "value": "John Doe"
            }
        },
        {
            "selenium": {
                "operator": "type",
                "selector": "input[name='custemail']",
                "value": "john@example.com"
            }
        },
        {
            "selenium": {
                "operator": "screenshot",
                "file": "form_filled.png"
            }
        }
    ]
}
```

### Workflow HTTP + navegador

HTTP y navegador ahora son cosas separadas — HTTP va por `http` (Sugar core), navegación por `selenium`:

```json
{
    "meta": { "mode": "selenium", "browser": "firefox" },
    "task": [
        {
            "http": { "GET": "https://httpbin.org/json", "result": "api_data" }
        },
        {
            "selenium": { "operator": "open", "url": "https://example.com" }
        },
        {
            "selenium": {
                "operator": "javascript",
                "from_string": "document.title = 'Data: ' + arguments[0];",
                "result": "title_change"
            }
        }
    ]
}
```

## Manejo de Errores

El plugin devuelve `{"success": false, "error": "..."}` en vez de propagar excepciones sin control, para:

- Elementos no encontrados en operaciones de navegador
- Errores de ejecución de JavaScript
- Timeouts en esperas explícitas
- Fallos al inicializar el driver (navegador no soportado, binario no encontrado, etc.)

## Dependencias

- `selenium>=4.0.0`
- `webdriver-manager>=3.8.0`
- `requests>=2.25.0`

## Notas Importantes

1. **Inicialización lazy**: el driver se levanta automáticamente en la primera operación `selenium` de la sesión, no hace falta un comando `init` aparte.
2. **Cleanup**: el plugin cierra el driver automáticamente al terminar; también se puede cerrar explícitamente a mitad de script con el operador `quit`.
3. **Navegadores soportados**: Chrome, Firefox y Edge — deben estar instalados en el sistema.
4. **Headless**: para entornos sin GUI, usar `"headless": true` en `meta`.
