# OpenSSL Plugin for Sugar

A comprehensive OpenSSL plugin that provides cryptographic operations for the Sugar framework.

## Features

- **Key Generation**: RSA and modern key generation
- **Certificate Operations**: CSR creation, self-signed certificates, verification
- **Format Conversion**: PEM ↔ DER ↔ CRT conversions
- **Encryption/Decryption**: File and data encryption using various algorithms
- **Digital Signatures**: File signing and verification
- **PKCS#12 Operations**: Import/export of certificate bundles
- **Hash Calculations**: Various hash algorithms (SHA256, MD5, etc.)
- **Certificate Chain Verification**: Complete certificate chain validation

## Requirements

- OpenSSL installed and available in PATH
- Sugar framework

## Installation

The plugin is automatically available when OpenSSL is installed on the system. The plugin will detect OpenSSL during initialization and provide appropriate warnings if it's not found.

## Quick Start

### Generate RSA Key

```json
{
  "openssl.genrsa": {
    "output": {
      "path": "private.key"
    },
    "params": {
      "bits": 2048
    },
    "assign_to": "key_result"
  }
}
```

### Create Certificate Signing Request

```json
{
  "openssl.req_new": {
    "input": {
      "key": "private.key"
    },
    "output": {
      "csr": "request.csr"
    },
    "params": {
      "subject": "/C=AR/ST=Buenos Aires/L=Bahia Blanca/O=Halcon Sistemas/CN=halcon.com"
    },
    "assign_to": "csr_result"
  }
}
```

### Create Self-Signed Certificate

```json
{
  "openssl.x509_selfsign": {
    "input": {
      "key": "private.key",
      "csr": "request.csr"
    },
    "output": {
      "certificate": "cert.crt"
    },
    "params": {
      "days": 365
    },
    "assign_to": "cert_result"
  }
}
```

## Available Operations

| Operation | Description |
|-----------|-------------|
| `genrsa` | Generate RSA private key |
| `genpkey` | Generate modern private key |
| `req_new` | Create Certificate Signing Request |
| `x509_selfsign` | Create self-signed certificate |
| `verify_cert` | Verify certificate |
| `convert` | Convert between formats |
| `encrypt` | Encrypt files |
| `decrypt` | Decrypt files |
| `sign` | Sign files |
| `verify` | Verify signatures |
| `pkcs12_export` | Export to PKCS#12 |
| `pkcs12_import` | Import from PKCS#12 |
| `extract_pubkey` | Extract public key |
| `hash` | Calculate hash |
| `verify_chain` | Verify certificate chain |
| `csr_to_cert` | Issue certificate from CSR |
| `pem_to_crt` | Convert PEM to CRT |
| `crt_to_pem` | Convert CRT to PEM |

## Examples

See the `examples/plugins/` directory for comprehensive examples:

- `openssl_example.json` - Complete certificate workflow
- `openssl_encryption_example.json` - Encryption/decryption operations
- `openssl_digital_signature_example.json` - Digital signature operations

## Documentation

For detailed documentation, see `docs/openssl_plugin.md`.

## Testing

Run the tests with:

```bash
python3 test/test_openssl_plugin_simple.py
```

## License

MIT License - see LICENSE file for details.