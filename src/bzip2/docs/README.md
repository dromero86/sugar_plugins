# Plugin Bzip2 para Sugar

## Descripción

El plugin Bzip2 para Sugar proporciona funcionalidades completas de compresión y descompresión usando el algoritmo bzip2. Este plugin está diseñado para integrarse perfectamente con el sistema de plugins de Sugar y utiliza el SDK para proporcionar funcionalidades avanzadas.

## Características

- **Compresión y descompresión**: Soporte completo para archivos bzip2
- **Integración SDK**: Utiliza el SDK de Sugar para hooks, interceptores y customización
- **Verificación de integridad**: Pruebas de integridad de archivos comprimidos
- **Conversión de formatos**: Conversión entre diferentes formatos de compresión
- **División y combinación**: Dividir archivos grandes y combinar múltiples archivos
- **Gestión de dependencias**: Verificación automática de dependencias
- **Optimización automática**: Selección automática del nivel de compresión óptimo

## Comandos Disponibles

### bzip2_compress
Comprime un archivo usando bzip2.

```json
{
  "bzip2": {
    "operator": "bzip2_compress",
    "source": "archivo.txt",
    "destination": "archivo.txt.bz2",
    "compression_level": 6,
    "result": "compression_result"
  }
}
```

**Parámetros:**
- `source`: Archivo fuente a comprimir
- `destination`: Archivo de destino comprimido
- `compression_level`: Nivel de compresión (1-9, por defecto 6)
- `result`: Variable para almacenar el resultado

### bzip2_decompress
Descomprime un archivo bzip2.

```json
{
  "bzip2": {
    "operator": "bzip2_decompress",
    "source": "archivo.txt.bz2",
    "destination": "archivo.txt",
    "result": "decompression_result"
  }
}
```

**Parámetros:**
- `source`: Archivo bzip2 a descomprimir
- `destination`: Archivo de destino descomprimido
- `result`: Variable para almacenar el resultado

### bzip2_info
Obtiene información sobre un archivo bzip2.

```json
{
  "bzip2": {
    "operator": "bzip2_info",
    "source": "archivo.txt.bz2",
    "result": "file_info"
  }
}
```

### bzip2_test
Prueba la integridad de un archivo bzip2.

```json
{
  "bzip2": {
    "operator": "bzip2_test",
    "source": "archivo.txt.bz2",
    "result": "test_result"
  }
}
```

### bzip2_convert
Convierte entre formatos de compresión.

```json
{
  "bzip2": {
    "operator": "bzip2_convert",
    "source": "archivo.gz",
    "destination": "archivo.bz2",
    "target_format": "bz2",
    "compression_level": 6,
    "result": "conversion_result"
  }
}
```

### bzip2_merge
Combina múltiples archivos en uno solo comprimido.

```json
{
  "bzip2": {
    "operator": "bzip2_merge",
    "sources": ["archivo1.txt", "archivo2.txt", "archivo3.txt"],
    "destination": "combinado.bz2",
    "compression_level": 6,
    "result": "merge_result"
  }
}
```

### bzip2_split
Divide un archivo bzip2 en partes más pequeñas.

```json
{
  "bzip2": {
    "operator": "bzip2_split",
    "source": "archivo_grande.bz2",
    "destination_dir": "./partes",
    "chunk_size": 1048576,
    "compression_level": 6,
    "result": "split_result"
  }
}
```

### sdk_info
Obtiene información sobre el SDK y el plugin.

```json
{
  "bzip2": {
    "operator": "sdk_info",
    "result": "sdk_info"
  }
}
```

### test_sdk
Prueba las funcionalidades del SDK.

```json
{
  "bzip2": {
    "operator": "test_sdk",
    "result": "sdk_test_result"
  }
}
```

## Niveles de Compresión

El plugin bzip2 soporta niveles de compresión del 1 al 9:

- **Nivel 1-3**: Compresión rápida, archivos más grandes
- **Nivel 4-6**: Balance entre velocidad y tamaño (recomendado)
- **Nivel 7-9**: Compresión máxima, más lenta

## Ejemplos de Uso

### Compresión Básica
```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_compress",
        "source": "datos.txt",
        "destination": "datos.txt.bz2",
        "result": "resultado"
      }
    },
    {
      "print": { "text": "Compresión completada: {{resultado.compression_ratio}}% reducción" }
    }
  ]
}
```

### Descompresión con Verificación
```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_test",
        "source": "archivo.bz2",
        "result": "test_result"
      }
    },
    {
      "if": {
        "condition": "${test_result.is_valid} == true",
        "then": {
          "task": [
            {
              "bzip2": {
                "operator": "bzip2_decompress",
                "source": "archivo.bz2",
                "destination": "archivo.txt"
              }
            },
            {
              "print": { "text": "Descompresión exitosa" }
            }
          ]
        },
        "else": {
          "print": { "text": "Archivo corrupto: {{test_result.error}}" }
        }
      }
    }
  ]
}
```

### Conversión de Formatos
```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_convert",
        "source": "archivo.gz",
        "destination": "archivo.bz2",
        "target_format": "bz2",
        "compression_level": 8,
        "result": "conversion"
      }
    },
    {
      "print": { "text": "Conversión completada en {{conversion.processing_time}} segundos" }
    }
  ]
}
```

## Dependencias

### Dependencias de Python
- `bz2`: Biblioteca estándar de Python (incluida)

### Dependencias del Sistema
- `bzip2`: Utilidad de línea de comandos (opcional)

### Requerimientos de Hardware
- RAM mínima: 1 GB
- Disco mínimo: 0.5 GB
- CPU mínima: 1 núcleo

## Instalación

El plugin se instala automáticamente con Sugar. Para verificar la instalación:

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "sdk_info",
        "result": "info"
      }
    },
    {
      "print": { "text": "Plugin bzip2 versión: {{info.version}}" }
    }
  ]
}
```

## Troubleshooting

### Error: "Source file does not exist"
Verificar que el archivo fuente existe y la ruta es correcta.

### Error: "Invalid bzip2 parameters"
Verificar que todos los parámetros requeridos están presentes.

### Error: "Error during compression"
Verificar permisos de escritura en el directorio de destino.

### Rendimiento lento
- Usar niveles de compresión más bajos (1-3) para archivos grandes
- Verificar espacio disponible en disco
- Considerar usar SSD para mejor rendimiento

## Integración con SDK

El plugin utiliza completamente el SDK de Sugar:

- **Hooks**: Intercepta comandos antes y después de la ejecución
- **Interceptores**: Maneja interpolación de variables de rutas
- **Customizadores**: Personaliza comandos automáticamente
- **Extensiones**: Registra funcionalidades extendidas

## Licencia

MIT License - Ver archivo LICENSE para más detalles.
