# Funciones del Navegador (Navigator Plugin)

Estas funciones permiten interactuar con un navegador web usando el plugin `navigator_selenium`.

## Plugin
`navigator_selenium`

## Uso

```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "navigate",
        "config": {
            "url": "https://example.com",
            "wait_for_load": true,
            "id": "navigation_result"
        }
    }
}
```

## Comandos Disponibles

### Sintaxis General
```json
{
  "plugin": {
    "name": "navigator_selenium",
    "command": "comando",
    "config": {
      "parametros": "valores"
    }
  }
}
```

### Comandos Disponibles

**Operaciones de Navegación:**
- `navigate` - Navegar a una URL
- `click` - Hacer clic en un elemento
- `input` - Ingresar texto en elementos
- `wait` - Esperar por tiempo o elementos
- `screenshot` - Capturar pantalla

**Operaciones HTTP:**
- `http` - Realizar requests HTTP (GET, POST, PUT, DELETE, PATCH)

**Operaciones JavaScript:**
- `javascript` - Ejecutar código JavaScript

### Ejemplos de Uso

**Operaciones de Navegación:**
```json
{
  "plugin": {
    "name": "navigator_selenium",
    "command": "navigate",
    "config": {
      "url": "https://example.com",
      "wait_for_load": true
    }
  }
}

{
  "plugin": {
    "name": "navigator_selenium",
    "command": "click",
    "config": {
      "selector": "#submit-button",
      "type": "css"
    }
  }
}

{
  "plugin": {
    "name": "navigator_selenium",
    "command": "input",
    "config": {
      "selector": "#username",
      "text": "user123",
      "type": "css"
    }
  }
}
```

**Operaciones HTTP:**
```json
{
  "plugin": {
    "name": "navigator_selenium",
    "command": "http",
    "config": {
      "GET": "https://httpbin.org/get",
      "headers": {
        "User-Agent": "Sugar-Navigator/1.0"
      }
    }
  }
}
```

**Operaciones JavaScript:**
```json
{
  "plugin": {
    "name": "navigator_selenium",
    "command": "javascript",
    "config": {
      "code": "return document.title;",
      "id": "page_title"
    }
  }
}
```

{
  "plugin": {
    "name": "navigator_selenium",
    "command": "wait",
    "config": {
      "type": "element",
      "selector": ".dynamic-content",
      "selector_type": "css"
    }
  }
}

{
  "plugin": {
    "name": "navigator_selenium",
    "command": "screenshot",
    "config": {
      "file": "page_screenshot.png"
    }
  }
}
```

## HTTP (Plugin)

Realiza solicitudes HTTP usando el plugin `navigator_selenium`.

### Comando
`http`

### Parámetros
* GET (string): URL para una solicitud GET.
* POST (string): URL para una solicitud POST.
* PUT (string): URL para una solicitud PUT.
* DELETE (string): URL para una solicitud DELETE.
* PATCH (string): URL para una solicitud PATCH.
* headers (object): Headers de la solicitud.
* data/body (object): Datos a enviar en la solicitud.
* cookies (object): Cookies de la sesión.
* timeout (number): Timeout en segundos.
* value (string): Nombre de una variable que contiene la URL.
* replace (object): Objeto de pares clave-valor para reemplazar marcadores de posición en la URL (ej. {{foo}}).
* headers (object, opcional): Diccionario de cabeceras HTTP a enviar con la solicitud.
* cookies (array, opcional): Array de objetos cookie a enviar con la solicitud. Cada objeto cookie debe incluir name, value, domain y opcionalmente path, expiry, httpOnly, secure.
* body (object/string, opcional): Cuerpo de la solicitud para métodos como POST. Puede ser JSON, texto, form-encoded, graphql, o binario.

### Ejemplos de Uso
```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "GET": "http://www.example.com"
        }
    }
}

{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "POST": "http://www.example.com/api/data",
            "data": {
                "key": "value_to_send",
                "another_field": 123
            },
            "headers": {
                "Authorization": "Bearer {{token}}",
                "Content-Type": "application/json",
                "Accept": "*/*"
            }
        }
    }
}

{
    "plugin": {
        "name": "navigator_selenium",
        "command": "http",
        "config": {
            "GET": "http://www.example.com/{{foo_id}}/data/{{bar_param}}"
        }
    }
}
```

## JAVASCRIPT (Plugin)

Ejecuta código JavaScript usando el plugin `navigator_selenium`.

### Comando
`javascript`

### Parámetros
* code (string): Cadena de código JavaScript a ejecutar.
* file (string): Ruta a un archivo JavaScript para ejecutar.
* wait (number): Tiempo de espera después de la ejecución.

### Ejemplos de Uso
```json
{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": {
            "code": "return document.title;",
            "id": "page_title"
        }
    }
}

{
    "plugin": {
        "name": "navigator_selenium",
        "command": "javascript",
        "config": {
            "file": "path/to/file.js"
        }
    }
}
```

## Migración desde Core

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

**Nota:** Se recomienda usar la nueva sintaxis de plugin para nuevos proyectos, ya que proporciona una implementación más robusta y mantenible basada en Selenium WebDriver.