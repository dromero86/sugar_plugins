# SOAP Plugin Documentation

## Overview

The SOAP Plugin for Sugar Language provides comprehensive SOAP (Simple Object Access Protocol) capabilities without external dependencies, using only Python standard library components.

## Features

- **Native Implementation**: No external dependencies required
- **Client & Server**: Full SOAP client and server functionality
- **WSDL Support**: Parse, generate, and validate WSDL documents
- **XML Schema**: Validate XML against schemas and generate schemas
- **Security**: WS-Security, Basic Auth, Certificate authentication
- **Middleware**: Extensible middleware system for request/response processing
- **Async Support**: Asynchronous operations for better performance

## Architecture

### Core Components

1. **SOAPPlugin**: Main plugin class inheriting from PluginBase
2. **SOAPClient**: Native SOAP client implementation
3. **SOAPServer**: Native SOAP server implementation
4. **WSDLProcessor**: WSDL parsing and generation
5. **XMLSchemaValidator**: XML schema validation

### Helper Components

1. **SOAPEnvelope**: SOAP envelope generation
2. **WSSecurityHelper**: WS-Security token generation
3. **XMLHelper**: XML manipulation utilities
4. **WSDLHelper**: WSDL processing utilities
5. **SchemaHelper**: XML Schema generation

## Usage Examples

### Basic SOAP Client

```json
{
  "soap_client": {
    "operator": "create",
    "wsdl_url": "https://webservices.example.com/service?wsdl",
    "result": "client"
  }
}
```

### SOAP Method Call

```json
{
  "soap_client": {
    "operator": "call",
    "client": "{{client}}",
    "method": "GetUserInfo",
    "parameters": {
      "userId": 123
    },
    "result": "response"
  }
}
```

### SOAP Server Creation

```json
{
  "soap_server": {
    "operator": "create",
    "port": 8080,
    "host": "localhost",
    "service_name": "UserService",
    "result": "server"
  }
}
```

## Configuration

### Client Configuration

```json
{
  "soap_client": {
    "operator": "create",
    "wsdl_url": "https://webservices.example.com/service?wsdl",
    "config": {
      "timeout": 30,
      "verify_ssl": true,
      "auth": {
        "type": "basic",
        "username": "user",
        "password": "pass"
      },
      "ws_security": {
        "type": "username_token",
        "username": "user",
        "password": "pass",
        "password_type": "PasswordDigest"
      }
    },
    "result": "client"
  }
}
```

### Server Configuration

```json
{
  "soap_server": {
    "operator": "create",
    "port": 8080,
    "host": "localhost",
    "service_name": "Service",
    "auto_generate_wsdl": true,
    "config": {
      "log_requests": true,
      "validate_schema": true,
      "ssl_cert": "/path/to/cert.pem",
      "ssl_key": "/path/to/key.pem"
    },
    "result": "server"
  }
}
```

## Error Handling

### SOAP Faults

```json
{
  "try": {
    "task": [
      {
        "soap_client": {
          "operator": "call",
          "client": "{{client}}",
          "method": "GetUserInfo",
          "parameters": {"userId": 999},
          "result": "response"
        }
      }
    ],
    "catch": {
      "task": [
        {
          "print": {
            "text": "SOAP Fault: {{error.fault_code}} - {{error.fault_string}}"
          }
        }
      ]
    }
  }
}
```

## Security

### WS-Security

The plugin supports WS-Security with UsernameToken:

- **PasswordText**: Plain text password
- **PasswordDigest**: SHA1 digest with nonce and timestamp

### SSL/TLS

- Automatic SSL context creation
- Certificate validation
- Custom certificate support

## Performance

### Caching

- WSDL content caching
- Schema caching
- Connection reuse

### Async Operations

- Asynchronous method calls
- Non-blocking server operations
- Thread-safe implementations

## Testing

Run the test suite:

```bash
cd plugins/src/soap
python -m pytest tests/
```

## Dependencies

This plugin uses only Python standard library components:

- `xml.etree.ElementTree`: XML processing
- `urllib.request`: HTTP requests
- `ssl`: Secure communications
- `base64`: Encoding/decoding
- `hashlib`: Cryptographic functions
- `threading`: Async operations
- `socket`: Network communications
- `http.server`: HTTP server
- `socketserver`: Server framework

## Troubleshooting

### Common Issues

1. **WSDL Connection Errors**
   - Verify WSDL URL accessibility
   - Check network connectivity
   - Validate SSL certificates

2. **Authentication Errors**
   - Verify credentials
   - Check authentication type
   - Validate WS-Security configuration

3. **XML Validation Errors**
   - Check XML format
   - Validate against schema
   - Verify namespaces

### Debug Mode

Enable debug logging:

```python
# In your Sugar script
{
  "soap_client": {
    "operator": "create",
    "wsdl_url": "https://example.com/service?wsdl",
    "config": {
      "debug": true
    },
    "result": "client"
  }
}
```

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Ensure no external dependencies are added

## License

MIT License - see LICENSE file for details.