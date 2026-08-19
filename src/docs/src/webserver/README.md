# WebServer Plugin

El plugin WebServer proporciona funcionalidades para crear y gestionar servidores web integrados en Sugar.

## Características

- **Servidor HTTP**: Crear servidores web básicos
- **Servidor HTTPS**: Servidores web seguros con SSL/TLS
- **Rutas personalizadas**: Definir endpoints y handlers
- **Middleware**: Interceptar y procesar requests
- **Archivos estáticos**: Servir archivos estáticos
- **API REST**: Crear APIs RESTful
- **WebSockets**: Soporte para conexiones WebSocket

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `flask>=2.0.0`
- `werkzeug>=2.0.0`

## Uso

### 1. Servidor HTTP Básico

```json
{
  "webserver": {
    "host": "0.0.0.0",
    "port": 8080,
    "routes": [
      {
        "path": "/",
        "method": "GET",
        "handler": "index_handler"
      }
    ],
    "start": true,
    "result": "server_status"
  }
}
```

### 2. Servidor con Múltiples Rutas

```json
{
  "webserver": {
    "host": "localhost",
    "port": 5000,
    "routes": [
      {
        "path": "/api/users",
        "method": "GET",
        "handler": "get_users"
      },
      {
        "path": "/api/users",
        "method": "POST",
        "handler": "create_user"
      },
      {
        "path": "/static/<path:filename>",
        "method": "GET",
        "handler": "serve_static"
      }
    ],
    "static_folder": "/var/www/static",
    "start": true,
    "result": "api_server"
  }
}
```

### 3. Servidor HTTPS

```json
{
  "webserver": {
    "host": "0.0.0.0",
    "port": 443,
    "ssl": {
      "cert_file": "/path/to/cert.pem",
      "key_file": "/path/to/key.pem"
    },
    "routes": [
      {
        "path": "/secure",
        "method": "GET",
        "handler": "secure_handler"
      }
    ],
    "start": true,
    "result": "https_server"
  }
}
```

## Parámetros

### Configuración del Servidor
- `host` (string, opcional): Host del servidor (default: "127.0.0.1")
- `port` (integer, opcional): Puerto del servidor (default: 5000)
- `debug` (boolean, opcional): Modo debug (default: false)
- `threaded` (boolean, opcional): Servidor multi-threaded (default: true)

### SSL/TLS
- `ssl` (object, opcional): Configuración SSL
  - `cert_file` (string): Ruta al certificado SSL
  - `key_file` (string): Ruta a la clave privada

### Rutas
- `routes` (array, opcional): Lista de rutas del servidor
  - `path` (string): Ruta del endpoint
  - `method` (string): Método HTTP (GET, POST, PUT, DELETE)
  - `handler` (string): Nombre del handler

### Archivos Estáticos
- `static_folder` (string, opcional): Carpeta para archivos estáticos
- `static_url_path` (string, opcional): URL path para archivos estáticos

### Control
- `start` (boolean, opcional): Iniciar el servidor automáticamente
- `stop` (boolean, opcional): Detener el servidor
- `result` (string, opcional): Variable para almacenar el estado

## Handlers Disponibles

### Handlers Básicos
- `index_handler`: Página principal
- `health_check`: Verificación de salud del servidor
- `serve_static`: Servir archivos estáticos

### Handlers de API
- `get_users`: Obtener lista de usuarios
- `create_user`: Crear nuevo usuario
- `update_user`: Actualizar usuario
- `delete_user`: Eliminar usuario

### Handlers Personalizados
Los handlers pueden ser funciones personalizadas definidas en el contexto de Sugar.

## Ejemplos de Handlers

### Handler Básico

```json
{
  "function": {
    "name": "index_handler",
    "code": [
      {"return": {"html": "<h1>Bienvenido a Sugar WebServer</h1>"}}
    ]
  }
}
```

### Handler de API

```json
{
  "function": {
    "name": "get_users",
    "code": [
      {"return": {"json": {"users": ["user1", "user2", "user3"]}}}
    ]
  }
}
```

### Handler con Parámetros

```json
{
  "function": {
    "name": "user_detail",
    "code": [
      {"var": {"user_id": "{{ request.args.user_id }}"}},
      {"return": {"json": {"id": "{{ user_id }}", "name": "Usuario {{ user_id }}"}}}
    ]
  }
}
```

## Middleware

### Logging Middleware

```json
{
  "webserver": {
    "middleware": [
      {
        "type": "logging",
        "enabled": true
      }
    ],
    "routes": [...],
    "start": true
  }
}
```

### CORS Middleware

```json
{
  "webserver": {
    "middleware": [
      {
        "type": "cors",
        "origins": ["http://localhost:3000", "https://example.com"]
      }
    ],
    "routes": [...],
    "start": true
  }
}
```

## WebSockets

### Configuración WebSocket

```json
{
  "webserver": {
    "websocket": {
      "enabled": true,
      "path": "/ws"
    },
    "routes": [...],
    "start": true
  }
}
```

### Handler WebSocket

```json
{
  "function": {
    "name": "websocket_handler",
    "code": [
      {"websocket": {"send": "Mensaje recibido: {{ message }}"}}
    ]
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Puerto en uso**: Puerto ya ocupado por otro proceso
- **Certificado SSL inválido**: Problemas con certificados SSL
- **Ruta no encontrada**: 404 para rutas no definidas
- **Método no permitido**: 405 para métodos HTTP no soportados

## Ejemplos Avanzados

### API REST Completa

```json
{
  "webserver": {
    "host": "0.0.0.0",
    "port": 8000,
    "routes": [
      {
        "path": "/api/v1/users",
        "method": "GET",
        "handler": "list_users"
      },
      {
        "path": "/api/v1/users/<int:user_id>",
        "method": "GET",
        "handler": "get_user"
      },
      {
        "path": "/api/v1/users",
        "method": "POST",
        "handler": "create_user"
      },
      {
        "path": "/api/v1/users/<int:user_id>",
        "method": "PUT",
        "handler": "update_user"
      },
      {
        "path": "/api/v1/users/<int:user_id>",
        "method": "DELETE",
        "handler": "delete_user"
      }
    ],
    "start": true,
    "result": "rest_api"
  }
}
```

### Servidor de Archivos Estáticos

```json
{
  "webserver": {
    "host": "0.0.0.0",
    "port": 8080,
    "static_folder": "/var/www/html",
    "static_url_path": "/static",
    "routes": [
      {
        "path": "/",
        "method": "GET",
        "handler": "serve_index"
      }
    ],
    "start": true,
    "result": "file_server"
  }
}
```

## Seguridad

- Usar HTTPS en producción
- Validar todas las entradas de usuario
- Implementar autenticación y autorización
- Configurar CORS apropiadamente
- Mantener dependencias actualizadas

## Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Guía de Seguridad Web](../../../docs/security/ADVANCED_SECURITY_DIAGNOSTICS.md)
