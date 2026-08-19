# Request Plugin

El plugin Request proporciona funcionalidades para realizar peticiones HTTP nativas con configuración avanzada y manejo de respuestas.

## Características

- **Peticiones HTTP**: GET, POST, PUT, DELETE, PATCH
- **Configuración avanzada**: Headers, cookies, timeouts
- **Autenticación**: Basic, Bearer, OAuth, API Keys
- **Manejo de respuestas**: JSON, XML, texto, archivos
- **Gestión de sesiones**: Mantener cookies y estado
- **Retry automático**: Reintentos configurables
- **Validación**: Validación de respuestas y esquemas

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `requests>=2.25.0`
- `urllib3>=1.26.0`

## Uso

### 1. Petición GET Básica

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/users",
    "result": "response_data"
  }
}
```

### 2. Petición POST con Datos

```json
{
  "request": {
    "method": "POST",
    "url": "https://api.example.com/users",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer {{ token }}"
    },
    "data": {
      "name": "Juan Pérez",
      "email": "juan@example.com"
    },
    "result": "create_response"
  }
}
```

### 3. Petición con Parámetros

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/search",
    "params": {
      "q": "sugar",
      "limit": 10,
      "offset": 0
    },
    "result": "search_results"
  }
}
```

### 4. Subir Archivo

```json
{
  "request": {
    "method": "POST",
    "url": "https://api.example.com/upload",
    "files": {
      "document": "/path/to/file.pdf"
    },
    "result": "upload_response"
  }
}
```

### 5. Petición con Autenticación

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/secure",
    "auth": {
      "type": "basic",
      "username": "{{ username }}",
      "password": "{{ password }}"
    },
    "result": "secure_data"
  }
}
```

## Parámetros

### Configuración Básica
- `method` (string, requerido): Método HTTP (GET, POST, PUT, DELETE, PATCH)
- `url` (string, requerido): URL de la petición
- `result` (string, opcional): Variable para almacenar el resultado

### Headers y Configuración
- `headers` (object, opcional): Headers HTTP personalizados
- `params` (object, opcional): Parámetros de query string
- `data` (object/string, opcional): Datos a enviar en el body
- `json` (object, opcional): Datos JSON a enviar

### Autenticación
- `auth` (object, opcional): Configuración de autenticación
  - `type`: basic, bearer, oauth, api_key
  - `username`, `password`: Para autenticación básica
  - `token`: Para Bearer token
  - `api_key`: Para API key

### Configuración Avanzada
- `timeout` (integer, opcional): Timeout en segundos
- `verify` (boolean, opcional): Verificar SSL (default: true)
- `allow_redirects` (boolean, opcional): Permitir redirecciones (default: true)
- `stream` (boolean, opcional): Stream de respuesta (default: false)

### Archivos y Datos
- `files` (object, opcional): Archivos a subir
- `cookies` (object, opcional): Cookies a enviar
- `proxies` (object, opcional): Configuración de proxy

## Operaciones Disponibles

### Métodos HTTP
- **GET**: Obtener recursos
- **POST**: Crear recursos
- **PUT**: Actualizar recursos completos
- **PATCH**: Actualizar recursos parcialmente
- **DELETE**: Eliminar recursos
- **HEAD**: Obtener headers
- **OPTIONS**: Obtener opciones

### Tipos de Autenticación
- **Basic**: Usuario y contraseña
- **Bearer**: Token de acceso
- **OAuth**: OAuth 1.0/2.0
- **API Key**: Clave de API
- **Digest**: Autenticación digest

### Formatos de Respuesta
- **JSON**: Respuesta JSON automática
- **XML**: Respuesta XML
- **Texto**: Respuesta como texto
- **Binario**: Respuesta binaria
- **Stream**: Respuesta en stream

## Ejemplos Avanzados

### Petición con Retry

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/data",
    "retry": {
      "max_attempts": 3,
      "backoff_factor": 2,
      "status_codes": [500, 502, 503, 504]
    },
    "result": "retry_response"
  }
}
```

### Petición con Validación

```json
{
  "request": {
    "method": "POST",
    "url": "https://api.example.com/users",
    "json": {
      "name": "Ana García",
      "email": "ana@example.com"
    },
    "validation": {
      "status_code": 201,
      "schema": {
        "type": "object",
        "properties": {
          "id": {"type": "integer"},
          "name": {"type": "string"},
          "email": {"type": "string"}
        }
      }
    },
    "result": "validated_response"
  }
}
```

### Petición con Sesión

```json
{
  "request": {
    "method": "POST",
    "url": "https://api.example.com/login",
    "json": {
      "username": "{{ username }}",
      "password": "{{ password }}"
    },
    "session": {
      "name": "api_session",
      "persist": true
    },
    "result": "login_response"
  }
}
```

### Petición con Rate Limiting

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/rate-limited",
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000,
      "strategy": "delay"
    },
    "result": "rate_limited_response"
  }
}
```

### Petición con Cache

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/cacheable",
    "cache": {
      "enabled": true,
      "ttl": 3600,
      "key": "api_data_{{ params.q }}"
    },
    "result": "cached_response"
  }
}
```

### Petición con Transformación

```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/transform",
    "transform": {
      "response": {
        "extract": "data.items",
        "map": {
          "id": "item_id",
          "title": "item_title",
          "price": "item_price"
        }
      }
    },
    "result": "transformed_response"
  }
}
```

## Configuración de Seguridad

### Configuración SSL
```json
{
  "request": {
    "method": "GET",
    "url": "https://secure.example.com",
    "ssl": {
      "verify": true,
      "cert": "/path/to/cert.pem",
      "key": "/path/to/key.pem",
      "ca_bundle": "/path/to/ca-bundle.crt"
    },
    "result": "secure_response"
  }
}
```

### Configuración de Proxy
```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com",
    "proxy": {
      "http": "http://proxy.example.com:8080",
      "https": "https://proxy.example.com:8080",
      "auth": {
        "username": "{{ proxy_user }}",
        "password": "{{ proxy_pass }}"
      }
    },
    "result": "proxied_response"
  }
}
```

## Manejo de Errores

### Configuración de Errores
```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/error-prone",
    "error_handling": {
      "raise_on_4xx": false,
      "raise_on_5xx": true,
      "timeout_retry": 3,
      "custom_errors": {
        "429": "Rate limit exceeded",
        "503": "Service unavailable"
      }
    },
    "result": "error_handled_response"
  }
}
```

### Validación de Respuesta
```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/validate",
    "validation": {
      "required_fields": ["id", "name", "status"],
      "status_codes": [200, 201],
      "content_type": "application/json",
      "max_size": "1MB"
    },
    "result": "validated_response"
  }
}
```

## Optimización

### Configuración de Rendimiento
```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/performance",
    "performance": {
      "connection_pool": true,
      "keep_alive": true,
      "compression": true,
      "timeout": {
        "connect": 5,
        "read": 30
      }
    },
    "result": "fast_response"
  }
}
```

### Configuración de Memoria
```json
{
  "request": {
    "method": "GET",
    "url": "https://api.example.com/large-file",
    "memory": {
      "stream": true,
      "chunk_size": 8192,
      "max_size": "100MB"
    },
    "result": "memory_efficient_response"
  }
}
```

## Recursos Adicionales

- [Documentación de requests](https://requests.readthedocs.io/)
- [Guía de APIs REST](../../../docs/development/api_integration.md) 