# ZIP Plugin

El plugin ZIP proporciona funcionalidades para crear, extraer y manipular archivos comprimidos en formato ZIP.

## Características

- **Crear archivos ZIP**: Comprimir archivos y directorios
- **Extraer archivos ZIP**: Descomprimir archivos ZIP
- **Listar contenido**: Ver contenido de archivos ZIP
- **Comprimir con contraseña**: Archivos ZIP protegidos
- **Filtros de archivos**: Incluir/excluir archivos específicos
- **Compresión personalizada**: Niveles de compresión configurables

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `zipfile` (incluido en Python estándar)
- `pathlib` (incluido en Python estándar)

## Uso

### 1. Crear Archivo ZIP Básico

```json
{
  "zip": {
    "operation": "create",
    "source": "/path/to/source",
    "destination": "/path/to/archive.zip",
    "result": "zip_status"
  }
}
```

### 2. Crear ZIP con Múltiples Fuentes

```json
{
  "zip": {
    "operation": "create",
    "sources": [
      "/path/to/file1.txt",
      "/path/to/file2.txt",
      "/path/to/directory"
    ],
    "destination": "/path/to/archive.zip",
    "result": "multi_zip"
  }
}
```

### 3. Extraer Archivo ZIP

```json
{
  "zip": {
    "operation": "extract",
    "source": "/path/to/archive.zip",
    "destination": "/path/to/extract",
    "result": "extract_status"
  }
}
```

### 4. ZIP con Contraseña

```json
{
  "zip": {
    "operation": "create",
    "source": "/path/to/sensitive_data",
    "destination": "/path/to/secure.zip",
    "password": "{{ secret_password }}",
    "result": "secure_zip"
  }
}
```

### 5. Listar Contenido ZIP

```json
{
  "zip": {
    "operation": "list",
    "source": "/path/to/archive.zip",
    "result": "zip_contents"
  }
}
```

## Parámetros

### Operaciones
- `operation` (string, requerido): Tipo de operación
  - `create`: Crear archivo ZIP
  - `extract`: Extraer archivo ZIP
  - `list`: Listar contenido
  - `test`: Verificar integridad

### Fuentes
- `source` (string, opcional): Archivo o directorio fuente único
- `sources` (array, opcional): Lista de archivos/directorios fuente

### Destino
- `destination` (string, opcional): Ruta de destino para el archivo ZIP
- `extract_path` (string, opcional): Ruta de extracción

### Configuración
- `password` (string, opcional): Contraseña para archivos protegidos
- `compression_level` (integer, opcional): Nivel de compresión (0-9, default: 6)
- `include_hidden` (boolean, opcional): Incluir archivos ocultos (default: false)

### Filtros
- `include_patterns` (array, opcional): Patrones de archivos a incluir
- `exclude_patterns` (array, opcional): Patrones de archivos a excluir

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Operaciones Disponibles

### Crear ZIP
- Comprimir archivos y directorios
- Soporte para múltiples fuentes
- Filtros de inclusión/exclusión
- Compresión con contraseña

### Extraer ZIP
- Extraer archivos completos
- Extraer archivos específicos
- Verificar integridad durante extracción
- Manejo de archivos protegidos

### Listar Contenido
- Mostrar estructura de archivos
- Información de tamaños
- Fechas de modificación
- Estado de compresión

### Verificar Integridad
- Verificar archivos corruptos
- Validar checksums
- Detectar archivos faltantes

## Ejemplos Avanzados

### Backup con Filtros

```json
{
  "zip": {
    "operation": "create",
    "source": "/var/www",
    "destination": "/backup/website_$(date +%Y%m%d).zip",
    "exclude_patterns": [
      "*.log",
      "*.tmp",
      "node_modules/*",
      ".git/*"
    ],
    "compression_level": 9,
    "result": "backup_status"
  }
}
```

### Extracción Selectiva

```json
{
  "zip": {
    "operation": "extract",
    "source": "/path/to/archive.zip",
    "destination": "/path/to/extract",
    "include_patterns": [
      "*.txt",
      "*.md"
    ],
    "result": "selective_extract"
  }
}
```

### ZIP Incremental

```json
{
  "zip": {
    "operation": "create",
    "source": "/path/to/data",
    "destination": "/backup/incremental_$(date +%Y%m%d_%H%M).zip",
    "include_patterns": [
      "*.json",
      "*.csv"
    ],
    "compression_level": 5,
    "result": "incremental_backup"
  }
}
```

### Verificación de Integridad

```json
{
  "zip": {
    "operation": "test",
    "source": "/path/to/archive.zip",
    "result": "integrity_check"
  }
}
```

## Filtros de Archivos

### Patrones de Inclusión
- `*.txt`: Solo archivos de texto
- `**/*.py`: Archivos Python en cualquier subdirectorio
- `data/*`: Todo en el directorio data

### Patrones de Exclusión
- `*.log`: Excluir archivos de log
- `temp/*`: Excluir directorio temporal
- `.git/*`: Excluir directorio git

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Archivo no encontrado**: Fuente inexistente
- **Permisos insuficientes**: Falta de permisos de lectura/escritura
- **Disco lleno**: Espacio insuficiente
- **Archivo corrupto**: ZIP dañado
- **Contraseña incorrecta**: Error en archivos protegidos

## Ejemplos de Uso Común

### Backup de Base de Datos

```json
{
  "zip": {
    "operation": "create",
    "source": "/var/lib/mysql/backup",
    "destination": "/backup/db_$(date +%Y%m%d_%H%M).zip",
    "compression_level": 9,
    "result": "db_backup"
  }
}
```

### Distribución de Archivos

```json
{
  "zip": {
    "operation": "create",
    "sources": [
      "/app/dist/*",
      "/app/README.md",
      "/app/LICENSE"
    ],
    "destination": "/releases/app_v1.0.0.zip",
    "exclude_patterns": [
      "*.map",
      "*.log"
    ],
    "result": "release_package"
  }
}
```

### Logs de Aplicación

```json
{
  "zip": {
    "operation": "create",
    "source": "/var/log/app",
    "destination": "/archive/logs_$(date +%Y%m).zip",
    "include_patterns": ["*.log"],
    "compression_level": 6,
    "result": "log_archive"
  }
}
```

## Optimización

### Niveles de Compresión
- `0`: Sin compresión (más rápido)
- `6`: Compresión balanceada (default)
- `9`: Máxima compresión (más lento)

### Mejores Prácticas
- Usar filtros para excluir archivos innecesarios
- Elegir nivel de compresión según necesidades
- Verificar integridad de archivos importantes
- Usar contraseñas para datos sensibles

## Recursos Adicionales

- [Documentación de zipfile](https://docs.python.org/3/library/zipfile.html)
- [Guía de Backup](../../../docs/development/phase2_implementation.md)
