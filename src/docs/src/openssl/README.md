# OpenSSL Plugin

El plugin OpenSSL proporciona funcionalidades criptográficas avanzadas usando la biblioteca OpenSSL.

## Características

- **Cifrado/Descifrado**: Algoritmos de cifrado simétrico y asimétrico
- **Generación de claves**: Claves RSA, DSA, ECDSA
- **Certificados SSL/TLS**: Crear y gestionar certificados
- **Funciones hash**: MD5, SHA1, SHA256, SHA512
- **Firmas digitales**: Firmar y verificar documentos
- **Gestión de CA**: Autoridades certificadoras

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `cryptography>=3.4.0`
- `pyopenssl>=20.0.0`

## Uso

### 1. Generar Clave RSA

```json
{
  "openssl": {
    "operation": "generate_key",
    "type": "rsa",
    "bits": 2048,
    "output": "/path/to/private_key.pem",
    "result": "key_status"
  }
}
```

### 2. Cifrar Archivo

```json
{
  "openssl": {
    "operation": "encrypt",
    "algorithm": "aes-256-cbc",
    "input": "/path/to/plaintext.txt",
    "output": "/path/to/encrypted.bin",
    "key": "{{ secret_key }}",
    "result": "encrypt_status"
  }
}
```

### 3. Descifrar Archivo

```json
{
  "openssl": {
    "operation": "decrypt",
    "algorithm": "aes-256-cbc",
    "input": "/path/to/encrypted.bin",
    "output": "/path/to/decrypted.txt",
    "key": "{{ secret_key }}",
    "result": "decrypt_status"
  }
}
```

### 4. Generar Hash

```json
{
  "openssl": {
    "operation": "hash",
    "algorithm": "sha256",
    "input": "/path/to/file.txt",
    "result": "file_hash"
  }
}
```

### 5. Crear Certificado SSL

```json
{
  "openssl": {
    "operation": "create_certificate",
    "type": "self_signed",
    "subject": {
      "CN": "example.com",
      "O": "Example Organization",
      "C": "US"
    },
    "days": 365,
    "private_key": "/path/to/private_key.pem",
    "output": "/path/to/certificate.pem",
    "result": "cert_status"
  }
}
```

## Parámetros

### Operaciones
- `operation` (string, requerido): Tipo de operación
  - `generate_key`: Generar clave
  - `encrypt`: Cifrar datos
  - `decrypt`: Descifrar datos
  - `hash`: Generar hash
  - `sign`: Firmar documento
  - `verify`: Verificar firma
  - `create_certificate`: Crear certificado

### Configuración de Claves
- `type` (string, opcional): Tipo de clave (rsa, dsa, ecdsa)
- `bits` (integer, opcional): Tamaño de clave en bits
- `curve` (string, opcional): Curva para ECDSA

### Algoritmos de Cifrado
- `algorithm` (string, opcional): Algoritmo de cifrado
  - `aes-128-cbc`, `aes-256-cbc`
  - `aes-128-gcm`, `aes-256-gcm`
  - `des-ede3-cbc`
  - `bf-cbc`

### Algoritmos de Hash
- `hash_algorithm` (string, opcional): Algoritmo de hash
  - `md5`, `sha1`, `sha256`, `sha512`
  - `sha3-256`, `sha3-512`

### Rutas
- `input` (string, opcional): Archivo de entrada
- `output` (string, opcional): Archivo de salida
- `private_key` (string, opcional): Ruta a clave privada
- `public_key` (string, opcional): Ruta a clave pública

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Operaciones Disponibles

### Generación de Claves
- **RSA**: Claves RSA de 1024, 2048, 4096 bits
- **DSA**: Claves DSA de 1024, 2048 bits
- **ECDSA**: Claves ECDSA con curvas estándar
- **Ed25519**: Claves Ed25519 para firma

### Cifrado Simétrico
- **AES**: AES-128, AES-256 en modo CBC/GCM
- **DES**: DES-EDE3 (Triple DES)
- **Blowfish**: Algoritmo Blowfish
- **Camellia**: Algoritmo Camellia

### Cifrado Asimétrico
- **RSA**: Cifrado con clave pública RSA
- **ElGamal**: Cifrado ElGamal
- **ECIES**: Cifrado de curva elíptica

### Funciones Hash
- **MD5**: Hash MD5 (no recomendado para seguridad)
- **SHA1**: Hash SHA-1
- **SHA2**: SHA-256, SHA-384, SHA-512
- **SHA3**: SHA3-256, SHA3-512

## Ejemplos Avanzados

### Generar Par de Claves RSA

```json
{
  "openssl": {
    "operation": "generate_key",
    "type": "rsa",
    "bits": 4096,
    "private_key": "/path/to/private_key.pem",
    "public_key": "/path/to/public_key.pem",
    "passphrase": "{{ key_passphrase }}",
    "result": "rsa_keys"
  }
}
```

### Cifrar con Clave Pública

```json
{
  "openssl": {
    "operation": "encrypt",
    "algorithm": "rsa",
    "input": "/path/to/secret.txt",
    "output": "/path/to/encrypted.bin",
    "public_key": "/path/to/public_key.pem",
    "padding": "oaep",
    "result": "public_encrypt"
  }
}
```

### Firmar Documento

```json
{
  "openssl": {
    "operation": "sign",
    "algorithm": "sha256",
    "input": "/path/to/document.pdf",
    "output": "/path/to/signature.sig",
    "private_key": "/path/to/private_key.pem",
    "result": "signature"
  }
}
```

### Verificar Firma

```json
{
  "openssl": {
    "operation": "verify",
    "algorithm": "sha256",
    "input": "/path/to/document.pdf",
    "signature": "/path/to/signature.sig",
    "public_key": "/path/to/public_key.pem",
    "result": "verification"
  }
}
```

### Crear Certificado CA

```json
{
  "openssl": {
    "operation": "create_certificate",
    "type": "ca",
    "subject": {
      "CN": "My Root CA",
      "O": "My Organization",
      "C": "US",
      "ST": "California",
      "L": "San Francisco"
    },
    "days": 3650,
    "private_key": "/path/to/ca_key.pem",
    "output": "/path/to/ca_cert.pem",
    "result": "ca_certificate"
  }
}
```

### Generar Certificado de Servidor

```json
{
  "openssl": {
    "operation": "create_certificate",
    "type": "server",
    "subject": {
      "CN": "*.example.com",
      "O": "Example Organization",
      "C": "US"
    },
    "san": [
      "DNS:example.com",
      "DNS:www.example.com",
      "IP:192.168.1.1"
    ],
    "days": 365,
    "ca_cert": "/path/to/ca_cert.pem",
    "ca_key": "/path/to/ca_key.pem",
    "private_key": "/path/to/server_key.pem",
    "output": "/path/to/server_cert.pem",
    "result": "server_certificate"
  }
}
```

## Configuración de Seguridad

### Mejores Prácticas
- Usar claves de al menos 2048 bits para RSA
- Usar AES-256 para cifrado simétrico
- Usar SHA-256 o superior para hashes
- Rotar claves regularmente
- Proteger claves privadas con contraseñas

### Configuración Segura
```json
{
  "openssl": {
    "operation": "encrypt",
    "algorithm": "aes-256-gcm",
    "input": "/path/to/data.txt",
    "output": "/path/to/encrypted.bin",
    "key": "{{ strong_key }}",
    "iv": "{{ random_iv }}",
    "tag": "{{ auth_tag }}",
    "result": "secure_encrypt"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Clave inválida**: Clave corrupta o formato incorrecto
- **Algoritmo no soportado**: Algoritmo no disponible
- **Archivo no encontrado**: Archivo de entrada inexistente
- **Permisos insuficientes**: Falta de permisos de lectura/escritura
- **Error de cifrado**: Error durante el proceso de cifrado

## Optimización

### Rendimiento
- Usar AES-GCM para cifrado autenticado
- Usar ECDSA para firmas rápidas
- Usar hardware acceleration cuando esté disponible

### Almacenamiento
- Comprimir claves grandes
- Usar formatos eficientes (DER vs PEM)
- Implementar caché de claves frecuentes

## Recursos Adicionales

- [Documentación de OpenSSL](https://www.openssl.org/docs/)
- [Guía de Criptografía](../../../docs/security/ADVANCED_SECURITY_DIAGNOSTICS.md)
