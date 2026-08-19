# AI Native Plugin - Documentación

## Visión General

El **AI Native Plugin** es un plugin revolucionario para Sugar v2.0.0 que proporciona capacidades de inteligencia artificial nativas de manera modular y reutilizable. Este plugin permite generar código, optimizar algoritmos y crear scripts completos usando solo descripciones en lenguaje natural.

## Características Principales

### 🚀 **Generación de Código Inteligente**
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

## Instalación

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

## Comandos Disponibles

### 1. **generate_code** - Generación de Código
Genera código basado en descripción y contexto.

**Parámetros:**
- `description` (String, requerido): Descripción de la funcionalidad a generar
- `context` (Dict, opcional): Contexto del dominio (default: `{"domain": "general"}`)
- `options` (Dict, opcional): Opciones adicionales
- `result` (String, opcional): Variable para almacenar resultado (default: `"generated_code"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "generate_code",
    "description": "Crear función que procese datos JSON de una API REST",
    "context": {
      "domain": "web_scraping"
    },
    "options": {
      "language": "sugar",
      "style": "functional",
      "complexity": "medium"
    },
    "result": "api_processor"
  }
}
```

### 2. **optimize_code** - Optimización de Código
Optimiza código existente para mejorar rendimiento, memoria o legibilidad.

**Parámetros:**
- `code` (String, requerido): Código a optimizar
- `target` (String, opcional): Objetivo de optimización (default: `"performance"`)
- `constraints` (Dict, opcional): Restricciones de optimización
- `result` (String, opcional): Variable para resultado (default: `"optimized_code"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "optimize_code",
    "code": "{{current_function}}",
    "target": "performance",
    "constraints": {
      "maintain_api": true,
      "preserve_behavior": true
    },
    "result": "optimized_function"
  }
}
```

### 3. **nl_to_code** - Interfaz de Lenguaje Natural
Convierte consultas en lenguaje natural a código ejecutable.

**Parámetros:**
- `query` (String, requerido): Consulta en lenguaje natural
- `context` (Dict, opcional): Contexto adicional
- `result` (String, opcional): Variable para script (default: `"generated_script"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "nl_to_code",
    "query": "Obtener datos de API y guardar en base de datos",
    "context": {
      "domain": "data_processing",
      "requirements": ["error_handling", "logging", "data_validation"]
    },
    "result": "api_to_database_script"
  }
}
```

### 4. **analyze_code** - Análisis de Código
Analiza código para determinar optimizaciones posibles.

**Parámetros:**
- `code` (String, requerido): Código a analizar
- `result` (String, opcional): Variable para análisis (default: `"code_analysis"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "analyze_code",
    "code": "{{function_to_analyze}}",
    "result": "analysis_result"
  }
}
```

### 5. **validate_code** - Validación de Código
Valida código generado por IA para seguridad y calidad.

**Parámetros:**
- `code` (String, requerido): Código a validar
- `result` (String, opcional): Variable para validación (default: `"validation_result"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "validate_code",
    "code": "{{generated_code}}",
    "result": "validation_status"
  }
}
```

### 6. **get_context** - Obtener Contexto
Obtiene contexto específico del dominio.

**Parámetros:**
- `domain` (String, opcional): Dominio específico (default: `"general"`)
- `result` (String, opcional): Variable para contexto (default: `"domain_context"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "get_context",
    "domain": "web_scraping",
    "result": "scraping_context"
  }
}
```

### 7. **update_context** - Actualizar Contexto
Actualiza conocimiento del dominio.

**Parámetros:**
- `domain` (String, requerido): Dominio a actualizar
- `knowledge` (Dict, requerido): Nuevo conocimiento

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "update_context",
    "domain": "web_scraping",
    "knowledge": {
      "new_patterns": ["ajax_handling", "dynamic_content"],
      "new_libraries": ["playwright", "puppeteer"]
    }
  }
}
```

### 8. **check_security** - Verificar Seguridad
Verifica configuración de seguridad del plugin.

**Parámetros:**
- `result` (String, opcional): Variable para estado (default: `"security_status"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "check_security",
    "result": "security_info"
  }
}
```

### 9. **get_ai_info** - Información del Plugin
Obtiene información completa sobre el plugin AI.

**Parámetros:**
- `result` (String, opcional): Variable para información (default: `"ai_info"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "get_ai_info",
    "result": "plugin_info"
  }
}
```

### 10. **install_dependencies** - Instalar Dependencias
Instala dependencias faltantes automáticamente.

**Parámetros:**
- `result` (String, opcional): Variable para resultado (default: `"install_result"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "install_dependencies",
    "result": "install_result"
  }
}
```

### 11. **download_model** - Descargar Modelo
Descarga un modelo local para inferencia offline.

**Parámetros:**
- `model_name` (String, opcional): Nombre del modelo (default: `"codellama-7b-instruct"`)
- `model_path` (String, opcional): Ruta de descarga (default: `"./models"`)
- `result` (String, opcional): Variable para resultado (default: `"download_result"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "download_model",
    "model_name": "codellama-7b-instruct",
    "model_path": "./models",
    "result": "download_result"
  }
}
```

### 12. **switch_model** - Cambiar Modelo
Cambia el modelo actual de IA.

**Parámetros:**
- `model_type` (String, requerido): Tipo de modelo (`template`, `openai`, `anthropic`, `local`)
- `model_name` (String, opcional): Nombre específico del modelo
- `result` (String, opcional): Variable para resultado (default: `"switch_result"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "switch_model",
    "model_type": "openai",
    "model_name": "gpt-4",
    "result": "switch_result"
  }
}
```

### 13. **test_model** - Probar Modelo
Prueba el modelo actual con un prompt de ejemplo.

**Parámetros:**
- `prompt` (String, opcional): Prompt de prueba (default: `"Crear una función simple que sume dos números"`)
- `result` (String, opcional): Variable para resultado (default: `"test_result"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "test_model",
    "prompt": "Crear una función que procese datos JSON",
    "result": "test_result"
  }
}
```

### 14. **get_model_info** - Información del Modelo
Obtiene información detallada del modelo actual.

**Parámetros:**
- `result` (String, opcional): Variable para información (default: `"model_info"`)

**Ejemplo:**
```json
{
  "ai_native": {
    "operator": "get_model_info",
    "result": "model_info"
  }
}
```

## Dominios Soportados

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

## Ejemplos Prácticos

### Ejemplo 1: Generación de Web Scraper
```json
{
  "description": "Generar web scraper para e-commerce",
  "variables": {
    "target_url": {
      "type": "String",
      "value": "https://example-store.com/products"
    }
  },
  "task": [
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Crear un web scraper que extraiga títulos y precios de productos",
        "context": {
          "domain": "web_scraping"
        },
        "options": {
          "language": "sugar",
          "style": "functional"
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
        "constraints": {
          "maintain_api": true,
          "preserve_behavior": true
        },
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

## Configuración

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

### Configuración Avanzada
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
    },
    "security": {
      "code_validation": true,
      "sandbox_execution": true,
      "audit_logging": true,
      "forbidden_patterns": ["eval(", "exec(", "system("]
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

### Dependencias del Sistema
```bash
# Herramientas necesarias
curl          # Para descarga de modelos
git           # Para clonar repositorios
wget          # Para descarga alternativa
unzip         # Para extraer modelos
tar           # Para archivos comprimidos
gcc           # Para compilar extensiones
make          # Para build de dependencias
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

### Verificación de Dependencias
```json
{
  "ai_native": {
    "operator": "get_ai_info",
    "result": "plugin_info"
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

## Seguridad

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

### Configuración de Seguridad
```json
{
  "security": {
    "code_validation": true,
    "sandbox_execution": true,
    "audit_logging": true,
    "forbidden_patterns": ["eval(", "exec(", "system("]
  }
}
```

## Troubleshooting

### Problemas Comunes

#### 1. Error de Validación
```
Error: Task validation failed
```
**Solución**: Verificar que la descripción sea clara y el contexto sea válido

#### 2. Tiempo de Ejecución Excedido
```
Error: Execution time limit exceeded
```
**Solución**: Reducir la complejidad de la descripción o aumentar el límite

#### 3. Código Generado Inválido
```
Error: Generated code validation failed
```
**Solución**: Revisar la descripción y asegurar que sea específica

#### 4. Dependencias Faltantes
```
Error: Dependencias no satisfechas
```
**Solución**: Verificar dependencias con `check_dependencies`

### Debug
```json
{
  "task": [
    {
      "ai_native": {
        "operator": "get_ai_info",
        "result": "debug_info"
      }
    },
    {
      "print": {
        "text": "Debug info: {{debug_info}}"
      }
    }
  ]
}
```

## Mejores Prácticas

### 1. Descripciones Claras
```json
// ✅ Bueno
"description": "Crear función que procese datos JSON de API REST y valide campos requeridos"

// ❌ Evitar
"description": "hacer algo con datos"
```

### 2. Contexto Específico
```json
// ✅ Específico
"context": {"domain": "web_scraping"}

// ❌ Genérico
"context": {"domain": "general"}
```

### 3. Validación de Resultados
```json
{
  "task": [
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Función de ejemplo",
        "result": "generated_function"
      }
    },
    {
      "ai_native": {
        "operator": "validate_code",
        "code": "{{generated_function}}",
        "result": "validation_result"
      }
    },
    {
      "if": {
        "condition": "{{validation_result.valid}} == true",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Código válido"
              }
            }
          ]
        },
        "else": {
          "task": [
            {
              "print": {
                "text": "❌ Código inválido: {{validation_result.issues}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### 4. Manejo de Errores
```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "ai_native": {
              "operator": "generate_code",
              "description": "Función compleja",
              "result": "complex_function"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": {
              "text": "Error generando código: {{error}}"
            }
          }
        ]
      }
    }
  ]
}
```

## Roadmap

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

## Compatibilidad

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

## Contribución

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
virtual/bin/sugar examples/ai_native/basic_usage.json
```

### Documentación
- Mantener documentación actualizada
- Agregar ejemplos para nuevas funcionalidades
- Documentar cambios en API

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Soporte

- **Issues**: [GitHub Issues](https://github.com/sugar-lang/sugar/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/sugar-lang/sugar/discussions)
- **Documentación**: [docs.sugar-lang.org](https://docs.sugar-lang.org)

---

**¡Comienza a usar AI Native Plugin hoy mismo y descubre el poder de la programación con IA en Sugar!**