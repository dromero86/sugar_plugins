# Navigator Plugin

El plugin `navigator_selenium` proporciona funcionalidades de navegación web y automatización usando Selenium WebDriver.

## Instalación

```bash
pip install -r plugins/navigator_selenium/requirements.txt
```

## Uso Básico

### HTTP Requests

```json
{
    "task": [
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "http",
                "config": {
                    "GET": "https://httpbin.org/get",
                    "headers": {
                        "User-Agent": "Sugar-Navigator/1.0"
                    },
                    "result": "response"
                }
            }
        }
    ]
}
```

### JavaScript Execution

```json
{
    "task": [
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "javascript",
                "config": {
                    "code": "return document.title;",
                    "result": "page_title"
                }
            }
        }
    ]
}
```

## Comandos Disponibles

### HTTP Commands

#### GET Request

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "GET": "https://api.example.com/data",
            "headers": {
                "Authorization": "Bearer token123"
            },
            "result": "api_response"
        }
    }
}
```

#### POST Request

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "POST": "https://api.example.com/users",
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "headers": {
                "Content-Type": "application/json"
            },
            "result": "create_response"
        }
    }
}
```

### Browser Commands

#### Navigate

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "navigate",
        "config": {
            "url": "https://example.com",
            "wait_for_load": true,
            "result": "navigation_result"
        }
    }
}
```

#### Click Element

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "click",
        "config": {
            "selector": "#submit-button",
            "type": "css",
            "result": "click_result"
        }
    }
}
```

#### Input Text

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "input",
        "config": {
            "selector": "#username",
            "text": "myuser",
            "type": "css",
            "result": "input_result"
        }
    }
}
```

#### Wait

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "wait",
        "config": {
            "type": "element",
            "selector": ".loading-spinner",
            "selector_type": "css",
            "result": "wait_result"
        }
    }
}
```

#### Screenshot

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "screenshot",
        "config": {
            "file": "screenshot.png",
            "result": "screenshot_result"
        }
    }
}
```

### JavaScript Commands

#### Execute Code

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": {
            "code": "return document.querySelector('h1').textContent;",
            "result": "heading_text"
        }
    }
}
```

#### Execute from File

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": {
            "file": "script.js",
            "result": "file_result"
        }
    }
}
```

## Tipos de Selectores

- **css**: Selector CSS (por defecto)
- **xpath**: Selector XPath
- **id**: ID del elemento

## Configuración

### Inicialización del Plugin

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "init": {
            "headless": false,
            "timeout": 30
        }
    }
}
```

### Opciones de Configuración

- **headless**: Ejecutar navegador en modo headless (por defecto: false)
- **timeout**: Timeout por defecto para operaciones en segundos (por defecto: 30)

## Ejemplos Complejos

### Automatización de Formulario

```json
{
    "task": [
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "navigate",
                "config": {
                    "url": "https://httpbin.org/forms/post",
                    "wait_for_load": true
                }
            }
        },
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "input",
                "config": {
                    "selector": "input[name='custname']",
                    "text": "John Doe",
                    "type": "css"
                }
            }
        },
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "input",
                "config": {
                    "selector": "input[name='custemail']",
                    "text": "john@example.com",
                    "type": "css"
                }
            }
        },
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "screenshot",
                "config": {
                    "file": "form_filled.png"
                }
            }
        }
    ]
}
```

### Workflow HTTP + JavaScript

```json
{
    "task": [
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "http",
                "config": {
                    "GET": "https://httpbin.org/json",
                    "result": "api_data"
                }
            }
        },
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "navigate",
                "config": {
                    "url": "https://example.com",
                    "wait_for_load": true
                }
            }
        },
        {
            "plugin": {
                "name": "navigator_selenium",
                "command": "javascript",
                "config": {
                    "code": "document.title = 'Data: ' + arguments[0];",
                    "result": "title_change"
                }
            }
        }
    ]
}
```

## Manejo de Errores

El plugin proporciona manejo de errores para:

- Errores de red en requests HTTP
- Elementos no encontrados en operaciones de navegador
- Errores de ejecución de JavaScript
- Timeouts

## Dependencias

- selenium>=4.0.0
- webdriver-manager>=3.8.0
- requests>=2.25.0

## Migración desde Navigator Core

Si estás migrando desde el módulo Navigator core, reemplaza:

```json
// Antes (Core)
{
    "GET": "https://example.com"
}

// Después (Plugin)
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "GET": "https://example.com"
        }
    }
}
```

```json
// Antes (Core)
{
    "javascript": {
        "code": "return document.title;"
    }
}

// Después (Plugin)
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": {
            "code": "return document.title;"
        }
    }
}
```

## Notas Importantes

1. **Inicialización**: El plugin debe ser inicializado antes de usar comandos de navegador
2. **Cleanup**: El plugin maneja automáticamente la limpieza de recursos
3. **Selenium**: Requiere Chrome/Chromium instalado en el sistema
4. **Headless**: Para entornos sin GUI, usar `headless: true`

---

**Nota**: Este plugin reemplaza la funcionalidad del módulo Navigator core, proporcionando una implementación más robusta y mantenible basada en Selenium WebDriver.