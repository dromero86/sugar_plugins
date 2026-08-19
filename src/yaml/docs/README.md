# YAML Plugin para Sugar Language

## Descripción

El plugin YAML proporciona soporte completo para archivos YAML en Sugar Language, permitiendo escribir scripts de Sugar usando la sintaxis más legible y flexible de YAML, manteniendo toda la funcionalidad existente.

## Características

- ✅ **Sintaxis YAML completa**: Soporte para todas las características de YAML
- ✅ **Compatibilidad total**: Misma funcionalidad que JSON
- ✅ **Anclajes y referencias**: Reutilización de configuraciones
- ✅ **Comentarios**: Documentación inline en los archivos
- ✅ **Tipos de datos**: Soporte para todos los tipos de YAML
- ✅ **Plugins**: Compatibilidad completa con el sistema de plugins
- ✅ **Detección automática**: Archivos `.yml` y `.yaml` se detectan automáticamente
- ✅ **Conversión JSON → YAML**: Herramientas de migración
- ✅ **Validación**: Verificación de sintaxis YAML

## Instalación

### Dependencias

El plugin requiere la librería **PyYAML**:

```bash
pip install pyyaml
```

### Verificación de dependencias

```json
{
  "task": [
    {
      "yaml": {
        "operator": "check_dependencies",
        "result": "dependency_status"
      }
    },
    {
      "if": {
        "condition": "${dependency_status.all_satisfied} == true",
        "then": {
          "task": [
            {
              "print": { "text": "✅ YAML Plugin listo para usar" }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": { "text": "❌ Instala PyYAML: pip install pyyaml" }
            }
          ]
        }
      }
    }
  ]
}
```

## Uso

### Comandos Disponibles

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `process_file` | Procesa un archivo YAML | `file_path` |
| `convert_json_to_yaml` | Convierte JSON a YAML | `json_file`, `yaml_file` (opcional), `pretty` (opcional) |
| `validate_yaml` | Valida archivo YAML | `yaml_file` |
| `convert_directory` | Convierte directorio completo | `input_dir`, `output_dir` (opcional), `recursive` (opcional) |
| `register_cli` | Registra parámetros CLI | Ninguno |

### Procesamiento de Archivos YAML

```json
{
  "task": [
    {
      "yaml": {
        "operator": "process_file",
        "file_path": "script.yaml",
        "result": "processing_result"
      }
    },
    {
      "print": { "text": "{{processing_result.message}}" }
    }
  ]
}
```

### Conversión JSON a YAML

```json
{
  "task": [
    {
      "yaml": {
        "operator": "convert_json_to_yaml",
        "json_file": "script.json",
        "yaml_file": "script.yaml",
        "pretty": true,
        "result": "conversion_result"
      }
    },
    {
      "print": { "text": "{{conversion_result.message}}" }
    }
  ]
}
```

### Validación de YAML

```json
{
  "task": [
    {
      "yaml": {
        "operator": "validate_yaml",
        "yaml_file": "script.yaml",
        "result": "validation_result"
      }
    },
    {
      "print": { "text": "{{validation_result.message}}" }
    }
  ]
}
```

### Conversión de Directorios

```json
{
  "task": [
    {
      "yaml": {
        "operator": "convert_directory",
        "input_dir": "examples/",
        "output_dir": "examples_yaml/",
        "recursive": true,
        "result": "directory_result"
      }
    },
    {
      "print": { "text": "{{directory_result.message}}" }
    }
  ]
}
```

## Sintaxis YAML

### Estructura básica

```yaml
# Comentarios en YAML
task:
  - print:
      text: "Hola mundo"
  
  - let:
      name: "variable"
      value: "valor"
```

### Comparación JSON vs YAML

**JSON:**
```json
{
  "task": [
    {
      "print": {
        "text": "Hola mundo"
      }
    },
    {
      "let": {
        "name": "variable",
        "value": "valor"
      }
    }
  ]
}
```

**YAML:**
```yaml
task:
  - print:
      text: "Hola mundo"
  
  - let:
      name: "variable"
      value: "valor"
```

### Características avanzadas de YAML

#### Anclajes y referencias

```yaml
# Definir configuración reutilizable
configuracion: &db_config
  host: "localhost"
  port: 5432
  database: "mydb"

task:
  - let:
      name: "db_settings"
      value: "{{configuracion}}"
  
  - print:
      text: "Conectando a {{db_settings.host}}:{{db_settings.port}}"
```

#### Listas y arrays

```yaml
variables:
  features:
    - "YAML"
    - "JSON"
    - "AST"
    - "Plugins"

task:
  - for:
      variable: "feature"
      in: "{{variables.features}}"
      task:
        - print:
            text: "• {{feature}}"
```

#### Tipos de datos

```yaml
task:
  - let:
      name: "string_var"
      value: "Texto"
  
  - let:
      name: "number_var"
      value: 42
  
  - let:
      name: "boolean_var"
      value: true
  
  - let:
      name: "list_var"
      value: "[1, 2, 3, 4, 5]"
  
  - let:
      name: "dict_var"
      value: "{'key': 'value'}"
```

## Ejemplos Prácticos

### Ejemplo básico

```yaml
# examples/basic_hello.yaml
task:
  - print:
      text: "🍬 ¡Hola desde YAML!"
  
  - let:
      name: "mensaje"
      value: "Sugar ahora soporta YAML"
  
  - print:
      text: "{{mensaje}}"
```

### Ejemplo con plugins

```yaml
# examples/plugin_example.yaml
task:
  - simple:
      operator: "hello"
      name: "YAML"
      result: "saludo"
  
  - print:
      text: "{{saludo}}"
  
  - simple:
      operator: "add"
      left: 10
      right: 20
      result: "suma"
  
  - print:
      text: "10 + 20 = {{suma}}"
```

### Ejemplo avanzado

```yaml
# examples/advanced_features.yaml
configuraciones: &db_config
  host: "localhost"
  port: 5432
  database: "mydb"

variables:
  nombre: "Sugar YAML"
  version: "2.0.0"
  features:
    - "Soporte YAML"
    - "Plugins"
    - "AST"

task:
  - let:
      name: "app_name"
      value: "{{variables.nombre}}"
  
  - print:
      text: "🚀 Iniciando {{app_name}} v{{variables.version}}"
  
  - for:
      variable: "feature"
      in: "{{variables.features}}"
      task:
        - print:
            text: "  • {{feature}}"
```

## Ventajas de YAML sobre JSON

### 1. Legibilidad
- **YAML**: Sintaxis más limpia y legible
- **JSON**: Sintaxis más verbosa con llaves y comas

### 2. Comentarios
- **YAML**: Soporte nativo para comentarios
- **JSON**: No soporta comentarios

### 3. Anclajes y referencias
- **YAML**: Reutilización de configuraciones
- **JSON**: Duplicación de código

### 4. Menos verbosidad
- **YAML**: Menos caracteres para la misma funcionalidad
- **JSON**: Más caracteres de sintaxis

### 5. Tipos de datos
- **YAML**: Soporte nativo para tipos de datos
- **JSON**: Limitado a tipos básicos

## Compatibilidad

### Plugins existentes
Todos los plugins existentes funcionan sin modificaciones con archivos YAML:

```yaml
task:
  - ssh:
      operator: "connect"
      host: "192.168.1.100"
      username: "admin"
      password: "secret123"
  
  - request:
      operator: "get"
      url: "https://api.example.com/data"
      result: "response"
  
  - selenium:
      operator: "open_browser"
      browser: "chrome"
```

### Variables e interpolación
La interpolación de variables funciona exactamente igual:

```yaml
task:
  - let:
      name: "api_url"
      value: "https://api.example.com"
  
  - request:
      operator: "get"
      url: "{{api_url}}/users"
      result: "users"
  
  - print:
      text: "Usuarios obtenidos: {{users}}"
```

### Control de flujo
Todas las estructuras de control funcionan:

```yaml
task:
  - if:
      condition: "${users.length} > 0"
      then:
        task:
          - print:
              text: "Hay usuarios disponibles"
      else:
        task:
          - print:
              text: "No hay usuarios"
  
  - for:
      variable: "user"
      in: "{{users}}"
      task:
        - print:
            text: "Usuario: {{user.name}}"
```

## Testing

### Ejecutar pruebas del plugin

```json
{
  "task": [
    {
      "yaml": {
        "operator": "validate_yaml",
        "yaml_file": "examples/basic_hello.yaml",
        "result": "validation_result"
      }
    },
    {
      "if": {
        "condition": "${validation_result.status} == 'success'",
        "then": {
          "task": [
            {
              "print": { "text": "✅ Archivo YAML válido" }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": { "text": "❌ Archivo YAML inválido" }
            }
          ]
        }
      }
    }
  ]
}
```

### Verificar sintaxis

```bash
# Verificar que un archivo YAML es válido
python3 -c "import yaml; yaml.safe_load(open('script.yaml'))"
```

## Mejores prácticas

### 1. Usar comentarios
```yaml
# Configuración de la aplicación
app_config:
  name: "Mi App"
  version: "1.0.0"
  debug: true

# Tareas principales
task:
  - print:
      text: "Iniciando {{app_config.name}}"
```

### 2. Organizar configuraciones
```yaml
# Configuraciones reutilizables
database: &db_config
  host: "localhost"
  port: 5432

api: &api_config
  base_url: "https://api.example.com"
  timeout: 30

# Usar configuraciones
task:
  - let:
      name: "db_settings"
      value: "{{database}}"
  
  - let:
      name: "api_settings"
      value: "{{api}}"
```

### 3. Usar tipos de datos apropiados
```yaml
task:
  - let:
      name: "string_value"
      value: "Texto"  # String
  
  - let:
      name: "number_value"
      value: 42       # Número
  
  - let:
      name: "boolean_value"
      value: true     # Booleano
  
  - let:
      name: "list_value"
      value: "[1, 2, 3]"  # Lista como string
```

### 4. Estructurar tareas lógicamente
```yaml
task:
  # 1. Configuración inicial
  - let:
      name: "app_name"
      value: "Mi Aplicación"
  
  # 2. Validaciones
  - if:
      condition: "${app_name} != ''"
      then:
        task:
          - print:
              text: "✅ Configuración válida"
  
  # 3. Lógica principal
  - print:
      text: "🚀 Ejecutando {{app_name}}"
  
  # 4. Limpieza
  - print:
      text: "✅ Proceso completado"
```

## Troubleshooting

### Error: "No module named 'yaml'"
```bash
# Instalar PyYAML
pip install pyyaml

# O desde el entorno virtual
virtual/bin/pip install pyyaml
```

### Error: "Invalid YAML syntax"
- Verificar la indentación (YAML es sensible a espacios)
- Usar un validador de YAML online
- Verificar que no hay caracteres especiales

### Error: "File not found"
- Verificar la ruta del archivo
- Usar rutas absolutas si es necesario
- Verificar permisos de archivo

### Error: "YAML parsing failed"
- Verificar que el archivo es YAML válido
- Revisar la estructura de datos
- Verificar que los tipos de datos son correctos

## Migración de JSON a YAML

### Herramientas de conversión

```json
{
  "task": [
    {
      "yaml": {
        "operator": "convert_json_to_yaml",
        "json_file": "script.json",
        "yaml_file": "script.yaml",
        "pretty": true,
        "result": "conversion_result"
      }
    },
    {
      "print": { "text": "{{conversion_result.message}}" }
    }
  ]
}
```

### Cambios principales

1. **Eliminar llaves y comas**: YAML no los necesita
2. **Usar indentación**: En lugar de llaves anidadas
3. **Agregar comentarios**: Documentar el código
4. **Usar anclajes**: Para configuraciones reutilizables

## Conclusión

El plugin YAML proporciona una alternativa más legible y flexible a JSON, manteniendo toda la funcionalidad existente. La sintaxis más limpia, el soporte para comentarios y las características avanzadas como anclajes y referencias hacen que YAML sea una excelente opción para scripts de Sugar complejos.

Para comenzar a usar YAML, simplemente crea archivos con extensión `.yaml` o `.yml` y el plugin los detectará automáticamente.