# FTP Plugin

El plugin FTP permite realizar operaciones de transferencia de archivos usando el protocolo FTP (File Transfer Protocol).

## Características

- **Conexión FTP**: Establecer conexiones a servidores FTP
- **Subir archivos**: Upload de archivos al servidor
- **Descargar archivos**: Download de archivos del servidor
- **Listar directorios**: Navegar estructura de directorios
- **Crear directorios**: Crear carpetas en el servidor
- **Eliminar archivos**: Borrar archivos del servidor
- **Modo pasivo/activo**: Configuración de modo de conexión

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `ftplib` (incluido en Python estándar)
- `pathlib` (incluido en Python estándar)

## Uso

### 1. Conexión FTP Básica

```json
{
  "ftp": {
    "host": "ftp.example.com",
    "port": 21,
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "list",
    "path": "/",
    "result": "directory_list"
  }
}
```

### 2. Subir Archivo

```json
{
  "ftp": {
    "host": "ftp.example.com",
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "upload",
    "local_file": "/local/path/file.txt",
    "remote_file": "/remote/path/file.txt",
    "result": "upload_status"
  }
}
```

### 3. Descargar Archivo

```json
{
  "ftp": {
    "host": "ftp.example.com",
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "download",
    "remote_file": "/remote/path/file.txt",
    "local_file": "/local/path/file.txt",
    "result": "download_status"
  }
}
```

### 4. Crear Directorio

```json
{
  "ftp": {
    "host": "ftp.example.com",
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "mkdir",
    "path": "/remote/new_directory",
    "result": "mkdir_status"
  }
}
```

### 5. Eliminar Archivo

```json
{
  "ftp": {
    "host": "ftp.example.com",
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "delete",
    "file": "/remote/path/file.txt",
    "result": "delete_status"
  }
}
```

## Parámetros

### Conexión
- `host` (string, requerido): Servidor FTP
- `port` (integer, opcional): Puerto FTP (default: 21)
- `username` (string, requerido): Nombre de usuario
- `password` (string, requerido): Contraseña
- `timeout` (integer, opcional): Timeout de conexión (default: 30)

### Configuración
- `passive` (boolean, opcional): Modo pasivo (default: true)
- `encoding` (string, opcional): Codificación de archivos (default: "utf-8")

### Operaciones
- `operation` (string, requerido): Tipo de operación
  - `list`: Listar directorio
  - `upload`: Subir archivo
  - `download`: Descargar archivo
  - `mkdir`: Crear directorio
  - `delete`: Eliminar archivo
  - `rename`: Renombrar archivo

### Rutas
- `path` (string, opcional): Ruta del directorio
- `local_file` (string, opcional): Ruta local del archivo
- `remote_file` (string, opcional): Ruta remota del archivo
- `file` (string, opcional): Archivo a eliminar

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Operaciones Disponibles

### Listar Directorio
- Mostrar contenido de directorio
- Información de archivos (tamaño, fecha)
- Navegación recursiva
- Filtros de archivos

### Subir Archivos
- Upload de archivos individuales
- Upload de directorios completos
- Verificación de transferencia
- Resumen de progreso

### Descargar Archivos
- Download de archivos individuales
- Download de directorios completos
- Verificación de integridad
- Resumen de progreso

### Gestión de Directorios
- Crear directorios
- Eliminar directorios
- Navegar estructura
- Verificar permisos

### Gestión de Archivos
- Eliminar archivos
- Renombrar archivos
- Verificar existencia
- Obtener información

## Ejemplos Avanzados

### Backup Automático

```json
{
  "ftp": {
    "host": "backup.example.com",
    "username": "backup_user",
    "password": "{{ backup_password }}",
    "operation": "upload",
    "local_file": "/backup/database_$(date +%Y%m%d).sql",
    "remote_file": "/backups/database_$(date +%Y%m%d).sql",
    "result": "backup_upload"
  }
}
```

### Sincronización de Archivos

```json
{
  "ftp": {
    "host": "sync.example.com",
    "username": "sync_user",
    "password": "{{ sync_password }}",
    "operation": "list",
    "path": "/sync",
    "result": "remote_files"
  },
  "ftp": {
    "host": "sync.example.com",
    "username": "sync_user",
    "password": "{{ sync_password }}",
    "operation": "download",
    "remote_file": "/sync/config.json",
    "local_file": "/local/config.json",
    "result": "config_sync"
  }
}
```

### Distribución de Contenido

```json
{
  "ftp": {
    "host": "cdn.example.com",
    "username": "cdn_user",
    "password": "{{ cdn_password }}",
    "operation": "upload",
    "local_file": "/build/app.js",
    "remote_file": "/public/js/app.js",
    "result": "js_upload"
  },
  "ftp": {
    "host": "cdn.example.com",
    "username": "cdn_user",
    "password": "{{ cdn_password }}",
    "operation": "upload",
    "local_file": "/build/style.css",
    "remote_file": "/public/css/style.css",
    "result": "css_upload"
  }
}
```

### Limpieza de Archivos Antiguos

```json
{
  "ftp": {
    "host": "storage.example.com",
    "username": "admin",
    "password": "{{ admin_password }}",
    "operation": "list",
    "path": "/logs",
    "result": "log_files"
  },
  "ftp": {
    "host": "storage.example.com",
    "username": "admin",
    "password": "{{ admin_password }}",
    "operation": "delete",
    "file": "/logs/old_log_20230101.log",
    "result": "cleanup_status"
  }
}
```

## Modos de Conexión

### Modo Pasivo (Recomendado)
- Mejor compatibilidad con firewalls
- Menos problemas de NAT
- Configuración automática de puertos

### Modo Activo
- Conexión directa del servidor
- Puede requerir configuración de firewall
- Mejor rendimiento en redes internas

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Conexión fallida**: Servidor inalcanzable
- **Autenticación fallida**: Credenciales incorrectas
- **Archivo no encontrado**: Ruta inexistente
- **Permisos insuficientes**: Falta de permisos
- **Timeout**: Conexión lenta o interrumpida

## Seguridad

### Mejores Prácticas
- Usar SFTP cuando sea posible
- Limitar permisos de usuario FTP
- Usar contraseñas fuertes
- Configurar timeouts apropiados
- Monitorear conexiones

### Configuración Segura
```json
{
  "ftp": {
    "host": "secure.example.com",
    "username": "{{ ftp_user }}",
    "password": "{{ ftp_password }}",
    "timeout": 60,
    "passive": true,
    "operation": "list",
    "path": "/",
    "result": "secure_list"
  }
}
```

## Optimización

### Transferencias Grandes
- Usar modo binario para archivos grandes
- Configurar timeouts apropiados
- Verificar integridad después de transferencia

### Múltiples Archivos
- Usar operaciones en lote
- Paralelizar transferencias cuando sea posible
- Mantener conexiones persistentes

## Recursos Adicionales

- [Documentación de ftplib](https://docs.python.org/3/library/ftplib.html)
- [Guía de Transferencia de Archivos](../../../docs/development/phase6_io.md)
