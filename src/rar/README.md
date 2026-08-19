# Plugin RAR para Sugar

Plugin completo para compresión y descompresión de archivos RAR usando el SDK de Sugar.

## Características

- ✅ **Compresión RAR**: Crear archivos RAR con múltiples opciones
- ✅ **Descompresión RAR**: Extraer archivos RAR con soporte de contraseñas
- ✅ **Información de archivos**: Obtener detalles de archivos RAR
- ✅ **Listado de contenido**: Ver contenido de archivos RAR
- ✅ **Prueba de integridad**: Verificar integridad de archivos RAR
- ✅ **Conversión de formatos**: Convertir entre diferentes formatos
- ✅ **Combinación de archivos**: Fusionar múltiples archivos RAR
- ✅ **División de archivos**: Dividir archivos RAR grandes
- ✅ **SDK completo**: Integración con el SDK de Sugar
- ✅ **Sistema de dependencias**: Verificación automática de dependencias
- ✅ **Manejo de errores**: Sistema robusto de manejo de errores

## Instalación

### Dependencias del Sistema

El plugin requiere herramientas del sistema para manejar archivos RAR:

#### Ubuntu/Debian:
```bash
sudo apt-get install unrar
```

#### CentOS/RHEL/Fedora:
```bash
sudo yum install unrar
# o
sudo dnf install unrar
```

#### macOS:
```bash
brew install unrar
```

#### Windows:
Descargar e instalar WinRAR desde https://www.win-rar.com/ o instalar unrar desde https://www.win-rar.com/unrar.html

### Instalación del Plugin

```bash
# Desde el directorio del plugin
pip install .

# O instalar dependencias manualmente
pip install rarfile>=4.0 psutil>=5.8.0
```

## Uso

### Comandos Disponibles

#### 1. Comprimir archivos (`rar_compress`)

```json
{
  "rar": {
    "operator": "rar_compress",
    "source": "./archivos",
    "destination": "./archivo.rar",
    "compression_level": 3,
    "password": "mi_contraseña",
    "include_hidden": false,
    "result": "compression_result"
  }
}
```

**Parámetros:**
- `source`: Archivo o directorio a comprimir
- `destination`: Archivo RAR de salida
- `compression_level`: Nivel de compresión (0-5, por defecto 3)
- `password`: Contraseña para el archivo (opcional)
- `include_hidden`: Incluir archivos ocultos (por defecto false)
- `result`: Variable para almacenar el resultado

#### 2. Extraer archivos (`rar_extract`)

```json
{
  "rar": {
    "operator": "rar_extract",
    "source": "./archivo.rar",
    "destination": "./extraido",
    "password": "mi_contraseña",
    "overwrite": false,
    "result": "extraction_result"
  }
}
```

**Parámetros:**
- `source`: Archivo RAR a extraer
- `destination`: Directorio de destino
- `password`: Contraseña del archivo (si está protegido)
- `overwrite`: Sobrescribir archivos existentes (por defecto false)
- `result`: Variable para almacenar el resultado

#### 3. Información de archivo (`rar_info`)

```json
{
  "rar": {
    "operator": "rar_info",
    "source": "./archivo.rar",
    "result": "file_info"
  }
}
```

#### 4. Listar contenido (`rar_list`)

```json
{
  "rar": {
    "operator": "rar_list",
    "source": "./archivo.rar",
    "password": "mi_contraseña",
    "result": "file_list"
  }
}
```

#### 5. Probar integridad (`rar_test`)

```json
{
  "rar": {
    "operator": "rar_test",
    "source": "./archivo.rar",
    "password": "mi_contraseña",
    "result": "test_result"
  }
}
```

#### 6. Convertir formato (`rar_convert`)

```json
{
  "rar": {
    "operator": "rar_convert",
    "source": "./archivo.rar",
    "destination": "./archivo.zip",
    "target_format": "zip",
    "result": "conversion_result"
  }
}
```

#### 7. Combinar archivos (`rar_merge`)

```json
{
  "rar": {
    "operator": "rar_merge",
    "sources": ["./archivo1.rar", "./archivo2.rar"],
    "destination": "./combinado.rar",
    "result": "merge_result"
  }
}
```

#### 8. Dividir archivo (`rar_split`)

```json
{
  "rar": {
    "operator": "rar_split",
    "source": "./archivo_grande.rar",
    "destination_dir": "./partes",
    "max_size": 104857600,
    "result": "split_result"
  }
}
```

#### 9. Información del SDK (`sdk_info`)

```json
{
  "rar": {
    "operator": "sdk_info",
    "result": "sdk_info"
  }
}
```

#### 10. Listar formatos (`list_formats`)

```json
{
  "rar": {
    "operator": "list_formats",
    "result": "formats"
  }
}
```

#### 11. Probar SDK (`test_sdk`)

```json
{
  "rar": {
    "operator": "test_sdk",
    "result": "sdk_test"
  }
}
```

#### 12. Verificar dependencias (`check_dependencies`)

```json
{
  "rar": {
    "operator": "check_dependencies",
    "result": "deps_status"
  }
}
```

#### 13. Información del sistema (`system_info`)

```json
{
  "rar": {
    "operator": "system_info",
    "result": "sys_info"
  }
}
```

#### 14. Probar funcionalidad (`test_functionality`)

```json
{
  "rar": {
    "operator": "test_functionality",
    "result": "func_test"
  }
}
```

## Ejemplos Completos

### Ejemplo 1: Compresión básica

```json
{
  "task": [
    {
      "rar": {
        "operator": "rar_compress",
        "source": "./documentos",
        "destination": "./backup.rar",
        "compression_level": 5,
        "result": "compression_result"
      }
    },
    {
      "print": {
        "text": "Compresión completada: {{compression_result.status}}"
      }
    },
    {
      "print": {
        "text": "Tamaño original: {{compression_result.original_size}} bytes"
      }
    },
    {
      "print": {
        "text": "Tamaño comprimido: {{compression_result.compressed_size}} bytes"
      }
    },
    {
      "print": {
        "text": "Ratio de compresión: {{compression_result.compression_ratio}}%"
      }
    }
  ]
}
```

### Ejemplo 2: Extracción con contraseña

```json
{
  "task": [
    {
      "rar": {
        "operator": "rar_extract",
        "source": "./archivo_protegido.rar",
        "destination": "./extraido",
        "password": "mi_contraseña_secreta",
        "result": "extraction_result"
      }
    },
    {
      "if": {
        "condition": "${extraction_result.status} == 'success'",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Extracción exitosa: {{extraction_result.extracted_files}} archivos extraídos"
              }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": {
                "text": "❌ Error en extracción: {{extraction_result.error}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### Ejemplo 3: Verificación de integridad

```json
{
  "task": [
    {
      "rar": {
        "operator": "rar_info",
        "source": "./archivo.rar",
        "result": "file_info"
      }
    },
    {
      "print": {
        "text": "Archivo: {{file_info.file}}"
      }
    },
    {
      "print": {
        "text": "Tamaño: {{file_info.size_human}}"
      }
    },
    {
      "print": {
        "text": "Archivos contenidos: {{file_info.files_count}}"
      }
    },
    {
      "print": {
        "text": "Protegido con contraseña: {{file_info.is_encrypted}}"
      }
    },
    {
      "rar": {
        "operator": "rar_test",
        "source": "./archivo.rar",
        "result": "test_result"
      }
    },
    {
      "if": {
        "condition": "${test_result.is_valid} == true",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Archivo RAR válido"
              }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": {
                "text": "❌ Archivo RAR corrupto o dañado"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### Ejemplo 4: Verificación de dependencias

```json
{
  "task": [
    {
      "rar": {
        "operator": "check_dependencies",
        "result": "deps_status"
      }
    },
    {
      "print": {
        "text": "Estado de dependencias: {{deps_status.all_satisfied}}"
      }
    },
    {
      "if": {
        "condition": "${deps_status.all_satisfied} == false",
        "then": {
          "task": [
            {
              "print": {
                "text": "⚠️ Dependencias faltantes:"
              }
            },
            {
              "for": {
                "variable": "missing_dep",
                "in": "${deps_status.missing_dependencies}",
                "task": [
                  {
                    "print": {
                      "text": "  - {{missing_dep}}"
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    }
  ]
}
```

## SDK y Extensiones

El plugin RAR utiliza el SDK completo de Sugar para proporcionar funcionalidades avanzadas:

### Hooks Registrados
- **Before Command Hook**: Validación de parámetros antes de ejecutar comandos
- **After Command Hook**: Procesamiento de resultados y estadísticas

### Interceptores de Interpolación
- **Path Interpolation**: Expansión automática de rutas relativas

### Customizadores de Comandos
- **Command Customization**: Auto-detección de formatos y configuración por defecto
- **Alias Registration**: Alias para comandos comunes (compress/extract)

### Extensiones del SDK
- **Extension Manager**: Gestión centralizada de extensiones
- **Flow Controller**: Control de flujo de ejecución
- **AST Modifier**: Modificación del árbol de sintaxis abstracta

## Manejo de Errores

El plugin incluye un sistema robusto de manejo de errores:

```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "rar": {
              "operator": "rar_extract",
              "source": "./archivo_inexistente.rar",
              "destination": "./extraido"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": {
              "text": "Error capturado: {{error}}"
            }
          }
        ]
      }
    }
  ]
}
```

## Configuración Avanzada

### Configuración de rarfile

El plugin configura automáticamente rarfile para detectar las herramientas del sistema:

- **Linux/Unix**: Busca `unrar` y `rar` en el PATH
- **Windows**: Configura rutas de WinRAR
- **macOS**: Usa herramientas instaladas via Homebrew

### Personalización de rutas

Si las herramientas no están en el PATH, puedes configurar manualmente:

```python
import rarfile

# Configurar manualmente la ruta de unrar
rarfile.UNRAR_TOOL = "/usr/local/bin/unrar"
```

## Limitaciones

- **Solo lectura**: rarfile solo permite extracción, no creación de archivos RAR
- **Dependencias del sistema**: Requiere herramientas externas (unrar/rar)
- **Formato RAR**: Solo soporta archivos RAR, no otros formatos

## Troubleshooting

### Error: "rarfile.BadRarFile: Failed the read enough data"

**Causa**: Archivo RAR corrupto o herramienta unrar no disponible
**Solución**: 
1. Verificar que unrar esté instalado: `which unrar`
2. Verificar integridad del archivo: `unrar t archivo.rar`

### Error: "rarfile.BadRarFile: File is password protected"

**Causa**: Archivo protegido con contraseña
**Solución**: Proporcionar la contraseña en el parámetro `password`

### Error: "rarfile.BadRarFile: Archive is not RAR"

**Causa**: El archivo no es un archivo RAR válido
**Solución**: Verificar que el archivo sea realmente un archivo RAR

## Contribución

Para contribuir al plugin RAR:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar los cambios
4. Agregar tests
5. Enviar un pull request

## Licencia

Este plugin está licenciado bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## Soporte

Para soporte y preguntas:

- **Issues**: https://github.com/sugar-lang/sugar-rar-plugin/issues
- **Documentación**: https://sugar-lang.org/plugins/rar
- **Comunidad**: https://github.com/sugar-lang/community
