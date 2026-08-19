#!/usr/bin/env python3
"""
Script de configuración segura para el plugin AI Native
"""

import os
import json
import getpass
from pathlib import Path

def create_secure_config():
    """Crea una configuración segura para el plugin"""
    
    print("Configuración Segura - Plugin AI Native")
    print("=" * 50)
    
    # Verificar si ya existe configuración
    config_file = Path("ai_native_config.json")
    if config_file.exists():
        print("Ya existe un archivo de configuración")
        response = input("¿Deseas sobrescribirlo? (y/N): ").strip().lower()
        if response != 'y':
            print("Configuración cancelada")
            return
    
    # Solicitar API keys de forma segura
    print("\nConfiguración de API Keys")
    print("(Presiona Enter para omitir si no tienes la API key)")
    
    openai_key = getpass.getpass("OpenAI API Key: ").strip()
    anthropic_key = getpass.getpass("Anthropic API Key: ").strip()
    huggingface_key = getpass.getpass("Hugging Face Token: ").strip()
    
    # Configuración del plugin
    config = {
        "ai_native_config": {
            "enabled": True,
            "models": {
                "code_generation": "auto",
                "optimization": "auto",
                "nl_processing": "auto"
            },
            "api_keys": {
                "openai": openai_key if openai_key else None,
                "anthropic": anthropic_key if anthropic_key else None,
                "huggingface": huggingface_key if huggingface_key else None
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
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguración guardada en {config_file}")
    
    # Crear .env si hay API keys
    if any([openai_key, anthropic_key, huggingface_key]):
        env_file = Path(".env")
        env_content = []
        
        if openai_key:
            env_content.append(f"OPENAI_API_KEY={openai_key}")
        if anthropic_key:
            env_content.append(f"ANTHROPIC_API_KEY={anthropic_key}")
        if huggingface_key:
            env_content.append(f"HUGGINGFACE_TOKEN={huggingface_key}")
        
        with open(env_file, 'w') as f:
            f.write("\n".join(env_content))
        
        print(f"Variables de entorno guardadas en {env_file}")
        print("IMPORTANTE: Agrega .env a tu .gitignore")
    
    # Crear .gitignore si no existe
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_content = """# API Keys y Configuración Sensible
.env
*.key
*.pem
config.json
secrets.json
api_keys.json
ai_native_config.json

# Archivos de Test con API Keys Reales
test_*.py
*_with_api_key.json
*_test.py
*_demo.py

# Logs y Archivos Temporales
*.log
*.tmp
*.cache
logs/
temp/
cache/

# Modelos Descargados
models/
*.bin
*.safetensors
*.gguf

# Archivos de Configuración Local
local_config.json
user_config.json
"""
        
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        
        print(f".gitignore creado para proteger información sensible")
    
    print("\nConfiguración completada!")
    print("\nPara usar el plugin:")
    print("   1. Instalar dependencias: pip install openai anthropic")
    print("   2. Ejecutar Sugar con el plugin")
    print("   3. ¡Disfrutar de la generación de código con IA!")

def create_env_template():
    """Crea un template de archivo .env"""
    
    print("\nCreando template de .env")
    
    env_template = """# API Keys para el plugin AI Native
# Reemplaza con tus API keys reales

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key (opcional)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Hugging Face Token (opcional)
HUGGINGFACE_TOKEN=hf-your-huggingface-token-here

# Configuración adicional
AI_NATIVE_CACHE_SIZE=1GB
AI_NATIVE_MAX_TOKENS=8000
"""
    
    with open(".env.template", 'w') as f:
        f.write(env_template)
    
    print("Template .env.template creado")
    print("Copia .env.template a .env y agrega tus API keys reales")

def main():
    """Función principal"""
    
    print("Configuración Segura - Plugin AI Native")
    print("=" * 50)
    
    print("Opciones:")
    print("1. Configuración interactiva (recomendado)")
    print("2. Crear template de .env")
    print("3. Salir")
    
    choice = input("\nSelecciona una opción (1-3): ").strip()
    
    if choice == "1":
        create_secure_config()
    elif choice == "2":
        create_env_template()
    elif choice == "3":
        print("¡Hasta luego!")
    else:
        print("Opción inválida")

if __name__ == "__main__":
    main()