# Plugins Disponibles

Esta carpeta contiene la documentación específica de cada plugin disponible en el sistema Sugar.

## Lista de Plugins

### 🔗 Networking
- **[curl](curl/README.md)** - Operaciones cURL avanzadas
- **[request](request/README.md)** - Peticiones HTTP nativas
- **[http_session](http_session/README.md)** - Sesiones HTTP
- **[ftp](ftp/README.md)** - Operaciones FTP
- **[ssh](ssh/README.md)** - Operaciones SSH

### 🌐 Web Automation
- **[selenium](selenium/README.md)** - Automatización web con Selenium
- **[extract_table_selenium](extract_table_selenium/README.md)** - Extracción de tablas HTML
- **[webserver](webserver/README.md)** - Servidor web integrado

### 💾 Data & Storage
- **[database](database/README.md)** - Operaciones con base de datos
- **[zip](zip/README.md)** - Operaciones de compresión

### 🔐 Security & Authentication
- **[jwt](jwt/README.md)** - Manejo de tokens JWT
- **[openssl](openssl/README.md)** - Operaciones criptográficas
- **[openssl_binary](openssl_binary/README.md)** - OpenSSL binario
- **[openssl_native](openssl_native/README.md)** - OpenSSL nativo

### 🛠️ Development Tools
- **[compiler](compiler/README.md)** - Compilación de código
- **[driver](driver/README.md)** - Drivers de sistema
- **[environment](environment/README.md)** - Gestión de variables de entorno
- **[meta](meta/README.md)** - Operaciones meta-programación

### 📝 Templates & Processing
- **[jinja2](jinja2/README.md)** - Plantillas Jinja2

## Estado de Desarrollo

### ✅ Estable
- curl
- request
- database
- environment
- jwt
- selenium
- ssh
- webserver
- zip

### 🔄 En Desarrollo
- extract_table_selenium
- openssl_native
- meta

### 📋 Planificado
- Nuevos plugins según necesidades del proyecto

## Instalación

### Instalación Individual
```bash
# Para un plugin específico
cd plugins/plugin_name
pip install -r requirements.txt
```

### Instalación Completa
```bash
# Instalar todos los plugins
cd plugins
find . -name "requirements.txt" -exec pip install -r {} \;
```

## Dependencias Comunes

### Networking
- `requests>=2.25.0`
- `urllib3>=1.26.0`

### Web Automation
- `selenium>=4.0.0`
- `webdriver-manager>=3.8.0`

### Database
- `sqlalchemy>=1.4.0`
- `psycopg2-binary>=2.9.0`

### Security
- `pyjwt>=2.3.0`
- `cryptography>=3.4.0`

## Contribución

Para contribuir a un plugin:

1. Revisar la documentación del plugin específico
2. Seguir las convenciones de desarrollo
3. Añadir tests para nuevas funcionalidades
4. Actualizar la documentación
5. Verificar compatibilidad con otros plugins

## Reportar Problemas

Si encuentras problemas con un plugin:

1. Revisar la documentación del plugin
2. Verificar las dependencias
3. Revisar los logs de error
4. Crear un issue con información detallada

## Recursos Adicionales

- [Guía de Desarrollo](../user_guide/README.md)
- [Convenciones del Proyecto](../../../docs/development/coding_standards.md)
- [Ejemplos de Uso](../../../examples/)
