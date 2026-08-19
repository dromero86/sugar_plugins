#!/usr/bin/env python3
"""
Script de configuración para OpenAI en el plugin AI Native
"""

import json
import os
import sys

def setup_openai_config(api_key):
    """Configura la API key de OpenAI para el plugin"""
    
    # Configuración del plugin con OpenAI
    config = {
        "ai_native_config": {
            "enabled": True,
            "models": {
                "code_generation": "openai",
                "optimization": "openai", 
                "nl_processing": "openai"
            },
            "api_keys": {
                "openai": api_key,
                "anthropic": None,
                "huggingface": None
            },
            "local_models": {
                "enabled": False,
                "model_path": "./models",
                "default_model": "codellama-7b-instruct"
            },
            "limits": {
                "max_tokens": 8000,
                "max_execution_time": 60,
                "max_memory_usage": "2GB",
                "max_concurrent_requests": 5
            },
            "security": {
                "code_validation": True,
                "sandbox_execution": True,
                "audit_logging": True,
                "rate_limiting": True,
                "content_filtering": True
            },
            "cache": {
                "enabled": True,
                "max_size": "1GB",
                "ttl_hours": 24
            }
        }
    }
    
    # Guardar configuración
    config_file = "openai_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuración guardada en {config_file}")
    print(f"API Key configurada: {api_key[:10]}...")
    
    return config_file

def create_test_script(api_key):
    """Crea un script de prueba con la API key"""
    
    # Leer el template de prueba
    template_file = "examples/openai_test.json"
    
    if os.path.exists(template_file):
        with open(template_file, 'r') as f:
            test_data = json.load(f)
        
        # Reemplazar la API key en el template
        test_data["variables"]["openai_api_key"]["value"] = api_key
        
        # Guardar script de prueba
        test_file = "openai_test_configured.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"Script de prueba creado: {test_file}")
        return test_file
    else:
        print(f"No se encontró el template: {template_file}")
        return None

def install_dependencies():
    """Instala las dependencias necesarias"""
    
    print("Instalando dependencias...")
    
    try:
        import subprocess
        import sys
        
        # Dependencias básicas para OpenAI
        dependencies = [
            "openai>=1.0.0",
            "requests>=2.31.0",
            "aiohttp>=3.8.0",
            "python-dotenv>=1.0.0"
        ]
        
        for dep in dependencies:
            print(f"Instalando {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{dep} instalado correctamente")
            else:
                print(f"Error instalando {dep}: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"Error instalando dependencias: {e}")
        return False

def main():
    """Función principal"""
    
    print("Configuración del Plugin AI Native con OpenAI")
    print("=" * 50)
    
    # Solicitar API key
    api_key = input("Ingresa tu API key de OpenAI: ").strip()
    
    if not api_key:
        print("API key requerida")
        return
    
    if not api_key.startswith("sk-"):
        print("API key inválida (debe empezar con 'sk-')")
        return
    
    print("\nConfigurando plugin...")
    
    # Configurar plugin
    config_file = setup_openai_config(api_key)
    
    # Crear script de prueba
    test_file = create_test_script(api_key)
    
    # Instalar dependencias
    print("\nVerificando dependencias...")
    deps_ok = install_dependencies()
    
    print("\nConfiguración completada!")
    print("=" * 50)
    
    if deps_ok and test_file:
        print(f"Para ejecutar la prueba:")
        print(f"   virtual/bin/sugar {test_file}")
        print(f"\nPara usar la configuración:")
        print(f"   virtual/bin/sugar --config {config_file} {test_file}")
    
    print("\nNotas:")
    print("- El plugin detectará automáticamente OpenAI")
    print("- Si no hay dependencias, usará templates como fallback")
    print("- La API key se guarda localmente (no la compartas)")

if __name__ == "__main__":
    main()