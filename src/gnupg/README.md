# GnuPG Plugin for Sugar Language v2.0.0

A comprehensive GnuPG plugin that provides cryptographic operations for the Sugar framework.

## Features

- **Key Generation**: RSA, DSA, ECDSA, EDDSA key generation
- **Key Management**: Import/export, listing, deletion, trust management
- **Encryption/Decryption**: File and text encryption using symmetric and asymmetric methods
- **Digital Signatures**: File signing, verification, clearsign, and detached signatures
- **Agent Configuration**: GnuPG agent setup and SSH integration
- **System Information**: Version info, supported algorithms, dependency checking
- **Testing**: Comprehensive functionality testing

## Requirements

- GnuPG installed and available in PATH
- Sugar framework
- Python package: `python-gnupg>=0.5.0` (optional, for advanced features)

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
# Install Python package (optional)
pip install python-gnupg>=0.5.0
```

## Quick Start

### Check Dependencies

```json
{
  "gnupg": {
    "operator": "check_dependencies",
    "result": "dependency_status"
  }
}
```

### Generate RSA Key

```json
{
  "gnupg": {
    "operator": "generate_key",
    "key_type": "RSA",
    "key_length": 2048,
    "name_real": "Juan Pérez",
    "name_email": "juan.perez@ejemplo.com",
    "name_comment": "Clave para Sugar Language",
    "expire_date": "2y",
    "passphrase": "MiPassphraseSegura123!",
    "result": "key_generation"
  }
}
```

### Encrypt Text

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

### Sign Document

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

## Available Operations

### Key Management

| Operation | Description |
|-----------|-------------|
| `generate_key` | Generate new GnuPG key |
| `list_keys` | List public/secret keys |
| `import_key` | Import key from file |
| `export_key` | Export key to file |
| `delete_key` | Delete key |
| `sign_key` | Sign public key |
| `revoke_key` | Generate revocation certificate |
| `trust_key` | Set trust level |

### Encryption/Decryption

| Operation | Description |
|-----------|-------------|
| `encrypt_file` | Encrypt file asymmetrically |
| `decrypt_file` | Decrypt file |
| `encrypt_text` | Encrypt text asymmetrically |
| `decrypt_text` | Decrypt text |
| `symmetric_encrypt` | Encrypt file symmetrically |
| `symmetric_decrypt` | Decrypt file symmetrically |

### Signing/Verification

| Operation | Description |
|-----------|-------------|
| `sign_file` | Sign file (binary) |
| `verify_signature` | Verify signature |
| `clearsign` | Create clearsigned file |
| `detached_sign` | Create detached signature |
| `sign_text` | Sign text content |
| `verify_text` | Verify text signature |

### Utility

| Operation | Description |
|-----------|-------------|
| `check_dependencies` | Check system dependencies |
| `system_info` | Get GnuPG system information |
| `test_functionality` | Test GnuPG functionality |
| `configure_agent` | Configure GnuPG agent |
| `check_agent_status` | Check agent status |

## Examples

See the `examples/` directory for comprehensive examples:

- `basic_usage.json` - Basic key generation and encryption
- `key_management.json` - Complete key management workflow
- `encryption_examples.json` - Encryption/decryption operations
- `signing_examples.json` - Digital signature operations

## Documentation

For detailed documentation, see `docs/` directory:

- `API.md` - Complete API reference
- `examples.md` - Detailed examples and use cases

## Testing

Run the tests with:

```bash
python3 tests/test_gnupg_plugin.py
```

## License

MIT License - see LICENSE file for details.