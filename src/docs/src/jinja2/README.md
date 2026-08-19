# Jinja2 Plugin

El plugin Jinja2 proporciona funcionalidades para generar contenido dinámico usando el motor de plantillas Jinja2.

## Características

- **Plantillas dinámicas**: Generar contenido basado en plantillas
- **Variables de contexto**: Interpolación de variables de Sugar
- **Filtros personalizados**: Aplicar transformaciones a datos
- **Herencia de plantillas**: Reutilizar y extender plantillas
- **Condicionales y bucles**: Lógica de control en plantillas
- **Macros**: Funciones reutilizables en plantillas

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `jinja2>=3.0.0`
- `markupsafe>=2.0.0`

## Uso

### 1. Renderizado Básico

```json
{
  "jinja2": {
    "template": "Hola {{ nombre }}, bienvenido a {{ sistema }}",
    "context": {
      "nombre": "Usuario",
      "sistema": "Sugar"
    },
    "result": "saludo"
  }
}
```

### 2. Plantilla desde Archivo

```json
{
  "jinja2": {
    "template_file": "/path/to/template.html",
    "context": {
      "usuarios": ["Ana", "Bob", "Carlos"],
      "titulo": "Lista de Usuarios"
    },
    "result": "html_output"
  }
}
```

### 3. Plantilla con Filtros

```json
{
  "jinja2": {
    "template": "Fecha: {{ fecha|strftime('%Y-%m-%d') }}\nPrecio: {{ precio|currency }}",
    "context": {
      "fecha": "2024-01-15",
      "precio": 99.99
    },
    "filters": {
      "currency": "lambda x: f'${x:.2f}'",
      "strftime": "lambda x, fmt: datetime.strptime(x, '%Y-%m-%d').strftime(fmt)"
    },
    "result": "formatted_output"
  }
}
```

### 4. Plantilla con Condicionales

```json
{
  "jinja2": {
    "template": "{% if usuario.admin %}Admin: {{ usuario.nombre }}{% else %}Usuario: {{ usuario.nombre }}{% endif %}",
    "context": {
      "usuario": {
        "nombre": "Admin",
        "admin": true
      }
    },
    "result": "user_info"
  }
}
```

### 5. Plantilla con Bucles

```json
{
  "jinja2": {
    "template": "{% for item in items %}- {{ item }}\n{% endfor %}",
    "context": {
      "items": ["Item 1", "Item 2", "Item 3"]
    },
    "result": "item_list"
  }
}
```

## Parámetros

### Configuración Básica
- `template` (string, opcional): Plantilla como string
- `template_file` (string, opcional): Ruta al archivo de plantilla
- `context` (object, opcional): Variables de contexto
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración Avanzada
- `filters` (object, opcional): Filtros personalizados
- `functions` (object, opcional): Funciones personalizadas
- `autoescape` (boolean, opcional): Escape automático (default: true)
- `trim_blocks` (boolean, opcional): Recortar bloques (default: false)
- `lstrip_blocks` (boolean, opcional): Recortar espacios (default: false)

### Opciones de Salida
- `output_file` (string, opcional): Archivo de salida
- `encoding` (string, opcional): Codificación (default: "utf-8")

## Filtros Disponibles

### Filtros de Texto
- `upper`: Convertir a mayúsculas
- `lower`: Convertir a minúsculas
- `title`: Capitalizar palabras
- `trim`: Eliminar espacios
- `replace`: Reemplazar texto

### Filtros de Números
- `round`: Redondear números
- `int`: Convertir a entero
- `float`: Convertir a flotante
- `abs`: Valor absoluto

### Filtros de Listas
- `length`: Longitud de lista
- `first`: Primer elemento
- `last`: Último elemento
- `sort`: Ordenar lista
- `unique`: Elementos únicos

### Filtros de Fechas
- `strftime`: Formatear fecha
- `date`: Extraer fecha
- `time`: Extraer hora

## Ejemplos Avanzados

### Plantilla HTML Completa

```json
{
  "jinja2": {
    "template_file": "/templates/report.html",
    "context": {
      "titulo": "Reporte Mensual",
      "fecha": "2024-01-15",
      "datos": [
        {"mes": "Enero", "ventas": 15000},
        {"mes": "Febrero", "ventas": 18000},
        {"mes": "Marzo", "ventas": 22000}
      ],
      "total": 55000
    },
    "filters": {
      "currency": "lambda x: f'${x:,.2f}'",
      "percentage": "lambda x: f'{x:.1f}%'"
    },
    "result": "html_report"
  }
}
```

### Plantilla de Configuración

```json
{
  "jinja2": {
    "template": "DATABASE_URL=postgresql://{{ db_user }}:{{ db_pass }}@{{ db_host }}:{{ db_port }}/{{ db_name }}\nDEBUG={{ debug|lower }}\nSECRET_KEY={{ secret_key }}",
    "context": {
      "db_user": "myuser",
      "db_pass": "mypass",
      "db_host": "localhost",
      "db_port": 5432,
      "db_name": "mydb",
      "debug": true,
      "secret_key": "{{ env.SECRET_KEY }}"
    },
    "result": "config_content"
  }
}
```

### Plantilla con Herencia

```json
{
  "jinja2": {
    "template": "{% extends 'base.html' %}\n{% block content %}\n<h1>{{ titulo }}</h1>\n<p>{{ contenido }}</p>\n{% endblock %}",
    "context": {
      "titulo": "Página Principal",
      "contenido": "Bienvenido a nuestro sitio"
    },
    "template_dirs": ["/templates"],
    "result": "page_content"
  }
}
```

### Plantilla de Email

```json
{
  "jinja2": {
    "template": "Estimado {{ usuario.nombre }},\n\nSu pedido #{{ pedido.id }} ha sido confirmado.\n\nProductos:\n{% for item in pedido.items %}- {{ item.nombre }}: {{ item.precio|currency }}\n{% endfor %}\n\nTotal: {{ pedido.total|currency }}\n\nGracias por su compra.",
    "context": {
      "usuario": {
        "nombre": "Juan Pérez",
        "email": "juan@example.com"
      },
      "pedido": {
        "id": "12345",
        "items": [
          {"nombre": "Producto A", "precio": 29.99},
          {"nombre": "Producto B", "precio": 19.99}
        ],
        "total": 49.98
      }
    },
    "filters": {
      "currency": "lambda x: f'${x:.2f}'"
    },
    "result": "email_content"
  }
}
```

## Funciones Personalizadas

### Definir Funciones

```json
{
  "jinja2": {
    "template": "{{ calcular_edad(fecha_nacimiento) }} años",
    "context": {
      "fecha_nacimiento": "1990-05-15"
    },
    "functions": {
      "calcular_edad": "lambda fecha: (datetime.now() - datetime.strptime(fecha, '%Y-%m-%d')).days // 365"
    },
    "result": "edad_calculada"
  }
}
```

### Funciones con Múltiples Parámetros

```json
{
  "jinja2": {
    "template": "{{ formatear_telefono(codigo, numero) }}",
    "context": {
      "codigo": "+1",
      "numero": "5551234567"
    },
    "functions": {
      "formatear_telefono": "lambda codigo, numero: f'{codigo} ({numero[:3]}) {numero[3:6]}-{numero[6:]}'"
    },
    "result": "phone_formatted"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Plantilla no encontrada**: Archivo de plantilla inexistente
- **Variable no definida**: Variable de contexto faltante
- **Error de sintaxis**: Sintaxis incorrecta en plantilla
- **Filtro no encontrado**: Filtro personalizado no definido
- **Error de renderizado**: Error durante el procesamiento

## Optimización

### Caché de Plantillas
- Las plantillas se compilan una vez
- Reutilización de plantillas compiladas
- Mejora del rendimiento en uso repetido

### Configuración de Rendimiento
```json
{
  "jinja2": {
    "template": "{{ contenido }}",
    "context": {"contenido": "texto"},
    "autoescape": false,
    "trim_blocks": true,
    "lstrip_blocks": true,
    "result": "optimized_output"
  }
}
```

## Recursos Adicionales

- [Documentación de Jinja2](https://jinja.palletsprojects.com/)
- [Guía de Plantillas](../../../docs/language/template_system.md)
