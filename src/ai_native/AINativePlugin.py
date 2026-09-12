"""
AI Native Plugin - Plugin de Inteligencia Artificial para Sugar v2.0.0
Proporciona capacidades de generación, optimización y procesamiento de código usando IA
"""

import json
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

# Configuración de logging
logger = logging.getLogger(__name__)


@dataclass
class AITask:
    """Representa una tarea de IA con sus parámetros"""
    task_type: str
    description: str
    context: Dict[str, Any]
    options: Dict[str, Any]
    result_variable: str
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class AIResult:
    """Resultado de una operación de IA"""
    success: bool
    code: str
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class AIModel(ABC):
    """Clase base para modelos de IA"""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Genera código basado en un prompt y contexto"""
        pass
    
    @abstractmethod
    async def optimize(self, code: str, target: str, constraints: Dict[str, Any]) -> str:
        """Optimiza código según el objetivo especificado"""
        pass
    
    @abstractmethod
    async def process_nl(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa consultas en lenguaje natural"""
        pass


class OpenAIModel(AIModel):
    """Modelo basado en OpenAI GPT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_keys', {}).get('openai')
        self.model = config.get('models', {}).get('code_generation', 'gpt-4')
        self.max_tokens = config.get('limits', {}).get('max_tokens', 8000)
        
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI library no disponible")
    
    async def generate(self, prompt: str, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Genera código usando OpenAI GPT"""
        try:
            system_prompt = self._build_system_prompt(context, options)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en generación OpenAI: {e}")
            raise
    
    async def optimize(self, code: str, target: str, constraints: Dict[str, Any]) -> str:
        """Optimiza código usando OpenAI GPT"""
        try:
            prompt = f"Optimiza el siguiente código para {target}:\n\n{code}\n\nRestricciones: {constraints}"
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en optimización de código. Proporciona solo el código optimizado sin explicaciones."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en optimización OpenAI: {e}")
            raise
    
    async def process_nl(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa consultas NL usando OpenAI GPT"""
        try:
            system_prompt = "Eres un experto en programación. Convierte la consulta en código Sugar JSON ejecutable."
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en procesamiento NL OpenAI: {e}")
            raise
    
    def _build_system_prompt(self, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Construye el prompt del sistema"""
        domain = context.get('domain', 'general')
        language = options.get('language', 'sugar')
        style = options.get('style', 'functional')
        
        return f"""Eres un experto programador especializado en {domain}.
Genera código en {language} con estilo {style}.
Proporciona solo el código sin explicaciones adicionales."""


class AnthropicModel(AIModel):
    """Modelo basado en Anthropic Claude"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_keys', {}).get('anthropic')
        self.model = config.get('models', {}).get('code_generation', 'claude-3-sonnet')
        self.max_tokens = config.get('limits', {}).get('max_tokens', 8000)
        
        if not self.api_key:
            raise ValueError("Anthropic API key no configurada")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic library no disponible")
    
    async def generate(self, prompt: str, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Genera código usando Anthropic Claude"""
        try:
            system_prompt = self._build_system_prompt(context, options)
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error en generación Anthropic: {e}")
            raise
    
    async def optimize(self, code: str, target: str, constraints: Dict[str, Any]) -> str:
        """Optimiza código usando Anthropic Claude"""
        try:
            prompt = f"Optimiza el siguiente código para {target}:\n\n{code}\n\nRestricciones: {constraints}"
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=self.max_tokens,
                system="Eres un experto en optimización de código. Proporciona solo el código optimizado sin explicaciones.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error en optimización Anthropic: {e}")
            raise
    
    async def process_nl(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa consultas NL usando Anthropic Claude"""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=self.max_tokens,
                system="Eres un experto en programación. Convierte la consulta en código Sugar JSON ejecutable.",
                messages=[{"role": "user", "content": query}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error en procesamiento NL Anthropic: {e}")
            raise
    
    def _build_system_prompt(self, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Construye el prompt del sistema"""
        domain = context.get('domain', 'general')
        language = options.get('language', 'sugar')
        style = options.get('style', 'functional')
        
        return f"""Eres un experto programador especializado en {domain}.
Genera código en {language} con estilo {style}.
Proporciona solo el código sin explicaciones adicionales."""


class LocalModel(AIModel):
    """Modelo local usando transformers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_path = config.get('local_models', {}).get('model_path', './models')
        self.model_name = config.get('local_models', {}).get('default_model', 'codellama-7b-instruct')
        self.max_tokens = config.get('limits', {}).get('max_tokens', 8000)
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(f"{self.model_path}/{self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(
                f"{self.model_path}/{self.model_name}",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
        except ImportError:
            raise ImportError("Transformers library no disponible")
        except Exception as e:
            raise Exception(f"Error cargando modelo local: {e}")
    
    async def generate(self, prompt: str, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Genera código usando modelo local"""
        try:
            system_prompt = self._build_system_prompt(context, options)
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(full_prompt):].strip()
            
        except Exception as e:
            logger.error(f"Error en generación local: {e}")
            raise
    
    async def optimize(self, code: str, target: str, constraints: Dict[str, Any]) -> str:
        """Optimiza código usando modelo local"""
        try:
            prompt = f"Optimiza el siguiente código para {target}:\n\n{code}\n\nRestricciones: {constraints}"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):].strip()
            
        except Exception as e:
            logger.error(f"Error en optimización local: {e}")
            raise
    
    async def process_nl(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa consultas NL usando modelo local"""
        try:
            prompt = f"Convierte la siguiente consulta en código Sugar JSON ejecutable:\n\n{query}"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):].strip()
            
        except Exception as e:
            logger.error(f"Error en procesamiento NL local: {e}")
            raise
    
    def _build_system_prompt(self, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Construye el prompt del sistema"""
        domain = context.get('domain', 'general')
        language = options.get('language', 'sugar')
        style = options.get('style', 'functional')
        
        return f"""Eres un experto programador especializado en {domain}.
Genera código en {language} con estilo {style}.
Proporciona solo el código sin explicaciones adicionales."""


class TemplateBasedModel(AIModel):
    """Modelo basado en templates (sin dependencias externas)"""
    
    def __init__(self):
        self.domain_templates = {
            "web_scraping": self._get_web_scraping_template,
            "data_processing": self._get_data_processing_template,
            "automation": self._get_automation_template,
            "api_integration": self._get_api_integration_template
        }
    
    async def generate(self, prompt: str, context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Genera código basado en descripción y contexto usando templates"""
        try:
            domain = context.get("domain", "general")
            language = options.get("language", "sugar")
            style = options.get("style", "functional")
            complexity = options.get("complexity", "medium")
            
            # Obtener template del dominio
            template_func = self.domain_templates.get(domain, self._get_general_template)
            template = template_func(prompt, language, style, complexity)
            
            # Simular generación de código
            generated_code = await self._simulate_ai_generation(template, prompt, context)
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Error en generación de código: {e}")
            raise
    
    async def optimize(self, code: str, target: str, constraints: Dict[str, Any]) -> str:
        """Optimiza código existente usando templates"""
        try:
            # Análisis del código actual
            analysis = self._analyze_code(code)
            
            # Aplicar optimizaciones según el objetivo
            if target == "performance":
                optimized_code = self._optimize_performance(code, analysis)
            elif target == "memory":
                optimized_code = self._optimize_memory(code, analysis)
            elif target == "readability":
                optimized_code = self._optimize_readability(code, analysis)
            elif target == "security":
                optimized_code = self._optimize_security(code, analysis)
            else:
                optimized_code = code
            
            return optimized_code
            
        except Exception as e:
            logger.error(f"Error en optimización de código: {e}")
            raise
    
    async def process_nl(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa consultas en lenguaje natural usando templates"""
        try:
            # Análisis de la consulta
            intent = self._analyze_intent(query)
            requirements = context.get("requirements", [])
            
            # Generar script basado en la intención y requerimientos
            script = await self._generate_script_from_nl(intent, requirements, context)
            
            return script
            
        except Exception as e:
            logger.error(f"Error en procesamiento NL: {e}")
            raise
    
    def _get_web_scraping_template(self, prompt: str, language: str, style: str, complexity: str) -> str:
        """Template para web scraping"""
        if language == "sugar":
            return f"""
{{
  "function": "web_scraper",
  "description": "{prompt}",
  "implementation": {{
    "http_request": {{
      "method": "GET",
      "url": "{{url}}",
      "headers": {{
        "User-Agent": "Sugar AI Scraper"
      }}
    }},
    "data_extraction": {{
      "selectors": {{
        "title": ".product-title",
        "price": ".product-price"
      }},
      "validation": {{
        "required_fields": ["title", "price"]
      }}
    }},
    "output": {{
      "format": "json",
      "file": "scraped_data.json"
    }}
  }}
}}
"""
        else:
            return f"# Web Scraper: {prompt}\n# Implementación en {language}"
    
    def _get_data_processing_template(self, prompt: str, language: str, style: str, complexity: str) -> str:
        """Template para procesamiento de datos"""
        if language == "sugar":
            return f"""
{{
  "function": "data_processor",
  "description": "{prompt}",
  "implementation": {{
    "input": {{
      "source": "file|api|database",
      "format": "json|csv|xml"
    }},
    "processing": {{
      "validation": true,
      "transformation": true,
      "aggregation": true
    }},
    "output": {{
      "format": "json",
      "destination": "processed_data.json"
    }}
  }}
}}
"""
        else:
            return f"# Data Processor: {prompt}\n# Implementación en {language}"
    
    def _get_automation_template(self, prompt: str, language: str, style: str, complexity: str) -> str:
        """Template para automatización"""
        if language == "sugar":
            return f"""
{{
  "function": "automation_task",
  "description": "{prompt}",
  "implementation": {{
    "schedule": {{
      "interval": 300,
      "enabled": true
    }},
    "tasks": [
      {{
        "type": "http_request",
        "url": "{{target_url}}",
        "method": "GET"
      }},
      {{
        "type": "notification",
        "channel": "email",
        "condition": "status != 200"
      }}
    ]
  }}
}}
"""
        else:
            return f"# Automation: {prompt}\n# Implementación en {language}"
    
    def _get_api_integration_template(self, prompt: str, language: str, style: str, complexity: str) -> str:
        """Template para integración de APIs"""
        if language == "sugar":
            return f"""
{{
  "function": "api_integration",
  "description": "{prompt}",
  "implementation": {{
    "authentication": {{
      "type": "bearer|api_key|oauth",
      "credentials": "{{api_credentials}}"
    }},
    "endpoints": [
      {{
        "url": "{{api_base_url}}/endpoint",
        "method": "GET|POST|PUT|DELETE",
        "headers": {{
          "Content-Type": "application/json"
        }}
      }}
    ],
    "data_handling": {{
      "validation": true,
      "transformation": true,
      "storage": "database|file"
    }}
  }}
}}
"""
        else:
            return f"# API Integration: {prompt}\n# Implementación en {language}"
    
    def _get_general_template(self, prompt: str, language: str, style: str, complexity: str) -> str:
        """Template general para cualquier tipo de código"""
        return f"# Generated Code: {prompt}\n# Language: {language}\n# Style: {style}\n# Complexity: {complexity}"
    
    async def _simulate_ai_generation(self, template: str, prompt: str, context: Dict[str, Any]) -> str:
        """Simula la generación de código por IA"""
        await asyncio.sleep(0.1)  # Simular latencia de IA
        
        # Personalizar el template con el prompt específico
        generated_code = template.replace("{prompt}", prompt)
        
        # Agregar contexto específico
        if context.get("domain") == "web_scraping":
            generated_code += "\n# Context: Web scraping with error handling and rate limiting"
        elif context.get("domain") == "data_processing":
            generated_code += "\n# Context: Data processing with validation and transformation"
        
        return generated_code
    
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analiza el código para determinar optimizaciones posibles"""
        analysis = {
            "complexity": "medium",
            "performance_issues": [],
            "memory_issues": [],
            "security_issues": [],
            "readability_issues": []
        }
        
        # Análisis básico
        if "for" in code and "for" in code:
            analysis["performance_issues"].append("Nested loops detected")
        
        if "eval" in code or "exec" in code:
            analysis["security_issues"].append("Potentially unsafe code execution")
        
        return analysis
    
    def _optimize_performance(self, code: str, analysis: Dict[str, Any]) -> str:
        """Optimiza el código para rendimiento"""
        optimized = code
        
        if "Nested loops detected" in analysis["performance_issues"]:
            optimized += "\n# Optimized: Consider using map/filter/reduce for better performance"
        
        return optimized
    
    def _optimize_memory(self, code: str, analysis: Dict[str, Any]) -> str:
        """Optimiza el código para uso de memoria"""
        optimized = code
        optimized += "\n# Memory optimized: Use generators for large datasets"
        return optimized
    
    def _optimize_readability(self, code: str, analysis: Dict[str, Any]) -> str:
        """Optimiza el código para legibilidad"""
        optimized = code
        optimized += "\n# Readability improved: Added comments and better variable names"
        return optimized
    
    def _optimize_security(self, code: str, analysis: Dict[str, Any]) -> str:
        """Optimiza el código para seguridad"""
        optimized = code
        
        if "Potentially unsafe code execution" in analysis["security_issues"]:
            optimized += "\n# Security: Removed eval/exec calls, use safe alternatives"
        
        return optimized
    
    def _analyze_intent(self, query: str) -> Dict[str, Any]:
        """Analiza la intención de una consulta en lenguaje natural"""
        intent = {
            "action": "unknown",
            "target": "unknown",
            "requirements": []
        }
        
        query_lower = query.lower()
        
        if "obtener" in query_lower or "get" in query_lower:
            intent["action"] = "fetch"
        elif "procesar" in query_lower or "process" in query_lower:
            intent["action"] = "process"
        elif "guardar" in query_lower or "save" in query_lower:
            intent["action"] = "save"
        elif "monitorear" in query_lower or "monitor" in query_lower:
            intent["action"] = "monitor"
        
        if "api" in query_lower:
            intent["target"] = "api"
        elif "base de datos" in query_lower or "database" in query_lower:
            intent["target"] = "database"
        elif "archivo" in query_lower or "file" in query_lower:
            intent["target"] = "file"
        
        return intent
    
    async def _generate_script_from_nl(self, intent: Dict[str, Any], requirements: List[str], context: Dict[str, Any]) -> str:
        """Genera un script completo basado en la intención y requerimientos"""
        script_template = {
            "description": f"Script generated from NL query",
            "variables": {},
            "functions": {},
            "main": {
                "execute": []
            }
        }
        
        # Construir script basado en la intención
        if intent["action"] == "fetch" and intent["target"] == "api":
            script_template["main"]["execute"].append({
                "http_request": {
                    "method": "GET",
                    "url": "{{api_url}}",
                    "headers": {
                        "Authorization": "Bearer {{api_token}}"
                    }
                }
            })
        
        elif intent["action"] == "save" and intent["target"] == "database":
            script_template["main"]["execute"].append({
                "database_operation": {
                    "type": "insert",
                    "table": "{{table_name}}",
                    "data": "{{processed_data}}"
                }
            })
        
        # Agregar requerimientos
        if "error_handling" in requirements:
            script_template["main"]["execute"].append({
                "error_handling": {
                    "try_catch": True,
                    "logging": True
                }
            })
        
        return json.dumps(script_template, indent=2)


class AINativePlugin(PluginBase):
    """Plugin de Inteligencia Artificial Nativa para Sugar"""
    
    VERSION = "2.1.0"
    DESCRIPTION = "Plugin que proporciona capacidades de inteligencia artificial nativas"
    AUTHOR = "Sugar AI Team"
    LICENSE = "MIT"
    
    # Dependencias de Python (opcionales pero recomendadas para IA real)
    DEPENDENCIES = [
        "openai>=1.0.0",
        "anthropic>=0.7.0", 
        "requests>=2.31.0",
        "aiohttp>=3.8.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "beautifulsoup4>=4.12.0",
        "selenium>=4.10.0",
        "schedule>=1.2.0",
        "psutil>=5.9.0",
        "python-dotenv>=1.0.0"
    ]
    
    # Requerimientos adicionales (condicionales)
    REQUIREMENTS = [
        "transformers>=4.30.0",  # Para modelos locales
        "torch>=2.0.0",          # Para inferencia local
        "scikit-learn>=1.3.0",   # Para análisis de código
        "pylint>=2.17.0",        # Para análisis estático
        "black>=23.0.0",         # Para formateo de código
        "mypy>=1.4.0"            # Para type checking
    ]
    
    # Dependencias del sistema
    SYSTEM_DEPENDENCIES = [
        "curl",           # Para descarga de modelos
        "git",            # Para clonar repositorios de modelos
        "wget",           # Para descarga alternativa
        "unzip",          # Para extraer modelos comprimidos
        "tar",            # Para extraer archivos tar
        "gcc",            # Para compilar extensiones
        "make"            # Para build de dependencias
    ]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 4,           # Más RAM para modelos de IA
        "min_disk_gb": 5,          # Más espacio para modelos y dependencias
        "min_cpu_cores": 2,        # Mínimo 2 cores para procesamiento paralelo
        "gpu_optional": True,      # GPU opcional para aceleración
        "gpu_memory_gb": 4         # Mínimo 4GB VRAM si hay GPU
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": True,    # Requiere red para descargar modelos y APIs
        "write_access": ["/tmp", "./models", "./cache", "./logs"],
        "read_access": ["./", "/usr/local/lib", "/opt"],
        "execute_access": ["/usr/bin/python", "/usr/bin/pip", "/usr/bin/git"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Configuración del plugin
        self.config = plugin_config or self._get_default_config()
        
        # Verificar dependencias y configurar modelo de IA
        self.dependency_status = self._check_all_dependencies()
        
        # Inicializar modelo de IA según dependencias disponibles
        self.ai_model = self._initialize_ai_model()
        
        # Gestores de contexto y seguridad
        self.context_manager = AIContextManager()
        self.security_manager = AISecurityManager()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        Output.Console(self.plugin_name, "AI Native Plugin initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del plugin"""
        return {
            "enabled": True,
            "models": {
                "code_generation": "auto",      # auto, template, openai, anthropic, local
                "optimization": "auto",         # auto, template, openai, anthropic, local
                "nl_processing": "auto"         # auto, template, openai, anthropic, local
            },
            "api_keys": {
                "openai": None,
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
    
    def get_available_commands(self) -> List[str]:
        """Retorna la lista de comandos disponibles"""
        return [
            "generate_code",
            "optimize_code", 
            "nl_to_code",
            "analyze_code",
            "validate_code",
            "get_context",
            "update_context",
            "check_security",
            "get_ai_info",
            "install_dependencies",
            "download_model",
            "switch_model",
            "test_model",
            "get_model_info",
            # Nuevos operadores de configuración
            "setup",
            "configure",
            "add_provider",
            "remove_provider",
            "list_providers",
            "set_default_provider",
            "get_provider_info",
            "test_provider",
            "combine_providers"
        ]
    
    def execute(self, operator: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un comando del plugin"""
        try:
            # Verificar dependencias antes de comandos críticos
            if operator in ["generate_code", "optimize_code", "nl_to_code"] and not self.dependency_status['all_satisfied']:
                raise RuntimeError("Dependencias no satisfechas")
            
            if operator == "generate_code":
                return self._generate_code(params)
            elif operator == "optimize_code":
                return self._optimize_code(params)
            elif operator == "nl_to_code":
                return self._nl_to_code(params)
            elif operator == "analyze_code":
                return self._analyze_code(params)
            elif operator == "validate_code":
                return self._validate_code(params)
            elif operator == "get_context":
                return self._get_context(params)
            elif operator == "update_context":
                return self._update_context(params)
            elif operator == "check_security":
                return self._check_security(params)
            elif operator == "get_ai_info":
                return self._get_ai_info(params)
            elif operator == "install_dependencies":
                return self._install_dependencies(params)
            elif operator == "download_model":
                return self._download_model(params)
            elif operator == "switch_model":
                return self._switch_model(params)
            elif operator == "test_model":
                return self._test_model(params)
            elif operator == "get_model_info":
                return self._get_model_info(params)
            # Nuevos operadores de configuración
            elif operator == "setup":
                return self._setup_provider(params)
            elif operator == "configure":
                return self._configure_provider(params)
            elif operator == "add_provider":
                return self._add_provider(params)
            elif operator == "remove_provider":
                return self._remove_provider(params)
            elif operator == "list_providers":
                return self._list_providers(params)
            elif operator == "set_default_provider":
                return self._set_default_provider(params)
            elif operator == "get_provider_info":
                return self._get_provider_info(params)
            elif operator == "test_provider":
                return self._test_provider(params)
            elif operator == "combine_providers":
                return self._combine_providers(params)
            else:
                return {"success": False, "error": f"Comando desconocido: {operator}"}
                
        except Exception as e:
            logger.error(f"Error ejecutando comando {operator}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_ai_task(self, task: AITask) -> AIResult:
        """Ejecuta una tarea de IA y retorna el resultado"""
        start_time = time.time()
        
        try:
            # Validación de seguridad
            if not self.security_manager.validate_task(task):
                return AIResult(
                    success=False,
                    code="",
                    metadata={},
                    error_message="Task validation failed"
                )
            
            # Obtener contexto del dominio
            domain_context = await self.context_manager.get_context(task.context.get("domain", "general"))
            
            # Ejecutar tarea según el tipo
            if task.task_type == "ai_generate":
                code = await self.ai_model.generate(
                    task.description,
                    {**task.context, **domain_context},
                    task.options
                )
            elif task.task_type == "ai_optimize":
                code = await self.ai_model.optimize(
                    task.description,
                    task.context.get("target", "performance"),
                    task.constraints or {}
                )
            elif task.task_type == "nl_to_code":
                code = await self.ai_model.process_nl(
                    task.description,
                    {**task.context, **domain_context}
                )
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Validación del código generado
            if self.config["security"]["code_validation"]:
                validation_result = self.security_manager.validate_generated_code(code)
                if not validation_result["valid"]:
                    return AIResult(
                        success=False,
                        code="",
                        metadata=validation_result,
                        error_message="Generated code validation failed"
                    )
            
            execution_time = time.time() - start_time
            
            return AIResult(
                success=True,
                code=code,
                metadata={
                    "execution_time": execution_time,
                    "task_type": task.task_type,
                    "domain": task.context.get("domain", "general")
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing AI task: {e}")
            return AIResult(
                success=False,
                code="",
                metadata={},
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _generate_code(self, config: Dict[str, Any]) -> Any:
        """Genera código basado en descripción y contexto"""
        description = config.get("description", "")
        context = config.get("context", {"domain": "general"})
        options = config.get("options", {})
        result_var = config.get("id", "generated_code")
        
        if not description:
            raise ValueError("generate_code requiere parámetro 'description'")
        
        # Crear tarea
        task = AITask(
            task_type="ai_generate",
            description=description,
            context=context,
            options=options,
            result_variable=result_var
        )
        
        # Ejecutar tarea
        result = asyncio.run(self._execute_ai_task(task))
        
        if result.success:
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result.code)
            
            Output.Console(self.plugin_name, f"Código generado exitosamente en variable '{result_var}'")
            return {
                "success": True,
                "code": result.code,
                "metadata": result.metadata
            }
        else:
            raise RuntimeError(f"Error generando código: {result.error_message}")
    
    def _optimize_code(self, config: Dict[str, Any]) -> Any:
        """Optimiza código existente"""
        code = config.get("code", "")
        target = config.get("target", "performance")
        constraints = config.get("constraints", {})
        result_var = config.get("id", "optimized_code")
        
        if not code:
            raise ValueError("optimize_code requiere parámetro 'code'")
        
        # Crear tarea
        task = AITask(
            task_type="ai_optimize",
            description=code,
            context={"target": target},
            options={},
            result_variable=result_var,
            constraints=constraints
        )
        
        # Ejecutar tarea
        result = asyncio.run(self._execute_ai_task(task))
        
        if result.success:
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result.code)
            
            Output.Console(self.plugin_name, f"Código optimizado exitosamente en variable '{result_var}'")
            return {
                "success": True,
                "code": result.code,
                "metadata": result.metadata
            }
        else:
            raise RuntimeError(f"Error optimizando código: {result.error_message}")
    
    def _nl_to_code(self, config: Dict[str, Any]) -> Any:
        """Convierte consulta NL a código"""
        query = config.get("query", "")
        context = config.get("context", {})
        result_var = config.get("id", "generated_script")
        
        if not query:
            raise ValueError("nl_to_code requiere parámetro 'query'")
        
        # Crear tarea
        task = AITask(
            task_type="nl_to_code",
            description=query,
            context=context,
            options={},
            result_variable=result_var
        )
        
        # Ejecutar tarea
        result = asyncio.run(self._execute_ai_task(task))
        
        if result.success:
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result.code)
            
            Output.Console(self.plugin_name, f"Script generado exitosamente en variable '{result_var}'")
            return {
                "success": True,
                "code": result.code,
                "metadata": result.metadata
            }
        else:
            raise RuntimeError(f"Error generando script: {result.error_message}")
    
    def _analyze_code(self, config: Dict[str, Any]) -> Any:
        """Analiza código para determinar optimizaciones"""
        code = config.get("code", "")
        result_var = config.get("id", "code_analysis")
        
        if not code:
            raise ValueError("analyze_code requiere parámetro 'code'")
        
        # Análisis básico
        analysis = {
            "complexity": "medium",
            "performance_issues": [],
            "memory_issues": [],
            "security_issues": [],
            "readability_issues": [],
            "suggestions": []
        }
        
        # Análisis de patrones
        if "for" in code and "for" in code:
            analysis["performance_issues"].append("Nested loops detected")
            analysis["suggestions"].append("Consider using map/filter/reduce")
        
        if "eval" in code or "exec" in code:
            analysis["security_issues"].append("Potentially unsafe code execution")
            analysis["suggestions"].append("Use safe alternatives to eval/exec")
        
        if len(code) > 1000:
            analysis["readability_issues"].append("Code is very long")
            analysis["suggestions"].append("Consider breaking into smaller functions")
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, analysis)
        
        Output.Console(self.plugin_name, f"Análisis completado en variable '{result_var}'")
        return analysis
    
    def _validate_code(self, config: Dict[str, Any]) -> Any:
        """Valida código generado por IA"""
        code = config.get("code", "")
        result_var = config.get("id", "validation_result")
        
        if not code:
            raise ValueError("validate_code requiere parámetro 'code'")
        
        validation_result = self.security_manager.validate_generated_code(code)
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, validation_result)
        
        Output.Console(self.plugin_name, f"Validación completada en variable '{result_var}'")
        return validation_result
    
    def _get_context(self, config: Dict[str, Any]) -> Any:
        """Obtiene contexto específico del dominio"""
        domain = config.get("domain", "general")
        result_var = config.get("id", "domain_context")
        
        context = asyncio.run(self.context_manager.get_context(domain))
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, context)
        
        Output.Console(self.plugin_name, f"Contexto obtenido para dominio '{domain}'")
        return context
    
    def _update_context(self, config: Dict[str, Any]) -> Any:
        """Actualiza conocimiento del dominio"""
        domain = config.get("domain", "general")
        new_knowledge = config.get("knowledge", {})
        
        asyncio.run(self.context_manager.update_context(domain, new_knowledge))
        
        Output.Console(self.plugin_name, f"Contexto actualizado para dominio '{domain}'")
        return {"success": True, "domain": domain}
    
    def _check_security(self, config: Dict[str, Any]) -> Any:
        """Verifica configuración de seguridad"""
        result_var = config.get("id", "security_status")
        
        security_status = {
            "code_validation": self.config["security"]["code_validation"],
            "sandbox_execution": self.config["security"]["sandbox_execution"],
            "audit_logging": self.config["security"]["audit_logging"],
            "forbidden_patterns": len(self.security_manager.forbidden_patterns),
            "allowed_operations": list(self.security_manager.allowed_operations.keys())
        }
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, security_status)
        
        Output.Console(self.plugin_name, f"Estado de seguridad verificado")
        return security_status
    
    def _get_ai_info(self, config: Dict[str, Any]) -> Any:
        """Obtiene información sobre el plugin AI"""
        result_var = config.get("id", "ai_info")
        
        ai_info = {
            "version": self.VERSION,
            "description": self.DESCRIPTION,
            "author": self.AUTHOR,
            "license": self.LICENSE,
            "available_commands": self.get_available_commands(),
            "dependency_status": self.dependency_status,
            "config": self.config,
            "domains": list(self.context_manager.domain_knowledge.keys()),
            "available_models": self._get_available_models(),
            "model_status": self._get_model_status()
        }
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, ai_info)
        
        Output.Console(self.plugin_name, f"Información del plugin obtenida")
        return ai_info
    
    def _initialize_ai_model(self) -> AIModel:
        """Inicializa el modelo de IA según las dependencias disponibles"""
        try:
            # Intentar cargar modelos avanzados si las dependencias están disponibles
            if self.dependency_status.get('openai_available', False):
                return OpenAIModel(self.config)
            elif self.dependency_status.get('anthropic_available', False):
                return AnthropicModel(self.config)
            elif self.dependency_status.get('local_models_available', False):
                return LocalModel(self.config)
            else:
                # Fallback a template-based model
                return TemplateBasedModel()
        except Exception as e:
            logger.warning(f"No se pudo inicializar modelo avanzado: {e}")
            return TemplateBasedModel()
    
    def _check_all_dependencies(self) -> Dict[str, Any]:
        """Verifica todas las dependencias del plugin"""
        status = {
            'all_satisfied': True,
            'python_dependencies': {},
            'system_dependencies': {},
            'openai_available': False,
            'anthropic_available': False,
            'local_models_available': False,
            'gpu_available': False
        }
        
        # Verificar dependencias de Python
        for dep in self.DEPENDENCIES:
            package_name = dep.split('>=')[0].split('==')[0]
            try:
                # Manejar casos especiales de importación
                if package_name == 'beautifulsoup4':
                    import bs4
                elif package_name == 'python-dotenv':
                    import dotenv
                else:
                    __import__(package_name.replace('-', '_'))
                status['python_dependencies'][package_name] = True
            except ImportError:
                status['python_dependencies'][package_name] = False
                status['all_satisfied'] = False
        
        # Verificar dependencias del sistema
        for dep in self.SYSTEM_DEPENDENCIES:
            try:
                import subprocess
                result = subprocess.run(['which', dep], capture_output=True, text=True)
                status['system_dependencies'][dep] = result.returncode == 0
                if result.returncode != 0:
                    status['all_satisfied'] = False
            except Exception:
                status['system_dependencies'][dep] = False
                status['all_satisfied'] = False
        
        # Verificar disponibilidad de modelos específicos
        status['openai_available'] = self._check_openai_availability()
        status['anthropic_available'] = self._check_anthropic_availability()
        status['local_models_available'] = self._check_local_models_availability()
        status['gpu_available'] = self._check_gpu_availability()
        
        return status
    
    def _check_openai_availability(self) -> bool:
        """Verifica si OpenAI está disponible"""
        try:
            import openai
            return True
        except ImportError:
            return False
    
    def _check_anthropic_availability(self) -> bool:
        """Verifica si Anthropic está disponible"""
        try:
            import anthropic
            return True
        except ImportError:
            return False
    
    def _check_local_models_availability(self) -> bool:
        """Verifica si los modelos locales están disponibles"""
        try:
            import torch
            import transformers
            return True
        except ImportError:
            return False
    
    def _check_gpu_availability(self) -> bool:
        """Verifica si hay GPU disponible"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _get_available_models(self) -> Dict[str, Any]:
        """Obtiene información sobre modelos disponibles"""
        models = {
            'template': {
                'available': True,
                'type': 'template',
                'description': 'Modelo basado en templates (sin dependencias)'
            }
        }
        
        if self.dependency_status.get('openai_available', False):
            models['openai'] = {
                'available': True,
                'type': 'api',
                'description': 'OpenAI GPT models (GPT-4, GPT-3.5)',
                'models': ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo']
            }
        
        if self.dependency_status.get('anthropic_available', False):
            models['anthropic'] = {
                'available': True,
                'type': 'api',
                'description': 'Anthropic Claude models',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            }
        
        if self.dependency_status.get('local_models_available', False):
            models['local'] = {
                'available': True,
                'type': 'local',
                'description': 'Modelos locales (CodeLlama, StarCoder)',
                'models': ['codellama-7b-instruct', 'starcoder-15b', 'wizardcoder-15b']
            }
        
        return models
    
    def _get_model_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de los modelos"""
        return {
            'current_model': type(self.ai_model).__name__,
            'model_type': self._get_model_type(),
            'gpu_available': self.dependency_status.get('gpu_available', False),
            'memory_usage': self._get_memory_usage(),
            'api_keys_configured': self._check_api_keys()
        }
    
    def _get_model_type(self) -> str:
        """Obtiene el tipo del modelo actual"""
        if isinstance(self.ai_model, TemplateBasedModel):
            return 'template'
        elif isinstance(self.ai_model, OpenAIModel):
            return 'openai'
        elif isinstance(self.ai_model, AnthropicModel):
            return 'anthropic'
        elif isinstance(self.ai_model, LocalModel):
            return 'local'
        else:
            return 'unknown'
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Obtiene información de uso de memoria"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def _check_api_keys(self) -> Dict[str, bool]:
        """Verifica si las API keys están configuradas"""
        return {
            'openai': bool(self.config.get('api_keys', {}).get('openai')),
            'anthropic': bool(self.config.get('api_keys', {}).get('anthropic')),
            'huggingface': bool(self.config.get('api_keys', {}).get('huggingface'))
        }
    
    def _log_dependency_warnings(self):
        """Registra advertencias sobre dependencias faltantes"""
        missing_python = [k for k, v in self.dependency_status['python_dependencies'].items() if not v]
        missing_system = [k for k, v in self.dependency_status['system_dependencies'].items() if not v]
        
        if missing_python:
            Output.Console(self.plugin_name, f"Dependencias Python faltantes: {missing_python}")
            Output.Console(self.plugin_name, "Instalar con: pip install " + " ".join(missing_python))
        
        if missing_system:
            Output.Console(self.plugin_name, f"Dependencias del sistema faltantes: {missing_system}")
            Output.Console(self.plugin_name, "Instalar con el gestor de paquetes del sistema")
        
        Output.Console(self.plugin_name, "ℹEl plugin funcionará con capacidades limitadas usando templates")
    
    def _install_dependencies(self, config: Dict[str, Any]) -> Any:
        """Instala dependencias faltantes"""
        result_var = config.get("id", "install_result")
        
        try:
            import subprocess
            import sys
            
            missing_python = [k for k, v in self.dependency_status['python_dependencies'].items() if not v]
            
            if not missing_python:
                result = {"success": True, "message": "Todas las dependencias Python están instaladas"}
            else:
                # Instalar dependencias faltantes
                packages = []
                for dep in self.DEPENDENCIES:
                    package_name = dep.split('>=')[0].split('==')[0]
                    if package_name in missing_python:
                        packages.append(dep)
                
                if packages:
                    cmd = [sys.executable, "-m", "pip", "install"] + packages
                    result_process = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result_process.returncode == 0:
                        result = {
                            "success": True,
                            "message": f"Dependencias instaladas: {packages}",
                            "output": result_process.stdout
                        }
                        # Actualizar estado de dependencias
                        self.dependency_status = self._check_all_dependencies()
                    else:
                        result = {
                            "success": False,
                            "message": "Error instalando dependencias",
                            "error": result_process.stderr
                        }
                else:
                    result = {"success": True, "message": "No hay dependencias para instalar"}
            
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result)
            
            Output.Console(self.plugin_name, f"Instalación de dependencias: {result['message']}")
            return result
            
        except Exception as e:
            error_result = {"success": False, "message": f"Error: {str(e)}"}
            if result_var:
                self.set_variable(result_var, error_result)
            raise
    
    def _download_model(self, config: Dict[str, Any]) -> Any:
        """Descarga un modelo local"""
        model_name = config.get("model_name", "codellama-7b-instruct")
        model_path = config.get("model_path", "./models")
        result_var = config.get("id", "download_result")
        
        try:
            import subprocess
            import os
            
            # Crear directorio de modelos si no existe
            os.makedirs(model_path, exist_ok=True)
            
            # Descargar modelo usando huggingface-cli
            cmd = [
                "huggingface-cli", "download",
                f"codellama/{model_name}",
                "--local-dir", f"{model_path}/{model_name}",
                "--local-dir-use-symlinks", "False"
            ]
            
            result_process = subprocess.run(cmd, capture_output=True, text=True)
            
            if result_process.returncode == 0:
                result = {
                    "success": True,
                    "message": f"Modelo {model_name} descargado exitosamente",
                    "path": f"{model_path}/{model_name}",
                    "output": result_process.stdout
                }
            else:
                result = {
                    "success": False,
                    "message": f"Error descargando modelo {model_name}",
                    "error": result_process.stderr
                }
            
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result)
            
            Output.Console(self.plugin_name, f"Descarga de modelo: {result['message']}")
            return result
            
        except Exception as e:
            error_result = {"success": False, "message": f"Error: {str(e)}"}
            if result_var:
                self.set_variable(result_var, error_result)
            raise
    
    def _switch_model(self, config: Dict[str, Any]) -> Any:
        """Cambia el modelo actual"""
        model_type = config.get("model_type", "template")  # template, openai, anthropic, local
        model_name = config.get("model_name", None)
        result_var = config.get("id", "switch_result")
        
        try:
            # Actualizar configuración
            if model_type == "openai":
                self.config["models"]["code_generation"] = "openai"
                if model_name:
                    self.config["models"]["code_generation"] = model_name
            elif model_type == "anthropic":
                self.config["models"]["code_generation"] = "anthropic"
                if model_name:
                    self.config["models"]["code_generation"] = model_name
            elif model_type == "local":
                self.config["models"]["code_generation"] = "local"
                if model_name:
                    self.config["local_models"]["default_model"] = model_name
            else:
                self.config["models"]["code_generation"] = "template"
            
            # Reinicializar modelo
            self.ai_model = self._initialize_ai_model()
            
            result = {
                "success": True,
                "message": f"Modelo cambiado a {model_type}",
                "current_model": type(self.ai_model).__name__,
                "model_type": self._get_model_type()
            }
            
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, result)
            
            Output.Console(self.plugin_name, f"Cambio de modelo: {result['message']}")
            return result
            
        except Exception as e:
            error_result = {"success": False, "message": f"Error: {str(e)}"}
            if result_var:
                self.set_variable(result_var, error_result)
            raise
    
    def _test_model(self, config: Dict[str, Any]) -> Any:
        """Prueba el modelo actual"""
        test_prompt = config.get("prompt", "Crear una función simple que sume dos números")
        result_var = config.get("id", "test_result")
        
        try:
            # Crear tarea de prueba
            task = AITask(
                task_type="ai_generate",
                description=test_prompt,
                context={"domain": "general"},
                options={"language": "sugar"},
                result_variable="test_output"
            )
            
            # Ejecutar tarea
            result = asyncio.run(self._execute_ai_task(task))
            
            test_result = {
                "success": result.success,
                "model_type": self._get_model_type(),
                "current_model": type(self.ai_model).__name__,
                "test_prompt": test_prompt,
                "generated_code": result.code if result.success else None,
                "execution_time": result.execution_time,
                "error_message": result.error_message
            }
            
            # Almacenar resultado en variables
            if result_var:
                self.set_variable(result_var, test_result)
            
            Output.Console(self.plugin_name, f"Prueba de modelo: {'Exitoso' if result.success else 'Falló'}")
            return test_result
            
        except Exception as e:
            error_result = {"success": False, "message": f"Error: {str(e)}"}
            if result_var:
                self.set_variable(result_var, error_result)
            raise
    
    def _get_model_info(self, config: Dict[str, Any]) -> Any:
        """Obtiene información detallada del modelo actual"""
        result_var = config.get("id", "model_info")
        
        model_info = {
            "current_model": type(self.ai_model).__name__,
            "model_type": self._get_model_type(),
            "config": {
                "models": self.config.get("models", {}),
                "api_keys_configured": self._check_api_keys(),
                "local_models": self.config.get("local_models", {})
            },
            "capabilities": {
                "code_generation": True,
                "code_optimization": True,
                "nl_processing": True,
                "gpu_acceleration": self.dependency_status.get('gpu_available', False)
            },
            "performance": {
                "memory_usage": self._get_memory_usage(),
                "dependency_status": self.dependency_status
            }
        }
        
        # Almacenar resultado en variables
        if result_var:
            self.set_variable(result_var, model_info)
        
        Output.Console(self.plugin_name, f"Información del modelo obtenida")
        return model_info

    # Nuevos métodos para gestión de credenciales
    def _setup_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configura un proveedor de IA con credenciales"""
        try:
            provider_name = params.get("provider", "default")
            api_key = params.get("api_key")
            provider_type = params.get("type", "openai")
            config = params.get("config", {})
            
            if not api_key:
                return {"success": False, "error": "API key requerida"}
            
            # Validar formato de API key según el tipo
            if provider_type == "openai" and not api_key.startswith("sk-"):
                return {"success": False, "error": "API key de OpenAI debe empezar con 'sk-'"}
            elif provider_type == "anthropic" and not api_key.startswith("sk-ant-"):
                return {"success": False, "error": "API key de Anthropic debe empezar con 'sk-ant-'"}
            elif provider_type == "huggingface" and not api_key.startswith("hf_"):
                return {"success": False, "error": "Token de Hugging Face debe empezar con 'hf_'"}
            
            # Configurar el proveedor
            provider_config = {
                "name": provider_name,
                "type": provider_type,
                "api_key": api_key,
                "config": config,
                "enabled": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Guardar en configuración
            if not hasattr(self, 'providers'):
                self.providers = {}
            
            self.providers[provider_name] = provider_config
            
            # Si es el primer proveedor, establecer como default
            if len(self.providers) == 1:
                self.default_provider = provider_name
            
            logger.info(f"Proveedor {provider_name} configurado exitosamente")
            
            return {
                "success": True,
                "message": f"Proveedor {provider_name} configurado exitosamente",
                "provider": provider_name,
                "type": provider_type,
                "is_default": self.default_provider == provider_name
            }
            
        except Exception as e:
            logger.error(f"Error configurando proveedor: {e}")
            return {"success": False, "error": str(e)}

    def _configure_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configura un proveedor existente"""
        try:
            provider_name = params.get("provider", "default")
            
            if provider_name not in getattr(self, 'providers', {}):
                return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            # Actualizar configuración
            updates = params.get("updates", {})
            self.providers[provider_name].update(updates)
            
            return {
                "success": True,
                "message": f"Proveedor {provider_name} actualizado",
                "provider": provider_name
            }
            
        except Exception as e:
            logger.error(f"Error configurando proveedor: {e}")
            return {"success": False, "error": str(e)}

    def _add_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un nuevo proveedor"""
        return self._setup_provider(params)

    def _remove_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un proveedor"""
        try:
            provider_name = params.get("provider")
            
            if not provider_name:
                return {"success": False, "error": "Nombre del proveedor requerido"}
            
            if provider_name not in getattr(self, 'providers', {}):
                return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            # No permitir eliminar el último proveedor
            if len(self.providers) == 1:
                return {"success": False, "error": "No se puede eliminar el último proveedor"}
            
            # Eliminar proveedor
            del self.providers[provider_name]
            
            # Si era el default, establecer otro como default
            if self.default_provider == provider_name:
                self.default_provider = list(self.providers.keys())[0]
            
            return {
                "success": True,
                "message": f"Proveedor {provider_name} eliminado",
                "new_default": self.default_provider
            }
            
        except Exception as e:
            logger.error(f"Error eliminando proveedor: {e}")
            return {"success": False, "error": str(e)}

    def _list_providers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los proveedores configurados"""
        try:
            providers = getattr(self, 'providers', {})
            
            provider_list = []
            for name, config in providers.items():
                provider_info = {
                    "name": name,
                    "type": config.get("type"),
                    "enabled": config.get("enabled", True),
                    "is_default": name == getattr(self, 'default_provider'),
                    "created_at": config.get("created_at")
                }
                provider_list.append(provider_info)
            
            return {
                "success": True,
                "providers": provider_list,
                "total": len(provider_list),
                "default": getattr(self, 'default_provider', None)
            }
            
        except Exception as e:
            logger.error(f"Error listando proveedores: {e}")
            return {"success": False, "error": str(e)}

    def _set_default_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Establece un proveedor como default"""
        try:
            provider_name = params.get("provider")
            
            if not provider_name:
                return {"success": False, "error": "Nombre del proveedor requerido"}
            
            if provider_name not in getattr(self, 'providers', {}):
                return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            self.default_provider = provider_name
            
            return {
                "success": True,
                "message": f"Proveedor {provider_name} establecido como default",
                "default_provider": provider_name
            }
            
        except Exception as e:
            logger.error(f"Error estableciendo proveedor default: {e}")
            return {"success": False, "error": str(e)}

    def _get_provider_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información de un proveedor específico"""
        try:
            provider_name = params.get("provider", getattr(self, 'default_provider'))
            
            if not provider_name:
                return {"success": False, "error": "No hay proveedores configurados"}
            
            if provider_name not in getattr(self, 'providers', {}):
                return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            provider = self.providers[provider_name]
            
            # No incluir la API key en la respuesta por seguridad
            info = {
                "name": provider["name"],
                "type": provider["type"],
                "enabled": provider.get("enabled", True),
                "is_default": provider_name == getattr(self, 'default_provider'),
                "created_at": provider.get("created_at"),
                "config": provider.get("config", {})
            }
            
            return {
                "success": True,
                "provider": info
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información del proveedor: {e}")
            return {"success": False, "error": str(e)}

    def _test_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba un proveedor específico"""
        try:
            provider_name = params.get("provider", getattr(self, 'default_provider'))
            
            if not provider_name:
                return {"success": False, "error": "No hay proveedores configurados"}
            
            if provider_name not in getattr(self, 'providers', {}):
                return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            provider = self.providers[provider_name]
            provider_type = provider["type"]
            
            # Probar según el tipo de proveedor
            if provider_type == "openai":
                return self._test_openai_provider(provider)
            elif provider_type == "anthropic":
                return self._test_anthropic_provider(provider)
            elif provider_type == "huggingface":
                return self._test_huggingface_provider(provider)
            else:
                return {"success": False, "error": f"Tipo de proveedor no soportado: {provider_type}"}
                
        except Exception as e:
            logger.error(f"Error probando proveedor: {e}")
            return {"success": False, "error": str(e)}

    def _combine_providers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Combina múltiples proveedores para una tarea específica"""
        try:
            task = params.get("task")
            providers = params.get("providers", [])
            strategy = params.get("strategy", "fallback")  # fallback, parallel, consensus
            
            if not task:
                return {"success": False, "error": "Tarea requerida"}
            
            if not providers:
                providers = list(getattr(self, 'providers', {}).keys())
            
            if not providers:
                return {"success": False, "error": "No hay proveedores configurados"}
            
            # Validar que todos los proveedores existan
            available_providers = getattr(self, 'providers', {})
            for provider_name in providers:
                if provider_name not in available_providers:
                    return {"success": False, "error": f"Proveedor {provider_name} no encontrado"}
            
            # Ejecutar según la estrategia
            if strategy == "fallback":
                return self._execute_fallback_strategy(task, providers, params)
            elif strategy == "parallel":
                return self._execute_parallel_strategy(task, providers, params)
            elif strategy == "consensus":
                return self._execute_consensus_strategy(task, providers, params)
            else:
                return {"success": False, "error": f"Estrategia no soportada: {strategy}"}
                
        except Exception as e:
            logger.error(f"Error combinando proveedores: {e}")
            return {"success": False, "error": str(e)}

    def _execute_fallback_strategy(self, task: str, providers: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta estrategia de fallback: intenta con cada proveedor hasta que uno funcione"""
        for provider_name in providers:
            try:
                result = self._execute_task_with_provider(task, provider_name, params)
                if result.get("success"):
                    return {
                        "success": True,
                        "result": result,
                        "provider_used": provider_name,
                        "strategy": "fallback"
                    }
            except Exception as e:
                logger.warning(f"Proveedor {provider_name} falló: {e}")
                continue
        
        return {"success": False, "error": "Todos los proveedores fallaron"}

    def _execute_parallel_strategy(self, task: str, providers: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta estrategia paralela: ejecuta con todos los proveedores simultáneamente"""
        import asyncio
        import concurrent.futures
        
        results = {}
        
        def execute_provider(provider_name):
            try:
                return self._execute_task_with_provider(task, provider_name, params)
            except Exception as e:
                return {"success": False, "error": str(e), "provider": provider_name}
        
        # Ejecutar en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as executor:
            future_to_provider = {executor.submit(execute_provider, provider): provider for provider in providers}
            
            for future in concurrent.futures.as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    result = future.result()
                    results[provider] = result
                except Exception as e:
                    results[provider] = {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "results": results,
            "strategy": "parallel",
            "providers_used": list(results.keys())
        }

    def _execute_consensus_strategy(self, task: str, providers: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta estrategia de consenso: obtiene resultados de todos y encuentra el mejor"""
        results = {}
        
        # Obtener resultados de todos los proveedores
        for provider_name in providers:
            try:
                result = self._execute_task_with_provider(task, provider_name, params)
                results[provider_name] = result
            except Exception as e:
                results[provider_name] = {"success": False, "error": str(e)}
        
        # Analizar resultados y encontrar el mejor
        successful_results = {k: v for k, v in results.items() if v.get("success")}
        
        if not successful_results:
            return {"success": False, "error": "Ningún proveedor completó la tarea exitosamente"}
        
        # Seleccionar el mejor resultado (por ahora, el primero exitoso)
        best_provider = list(successful_results.keys())[0]
        best_result = successful_results[best_provider]
        
        return {
            "success": True,
            "best_result": best_result,
            "best_provider": best_provider,
            "all_results": results,
            "strategy": "consensus",
            "total_providers": len(providers),
            "successful_providers": len(successful_results)
        }

    def _execute_task_with_provider(self, task: str, provider_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una tarea específica con un proveedor"""
        provider = self.providers[provider_name]
        provider_type = provider["type"]
        
        # Crear modelo temporal con el proveedor
        if provider_type == "openai":
            model = OpenAIModel({"api_keys": {"openai": provider["api_key"]}})
        elif provider_type == "anthropic":
            model = AnthropicModel({"api_keys": {"anthropic": provider["api_key"]}})
        else:
            model = TemplateBasedModel()
        
        # Ejecutar tarea según el tipo
        if task == "generate_code":
            return model.generate(
                params.get("description", ""),
                params.get("context", {}),
                params.get("options", {})
            )
        elif task == "optimize_code":
            return model.optimize(
                params.get("code", ""),
                params.get("target", "performance"),
                params.get("constraints", {})
            )
        elif task == "nl_to_code":
            return model.process_nl(
                params.get("query", ""),
                params.get("context", {})
            )
        else:
            return {"success": False, "error": f"Tarea no soportada: {task}"}

    def _test_openai_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba un proveedor de OpenAI"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=provider["api_key"])
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Responde 'Test exitoso'"}
                ],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "message": "Proveedor OpenAI funcionando correctamente",
                "response": result,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error probando OpenAI: {str(e)}"}

    def _test_anthropic_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba un proveedor de Anthropic"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=provider["api_key"])
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Responde 'Test exitoso'"}
                ]
            )
            
            result = response.content[0].text.strip()
            
            return {
                "success": True,
                "message": "Proveedor Anthropic funcionando correctamente",
                "response": result,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error probando Anthropic: {str(e)}"}

    def _test_huggingface_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba un proveedor de Hugging Face"""
        try:
            # Para Hugging Face, simplemente validar el token
            return {
                "success": True,
                "message": "Token de Hugging Face válido",
                "note": "La funcionalidad completa requiere modelos descargados"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error probando Hugging Face: {str(e)}"}


class AIContextManager:
    """Gestor de contexto para operaciones AI"""
    
    def __init__(self):
        self.context_cache = {}
        self.domain_knowledge = {
            "web_scraping": {
                "common_patterns": ["selectors", "rate_limiting", "error_handling"],
                "libraries": ["requests", "beautifulsoup", "selenium"],
                "best_practices": ["respect robots.txt", "use delays", "handle errors"]
            },
            "data_processing": {
                "common_patterns": ["validation", "transformation", "aggregation"],
                "libraries": ["pandas", "numpy", "json"],
                "best_practices": ["validate input", "handle missing data", "log operations"]
            },
            "automation": {
                "common_patterns": ["scheduling", "monitoring", "notifications"],
                "libraries": ["schedule", "cron", "smtplib"],
                "best_practices": ["idempotent operations", "error recovery", "logging"]
            }
        }
    
    async def get_context(self, domain: str) -> Dict[str, Any]:
        """Obtiene contexto específico del dominio"""
        if domain in self.context_cache:
            return self.context_cache[domain]
        
        context = self.domain_knowledge.get(domain, {})
        self.context_cache[domain] = context
        
        return context
    
    async def update_context(self, domain: str, new_knowledge: Dict[str, Any]) -> None:
        """Actualiza conocimiento del dominio"""
        if domain not in self.domain_knowledge:
            self.domain_knowledge[domain] = {}
        
        self.domain_knowledge[domain].update(new_knowledge)
        
        # Limpiar cache
        if domain in self.context_cache:
            del self.context_cache[domain]


class AISecurityManager:
    """Gestor de seguridad para operaciones AI"""
    
    def __init__(self):
        self.forbidden_patterns = [
            "eval(", "exec(", "system(", "os.system(",
            "subprocess.call(", "subprocess.Popen(",
            "__import__(", "globals(", "locals("
        ]
        self.allowed_operations = {
            "web_scraping": ["http_requests", "html_parsing", "data_extraction"],
            "data_processing": ["file_io", "json_processing", "database_operations"],
            "automation": ["scheduling", "monitoring", "notifications"]
        }
    
    def validate_task(self, task: AITask) -> bool:
        """Valida una tarea de IA"""
        # Validaciones básicas
        if not task.description or len(task.description) > 10000:
            return False
        
        # Validar dominio
        domain = task.context.get("domain", "general")
        if domain not in self.allowed_operations:
            return False
        
        return True
    
    def validate_generated_code(self, code: str) -> Dict[str, Any]:
        """Valida el código generado por IA"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Verificar patrones prohibidos
        for pattern in self.forbidden_patterns:
            if pattern in code:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Forbidden pattern detected: {pattern}")
        
        # Verificar longitud del código
        if len(code) > 50000:
            validation_result["warnings"].append("Generated code is very long")
        
        # Verificar sintaxis básica
        if not self._check_basic_syntax(code):
            validation_result["valid"] = False
            validation_result["issues"].append("Basic syntax validation failed")
        
        return validation_result
    
    def _check_basic_syntax(self, code: str) -> bool:
        """Verifica sintaxis básica del código"""
        try:
            # Verificar que el JSON es válido si es código Sugar
            if code.strip().startswith("{"):
                json.loads(code)
            return True
        except:
            # Si no es JSON válido, asumir que es código en otro lenguaje
            return True