# YAML Plugin para Sugar Language

## 🍬 Descripción

El plugin YAML proporciona soporte completo para archivos YAML en Sugar Language, permitiendo escribir scripts de Sugar usando la sintaxis más legible y flexible de YAML, manteniendo toda la funcionalidad existente.

## ✨ Características

- ✅ **Sintaxis YAML completa**: Soporte para todas las características de YAML
- ✅ **Compatibilidad total**: Misma funcionalidad que JSON
- ✅ **Anclajes y referencias**: Reutilización de configuraciones
- ✅ **Comentarios**: Documentación inline en los archivos
- ✅ **Tipos de datos**: Soporte para todos los tipos de YAML
- ✅ **Plugins**: Compatibilidad completa con el sistema de plugins
- ✅ **Detección automática**: Archivos `.yml` y `.yaml` se detectan automáticamente
- ✅ **Conversión JSON → YAML**: Herramientas de migración
- ✅ **Validación**: Verificación de sintaxis YAML

## 🚀 Instalación

### Dependencias

El plugin requiere la librería **PyYAML**:

```bash
pip install pyyaml
```

### Verificación

```json
{
  "task": [
    {
      "yaml": {
        "operator": "check_dependencies",
        "result": "dependency_status"
      }
    }
  ]
}
```

## 📖 Uso

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `process_file` | Procesa un archivo YAML |
| `convert_json_to_yaml` | Convierte JSON a YAML |
| `validate_yaml` | Valida archivo YAML |
| `convert_directory` | Convierte directorio completo |
| `register_cli` | Registra parámetros CLI |

### Ejemplo Básico

```yaml
# script.yaml
task:
  - print:
      text: "🍬 ¡Hola desde YAML!"
  
  - let:
      name: "mensaje"
      value: "Sugar ahora soporta YAML"
  
  - print:
      text: "{{mensaje}}"
```

### Conversión JSON → YAML

```json
{
  "task": [
    {
      "yaml": {
        "operator": "convert_json_to_yaml",
        "json_file": "script.json",
        "yaml_file": "script.yaml",
        "result": "conversion_result"
      }
    }
  ]
}
```

## 📁 Estructura del Plugin

```
plugins/src/yaml/
├── __init__.py                 # Inicialización del plugin
├── YAMLPlugin.py              # Plugin principal
├── plugin.json                # Configuración del plugin
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── docs/
│   └── README.md             # Documentación completa
├── examples/
│   ├── basic_hello.yaml      # Ejemplo básico
│   ├── plugin_example.yaml   # Ejemplo con plugins
│   ├── advanced_features.yaml # Ejemplo avanzado
│   └── conversion_example.json # JSON para conversión
└── tests/
    └── test_yaml_plugin.py   # Tests del plugin
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Desde el directorio raíz del proyecto
python3 -m pytest plugins/src/yaml/tests/

# O ejecutar directamente
python3 plugins/src/yaml/tests/test_yaml_plugin.py
```

### Ejecutar Ejemplos

```bash
# Ejecutar ejemplo básico
python3 Sugar/Service/SugarConsole.py plugins/src/yaml/examples/basic_hello.yaml

# Ejecutar ejemplo con plugins
python3 Sugar/Service/SugarConsole.py plugins/src/yaml/examples/plugin_example.yaml

# Ejecutar ejemplo avanzado
python3 Sugar/Service/SugarConsole.py plugins/src/yaml/examples/advanced_features.yaml
```

## 📚 Documentación

Para documentación completa, consulta:
- [Documentación del Plugin](docs/README.md)
- [Ejemplos de Uso](examples/)
- [Tests](tests/)

## 🔧 Desarrollo

### Estructura del Plugin

El plugin sigue la estructura estándar de plugins de Sugar:

1. **YAMLPlugin.py**: Clase principal que hereda de `PluginBase`
2. **Dependencias**: Declaradas en `requirements.txt` y `plugin.json`
3. **Documentación**: Completa en `docs/README.md`
4. **Ejemplos**: Archivos de ejemplo en `examples/`
5. **Tests**: Suite completa de tests en `tests/`

### Comandos del Plugin

- `process_file`: Procesa archivos YAML
- `convert_json_to_yaml`: Convierte JSON a YAML
- `validate_yaml`: Valida sintaxis YAML
- `convert_directory`: Conversión masiva de directorios
- `register_cli`: Registro dinámico de parámetros CLI

## 🤝 Contribución

Para contribuir al plugin:

1. Sigue la estructura de plugins de Sugar
2. Agrega tests para nuevas funcionalidades
3. Actualiza la documentación
4. Verifica que los ejemplos funcionen
5. Mantén compatibilidad con el sistema existente

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 🆘 Soporte

Para soporte y preguntas:
- Consulta la documentación en `docs/README.md`
- Revisa los ejemplos en `examples/`
- Ejecuta los tests para verificar la instalación

---

**YAML Plugin v1.0.0** - Haciendo Sugar más legible y flexible 🍬