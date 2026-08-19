# Extract Table Selenium Plugin

El plugin Extract Table Selenium permite extraer datos de tablas HTML usando Selenium WebDriver para automatización web avanzada.

## Características

- **Extracción de tablas**: Extraer datos de tablas HTML complejas
- **Automatización web**: Usar Selenium WebDriver para navegación
- **Selección dinámica**: Seleccionar elementos usando CSS/XPath
- **Manejo de JavaScript**: Extraer datos de contenido dinámico
- **Filtros avanzados**: Filtrar y procesar datos extraídos
- **Exportación**: Exportar datos en múltiples formatos

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `selenium>=4.0.0`
- `webdriver-manager>=3.8.0`
- `pandas>=1.3.0`
- `beautifulsoup4>=4.9.0`

## Uso

### 1. Extracción Básica de Tabla

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data-table",
    "result": "table_data"
  }
}
```

### 2. Extracción con Configuración Avanzada

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table#main-table",
    "wait_time": 10,
    "headless": true,
    "columns": ["Nombre", "Edad", "Ciudad"],
    "result": "filtered_data"
  }
}
```

### 3. Extracción de Tabla Dinámica

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/dynamic-table",
    "table_selector": "table.dynamic-content",
    "wait_for": "table.dynamic-content tbody tr",
    "scroll_to_load": true,
    "max_rows": 100,
    "result": "dynamic_data"
  }
}
```

### 4. Extracción con Filtros

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data-table",
    "filters": {
      "column": "Estado",
      "value": "Activo",
      "operator": "equals"
    },
    "sort_by": "Fecha",
    "sort_order": "desc",
    "result": "filtered_table"
  }
}
```

### 5. Extracción de Múltiples Tablas

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/multiple-tables",
    "table_selectors": [
      "table#table1",
      "table#table2",
      "table#table3"
    ],
    "result": "all_tables"
  }
}
```

## Parámetros

### Configuración Básica
- `url` (string, requerido): URL de la página web
- `table_selector` (string, opcional): Selector CSS/XPath de la tabla
- `table_selectors` (array, opcional): Múltiples selectores de tabla
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Selenium
- `headless` (boolean, opcional): Modo headless (default: false)
- `wait_time` (integer, opcional): Tiempo de espera en segundos
- `wait_for` (string, opcional): Elemento a esperar antes de extraer
- `scroll_to_load` (boolean, opcional): Scroll para cargar contenido

### Configuración de Extracción
- `columns` (array, opcional): Columnas específicas a extraer
- `max_rows` (integer, opcional): Número máximo de filas
- `include_headers` (boolean, opcional): Incluir encabezados (default: true)
- `skip_empty_rows` (boolean, opcional): Saltar filas vacías (default: true)

### Filtros y Ordenamiento
- `filters` (object, opcional): Filtros a aplicar
- `sort_by` (string, opcional): Columna para ordenar
- `sort_order` (string, opcional): Orden (asc/desc)

### Configuración de Salida
- `output_format` (string, opcional): Formato de salida (json, csv, excel)
- `output_file` (string, opcional): Archivo de salida
- `encoding` (string, opcional): Codificación (default: utf-8)

## Operaciones Disponibles

### Extracción de Datos
- **Tabla completa**: Extraer toda la tabla
- **Columnas específicas**: Extraer columnas seleccionadas
- **Filas filtradas**: Extraer filas que cumplan criterios
- **Datos paginados**: Extraer datos de múltiples páginas

### Procesamiento de Datos
- **Limpieza**: Limpiar datos extraídos
- **Transformación**: Transformar formatos de datos
- **Validación**: Validar datos extraídos
- **Enriquecimiento**: Añadir datos adicionales

### Exportación
- **JSON**: Exportar en formato JSON
- **CSV**: Exportar en formato CSV
- **Excel**: Exportar en formato Excel
- **Base de datos**: Insertar en base de datos

## Ejemplos Avanzados

### Extracción de Tabla con Login

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/login",
    "login": {
      "username_selector": "#username",
      "password_selector": "#password",
      "submit_selector": "#login-btn",
      "username": "{{ user }}",
      "password": "{{ pass }}"
    },
    "table_selector": "table.secure-data",
    "result": "secure_table"
  }
}
```

### Extracción con Captcha Handling

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/protected-table",
    "captcha": {
      "enabled": true,
      "manual_solve": true,
      "timeout": 60
    },
    "table_selector": "table.protected",
    "result": "captcha_table"
  }
}
```

### Extracción de Tabla con JavaScript

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/js-table",
    "javascript": [
      "document.querySelector('#load-more').click()",
      "await new Promise(resolve => setTimeout(resolve, 2000))"
    ],
    "table_selector": "table.js-generated",
    "result": "js_table"
  }
}
```

### Extracción con Proxy

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "proxy": {
      "host": "proxy.example.com",
      "port": 8080,
      "username": "{{ proxy_user }}",
      "password": "{{ proxy_pass }}"
    },
    "table_selector": "table.data",
    "result": "proxied_table"
  }
}
```

### Extracción de Tabla Responsive

```json
{
  "extract_table_selenium": {
    "url": "https://example.com/responsive-table",
    "responsive": {
      "enabled": true,
      "mobile_view": false,
      "screen_width": 1920,
      "screen_height": 1080
    },
    "table_selector": "table.responsive",
    "result": "responsive_table"
  }
}
```

## Configuración de Navegador

### Opciones de Chrome
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "browser_options": {
      "chrome": {
        "headless": true,
        "no_sandbox": true,
        "disable_dev_shm_usage": true,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      }
    },
    "table_selector": "table.data",
    "result": "chrome_table"
  }
}
```

### Opciones de Firefox
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "browser_options": {
      "firefox": {
        "headless": true,
        "marionette": true,
        "preferences": {
          "dom.webdriver.enabled": false
        }
      }
    },
    "table_selector": "table.data",
    "result": "firefox_table"
  }
}
```

## Manejo de Errores

### Configuración de Reintentos
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data",
    "error_handling": {
      "retry_count": 3,
      "retry_delay": 5,
      "continue_on_error": true,
      "log_errors": true
    },
    "result": "robust_table"
  }
}
```

### Validación de Datos
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data",
    "validation": {
      "required_columns": ["ID", "Nombre", "Email"],
      "min_rows": 1,
      "max_rows": 1000,
      "data_types": {
        "ID": "integer",
        "Nombre": "string",
        "Email": "email"
      }
    },
    "result": "validated_table"
  }
}
```

## Optimización

### Configuración de Rendimiento
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data",
    "performance": {
      "page_load_strategy": "eager",
      "implicit_wait": 10,
      "explicit_wait": 30,
      "timeout": 60
    },
    "result": "fast_table"
  }
}
```

### Configuración de Memoria
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data",
    "memory": {
      "chunk_size": 1000,
      "stream_processing": true,
      "clear_cache": true
    },
    "result": "memory_efficient_table"
  }
}
```

## Configuración de Seguridad

### Configuración Segura
```json
{
  "extract_table_selenium": {
    "url": "https://example.com/table",
    "table_selector": "table.data",
    "security": {
      "disable_images": true,
      "disable_javascript": false,
      "disable_css": true,
      "user_agent": "Sugar Bot 1.0"
    },
    "result": "secure_table"
  }
}
```

## Recursos Adicionales

- [Documentación de Selenium](https://selenium-python.readthedocs.io/)
- [Guía de Web Scraping](../../../docs/development/web_automation.md) 