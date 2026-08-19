# Plugin Bzip2 para Sugar

[![Sugar Plugin](https://img.shields.io/badge/Sugar-Plugin-blue.svg)](https://sugar-lang.org)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/sugar-lang/plugins)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Plugin completo para compresión y descompresión de archivos usando el algoritmo bzip2 con integración completa del SDK de Sugar.

## 🚀 Características

- **Compresión y descompresión** de archivos individuales y directorios
- **Integración completa con el SDK** de Sugar (hooks, interceptores, customizadores)
- **Verificación de integridad** de archivos comprimidos
- **Conversión entre formatos** de compresión
- **División y combinación** de archivos grandes
- **Gestión automática de dependencias** y verificación de sistema
- **Optimización automática** del nivel de compresión
- **Soporte para múltiples niveles** de compresión (1-9)

## 📦 Instalación

El plugin se instala automáticamente con Sugar. No requiere dependencias externas ya que `bz2` es parte de la biblioteca estándar de Python.

### Verificar instalación

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

## 🎯 Uso Rápido

### Compresión básica

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_compress",
        "source": "datos.txt",
        "destination": "datos.txt.bz2",
        "compression_level": 6,
        "result": "resultado"
      }
    },
    {
      "print": { "text": "Compresión completada: {{resultado.compression_ratio}}% reducción" }
    }
  ]
}
```

### Descompresión

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_decompress",
        "source": "datos.txt.bz2",
        "destination": "datos.txt",
        "result": "resultado"
      }
    }
  ]
}
```

## 🔧 Comandos Disponibles

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `bzip2_compress` | Comprimir archivo | `source`, `destination`, `compression_level` |
| `bzip2_decompress` | Descomprimir archivo | `source`, `destination` |
| `bzip2_info` | Información del archivo | `source` |
| `bzip2_test` | Probar integridad | `source` |
| `bzip2_convert` | Convertir formato | `source`, `destination`, `target_format` |
| `bzip2_merge` | Combinar archivos | `sources`, `destination` |
| `bzip2_split` | Dividir archivo | `source`, `destination_dir`, `chunk_size` |
| `sdk_info` | Información del SDK | - |
| `test_sdk` | Probar SDK | - |

## 📊 Niveles de Compresión

- **Nivel 1-3**: Compresión rápida, archivos más grandes
- **Nivel 4-6**: Balance entre velocidad y tamaño ⭐ **Recomendado**
- **Nivel 7-9**: Compresión máxima, más lenta

## 🔄 Ejemplos Avanzados

### Compresión con verificación

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_compress",
        "source": "archivo.txt",
        "destination": "archivo.txt.bz2",
        "compression_level": 8,
        "result": "compression_result"
      }
    },
    {
      "bzip2": {
        "operator": "bzip2_test",
        "source": "archivo.txt.bz2",
        "result": "test_result"
      }
    },
    {
      "if": {
        "condition": "${test_result.is_valid} == true",
        "then": {
          "print": { "text": "✅ Compresión exitosa y verificada" }
        },
        "else": {
          "print": { "text": "❌ Error en la compresión" }
        }
      }
    }
  ]
}
```

### Conversión de formatos

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_convert",
        "source": "archivo.gz",
        "destination": "archivo.bz2",
        "target_format": "bz2",
        "compression_level": 6,
        "result": "conversion"
      }
    },
    {
      "print": { "text": "Conversión completada en {{conversion.processing_time}} segundos" }
    }
  ]
}
```

### División de archivos grandes

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "bzip2_split",
        "source": "archivo_grande.bz2",
        "destination_dir": "./partes",
        "chunk_size": 1048576,
        "compression_level": 6,
        "result": "split_result"
      }
    },
    {
      "print": { "text": "Archivo dividido en {{split_result.total_chunks}} partes" }
    }
  ]
}
```

## 🛠️ Integración con SDK

El plugin utiliza completamente el SDK de Sugar:

### Hooks
- Intercepta comandos antes y después de la ejecución
- Valida parámetros automáticamente
- Agrega información de contexto

### Interceptores
- Maneja interpolación de variables de rutas
- Expande rutas relativas automáticamente

### Customizadores
- Personaliza comandos automáticamente
- Establece valores por defecto
- Valida niveles de compresión

### Extensiones
- Registra funcionalidades extendidas
- Proporciona callbacks personalizados

## 📋 Dependencias

### Dependencias de Python
- `bz2`: Biblioteca estándar de Python ✅

### Dependencias del Sistema
- `bzip2`: Utilidad de línea de comandos (opcional)

### Requerimientos de Hardware
- RAM mínima: 1 GB
- Disco mínimo: 0.5 GB
- CPU mínima: 1 núcleo

## 🧪 Testing

### Probar funcionalidades del SDK

```json
{
  "task": [
    {
      "bzip2": {
        "operator": "test_sdk",
        "result": "sdk_test"
      }
    },
    {
      "print": { "text": "Resultados de tests: {{sdk_test.tests}}" }
    }
  ]
}
```

### Verificar dependencias

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
      "print": { "text": "Estado de dependencias: {{info.dependency_status}}" }
    }
  ]
}
```

## 🚨 Troubleshooting

### Problemas Comunes

| Error | Solución |
|-------|----------|
| "Source file does not exist" | Verificar que el archivo existe y la ruta es correcta |
| "Invalid bzip2 parameters" | Verificar que todos los parámetros requeridos están presentes |
| "Error during compression" | Verificar permisos de escritura en el directorio de destino |
| Rendimiento lento | Usar niveles de compresión más bajos (1-3) para archivos grandes |

### Optimización de Rendimiento

- **Archivos pequeños (< 1MB)**: Usar nivel 9 para máxima compresión
- **Archivos medianos (1-10MB)**: Usar nivel 6-8 para balance
- **Archivos grandes (> 10MB)**: Usar nivel 1-3 para velocidad
- **Archivos binarios**: Usar niveles 5-6 (menos efectivo que texto)

## 📚 Documentación Completa

Para documentación detallada, ver [docs/README.md](docs/README.md).

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces

- [Documentación de Sugar](https://sugar-lang.org/docs)
- [Sistema de Plugins](https://sugar-lang.org/docs/plugins)
- [SDK de Plugins](https://sugar-lang.org/docs/plugins/sdk)
- [Repositorio de Plugins](https://github.com/sugar-lang/plugins)

---

**Desarrollado con ❤️ por el equipo de Sugar**
