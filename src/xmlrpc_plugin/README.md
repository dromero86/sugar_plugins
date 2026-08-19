# XML-RPC Plugin para Sugar Language

Este plugin proporciona funcionalidades completas de cliente y servidor XML-RPC para Sugar Language.

## Características

### Cliente XML-RPC
- Conexión segura con SSL/TLS
- Autenticación (Basic Auth, Token-based, Digest)
- Manejo de errores robusto
- Operaciones asíncronas
- Caching de respuestas
- Métricas de rendimiento
- Logging configurable

### Servidor XML-RPC
- Configuración flexible (host, puerto, timeouts)
- Registro dinámico de métodos
- Métodos del sistema estándar (system.listMethods, etc.)
- Soporte SSL/TLS
- Métricas de rendimiento
- Logging configurable

## Uso

### Habilitar el plugin
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pe xmlrpc_plugin
```

### Ejemplos de uso
Ver los ejemplos en `examples/08_networking/xml_rpc/` para casos de uso completos.

## Estructura del Plugin

```
xmlrpc_plugin/
├── __init__.py          # Registro del plugin
├── xml_rpc_client.py    # Implementación del cliente
├── xml_rpc_server.py    # Implementación del servidor
└── README.md           # Documentación
```

## Dependencias

- `requests` - Para comunicación HTTP
- `xml.etree.ElementTree` - Para parsing XML
- `threading` - Para operaciones asíncronas
- `concurrent.futures` - Para ThreadPoolExecutor

## Versión

1.0.0 - Compatible con Sugar Language 3.0.0+
