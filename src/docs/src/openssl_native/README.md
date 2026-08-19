# OpenSSL Native Plugin

El plugin OpenSSL Native proporciona acceso directo a las bibliotecas OpenSSL a través de bindings nativos de Python para operaciones criptográficas de alto rendimiento.

## Características

- **Bindings nativos**: Acceso directo a librerías OpenSSL
- **Alto rendimiento**: Operaciones criptográficas optimizadas
- **Cifrado/Descifrado**: Algoritmos simétricos y asimétricos
- **Gestión de claves**: Claves RSA, DSA, ECDSA, Ed25519
- **Certificados SSL/TLS**: Crear y gestionar certificados
- **Funciones hash**: MD5, SHA1, SHA256, SHA512
- **Firmas digitales**: Firmar y verificar documentos

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `cryptography>=3.4.0`
- `pyopenssl>=20.0.0`
- `cffi>=1.14.0`

## Uso

### 1. Generar Clave RSA

```json
{
  "openssl_native": {
    "operation": "generate_key",
    "type": "rsa",
    "bits": 2048,
    "output": "/path/to/private_key.pem",
    "result": "key_status"
  }
}
```

### 2. Cifrar Datos

```json
{
  "openssl_native": {
    "operation": "encrypt",
    "algorithm": "aes-256-gcm",
    "data": "{{ sensitive_data }}",
    "key": "{{ encryption_key }}",
    "result": "encrypted_data"
  }
}
```

### 3. Descifrar Datos

```json
{
  "openssl_native": {
    "operation": "decrypt",
    "algorithm": "aes-256-gcm",
    "data": "{{ encrypted_data }}",
    "key": "{{ encryption_key }}",
    "result": "decrypted_data"
  }
}
```

### 4. Generar Hash

```json
{
  "openssl_native": {
    "operation": "hash",
    "algorithm": "sha256",
    "data": "{{ data_to_hash }}",
    "result": "hash_value"
  }
}
```

### 5. Firmar Datos

```json
{
  "openssl_native": {
    "operation": "sign",
    "algorithm": "sha256",
    "data": "{{ data_to_sign }}",
    "private_key": "/path/to/private_key.pem",
    "result": "signature"
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
  - `sign`: Firmar datos
  - `verify`: Verificar firma
  - `create_certificate`: Crear certificado

### Configuración de Claves
- `type` (string, opcional): Tipo de clave (rsa, dsa, ecdsa, ed25519)
- `bits` (integer, opcional): Tamaño de clave en bits
- `curve` (string, opcional): Curva para ECDSA

### Algoritmos de Cifrado
- `algorithm` (string, opcional): Algoritmo de cifrado
  - `aes-128-cbc`, `aes-256-cbc`
  - `aes-128-gcm`, `aes-256-gcm`
  - `chacha20-poly1305`
  - `rsa`, `rsa-oaep`

### Algoritmos de Hash
- `hash_algorithm` (string, opcional): Algoritmo de hash
  - `md5`, `sha1`, `sha256`, `sha512`
  - `sha3-256`, `sha3-512`
  - `blake2b`, `blake2s`

### Datos
- `data` (string/bytes, opcional): Datos a procesar
- `key` (string/bytes, opcional): Clave de cifrado
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
- **X25519**: Claves X25519 para intercambio

### Cifrado Simétrico
- **AES**: AES-128, AES-256 en modo CBC/GCM/CTR
- **ChaCha20**: ChaCha20-Poly1305
- **Camellia**: Algoritmo Camellia
- **SM4**: Algoritmo SM4 (China)

### Cifrado Asimétrico
- **RSA**: Cifrado con clave pública RSA
- **RSA-OAEP**: RSA con Optimal Asymmetric Encryption Padding
- **ECIES**: Cifrado de curva elíptica
- **Kyber**: Algoritmo post-cuántico

### Funciones Hash
- **SHA2**: SHA-256, SHA-384, SHA-512
- **SHA3**: SHA3-256, SHA3-512
- **BLAKE2**: BLAKE2b, BLAKE2s
- **SM3**: Hash SM3 (China)

## Ejemplos Avanzados

### Generar Par de Claves ECDSA

```json
{
  "openssl_native": {
    "operation": "generate_key",
    "type": "ecdsa",
    "curve": "secp256r1",
    "private_key": "/path/to/ecdsa_private.pem",
    "public_key": "/path/to/ecdsa_public.pem",
    "result": "ecdsa_keys"
  }
}
```

### Cifrado Híbrido (RSA + AES)

```json
{
  "openssl_native": {
    "operation": "hybrid_encrypt",
    "data": "{{ sensitive_data }}",
    "public_key": "/path/to/rsa_public.pem",
    "symmetric_algorithm": "aes-256-gcm",
    "result": "hybrid_encrypted"
  }
}
```

### Firma con Ed25519

```json
{
  "openssl_native": {
    "operation": "sign",
    "algorithm": "ed25519",
    "data": "{{ data_to_sign }}",
    "private_key": "/path/to/ed25519_private.pem",
    "result": "ed25519_signature"
  }
}
```

### Verificar Firma ECDSA

```json
{
  "openssl_native": {
    "operation": "verify",
    "algorithm": "ecdsa",
    "data": "{{ original_data }}",
    "signature": "{{ signature }}",
    "public_key": "/path/to/ecdsa_public.pem",
    "result": "verification_result"
  }
}
```

### Generar Certificado con Extensions

```json
{
  "openssl_native": {
    "operation": "create_certificate",
    "type": "server",
    "subject": {
      "CN": "*.example.com",
      "O": "Example Organization",
      "C": "US"
    },
    "extensions": {
      "subjectAltName": [
        "DNS:example.com",
        "DNS:www.example.com",
        "IP:192.168.1.1"
      ],
      "keyUsage": ["digitalSignature", "keyEncipherment"],
      "extendedKeyUsage": ["serverAuth"]
    },
    "days": 365,
    "private_key": "/path/to/private_key.pem",
    "output": "/path/to/certificate.pem",
    "result": "server_certificate"
  }
}
```

### Cifrado con Clave Derivada

```json
{
  "openssl_native": {
    "operation": "derive_and_encrypt",
    "password": "{{ master_password }}",
    "salt": "{{ random_salt }}",
    "data": "{{ data_to_encrypt }}",
    "algorithm": "aes-256-gcm",
    "iterations": 100000,
    "result": "derived_encrypted"
  }
}
```

## Configuración de Rendimiento

### Optimización de Algoritmos
```json
{
  "openssl_native": {
    "operation": "encrypt",
    "algorithm": "aes-256-gcm",
    "data": "{{ data }}",
    "key": "{{ key }}",
    "optimization": {
      "use_hardware": true,
      "parallel_processing": true,
      "buffer_size": 8192
    },
    "result": "optimized_encryption"
  }
}
```

### Configuración de Memoria
```json
{
  "openssl_native": {
    "operation": "hash",
    "algorithm": "sha256",
    "data": "{{ large_data }}",
    "memory_config": {
      "chunk_size": 65536,
      "max_memory": "1GB",
      "use_mmap": true
    },
    "result": "large_file_hash"
  }
}
```

## Configuración de Seguridad

### Mejores Prácticas
- Usar claves de al menos 2048 bits para RSA
- Usar AES-256-GCM para cifrado simétrico
- Usar SHA-256 o superior para hashes
- Implementar rotación de claves
- Validar todas las entradas

### Configuración Segura
```json
{
  "openssl_native": {
    "operation": "encrypt",
    "algorithm": "aes-256-gcm",
    "data": "{{ data }}",
    "key": "{{ strong_key }}",
    "security_config": {
      "validate_input": true,
      "secure_random": true,
      "constant_time": true,
      "clear_memory": true
    },
    "result": "secure_encryption"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Clave inválida**: Clave corrupta o formato incorrecto
- **Algoritmo no soportado**: Algoritmo no disponible
- **Datos corruptos**: Datos de entrada inválidos
- **Error de memoria**: Problemas de memoria
- **Error de hardware**: Problemas con aceleración hardware

## Optimización

### Hardware Acceleration
- Usar AES-NI cuando esté disponible
- Usar aceleración de curvas elípticas
- Optimizar para procesadores específicos
- Usar SIMD cuando sea posible

### Gestión de Memoria
- Implementar limpieza segura de memoria
- Usar buffers optimizados
- Minimizar copias de memoria
- Implementar pool de memoria

## Recursos Adicionales

- [Documentación de cryptography](https://cryptography.io/)
- [Documentación de pyOpenSSL](https://pyopenssl.org/)
- [Guía de Criptografía](../../../docs/security/ADVANCED_SECURITY_DIAGNOSTICS.md)
