# 🔐 Gestión de Credenciales - Plugin AI Native

## 📋 Nuevos Operadores de Configuración

El plugin AI Native ahora incluye operadores especializados para gestionar múltiples proveedores de IA y sus credenciales de forma dinámica.

### 🎯 Operadores Disponibles

#### 1. **`setup`** - Configurar Proveedor
```json
{
  "ai_native": {
    "operator": "setup",
    "provider": "openai_main",
    "type": "openai",
    "api_key": "sk-your-openai-api-key-here",
    "config": {
      "model": "gpt-4",
      "max_tokens": 4000,
      "temperature": 0.1
    },
    "result": "setup_result"
  }
}
```

#### 2. **`configure`** - Actualizar Configuración
```json
{
  "ai_native": {
    "operator": "configure",
    "provider": "openai_main",
    "updates": {
      "config": {
        "temperature": 0.2
      }
    },
    "result": "config_result"
  }
}
```

#### 3. **`add_provider`** - Agregar Nuevo Proveedor
```json
{
  "ai_native": {
    "operator": "add_provider",
    "provider": "anthropic_claude",
    "type": "anthropic",
    "api_key": "sk-ant-your-anthropic-api-key-here",
    "result": "add_result"
  }
}
```

#### 4. **`list_providers`** - Listar Proveedores
```json
{
  "ai_native": {
    "operator": "list_providers",
    "result": "providers_list"
  }
}
```

#### 5. **`set_default_provider`** - Establecer Proveedor por Defecto
```json
{
  "ai_native": {
    "operator": "set_default_provider",
    "provider": "openai_main",
    "result": "default_result"
  }
}
```

#### 6. **`test_provider`** - Probar Proveedor
```json
{
  "ai_native": {
    "operator": "test_provider",
    "provider": "openai_main",
    "result": "test_result"
  }
}
```

#### 7. **`combine_providers`** - Combinar Múltiples Proveedores
```json
{
  "ai_native": {
    "operator": "combine_providers",
    "task": "generate_code",
    "providers": ["openai_main", "anthropic_claude"],
    "strategy": "fallback",
    "description": "Crear función de ordenamiento",
    "result": "combined_result"
  }
}
```

## 🎯 Escenarios de Uso

### 📊 **Escenario 1: Configuración Inicial**
```json
{
  "description": "Configuración inicial de múltiples proveedores",
  "task": [
    {
      "ai_native": {
        "operator": "setup",
        "provider": "openai_fast",
        "type": "openai",
        "api_key": "sk-your-openai-api-key-here",
        "config": {"model": "gpt-3.5-turbo"}
      }
    },
    {
      "ai_native": {
        "operator": "setup",
        "provider": "anthropic_quality",
        "type": "anthropic",
        "api_key": "sk-ant-your-anthropic-api-key-here"
      }
    },
    {
      "ai_native": {
        "operator": "list_providers",
        "result": "providers"
      }
    }
  ]
}
```

### 🔄 **Escenario 2: Estrategia de Fallback**
```json
{
  "description": "Usar múltiples proveedores con fallback",
  "task": [
    {
      "ai_native": {
        "operator": "combine_providers",
        "task": "generate_code",
        "providers": ["openai_fast", "anthropic_quality"],
        "strategy": "fallback",
        "description": "Crear función de validación de email",
        "result": "email_validator"
      }
    }
  ]
}
```

### ⚡ **Escenario 3: Ejecución Paralela**
```json
{
  "description": "Ejecutar con múltiples proveedores en paralelo",
  "task": [
    {
      "ai_native": {
        "operator": "combine_providers",
        "task": "optimize_code",
        "providers": ["openai_fast", "anthropic_quality"],
        "strategy": "parallel",
        "code": "function bubbleSort(arr) { ... }",
        "target": "performance",
        "result": "optimization_results"
      }
    }
  ]
}
```

### 🎯 **Escenario 4: Consenso entre Proveedores**
```json
{
  "description": "Obtener consenso entre múltiples proveedores",
  "task": [
    {
      "ai_native": {
        "operator": "combine_providers",
        "task": "nl_to_code",
        "providers": ["openai_fast", "anthropic_quality"],
        "strategy": "consensus",
        "query": "Crear sistema de monitoreo de servidores",
        "result": "best_solution"
      }
    }
  ]
}
```

### 🔧 **Escenario 5: Gestión Dinámica**
```json
{
  "description": "Gestión dinámica de proveedores",
  "task": [
    {
      "ai_native": {
        "operator": "set_default_provider",
        "provider": "openai_fast"
      }
    },
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Crear función simple",
        "result": "simple_function"
      }
    },
    {
      "ai_native": {
        "operator": "set_default_provider",
        "provider": "anthropic_quality"
      }
    },
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Crear función compleja",
        "result": "complex_function"
      }
    }
  ]
}
```

## 🎯 Estrategias de Combinación

### 1. **Fallback** (Por Defecto)
- Intenta con cada proveedor hasta que uno funcione
- Útil para alta disponibilidad
- Menor costo (solo usa un proveedor)

### 2. **Parallel**
- Ejecuta con todos los proveedores simultáneamente
- Útil para comparar resultados
- Mayor costo pero más rápido

### 3. **Consensus**
- Obtiene resultados de todos los proveedores
- Selecciona el mejor resultado
- Útil para calidad máxima

## 🔐 Configuración en Meta

Los operadores también pueden usarse en la sección `meta` para configuración global:

```json
{
  "meta": {
    "ai_native": {
      "operator": "setup",
      "provider": "openai_global",
      "type": "openai",
      "api_key": "sk-your-openai-api-key-here"
    }
  },
  "description": "Script con configuración global",
  "task": [
    {
      "ai_native": {
        "operator": "generate_code",
        "description": "Usar proveedor configurado en meta",
        "result": "generated_code"
      }
    }
  ]
}
```

## 🛡️ Seguridad

### ✅ Validaciones Automáticas
- Formato de API keys según el tipo de proveedor
- Validación de permisos antes de usar
- Protección contra exposición de credenciales

### 🔒 Mejores Prácticas
- Usar variables de entorno cuando sea posible
- No incluir API keys en código fuente
- Rotar credenciales regularmente
- Monitorear uso de cada proveedor

## 📊 Monitoreo y Logging

### 📈 Métricas Disponibles
- Tokens usados por proveedor
- Tiempo de respuesta por proveedor
- Tasa de éxito por proveedor
- Costos estimados por proveedor

### 🔍 Logging Detallado
- Configuración de proveedores
- Cambios de proveedor por defecto
- Errores de autenticación
- Uso de estrategias de combinación

---

**🎯 ¡Con estos nuevos operadores, puedes gestionar múltiples proveedores de IA de forma dinámica y crear sistemas robustos de generación de código!**