# Guía para Desarrolladores de Plugins

Esta guía proporciona información completa sobre cómo desarrollar plugins para el sistema Sugar.

## Estructura de un Plugin

Un plugin típico debe seguir esta estructura:

```
plugin_name/
├── __init__.py              # Inicialización del plugin
├── plugin_name_plugin.py    # Implementación principal
├── requirements.txt         # Dependencias del plugin
├── README.md               # Documentación del plugin
├── docs/                   # Documentación adicional
├── examples/               # Ejemplos de uso
└── tests/                  # Tests del plugin
```

## Convenciones de Nomenclatura

### Archivos
- **Plugin principal**: `{plugin_name}_plugin.py`
- **Inicialización**: `__init__.py`
- **Dependencias**: `requirements.txt`
- **Documentación**: `README.md`

### Clases y Funciones
- **Clase principal**: `{PluginName}Plugin`
- **Métodos**: Usar snake_case para métodos internos
- **Constantes**: Usar UPPER_CASE

## Sintaxis del Plugin

### Estructura Básica

```python
from Sugar.plugins import PluginBase

class MiPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "mi_plugin"
        self.version = "1.0.0"
    
    def execute(self, command, context):
        # Lógica del plugin
        pass
```

### Registro del Plugin

```python
# En __init__.py
from .mi_plugin_plugin import MiPlugin

def register():
    return MiPlugin()
```

## Gestión de Dependencias

### requirements.txt
```
# Ejemplo de requirements.txt
requests>=2.25.0
selenium>=4.0.0
```

### Instalación
```bash
pip install -r requirements.txt
```

## Documentación

### README.md del Plugin
Cada plugin debe incluir:

1. **Descripción**: Qué hace el plugin
2. **Instalación**: Cómo instalarlo
3. **Uso**: Ejemplos básicos
4. **Configuración**: Opciones disponibles
5. **API**: Referencia de métodos
6. **Ejemplos**: Casos de uso comunes

### Ejemplos
- Incluir ejemplos en la carpeta `examples/`
- Usar archivos JSON para ejemplos de configuración
- Proporcionar casos de uso reales

## Testing

### Estructura de Tests
```
tests/
├── test_plugin_name.py
├── test_integration.py
└── test_examples.py
```

### Convenciones de Testing
- Usar pytest para tests
- Incluir tests unitarios y de integración
- Probar casos de error y éxito
- Mantener cobertura de código alta

## Integración con Sugar

### Comandos del Plugin
Los plugins se ejecutan a través de comandos JSON:

```json
{
    "plugin_name": {
        "operation": "method_name",
        "param1": "value1",
        "param2": "value2"
    }
}
```

### Manejo de Errores
```python
def execute(self, command, context):
    try:
        # Lógica del plugin
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Mejores Prácticas

1. **Simplicidad**: Mantener la API simple y clara
2. **Documentación**: Documentar todo el código
3. **Testing**: Escribir tests completos
4. **Manejo de errores**: Proporcionar mensajes de error útiles
5. **Performance**: Optimizar para casos de uso comunes
6. **Seguridad**: Validar todas las entradas
7. **Compatibilidad**: Mantener compatibilidad hacia atrás

## Publicación

### Checklist antes de publicar:
- [ ] Tests pasando
- [ ] Documentación completa
- [ ] Ejemplos funcionando
- [ ] Manejo de errores implementado
- [ ] Dependencias documentadas
- [ ] README actualizado

## Recursos Adicionales

- [Documentación de PluginBase](../src/README.md)
- [Ejemplos de plugins](../src/)
- [Convenciones del proyecto](../../../docs/development/coding_standards.md)
