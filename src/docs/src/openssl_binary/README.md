# OpenSSL Binary Plugin

El plugin OpenSSL Binary proporciona acceso directo a las herramientas de línea de comandos de OpenSSL para operaciones criptográficas avanzadas.

## Características

- **Acceso directo a OpenSSL**: Usar comandos OpenSSL nativos
- **Operaciones criptográficas**: Cifrado, descifrado, hashing, firmas
- **Gestión de certificados**: Crear y gestionar certificados SSL/TLS
- **Generación de claves**: Claves RSA, DSA, ECDSA, Ed25519
- **Análisis de certificados**: Verificar y analizar certificados
- **Operaciones de CA**: Gestión de autoridades certificadoras

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `subprocess` (incluido en Python estándar)
- `pathlib` (incluido en Python estándar)
- OpenSSL instalado en el sistema

## Uso

### 1. Generar Clave Privada RSA

```json
{
  "openssl_binary": {
    "command": "genrsa",
    "args": [
      "-out", "/path/to/private_key.pem",
      "-2048"
    ],
    "result": "key_generation"
  }
}
```

### 2. Crear Certificado Autofirmado

```json
{
  "openssl_binary": {
    "command": "req",
    "args": [
      "-new",
      "-x509",
      "-key", "/path/to/private_key.pem",
      "-out", "/path/to/certificate.pem",
      "-days", "365",
      "-subj", "/C=US/ST=CA/L=SF/O=Example/CN=example.com"
    ],
    "result": "certificate_creation"
  }
}
```

### 3. Cifrar Archivo

```json
{
  "openssl_binary": {
    "command": "enc",
    "args": [
      "-aes-256-cbc",
      "-salt",
      "-in", "/path/to/plaintext.txt",
      "-out", "/path/to/encrypted.bin",
      "-pass", "pass:{{ password }}"
    ],
    "result": "encryption"
  }
}
```

### 4. Descifrar Archivo

```json
{
  "openssl_binary": {
    "command": "enc",
    "args": [
      "-aes-256-cbc",
      "-d",
      "-in", "/path/to/encrypted.bin",
      "-out", "/path/to/decrypted.txt",
      "-pass", "pass:{{ password }}"
    ],
    "result": "decryption"
  }
}
```

### 5. Generar Hash SHA256

```json
{
  "openssl_binary": {
    "command": "dgst",
    "args": [
      "-sha256",
      "-out", "/path/to/hash.txt",
      "/path/to/file.txt"
    ],
    "result": "hash_generation"
  }
}
```

## Parámetros

### Configuración Básica
- `command` (string, requerido): Comando OpenSSL
- `args` (array, opcional): Argumentos del comando
- `input` (string, opcional): Entrada estándar
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración Avanzada
- `env` (object, opcional): Variables de entorno
- `cwd` (string, opcional): Directorio de trabajo
- `timeout` (integer, opcional): Timeout en segundos
- `capture_output` (boolean, opcional): Capturar salida (default: true)

### Opciones de Seguridad
- `passphrase` (string, opcional): Contraseña para claves
- `verify_ssl` (boolean, opcional): Verificar SSL (default: true)
- `strict_mode` (boolean, opcional): Modo estricto (default: false)

## Comandos Disponibles

### Generación de Claves
- **genrsa**: Generar clave privada RSA
- **genpkey**: Generar claves privadas (RSA, DSA, EC)
- **gendsa**: Generar clave privada DSA
- **genec**: Generar clave privada de curva elíptica

### Gestión de Certificados
- **req**: Crear solicitudes de certificado y certificados
- **x509**: Gestionar certificados X.509
- **ca**: Operaciones de autoridad certificadora
- **verify**: Verificar certificados

### Cifrado y Descifrado
- **enc**: Cifrado simétrico
- **rsautl**: Cifrado asimétrico RSA
- **pkeyutl**: Operaciones de clave pública
- **dgst**: Funciones hash y firmas

### Análisis y Conversión
- **asn1parse**: Analizar archivos ASN.1
- **pkcs7**: Operaciones PKCS#7
- **pkcs12**: Operaciones PKCS#12
- **crl**: Listas de revocación de certificados

## Ejemplos Avanzados

### Crear CA Completa

```json
{
  "openssl_binary": {
    "command": "req",
    "args": [
      "-new",
      "-x509",
      "-days", "3650",
      "-keyout", "/path/to/ca_key.pem",
      "-out", "/path/to/ca_cert.pem",
      "-subj", "/C=US/ST=CA/L=SF/O=MyCA/CN=My Root CA",
      "-extensions", "v3_ca"
    ],
    "result": "ca_creation"
  }
}
```

### Generar Solicitud de Certificado

```json
{
  "openssl_binary": {
    "command": "req",
    "args": [
      "-new",
      "-key", "/path/to/server_key.pem",
      "-out", "/path/to/server.csr",
      "-subj", "/C=US/ST=CA/L=SF/O=Example/CN=server.example.com",
      "-config", "/path/to/openssl.cnf"
    ],
    "result": "csr_generation"
  }
}
```

### Firmar Certificado con CA

```json
{
  "openssl_binary": {
    "command": "ca",
    "args": [
      "-in", "/path/to/server.csr",
      "-out", "/path/to/server_cert.pem",
      "-cert", "/path/to/ca_cert.pem",
      "-keyfile", "/path/to/ca_key.pem",
      "-days", "365",
      "-extensions", "server_cert"
    ],
    "result": "certificate_signing"
  }
}
```

### Convertir Formato de Certificado

```json
{
  "openssl_binary": {
    "command": "x509",
    "args": [
      "-in", "/path/to/certificate.pem",
      "-out", "/path/to/certificate.der",
      "-outform", "DER"
    ],
    "result": "format_conversion"
  }
}
```

### Verificar Cadena de Certificados

```json
{
  "openssl_binary": {
    "command": "verify",
    "args": [
      "-CAfile", "/path/to/ca_cert.pem",
      "-untrusted", "/path/to/intermediate.pem",
      "/path/to/server_cert.pem"
    ],
    "result": "certificate_verification"
  }
}
```

### Generar Clave Ed25519

```json
{
  "openssl_binary": {
    "command": "genpkey",
    "args": [
      "-algorithm", "ED25519",
      "-out", "/path/to/ed25519_key.pem"
    ],
    "result": "ed25519_generation"
  }
}
```

## Configuración de OpenSSL

### Archivo de Configuración
```json
{
  "openssl_binary": {
    "command": "req",
    "args": [
      "-new",
      "-config", "/path/to/openssl.cnf",
      "-key", "/path/to/key.pem",
      "-out", "/path/to/cert.pem"
    ],
    "env": {
      "OPENSSL_CONF": "/path/to/openssl.cnf"
    },
    "result": "configured_request"
  }
}
```

### Variables de Entorno
- `OPENSSL_CONF`: Archivo de configuración
- `OPENSSL_ENGINES`: Directorio de engines
- `OPENSSL_MODULES`: Directorio de módulos
- `OPENSSL_TRACE`: Habilitar trazas

## Diagnóstico y Troubleshooting

### Verificar Instalación
```json
{
  "openssl_binary": {
    "command": "version",
    "args": ["-a"],
    "result": "openssl_version"
  }
}
```

### Listar Algoritmos Disponibles
```json
{
  "openssl_binary": {
    "command": "list",
    "args": ["-cipher-algorithms"],
    "result": "available_ciphers"
  }
}
```

### Analizar Certificado
```json
{
  "openssl_binary": {
    "command": "x509",
    "args": [
      "-in", "/path/to/certificate.pem",
      "-text",
      "-noout"
    ],
    "result": "certificate_analysis"
  }
}
```

## Configuración de Seguridad

### Mejores Prácticas
- Usar claves de al menos 2048 bits para RSA
- Usar algoritmos modernos (AES-256, SHA-256)
- Proteger claves privadas con contraseñas
- Verificar certificados antes de usar
- Rotar claves regularmente

### Configuración Segura
```json
{
  "openssl_binary": {
    "command": "genrsa",
    "args": [
      "-out", "/path/to/secure_key.pem",
      "-4096",
      "-aes256"
    ],
    "passphrase": "{{ strong_passphrase }}",
    "result": "secure_key"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **OpenSSL no encontrado**: OpenSSL no instalado
- **Comando inválido**: Comando OpenSSL no válido
- **Archivo no encontrado**: Archivo de entrada inexistente
- **Error de contraseña**: Contraseña incorrecta
- **Error de formato**: Formato de archivo incorrecto

## Optimización

### Rendimiento
- Usar algoritmos eficientes
- Optimizar tamaños de clave
- Usar hardware acceleration cuando esté disponible
- Cachear operaciones frecuentes

### Almacenamiento
- Usar formatos eficientes (DER vs PEM)
- Comprimir claves grandes
- Implementar gestión de claves

## Recursos Adicionales

- [Documentación de OpenSSL](https://www.openssl.org/docs/)
- [Guía de Criptografía](../../../docs/security/ADVANCED_SECURITY_DIAGNOSTICS.md)
