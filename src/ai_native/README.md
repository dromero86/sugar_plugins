# AI Native Plugin

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/sugar-lang/sugar)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Sugar](https://img.shields.io/badge/Sugar-v2.0.0+-orange.svg)](https://github.com/sugar-lang/sugar)

## 🚀 Visión General

El **AI Native Plugin** es un plugin revolucionario para Sugar v2.0.0 que proporciona capacidades de inteligencia artificial nativas de manera modular y reutilizable. Este plugin permite generar código, optimizar algoritmos y crear scripts completos usando solo descripciones en lenguaje natural.

## ✨ Características Principales

### 🎯 **Generación de Código Inteligente**
- **Descripción → Código**: Describe lo que quieres hacer y obtén código funcional
- **Contexto Inteligente**: El sistema entiende el dominio y genera código específico
- **Múltiples Lenguajes**: Soporte para Sugar, Python, JavaScript y más
- **Templates Avanzados**: Sistema de templates por dominio

### ⚡ **Optimización Automática**
- **Análisis de Rendimiento**: Identifica y corrige problemas de rendimiento
- **Optimización de Memoria**: Mejora el uso de recursos del sistema
- **Refactoring Inteligente**: Aplica mejores prácticas automáticamente
- **Análisis de Seguridad**: Detecta y corrige vulnerabilidades

### 💬 **Interfaz de Lenguaje Natural**
- **Consulta Natural → Script Completo**: Convierte descripciones en scripts ejecutables
- **Comprensión de Intención**: El sistema entiende lo que quieres lograr
- **Generación Automática**: Crea sistemas complejos desde cero

### 🛡️ **Sistema de Seguridad Integrado**
- **Validación de Código**: Análisis estático antes de la ejecución
- **Sandboxing**: Ejecución en entorno controlado
- **Patrones Prohibidos**: Bloqueo de código potencialmente peligroso
- **Auditoría**: Logging de todas las operaciones AI

## 📦 Instalación

### Instalación Automática
```bash
# El plugin se instala automáticamente con Sugar
# No requiere dependencias externas por defecto
```

### Verificación de Instalación
```json
{
  "task": [
    {
      "ai_native": {
        "operator": "get_ai_info",
        "result": "plugin_info"
      }
    },
    {
      "print": {
        "text": "Plugin AI Native: {{plugin_info}}"
      }
    }
  ]
}
```

## 🎮 Uso Rápido

### Generar Código
```json
{
  "ai_native": {
    "operator": "generate_code",
    "description": "Crear función que procese datos JSON de una API REST",
    "context": {
      "domain": "web_scraping"
    },
    "result": "api_processor"
  }
}
```

### Optimizar Código
```json
{
  "ai_native": {
    "operator": "optimize_code",
    "code": "{{current_function}}",
    "target": "performance",
    "result": "optimized_function"
  }
}
```

### Procesar Lenguaje Natural
```json
{
  "ai_native": {
    "operator": "nl_to_code",
    "query": "Crear un sistema de monitoreo de servidores con alertas por email",
    "result": "monitoring_system"
  }
}
```

## 📚 Comandos Disponibles

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `generate_code` | Genera código basado en descripción | `description`, `context`, `options`, `result` |
| `optimize_code` | Optimiza código existente | `code`, `target`, `constraints`, `result` |
| `nl_to_code` | Convierte NL a código | `query`, `context`, `result` |
| `analyze_code` | Analiza código para optimizaciones | `code`, `result` |
| `validate_code` | Valida código generado | `code`, `result` |
| `get_context` | Obtiene contexto del dominio | `domain`, `result` |
| `update_context` | Actualiza conocimiento del dominio | `domain`, `knowledge` |
| `check_security` | Verifica configuración de seguridad | `result` |
| `get_ai_info` | Obtiene información del plugin | `result` |
| `install_dependencies` | Instala dependencias faltantes | `result` |
| `download_model` | Descarga un modelo local | `model_name`, `model_path`, `result` |
| `switch_model` | Cambia el modelo actual | `model_type`, `model_name`, `result` |
| `test_model` | Prueba el modelo actual | `prompt`, `result` |
| `get_model_info` | Obtiene información del modelo | `result` |
| `setup` | Configura un proveedor de IA | `provider`, `type`, `api_key`, `config`, `result` |
| `configure` | Actualiza configuración de proveedor | `provider`, `updates`, `result` |
| `add_provider` | Agrega un nuevo proveedor | `provider`, `type`, `api_key`, `result` |
| `remove_provider` | Elimina un proveedor | `provider`, `result` |
| `list_providers` | Lista todos los proveedores | `result` |
| `set_default_provider` | Establece proveedor por defecto | `provider`, `result` |
| `get_provider_info` | Obtiene información de proveedor | `provider`, `result` |
| `test_provider` | Prueba un proveedor específico | `provider`, `result` |
| `combine_providers` | Combina múltiples proveedores | `task`, `providers`, `strategy`, `result` |

## 🌐 Dominios Soportados

### 🌐 **Web Scraping**
- **Patrones**: Selectors, rate limiting, error handling
- **Librerías**: Requests, BeautifulSoup, Selenium
- **Mejores Prácticas**: Respetar robots.txt, usar delays, validar datos

### 📊 **Data Processing**
- **Patrones**: Validation, transformation, aggregation
- **Librerías**: Pandas, NumPy, JSON
- **Mejores Prácticas**: Validar entrada, manejar datos faltantes, logging

### 🤖 **Automation**
- **Patrones**: Scheduling, monitoring, notifications
- **Librerías**: Schedule, cron, smtplib
- **Mejores Prácticas**: Operaciones idempotentes, recuperación de errores

### 🔌 **API Integration**
- **Patrones**: Authentication, rate limiting, error handling
- **Librerías**: Requests, urllib, json
- **Mejores Prácticas**: Usar autenticación apropiada, manejar rate limits

## 📖 Ejemplos

### Ejemplo 1: Generación de Web Scraper
```json
{
  "description": "Generar web scraper para e-commerce",
  "task": [
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Crear un web scraper que extraiga títulos y precios de productos",
        "context": {
          "domain": "web_scraping"
        },
        "result": "ecommerce_scraper"
      }
    },
    {
      "print": {
        "text": "Web scraper generado: {{ecommerce_scraper}}"
      }
    }
  ]
}
```

### Ejemplo 2: Optimización de Algoritmo
```json
{
  "variables": {
    "bubble_sort": {
      "type": "String",
      "value": "function sort(arr) { for (let i = 0; i < arr.length; i++) { for (let j = 0; j < arr.length - 1; j++) { if (arr[j] > arr[j + 1]) { let temp = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = temp; } } } return arr; }"
    }
  },
  "task": [
    {
      "ai_native": {
        "operator": "optimize_code",
        "code": "{{bubble_sort}}",
        "target": "performance",
        "result": "optimized_sort"
      }
    },
    {
      "print": {
        "text": "Algoritmo optimizado: {{optimized_sort}}"
      }
    }
  ]
}
```

### Ejemplo 3: Script Completo desde NL
```json
{
  "task": [
    {
      "ai_native": {
        "operator": "nl_to_code",
        "query": "Crear un sistema de monitoreo que verifique servidores web cada 5 minutos",
        "context": {
          "domain": "automation",
          "requirements": ["http_requests", "scheduling", "notifications"]
        },
        "result": "server_monitor"
      }
    },
    {
      "print": {
        "text": "Sistema de monitoreo: {{server_monitor}}"
      }
    }
  ]
}
```

## 🔧 Configuración

### Configuración por Defecto
```json
{
  "ai_native_config": {
    "enabled": true,
    "models": {
      "code_generation": "template",
      "optimization": "template",
      "nl_processing": "template"
    },
    "limits": {
      "max_tokens": 4000,
      "max_execution_time": 30,
      "max_memory_usage": "512MB"
    },
    "security": {
      "code_validation": true,
      "sandbox_execution": true,
      "audit_logging": true
    }
  }
}
```

### Configuración Avanzada (con IA Real)
```json
{
  "ai_native_config": {
    "enabled": true,
    "models": {
      "code_generation": "gpt-4",
      "optimization": "claude-3",
      "nl_processing": "gpt-4"
    },
    "api_keys": {
      "openai": "sk-...",
      "anthropic": "sk-ant-..."
    },
    "limits": {
      "max_tokens": 8000,
      "max_execution_time": 60,
      "max_memory_usage": "1GB"
    }
  }
}
```

## 📦 Dependencias

### Sistema de Dependencias Inteligente
El plugin AI Native utiliza un sistema de dependencias inteligente que:

1. **✅ Funciona sin dependencias**: Usa templates por defecto
2. **🔄 Detecta automáticamente**: Dependencias disponibles
3. **📈 Escala automáticamente**: Mejora capacidades según dependencias
4. **🔧 Instala automáticamente**: Dependencias faltantes

### Dependencias Principales
```txt
# requirements.txt
# APIs de IA
openai>=1.0.0
anthropic>=0.7.0

# HTTP y Networking
requests>=2.31.0
aiohttp>=3.8.0

# Procesamiento de Datos
numpy>=1.24.0
pandas>=2.0.0

# Web Scraping
beautifulsoup4>=4.12.0
selenium>=4.10.0

# Automatización
schedule>=1.2.0
psutil>=5.9.0

# Modelos Locales (Opcional)
transformers>=4.30.0
torch>=2.0.0
accelerate>=0.20.0

# Análisis de Código
scikit-learn>=1.3.0
pylint>=2.17.0
black>=23.0.0
mypy>=1.4.0
```

### Instalación Automática
```json
{
  "ai_native": {
    "operator": "install_dependencies",
    "result": "install_result"
  }
}
```

### Niveles de Capacidad

#### 🟢 **Nivel Básico (Sin Dependencias)**
- ✅ Generación de código con templates
- ✅ Optimización básica
- ✅ Análisis de código simple
- ✅ Validación de seguridad

#### 🟡 **Nivel Intermedio (Dependencias Básicas)**
- ✅ APIs de IA (OpenAI, Anthropic)
- ✅ Procesamiento de datos avanzado
- ✅ Web scraping completo
- ✅ Automatización avanzada

#### 🔴 **Nivel Avanzado (Todas las Dependencias)**
- ✅ Modelos locales (CodeLlama, StarCoder)
- ✅ Análisis de código profundo
- ✅ Optimización inteligente
- ✅ GPU acceleration

## 🛡️ Seguridad

### Validación Automática
- **Análisis Estático**: El código generado se valida antes de la ejecución
- **Sandboxing**: Ejecución en entorno controlado
- **Patrones Prohibidos**: Bloqueo de código potencialmente peligroso
- **Auditoría**: Logging de todas las operaciones AI

### Patrones Prohibidos
```python
forbidden_patterns = [
    "eval(", "exec(", "system(", "os.system(",
    "subprocess.call(", "subprocess.Popen(",
    "__import__(", "globals(", "locals("
]
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Ejecutar tests del plugin
python -m pytest plugins/src/ai_native/tests/

# Ejecutar ejemplo básico
virtual/bin/sugar plugins/src/ai_native/examples/basic_usage.json

# Ejecutar ejemplo de generación
virtual/bin/sugar plugins/src/ai_native/examples/code_generation.json

# Ejecutar ejemplo de optimización
virtual/bin/sugar plugins/src/ai_native/examples/code_optimization.json

# Ejecutar ejemplo de lenguaje natural
virtual/bin/sugar plugins/src/ai_native/examples/natural_language.json

# Ejecutar ejemplo de gestión de dependencias
virtual/bin/sugar plugins/src/ai_native/examples/dependencies_management.json

## 🔐 Gestión de Credenciales

### 🎯 Configuración Dinámica de Proveedores

El plugin soporta múltiples proveedores de IA que pueden configurarse dinámicamente:

#### Configuración Básica
```json
{
  "ai_native": {
    "operator": "setup",
    "provider": "openai_main",
    "type": "openai",
    "api_key": "sk-your-openai-api-key-here",
    "result": "setup_result"
  }
}
```

#### Múltiples Proveedores
```json
{
  "ai_native": {
    "operator": "combine_providers",
    "task": "generate_code",
    "providers": ["openai_fast", "anthropic_quality"],
    "strategy": "fallback",
    "description": "Crear función de validación",
    "result": "combined_result"
  }
}
```

#### Configuración en Meta
```json
{
  "meta": {
    "ai_native": {
      "operator": "setup",
      "provider": "openai_global",
      "type": "openai",
      "api_key": "sk-your-openai-api-key-here"
    }
  }
}
```

### 🎯 Estrategias de Combinación
- **Fallback**: Intenta con cada proveedor hasta que uno funcione
- **Parallel**: Ejecuta con todos los proveedores simultáneamente
- **Consensus**: Obtiene resultados de todos y selecciona el mejor

### 📚 Documentación Completa
Ver [CREDENTIAL_MANAGEMENT.md](CREDENTIAL_MANAGEMENT.md) para ejemplos detallados.

## 🔐 Seguridad

### Características de Seguridad
- ✅ Validación de código generado
- ✅ Detección de patrones peligrosos
- ✅ Sandbox de ejecución
- ✅ Rate limiting
- ✅ Filtros de contenido
- ✅ Análisis de complejidad

### ⚠️ Protección de API Keys
- **🔒 IMPORTANTE**: Nunca incluyas API keys reales en la documentación o código fuente
- **🔑 Configuración Segura**: Usa variables de entorno o archivos de configuración seguros
- **📝 Templates**: Los ejemplos usan placeholders seguros (`sk-your-openai-api-key-here`)
- **🛡️ Validación**: El plugin valida automáticamente las API keys antes de usarlas

### Configuración Segura
```bash
# Usar variables de entorno
export OPENAI_API_KEY="tu-api-key-real"
export ANTHROPIC_API_KEY="tu-api-key-real"

# O usar archivo .env (no incluir en git)
echo "OPENAI_API_KEY=tu-api-key-real" >> .env
```

## 🚀 Roadmap

### v2.1.0 - Core Plugin ✅
- [x] Plugin base con templates
- [x] Comandos principales
- [x] Sistema de seguridad
- [x] Gestión de contexto
- [x] Tests unitarios

### v2.2.0 - Optimización y NL
- [ ] Optimización de código avanzada
- [ ] Interfaz de lenguaje natural mejorada
- [ ] Gestión de contexto por dominio
- [ ] Configuración avanzada

### v2.3.0 - Seguridad y Escalabilidad
- [ ] Sistema de seguridad completo
- [ ] Sandboxing avanzado
- [ ] Auditoría y logging
- [ ] Optimización de rendimiento

### v2.4.0 - Ecosistema Completo
- [ ] Integración con plugins
- [ ] Gestión de paquetes AI
- [ ] Testing y debugging avanzado
- [ ] Documentación completa

## 🔗 Compatibilidad

### Versiones de Sugar
- ✅ Sugar v2.0.0+
- ✅ Compatible con sistema de plugins
- ✅ Integración AST completa

### Sistemas Operativos
- ✅ Linux
- ✅ Windows
- ✅ macOS

### Dependencias
- ✅ Sin dependencias externas por defecto
- ✅ Dependencias opcionales para IA real

## 🤝 Contribución

### Desarrollo
1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Testing
```bash
# Ejecutar tests del plugin
python -m pytest plugins/src/ai_native/tests/

# Ejecutar ejemplo
virtual/bin/sugar plugins/src/ai_native/examples/basic_usage.json
```

### Documentación
- Mantener documentación actualizada
- Agregar ejemplos para nuevas funcionalidades
- Documentar cambios en API

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/sugar-lang/sugar/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/sugar-lang/sugar/discussions)
- **Documentación**: [docs.sugar-lang.org](https://docs.sugar-lang.org)

## 📁 Estructura del Plugin

```
plugins/src/ai_native/
├── __init__.py                 # Exportaciones del plugin
├── AINativePlugin.py           # Plugin principal
├── docs/
│   └── README.md              # Documentación completa
├── examples/
│   ├── basic_usage.json       # Ejemplo básico
│   ├── code_generation.json   # Ejemplo de generación
│   ├── code_optimization.json # Ejemplo de optimización
│   └── natural_language.json  # Ejemplo de NL
├── tests/
│   ├── __init__.py
│   └── test_ai_native_plugin.py # Tests unitarios
└── README.md                  # Este archivo
```

---

**¡Comienza a usar AI Native Plugin hoy mismo y descubre el poder de la programación con IA en Sugar!** 🚀