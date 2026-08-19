# SOAP Plugin para Sugar Language

Plugin nativo para SOAP (Simple Object Access Protocol) que proporciona capacidades completas de cliente y servidor SOAP sin dependencias externas, utilizando solo bibliotecas estándar de Python.

## Características

- ✅ **Sin dependencias externas**: Solo usa bibliotecas estándar de Python
- ✅ **Cliente SOAP completo**: Generación automática de clientes desde WSDL
- ✅ **Servidor SOAP**: Creación de servicios web SOAP
- ✅ **WSDL Support**: Parseo y generación de WSDL
- ✅ **XML Schema**: Validación y generación de esquemas XML
- ✅ **Autenticación**: WS-Security, Basic Auth, Certificate Auth
- ✅ **Manejo de errores**: SOAP Faults y excepciones
- ✅ **Logging**: Logging detallado de peticiones/respuestas
- ✅ **Caché**: Caché de WSDL y esquemas
- ✅ **Async/Await**: Operaciones asíncronas
- ✅ **Middleware**: Hooks personalizables
- ✅ **SSL/TLS**: Comunicaciones seguras
- ✅ **Proxy**: Soporte para proxies

## Instalación

No requiere instalación de dependencias externas. El plugin utiliza solo bibliotecas estándar de Python:

- `xml.etree.ElementTree` - Procesamiento XML
- `urllib.request` - Peticiones HTTP
- `ssl` - Comunicaciones seguras
- `base64` - Codificación/decodificación
- `hashlib` - Funciones hash para WS-Security
- `threading` - Operaciones asíncronas

## Uso

### Cliente SOAP Básico

```json
{
  "soap_client": {
    "operator": "create",
    "wsdl_url": "https://webservices.example.com/service?wsdl",
    "result": "cliente_soap"
  }
}
```

### Servidor SOAP Básico

```json
{
  "soap_server": {
    "operator": "create",
    "port": 8080,
    "host": "localhost",
    "service_name": "UserService",
    "result": "servidor_soap"
  }
}
```

## Comandos Disponibles

### Cliente SOAP
- `soap_client.create` - Crear cliente SOAP
- `soap_client.call` - Llamar método SOAP

### Servidor SOAP
- `soap_server.create` - Crear servidor SOAP
- `soap_server.register_method` - Registrar método
- `soap_server.start` - Iniciar servidor
- `soap_server.stop` - Detener servidor

### WSDL
- `soap_wsdl.parse` - Parsear WSDL
- `soap_wsdl.generate` - Generar WSDL
- `soap_wsdl.validate` - Validar WSDL

### XML Schema
- `soap_schema.validate` - Validar XML
- `soap_schema.generate_from_class` - Generar esquema

### Middleware
- `soap_middleware.register` - Registrar middleware

## Ejemplos

Ver los ejemplos en `/examples/08_networking/soap/` para casos de uso completos.

## Documentación

Para más información, consulta la documentación completa en `/docs/language/soap.md`.