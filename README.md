# Guía Completa de Plugins de Sugar 2.0.0

Esta guía contiene toda la documentación de plugins para Sugar en un solo documento, incluyendo desarrollo, uso, sistema de dependencias, SDK, ejemplos prácticos y mejores prácticas.

## 📚 Índice

1. [Introducción](#introducción)
2. [Sistema de Plugins](#sistema-de-plugins)
3. [Desarrollo de Plugins](#desarrollo-de-plugins)
4. [Sistema de Control de Dependencias](#sistema-de-control-de-dependencias)
5. [Plugin SDK](#plugin-sdk)
6. [Desarrollo Independiente](#desarrollo-independiente)
7. [Sistema de Meta Hooks](#sistema-de-meta-hooks)
8. [Plugins Disponibles](#plugins-disponibles)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [Instalación y Gestión](#instalación-y-gestión)
11. [Funcionalidades Avanzadas v4.1.0](#-funcionalidades-avanzadas-v410)
12. [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

Sugar incluye un sistema robusto de plugins que extiende las funcionalidades del lenguaje de manera modular. Características principales:

- **Modularidad**: Plugins independientes y reutilizables
- **Compatibilidad AST**: Integración perfecta con el sistema de Abstract Syntax Tree
- **Sistema de Dependencias**: Control automático de dependencias y requerimientos
- **Plugin SDK**: Sistema completo para desarrollo avanzado
- **Desarrollo Independiente**: Plantillas para desarrollo sin Sugar completo
- **Estructura Organizada**: Todos los plugins se encuentran en el directorio `plugins/src/`
- **Carga Optimizada**: Estrategias de carga paralela y secuencial (v4.1.0)
- **Procesamiento Heterogéneo**: CPU + GPU + Coordinación automática (v4.1.0)
- **Gestión de Recursos**: Monitoreo y optimización automática (v4.1.0)
- **Debug Avanzado**: Herramientas mejoradas de diagnóstico (v4.1.0)

---

## Sistema de Plugins

### Estructura de Archivos
```
plugins/
├── src/                     # Código fuente de plugins
│   ├── plugin_name/
│   │   ├── __init__.py      # Configuración del plugin
│   │   ├── PluginName.py    # Implementación principal
│   │   ├── requirements.txt # Dependencias (opcional)
│   │   └── examples/        # Ejemplos de uso (opcional)
│   └── ...
├── samples/
│   ├── example_dependency_plugin.py    # Plugin con dependencias
│   └── standalone_plugin_template.py   # Plantilla standalone
└── README.md                # Esta documentación
```

### Sintaxis de Comandos
```json
{
  "nombre_plugin": {
    "operator": "comando",
    "parametro1": "valor1",
    "parametro2": "valor2",
    "result": "variable_resultado"
  }
}
```

---

## Desarrollo de Plugins

### Clase Base PluginBase

```python
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output
from typing import Dict, Any, List, Optional

class MiPlugin(PluginBase):
    VERSION = "1.0.0"
    DESCRIPTION = "Descripción del plugin"
    AUTHOR = "Tu Nombre"
    LICENSE = "MIT"
    
    # Dependencias básicas de Python
    DEPENDENCIES = ["dependency1", "dependency2"]
    REQUIREMENTS = ["dependency1>=1.0.0"]
    
    # Dependencias del sistema (ejecutables)
    SYSTEM_DEPENDENCIES = ["curl", "git"]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 4,
        "min_disk_gb": 1,
        "min_cpu_cores": 2
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": True,
        "write_access": ["/tmp", "./output"],
        "read_access": ["./data"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Verificar dependencias al inicializar
        self.dependency_status = self._check_all_dependencies()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Inicializar SDK si las dependencias están satisfechas
        if self.dependency_status['all_satisfied']:
            self._initialize_sdk()
    
    def get_available_commands(self) -> List[str]:
        return ["comando1", "comando2", "comando3"]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        # Verificar dependencias antes de comandos críticos
        if command in ["critical_command"] and not self.dependency_status['all_satisfied']:
            raise RuntimeError("Dependencias no satisfechas")
        
        if command == "comando1":
            return self._comando1(config)
        elif command == "comando2":
            return self._comando2(config)
        else:
            raise ValueError(f"Comando desconocido: {command}")
    
    def _comando1(self, config: Dict[str, Any]) -> Any:
        result = "resultado del comando"
        if "result" in config:
            self.set_variable(config["result"], result)
        return result
```

### Métodos Principales

- `get_available_commands()` - Lista de comandos soportados
- `execute(command, config)` - Ejecuta un comando específico
- `interpolate_variables(value)` - Interpola variables de Sugar
- `set_variable(name, value)` - Asigna una variable
- `get_variable(name, default)` - Obtiene una variable

---

## Sistema de Control de Dependencias

### Tipos de Dependencias Soportadas

1. **Dependencias de Python (Paquetes)**
   ```python
   DEPENDENCIES = ["requests", "numpy", "pandas"]
   REQUIREMENTS = ["requests>=2.25.0", "numpy>=1.20.0", "pandas>=1.3.0"]
   ```

2. **Dependencias del Sistema (Ejecutables)**
   ```python
   SYSTEM_DEPENDENCIES = ["curl", "git", "openssl"]
   ```

3. **Requerimientos de Hardware**
   ```python
   HARDWARE_REQUIREMENTS = {
       "min_ram_gb": 4,
       "min_disk_gb": 1,
       "min_cpu_cores": 2
   }
   ```

4. **Requerimientos de Permisos**
   ```python
   PERMISSION_REQUIREMENTS = {
       "network_access": True,
       "write_access": ["/tmp", "./output"],
       "read_access": ["./data"]
   }
   ```

### Comandos de Verificación

- `check_dependencies` - Verificar estado de dependencias
- `system_info` - Información del sistema
- `test_functionality` - Probar funcionalidad
- `dependency_report` - Reporte completo de dependencias
- `install_dependencies` - Instalar dependencias faltantes

### Implementación de Verificación

```python
def _check_all_dependencies(self) -> Dict[str, Any]:
    """Verificar todas las dependencias y requerimientos."""
    status = {
        'python_packages': self._check_python_packages(),
        'system_dependencies': self._check_system_dependencies(),
        'hardware_requirements': self._check_hardware_requirements(),
        'permission_requirements': self._check_permission_requirements(),
        'all_satisfied': True
    }
    
    for category in status.keys():
        if category != 'all_satisfied' and not status[category]['satisfied']:
            status['all_satisfied'] = False
    
    return status

def _check_python_packages(self) -> Dict[str, Any]:
    """Verificar paquetes de Python."""
    results = {
        'satisfied': True,
        'packages': {},
        'missing': [],
        'install_commands': []
    }
    
    for package in self.DEPENDENCIES:
        try:
            __import__(package)
            results['packages'][package] = {
                'available': True,
                'version': self._get_package_version(package)
            }
        except ImportError:
            results['packages'][package] = {
                'available': False,
                'version': None
            }
            results['missing'].append(package)
            results['satisfied'] = False
    
    return results
```

---

## Plugin SDK

### Componentes del SDK

1. **ExtensionManager** - Gestión centralizada de extensiones
2. **HookSystem** - Sistema de hooks para interceptar eventos
3. **InterpolationInterceptor** - Interceptar interpolaciones de variables
4. **ASTModifier** - Modificar el árbol de sintaxis abstracta
5. **FlowController** - Controlar el flujo de ejecución
6. **CommandCustomizer** - Personalizar comandos existentes

### Uso Básico del SDK

```python
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    CommandCustomizer, CommandEvent
)

class AdvancedPlugin(PluginBase):
    def _initialize_sdk(self):
        """Inicializar componentes del SDK."""
        self.extension_manager = ExtensionManager()
        self.hook_system = HookSystem()
        self.command_customizer = CommandCustomizer()
        
        # Registrar extensiones
        self._register_sdk_extensions()
    
    def _register_sdk_extensions(self):
        """Registrar extensiones específicas del plugin."""
        # Hook para tareas
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=5
        )
        
        # Customización de comandos
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_command_callback,
            priority=5
        )
    
    def _before_task_hook(self, hook_context):
        """Hook ejecutado antes de cada tarea."""
        Output.Console(self.plugin_name, "Hook ejecutado antes de tarea")
        return hook_context
    
    def _before_command_callback(self, context):
        """Callback para customización de comandos."""
        Output.Console(self.plugin_name, f"Ejecutando comando: {context.command_name}")
        return context
```

### Casos de Uso Comunes

#### Logging Avanzado
```python
def _logging_hook(self, hook_context):
    """Hook para logging personalizado"""
    hook_context.data['plugin_info'] = {
        'plugin': self.plugin_name,
        'timestamp': time.time(),
        'user_id': get_current_user_id()
    }
    return hook_context
```

#### Seguridad y Validación
```python
def _security_hook(self, hook_context):
    """Hook de seguridad"""
    if not self._has_permission(hook_context.data):
        hook_context.should_abort = True
        hook_context.data['error'] = 'Permission denied'
    return hook_context
```

#### Variables Personalizadas
```python
def _variable_interceptor(self, context):
    """Interceptor para variables personalizadas"""
    if context.original_value.startswith('${config.'):
        config_key = context.original_value[8:-1]
        config_value = self._get_config_value(config_key)
        context.interpolated_value = str(config_value)
        context.modified = True
    return context
```

---

## Sistema de Meta Hooks

### Overview

El sistema de Meta Hooks en Sugar permite a los plugins definir su comportamiento inicial que será precargado antes de la ejecución. Esto proporciona una forma centralizada y modular de configurar plugins.

### Concepto

El sistema `meta` funciona como un hook donde cada plugin puede definir su configuración inicial. Esta configuración se procesa antes de que comience la ejecución de las tareas, permitiendo que los plugins se configuren automáticamente.

### Sintaxis

```json
{
    "meta": {
        "plugin_name": {
            "option1": "value1",
            "option2": "value2",
            "options": {
                "nested_option": "value"
            }
        }
    }
}
```

### Plugins Compatibles

#### Selenium Plugin

Configura el driver de Selenium y las opciones del navegador.

```json
{
    "meta": {
        "selenium": {
            "driver": {
                "bin": "/path/to/chromedriver"
            },
            "options": [
                "--disable-gpu",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-dev-shm-usage",
                "--window-size=1280,720",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-service-autorun",
                "--disable-features=VizDisplayCompositor",
                "--user-data-dir=/opt/selenium/profile", 
                "--profile-directory=Default",
                "user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
            ],
            "detach": true
        }
    }
}
```

#### WebServer Plugin

Configura el servidor web con puerto, directorios estáticos y autenticación.

```json
{
    "meta": {
        "webserver": {
            "options": {
                "port": 8080,
                "static": "./public",
                "insecure_passw": {
                    "user": "admin",
                    "pass": "password123"
                }
            }
        }
    }
}
```

#### SSH Plugin

Configura sesiones SSH predefinidas con conexión automática.

```json
{
    "meta": {
        "ssh": {
            "options": {
                "my_pc": {
                    "host": "192.168.0.100",
                    "username": "admin",
                    "password": "adminpass",
                    "auto_connect": true
                },
                "server1": {
                    "host": "10.0.0.50",
                    "username": "root",
                    "password": "rootpass",
                    "port": 22,
                    "auto_connect": false
                }
            }
        }
    }
}
```

#### Database Plugin

Configura conexiones de base de datos predefinidas con conexión automática.

```json
{
    "meta": {
        "database": {
            "connections": {
                "main_db": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "mydb",
                    "username": "user",
                    "password": "password",
                    "auto_connect": true
                },
                "backup_db": {
                    "host": "backup-server",
                    "port": 5432,
                    "database": "backupdb",
                    "username": "backup_user",
                    "password": "backup_pass",
                    "auto_connect": false
                }
            }
        }
    }
}
```

#### Environment Plugin

Configura variables de entorno y archivos .env.

```json
{
    "meta": {
        "environment": {
            "variables": {
                "APP_ENV": "production",
                "DEBUG": false,
                "API_URL": "https://api.example.com",
                "DB_HOST": "localhost",
                "DB_PORT": 3306,
                "LOG_LEVEL": "INFO"
            },
            "env_files": [
                ".env.production",
                ".env.local"
            ],
            "auto_set": true
        }
    }
}
```

### Implementación en Plugins

Para que un plugin sea compatible con el sistema de meta hooks, debe implementar el método `meta_hook`:

```python
def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Meta hook para configuración del plugin.
    Llamado por el plugin meta para configurar el plugin antes de la ejecución.
    
    Args:
        config: Configuración desde la sección meta
        
    Returns:
        Resultado de la configuración
    """
    try:
        # Procesar configuración
        self.meta_config = config
        
        # Aplicar configuración específica
        # ...
        
        return {
            "success": True,
            "config_applied": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Comandos del Plugin Meta

El plugin meta proporciona varios comandos para gestionar los hooks:

#### configure
Configura el sistema con la configuración meta.

```json
{
    "meta": {
        "command": "configure",
        "config": {}
    }
}
```

#### get_status
Obtiene el estado del sistema de hooks.

```json
{
    "meta": {
        "command": "get_status",
        "config": {}
    }
}
```

#### get_plugin_config
Obtiene la configuración de un plugin específico.

```json
{
    "meta": {
        "command": "get_plugin_config",
        "config": {
            "plugin": "selenium"
        }
    }
}
```

#### execute_hooks
Ejecuta todos los hooks registrados.

```json
{
    "meta": {
        "command": "execute_hooks",
        "config": {}
    }
}
```

#### initialize_plugin
Inicializa un plugin específico con su configuración meta.

```json
{
    "meta": {
        "command": "initialize_plugin",
        "config": {
            "plugin": "selenium"
        }
    }
}
```

### Ejemplos de Uso

#### Ejemplo Básico - Selenium

```json
{
    "meta": {
        "selenium": {
            "driver": {
                "bin": "/usr/bin/chromedriver"
            },
            "options": [
                "--headless",
                "--no-sandbox"
            ],
            "detach": false
        }
    },
    "task": [
        {
            "selenium": {
                "command": "open_browser",
                "config": {
                    "browser": "chrome"
                }
            }
        }
    ]
}
```

#### Ejemplo Múltiples Plugins

```json
{
    "meta": {
        "selenium": {
            "options": ["--headless"]
        },
        "webserver": {
            "options": {
                "port": 8080
            }
        },
        "ssh": {
            "options": {
                "server": {
                    "host": "192.168.1.100",
                    "username": "admin",
                    "password": "pass",
                    "auto_connect": true
                }
            }
        },
        "database": {
            "connections": {
                "main_db": {
                    "host": "localhost",
                    "database": "mydb",
                    "username": "user",
                    "password": "pass",
                    "auto_connect": true
                }
            }
        },
        "environment": {
            "variables": {
                "APP_ENV": "production"
            },
            "auto_set": true
        }
    },
    "task": [
        {
            "print": {
                "message": "Todos los plugins configurados via meta"
            }
        }
    ]
}
```

### Ventajas del Sistema

1. **Configuración Centralizada**: Toda la configuración de plugins en un solo lugar
2. **Precarga Automática**: Los plugins se configuran antes de la ejecución
3. **Modularidad**: Cada plugin define su propia configuración
4. **Compatibilidad**: Compatible con el sistema `require` existente
5. **Flexibilidad**: Permite configuración compleja y anidada
6. **Dependencias Automáticas**: Los plugins con meta tienen dependencia automática al plugin meta

### Compatibilidad

El sistema de meta hooks es compatible con:
- Sistema AST existente
- Sistema `require` para inclusión de archivos
- Todos los plugins existentes (con implementación de `meta_hook`)
- Configuración heredada (fallback a configuración por defecto)

### Migración

Para migrar desde el sistema anterior de meta:

1. **Antes**: `{"meta": {"mode": "selenium"}}`
2. **Ahora**: `{"meta": {"selenium": {"options": ["--headless"]}}}`

El nuevo sistema es más específico y permite configuración granular por plugin.

### Plugins Excluidos

Los siguientes plugins NO tienen propiedades meta configuradas:
- `curl`: Plugin para operaciones cURL
- `openssl`: Plugin para operaciones criptográficas
- `compiler`: Plugin para compilación
- `meta`: El propio plugin meta (no se configura a sí mismo)

---

## Desarrollo Independiente

### Características del Desarrollo Independiente

- ✅ **Desarrollo rápido** - No necesitas configurar todo el entorno de Sugar
- ✅ **Testing aislado** - Pruebas independientes sin interferencias
- ✅ **SDK completo** - Incluye todos los componentes del SDK
- ✅ **Mock classes** - Simula el entorno de Sugar
- ✅ **Migración fácil** - Transición sencilla a Sugar completo

### Plantilla Standalone

```bash
# Usar la plantilla para desarrollo independiente
cp plugins/samples/standalone_plugin_template.py mi_plugin.py
```

### Ejemplo de Plugin Standalone

```python
from standalone_plugin_template import *

class MiPluginStandalone(MockPluginBase):
    VERSION = "1.0.0"
    DESCRIPTION = "Mi plugin standalone"
    
    def __init__(self, context=None, plugin_config=None):
        super().__init__(context, plugin_config)
        self._initialize_sdk()
    
    def get_available_commands(self) -> List[str]:
        return ["mi_comando"]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        if command == "mi_comando":
            return {"status": "success", "message": "Plugin standalone funcionando"}
        else:
            raise ValueError(f"Comando desconocido: {command}")

# Probar el plugin
if __name__ == "__main__":
    plugin = MiPluginStandalone()
    result = plugin.execute("mi_comando", {})
    print(f"Resultado: {result}")
```

### Migración a Sugar Completo

```python
# Antes (standalone)
from standalone_plugin_template import MockPluginBase, MockOutput

# Después (Sugar completo)
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

# Antes
class MiPlugin(MockPluginBase):

# Después
class MiPlugin(PluginBase):
```

---

## Plugins Disponibles

### 🔌 Plugins de Networking

#### SSH Plugin
**Ubicación**: `plugins/src/ssh/`
**Comandos**: `connect`, `disconnect`, `execute`, `upload`, `download`, `create_tunnel`, `system_info`, `service_control`

#### FTP/FTPS Plugin
**Ubicación**: `plugins/src/ftp/`
**Comandos**: `connect`, `upload`, `download`, `list`

#### Request Plugin
**Ubicación**: `plugins/src/request/`
**Comandos**: `get`, `post`, `put`, `delete`, `patch`, `head`, `options`, `session`

#### Socket Plugin
**Ubicación**: `plugins/src/socket/`
**Comandos**: `connect`, `send`, `receive`

### 🌐 Plugins Web

#### Selenium Plugin
**Ubicación**: `plugins/src/selenium/`
**Comandos**: `open_browser`, `navigate`, `click`, `type`, `screenshot`, `wait_for_element`

#### WebServer Plugin
**Ubicación**: `plugins/src/webserver/`
**Comandos**: `send`, `set_cookies`, `redirect`

### 🔐 Plugins de Seguridad

#### OpenSSL Plugin
**Ubicación**: `plugins/src/openssl/`
**Comandos**: `generate_key`, `sign`, `verify`, `encrypt`, `decrypt`

#### JWT Plugin
**Ubicación**: `plugins/src/jwt/`
**Comandos**: `encode`, `decode`, `verify`

### 🛠️ Plugins de Desarrollo

#### Compiler Plugin
**Ubicación**: `plugins/src/compiler/`
**Comandos**: `compile`, `build`

#### Database Plugin
**Ubicación**: `plugins/src/database/`
**Comandos**: `connect`, `query`, `insert`, `update`, `delete`

#### Meta Plugin
**Ubicación**: `plugins/src/meta/`
**Características**: Sistema de hooks para configuración previa de plugins

### 📦 Plugins de Utilidades

#### Jinja2 Plugin
**Ubicación**: `plugins/src/jinja2/`
**Comandos**: `render`, `render_file`

#### Simple Plugin
**Ubicación**: `plugins/src/simple_plugin.py`
**Comandos**: `hello`, `add`, `multiply`, `subtract`, `divide`

#### Zip Plugin
**Ubicación**: `plugins/src/zip/`
**Características**: Compresión y descompresión de archivos

### 📋 Tabla de Compatibilidad

| Plugin | Versión | AST | Legacy | Testing | Documentación | Dependencias | SDK |
|--------|---------|-----|--------|---------|---------------|--------------|-----|
| SSH | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FTP/FTPS | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| HTTP | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Socket | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cURL | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Selenium | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WebServer | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OpenSSL | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| JWT | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compiler | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Database | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Meta | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Jinja2 | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Simple Plugin | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Zip | 1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Leyenda**: AST, Legacy, Testing, Documentación, Dependencias, SDK

---

## Ejemplos de Uso

### SSH - Conexión y Ejecución de Comandos
```json
{
  "task": [
    {
      "ssh": {
        "operator": "connect",
        "host": "192.168.1.100",
        "username": "admin",
        "password": "secret123",
        "session_name": "servidor1"
      }
    },
    {
      "ssh": {
        "operator": "execute",
        "session": "servidor1",
        "command": "ls -la",
        "result": "archivos"
      }
    },
    {
      "print": { "text": "Archivos: {{archivos}}" }
    }
  ]
}
```

### Request - Peticiones HTTP
```json
{
  "task": [
    {
      "request": {
        "operator": "get",
        "url": "https://api.example.com/data",
        "headers": {
          "Authorization": "Bearer token123",
          "Content-Type": "application/json"
        },
        "result": "response_data"
      }
    }
  ]
}
```

### Selenium - Automatización Web
```json
{
  "task": [
    {
      "selenium": {
        "operator": "open_browser",
        "browser": "chrome",
        "headless": false
      }
    },
    {
      "selenium": {
        "operator": "navigate",
        "url": "https://example.com"
      }
    },
    {
      "selenium": {
        "operator": "type",
        "selector": "#username",
        "text": "usuario@ejemplo.com"
      }
    },
    {
      "selenium": {
        "operator": "click",
        "selector": "#submit"
      }
    }
  ]
}
```

### Plugin con Sistema de Dependencias
```json
{
  "task": [
    {
      "dependency_plugin": {
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
              "dependency_plugin": {
                "operator": "test_functionality",
                "result": "test_results"
              }
            },
            {
              "print": { "text": "✅ Plugin funcionando correctamente" }
            }
          ]
        },
        "else": {
          "task": [
            {
              "dependency_plugin": {
                "operator": "install_dependencies",
                "auto_install": true
              }
            }
          ]
        }
      }
    }
  ]
}
```

### Workflow Completo - Múltiples Plugins
```json
{
  "task": [
    {
      "String::servidor": "192.168.1.100"
    },
    {
      "ssh": {
        "operator": "connect",
        "host": "{{servidor}}",
        "username": "admin",
        "password": "secret123",
        "session_name": "servidor_principal"
      }
    },
    {
      "ssh": {
        "operator": "execute",
        "session": "servidor_principal",
        "command": "cat /var/log/app.log | tail -n 10",
        "result": "logs_recientes"
      }
    },
    {
      "file": {
        "operator": "write",
        "filename": "logs_backup.txt",
        "content": "{{logs_recientes}}"
      }
    },
    {
      "request": {
        "operator": "post",
        "url": "https://api.monitoring.com/alert",
        "data": {
          "message": "Backup completado",
          "server": "{{servidor}}"
        }
      }
    }
  ]
}
```

---

## Instalación y Gestión

### Instalación Automática
```bash
pip install sugar
```

### Gestión desde Línea de Comandos

Sugar incluye parámetros CLI completos para gestionar plugins directamente desde la consola, incluyendo las nuevas funcionalidades de la versión 4.1.0:

#### Parámetros Disponibles

```bash
# Gestión básica de plugins
virtual/bin/python3 -m Sugar.Service.SugarConsole -p                    # Listar todos los plugins
virtual/bin/python3 -m Sugar.Service.SugarConsole -pe "plugin1,plugin2" # Habilitar plugins
virtual/bin/python3 -m Sugar.Service.SugarConsole -pd "plugin1,plugin2" # Deshabilitar plugins
virtual/bin/python3 -m Sugar.Service.SugarConsole -po                   # Deshabilitar TODOS los plugins
virtual/bin/python3 -m Sugar.Service.SugarConsole -pt plugin_name       # Evaluar un plugin específico
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir [ruta_opcional] # Gestionar directorio de plugins

# Estrategias de carga de plugins (NUEVO v4.1.0)
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy [parallel|sequential]
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-workers N

# Procesamiento paralelo (NUEVO v4.1.0)
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-info
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-test

# Gestión de recursos (NUEVO v4.1.0)
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-info
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-status
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-optimize

# Debug mejorado (NUEVO v4.1.0)
virtual/bin/python3 -m Sugar.Service.SugarConsole --debug=yes
virtual/bin/python3 -m Sugar.Service.SugarConsole --dev-mode
```

#### Ejemplos de Uso CLI

**Listar plugins disponibles:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -p
```

**Habilitar múltiples plugins:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pe "selenium_plugin,ssh,yaml"
```

**Deshabilitar plugins problemáticos:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pd "plugin_problematico"
```

**Deshabilitar todos los plugins (para limpieza):**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -po
```

**Evaluar plugin para diagnóstico:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pt selenium_plugin
```

**Ver información de directorios de plugins:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir
```

**Establecer directorio personalizado de plugins:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir "/ruta/personalizada/plugins"
```

**Combinar con modo debug:**
```bash
virtual/bin/python3 -m Sugar.Service.SugarConsole -p --debug=yes
```

#### Nuevas Funcionalidades v4.1.0

**Estrategias de Carga de Plugins:**
```bash
# Carga paralela (más rápida, por defecto)
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy parallel

# Carga secuencial (tradicional)
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy sequential

# Especificar número de workers para carga paralela
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-workers 4
```

**Procesamiento Paralelo:**
```bash
# Ver información sobre capacidades de procesamiento paralelo
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-info

# Probar funcionalidad de procesamiento paralelo
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-test
```

**Gestión de Recursos:**
```bash
# Información detallada del sistema
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-info

# Estado actual de todos los recursos
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-status

# Optimización automática de recursos
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-optimize
```

**Debug Mejorado:**
```bash
# Debug completo con logs detallados
virtual/bin/python3 -m Sugar.Service.SugarConsole --debug=yes

# Modo desarrollo con carga completa
virtual/bin/python3 -m Sugar.Service.SugarConsole --dev-mode
```

#### Características CLI

- ✅ **Configuración Persistente** - Los cambios se guardan automáticamente
- ✅ **Múltiples Plugins** - Soporte para listas separadas por comas
- ✅ **Gestión de Directorios** - Control completo de rutas de plugins
- ✅ **Información Detallada** - Estado completo de todos los plugins
- ✅ **Diagnóstico** - Evaluación completa de plugins individuales
- ✅ **Compatibilidad** - Funciona con otros parámetros como --debug
- ✅ **Cross-Platform** - Directorios apropiados por OS (Windows/Unix)
- ✅ **Carga Paralela** - Estrategias de carga optimizadas (v4.1.0)
- ✅ **Procesamiento Heterogéneo** - CPU + GPU + Coordinación (v4.1.0)
- ✅ **Gestión de Recursos** - Monitoreo y optimización automática (v4.1.0)
- ✅ **Debug Avanzado** - Logs detallados y modo desarrollo (v4.1.0)

### Gestión con @sugarize/
```bash
# Instalar plugin específico
sugarize require plugin-name ^1.0.0

# Instalar desde repositorio Git
sugarize require https://github.com/user/plugin-repo --branch main

# Actualizar plugin
sugarize update plugin-name

# Remover plugin
sugarize remove plugin-name
```

### Directorios de Plugins por Defecto

**Cambio Importante**: El sistema ahora solo incluye el directorio oficial de plugins por defecto:

- **Directorio Oficial**: `~/.sugar/plugins` (Unix/Linux/macOS) o `C:\Users\<Usuario>\AppData\Sugar\Plugins` (Windows)
- **Razón**: Las rutas del repositorio de desarrollo (`plugins/`, `plugins/src/`) no se incluyen por defecto ya que son específicas del entorno de desarrollo y pueden cambiar.

#### Para Desarrollo
Si necesitas usar plugins del repositorio durante el desarrollo, puedes agregar manualmente las rutas:

```bash
# Agregar directorio de desarrollo temporalmente
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir "plugins/src"

# O usar rutas absolutas
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir "/ruta/completa/al/repositorio/plugins/src"
```

#### Para Producción
En producción, solo se usará el directorio oficial:

```bash
# Verificar directorio oficial
virtual/bin/python3 -m Sugar.Service.SugarConsole -pdir

# Crear directorio si no existe
mkdir -p ~/.sugar/plugins

# Instalar plugins en el directorio oficial
cp -r mi_plugin ~/.sugar/plugins/
```

### Gestión de Dependencias de Plugins

```python
# Verificar dependencias de un plugin
plugin_manager.check_plugin_dependencies("plugin_name")

# Instalar dependencias automáticamente
plugin_manager.install_plugin_dependencies("plugin_name", auto_install=True)

# Verificar dependencias del sistema
plugin_manager.check_system_dependencies(["curl", "git"])
```

### Ubicación de Plugins

Todos los plugins se encuentran en el directorio `plugins/src/`. Esta estructura organizada facilita:

- **Desarrollo**: Separación clara entre código fuente y otros archivos
- **Mantenimiento**: Organización lógica de plugins por funcionalidad
- **Testing**: Tests específicos para cada plugin en su directorio correspondiente
- **Documentación**: Documentación específica de cada plugin en su ubicación

### Testing de Plugins
```bash
# Ejecutar tests de un plugin específico
python -m pytest plugins/src/plugin_name/tests/

# Ejecutar todos los tests
python -m pytest plugins/src/

# Ejecutar ejemplo de SSH
sugar examples/ssh/basic_connection.json
```

---

## 🚀 Funcionalidades Avanzadas v4.1.0

### Estrategias de Carga de Plugins

La versión 4.1.0 introduce estrategias de carga optimizadas para mejorar el rendimiento:

#### Carga Paralela (Recomendada)
```bash
# Carga paralela automática con detección de workers
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy parallel

# Carga paralela con workers específicos
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy parallel --plugin-workers 8
```

**Ventajas:**
- ⚡ **40% más rápida** que la carga secuencial
- 🔄 **Detección automática** del número óptimo de workers
- 🎯 **Carga inteligente** basada en dependencias
- 📊 **Monitoreo en tiempo real** del progreso

#### Carga Secuencial (Tradicional)
```bash
# Carga secuencial para compatibilidad
virtual/bin/python3 -m Sugar.Service.SugarConsole --plugin-load-strategy sequential
```

**Casos de uso:**
- 🔧 **Debugging** de problemas de carga
- 🧪 **Testing** de plugins individuales
- 💾 **Sistemas con recursos limitados**

### Procesamiento Paralelo Heterogéneo

Nuevo sistema de procesamiento que aprovecha CPU y GPU simultáneamente:

#### Información del Sistema
```bash
# Ver capacidades de procesamiento paralelo
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-info
```

**Salida típica:**
```
🚀 Información de Procesamiento Paralelo
============================================================
✅ Procesamiento paralelo heterogéneo disponible

📦 Componentes:
   • CPU Multi-core           ✅ Disponible
   • CUDA GPU                 ✅ Disponible
   • OpenCL GPU               ✅ Disponible
   • Vulkan GPU               ❌ No disponible

🔧 Características:
   • Detección automática de hardware
   • Procesamiento CPU multi-núcleo
   • Procesamiento GPU (CUDA, OpenCL, Vulkan)
   • Coordinación heterogénea
   • Fallback inteligente a CPU
   • Monitoreo y telemetría
   • Optimización automática
```

#### Testing de Funcionalidad
```bash
# Probar procesamiento paralelo
virtual/bin/python3 -m Sugar.Service.SugarConsole --parallel-test
```

### Gestión Avanzada de Recursos

Sistema completo de monitoreo y optimización de recursos:

#### Información Detallada del Sistema
```bash
# Información completa del sistema
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-info
```

**Incluye:**
- 💾 **Memoria RAM**: Uso actual y disponible
- 🖥️ **CPU**: Cores, frecuencia, carga
- 🎮 **GPU**: Memoria, temperatura, utilización
- 💿 **Disco**: Espacio, velocidad de lectura/escritura
- 🌐 **Red**: Ancho de banda, latencia

#### Estado de Recursos
```bash
# Estado actual de todos los recursos
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-status
```

**Monitorea:**
- 📊 **Uso en tiempo real** de todos los recursos
- ⚠️ **Alertas** cuando se alcanzan límites
- 📈 **Tendencias** de uso de recursos
- 🎯 **Recomendaciones** de optimización

#### Optimización Automática
```bash
# Optimización automática de recursos
virtual/bin/python3 -m Sugar.Service.SugarConsole --resource-optimize
```

**Optimizaciones aplicadas:**
- 🔄 **Reasignación** de recursos entre procesos
- 🧹 **Limpieza** de memoria no utilizada
- ⚡ **Ajuste** de prioridades de procesos
- 🎛️ **Configuración** automática de límites

### Debug Avanzado

Sistema de debugging mejorado con múltiples niveles:

#### Debug Completo
```bash
# Debug con logs detallados
virtual/bin/python3 -m Sugar.Service.SugarConsole --debug=yes
```

**Información disponible:**
- 📝 **Logs de parsing** y construcción del AST
- 🔍 **Información de variables** y contexto
- ⚙️ **Detalles de ejecución** de comandos
- 🔌 **Información de plugins** y componentes
- 🐛 **Stack traces** completos

#### Modo Desarrollo
```bash
# Modo desarrollo con carga completa
virtual/bin/python3 -m Sugar.Service.SugarConsole --dev-mode
```

**Características:**
- 🔧 **Carga completa** de palabras reservadas
- 🧪 **Modo testing** habilitado
- 📊 **Métricas detalladas** de rendimiento
- 🔍 **Validación estricta** de código

### Casos de Uso Avanzados

#### Optimización de Rendimiento
```bash
# Configuración para máximo rendimiento
virtual/bin/python3 -m Sugar.Service.SugarConsole \
  --plugin-load-strategy parallel \
  --plugin-workers 8 \
  --resource-optimize \
  script.json
```

#### Debugging Complejo
```bash
# Debug completo con información de recursos
virtual/bin/python3 -m Sugar.Service.SugarConsole \
  --debug=yes \
  --resource-info \
  --parallel-info \
  script.json
```

#### Desarrollo y Testing
```bash
# Entorno completo para desarrollo
virtual/bin/python3 -m Sugar.Service.SugarConsole \
  --dev-mode \
  --plugin-load-strategy sequential \
  --debug=yes \
  test_script.json
```

### Compatibilidad y Migración

#### Compatibilidad
- ✅ **100% compatible** con versiones anteriores
- 🔄 **Migración automática** sin cambios manuales
- 📦 **Plugins existentes** funcionan sin modificación
- 🎯 **APIs existentes** mantienen compatibilidad

#### Nuevas Funcionalidades Opcionales
- 🚀 **Procesamiento paralelo**: Disponible para nuevos desarrollos
- ⚡ **Carga optimizada**: Mejora automática del rendimiento
- 📊 **Gestión de recursos**: Monitoreo y optimización automática
- 🔍 **Debug avanzado**: Herramientas mejoradas de diagnóstico

---

## Mejores Prácticas

### 1. Manejo de Errores
```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "ssh": {
              "operator": "connect",
              "host": "servidor_inaccesible.com",
              "username": "user",
              "password": "pass"
            }
          }
        ]
      },
      "catch": {
        "task": [
          { "print": { "text": "Error de conexión SSH: {{error}}" } }
        ]
      }
    }
  ]
}
```

### 2. Configuración Reutilizable
```json
{
  "String::db_config": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "password": "pass"
  },
  "task": [
    {
      "database": {
        "operator": "connect",
        "config": "{{db_config}}"
      }
    }
  ]
}
```

### 3. Testing de Plugins
```json
{
  "task": [
    {
      "simple": {
        "operator": "hello",
        "name": "Test",
        "result": "test_greeting"
      }
    },
    {
      "if": {
        "condition": "${test_greeting} == 'Hello, Test!'",
        "then": {
          "task": [
            { "print": { "text": "✅ Test de saludo exitoso" } }
          ]
        },
        "else": {
          "task": [
            { "print": { "text": "❌ Test de saludo falló" } }
          ]
        }
      }
    }
  ]
}
```

### 4. Estructura Recomendada
```
mi_plugin/
├── __init__.py
├── src/
│   └── MiPlugin.py
├── components/
│   ├── __init__.py
│   └── Helper.py
├── docs/
│   └── README.md
├── tests/
│   ├── __init__.py
│   └── test_mi_plugin.py
├── examples/
│   ├── basic_usage.json
│   └── advanced_usage.json
├── README.md
├── requirements.txt
├── plugin.json
└── setup.py
```

### 5. Mejores Prácticas Generales

1. **Nomenclatura**: Usa nombres descriptivos para comandos y parámetros
2. **Validación**: Valida siempre la entrada del usuario
3. **Logging**: Usa el sistema de logging de Sugar para debug
4. **Documentación**: Documenta todos los comandos y parámetros
5. **Testing**: Incluye tests unitarios y de integración
6. **Manejo de Errores**: Maneja excepciones apropiadamente
7. **Variables**: Usa interpolación de variables cuando sea apropiado
8. **Configuración**: Proporciona valores por defecto sensatos
9. **Dependencias**: Implementa verificación de dependencias
10. **SDK**: Usa el SDK para funcionalidad avanzada cuando sea apropiado

---

## Troubleshooting

### Problemas Comunes

#### 1. Plugin no se carga
- Verificar que la clase herede de `PluginBase`
- Asegurar que `__init__.py` esté configurado correctamente
- Revisar que la ruta del plugin sea correcta (debe estar en `plugins/src/plugin_name/`)

#### 2. Comando no encontrado
- Verificar que el comando esté en `get_available_commands()`
- Asegurar que el comando esté manejado en `execute()`
- Revisar la ortografía del comando

#### 3. Error de variables
- Verificar que el plugin tenga acceso al contexto
- Asegurar que las variables existan antes de usarlas
- Usar `get_variable()` con valores por defecto

#### 4. Error de sintaxis
- Usar la sintaxis correcta: `{"plugin": {"operator": "command", ...}}`
- Verificar que los parámetros sean correctos
- Revisar que el JSON sea válido

#### 5. Dependencias faltantes
- Verificar dependencias con `check_dependencies`
- Instalar dependencias faltantes con `install_dependencies`
- Revisar requerimientos de hardware y permisos

### Debug
```python
# Habilitar debug en el plugin
class MiPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.debug = True
    
    def execute(self, command: str, config: dict) -> any:
        if self.debug:
            Output.Console(self.plugin_name, f"Executing command: {command}")
            Output.Console(self.plugin_name, f"Config: {config}")
        
        # ... resto del código
```

### Validación de Configuración
```python
def _validate_config(self, config: dict, required_keys: list) -> None:
    """Validate configuration parameters."""
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Required parameter '{key}' not found in config")
```

### Manejo de Excepciones
```python
def execute(self, command: str, config: dict) -> any:
    """Execute a plugin command with error handling."""
    try:
        if command == "comando1":
            return self._comando1(config)
        elif command == "comando2":
            return self._comando2(config)
        else:
            raise ValueError(f"Unknown command: {command}")
    except ValueError as e:
        # Re-raise ValueError for parameter errors
        raise
    except Exception as e:
        # Log unexpected errors
        Output.Console(self.plugin_name, f"Error executing command '{command}': {str(e)}")
        raise
```

---

## Recursos Adicionales

- **[Documentación del Lenguaje](../language/README.md)** - Especificación completa del lenguaje
- **[Ejemplos de Uso](../../examples/)** - Ejemplos prácticos de todos los plugins
- **[Guía de Contribución](../../CONTRIBUTING.md)** - Cómo contribuir al proyecto
- **[Changelog](../../changelog/)** - Historial de cambios y nuevas funcionalidades

---

## Conclusión

Esta guía proporciona toda la información necesaria para trabajar con plugins en Sugar. Recuerda:

- Usar siempre la sintaxis correcta: `{"plugin_name": {"operator": "command", ...}}` or `{"plugin_name": {"config": { ... } }}`
- Implementar verificación de dependencias en tus plugins
- Usar el SDK para funcionalidad avanzada cuando sea apropiado
- Seguir las mejores prácticas de desarrollo
- Probar exhaustivamente tus plugins
- Documentar claramente su uso
- Contribuir a la comunidad
