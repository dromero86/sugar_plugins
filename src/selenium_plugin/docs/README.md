# Plugin Selenium v2.0 para Sugar

## 📋 Descripción General

El plugin Selenium v2.0 para Sugar proporciona capacidades avanzadas de automatización web usando la sintaxis unificada `{"selenium": {"operator": ...}}`. Esta versión ha sido completamente rediseñada para ofrecer una experiencia más consistente, robusta y escalable.

### 🎯 Características Principales

- **Sintaxis unificada** `{"selenium": {"operator": ...}}` con operadores específicos
- **Soporte completo** para todos los navegadores de Selenium
- **Sistema avanzado de cookies** con arrays y propiedades completas
- **19 operadores disponibles** para automatización completa
- **Descarga automática de drivers** para todos los navegadores
- **Gestión robusta de errores** y timeouts configurables

---

## 🌐 Soporte de Navegadores

### Navegadores Soportados

| Navegador | Clave | Soporte | Plataforma | Características |
|-----------|-------|---------|------------|-----------------|
| **Chrome** | `chrome` | ✅ Completo | Multiplataforma | Headless, Detach, Auto-Download |
| **Firefox** | `firefox` | ✅ Completo | Multiplataforma | Headless, Auto-Download |
| **Edge** | `edge` | ✅ Completo | Multiplataforma | Headless, Detach, Auto-Download |
| **Safari** | `safari` | ✅ Completo | Solo macOS | Auto-Download, Limitaciones headless |
| **Opera** | `opera` | ✅ Completo | Multiplataforma | Headless, Detach, Auto-Download |
| **Internet Explorer** | `ie` | ⚠️ Limitado | Solo Windows | Sin headless, Deprecated |

### Configuración por Navegador

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",  // chrome, firefox, edge, safari, opera, ie
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
    "id": "is_clicked"
  }
}
```

### 2. **open** - Abrir navegador y URL
```json
{
  "selenium": {
    "operator": "open",
    "url": "https://example.com",
    "id": "is_open"
  }
}
```

### 3. **javascript** - Ejecutar código JavaScript
```json
{
  "selenium": {
    "operator": "javascript",
    "from_file": "./script.js",
    "id": "js_result"
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
    "id": "is_typed"
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
    "id": "element_found"
  }
}
```

### 6. **screenshot** - Capturar pantalla
```json
{
  "selenium": {
    "operator": "screenshot",
    "file": "./result.png",
    "id": "screenshot"
  }
}
```

### 7. **navigate** - Navegación básica
```json
{
  "selenium": {
    "operator": "navigate",
    "action": "refresh",
    "id": "navigated"
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
    "id": "found"
  }
}
```

### 9. **submit** - Enviar formularios
```json
{
  "selenium": {
    "operator": "submit",
    "selector": "form",
    "id": "submitted"
  }
}
```

### 10. **clear** - Limpiar campos
```json
{
  "selenium": {
    "operator": "clear",
    "selector": "input[name='q']",
    "id": "cleared"
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
    "id": "selected"
  }
}
```

### 12. **hover** - Pasar el mouse
```json
{
  "selenium": {
    "operator": "hover",
    "selector": ".menu-item",
    "id": "hovered"
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
    "id": "scrolled"
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
    "id": "uploaded"
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
    "id": "downloaded"
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
    "id": "cookies_added"
  }
}
```

### 17. **window** - Gestión de ventanas
```json
{
  "selenium": {
    "operator": "window",
    "action": "maximize",
    "id": "window_action"
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
    "id": "frame_action"
  }
}
```

### 19. **alert** - Manejar alertas
```json
{
  "selenium": {
    "operator": "alert",
    "action": "accept",
    "id": "alert_action"
  }
}
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
    "id": "cookies"
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
    "id": "cookie_added"
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
    "id": "cookies_added"
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
    "id": "cookie_deleted"
  }
}
```

#### 5. **clear** - Eliminar todas las cookies
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "clear",
    "id": "cookies_cleared"
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
    "id": "cookie_by_name"
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
    "id": "cookies_by_domain"
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
        "id": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='q']",
        "value": "Sugar automation",
        "id": "is_typed"
      }
    },
    {
      "selenium": {
        "operator": "click",
        "selector": "input[name='btnK']",
        "id": "is_clicked"
      }
    },
    {
      "selenium": {
        "operator": "screenshot",
        "file": "./google_result.png",
        "id": "screenshot"
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
        "id": "is_open"
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
        "id": "cookies_added"
      }
    },
    {
      "selenium": {
        "operator": "navigate",
        "action": "refresh",
        "id": "refreshed"
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
        "id": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "element",
        "selector": "form",
        "id": "form_loaded"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='name']",
        "value": "Juan Pérez",
        "id": "name_typed"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='email']",
        "value": "juan@example.com",
        "id": "email_typed"
      }
    },
    {
      "selenium": {
        "operator": "select",
        "selector": "select[name='country']",
        "value": "ES",
        "id": "country_selected"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "textarea[name='message']",
        "value": "Mensaje de prueba",
        "id": "message_typed"
      }
    },
    {
      "selenium": {
        "operator": "submit",
        "selector": "form",
        "id": "form_submitted"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "element",
        "selector": ".success-message",
        "id": "success_shown"
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

### 1. Instalación
```bash
pip install -e plugins/src/selenium/
```

### 2. Verificar Dependencias
```bash
pip install selenium>=4.0.0 webdriver-manager>=3.8.0
```

### 3. Ejecutar Script
```bash
sugar script.json
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
        "id": "is_open"
      }
    },
    {
      "selenium": {
        "operator": "wait",
        "type": "time",
        "seconds": 2,
        "id": "is_waited"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='q']",
        "value": "Sugar",
        "id": "is_typed"
      }
    },
    {
      "selenium": {
        "operator": "click",
        "selector": "input[name='btnK']",
        "id": "is_clicked"
      }
    },
    {
      "selenium": {
        "operator": "screenshot",
        "file": "./result.png",
        "id": "screenshot"
      }
    }
  ]
}
```

---

## ⚠️ Consideraciones y Limitaciones

### Limitaciones Conocidas
- **Safari:** Solo disponible en macOS
- **Internet Explorer:** Deprecated, limitado a Windows
- **Headless:** No soportado en Safari (versiones antiguas)
- **Detach:** No soportado en Firefox

### Requisitos del Sistema
- **Python:** >= 3.8
- **Navegadores:** Instalados según configuración
- **Permisos:** Escritura para descarga de drivers
- **Conexión:** Internet para descarga automática

### Compatibilidad
- **v1.0:** No compatible (requiere migración)
- **v2.0:** Compatible con todos los navegadores modernos
- **Futuro:** Diseñado para extensibilidad

---

## 📞 Soporte y Contacto

Para consultas sobre el plugin:
- **Documentación:** `docs/` directory
- **Ejemplos:** `examples/` directory
- **Pruebas:** `tests/` directory
- **Issues:** Sistema de tickets del proyecto

---

**Versión:** 2.0.0  
**Última actualización:** Diciembre 2024  
**Autor:** Sugar Team
