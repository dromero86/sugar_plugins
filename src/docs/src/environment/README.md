# Environment Plugin

El plugin Environment proporciona funcionalidades para gestionar variables de entorno, configuraciones del sistema y parámetros de ejecución de manera dinámica y segura.

## Características

- **Gestión de variables**: Leer, escribir y gestionar variables de entorno
- **Configuraciones dinámicas**: Cargar configuraciones desde archivos
- **Validación**: Validar variables de entorno requeridas
- **Encriptación**: Manejar variables sensibles de forma segura
- **Interpolación**: Interpolar variables en configuraciones
- **Entornos múltiples**: Gestionar diferentes entornos (dev, staging, prod)

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `python-dotenv>=0.19.0`
- `cryptography>=3.4.0` (para variables encriptadas)

## Uso

### 1. Leer Variable de Entorno

```json
{
  "environment": {
    "action": "get",
    "variable": "DATABASE_URL",
    "default": "sqlite:///default.db",
    "result": "db_url"
  }
}
```

### 2. Establecer Variable de Entorno

```json
{
  "environment": {
    "action": "set",
    "variable": "API_KEY",
    "value": "{{ secret_api_key }}",
    "result": "api_key_set"
  }
}
```

### 3. Cargar Archivo .env

```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/.env",
    "override": true,
    "result": "env_loaded"
  }
}
```

### 4. Validar Variables Requeridas

```json
{
  "environment": {
    "action": "validate",
    "required": [
      "DATABASE_URL",
      "API_KEY",
      "SECRET_KEY"
    ],
    "result": "validation_status"
  }
}
```

### 5. Obtener Todas las Variables

```json
{
  "environment": {
    "action": "list",
    "filter": "DB_*",
    "result": "database_vars"
  }
}
```

## Parámetros

### Configuración Básica
- `action` (string, requerido): Acción a realizar
- `variable` (string, opcional): Nombre de la variable
- `value` (string, opcional): Valor de la variable
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Archivos
- `file` (string, opcional): Ruta al archivo de configuración
- `override` (boolean, opcional): Sobrescribir variables existentes
- `encoding` (string, opcional): Codificación del archivo (default: utf-8)

### Configuración de Validación
- `required` (array, opcional): Variables requeridas
- `optional` (array, opcional): Variables opcionales
- `types` (object, opcional): Tipos de datos esperados
- `patterns` (object, opcional): Patrones de validación

### Configuración Avanzada
- `encrypt` (boolean, opcional): Encriptar variable
- `decrypt` (boolean, opcional): Desencriptar variable
- `scope` (string, opcional): Ámbito de la variable (session, global)

## Operaciones Disponibles

### Gestión de Variables
- **get**: Obtener variable de entorno
- **set**: Establecer variable de entorno
- **unset**: Eliminar variable de entorno
- **list**: Listar variables de entorno
- **exists**: Verificar si variable existe

### Gestión de Archivos
- **load_env**: Cargar archivo .env
- **save_env**: Guardar variables en archivo
- **export_env**: Exportar variables a archivo
- **import_env**: Importar variables desde archivo

### Validación y Seguridad
- **validate**: Validar variables requeridas
- **encrypt**: Encriptar variable sensible
- **decrypt**: Desencriptar variable
- **mask**: Enmascarar variable en logs

### Utilidades
- **interpolate**: Interpolar variables en texto
- **expand**: Expandir variables anidadas
- **merge**: Combinar configuraciones
- **diff**: Comparar configuraciones

## Ejemplos Avanzados

### Cargar Configuración por Entorno

```json
{
  "environment": {
    "action": "load_config",
    "config_files": [
      "/config/base.env",
      "/config/{{ env }}.env",
      "/config/local.env"
    ],
    "override": true,
    "result": "config_loaded"
  }
}
```

### Validación con Tipos

```json
{
  "environment": {
    "action": "validate",
    "required": ["DATABASE_URL", "API_KEY"],
    "types": {
      "DATABASE_URL": "url",
      "API_KEY": "string",
      "DEBUG": "boolean",
      "PORT": "integer"
    },
    "patterns": {
      "DATABASE_URL": "^[a-z]+://.*",
      "API_KEY": "^[A-Za-z0-9]{32,}$"
    },
    "result": "validation_result"
  }
}
```

### Variables Encriptadas

```json
{
  "environment": {
    "action": "set_encrypted",
    "variable": "DB_PASSWORD",
    "value": "{{ plain_password }}",
    "encryption_key": "{{ master_key }}",
    "result": "password_encrypted"
  }
}
```

### Interpolación de Variables

```json
{
  "environment": {
    "action": "interpolate",
    "template": "postgresql://{{ DB_USER }}:{{ DB_PASS }}@{{ DB_HOST }}:{{ DB_PORT }}/{{ DB_NAME }}",
    "variables": {
      "DB_USER": "{{ db_user }}",
      "DB_PASS": "{{ db_pass }}",
      "DB_HOST": "localhost",
      "DB_PORT": "5432",
      "DB_NAME": "mydb"
    },
    "result": "connection_string"
  }
}
```

### Configuración Dinámica

```json
{
  "environment": {
    "action": "load_dynamic",
    "sources": [
      {
        "type": "file",
        "path": "/config/app.env"
      },
      {
        "type": "vault",
        "path": "secret/app"
      },
      {
        "type": "aws_ssm",
        "path": "/app/config"
      }
    ],
    "result": "dynamic_config"
  }
}
```

### Gestión de Secretos

```json
{
  "environment": {
    "action": "manage_secrets",
    "operation": "rotate",
    "secrets": [
      "API_KEY",
      "JWT_SECRET",
      "DB_PASSWORD"
    ],
    "rotation_interval": "30d",
    "result": "secrets_rotated"
  }
}
```

## Configuración de Archivos

### Archivo .env Básico
```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/.env",
    "format": "dotenv",
    "result": "env_loaded"
  }
}
```

### Archivo YAML
```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/config.yaml",
    "format": "yaml",
    "result": "yaml_config"
  }
}
```

### Archivo JSON
```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/config.json",
    "format": "json",
    "result": "json_config"
  }
}
```

## Manejo de Errores

### Configuración de Errores
```json
{
  "environment": {
    "action": "validate",
    "required": ["CRITICAL_VAR"],
    "error_handling": {
      "missing_vars": "abort",
      "invalid_types": "warn",
      "invalid_patterns": "warn",
      "continue_on_error": false
    },
    "result": "validation_with_errors"
  }
}
```

### Validación Robusta
```json
{
  "environment": {
    "action": "validate_robust",
    "required": ["API_KEY", "DATABASE_URL"],
    "fallbacks": {
      "API_KEY": "default_api_key",
      "DATABASE_URL": "sqlite:///fallback.db"
    },
    "result": "robust_validation"
  }
}
```

## Optimización

### Configuración de Caché
```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/.env",
    "cache": {
      "enabled": true,
      "ttl": 300,
      "key": "env_cache"
    },
    "result": "cached_env"
  }
}
```

### Configuración de Memoria
```json
{
  "environment": {
    "action": "load_env",
    "file": "/path/to/.env",
    "memory": {
      "max_vars": 1000,
      "clear_on_reload": true
    },
    "result": "memory_efficient_env"
  }
}
```

## Configuración de Seguridad

### Configuración Segura
```json
{
  "environment": {
    "action": "load_secure",
    "file": "/path/to/.env",
    "security": {
      "encrypt_sensitive": true,
      "mask_in_logs": true,
      "file_permissions": "600",
      "validate_checksums": true
    },
    "result": "secure_env"
  }
}
```

### Gestión de Secretos
```json
{
  "environment": {
    "action": "secrets_manager",
    "operation": "store",
    "secrets": {
      "API_KEY": "{{ api_key }}",
      "DB_PASSWORD": "{{ db_password }}"
    },
    "encryption": {
      "algorithm": "AES-256-GCM",
      "key_source": "vault"
    },
    "result": "secrets_stored"
  }
}
```

## Recursos Adicionales

- [Documentación de python-dotenv](https://github.com/theskumar/python-dotenv)
- [Guía de Configuración](../../../docs/development/configuration_management.md) 