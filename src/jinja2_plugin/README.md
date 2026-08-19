# Jinja2 Plugin para Sugar

Plugin de Jinja2 para Sugar que proporciona capacidades avanzadas de templating directamente integradas en el sistema AST.

## Características

- ✅ **Integración Nativa**: Jinja2 como operador nativo de Sugar
- ✅ **Sintaxis Simple**: `{"jinja2": {"operator": "parser", ...}}`
- ✅ **Filtros Personalizados**: Formateo de moneda, fechas, texto, etc.
- ✅ **Funciones Avanzadas**: Bucles, condicionales, filtros de datos
- ✅ **Validación de Templates**: Detección de errores y análisis de sintaxis
- ✅ **Cache Inteligente**: Optimización de rendimiento automática
- ✅ **Compatibilidad Total**: Funciona con todas las características de Sugar

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r plugins/jinja2/requirements.txt
   ```

2. **Verificar instalación:**
   ```bash
   # Test del plugin
   python test_jinja2_plugin.py
   ```

3. **¡Listo!** Jinja2 ya está disponible como plugin en Sugar.

## Uso Básico

### Plugin de Sugar

Jinja2 está implementado como un plugin de Sugar que se registra automáticamente:

```json
{
  "variables": {
    "titulo": "Bienvenido a Sugar",
    "usuario": {"nombre": "Juan", "edad": 30}
  },
  "task": [
    {
      "jinja2": {
        "operator": "parser",
        "template": "{{ titulo|default('Bienvenido') }}",
        "result": "my_variable_string"
      }
    },
    {
      "print": {
        "text": "Variable procesada: {{my_variable_string}}"
      }
    }
  ]
}
```

## Plugin de Jinja2

### Integración como Plugin

Jinja2 está implementado como un plugin de Sugar que se registra automáticamente en el sistema de plugins. Esto significa que:

- **Se registra automáticamente**: El plugin se carga cuando Sugar inicia
- **Funciona como operador**: Se puede usar directamente en las tareas
- **Máxima compatibilidad**: Se integra perfectamente con el sistema de plugins de Sugar

### Registro en el Sistema

El plugin Jinja2 se registra automáticamente a través del archivo `plugins/jinja2/__init__.py`:

```python
def register_plugin():
    """Register the Jinja2 plugin with Sugar's plugin system"""
    return Jinja2Plugin()
```

### Ventajas del Plugin

1. **Arquitectura Modular**: Sigue las mejores prácticas de Sugar
2. **Fácil Mantenimiento**: Código organizado y separado
3. **Extensibilidad**: Fácil de extender con nuevas funcionalidades
4. **Compatibilidad Total**: Funciona con todas las características de Sugar

## Operadores Disponibles

### 1. `parser` - Procesar Template
```json
{
  "jinja2": {
    "operator": "parser",
    "template": "{{ variable|default('valor por defecto') }}",
    "result": "nombre_variable_resultado"
  }
}
```

**Parámetros:**
- `operator`: "parser" (obligatorio)
- `template`: Template Jinja2 a procesar (obligatorio)
- `result`: Nombre de la variable donde guardar el resultado (obligatorio)

### 2. `validate` - Validar Template
```json
{
  "jinja2": {
    "operator": "validate",
    "template": "{% if condition %}{{variable}}{% endif %}"
  }
}
```

### 3. `info` - Información del Template
```json
{
  "jinja2": {
    "operator": "info",
    "template": "{% for item in items %}{{item.name|upper}}{% endfor %}"
  }
}
```

### 4. `clear_cache` - Limpiar Cache
```json
{
  "jinja2": {
    "operator": "clear_cache"
  }
}
```

## Ejemplos de Uso

### Template Simple
```json
{
  "jinja2": {
    "operator": "parser",
    "template": "Hola {{nombre}}, tienes {{edad}} años",
    "result": "saludo"
  }
}
```

### Template con Condicionales
```json
{
  "jinja2": {
    "operator": "parser",
    "template": "{% if edad >= 18 %}{{nombre}} es mayor de edad{% else %}{{nombre}} es menor{% endif %}",
    "result": "estado_edad"
  }
}
```

### Template con Bucles
```json
{
  "jinja2": {
    "operator": "parser",
    "template": "{% for item in items %}- {{item.nombre}}: {{item.precio|format_currency}}\n{% endfor %}",
    "result": "lista_items"
  }
}
```

### Template Complejo
```json
{
  "jinja2": {
    "operator": "parser",
    "template": "{% if users %}{{users|length}} usuarios:\n{% for user in users %}- {{user.name|upper}} ({{user.age}} años){% if user.is_admin %} [ADMIN]{% endif %}\n{% endfor %}{% else %}No hay usuarios{% endif %}",
    "result": "reporte_usuarios"
  }
}
```

## Filtros Personalizados

### Filtros de Formateo
- `format_currency`: Formatea valores como moneda
- `format_date`: Formatea fechas
- `format_datetime`: Formatea fechas y horas
- `percentage`: Convierte decimal a porcentaje
- `truncate`: Trunca texto a longitud específica

### Filtros de Datos
- `sum`: Suma valores o atributos de listas
- `map`: Mapea atributos de objetos
- `selectattr`: Filtra objetos por atributo
- `unique`: Elimina duplicados
- `sort`: Ordena listas
- `slice`: Corta listas

### Filtros de Texto
- `upper`, `lower`, `title`, `capitalize`
- `replace`, `split`, `join`
- `strip`, `lstrip`, `rstrip`

### Ejemplos de Filtros

```python
# Formateo de moneda
"{{price|format_currency}}"  # €1,234.56

# Formateo de fecha
"{{date|format_date}}"  # 2024-01-15

# Suma de atributos
"{{items|sum(attribute='price')}}"  # 1500

# Filtrado y conteo
"{{users|selectattr('is_admin', 'equalto', true)|list|length}}"  # 3

# Mapeo y unión
"{{users|map(attribute='name')|join(', ')}}"  # "Ana, Carlos, María"
```

## Funciones Personalizadas

### Funciones de Utilidad
- `now()`: Fecha y hora actual
- `today()`: Fecha actual
- `calculate_total()`: Calcula total de items
- `is_empty()`: Verifica si un valor está vacío

### Funciones de Acceso a Datos
- `get_variable()`: Obtiene variable del contexto
- `len()`, `type()`, `isinstance()`: Funciones Python estándar

## Ejemplo Completo

```json
{
  "variables": {
    "titulo": "Bienvenido a Sugar con Jinja2",
    "usuario": {
      "nombre": "María García",
      "edad": 28,
      "departamento": "Desarrollo",
      "es_admin": true
    },
    "productos": [
      {"nombre": "Laptop Gaming", "precio": 1500.00, "categoria": "Electronics", "stock": 5},
      {"nombre": "Mouse Wireless", "precio": 45.99, "categoria": "Electronics", "stock": 15},
      {"nombre": "Escritorio", "precio": 350.00, "categoria": "Furniture", "stock": 3},
      {"nombre": "Monitor 4K", "precio": 800.00, "categoria": "Electronics", "stock": 8}
    ],
    "usuarios": [
      {"name": "Ana López", "age": 25, "is_admin": true, "department": "IT"},
      {"name": "Carlos Ruiz", "age": 32, "is_admin": false, "department": "Marketing"},
      {"name": "Elena Martín", "age": 29, "is_admin": false, "department": "Sales"},
      {"name": "David Pérez", "age": 35, "is_admin": true, "department": "Management"}
    ]
  },
  "task": [
    {
      "jinja2": {
        "operator": "parser",
        "template": "{{ titulo|default('Bienvenido') }}",
        "result": "saludo_bienvenida"
      }
    },
    {
      "print": {
        "text": "{{saludo_bienvenida}}"
      }
    },
    {
      "jinja2": {
        "operator": "parser",
        "template": "Usuario: {{usuario.nombre}}, Edad: {{usuario.edad}} años, Departamento: {{usuario.departamento|upper}}",
        "result": "info_usuario"
      }
    },
    {
      "print": {
        "text": "{{info_usuario}}"
      }
    },
    {
      "jinja2": {
        "operator": "parser",
        "template": "{% if usuario.es_admin %}{{usuario.nombre}} es administrador{% else %}{{usuario.nombre}} es usuario regular{% endif %}",
        "result": "rol_usuario"
      }
    },
    {
      "print": {
        "text": "{{rol_usuario}}"
      }
    },
    {
      "jinja2": {
        "operator": "parser",
        "template": "{% if productos %}{{productos|length}} productos disponibles:\n{% for producto in productos %}- {{producto.nombre|upper}}: {{producto.precio|format_currency}} (Stock: {{producto.stock}})\n{% endfor %}{% else %}No hay productos disponibles{% endif %}",
        "result": "reporte_productos"
      }
    },
    {
      "print": {
        "text": "{{reporte_productos}}"
      }
    },
    {
      "jinja2": {
        "operator": "parser",
        "template": "{% if usuarios %}{{usuarios|length}} usuarios en el sistema:\n{% for user in usuarios %}- {{user.name|upper}} ({{user.age}} años, {{user.department}}){% if user.is_admin %} [ADMIN]{% endif %}\n{% endfor %}{% else %}No hay usuarios{% endif %}",
        "result": "reporte_usuarios"
      }
    },
    {
      "print": {
        "text": "{{reporte_usuarios}}"
      }
    },
    {
      "jinja2": {
        "operator": "parser",
        "template": "Estadísticas:\n- Total productos: {{productos|length}}\n- Total usuarios: {{usuarios|length}}\n- Administradores: {{usuarios|selectattr('is_admin', 'equalto', true)|length}}\n- Valor total inventario: {{productos|sum('precio')|format_currency}}",
        "result": "estadisticas"
      }
    },
    {
      "print": {
        "text": "{{estadisticas}}"
      }
    },
    {
      "jinja2": {
        "operator": "validate",
        "template": "{% if condition %}{{variable}}{% endif %}"
      }
    },
    {
      "jinja2": {
        "operator": "info",
        "template": "{% for item in items %}{{item.name|upper}}{% endfor %}"
      }
    },
    {
      "jinja2": {
        "operator": "clear_cache"
      }
    }
  ]
}
```

## Solución de Problemas

### Error: "Jinja2 not available"
- Verificar que Jinja2 esté instalado: `pip install Jinja2`
- Verificar que el nodo AST esté registrado correctamente

### Error: "Template syntax error"
- Usar `validate` operator para detectar errores
- Verificar sintaxis de Jinja2
- Revisar la documentación de Jinja2

### Error: "Variable not found"
- Verificar que las variables estén definidas en memoria
- Usar `default` filter: `{{variable|default('valor por defecto')}}`

## Rendimiento

### Optimizaciones
- **Caching automático**: Los templates se cachean automáticamente
- **Procesamiento directo**: Integración nativa en el AST para máximo rendimiento
- **Validación eficiente**: Detección rápida de errores de sintaxis

### Recomendaciones
- Usar templates simples para casos básicos
- Usar filtros personalizados para formateo específico
- Limpiar cache periódicamente si se usan muchos templates únicos

## Contribuir

Para contribuir al plugin:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar cambios
4. Agregar tests
5. Crear pull request

## Licencia

Este plugin está bajo la misma licencia que Sugar. 