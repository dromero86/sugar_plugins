# cURL Plugin

El plugin cURL proporciona funcionalidades avanzadas para realizar peticiones HTTP usando la biblioteca cURL, ofreciendo control granular sobre configuraciones SSL, proxies, autenticación y otros parámetros avanzados.

## Características

- **Peticiones HTTP avanzadas**: Control completo sobre peticiones HTTP
- **Configuración SSL**: Certificados, verificación, opciones SSL
- **Gestión de proxies**: Configuración de proxies HTTP/HTTPS/SOCKS
- **Autenticación**: Basic, Digest, NTLM, OAuth
- **Cookies**: Gestión automática y manual de cookies
- **Headers personalizados**: Headers HTTP completamente configurables
- **Múltiples protocolos**: HTTP, HTTPS, FTP, FTPS, SFTP

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `pycurl>=7.45.0`
- `certifi>=2021.5.30`

## Uso

### 1. Petición GET Básica

```json
{
  "curl": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "result": "response_data"
  }
}
```

### 2. Petición POST con Datos

```json
{
  "curl": {
    "url": "https://api.example.com/users",
    "method": "POST",
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

### 3. Petición con Configuración SSL

```json
{
  "curl": {
    "url": "https://secure.example.com",
    "method": "GET",
    "ssl": {
      "verify": true,
      "cert": "/path/to/client.crt",
      "key": "/path/to/client.key",
      "ca_bundle": "/path/to/ca-bundle.crt"
    },
    "result": "secure_response"
  }
}
```

### 4. Petición con Proxy

```json
{
  "curl": {
    "url": "https://api.example.com",
    "method": "GET",
    "proxy": {
      "type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "username": "{{ proxy_user }}",
      "password": "{{ proxy_pass }}"
    },
    "result": "proxied_response"
  }
}
```

### 5. Petición con Autenticación

```json
{
  "curl": {
    "url": "https://api.example.com/secure",
    "method": "GET",
    "auth": {
      "type": "basic",
      "username": "{{ username }}",
      "password": "{{ password }}"
    },
    "result": "authenticated_response"
  }
}
```

## Parámetros

### Configuración Básica
- `url` (string, requerido): URL de la petición
- `method` (string, opcional): Método HTTP (GET, POST, PUT, DELETE, etc.)
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Headers
- `headers` (object, opcional): Headers HTTP personalizados
- `user_agent` (string, opcional): User-Agent personalizado
- `referer` (string, opcional): Referer personalizado

### Configuración de Datos
- `data` (object/string, opcional): Datos a enviar
- `json` (object, opcional): Datos JSON a enviar
- `form_data` (object, opcional): Datos de formulario
- `files` (object, opcional): Archivos a subir

### Configuración SSL
- `ssl` (object, opcional): Configuración SSL
  - `verify`: Verificar certificados
  - `cert`: Certificado cliente
  - `key`: Clave privada
  - `ca_bundle`: Bundle de certificados CA

### Configuración de Proxy
- `proxy` (object, opcional): Configuración de proxy
  - `type`: Tipo de proxy (http, https, socks4, socks5)
  - `host`: Host del proxy
  - `port`: Puerto del proxy
  - `username`: Usuario del proxy
  - `password`: Contraseña del proxy

### Configuración de Autenticación
- `auth` (object, opcional): Configuración de autenticación
  - `type`: Tipo de auth (basic, digest, ntlm, oauth)
  - `username`: Nombre de usuario
  - `password`: Contraseña
  - `token`: Token de acceso

### Configuración Avanzada
- `timeout` (integer, opcional): Timeout en segundos
- `follow_redirects` (boolean, opcional): Seguir redirecciones
- `max_redirects` (integer, opcional): Máximo de redirecciones
- `cookies` (object, opcional): Cookies a enviar

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
- **Basic**: Autenticación básica HTTP
- **Digest**: Autenticación digest
- **NTLM**: Autenticación NTLM
- **OAuth**: Autenticación OAuth
- **Bearer**: Token Bearer

### Tipos de Proxy
- **HTTP**: Proxy HTTP
- **HTTPS**: Proxy HTTPS
- **SOCKS4**: Proxy SOCKS4
- **SOCKS5**: Proxy SOCKS5

## Ejemplos Avanzados

### Petición con Configuración Completa

```json
{
  "curl": {
    "url": "https://api.example.com/complex",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": "{{ api_key }}",
      "X-Request-ID": "{{ request_id }}"
    },
    "json": {
      "data": "{{ payload }}"
    },
    "ssl": {
      "verify": true,
      "cert": "/path/to/cert.pem",
      "key": "/path/to/key.pem"
    },
    "timeout": 30,
    "follow_redirects": true,
    "max_redirects": 5,
    "result": "complex_response"
  }
}
```

### Petición con Cookies Persistentes

```json
{
  "curl": {
    "url": "https://example.com/login",
    "method": "POST",
    "data": {
      "username": "{{ username }}",
      "password": "{{ password }}"
    },
    "cookies": {
      "session_id": "{{ session_id }}",
      "csrf_token": "{{ csrf_token }}"
    },
    "save_cookies": true,
    "result": "login_response"
  }
}
```

### Petición con Retry Automático

```json
{
  "curl": {
    "url": "https://api.example.com/unreliable",
    "method": "GET",
    "retry": {
      "max_attempts": 3,
      "backoff_factor": 2,
      "status_codes": [500, 502, 503, 504]
    },
    "result": "retry_response"
  }
}
```

### Petición con Rate Limiting

```json
{
  "curl": {
    "url": "https://api.example.com/rate-limited",
    "method": "GET",
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000,
      "strategy": "delay"
    },
    "result": "rate_limited_response"
  }
}
```

### Petición con Compresión

```json
{
  "curl": {
    "url": "https://api.example.com/compressed",
    "method": "GET",
    "compression": {
      "accept_encoding": ["gzip", "deflate", "br"],
      "decompress": true
    },
    "result": "compressed_response"
  }
}
```

### Petición con Multipart

```json
{
  "curl": {
    "url": "https://api.example.com/upload",
    "method": "POST",
    "multipart": {
      "file": "/path/to/file.pdf",
      "description": "Documento importante",
      "category": "documents"
    },
    "result": "upload_response"
  }
}
```

## Configuración de SSL

### Configuración SSL Completa
```json
{
  "curl": {
    "url": "https://secure.example.com",
    "method": "GET",
    "ssl": {
      "verify": true,
      "cert": "/path/to/client.crt",
      "key": "/path/to/client.key",
      "ca_bundle": "/path/to/ca-bundle.crt",
      "verify_hostname": true,
      "verify_peer": true,
      "ssl_version": "TLSv1.2"
    },
    "result": "ssl_response"
  }
}
```

### Configuración SSL Insegura (Solo para desarrollo)
```json
{
  "curl": {
    "url": "https://dev.example.com",
    "method": "GET",
    "ssl": {
      "verify": false,
      "verify_hostname": false,
      "verify_peer": false
    },
    "result": "insecure_response"
  }
}
```

## Configuración de Proxy

### Proxy HTTP
```json
{
  "curl": {
    "url": "https://api.example.com",
    "method": "GET",
    "proxy": {
      "type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "username": "{{ proxy_user }}",
      "password": "{{ proxy_pass }}"
    },
    "result": "http_proxy_response"
  }
}
```

### Proxy SOCKS5
```json
{
  "curl": {
    "url": "https://api.example.com",
    "method": "GET",
    "proxy": {
      "type": "socks5",
      "host": "socks.example.com",
      "port": 1080
    },
    "result": "socks5_response"
  }
}
```

## Manejo de Errores

### Configuración de Errores
```json
{
  "curl": {
    "url": "https://api.example.com/error-prone",
    "method": "GET",
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
  "curl": {
    "url": "https://api.example.com/validate",
    "method": "GET",
    "validation": {
      "status_codes": [200, 201],
      "content_type": "application/json",
      "required_headers": ["X-API-Version"],
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
  "curl": {
    "url": "https://api.example.com/performance",
    "method": "GET",
    "performance": {
      "connection_timeout": 10,
      "transfer_timeout": 30,
      "dns_cache": true,
      "keep_alive": true,
      "compression": true
    },
    "result": "fast_response"
  }
}
```

### Configuración de Memoria
```json
{
  "curl": {
    "url": "https://api.example.com/large-file",
    "method": "GET",
    "memory": {
      "stream": true,
      "chunk_size": 8192,
      "max_size": "100MB"
    },
    "result": "memory_efficient_response"
  }
}
```

## Configuración de Seguridad

### Configuración Segura
```json
{
  "curl": {
    "url": "https://secure.example.com",
    "method": "GET",
    "security": {
      "ssl_verify": true,
      "ssl_cert": "/path/to/cert.pem",
      "ssl_key": "/path/to/key.pem",
      "user_agent": "Sugar Bot 1.0",
      "disable_redirects": false,
      "max_redirects": 5
    },
    "result": "secure_response"
  }
}
```

## Recursos Adicionales

- [Documentación de pycURL](http://pycurl.io/)
- [Guía de Peticiones HTTP](../../../docs/development/http_requests.md) 