# Curl (Comando Avanzado)

Este comando permite realizar solicitudes HTTP avanzadas con configuración granular similar a la herramienta curl de línea de comandos. Es ideal para interacciones complejas con APIs que requieren configuración específica de SSL, proxies, autenticación, cookies y otros parámetros avanzados.

## Palabra Reservada
`curl`

## Parámetros
* url (string, requerido): URL de destino para la solicitud HTTP.
* method (string, opcional): Método HTTP (GET, POST, PUT, DELETE, etc.). Por defecto es GET.
* headers (array, opcional): Array de strings con headers en formato "Key: Value".
* body (string, opcional): Cuerpo de la solicitud HTTP.
* timeout (integer, opcional): Timeout en segundos para la respuesta completa.
* connect_timeout (integer, opcional): Timeout en segundos para la conexión inicial.
* follow_location (boolean, opcional): Si seguir redirecciones automáticamente.
* max_redirs (integer, opcional): Número máximo de redirecciones a seguir.
* useragent (string, opcional): User-Agent personalizado.
* cookiefile (string, opcional): Ruta al archivo de cookies para enviar.
* cookiejar (string, opcional): Ruta al archivo de cookies para guardar.
* httpauth (string, opcional): Tipo de autenticación HTTP ("basic").
* username (string, opcional): Usuario para autenticación básica.
* password (string, opcional): Contraseña para autenticación básica.
* proxy (string, opcional): URL del proxy a utilizar.
* proxyuserpwd (string, opcional): Credenciales del proxy en formato "user:pass".
* sslcert (string, opcional): Ruta al certificado SSL del cliente.
* sslkey (string, opcional): Ruta a la clave privada SSL del cliente.
* cainfo (string, opcional): Ruta al archivo de certificados CA.
* verbose (boolean, opcional): Modo verbose para logging detallado.
* insecure (boolean, opcional): Deshabilitar verificación SSL.
* http_version (string, opcional): Versión de HTTP a utilizar.
* accept_encoding (string, opcional): Codificación de aceptación.
* custom_options (object, opcional): Opciones personalizadas de curl.
* result (string, requerido): Nombre de la variable donde se almacenará el resultado.

## Estructura del Resultado
El resultado se almacena en la variable especificada con la siguiente estructura:
* headers (array): Array de objetos con keys "key" y "value" para cada header.
* status_code (integer): Código de estado HTTP de la respuesta.
* cookies (array): Array de objetos con información de cookies (name, value, domain, path, expires, secure, httpOnly).
* type (string): Tipo MIME del contenido de la respuesta.
* content (string): Contenido de la respuesta.

## Excepciones
Si la solicitud falla, se lanza una `CurlException` con detalles del error.

## Ejemplos de Uso

### Solicitud básica GET:
```json
{
  "curl": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "result": "response"
  }
}
```

### Solicitud POST con headers y body:
```json
{
  "curl": {
    "url": "https://api.example.com/submit",
    "method": "POST",
    "headers": [
      "Content-Type: application/json",
      "Authorization: Bearer YOUR_TOKEN"
    ],
    "body": "{\"key1\": \"value1\", \"key2\": \"value2\"}",
    "result": "api_response"
  }
}
```

### Solicitud con autenticación básica:
```json
{
  "curl": {
    "url": "https://api.example.com/secure",
    "method": "GET",
    "httpauth": "basic",
    "username": "user",
    "password": "pass",
    "result": "secure_response"
  }
}
```

### Solicitud con proxy y configuración SSL:
```json
{
  "curl": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "proxy": "http://proxy.example.com:8080",
    "proxyuserpwd": "proxyuser:proxypass",
    "insecure": false,
    "timeout": 30,
    "result": "proxied_response"
  }
}
```

### Solicitud con cookies y configuración avanzada:
```json
{
  "curl": {
    "url": "https://api.example.com/session",
    "method": "POST",
    "cookiefile": "/tmp/cookies.txt",
    "cookiejar": "/tmp/cookies.txt",
    "useragent": "MyCustomClient/1.0",
    "follow_location": true,
    "max_redirs": 5,
    "result": "session_response"
  }
}
```