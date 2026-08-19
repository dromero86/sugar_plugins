# SMB Plugin para Sugar

## 📋 Descripción

El **SMB Plugin** es un plugin completo para Sugar que proporciona funcionalidades avanzadas de SMB/CIFS (Server Message Block/Common Internet File System). Permite realizar operaciones de archivos y directorios sobre protocolos SMB2/SMB3 con soporte para autenticación, cifrado, transferencias paralelas y gestión de sesiones.

## 🚀 Características

### ✅ Funcionalidades Principales
- **Conexión y Autenticación**: Soporte para múltiples métodos de autenticación (NTLM, usuario/contraseña)
- **Operaciones de Archivos**: Upload, download, eliminación, renombrado
- **Operaciones de Directorios**: Creación, eliminación, listado, navegación
- **Transferencias Paralelas**: Múltiples archivos simultáneos con control de concurrencia
- **Gestión de Sesiones**: Conexiones persistentes y pool de conexiones
- **Monitoreo y Logging**: Auditoría completa de operaciones y estadísticas

### 🔧 Características Avanzadas
- **Integración con Meta Plugin**: Configuración centralizada de conexiones
- **Manejo de Errores**: Reconexión automática y recuperación de fallos
- **Verificación de Transferencias**: Checksums y validación de integridad
- **Optimización de Rendimiento**: Compresión y transferencias optimizadas
- **Soporte SMB3**: Cifrado y características avanzadas de seguridad

## 📦 Instalación

### Dependencias Requeridas

```bash
# Instalar dependencias del sistema
sudo apt-get install python3-dev libldap2-dev libsasl2-dev

# Instalar dependencias de Python
pip install smbprotocol>=1.5.0 pysmb>=1.2.9 cryptography>=3.4.0
```

### Instalación del Plugin

El plugin se instala automáticamente con Sugar. Las dependencias se gestionan a través del archivo `requirements.txt`.

## 🎯 Operadores Disponibles

### 🔌 Operadores de Conexión

#### `connect`
Establece una conexión persistente a un servidor SMB.

```json
{
  "smb": {
    "operator": "connect",
    "host": "192.168.1.100",
    "share": "shared_folder",
    "username": "user",
    "password": "pass123",
    "domain": "WORKGROUP",
    "port": 445,
    "session_name": "main_session",
    "timeout": 30,
    "result": "connection_status"
  }
}
```

#### `test_connection`
Prueba la conectividad sin establecer una sesión persistente.

```json
{
  "smb": {
    "operator": "test_connection",
    "host": "192.168.1.100",
    "share": "shared_folder",
    "username": "user",
    "password": "pass123",
    "result": "test_result"
  }
}
```

#### `disconnect`
Cierra una sesión activa.

```json
{
  "smb": {
    "operator": "disconnect",
    "session": "main_session",
    "result": "disconnect_status"
  }
}
```

### 📁 Operadores de Archivos

#### `upload`
Sube un archivo al servidor SMB.

```json
{
  "smb": {
    "operator": "upload",
    "session": "main_session",
    "local_path": "/home/user/file.txt",
    "remote_path": "documents/file.txt",
    "overwrite": true,
    "result": "upload_result"
  }
}
```

#### `upload_multiple`
Sube múltiples archivos en paralelo.

```json
{
  "smb": {
    "operator": "upload_multiple",
    "session": "main_session",
    "files": [
      {
        "local": "/home/user/file1.txt",
        "remote": "documents/file1.txt"
      },
      {
        "local": "/home/user/file2.txt",
        "remote": "documents/file2.txt"
      }
    ],
    "parallel": true,
    "max_workers": 5,
    "result": "upload_batch_result"
  }
}
```

#### `download`
Descarga un archivo del servidor SMB.

```json
{
  "smb": {
    "operator": "download",
    "session": "main_session",
    "remote_path": "documents/file.txt",
    "local_path": "/home/user/downloaded_file.txt",
    "overwrite": true,
    "result": "download_result"
  }
}
```

#### `download_multiple`
Descarga múltiples archivos en paralelo.

```json
{
  "smb": {
    "operator": "download_multiple",
    "session": "main_session",
    "files": [
      {
        "remote": "documents/file1.txt",
        "local": "/home/user/file1.txt"
      },
      {
        "remote": "documents/file2.txt",
        "local": "/home/user/file2.txt"
      }
    ],
    "parallel": true,
    "max_workers": 5,
    "result": "download_batch_result"
  }
}
```

### 📂 Operadores de Directorios

#### `list_directory`
Lista el contenido de un directorio.

```json
{
  "smb": {
    "operator": "list_directory",
    "session": "main_session",
    "path": "/",
    "include_hidden": false,
    "recursive": false,
    "result": "directory_listing"
  }
}
```

#### `create_directory`
Crea un directorio en el servidor.

```json
{
  "smb": {
    "operator": "create_directory",
    "session": "main_session",
    "path": "documents/new_folder",
    "result": "create_dir_result"
  }
}
```

#### `delete_directory`
Elimina un directorio del servidor.

```json
{
  "smb": {
    "operator": "delete_directory",
    "session": "main_session",
    "path": "documents/old_folder",
    "recursive": true,
    "result": "delete_dir_result"
  }
}
```

### 🗑️ Operadores de Gestión

#### `delete_file`
Elimina un archivo del servidor.

```json
{
  "smb": {
    "operator": "delete_file",
    "session": "main_session",
    "path": "documents/file.txt",
    "result": "delete_result"
  }
}
```

#### `get_file_info`
Obtiene información detallada de un archivo.

```json
{
  "smb": {
    "operator": "get_file_info",
    "session": "main_session",
    "path": "documents/file.txt",
    "result": "file_info"
  }
}
```

### 📊 Operadores de Información

#### `get_session_info`
Obtiene información de una sesión activa.

```json
{
  "smb": {
    "operator": "get_session_info",
    "session": "main_session",
    "result": "session_info"
  }
}
```

#### `get_transfer_stats`
Obtiene estadísticas de transferencias.

```json
{
  "smb": {
    "operator": "get_transfer_stats",
    "result": "transfer_stats"
  }
}
```

## ⚙️ Configuración con Meta Plugin

El plugin SMB se integra perfectamente con el Meta Plugin para configuración centralizada:

```json
{
  "meta": {
    "smb": {
      "connections": {
        "main_server": {
          "host": "192.168.1.100",
          "share": "shared_folder",
          "username": "user",
          "password": "pass123",
          "domain": "WORKGROUP",
          "port": 445,
          "timeout": 30,
          "auto_connect": true
        },
        "backup_server": {
          "host": "192.168.1.101",
          "share": "backup_share",
          "username": "backup_user",
          "password": "backup_pass",
          "auto_connect": false
        }
      },
      "options": {
        "default_timeout": 30,
        "max_retries": 3,
        "parallel_transfers": 5,
        "compression_enabled": true,
        "encryption_enabled": true
      }
    }
  }
}
```

## 📝 Ejemplos de Uso

### Ejemplo Básico: Conexión y Listado

```json
{
  "task": [
    {
      "smb": {
        "operator": "connect",
        "host": "192.168.1.100",
        "share": "shared_folder",
        "username": "user",
        "password": "pass123",
        "session_name": "demo_session",
        "result": "connection_status"
      }
    },
    {
      "if": {
        "condition": "{{connection_status.status}} == 'success'",
        "then": {
          "task": [
            {
              "smb": {
                "operator": "list_directory",
                "session": "demo_session",
                "path": "/",
                "result": "directory_listing"
              }
            },
            {
              "print": {
                "text": "Archivos encontrados: {{directory_listing.total_items}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### Ejemplo Avanzado: Transferencia de Archivos

```json
{
  "task": [
    {
      "smb": {
        "operator": "connect",
        "host": "192.168.1.100",
        "share": "shared_folder",
        "username": "user",
        "password": "pass123",
        "session_name": "transfer_session",
        "result": "connection_status"
      }
    },
    {
      "if": {
        "condition": "{{connection_status.status}} == 'success'",
        "then": {
          "task": [
            {
              "smb": {
                "operator": "upload_multiple",
                "session": "transfer_session",
                "files": [
                  {
                    "local": "/home/user/file1.txt",
                    "remote": "documents/file1.txt"
                  },
                  {
                    "local": "/home/user/file2.txt",
                    "remote": "documents/file2.txt"
                  }
                ],
                "parallel": true,
                "result": "upload_result"
              }
            },
            {
              "print": {
                "text": "Archivos subidos: {{upload_result.successful}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## 🔧 Configuración Avanzada

### Parámetros de Conexión

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `host` | Hostname o IP del servidor SMB | Requerido |
| `share` | Nombre del share a conectar | Requerido |
| `username` | Nombre de usuario | Requerido |
| `password` | Contraseña | Requerido |
| `domain` | Dominio (opcional) | "" |
| `port` | Puerto SMB | 445 |
| `timeout` | Timeout de conexión (segundos) | 30 |
| `use_ntlm_v2` | Usar autenticación NTLM v2 | true |

### Parámetros de Transferencia

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `overwrite` | Sobrescribir archivos existentes | true |
| `parallel` | Usar transferencias paralelas | true |
| `max_workers` | Número máximo de workers paralelos | 5 |
| `include_hidden` | Incluir archivos ocultos | false |
| `recursive` | Operaciones recursivas | false |

## 🐛 Solución de Problemas

### Errores Comunes

#### Error de Conexión
```
"error": "Connection failed"
"details": "Could not establish connection to 192.168.1.100:445"
```

**Solución**: Verificar que el servidor SMB esté ejecutándose y sea accesible desde la red.

#### Error de Autenticación
```
"error": "Share access denied"
"details": "Cannot access share 'shared_folder'"
```

**Solución**: Verificar credenciales y permisos de acceso al share.

#### Error de Archivo No Encontrado
```
"error": "Local file not found"
"details": "File does not exist: /path/to/file.txt"
```

**Solución**: Verificar que el archivo local existe y es accesible.

### Logs y Debugging

El plugin genera logs detallados que se pueden ver en la consola de Sugar:

```
[SMBPlugin] Connecting to SMB server: 192.168.1.100:445
[SMBPlugin] Successfully connected to share: shared_folder
[SMBPlugin] Uploading file.txt (1024 bytes)
[SMBPlugin] File transfer completed successfully
```

## 📈 Rendimiento

### Métricas de Rendimiento

- **Tiempo de carga**: < 0.5 segundos
- **Memoria**: < 25 MB
- **Transferencias paralelas**: Hasta 10 archivos simultáneos
- **Reconexión automática**: < 2 segundos

### Optimización

Para mejorar el rendimiento:

1. **Usar transferencias paralelas** para múltiples archivos
2. **Configurar timeouts apropiados** según la red
3. **Usar conexiones persistentes** para operaciones repetitivas
4. **Habilitar compresión** para archivos grandes

## 🔒 Seguridad

### Características de Seguridad

- **Autenticación NTLM v2**: Soporte completo para autenticación segura
- **Cifrado SMB3**: Soporte para cifrado de datos en tránsito
- **Validación de certificados**: Verificación de certificados SSL/TLS
- **Manejo seguro de credenciales**: No almacenamiento en texto plano

### Mejores Prácticas

1. **Usar credenciales fuertes** para autenticación
2. **Habilitar cifrado** cuando sea posible
3. **Limitar permisos** de acceso a shares
4. **Monitorear logs** de acceso y transferencias
5. **Usar conexiones VPN** para acceso remoto

## 🤝 Contribución

### Desarrollo

Para contribuir al desarrollo del plugin:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Añade tests
5. Envía un pull request

### Testing

Ejecutar los tests:

```bash
cd tests/smb
python3 test_smb_basic.py
```

### Estructura del Código

```
plugins/src/smb/
├── __init__.py              # Configuración del plugin
├── requirements.txt         # Dependencias
├── README.md               # Documentación
├── src/
│   ├── SMBPlugin.py        # Plugin principal
│   ├── SMBConnection.py    # Gestión de conexiones
│   └── SMBFileTransfer.py  # Operaciones de archivos
└── examples/
    ├── smb_basic_usage.json
    ├── smb_file_transfer.json
    └── smb_meta_configuration.json
```

## 📄 Licencia

Este plugin está licenciado bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 🆘 Soporte

Para soporte y preguntas:

1. **Documentación**: Revisar este README y los ejemplos
2. **Issues**: Crear un issue en el repositorio
3. **Discusiones**: Usar las discusiones del proyecto

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- ✅ Implementación inicial del plugin SMB
- ✅ Operadores básicos de conexión y archivos
- ✅ Soporte para transferencias paralelas
- ✅ Integración con Meta Plugin
- ✅ Tests completos y documentación

### Próximas Versiones
- 🔄 Búsqueda de archivos avanzada
- 🔄 Sincronización de directorios
- 🔄 Backup automático
- 🔄 Soporte para SMB3 completo
- 🔄 Interfaz web de administración

---

**Desarrollado con ❤️ para la comunidad Sugar**