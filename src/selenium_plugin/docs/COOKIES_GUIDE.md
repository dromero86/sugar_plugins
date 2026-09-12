# Guía Completa de Cookies - Selenium Plugin v2.0

## 📋 Descripción General

El plugin Selenium v2.0 proporciona un sistema avanzado de gestión de cookies con soporte completo para todas las propiedades de cookies web, arrays de cookies y múltiples acciones. Esta guía cubre todos los aspectos del sistema de cookies.

---

## 🍪 Estructura Completa de Cookies

### Propiedades de Cookie

Cada cookie soporta todos los elementos clave de la especificación HTTP:

| Propiedad | Tipo | Requerido | Descripción | Ejemplo |
|-----------|------|-----------|-------------|---------|
| **name** | string | ✅ | Nombre de la cookie | `"session_id"` |
| **value** | string | ✅ | Valor de la cookie | `"abc123def456"` |
| **domain** | string | ❌ | Dominio al que se aplica | `".example.com"` |
| **path** | string | ❌ | Ruta específica | `"/api"` |
| **expiry** | string/int | ❌ | Fecha de caducidad | `"2024-12-31T23:59:59Z"` |
| **secure** | boolean | ❌ | Solo se envía por HTTPS | `true` |
| **httpOnly** | boolean | ❌ | No accesible via JavaScript | `false` |

### Formatos de Fecha Soportados

El plugin soporta múltiples formatos de fecha para la propiedad `expiry`:

#### 1. **ISO 8601 String**
```json
{
  "name": "session_id",
  "value": "abc123",
  "expiry": "2024-12-31T23:59:59Z"
}
```

#### 2. **ISO 8601 con Timezone**
```json
{
  "name": "session_id",
  "value": "abc123",
  "expiry": "2024-12-31T23:59:59+00:00"
}
```

#### 3. **Timestamp Unix**
```json
{
  "name": "session_id",
  "value": "abc123",
  "expiry": 1735689599
}
```

#### 4. **Fecha Relativa (días desde ahora)**
```json
{
  "name": "session_id",
  "value": "abc123",
  "expiry": "7d"  // 7 días desde ahora
}
```

---

## 🔧 Acciones de Cookies Disponibles

### 1. **get** - Obtener todas las cookies

Obtiene todas las cookies del dominio actual.

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "id": "cookies"
  }
}
```

**Resultado:**
```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123def456",
      "domain": ".example.com",
      "path": "/",
      "expiry": 1735689599,
      "secure": true,
      "httpOnly": true
    },
    {
      "name": "user_preferences",
      "value": "dark_mode,notifications_enabled",
      "domain": ".example.com",
      "path": "/settings"
    }
  ]
}
```

### 2. **add** - Agregar cookie individual

Agrega una cookie individual con propiedades completas.

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

### 3. **add** - Agregar array de cookies

Agrega múltiples cookies en una sola operación.

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
      },
      {
        "name": "analytics_id",
        "value": "ga_123456789",
        "domain": ".example.com",
        "expiry": "30d"
      }
    ],
    "id": "cookies_added"
  }
}
```

### 4. **delete** - Eliminar cookie específica

Elimina una cookie por nombre.

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

### 5. **clear** - Eliminar todas las cookies

Elimina todas las cookies del dominio actual.

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "clear",
    "id": "cookies_cleared"
  }
}
```

### 6. **get_by_name** - Obtener cookie por nombre

Obtiene una cookie específica por nombre.

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

**Resultado:**
```json
{
  "cookie_by_name": {
    "name": "session_id",
    "value": "abc123def456",
    "domain": ".example.com",
    "path": "/",
    "expiry": 1735689599,
    "secure": true,
    "httpOnly": true
  }
}
```

### 7. **get_by_domain** - Obtener cookies por dominio

Obtiene todas las cookies de un dominio específico.

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

**Resultado:**
```json
{
  "cookies_by_domain": [
    {
      "name": "session_id",
      "value": "abc123def456",
      "domain": ".example.com",
      "path": "/"
    },
    {
      "name": "user_preferences",
      "value": "dark_mode",
      "domain": ".example.com",
      "path": "/settings"
    }
  ]
}
```

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Configuración de Sesión

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "headless": true
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
            "name": "session_id",
            "value": "abc123def456",
            "domain": ".example.com",
            "secure": true,
            "httpOnly": true,
            "expiry": "2024-12-31T23:59:59Z"
          },
          {
            "name": "user_id",
            "value": "12345",
            "domain": ".example.com",
            "path": "/user"
          },
          {
            "name": "theme",
            "value": "dark",
            "domain": ".example.com",
            "path": "/settings"
          }
        ],
        "id": "session_cookies_added"
      }
    },
    {
      "selenium": {
        "operator": "navigate",
        "action": "refresh",
        "id": "page_refreshed"
      }
    }
  ]
}
```

### Ejemplo 2: Gestión de Autenticación

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox"
  },
  "task": [
    {
      "selenium": {
        "operator": "open",
        "url": "https://app.example.com/login",
        "id": "login_page_open"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='username']",
        "value": "user@example.com",
        "id": "username_typed"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "input[name='password']",
        "value": "password123",
        "id": "password_typed"
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
        "selector": ".dashboard",
        "id": "dashboard_loaded"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "get",
        "id": "auth_cookies"
      }
    }
  ]
}
```

### Ejemplo 3: Limpieza de Cookies

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome"
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
        "action": "get",
        "id": "cookies_before"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "delete",
        "name": "tracking_cookie",
        "id": "tracking_deleted"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "clear",
        "id": "all_cleared"
      }
    },
    {
      "selenium": {
        "operator": "cookies",
        "action": "get",
        "id": "cookies_after"
      }
    }
  ]
}
```

### Ejemplo 4: Configuración de Preferencias

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "edge"
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
            "name": "language",
            "value": "es",
            "domain": ".example.com",
            "path": "/",
            "expiry": "365d"
          },
          {
            "name": "timezone",
            "value": "America/Mexico_City",
            "domain": ".example.com",
            "path": "/",
            "expiry": "365d"
          },
          {
            "name": "notifications",
            "value": "enabled",
            "domain": ".example.com",
            "path": "/settings",
            "expiry": "30d"
          }
        ],
        "id": "preferences_set"
      }
    }
  ]
}
```

---

## 🔒 Configuraciones de Seguridad

### Cookies Seguras

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "auth_token",
    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "domain": ".example.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "expiry": "2024-12-31T23:59:59Z",
    "id": "secure_cookie_added"
  }
}
```

### Cookies de Sesión

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "session_id",
    "value": "sess_abc123def456",
    "domain": ".example.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "id": "session_cookie_added"
  }
}
```

### Cookies de Análisis

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "_ga",
    "value": "GA1.2.123456789.1234567890",
    "domain": ".example.com",
    "path": "/",
    "expiry": "730d",
    "id": "analytics_cookie_added"
  }
}
```

---

## ⚠️ Consideraciones Importantes

### 1. **Dominios y Rutas**

- **Dominio:** Debe coincidir con el dominio de la página actual
- **Ruta:** Define el alcance de la cookie en el sitio
- **Subdominios:** Usar `.example.com` para incluir subdominios

### 2. **Seguridad**

- **Secure:** Solo se envía por HTTPS
- **HttpOnly:** No accesible via JavaScript
- **SameSite:** Controlado por el navegador

### 3. **Fechas de Caducidad**

- **Sesión:** No especificar `expiry` para cookies de sesión
- **Persistentes:** Usar fechas futuras específicas
- **Relativas:** Usar formatos como `"7d"`, `"30d"`, `"1y"`

### 4. **Limitaciones del Navegador**

- **Tamaño:** Límite de 4KB por cookie
- **Cantidad:** Límite de 50 cookies por dominio
- **Caracteres:** Algunos caracteres especiales pueden causar problemas

---

## 🚨 Problemas Comunes

### 1. **Error: "Cookie inválida"**

**Causa:** Propiedades de cookie incorrectas
**Solución:**
```json
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "name": "test_cookie",
    "value": "test_value",
    "domain": ".example.com",
    "id": "cookie_added"
  }
}
```

### 2. **Error: "Dominio no válido"**

**Causa:** Dominio no coincide con la página actual
**Solución:** Usar el dominio correcto o omitir la propiedad `domain`

### 3. **Error: "Fecha de caducidad inválida"**

**Causa:** Formato de fecha incorrecto
**Solución:** Usar formato ISO 8601 o timestamp Unix

### 4. **Error: "Cookie no encontrada"**

**Causa:** Cookie no existe o nombre incorrecto
**Solución:** Verificar el nombre exacto de la cookie

---

## 🔧 Casos de Uso Avanzados

### 1. **Migración de Sesiones**

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "id": "old_cookies"
  }
},
{
  "selenium": {
    "operator": "open",
    "url": "https://new.example.com",
    "id": "new_site_open"
  }
},
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "cookies": "{{old_cookies}}",
    "id": "cookies_migrated"
  }
}
```

### 2. **Backup de Cookies**

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "id": "cookies_backup"
  }
},
{
  "selenium": {
    "operator": "javascript",
    "from_string": "localStorage.setItem('cookies_backup', JSON.stringify({{cookies_backup}}))",
    "id": "backup_saved"
  }
}
```

### 3. **Restauración de Cookies**

```json
{
  "selenium": {
    "operator": "javascript",
    "from_string": "return JSON.parse(localStorage.getItem('cookies_backup'))",
    "id": "cookies_restore"
  }
},
{
  "selenium": {
    "operator": "cookies",
    "action": "add",
    "cookies": "{{cookies_restore}}",
    "id": "cookies_restored"
  }
}
```

---

## 📊 Monitoreo y Debugging

### Verificar Cookies Existentes

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "id": "current_cookies"
  }
},
{
  "selenium": {
    "operator": "javascript",
    "from_string": "console.log('Cookies actuales:', {{current_cookies}})",
    "id": "cookies_logged"
  }
}
```

### Contar Cookies por Dominio

```json
{
  "selenium": {
    "operator": "cookies",
    "action": "get",
    "id": "all_cookies"
  }
},
{
  "selenium": {
    "operator": "javascript",
    "from_string": "return {{all_cookies}}.length",
    "id": "cookie_count"
  }
}
```

---

## 📞 Soporte

Para problemas específicos con cookies:

1. **Verificar documentación:** `docs/README.md`
2. **Consultar ejemplos:** `examples/cookies_example.json`
3. **Revisar pruebas:** `tests/test_selenium_plugin.py`
4. **Reportar issues:** Sistema de tickets del proyecto

---

**Versión:** 2.0.0  
**Última actualización:** Diciembre 2024  
**Autor:** Sugar Team
