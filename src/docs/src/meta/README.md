# Meta Plugin

El plugin Meta proporciona funcionalidades de meta-programación y reflexión para manipular el comportamiento del sistema Sugar en tiempo de ejecución.

## Características

- **Reflexión**: Inspeccionar y modificar objetos en tiempo de ejecución
- **Meta-hooks**: Interceptar y modificar operaciones del sistema
- **Generación de código**: Crear código dinámicamente
- **Modificación de AST**: Manipular el árbol de sintaxis abstracta
- **Inyección de dependencias**: Gestión dinámica de dependencias
- **Plugins dinámicos**: Cargar y descargar plugins en tiempo de ejecución

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `inspect` (incluido en Python estándar)
- `ast` (incluido en Python estándar)
- `types` (incluido en Python estándar)

## Uso

### 1. Inspección de Objeto

```json
{
  "meta": {
    "operation": "inspect",
    "target": "{{ objeto }}",
    "attributes": true,
    "methods": true,
    "result": "object_info"
  }
}
```

### 2. Modificación de Atributos

```json
{
  "meta": {
    "operation": "set_attribute",
    "target": "{{ objeto }}",
    "name": "nuevo_atributo",
    "value": "nuevo_valor",
    "result": "modification_status"
  }
}
```

### 3. Llamada Dinámica de Método

```json
{
  "meta": {
    "operation": "call_method",
    "target": "{{ objeto }}",
    "method": "metodo_dinamico",
    "args": ["arg1", "arg2"],
    "kwargs": {"param1": "valor1"},
    "result": "method_result"
  }
}
```

### 4. Generación de Clase

```json
{
  "meta": {
    "operation": "create_class",
    "name": "ClaseDinamica",
    "bases": ["ClaseBase"],
    "attributes": {
      "atributo1": "valor1",
      "atributo2": "valor2"
    },
    "methods": {
      "metodo1": "lambda self: print('Hola')"
    },
    "result": "dynamic_class"
  }
}
```

### 5. Modificación de AST

```json
{
  "meta": {
    "operation": "modify_ast",
    "code": "x = 1 + 2",
    "transformations": [
      {
        "type": "add_import",
        "module": "math",
        "names": ["sqrt"]
      }
    ],
    "result": "modified_code"
  }
}
```

## Parámetros

### Operaciones Básicas
- `operation` (string, requerido): Tipo de operación
  - `inspect`: Inspeccionar objeto
  - `set_attribute`: Establecer atributo
  - `get_attribute`: Obtener atributo
  - `call_method`: Llamar método
  - `create_class`: Crear clase
  - `modify_ast`: Modificar AST

### Configuración de Inspección
- `target` (object, opcional): Objeto a inspeccionar
- `attributes` (boolean, opcional): Incluir atributos
- `methods` (boolean, opcional): Incluir métodos
- `private` (boolean, opcional): Incluir miembros privados

### Configuración de Modificación
- `name` (string, opcional): Nombre del atributo/método
- `value` (any, opcional): Valor a asignar
- `args` (array, opcional): Argumentos posicionales
- `kwargs` (object, opcional): Argumentos nombrados

### Configuración de Generación
- `class_name` (string, opcional): Nombre de la clase
- `bases` (array, opcional): Clases base
- `attributes` (object, opcional): Atributos de la clase
- `methods` (object, opcional): Métodos de la clase

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Operaciones Disponibles

### Inspección
- **Información de objeto**: Atributos, métodos, tipo
- **Jerarquía de clases**: Clases base y herencia
- **Análisis de código**: Estructura y dependencias
- **Documentación**: Docstrings y comentarios

### Modificación
- **Atributos dinámicos**: Añadir/modificar atributos
- **Métodos dinámicos**: Añadir/modificar métodos
- **Propiedades**: Crear propiedades computadas
- **Decoradores**: Aplicar decoradores dinámicamente

### Generación
- **Clases dinámicas**: Crear clases en tiempo de ejecución
- **Funciones dinámicas**: Generar funciones
- **Módulos dinámicos**: Crear módulos
- **Código dinámico**: Generar código Python

### AST
- **Análisis de AST**: Parsear y analizar código
- **Modificación de AST**: Transformar código
- **Generación de AST**: Crear código desde AST
- **Optimización**: Optimizar código

## Ejemplos Avanzados

### Crear Plugin Dinámico

```json
{
  "meta": {
    "operation": "create_plugin",
    "name": "PluginDinamico",
    "version": "1.0.0",
    "methods": {
      "execute": "lambda self, command, context: {'success': True, 'result': 'Plugin dinámico ejecutado'}",
      "get_info": "lambda self: {'name': self.name, 'version': self.version}"
    },
    "result": "dynamic_plugin"
  }
}
```

### Interceptar Llamadas de Método

```json
{
  "meta": {
    "operation": "add_hook",
    "target": "{{ objeto }}",
    "method": "metodo_original",
    "hook": "lambda original, *args, **kwargs: {'pre': 'antes', 'result': original(*args, **kwargs), 'post': 'después'}",
    "result": "hook_status"
  }
}
```

### Generar API REST Dinámica

```json
{
  "meta": {
    "operation": "create_rest_api",
    "base_class": "Flask",
    "endpoints": [
      {
        "path": "/api/users",
        "method": "GET",
        "handler": "lambda: {'users': ['user1', 'user2']}"
      },
      {
        "path": "/api/users",
        "method": "POST",
        "handler": "lambda data: {'created': data}"
      }
    ],
    "result": "rest_api"
  }
}
```

### Modificar Comportamiento de Clase

```json
{
  "meta": {
    "operation": "monkey_patch",
    "target_class": "MiClase",
    "method_name": "metodo_original",
    "new_implementation": "lambda self, *args: 'Nueva implementación'",
    "result": "patch_status"
  }
}
```

### Crear Decorador Dinámico

```json
{
  "meta": {
    "operation": "create_decorator",
    "name": "log_calls",
    "implementation": "lambda func: lambda *args, **kwargs: {'log': 'Llamada a ' + func.__name__, 'result': func(*args, **kwargs)}",
    "result": "dynamic_decorator"
  }
}
```

### Análisis de Dependencias

```json
{
  "meta": {
    "operation": "analyze_dependencies",
    "target": "{{ modulo }}",
    "include_imports": true,
    "include_calls": true,
    "include_attributes": true,
    "result": "dependency_graph"
  }
}
```

## Meta-Hooks

### Hooks de Sistema
- **Pre-execution**: Antes de ejecutar comandos
- **Post-execution**: Después de ejecutar comandos
- **Error-handling**: Manejo de errores
- **Context-modification**: Modificación de contexto

### Hooks de Plugin
- **Plugin-load**: Al cargar plugins
- **Plugin-unload**: Al descargar plugins
- **Method-call**: Al llamar métodos
- **Attribute-access**: Al acceder a atributos

## Configuración de Seguridad

### Restricciones
- **Modo sandbox**: Ejecución en entorno controlado
- **Permisos**: Control de acceso a operaciones
- **Validación**: Validación de código generado
- **Auditoría**: Log de operaciones meta

### Configuración Segura
```json
{
  "meta": {
    "operation": "inspect",
    "target": "{{ objeto }}",
    "sandbox": true,
    "permissions": ["read_only"],
    "audit": true,
    "result": "safe_inspection"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Objeto no encontrado**: Objeto inexistente
- **Atributo no encontrado**: Atributo no existe
- **Método no encontrado**: Método no existe
- **Error de sintaxis**: Código generado inválido
- **Error de permisos**: Operación no permitida

## Optimización

### Caché de Reflexión
- Cachear información de objetos
- Reutilizar análisis de AST
- Optimizar búsquedas de atributos

### Lazy Loading
- Cargar información bajo demanda
- Deferir análisis complejos
- Optimizar uso de memoria

## Recursos Adicionales

- [Documentación de inspect](https://docs.python.org/3/library/inspect.html)
- [Documentación de ast](https://docs.python.org/3/library/ast.html)
- [Guía de Meta-programación](../../../docs/language/metaprogramming.md)
