# HTTP Session Plugin

El plugin HTTP Session proporciona funcionalidades para gestionar sesiones HTTP persistentes con cookies, headers y estado compartido entre múltiples peticiones.

## Características

- **Sesiones persistentes**: Mantener cookies y estado entre peticiones
- **Gestión de cookies**: Cookies automáticas y manuales
- **Headers compartidos**: Headers comunes para todas las peticiones
- **Autenticación**: Mantener autenticación en sesión
- **Gestión de estado**: Estado compartido entre peticiones
- **Múltiples sesiones**: Gestionar múltiples sesiones simultáneamente

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `requests>=2.25.0`
- `urllib3>=1.26.0`

## Uso

### 1. Crear Sesión Básica

```json
{
  "http_session": {
    "name": "api_session",
    "base_url": "https://api.example.com",
    "headers": {
      "User-Agent": "Sugar Bot 1.0",
      "Accept": "application/json"
    },
    "result": "session_created"
  }
}
```

### 2. Petición con Sesión

```json
{
  "http_session": {
    "name": "api_session",
    "request": {
      "method": "GET",
      "endpoint": "/users",
      "result": "users_data"
    }
  }
}
```

### 3. Login con Sesión

```json
{
  "http_session": {
    "name": "api_session",
    "request": {
      "method": "POST",
      "endpoint": "/login",
      "json": {
        "username": "{{ username }}",
        "password": "{{ password }}"
      },
      "result": "login_response"
    }
  }
}
```

### 4. Petición Autenticada

```json
{
  "http_session": {
    "name": "api_session",
    "request": {
      "method": "GET",
      "endpoint": "/secure-data",
      "result": "secure_data"
    }
  }
}
```

### 5. Múltiples Peticiones

```json
{
  "http_session": {
    "name": "api_session",
    "requests": [
      {
        "method": "GET",
        "endpoint": "/users",
        "result": "users"
      },
      {
        "method": "GET",
        "endpoint": "/posts",
        "result": "posts"
      }
    ]
  }
}
```

## Parámetros

### Configuración de Sesión
- `name` (string, requerido): Nombre de la sesión
- `base_url` (string, opcional): URL base para todas las peticiones
- `headers` (object, opcional): Headers por defecto
- `cookies` (object, opcional): Cookies iniciales
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Petición
- `method` (string, opcional): Método HTTP
- `endpoint` (string, opcional): Endpoint relativo a base_url
- `url` (string, opcional): URL completa (ignora base_url)
- `headers` (object, opcional): Headers específicos para esta petición
- `data` (object/string, opcional): Datos a enviar
- `json` (object, opcional): Datos JSON a enviar

### Configuración Avanzada
- `timeout` (integer, opcional): Timeout en segundos
- `verify` (boolean, opcional): Verificar SSL
- `allow_redirects` (boolean, opcional): Permitir redirecciones
- `stream` (boolean, opcional): Stream de respuesta

## Operaciones Disponibles

### Gestión de Sesiones
- **Crear sesión**: Inicializar nueva sesión
- **Usar sesión**: Realizar peticiones con sesión existente
- **Cerrar sesión**: Finalizar y limpiar sesión
- **Listar sesiones**: Ver sesiones activas

### Gestión de Cookies
- **Cookies automáticas**: Manejo automático de cookies
- **Cookies manuales**: Establecer cookies específicas
- **Persistencia**: Mantener cookies entre peticiones
- **Limpieza**: Limpiar cookies específicas

### Gestión de Headers
- **Headers por defecto**: Headers aplicados a todas las peticiones
- **Headers específicos**: Headers para peticiones individuales
- **Headers dinámicos**: Headers que cambian automáticamente
- **Headers de autenticación**: Headers de auth automáticos

## Ejemplos Avanzados

### Sesión con Autenticación OAuth

```json
{
  "http_session": {
    "name": "oauth_session",
    "base_url": "https://api.example.com",
    "auth": {
      "type": "oauth2",
      "client_id": "{{ client_id }}",
      "client_secret": "{{ client_secret }}",
      "token_url": "/oauth/token"
    },
    "result": "oauth_session"
  }
}
```

### Sesión con Retry Automático

```json
{
  "http_session": {
    "name": "retry_session",
    "base_url": "https://api.example.com",
    "retry": {
      "max_attempts": 3,
      "backoff_factor": 2,
      "status_codes": [500, 502, 503, 504]
    },
    "result": "retry_session"
  }
}
```

### Sesión con Cache

```json
{
  "http_session": {
    "name": "cache_session",
    "base_url": "https://api.example.com",
    "cache": {
      "enabled": true,
      "ttl": 3600,
      "max_size": "100MB"
    },
    "result": "cache_session"
  }
}
```

### Sesión con Rate Limiting

```json
{
  "http_session": {
    "name": "rate_limited_session",
    "base_url": "https://api.example.com",
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000,
      "strategy": "delay"
    },
    "result": "rate_limited_session"
  }
}
```

### Sesión con Validación

```json
{
  "http_session": {
    "name": "validated_session",
    "base_url": "https://api.example.com",
    "validation": {
      "status_codes": [200, 201, 204],
      "content_type": "application/json",
      "schema": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"}
        }
      }
    },
    "result": "validated_session"
  }
}
```

### Sesión con Transformación

```json
{
  "http_session": {
    "name": "transform_session",
    "base_url": "https://api.example.com",
    "transform": {
      "response": {
        "extract": "data",
        "map": {
          "id": "item_id",
          "name": "item_name"
        }
      }
    },
    "result": "transform_session"
  }
}
```

## Configuración de Seguridad

### Configuración SSL
```json
{
  "http_session": {
    "name": "secure_session",
    "base_url": "https://secure.example.com",
    "ssl": {
      "verify": true,
      "cert": "/path/to/cert.pem",
      "key": "/path/to/key.pem"
    },
    "result": "secure_session"
  }
}
```

### Configuración de Proxy
```json
{
  "http_session": {
    "name": "proxied_session",
    "base_url": "https://api.example.com",
    "proxy": {
      "http": "http://proxy.example.com:8080",
      "https": "https://proxy.example.com:8080"
    },
    "result": "proxied_session"
  }
}
```

## Manejo de Errores

### Configuración de Errores
```json
{
  "http_session": {
    "name": "error_session",
    "base_url": "https://api.example.com",
    "error_handling": {
      "raise_on_4xx": false,
      "raise_on_5xx": true,
      "timeout_retry": 3,
      "session_recovery": true
    },
    "result": "error_session"
  }
}
```

### Validación de Sesión
```json
{
  "http_session": {
    "name": "validated_session",
    "base_url": "https://api.example.com",
    "validation": {
      "required_cookies": ["session_id", "csrf_token"],
      "required_headers": ["Authorization"],
      "health_check": "/health"
    },
    "result": "validated_session"
  }
}
```

## Optimización

### Configuración de Rendimiento
```json
{
  "http_session": {
    "name": "fast_session",
    "base_url": "https://api.example.com",
    "performance": {
      "connection_pool": true,
      "keep_alive": true,
      "compression": true,
      "timeout": {
        "connect": 5,
        "read": 30
      }
    },
    "result": "fast_session"
  }
}
```

### Configuración de Memoria
```json
{
  "http_session": {
    "name": "memory_session",
    "base_url": "https://api.example.com",
    "memory": {
      "max_cookies": 100,
      "max_headers": 50,
      "clear_on_close": true
    },
    "result": "memory_session"
  }
}
```

## Recursos Adicionales

- [Documentación de requests](https://requests.readthedocs.io/)
- [Guía de Sesiones HTTP](../../../docs/development/api_integration.md) 