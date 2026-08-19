# JWT Plugin for Sugar

A comprehensive JWT plugin that provides JWT operations including encoding, decoding, and verification of JSON Web Tokens.

## Features

- **JWT Encoding**: Create JWT tokens with custom payloads and algorithms
- **JWT Decoding**: Decode JWT tokens with or without signature verification
- **JWT Verification**: Verify JWT token validity and signature
- **Template Variable Support**: Interpolate variables in payloads and configuration
- **Multiple Algorithms**: Support for HS256, RS256, and other JWT algorithms
- **Context Integration**: Seamless integration with Sugar's context system

## Installation

The plugin requires the following dependencies:
- PyJWT >= 2.8.0
- cryptography >= 3.4.0

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. JWT Encoding

Encode a JWT token with custom payload:

```json
{
  "jwt": {
    "operator": "encode",
    "payload": {
      "sub": "1234567890",
      "name": "{{ nombre|default('Usuario Anónimo') }}",
      "iat": "{{ timestamp }}",
      "exp": "{{ timestamp + 3600 }}"
    },
    "key": "{{ secret_key }}",
    "algorithm": "HS256",
    "result": "encoded_jwt"
  }
}
```

### 2. JWT Decoding with Verification

Decode and verify a JWT token:

```json
{
  "jwt": {
    "operator": "decode",
    "token": "{{ encoded_jwt }}",
    "key": "{{ secret_key }}",
    "algorithms": ["HS256"],
    "verify": true,
    "result": "decoded_payload"
  }
}
```

### 3. JWT Verification

Verify a JWT token validity:

```json
{
  "jwt": {
    "operator": "verify",
    "token": "{{ token_input }}",
    "key": "{{ public_key }}",
    "algorithms": ["RS256"],
    "result": "is_valid"
  }
}
```

### 4. JWT Decoding without Verification

Decode a JWT token without signature verification:

```json
{
  "jwt": {
    "operator": "decode",
    "token": "{{ token_input }}",
    "options": {
      "verify_signature": false
    },
    "result": "payload_unverified"
  }
}
```

## Template Variables

The plugin supports template variable interpolation in payloads and configuration:

### Special Variables

- `{{ timestamp }}`: Current Unix timestamp
- `{{ timestamp + 3600 }}`: Current timestamp + 1 hour (3600 seconds)

### Default Values

Use the `|default()` syntax to provide fallback values:
- `{{ nombre|default('Usuario Anónimo') }}`: Uses the value of `nombre` if available, otherwise uses 'Usuario Anónimo'

### Context Variables

Access variables from the Sugar context:
- `{{ secret_key }}`: Gets the value of `secret_key` from context
- `{{ user.name }}`: Gets nested variable `user.name` from context

## Configuration Options

### Encode Operation

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `payload` | dict | Yes | JWT payload data |
| `key` | str | Yes | Secret key for signing |
| `algorithm` | str | No | Algorithm to use (default: HS256) |
| `result` | str | No | Variable name to store result |

### Decode Operation

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | str | Yes | JWT token to decode |
| `key` | str | No* | Key for verification (*required if verify=true) |
| `algorithms` | list | No | Allowed algorithms (default: ["HS256"]) |
| `verify` | bool | No | Whether to verify signature (default: true) |
| `options` | dict | No | Additional decode options |
| `result` | str | No | Variable name to store result |

### Verify Operation

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | str | Yes | JWT token to verify |
| `key` | str | Yes | Key for verification |
| `algorithms` | list | No | Allowed algorithms (default: ["HS256"]) |
| `result` | str | No | Variable name to store result |

## Supported Algorithms

- **HS256**: HMAC with SHA-256
- **HS384**: HMAC with SHA-384
- **HS512**: HMAC with SHA-512
- **RS256**: RSA with SHA-256
- **RS384**: RSA with SHA-384
- **RS512**: RSA with SHA-512
- **ES256**: ECDSA with SHA-256
- **ES384**: ECDSA with SHA-384
- **ES512**: ECDSA with SHA-512

## Error Handling

The plugin provides comprehensive error handling:

- **Invalid Token**: Returns appropriate error messages for malformed tokens
- **Expired Token**: Handles token expiration gracefully
- **Invalid Signature**: Detects signature verification failures
- **Missing Parameters**: Validates required parameters

## Examples

See `example.py` for complete usage examples.

## License

MIT License - see LICENSE file for details.