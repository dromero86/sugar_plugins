# Guía de Migración: Selenium Plugin v1.0 → v2.0

## 📋 Resumen de Cambios

El plugin Selenium v2.0 introduce cambios significativos en la sintaxis y funcionalidad para mejorar la consistencia, robustez y escalabilidad. Esta guía le ayudará a migrar sus scripts existentes de v1.0 a v2.0.

### 🔄 Cambios Principales

1. **Sintaxis unificada** `@selenium/` con operadores específicos
2. **Configuración simplificada** en la sección `meta`
3. **Sistema avanzado de cookies** con arrays y propiedades completas
4. **Soporte completo** para todos los navegadores
5. **Gestión mejorada de errores** y timeouts

---

## 🔧 Mapeo de Comandos

### Tabla de Migración Completa

| Comando v1.0 | Operador v2.0 | Cambios | Ejemplo |
|--------------|---------------|---------|---------|
| `click` | `click` | Sin cambios | ✅ Compatible |
| `open_browser` | `open` | Renombrado | ⚠️ Requiere cambio |
| `javascript` | `javascript` | Soporta `from_string` y `from_file` | ✅ Compatible |
| `type` | `type` | Agregado soporte para `enter` | ✅ Compatible |
| `wait` | `wait` | Tipos: `time`, `element`, `clickable` | ✅ Compatible |
| `screenshot` | `screenshot` | Sin cambios | ✅ Compatible |
| `navigate` | `navigate` | Acciones: `refresh`, `back`, `forward` | ✅ Compatible |
| `find_element` | `find` | Agregado soporte para `multiple` | ⚠️ Requiere cambio |
| `submit` | `submit` | Sin cambios | ✅ Compatible |
| `clear` | `clear` | Sin cambios | ✅ Compatible |
| `select` | `select` | Sin cambios | ✅ Compatible |
| `hover` | `hover` | Sin cambios | ✅ Compatible |
| `scroll` | `scroll` | Tipos: `to_element`, `by_pixels`, `to_position` | ✅ Compatible |
| `upload` | `upload` | Sin cambios | ✅ Compatible |
| `download` | `download` | Nuevo operador | 🆕 Nuevo |
| `cookies` | `cookies` | Acciones: `get`, `add`, `delete`, `clear` | ⚠️ Requiere cambio |
| `window` | `window` | Acciones: `switch`, `close`, `maximize`, `minimize` | ✅ Compatible |
| `frame` | `frame` | Acciones: `switch` | ✅ Compatible |
| `alert` | `alert` | Acciones: `accept`, `dismiss`, `send_keys` | ✅ Compatible |

---

## 📝 Ejemplos de Migración

### 1. **Comandos Básicos (Sin Cambios)**

#### v1.0
```json
{
  "click": { "selector": "#btn" },
  "type": { "selector": "input[name='q']", "value": "Sugar" },
  "screenshot": { "file": "./result.png" }
}
```

#### v2.0
```json
{
  "selenium": {
    "operator": "click",
    "selector": "#btn",
    "result": "is_clicked"
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
    "operator": "screenshot",
    "file": "./result.png",
    "result": "screenshot"
  }
}
```

### 2. **open_browser → open**

#### v1.0
```json
{
  "open_browser": { "url": "https://www.google.com" }
}
```

#### v2.0
```json
{
  "selenium": {
    "operator": "open",
    "url": "https://www.google.com",
    "result": "is_open"
  }
}
```

### 3. **find_element → find**

#### v1.0
```json
{
  "find_element": { "selector": ".item" }
}
```

#### v2.0
```json
{
  "selenium": {
    "operator": "find",
    "selector": ".item",
    "result": "found"
  }
}
```

### 4. **Sistema de Cookies Mejorado**

#### v1.0 (Cookie Individual)
```json
{
  "cookies": {
    "action": "add",
    "name": "session_id",
    "value": "abc123",
    "domain": ".example.com"
  }
}
```

#### v2.0 (Cookie Individual)
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "session_id",
    "value": "abc123",
    "domain": ".example.com",
    "secure": true,
    "httpOnly": false,
    "result": "cookie_added"
  }
}
```

#### v1.0 (Array de Cookies)
```json
{
  "cookies": {
    "action": "add",
    "cookies": [
      { "name": "session_id", "value": "abc123" },
      { "name": "user_id", "value": "456" }
    ]
  }
}
```

#### v2.0 (Array de Cookies Mejorado)
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
        "secure": true,
        "httpOnly": true
      },
      {
        "name": "user_id",
        "value": "456",
        "domain": ".example.com",
        "path": "/user"
      }
    ],
    "result": "cookies_added"
  }
}
```

---

## ⚙️ Configuración Meta

### v1.0
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false,
    "headless": true,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

### v2.0
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false,
    "headless": true,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

**Nota:** La configuración `meta` permanece igual en v2.0.

---

## 🔄 Script Completo de Migración

### Script Original (v1.0)
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false,
    "headless": true,
    "timeout": 10
  },
  "task": [
    { "open_browser": { "url": "https://www.google.com" } },
    { "wait": { "seconds": 2 } },
    { "type": { "selector": "input[name='q']", "value": "Sugar automation" } },
    { "click": { "selector": "input[name='btnK']" } },
    { "wait": { "type": "element", "selector": "#search" } },
    { "find_element": { "selector": ".g" } },
    { "screenshot": { "file": "./google_result.png" } },
    { "cookies": { "action": "get" } }
  ]
}
```

### Script Migrado (v2.0)
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": { "bin": "./driver/chromedriver" },
    "options": ["--disable-gpu", "--no-sandbox"],
    "detach": false,
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
        "operator": "wait",
        "type": "element",
        "selector": "#search",
        "result": "search_loaded"
      }
    },
    {
      "selenium": {
        "operator": "find",
        "selector": ".g",
        "result": "results_found"
      }
    },
    {
      "selenium": {
        "operator": "screenshot",
        "file": "./google_result.png",
        "result": "screenshot"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "get",
        "result": "cookies"
      }
    }
  ]
}
```

---

## 🆕 Nuevas Funcionalidades

### 1. **Operador download**
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

### 2. **Cookies con propiedades completas**
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
        "path": "/",
        "secure": true,
        "httpOnly": true,
        "expiry": "2024-12-31T23:59:59Z"
      }
    ],
    "result": "cookies_added"
  }
}
```

### 3. **Acciones adicionales de cookies**
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

---

## ⚠️ Cambios Importantes

### 1. **Sintaxis Obligatoria**
- Todos los comandos deben usar la sintaxis `selenium` con `operator`
- El parámetro `result` es recomendado para capturar resultados

### 2. **Manejo de Errores**
- Mejor gestión de errores con mensajes descriptivos
- Timeouts configurables por operación

### 3. **Compatibilidad de Navegadores**
- Soporte mejorado para todos los navegadores
- Descarga automática de drivers

### 4. **Sistema de Cookies**
- Propiedades completas de cookies
- Múltiples formatos de fecha
- Acciones adicionales de consulta

---

## 🔧 Herramientas de Migración

### Script de Migración Automática

Puede usar el siguiente script Python para migrar automáticamente sus archivos:

```python
import json
import re

def migrate_selenium_v1_to_v2(input_file, output_file):
    """Migra un script de Selenium v1.0 a v2.0."""
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Mapeo de comandos
    command_mapping = {
        'open_browser': 'open',
        'find_element': 'find'
    }
    
    # Migrar task
    if 'task' in data:
        new_task = []
        for item in data['task']:
            for old_cmd, new_cmd in command_mapping.items():
                if old_cmd in item:
                    # Crear nueva estructura
                    new_item = {
                        'selenium': {
                            'operator': new_cmd,
                            **item[old_cmd]
                        }
                    }
                    new_task.append(new_item)
                    break
            else:
                # Comando sin cambios
                if 'selenium' in item:
                    new_task.append(item)
                else:
                    # Migrar comando directo
                    for cmd, config in item.items():
                        new_item = {
                            'selenium': {
                                'operator': cmd,
                                **config
                            }
                        }
                        new_task.append(new_item)
        
        data['task'] = new_task
    
    # Guardar archivo migrado
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

# Uso
migrate_selenium_v1_to_v2('script_v1.json', 'script_v2.json')
```

---

## ✅ Checklist de Migración

### Antes de Migrar
- [ ] Hacer backup de todos los scripts v1.0
- [ ] Identificar scripts críticos
- [ ] Documentar casos de uso específicos

### Durante la Migración
- [ ] Migrar configuración `meta` (sin cambios)
- [ ] Convertir comandos directos a sintaxis `selenium`
- [ ] Agregar parámetros `result` donde sea necesario
- [ ] Actualizar comandos `open_browser` → `open`
- [ ] Actualizar comandos `find_element` → `find`
- [ ] Migrar sistema de cookies si se usa

### Después de Migrar
- [ ] Probar scripts migrados
- [ ] Verificar funcionalidad en navegadores objetivo
- [ ] Validar resultados esperados
- [ ] Optimizar configuración según necesidades

---

## 🚨 Problemas Comunes

### 1. **Error: "Operador no soportado"**
**Causa:** Comando no migrado a sintaxis `selenium`
**Solución:** Usar sintaxis `{"selenium": {"operator": "comando", ...}}`

### 2. **Error: "Elemento no encontrado"**
**Causa:** Selector incorrecto o página no cargada
**Solución:** Agregar `wait` antes de interactuar con elementos

### 3. **Error: "Driver no inicializado"**
**Causa:** Configuración incorrecta en `meta`
**Solución:** Verificar configuración de navegador y driver

### 4. **Error: "Cookie inválida"**
**Causa:** Propiedades de cookie incorrectas
**Solución:** Usar estructura completa de cookies con propiedades válidas

---

## 📞 Soporte

Si encuentra problemas durante la migración:

1. **Revisar documentación:** `docs/README.md`
2. **Consultar ejemplos:** `examples/` directory
3. **Ejecutar pruebas:** `tests/` directory
4. **Reportar issues:** Sistema de tickets del proyecto

---

**Versión:** 2.1.0
**Autor:** Sugar Team
