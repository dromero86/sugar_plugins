# SSH Plugin

El plugin SSH permite realizar operaciones de conexión y ejecución remota usando el protocolo SSH.

## Características

- **Conexión SSH**: Establecer conexiones seguras a servidores remotos
- **Ejecución de comandos**: Ejecutar comandos en servidores remotos
- **Transferencia de archivos**: SCP y SFTP para transferencia de archivos
- **Gestión de claves**: Soporte para autenticación por clave pública/privada
- **Conexiones persistentes**: Mantener conexiones activas para múltiples operaciones

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `paramiko>=2.7.0`
- `cryptography>=3.4.0`

## Uso

### 1. Conexión SSH Básica

```json
{
  "ssh": {
    "host": "192.168.1.100",
    "port": 22,
    "username": "usuario",
    "password": "{{ password }}",
    "command": "ls -la",
    "result": "output"
  }
}
```

### 2. Conexión con Clave Privada

```json
{
  "ssh": {
    "host": "servidor.com",
    "port": 22,
    "username": "usuario",
    "key_filename": "/path/to/private_key",
    "command": "whoami",
    "result": "user_info"
  }
}
```

### 3. Transferencia de Archivos (SCP)

```json
{
  "ssh": {
    "host": "servidor.com",
    "username": "usuario",
    "password": "{{ password }}",
    "operation": "scp_upload",
    "local_path": "/local/file.txt",
    "remote_path": "/remote/file.txt",
    "result": "upload_status"
  }
}
```

### 4. Múltiples Comandos

```json
{
  "ssh": {
    "host": "servidor.com",
    "username": "usuario",
    "password": "{{ password }}",
    "commands": [
      "cd /var/log",
      "ls -la",
      "tail -n 10 system.log"
    ],
    "result": "log_output"
  }
}
```

## Parámetros

### Conexión
- `host` (string, requerido): Dirección IP o hostname del servidor
- `port` (integer, opcional): Puerto SSH (default: 22)
- `username` (string, requerido): Nombre de usuario
- `password` (string, opcional): Contraseña para autenticación
- `key_filename` (string, opcional): Ruta a la clave privada

### Operaciones
- `command` (string, opcional): Comando único a ejecutar
- `commands` (array, opcional): Lista de comandos a ejecutar
- `operation` (string, opcional): Tipo de operación (scp_upload, scp_download, sftp)

### Transferencia de Archivos
- `local_path` (string, opcional): Ruta local del archivo
- `remote_path` (string, opcional): Ruta remota del archivo
- `recursive` (boolean, opcional): Transferencia recursiva para directorios

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Operaciones Disponibles

### Comandos Remotos
- Ejecución de comandos individuales o múltiples
- Captura de salida estándar y errores
- Timeout configurable

### Transferencia SCP
- `scp_upload`: Subir archivos al servidor remoto
- `scp_download`: Descargar archivos del servidor remoto

### Transferencia SFTP
- `sftp_upload`: Subir archivos usando SFTP
- `sftp_download`: Descargar archivos usando SFTP
- `sftp_list`: Listar archivos en directorio remoto

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Conexión fallida**: Host inalcanzable o puerto cerrado
- **Autenticación fallida**: Credenciales incorrectas
- **Comando fallido**: Errores en la ejecución de comandos
- **Transferencia fallida**: Problemas en transferencia de archivos

## Ejemplos Avanzados

### Backup Remoto

```json
{
  "ssh": {
    "host": "servidor.com",
    "username": "admin",
    "key_filename": "/home/user/.ssh/id_rsa",
    "commands": [
      "mkdir -p /backup/$(date +%Y%m%d)",
      "tar -czf /backup/$(date +%Y%m%d)/backup.tar.gz /var/www",
      "ls -la /backup/$(date +%Y%m%d)"
    ],
    "result": "backup_status"
  }
}
```

### Monitoreo de Sistema

```json
{
  "ssh": {
    "host": "servidor.com",
    "username": "monitor",
    "password": "{{ monitor_password }}",
    "commands": [
      "uptime",
      "free -h",
      "df -h",
      "ps aux | head -10"
    ],
    "result": "system_status"
  }
}
```

## Seguridad

- Usar claves SSH en lugar de contraseñas cuando sea posible
- Limitar permisos de usuario en servidores remotos
- Usar conexiones VPN para acceso a servidores internos
- Rotar claves SSH regularmente

## Recursos Adicionales

- [Documentación de Paramiko](https://docs.paramiko.org/)
- [Guía de Seguridad SSH](../../../docs/security/ADVANCED_SECURITY_DIAGNOSTICS.md)
