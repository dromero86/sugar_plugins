# Zip Plugin for Sugar Framework

Plugin para compresión y descompresión de archivos con soporte completo para múltiples formatos y integración con el SDK de Sugar.

## 🚀 Características

- **8 formatos soportados**: ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ, GZ, BZ2, XZ
- **8 operadores**: compress, extract, info, list, test, convert, merge, split
- **Integración SDK**: Hooks, interceptores, customizers y alias
- **Sintaxis JSON**: Compatible con el lenguaje Sugar
- **Manejo de errores**: Robusto y informativo
- **Optimización**: Múltiples niveles de compresión

## 📦 Instalación

El plugin se instala automáticamente con Sugar Framework. No requiere dependencias adicionales.

## 🎯 Uso Básico

### Sintaxis JSON

```json
{
  "zip": {
    "operator": "compress",
    "source": "./datos_proyecto",
    "destination": "./backup.zip",
    "format": "zip",
    "compression_level": 9,
    "result": "backup_resultado"
  }
}
```

### Operadores Disponibles

#### 1. Compresión (`compress`)
```json
{
  "zip": {
    "operator": "compress",
    "source": "./datos",
    "destination": "./backup.zip",
    "format": "zip",
    "compression_level": 6,
    "include_hidden": false,
    "password": "opcional",
    "result": "resultado"
  }
}
```

#### 2. Extracción (`extract`)
```json
{
  "zip": {
    "operator": "extract",
    "source": "./backup.zip",
    "destination": "./datos_extraidos",
    "password": "opcional",
    "overwrite": true,
    "result": "resultado"
  }
}
```

#### 3. Información (`info`)
```json
{
  "zip": {
    "operator": "info",
    "source": "./backup.zip",
    "result": "info_archivo"
  }
}
```

#### 4. Listado (`list`)
```json
{
  "zip": {
    "operator": "list",
    "source": "./backup.zip",
    "password": "opcional",
    "result": "lista_archivos"
  }
}
```

#### 5. Verificación (`test`)
```json
{
  "zip": {
    "operator": "test",
    "source": "./backup.zip",
    "password": "opcional",
    "result": "verificacion"
  }
}
```

#### 6. Conversión (`convert`)
```json
{
  "zip": {
    "operator": "convert",
    "source": "./backup.zip",
    "destination": "./backup.tar.gz",
    "target_format": "tar.gz",
    "result": "conversion"
  }
}
```

#### 7. Combinación (`merge`)
```json
{
  "zip": {
    "operator": "merge",
    "sources": ["./archivo1.zip", "./archivo2.zip"],
    "destination": "./combinado.zip",
    "result": "merge_resultado"
  }
}
```

#### 8. División (`split`)
```json
{
  "zip": {
    "operator": "split",
    "source": "./archivo_grande.zip",
    "destination": "./partes",
    "max_size": "100MB",
    "result": "split_resultado"
  }
}
```

## 📋 Formatos Soportados

| Formato | Extensión | Descripción | Compresión |
|---------|-----------|-------------|------------|
| ZIP | `.zip` | ZIP archive format | Sí |
| TAR | `.tar` | TAR archive format | No |
| TAR.GZ | `.tar.gz`, `.tgz` | Gzipped TAR archive | Sí |
| TAR.BZ2 | `.tar.bz2`, `.tbz2` | Bzip2 compressed TAR | Sí |
| TAR.XZ | `.tar.xz`, `.txz` | XZ compressed TAR | Sí |
| GZ | `.gz` | Gzip compressed file | Sí |
| BZ2 | `.bz2` | Bzip2 compressed file | Sí |
| XZ | `.xz` | XZ compressed file | Sí |

## 🔧 Configuración

### Niveles de Compresión

- **ZIP**: 0-9 (0=sin compresión, 9=máxima)
- **TAR.GZ**: 1-9 (1=rápida, 9=máxima)
- **TAR.BZ2**: 1-9 (1=rápida, 9=máxima)
- **TAR.XZ**: 0-9 (0=rápida, 9=máxima)
- **GZ/BZ2/XZ**: 1-9 (1=rápida, 9=máxima)

### Opciones Avanzadas

- `include_hidden`: Incluir archivos ocultos (default: false)
- `password`: Contraseña para archivos protegidos
- `overwrite`: Sobrescribir archivos existentes (default: false)
- `max_size`: Tamaño máximo para división (ej: "100MB", "1GB")

## 🎭 SDK Integration

El plugin está completamente integrado con el SDK de Sugar:

### Hooks Registrados
- `before_zip_command`: Antes de ejecutar comandos zip
- `after_zip_command`: Después de ejecutar comandos zip

### Interceptores
- `path_interceptor`: Intercepta y modifica rutas de archivos

### Customizers
- `zip_command_customizer`: Personaliza comandos zip

### Alias
- `zip`: Alias para `zip_compress`
- `unzip`: Alias para `zip_extract`
- `zipinfo`: Alias para `zip_info`
- `ziplist`: Alias para `zip_list`

## 📊 Respuestas

Todas las operaciones devuelven un objeto JSON con:

```json
{
  "status": "success|error",
  "source": "ruta_origen",
  "destination": "ruta_destino",
  "format": "formato_detectado",
  "original_size": 12345,
  "compressed_size": 6789,
  "compression_ratio": 45.2,
  "processing_time": 1.23,
  "files_count": 10,
  "error": "mensaje_error_si_aplica"
}
```

## 🧪 Ejemplos

### Backup Completo
```json
{
  "name": "Backup Completo",
  "task": [
    {
      "zip": {
        "operator": "compress",
        "source": "./datos_proyecto",
        "destination": "./backup_{{Date.now()}}.zip",
        "format": "zip",
        "compression_level": 9,
        "result": "backup"
      }
    },
    {
      "if": {
        "condition": "${backup.status == 'success'}",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Backup creado: {{backup.destination}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### Verificación de Integridad
```json
{
  "name": "Verificar Backup",
  "task": [
    {
      "zip": {
        "operator": "test",
        "source": "./backup.zip",
        "result": "verificacion"
      }
    },
    {
      "if": {
        "condition": "${verificacion.is_valid}",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Archivo válido"
              }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": {
                "text": "❌ Archivo corrupto"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## 🐛 Solución de Problemas

### Errores Comunes

1. **"File not found"**: Verificar que la ruta del archivo sea correcta
2. **"Format not supported"**: Verificar que el formato esté soportado
3. **"Permission denied"**: Verificar permisos de escritura
4. **"Password required"**: Proporcionar contraseña para archivos protegidos

### Logs

El plugin registra información detallada en los logs de Sugar:
- Operaciones de compresión/extracción
- Errores y advertencias
- Estadísticas de rendimiento

## 📈 Rendimiento

- **Compresión**: Optimizada para archivos grandes
- **Memoria**: Uso eficiente de memoria
- **Velocidad**: Procesamiento rápido con múltiples hilos
- **Ratio**: Hasta 98% de compresión en archivos de texto

## 🤝 Contribución

Para contribuir al plugin:

1. Fork del repositorio
2. Crear rama para feature
3. Implementar cambios
4. Ejecutar pruebas
5. Crear Pull Request

## 📄 Licencia

Este plugin está bajo la misma licencia que Sugar Framework.

## 🔗 Enlaces

- [Documentación Sugar](https://sugar-framework.com)
- [Sintaxis JSON](docs/language/zip_syntax_proposal.md)
- [Ejemplos](docs/language/zip_example.json)
- [SDK Documentation](Sugar/Lang/Plugins/SDK/README.md)