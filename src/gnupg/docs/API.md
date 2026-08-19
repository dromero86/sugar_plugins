# GnuPG Plugin API Documentation

## Overview

The GnuPG plugin provides comprehensive cryptographic operations for Sugar Language, including key management, encryption/decryption, digital signatures, and utility functions.

## Plugin Class

### GnuPGPlugin

Main plugin class that orchestrates all GnuPG operations.

#### Properties

- `VERSION`: Plugin version (1.0.0)
- `DESCRIPTION`: Plugin description
- `AUTHOR`: Plugin author (Sugar Team)
- `LICENSE`: Plugin license (MIT)
- `SYSTEM_DEPENDENCIES`: List of system dependencies (["gpg"])
- `DEPENDENCIES`: List of Python dependencies (["python-gnupg"])
- `REQUIREMENTS`: List of Python requirements (["python-gnupg>=0.5.0"])

#### Methods

##### `__init__(context=None, plugin_config=None)`

Initialize the plugin and check dependencies.

**Parameters:**
- `context`: Sugar service context
- `plugin_config`: Plugin configuration dictionary

##### `get_available_commands() -> List[str]`

Get list of available commands.

**Returns:** List of command names

##### `execute(command: str, config: Dict[str, Any]) -> Any`

Execute a GnuPG command.

**Parameters:**
- `command`: Command name to execute
- `config`: Command configuration dictionary

**Returns:** Command result

## Components

### GnuPGKeyManager

Handles all key-related operations.

#### Methods

##### `execute(command: str, config: Dict[str, Any]) -> Any`

Execute key management command.

**Supported Commands:**
- `generate_key`: Generate new GnuPG key
- `list_keys`: List public/secret keys
- `import_key`: Import key from file
- `export_key`: Export key to file
- `delete_key`: Delete key
- `sign_key`: Sign public key
- `revoke_key`: Generate revocation certificate
- `trust_key`: Set trust level

### GnuPGEncryption

Handles encryption and decryption operations.

#### Methods

##### `execute(command: str, config: Dict[str, Any]) -> Any`

Execute encryption/decryption command.

**Supported Commands:**
- `encrypt_file`: Encrypt file asymmetrically
- `decrypt_file`: Decrypt file
- `encrypt_text`: Encrypt text asymmetrically
- `decrypt_text`: Decrypt text
- `symmetric_encrypt`: Encrypt file symmetrically
- `symmetric_decrypt`: Decrypt file symmetrically

### GnuPGSigning

Handles digital signature operations.

#### Methods

##### `execute(command: str, config: Dict[str, Any]) -> Any`

Execute signing/verification command.

**Supported Commands:**
- `sign_file`: Sign file (binary)
- `verify_signature`: Verify signature
- `clearsign`: Create clearsigned file
- `detached_sign`: Create detached signature
- `sign_text`: Sign text content
- `verify_text`: Verify text signature

### GnuPGUtils

Handles utility operations.

#### Methods

##### `execute(command: str, config: Dict[str, Any]) -> Any`

Execute utility command.

**Supported Commands:**
- `check_dependencies`: Check system dependencies
- `system_info`: Get GnuPG system information
- `test_functionality`: Test GnuPG functionality
- `configure_agent`: Configure GnuPG agent
- `check_agent_status`: Check agent status

## Command Reference

### Key Management Commands

#### generate_key

Generate a new GnuPG key.

**Parameters:**
- `key_type`: Key type (RSA, DSA, ECDSA, EDDSA)
- `key_length`: Key length in bits
- `name_real`: Real name
- `name_email`: Email address
- `name_comment`: Comment
- `expire_date`: Expiration date
- `passphrase`: Key passphrase

**Returns:**
```json
{
  "success": true,
  "fingerprint": "key_fingerprint",
  "key_type": "RSA",
  "key_length": 2048,
  "name_real": "Juan Pérez",
  "name_email": "juan.perez@ejemplo.com"
}
```

#### list_keys

List GnuPG keys.

**Parameters:**
- `show_secret`: Show secret keys (default: false)
- `fingerprint`: Show fingerprints (default: true)

**Returns:**
```json
{
  "success": true,
  "keys": [
    {
      "type": "public",
      "key_id": "key_id",
      "fingerprint": "fingerprint",
      "uids": ["user_ids"]
    }
  ],
  "count": 1
}
```

### Encryption Commands

#### encrypt_text

Encrypt text using asymmetric encryption.

**Parameters:**
- `text`: Text to encrypt
- `recipient`: Recipient email or key ID
- `armor`: Use ASCII armor (default: true)
- `compress`: Enable compression (default: true)

**Returns:**
```json
{
  "success": true,
  "encrypted_text": "encrypted_content",
  "recipient": "recipient_id"
}
```

#### decrypt_text

Decrypt text.

**Parameters:**
- `encrypted_text`: Encrypted text content
- `passphrase`: Private key passphrase

**Returns:**
```json
{
  "success": true,
  "decrypted_text": "original_text"
}
```

### Signing Commands

#### detached_sign

Create a detached signature.

**Parameters:**
- `input_file`: File to sign
- `signature_file`: Output signature file
- `key_id`: Signing key ID
- `passphrase`: Private key passphrase
- `armor`: Use ASCII armor (default: true)
- `hash_algorithm`: Hash algorithm (default: SHA256)

**Returns:**
```json
{
  "success": true,
  "input_file": "input_file",
  "signature_file": "signature_file",
  "key_id": "key_id",
  "hash_algorithm": "SHA256"
}
```

#### verify_signature

Verify a signature.

**Parameters:**
- `input_file`: Original file
- `signature_file`: Signature file (optional for clearsign)
- `key_file`: Public key file (optional)

**Returns:**
```json
{
  "success": true,
  "verified": true,
  "signer": "signer_name",
  "signature_date": "signature_date",
  "key_id": "key_id",
  "details": ["verification_details"]
}
```

### Utility Commands

#### check_dependencies

Check system and Python dependencies.

**Returns:**
```json
{
  "system_dependencies": {
    "satisfied": true,
    "gpg": {
      "available": true,
      "path": "/usr/bin/gpg",
      "version": "gpg (GnuPG) 2.4.4"
    }
  },
  "python_dependencies": {
    "satisfied": true,
    "python-gnupg": {
      "available": true,
      "version": "0.5.0"
    }
  },
  "all_satisfied": true
}
```

#### system_info

Get GnuPG system information.

**Returns:**
```json
{
  "gpg_path": "/usr/bin/gpg",
  "version": "gpg (GnuPG) 2.4.4",
  "home_directory": "/home/user/.gnupg",
  "supported_algorithms": {
    "pubkey": ["RSA", "ELG", "DSA", "ECDH", "ECDSA", "EDDSA"],
    "cipher": ["IDEA", "3DES", "CAST5", "BLOWFISH", "AES", "AES192", "AES256"],
    "hash": ["SHA1", "RIPEMD160", "SHA256", "SHA384", "SHA512"],
    "compression": ["Uncompressed", "ZIP", "ZLIB", "BZIP2"]
  }
}
```

## Error Handling

All commands return a consistent error format:

```json
{
  "success": false,
  "error": "Error description",
  "return_code": 1
}
```

## Examples

### Basic Usage

```json
{
  "gnupg": {
    "operator": "check_dependencies",
    "result": "dependency_status"
  }
}
```

### Key Generation

```json
{
  "gnupg": {
    "operator": "generate_key",
    "key_type": "RSA",
    "key_length": 2048,
    "name_real": "Juan Pérez",
    "name_email": "juan.perez@ejemplo.com",
    "expire_date": "2y",
    "passphrase": "MiPassphraseSegura123!",
    "result": "key_generation"
  }
}
```

### Text Encryption

```json
{
  "gnupg": {
    "operator": "encrypt_text",
    "text": "Mensaje secreto",
    "recipient": "juan.perez@ejemplo.com",
    "armor": true,
    "result": "encrypted_message"
  }
}
```

### Document Signing

```json
{
  "gnupg": {
    "operator": "detached_sign",
    "input_file": "documento.txt",
    "signature_file": "documento.txt.sig",
    "key_id": "juan.perez@ejemplo.com",
    "passphrase": "MiPassphraseSegura123!",
    "armor": true,
    "hash_algorithm": "SHA256",
    "result": "signature_result"
  }
}
```

## Installation

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install gnupg

# CentOS/RHEL
sudo yum install gnupg

# macOS
brew install gnupg

# Windows
# Download from https://gnupg.org/download/
```

### Python Dependencies

```bash
pip install python-gnupg>=0.5.0
```

## Testing

Run the test suite:

```bash
python3 test_plugin.py
```

## License

MIT License - see LICENSE file for details.