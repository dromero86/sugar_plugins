# Plugin Playwright para Sugar

Plugin de automatización web moderna para Sugar usando Playwright.

## Características

- **Automatización web moderna**: Soporte para Chromium, Firefox y WebKit
- **Navegación avanzada**: Control completo de páginas web
- **Interacción de elementos**: Click, type, fill, y más
- **Capturas de pantalla**: Screenshots de páginas y elementos
- **Grabación de video**: Captura de video durante la automatización
- **Interceptación de red**: Control de requests y responses
- **Emulación de dispositivos**: Simulación de dispositivos móviles
- **Gestión de cookies y storage**: Control de datos del navegador

## Instalación

### Dependencias

```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install
```

### Instalación del Plugin

```bash
# Desde el directorio del plugin
pip install .

# O usando el gestor de paquetes de Sugar
sugarize require playwright ^1.0.0
```

## Uso Básico

### Configuración Inicial

```json
{
  "meta": {
    "playwright": {
      "browser_type": "chromium",
      "headless": false,
      "slow_mo": 1000
    }
  },
  "task": [
    {
      "playwright": {
        "operator": "launch_browser",
        "browser_type": "chromium",
        "headless": false,
        "result": "browser_status"
      }
    },
    {
      "playwright": {
        "operator": "new_context",
        "viewport": {
          "width": 1280,
          "height": 720
        },
        "result": "context_status"
      }
    },
    {
      "playwright": {
        "operator": "new_page",
        "result": "page_status"
      }
    }
  ]
}
```

### Navegación

```json
{
  "task": [
    {
      "playwright": {
        "operator": "goto",
        "url": "https://example.com",
        "wait_until": "load",
        "timeout": 30000,
        "result": "navigation_result"
      }
    },
    {
      "playwright": {
        "operator": "get_title",
        "result": "page_title"
      }
    },
    {
      "print": {
        "text": "Título de la página: {{page_title.title}}"
      }
    }
  ]
}
```

### Interacción con Elementos

```json
{
  "task": [
    {
      "playwright": {
        "operator": "click",
        "selector": "#submit-button",
        "button": "left",
        "click_count": 1,
        "result": "click_result"
      }
    },
    {
      "playwright": {
        "operator": "type",
        "selector": "#username",
        "text": "usuario@ejemplo.com",
        "delay": 100,
        "result": "type_result"
      }
    },
    {
      "playwright": {
        "operator": "fill",
        "selector": "#password",
        "value": "contraseña123",
        "result": "fill_result"
      }
    }
  ]
}
```

### Capturas de Pantalla

```json
{
  "task": [
    {
      "playwright": {
        "operator": "screenshot",
        "path": "./screenshots/pagina_completa.png",
        "full_page": true,
        "result": "screenshot_result"
      }
    },
    {
      "playwright": {
        "operator": "screenshot_element",
        "selector": "#elemento-especifico",
        "path": "./screenshots/elemento.png",
        "result": "element_screenshot"
      }
    }
  ]
}
```

### JavaScript y Evaluación

```json
{
  "task": [
    {
      "playwright": {
        "operator": "evaluate",
        "script": "document.title = 'Nuevo Título'; return document.title;",
        "result": "js_result"
      }
    },
    {
      "playwright": {
        "operator": "evaluate",
        "script": "return window.innerWidth + 'x' + window.innerHeight;",
        "result": "viewport_size"
      }
    },
    {
      "print": {
        "text": "Tamaño del viewport: {{viewport_size.result}}"
      }
    }
  ]
}
```

### Gestión de Cookies

```json
{
  "task": [
    {
      "playwright": {
        "operator": "get_cookies",
        "result": "cookies"
      }
    },
    {
      "playwright": {
        "operator": "add_cookies",
        "cookies": [
          {
            "name": "session_id",
            "value": "abc123",
            "domain": "example.com"
          }
        ],
        "result": "add_cookies_result"
      }
    },
    {
      "playwright": {
        "operator": "clear_cookies",
        "result": "clear_cookies_result"
      }
    }
  ]
}
```

### Grabación de Video

```json
{
  "task": [
    {
      "playwright": {
        "operator": "start_video",
        "path": "./videos/automation.webm",
        "size": {
          "width": 1280,
          "height": 720
        },
        "result": "video_start"
      }
    },
    {
      "playwright": {
        "operator": "goto",
        "url": "https://example.com"
      }
    },
    {
      "playwright": {
        "operator": "click",
        "selector": "#button"
      }
    },
    {
      "playwright": {
        "operator": "stop_video",
        "result": "video_stop"
      }
    }
  ]
}
```

## Comandos Disponibles

### Gestión de Navegador
- `launch_browser` - Lanzar un navegador
- `close_browser` - Cerrar el navegador
- `new_context` - Crear un nuevo contexto
- `close_context` - Cerrar el contexto

### Gestión de Páginas
- `new_page` - Crear una nueva página
- `close_page` - Cerrar la página actual

### Navegación
- `goto` - Navegar a una URL
- `go_back` - Ir hacia atrás
- `go_forward` - Ir hacia adelante
- `reload` - Recargar la página

### Interacción con Elementos
- `click` - Hacer clic en un elemento
- `type` - Escribir texto en un elemento
- `fill` - Llenar un campo de formulario
- `clear` - Limpiar un campo
- `select_option` - Seleccionar una opción
- `check` - Marcar un checkbox
- `uncheck` - Desmarcar un checkbox
- `press` - Presionar una tecla

### Búsqueda de Elementos
- `locator` - Localizar un elemento
- `get_by_text` - Obtener elemento por texto
- `get_by_role` - Obtener elemento por rol
- `get_by_label` - Obtener elemento por etiqueta
- `get_by_placeholder` - Obtener elemento por placeholder
- `get_by_test_id` - Obtener elemento por test ID

### Esperas
- `wait_for_load_state` - Esperar estado de carga
- `wait_for_url` - Esperar URL específica
- `wait_for_selector` - Esperar selector
- `wait_for_element` - Esperar elemento

### JavaScript
- `evaluate` - Ejecutar JavaScript
- `evaluate_handle` - Ejecutar JavaScript con handle
- `get_content` - Obtener contenido de la página
- `get_title` - Obtener título de la página
- `get_url` - Obtener URL actual

### Capturas
- `screenshot` - Captura de pantalla de la página
- `screenshot_element` - Captura de pantalla de un elemento

### Red
- `route` - Interceptar requests
- `unroute` - Dejar de interceptar requests
- `set_extra_http_headers` - Establecer headers HTTP

### Cookies y Storage
- `get_cookies` - Obtener cookies
- `add_cookies` - Agregar cookies
- `clear_cookies` - Limpiar cookies
- `get_local_storage` - Obtener localStorage
- `set_local_storage` - Establecer localStorage
- `clear_local_storage` - Limpiar localStorage

### Funcionalidades Avanzadas
- `scroll_to` - Hacer scroll a un elemento
- `hover` - Hacer hover sobre un elemento
- `drag_and_drop` - Arrastrar y soltar
- `upload_file` - Subir archivo
- `download_file` - Descargar archivo
- `emulate_device` - Emular dispositivo
- `set_viewport_size` - Establecer tamaño de viewport
- `set_geolocation` - Establecer geolocalización
- `set_permissions` - Establecer permisos

### Video
- `start_video` - Iniciar grabación de video
- `stop_video` - Detener grabación de video

## Configuración Avanzada

### Opciones de Navegador

```json
{
  "playwright": {
    "operator": "launch_browser",
    "browser_type": "chromium",
    "headless": false,
    "slow_mo": 1000,
    "args": [
      "--no-sandbox",
      "--disable-dev-shm-usage"
    ]
  }
}
```

### Configuración de Contexto

```json
{
  "playwright": {
    "operator": "new_context",
    "viewport": {
      "width": 1920,
      "height": 1080
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "locale": "es-ES",
    "timezone_id": "Europe/Madrid",
    "permissions": ["geolocation", "notifications"]
  }
}
```

## Ejemplos Completos

### Automatización de Login

```json
{
  "meta": {
    "playwright": {
      "browser_type": "chromium",
      "headless": false
    }
  },
  "task": [
    {
      "playwright": {
        "operator": "launch_browser",
        "result": "browser"
      }
    },
    {
      "playwright": {
        "operator": "new_context",
        "result": "context"
      }
    },
    {
      "playwright": {
        "operator": "new_page",
        "result": "page"
      }
    },
    {
      "playwright": {
        "operator": "goto",
        "url": "https://example.com/login"
      }
    },
    {
      "playwright": {
        "operator": "fill",
        "selector": "#username",
        "value": "usuario@ejemplo.com"
      }
    },
    {
      "playwright": {
        "operator": "fill",
        "selector": "#password",
        "value": "contraseña123"
      }
    },
    {
      "playwright": {
        "operator": "click",
        "selector": "#login-button"
      }
    },
    {
      "playwright": {
        "operator": "wait_for_load_state",
        "state": "networkidle"
      }
    },
    {
      "playwright": {
        "operator": "get_title",
        "result": "title"
      }
    },
    {
      "print": {
        "text": "Login exitoso. Título: {{title.title}}"
      }
    },
    {
      "playwright": {
        "operator": "screenshot",
        "path": "./screenshots/after_login.png"
      }
    },
    {
      "playwright": {
        "operator": "close_browser"
      }
    }
  ]
}
```

### Testing de Formulario

```json
{
  "task": [
    {
      "playwright": {
        "operator": "launch_browser",
        "browser_type": "firefox",
        "headless": true
      }
    },
    {
      "playwright": {
        "operator": "new_context"
      }
    },
    {
      "playwright": {
        "operator": "new_page"
      }
    },
    {
      "playwright": {
        "operator": "goto",
        "url": "https://example.com/form"
      }
    },
    {
      "playwright": {
        "operator": "fill",
        "selector": "#name",
        "value": "Juan Pérez"
      }
    },
    {
      "playwright": {
        "operator": "fill",
        "selector": "#email",
        "value": "juan@ejemplo.com"
      }
    },
    {
      "playwright": {
        "operator": "select_option",
        "selector": "#country",
        "value": "ES"
      }
    },
    {
      "playwright": {
        "operator": "check",
        "selector": "#terms"
      }
    },
    {
      "playwright": {
        "operator": "click",
        "selector": "#submit"
      }
    },
    {
      "playwright": {
        "operator": "wait_for_selector",
        "selector": ".success-message"
      }
    },
    {
      "playwright": {
        "operator": "get_by_text",
        "text": "Formulario enviado correctamente",
        "result": "success_message"
      }
    },
    {
      "print": {
        "text": "✅ {{success_message.text}}"
      }
    }
  ]
}
```

## Troubleshooting

### Problemas Comunes

1. **Navegadores no instalados**
   ```bash
   playwright install
   ```

2. **Error de permisos en Linux**
   ```bash
   playwright install-deps
   ```

3. **Problemas de memoria**
   - Usar `headless: true`
   - Cerrar navegadores después de cada test

4. **Elementos no encontrados**
   - Usar `wait_for_selector` antes de interactuar
   - Verificar selectores CSS
   - Usar `wait_for_load_state`

### Debug

```json
{
  "playwright": {
    "operator": "launch_browser",
    "headless": false,
    "slow_mo": 2000
  }
}
```

## Contribución

Para contribuir al plugin:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Añade tests
5. Envía un pull request

## Licencia

MIT License - ver LICENSE para más detalles.
