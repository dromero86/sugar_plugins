# 🚀 Prueba Funcional con OpenAI

## 📋 Requisitos Previos

1. **API Key de OpenAI**: Necesitas una API key válida de OpenAI
2. **Dependencias**: El plugin instalará automáticamente las dependencias necesarias
3. **Sugar**: Asegúrate de tener Sugar v2.0.0+ instalado

## 🔧 Configuración Rápida

### Opción 1: Script Automático (Recomendado)

```bash
# Navegar al directorio del plugin
cd plugins/src/ai_native

# Ejecutar script de configuración
python setup_openai.py
```

El script te pedirá tu API key y configurará todo automáticamente.

### Opción 2: Configuración Manual

```bash
# Instalar dependencias
pip install openai requests aiohttp python-dotenv

# Crear test con tu API key
python quick_test.py "sk-tu-api-key-aqui"
```

## 🎯 Ejecutar Pruebas

### Prueba Simple
```bash
# Prueba básica
virtual/bin/sugar examples/simple_openai_test.json

# Prueba rápida (si usaste quick_test.py)
virtual/bin/sugar quick_openai_test.json
```

### Prueba Completa
```bash
# Prueba completa con todas las funcionalidades
virtual/bin/sugar examples/openai_test.json
```

## 📝 Ejemplos de Prueba

### 1. Generación de Código Simple
```json
{
  "ai_native": {
    "operator": "generate_code",
    "description": "Crear una función que sume dos números",
    "result": "sum_function"
  }
}
```

### 2. Optimización de Código
```json
{
  "ai_native": {
    "operator": "optimize_code",
    "code": "def bubble_sort(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
    "target": "performance",
    "result": "optimized_sort"
  }
}
```

### 3. Lenguaje Natural a Código
```json
{
  "ai_native": {
    "operator": "nl_to_code",
    "query": "Crear un script que lea un archivo CSV y calcule el promedio",
    "result": "csv_processor"
  }
}
```

## 🔍 Verificar Funcionamiento

### 1. Verificar Estado del Plugin
```json
{
  "ai_native": {
    "operator": "get_ai_info",
    "result": "plugin_info"
  }
}
```

### 2. Verificar Modelo Actual
```json
{
  "ai_native": {
    "operator": "get_model_info",
    "result": "model_info"
  }
}
```

### 3. Probar Modelo
```json
{
  "ai_native": {
    "operator": "test_model",
    "prompt": "Crear una función simple",
    "result": "test_result"
  }
}
```

## 🛠️ Solución de Problemas

### Error: "Dependencias no satisfechas"
```bash
# Instalar dependencias manualmente
pip install openai requests aiohttp python-dotenv

# O usar el comando del plugin
# El plugin detectará automáticamente las dependencias
```

### Error: "API key no configurada"
- Asegúrate de que tu API key sea válida
- Verifica que empiece con "sk-"
- Revisa que tengas créditos en tu cuenta de OpenAI

### Error: "Modelo no disponible"
- El plugin usará templates como fallback
- Verifica que las dependencias estén instaladas
- Revisa la configuración del plugin

## 📊 Resultados Esperados

### Con Dependencias Instaladas
- ✅ Modelo: OpenAIModel
- ✅ Tipo: openai
- ✅ Generación de código real
- ✅ Optimización inteligente
- ✅ Procesamiento de lenguaje natural

### Sin Dependencias
- ✅ Modelo: TemplateBasedModel
- ✅ Tipo: template
- ✅ Generación de código con templates
- ✅ Funcionalidad básica preservada

## 🔐 Seguridad

- La API key se guarda localmente
- No se comparte con terceros
- El plugin valida el código generado
- Se aplican filtros de seguridad

## 📞 Soporte

Si encuentras problemas:

1. Verifica que tu API key sea válida
2. Asegúrate de tener créditos en OpenAI
3. Revisa que las dependencias estén instaladas
4. Consulta los logs del plugin

---

**¡Disfruta probando el poder de la IA en Sugar!** 🚀