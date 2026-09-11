# Plugin Selenium v2.1 para Sugar

## 📋 Descripción General

El plugin Selenium v2.1 para Sugar proporciona capacidades avanzadas de automatización web usando la sintaxis unificada `@selenium/`.

### 🎯 Características Principales

- **Sintaxis unificada** `@selenium/` con operadores específicos
- **Soporte para Chrome, Firefox y Edge**
- **Sistema avanzado de cookies** con arrays y propiedades completas
- **28 operadores disponibles** para automatización completa
- **Descarga automática de drivers** vía WebDriver Manager
- **Gestión robusta de errores** y timeouts configurables
- **Selectores CSS y XPath** (autodetectados, o con prefijo explícito `xpath=`)
- **Dependencias del plugin autocontenidas**: el plugin trae su propio entorno (`venv`) con `selenium`/`webdriver-manager`/`requests`, sin que Sugar core dependa de ellas

---

## 🌐 Soporte de Navegadores

### Navegadores Soportados

| Navegador | Clave | Soporte | Plataforma | Características |
|-----------|-------|---------|------------|-----------------|
| **Chrome** | `chrome` | ✅ Completo | Multiplataforma | Headless, Detach, Auto-Download |
| **Firefox** | `firefox` | ✅ Completo | Multiplataforma | Headless, Auto-Download |
| **Edge** | `edge` | ✅ Completo | Multiplataforma | Headless, Detach, Auto-Download |

> Safari, Opera e Internet Explorer no están soportados actualmente (no figuran en `SUPPORTED_BROWSERS`); configurar `browser` con alguno de esos valores falla con "Navegador no soportado".

### Configuración por Navegador

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",  // chrome, firefox, edge
    "options": ["--width=1280", "--height=720"],
    "headless": true,
    "detach": false,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

---

## 🔧 Operadores Disponibles

### 1. **click** - Hacer clic en elementos
```json
{
  "selenium": {
    "operator": "click",
    "selector": "#btn",
    "result": "is_clicked"
  }
}
```

### 2. **open** - Abrir navegador y URL
```json
{
  "selenium": {
    "operator": "open",
    "url": "https://example.com",
    "result": "is_open"
  }
}
```

### 3. **javascript** - Ejecutar código JavaScript
```json
{
  "selenium": {
    "operator": "javascript",
    "from_file": "./script.js",
    "result": "js_result"
  }
}
```

### 4. **type** - Escribir texto
```json
{
  "selenium": {
    "operator": "type",
    "selector": "input[name='q']",
    "value": "Sugar",
    "enter": true,
    "result": "is_typed"
  }
}
```

### 5. **wait** - Esperar condiciones
```json
{
  "selenium": {
    "operator": "wait",
    "type": "element",
    "selector": "#content",
    "result": "element_found"
  }
}
```

### 6. **screenshot** - Capturar pantalla
```json
{
  "selenium": {
    "operator": "screenshot",
    "file": "./result.png",
    "result": "screenshot"
  }
}
```

### 7. **navigate** - Navegación básica
```json
{
  "selenium": {
    "operator": "navigate",
    "action": "refresh",
    "result": "navigated"
  }
}
```

### 8. **find** - Buscar elementos
```json
{
  "selenium": {
    "operator": "find",
    "selector": ".item",
    "multiple": true,
    "result": "found"
  }
}
```

### 9. **submit** - Enviar formularios
```json
{
  "selenium": {
    "operator": "submit",
    "selector": "form",
    "result": "submitted"
  }
}
```

### 10. **clear** - Limpiar campos
```json
{
  "selenium": {
    "operator": "clear",
    "selector": "input[name='q']",
    "result": "cleared"
  }
}
```

### 11. **select** - Seleccionar opciones
```json
{
  "selenium": {
    "operator": "select",
    "selector": "select[name='country']",
    "value": "ES",
    "result": "selected"
  }
}
```

### 12. **hover** - Pasar el mouse
```json
{
  "selenium": {
    "operator": "hover",
    "selector": ".menu-item",
    "result": "hovered"
  }
}
```

### 13. **scroll** - Desplazamiento
```json
{
  "selenium": {
    "operator": "scroll",
    "type": "to_element",
    "selector": "#footer",
    "result": "scrolled"
  }
}
```

### 14. **upload** - Subir archivos
```json
{
  "selenium": {
    "operator": "upload",
    "selector": "input[type='file']",
    "file": "./document.pdf",
    "result": "uploaded"
  }
}
```

### 15. **download** - Descargar archivos
```json
{
  "selenium": {
    "operator": "download",
    "url": "https://example.com/file.pdf",
    "file": "./downloads/file.pdf",
    "result": "downloaded"
  }
}
```

### 16. **cookies** - Gestión de cookies
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "cookies": [
      {
        "name": "session_id",
        "value": "abc123",
        "domain": ".example.com",
        "secure": true
      }
    ],
    "result": "cookies_added"
  }
}
```

### 17. **window** - Gestión de ventanas
```json
{
  "selenium": {
    "operator": "window",
    "action": "maximize",
    "result": "window_action"
  }
}
```

### 18. **frame** - Cambiar frames
```json
{
  "selenium": {
    "operator": "frame",
    "action": "switch",
    "name": "content-frame",
    "result": "frame_action"
  }
}
```

### 19. **alert** - Manejar alertas
```json
{
  "selenium": {
    "operator": "alert",
    "action": "accept",
    "result": "alert_action"
  }
}
```

### 20. **page** - Información de la página actual
Devuelve `url`, `title` y `source` (HTML) de la página actual.
```json
{
  "selenium": {
    "operator": "page",
    "result": "pagina"
  }
}
```

### 21. **state** - Estado de un elemento
Devuelve `exists`, `displayed`, `enabled` y `selected`. Si el elemento no existe, devuelve todo en `false` en vez de fallar.
```json
{
  "selenium": {
    "operator": "state",
    "selector": "#btn",
    "result": "estado_btn"
  }
}
```

### 22. **dblclick** - Doble clic en elemento
```json
{
  "selenium": {
    "operator": "dblclick",
    "selector": "#item",
    "result": "dbl_ok"
  }
}
```

### 23. **rightclick** - Clic derecho (context click) en elemento
```json
{
  "selenium": {
    "operator": "rightclick",
    "selector": "#item",
    "result": "ctx_ok"
  }
}
```

### 24. **keys** - Enviar teclas especiales
Envía una tecla (o lista de teclas) de `selenium.webdriver.common.keys.Keys` (`ENTER`, `ESCAPE`, `TAB`, `ARROW_DOWN`, etc., sin distinguir mayúsculas/minúsculas) a un selector, o al elemento activo si no se pasa `selector`.
```json
{
  "selenium": {
    "operator": "keys",
    "selector": "#buscador",
    "keys": ["ENTER"],
    "result": "keys_ok"
  }
}
```

### 25. **quit** - Cerrar la sesión del navegador
Cierra el navegador a mitad de script. La siguiente operación `selenium` que se ejecute levanta un driver nuevo automáticamente.
```json
{
  "selenium": {
    "operator": "quit",
    "result": "quit_ok"
  }
}
```

### 26. **storage** - Gestión de localStorage/sessionStorage
Mismo diseño que `cookies`, pero para Web Storage. `type` acepta `local` (default) o `session`. `action` acepta `get`, `get_all`, `set`, `remove`, `clear`.
```json
{
  "selenium": {
    "operator": "storage",
    "action": "set",
    "key": "token",
    "value": "abc123",
    "result": "storage_set"
  }
}
```

> No funciona en páginas `data:` (origen nulo) por restricción del propio navegador, no del plugin.

### 27. **drag_and_drop** - Arrastrar un elemento hasta otro
```json
{
  "selenium": {
    "operator": "drag_and_drop",
    "source": "#origen",
    "target": "#destino",
    "result": "drag_ok"
  }
}
```

> Funciona con drag-and-drop implementado con eventos de mouse (mousedown/mousemove/mouseup). El drag-and-drop nativo HTML5 (`draggable="true"` + eventos `dragstart`/`drop`) no siempre responde a esto — es una limitación conocida de Selenium/WebDriver, no de este plugin.

### 28. **pdf** - Imprimir la página actual a PDF
Usa el comando estándar "Print Page" de WebDriver (soportado tanto en Chrome/Edge como en Firefox).
```json
{
  "selenium": {
    "operator": "pdf",
    "file": "./pagina.pdf",
    "result": "pdf_ok"
  }
}
```

### Extensiones a operadores existentes

- **`screenshot`** acepta `selector` opcional: si se pasa, captura solo ese elemento en vez de la página completa.
- **`find`** acepta `attribute` opcional: además de `text`/`tag`, devuelve el valor de ese atributo del elemento (ej. `href`, `value`, `data-id`).
- **`wait`** suma los tipos `invisible` (espera a que un elemento desaparezca), `url_changes` (espera a que la URL cambie respecto a `from_url`, o a la URL actual si no se pasa) y `title_contains` (espera a que el `<title>` contenga un texto).

### Selectores: CSS y XPath

Todos los operadores que reciben `selector` aceptan CSS (comportamiento de siempre) o XPath. XPath se detecta automáticamente si el selector empieza con `//`, `.//` o `(`, o se puede forzar con el prefijo `xpath=`:
```json
{ "selenium": { "operator": "click", "selector": "//button[text()='Enviar']" } }
```

---

## 🍪 Sistema Avanzado de Cookies

### Estructura Completa de Cookies

Cada cookie soporta todos los elementos clave:

| Propiedad | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| **name** | string | ✅ | Nombre de la cookie |
| **value** | string | ✅ | Valor de la cookie |
| **domain** | string | ❌ | Dominio al que se aplica |
| **path** | string | ❌ | Ruta específica (default: "/") |
| **expiry** | string/int | ❌ | Fecha de caducidad |
| **secure** | boolean | ❌ | Solo se envía por HTTPS |
| **httpOnly** | boolean | ❌ | No accesible via JavaScript |

### Acciones de Cookies Disponibles

#### 1. **get** - Obtener todas las cookies
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "result": "cookies"
  }
}
```

#### 2. **add** - Agregar cookie individual
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "session_id",
    "value": "abc123def456",
    "domain": ".example.com",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "expiry": "2024-12-31T23:59:59Z",
    "result": "cookie_added"
  }
}
```

#### 3. **add** - Agregar array de cookies
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "cookies": [
      {
        "name": "session_id",
        "value": "abc123def456",
        "domain": ".example.com",
        "secure": true,
        "httpOnly": true
      },
      {
        "name": "user_preferences",
        "value": "dark_mode,notifications_enabled",
        "domain": ".example.com",
        "path": "/settings"
      }
    ],
    "result": "cookies_added"
  }
}
```

#### 4. **delete** - Eliminar cookie específica
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "delete",
    "name": "session_id",
    "result": "cookie_deleted"
  }
}
```

#### 5. **clear** - Eliminar todas las cookies
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "clear",
    "result": "cookies_cleared"
  }
}
```

#### 6. **get_by_name** - Obtener cookie por nombre
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get_by_name",
    "name": "session_id",
    "result": "cookie_by_name"
  }
}
```

#### 7. **get_by_domain** - Obtener cookies por dominio
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get_by_domain",
    "domain": ".example.com",
    "result": "cookies_by_domain"
  }
}
```

---

## 📝 Ejemplos Prácticos

### Ejemplo Básico (Chrome)
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "headless": true,
    "timeout": 10
  },
  "task": [
    {
      "selenium": {
        "operator": "open",
        "url": "https://www.google.com",
        "result": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='q']",
        "value": "Sugar automation",
        "result": "is_typed"
      }
    },
    {
      "selenium": {
        "operator": "click",
        "selector": "input[name='btnK']",
        "result": "is_clicked"
      }
    },
    {
      "selenium": {
        "operator": "screenshot",
        "file": "./google_result.png",
        "result": "screenshot"
      }
    }
  ]
}
```

### Ejemplo con Cookies
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",
    "headless": false
  },
  "task": [
    {
      "selenium": {
        "operator": "open",
        "url": "https://example.com",
        "result": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "add",
        "cookies": [
          {
            "name": "user_id",
            "value": "12345",
            "domain": ".example.com",
            "secure": true,
            "httpOnly": true
          },
          {
            "name": "theme",
            "value": "dark",
            "domain": ".example.com",
            "path": "/settings"
          }
        ],
        "result": "cookies_added"
      }
    },
    {
      "selenium": {
        "operator": "navigate",
        "action": "refresh",
        "result": "refreshed"
      }
    }
  ]
}
```

### Ejemplo de Formulario Completo
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "edge",
    "timeout": 15
  },
  "task": [
    {
      "selenium": {
        "operator": "open",
        "url": "https://example.com/contact",
        "result": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "element",
        "selector": "form",
        "result": "form_loaded"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='name']",
        "value": "Juan Pérez",
        "result": "name_typed"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='email']",
        "value": "juan@example.com",
        "result": "email_typed"
      }
    },
    {
      "selenium": {
        "operator": "select",
        "selector": "select[name='country']",
        "value": "ES",
        "result": "country_selected"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "textarea[name='message']",
        "value": "Mensaje de prueba",
        "result": "message_typed"
      }
    },
    {
      "selenium": {
        "operator": "submit",
        "selector": "form",
        "result": "form_submitted"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "element",
        "selector": ".success-message",
        "result": "success_shown"
      }
    }
  ]
}
```

---

## ⚙️ Configuración Avanzada

### Opciones de Navegador

#### Chrome
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "options": [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--window-size=1920,1080"
    ],
    "headless": true,
    "detach": false
  }
}
```

#### Firefox
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",
    "options": [
      "--width=1920",
      "--height=1080",
      "--no-sandbox"
    ],
    "headless": true
  }
}
```

#### Edge
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "edge",
    "options": [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage"
    ],
    "headless": true,
    "detach": false
  }
}
```

### Driver Personalizado
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": {
      "bin": "./drivers/chromedriver"
    }
  }
}
```

---

## 🚀 Instalación y Uso

El plugin trae sus propias dependencias (`selenium`, `webdriver-manager`, `requests`) en un `venv` propio, sin que Sugar core dependa de ellas.

### 1. Instalar el plugin en Sugar
Los plugins se copian (o enlazan) a la carpeta de plugins del usuario:
```bash
ln -s /ruta/a/sugar_plugins/src/selenium_plugin ~/.sugar/plugins/selenium_plugin
```

### 2. Instalar dependencias del plugin
Se puede usar un `venv` propio del plugin, o uno **compartido en la raíz del proyecto de plugins** (recomendado si tenés varios plugins con dependencias Python): Sugar busca, en este orden, `<plugin>/venv/`, `<plugin>/site-packages/`, y subiendo por los directorios padre del plugin, `virtual/` o `.venv/` — el primero que encuentra, gana.

```bash
# Venv compartido en la raíz del proyecto (ej. sugar_plugins/virtual)
cd sugar_plugins
python3 -m venv virtual
virtual/bin/pip install -r src/selenium_plugin/requirements.txt

# El plugin lo referencia con un symlink
ln -s ../../virtual src/selenium_plugin/venv
```

### 3. Ejecutar Script
```bash
sugar -f script.json
```

---

## 🔄 Migración desde v1.0

### Mapeo de Comandos

| Comando v1.0 | Operador v2.0 | Notas |
|--------------|---------------|-------|
| `click` | `click` | Sin cambios en funcionalidad |
| `open_browser` | `open` | Renombrado para claridad |
| `javascript` | `javascript` | Soporta `from_string` y `from_file` |
| `type` | `type` | Agregado soporte para `enter` |
| `wait` | `wait` | Tipos: `time`, `element`, `clickable` |
| `screenshot` | `screenshot` | Sin cambios |
| `navigate` | `navigate` | Acciones: `refresh`, `back`, `forward` |
| `find_element` | `find` | Agregado soporte para `multiple` |
| `submit` | `submit` | Sin cambios |
| `clear` | `clear` | Sin cambios |
| `select` | `select` | Sin cambios |
| `hover` | `hover` | Sin cambios |
| `scroll` | `scroll` | Tipos: `to_element`, `by_pixels`, `to_position` |
| `upload` | `upload` | Sin cambios |
| `download` | `download` | Nuevo operador |
| `cookies` | `cookies` | Acciones: `get`, `add`, `delete`, `clear` |
| `window` | `window` | Acciones: `switch`, `close`, `maximize`, `minimize` |
| `frame` | `frame` | Acciones: `switch` |
| `alert` | `alert` | Acciones: `accept`, `dismiss`, `send_keys` |

### Ejemplo de Migración

**Script Original (v1.0):**
```json
{
  "meta": {
    "mode": "selenium",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false
  },
  "task": [
    { "open_browser": { "url": "https://www.google.com" } },
    { "wait": { "seconds": 2 } },
    { "type": { "selector": "input[name='q']", "value": "Sugar" } },
    { "click": { "selector": "input[name='btnK']" } },
    { "screenshot": { "file": "./result.png" } }
  ]
}
```

**Script Migrado (v2.0):**
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false,
    "timeout": 10
  },
  "task": [
    {
      "selenium": {
        "operator": "open",
        "url": "https://www.google.com",
        "result": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "time",
        "seconds": 2,
        "result": "is_waited"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='q']",
        "value": "Sugar",
        "result": "is_typed"
      }
    },
    {
      "selenium": {
        "operator": "click",
        "selector": "input[name='btnK']",
        "result": "is_clicked"
      }
    },
    {
      "selenium": {
        "operator": "screenshot",
        "file": "./result.png",
        "result": "screenshot"
      }
    }
  ]
}
```

---

## ⚠️ Consideraciones y Limitaciones

### Limitaciones Conocidas
- **Navegadores soportados:** solo Chrome, Firefox y Edge (Safari/Opera/IE no están implementados)
- **Detach:** No soportado en Firefox
- **`drag_and_drop`:** funciona con drag-and-drop basado en eventos de mouse; el drag-and-drop nativo HTML5 no siempre responde
- **`download`:** el archivo se guarda en la carpeta de descargas por defecto del navegador, no directamente en `file` — para que coincidan hace falta configurar las preferencias de descarga del navegador vía `meta.options`. El operador verifica en disco y devuelve `success: false` si el archivo no aparece a tiempo, en vez de asumir éxito.
- **Un solo driver por instancia de plugin:** si Sugar corre tareas `selenium` en paralelo (`thread`/`parallel`), comparten el mismo navegador — hay un lock que evita que se pisen al inicializar, pero las operaciones sobre ese driver no son paralelas entre sí (WebDriver no lo soporta)

### Requisitos del Sistema
- **Python:** >= 3.9 (misma versión que usa Sugar core)
- **Navegadores:** Chrome, Firefox o Edge instalados según configuración
- **Permisos:** Escritura para descarga de drivers
- **Conexión:** Internet para descarga automática de drivers
- **Entorno de dependencias:** el plugin necesita su propio `venv` (o uno compartido en la raíz del proyecto de plugins) con `selenium`/`webdriver-manager`/`requests` instalados — ver sección de instalación

### Compatibilidad
- **v1.0:** No compatible (requiere migración)
- **v2.1:** Compatible con Chrome, Firefox y Edge
- **Futuro:** Diseñado para extensibilidad

---

## 📞 Soporte y Contacto

Para consultas sobre el plugin:
- **Documentación:** `docs/` directory
- **Ejemplos:** `examples/` directory
- **Pruebas:** `tests/` directory
- **Issues:** Sistema de tickets del proyecto

---

**Versión:** 2.1.0  
**Autor:** Sugar Team
