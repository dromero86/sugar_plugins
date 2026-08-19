# PDF Plugin para Sugar

Plugin completo para manipulación de documentos PDF en Sugar. Incluye lectura, escritura, extracción de texto e imágenes, manipulación de metadatos y operaciones avanzadas de transformación.

## Características

### 📖 Lectura y Análisis
- **Lectura de PDFs**: Información básica y detallada
- **Extracción de texto**: Texto completo o por páginas específicas
- **Extracción de imágenes**: Todas las imágenes del documento
- **Análisis de contenido**: Estadísticas y metadatos
- **Búsqueda de texto**: Búsqueda con contexto

### ✍️ Escritura y Creación
- **Creación de PDFs**: Desde cero con contenido personalizado
- **Escritura de PDFs**: Modificación y guardado
- **Combinación de PDFs**: Merge de múltiples archivos
- **División de PDFs**: Split por páginas

### 🔧 Manipulación
- **Agregar texto**: Texto en posiciones específicas
- **Agregar imágenes**: Imágenes en posiciones específicas
- **Metadatos**: Lectura y escritura de metadatos
- **Información de páginas**: Detalles por página

### 🛠️ Utilidades
- **Verificación de dependencias**: Estado de librerías
- **Información del sistema**: Recursos disponibles
- **Testing**: Pruebas de funcionalidad

## Instalación

### Dependencias Requeridas

```bash
pip install PyPDF2>=3.0.0 pdfplumber>=0.9.0 reportlab>=4.0.0 Pillow>=10.0.0
```

### Instalación del Plugin

```bash
# Desde el directorio del plugin
pip install -e .

# O usando sugarize
sugarize require pdf ^1.0.0
```

## Comandos Disponibles

### Comandos de Lectura

#### `read_pdf`
Lee un archivo PDF y retorna información básica.

```json
{
  "pdf": {
    "operator": "read_pdf",
    "file_path": "documento.pdf",
    "result": "pdf_info"
  }
}
```

#### `extract_text`
Extrae texto del PDF.

```json
{
  "pdf": {
    "operator": "extract_text",
    "file_path": "documento.pdf",
    "pages": "all",
    "output_file": "texto_extraido.txt",
    "result": "texto_extraido"
  }
}
```

#### `extract_images`
Extrae imágenes del PDF.

```json
{
  "pdf": {
    "operator": "extract_images",
    "file_path": "documento.pdf",
    "output_dir": "./imagenes",
    "result": "imagenes_extraidas"
  }
}
```

### Comandos de Escritura

#### `create_pdf`
Crea un nuevo PDF desde cero.

```json
{
  "pdf": {
    "operator": "create_pdf",
    "output_path": "nuevo_documento.pdf",
    "title": "Mi Documento",
    "content": [
      {
        "type": "text",
        "text": "Este es un documento creado con Sugar PDF Plugin",
        "font_size": 14
      },
      {
        "type": "table",
        "data": [
          ["Columna 1", "Columna 2"],
          ["Dato 1", "Dato 2"]
        ]
      }
    ],
    "result": "pdf_creado"
  }
}
```

#### `merge_pdfs`
Combina múltiples PDFs.

```json
{
  "pdf": {
    "operator": "merge_pdfs",
    "input_files": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    "output_path": "combinado.pdf",
    "result": "pdf_combinado"
  }
}
```

#### `split_pdf`
Divide un PDF en múltiples archivos.

```json
{
  "pdf": {
    "operator": "split_pdf",
    "input_path": "documento.pdf",
    "output_dir": "./paginas",
    "pages_per_file": 1,
    "result": "pdf_dividido"
  }
}
```

### Comandos de Manipulación

#### `add_text`
Agrega texto a un PDF existente.

```json
{
  "pdf": {
    "operator": "add_text",
    "input_path": "documento.pdf",
    "output_path": "documento_con_texto.pdf",
    "text": "Texto agregado",
    "page_number": 1,
    "x": 100,
    "y": 100,
    "font_size": 12,
    "result": "pdf_modificado"
  }
}
```

#### `add_image`
Agrega una imagen a un PDF existente.

```json
{
  "pdf": {
    "operator": "add_image",
    "input_path": "documento.pdf",
    "output_path": "documento_con_imagen.pdf",
    "image_path": "imagen.png",
    "page_number": 1,
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 200,
    "result": "pdf_modificado"
  }
}
```

### Comandos de Metadatos

#### `get_metadata`
Obtiene metadatos del PDF.

```json
{
  "pdf": {
    "operator": "get_metadata",
    "file_path": "documento.pdf",
    "result": "metadatos"
  }
}
```

#### `set_metadata`
Establece metadatos en el PDF.

```json
{
  "pdf": {
    "operator": "set_metadata",
    "input_path": "documento.pdf",
    "output_path": "documento_con_metadatos.pdf",
    "metadata": {
      "Title": "Mi Documento",
      "Author": "Sugar Team",
      "Subject": "Documento de prueba"
    },
    "result": "pdf_con_metadatos"
  }
}
```

### Comandos de Análisis

#### `analyze_pdf`
Analiza el contenido del PDF.

```json
{
  "pdf": {
    "operator": "analyze_pdf",
    "file_path": "documento.pdf",
    "result": "analisis"
  }
}
```

#### `search_text`
Busca texto en el PDF.

```json
{
  "pdf": {
    "operator": "search_text",
    "file_path": "documento.pdf",
    "search_term": "palabra",
    "case_sensitive": false,
    "result": "resultados_busqueda"
  }
}
```

### Comandos de Utilidad

#### `check_dependencies`
Verifica el estado de las dependencias.

```json
{
  "pdf": {
    "operator": "check_dependencies",
    "result": "estado_dependencias"
  }
}
```

#### `system_info`
Proporciona información del sistema.

```json
{
  "pdf": {
    "operator": "system_info",
    "result": "info_sistema"
  }
}
```

#### `test_functionality`
Prueba la funcionalidad del plugin.

```json
{
  "pdf": {
    "operator": "test_functionality",
    "result": "resultados_prueba"
  }
}
```

## Ejemplos de Uso

### Ejemplo 1: Análisis Completo de un PDF

```json
{
  "task": [
    {
      "pdf": {
        "operator": "read_pdf",
        "file_path": "documento.pdf",
        "result": "info_basica"
      }
    },
    {
      "pdf": {
        "operator": "extract_text",
        "file_path": "documento.pdf",
        "result": "texto_completo"
      }
    },
    {
      "pdf": {
        "operator": "analyze_pdf",
        "file_path": "documento.pdf",
        "result": "analisis_completo"
      }
    },
    {
      "print": {
        "text": "PDF analizado: {{info_basica.page_count}} páginas, {{analisis_completo.total_text_length}} caracteres"
      }
    }
  ]
}
```

### Ejemplo 2: Creación de un Reporte PDF

```json
{
  "task": [
    {
      "pdf": {
        "operator": "create_pdf",
        "output_path": "reporte.pdf",
        "title": "Reporte de Sistema",
        "content": [
          {
            "type": "text",
            "text": "Reporte Generado Automáticamente",
            "font_size": 16
          },
          {
            "type": "table",
            "data": [
              ["Métrica", "Valor"],
              ["Páginas", "5"],
              ["Tamaño", "2.5 MB"],
              ["Fecha", "2024-01-15"]
            ]
          }
        ],
        "result": "reporte_creado"
      }
    },
    {
      "print": {
        "text": "Reporte creado: {{reporte_creado.output_path}}"
      }
    }
  ]
}
```

### Ejemplo 3: Procesamiento de Múltiples PDFs

```json
{
  "task": [
    {
      "pdf": {
        "operator": "merge_pdfs",
        "input_files": ["capitulo1.pdf", "capitulo2.pdf", "capitulo3.pdf"],
        "output_path": "libro_completo.pdf",
        "result": "libro_mergeado"
      }
    },
    {
      "pdf": {
        "operator": "set_metadata",
        "input_path": "libro_completo.pdf",
        "output_path": "libro_final.pdf",
        "metadata": {
          "Title": "Libro Completo",
          "Author": "Autor del Libro",
          "Subject": "Contenido del libro"
        },
        "result": "libro_final"
      }
    },
    {
      "print": {
        "text": "Libro procesado: {{libro_final.output_path}} con {{libro_mergeado.total_pages}} páginas"
      }
    }
  ]
}
```

## Configuración

### Configuración del Plugin

```python
plugin_config = {
    'default_page_size': 'A4',  # A4, LETTER, etc.
    'default_font_size': 12,
    'temp_dir': '/tmp/sugar_pdf',
    'max_file_size_mb': 100
}
```

### Variables de Entorno

```bash
# Directorio temporal para archivos PDF
export SUGAR_PDF_TEMP_DIR="/tmp/sugar_pdf"

# Tamaño máximo de archivo (MB)
export SUGAR_PDF_MAX_SIZE="100"
```

## Manejo de Errores

### Errores Comunes

1. **Dependencias faltantes**: Ejecutar `check_dependencies` para verificar
2. **Archivo no encontrado**: Verificar ruta del archivo
3. **PDF corrupto**: Verificar integridad del archivo
4. **Permisos insuficientes**: Verificar permisos de escritura

### Ejemplo de Manejo de Errores

```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "pdf": {
              "operator": "read_pdf",
              "file_path": "archivo_inexistente.pdf",
              "result": "info"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": {
              "text": "Error al leer PDF: {{error}}"
            }
          }
        ]
      }
    }
  ]
}
```

## Limitaciones

- **Tamaño de archivo**: Limitado por memoria disponible
- **PDFs encriptados**: Requieren contraseña
- **PDFs con DRM**: Pueden tener restricciones
- **Imágenes complejas**: Algunas pueden no extraerse correctamente

## Contribución

Para contribuir al desarrollo del plugin:

1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Implementar cambios con tests
4. Enviar pull request

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Soporte

Para soporte técnico:

- Crear issue en el repositorio
- Consultar documentación en `/docs/`
- Revisar ejemplos en `/examples/`