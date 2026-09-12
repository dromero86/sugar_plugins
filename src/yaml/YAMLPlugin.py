"""
YAML Plugin for Sugar Language

This plugin provides YAML support for Sugar Language, allowing users to write
Sugar scripts using YAML syntax instead of JSON. It includes file processing,
conversion tools, and validation capabilities.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output


class YAMLPlugin(PluginBase):
    """
    YAML Plugin for Sugar Language
    
    Provides YAML support including:
    - File processing (.yml, .yaml files)
    - JSON to YAML conversion
    - YAML validation
    - Dynamic CLI parameter registration
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "YAML support for Sugar Language - write Sugar scripts using YAML syntax"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias de Python
    DEPENDENCIES = ["pyyaml"]
    REQUIREMENTS = ["pyyaml>=6.0"]
    
    # Dependencias del sistema
    SYSTEM_DEPENDENCIES = []
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 1,
        "min_disk_gb": 0.1,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": False,
        "write_access": ["./output"],
        "read_access": ["./"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Verificar dependencias básicas
        self.dependency_status = self._check_dependencies()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Inicializar funcionalidades si las dependencias están satisfechas
        if self.dependency_status['all_satisfied']:
            self._initialize_plugin()
            
        # Registrar parámetros CLI dinámicamente
        self._register_cli_parameters()
    
    def get_available_commands(self) -> List[str]:
        """Retorna los comandos disponibles del plugin"""
        return [
            "process_file",
            "convert_json_to_yaml", 
            "validate_yaml",
            "convert_directory",
            "register_cli"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Ejecuta un comando del plugin"""
        
        # Verificar dependencias antes de comandos críticos
        if operator in ["process_file", "convert_json_to_yaml"] and not self.dependency_status['all_satisfied']:
            raise RuntimeError("Dependencias no satisfechas. Instala PyYAML: pip install pyyaml")
        
        if operator == "process_file":
            return self._process_file(config)
        elif operator == "convert_json_to_yaml":
            return self._convert_json_to_yaml(config)
        elif operator == "validate_yaml":
            return self._validate_yaml(config)
        elif operator == "convert_directory":
            return self._convert_directory(config)
        elif operator == "register_cli":
            return self._register_cli_parameters()
        else:
            raise ValueError(f"Comando desconocido: {operator}")
    
    def _process_file(self, config: Dict[str, Any]) -> Any:
        """Procesa un archivo YAML"""
        file_path = config.get("file_path")
        if not file_path:
            raise ValueError("Parámetro 'file_path' requerido")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Procesar con el servicio de Sugar
            if self.context and hasattr(self.context, 'process_json'):
                self.context.process_json(data)
                result = {"status": "success", "message": f"Archivo YAML procesado: {file_path}"}
            else:
                result = {"status": "success", "data": data, "message": f"Archivo YAML parseado: {file_path}"}
            
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
            
        except yaml.YAMLError as e:
            error_msg = f"Error parseando YAML: {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error procesando archivo YAML: {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise
    
    def _convert_json_to_yaml(self, config: Dict[str, Any]) -> Any:
        """Convierte un archivo JSON a YAML"""
        json_file = config.get("json_file")
        yaml_file = config.get("yaml_file")
        pretty = config.get("pretty", True)
        
        if not json_file:
            raise ValueError("Parámetro 'json_file' requerido")
        
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Archivo JSON no encontrado: {json_file}")
        
        try:
            # Leer archivo JSON
            import json
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determinar archivo de salida
            if yaml_file is None:
                json_path = Path(json_file)
                yaml_file = str(json_path.with_suffix('.yaml'))
            
            # Configurar formato YAML
            if pretty:
                yaml_content = yaml.dump(
                    data, 
                    default_flow_style=False, 
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                    width=80
                )
            else:
                yaml_content = yaml.dump(data, allow_unicode=True)
            
            # Escribir archivo YAML
            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            result = {
                "status": "success", 
                "message": f"Convertido: {json_file} → {yaml_file}",
                "yaml_file": yaml_file
            }
            
            if "result" in config:
                self.set_variable(config["id"], result)
            
            Output.Console(self.plugin_name, f"{result['message']}")
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Error: JSON inválido en {json_file}: {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise
    
    def _validate_yaml(self, config: Dict[str, Any]) -> Any:
        """Valida que un archivo YAML es válido"""
        yaml_file = config.get("yaml_file")
        
        if not yaml_file:
            raise ValueError("Parámetro 'yaml_file' requerido")
        
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"Archivo YAML no encontrado: {yaml_file}")
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            
            result = {"status": "success", "message": f"YAML válido: {yaml_file}"}
            
            if "result" in config:
                self.set_variable(config["id"], result)
            
            Output.Console(self.plugin_name, f"{result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"YAML inválido: {yaml_file} - {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise ValueError(error_msg)
    
    def _convert_directory(self, config: Dict[str, Any]) -> Any:
        """Convierte todos los archivos JSON en un directorio"""
        input_dir = config.get("input_dir")
        output_dir = config.get("output_dir")
        recursive = config.get("recursive", False)
        
        if not input_dir:
            raise ValueError("Parámetro 'input_dir' requerido")
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Directorio no encontrado: {input_dir}")
        
        if not os.path.isdir(input_dir):
            raise ValueError(f"No es un directorio: {input_dir}")
        
        try:
            # Determinar directorio de salida
            if output_dir is None:
                output_path = Path(input_dir)
            else:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            
            # Buscar archivos JSON
            pattern = "**/*.json" if recursive else "*.json"
            json_files = list(Path(input_dir).glob(pattern))
            
            if not json_files:
                result = {"status": "warning", "message": f"No se encontraron archivos JSON en: {input_dir}"}
                if "result" in config:
                    self.set_variable(config["id"], result)
                return result
            
            Output.Console(self.plugin_name, f"Procesando {len(json_files)} archivos JSON...")
            
            success_count = 0
            for json_file in json_files:
                # Calcular ruta relativa para mantener estructura
                rel_path = json_file.relative_to(Path(input_dir))
                yaml_file = output_path / rel_path.with_suffix('.yaml')
                
                # Crear directorio de salida si es necesario
                yaml_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    self._convert_json_to_yaml({
                        "json_file": str(json_file),
                        "yaml_file": str(yaml_file)
                    })
                    success_count += 1
                except Exception as e:
                    Output.Console(self.plugin_name, f"Error convirtiendo {json_file}: {e}")
            
            result = {
                "status": "success", 
                "message": f"Conversión completada: {success_count}/{len(json_files)} archivos",
                "converted_count": success_count,
                "total_count": len(json_files)
            }
            
            if "result" in config:
                self.set_variable(config["id"], result)
            
            Output.Console(self.plugin_name, f"{result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Error procesando directorio: {e}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise
    
    def _register_cli_parameters(self) -> Dict[str, Any]:
        """Registra parámetros CLI dinámicamente"""
        try:
            # Importar argparse dinámicamente para evitar dependencias circulares
            import argparse
            import sys
            
            # Buscar el parser de argumentos existente
            for arg in sys.argv:
                if arg == '--help' or arg == '-h':
                    # Si se solicita ayuda, mostrar información del plugin
                    print("\nYAML Plugin para Sugar Language")
                    print("=" * 40)
                    print("Comandos disponibles:")
                    print("  -y, --yaml <archivo>     Procesar archivo YAML")
                    print("  --yaml-validate <archivo> Validar archivo YAML")
                    print("  --yaml-convert <json>    Convertir JSON a YAML")
                    print("=" * 40)
            
            # Detectar archivos YAML en argumentos
            for i, arg in enumerate(sys.argv):
                if arg.endswith(('.yml', '.yaml')) and os.path.isfile(arg):
                    # Es un archivo YAML, procesarlo
                    try:
                        result = self._process_file({"file_path": arg})
                        Output.Console(self.plugin_name, f"Archivo YAML procesado: {arg}")
                        return result
                    except Exception as e:
                        Output.Console(self.plugin_name, f"Error procesando YAML: {e}")
                        sys.exit(1)
            
            return {"status": "success", "message": "Parámetros CLI registrados"}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error registrando parámetros CLI: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica las dependencias del plugin"""
        status = {
            'all_satisfied': True,
            'pyyaml': False,
            'details': {}
        }
        
        # Verificar PyYAML
        try:
            import yaml
            status['pyyaml'] = True
            status['details']['pyyaml'] = "PyYAML disponible"
        except ImportError:
            status['pyyaml'] = False
            status['all_satisfied'] = False
            status['details']['pyyaml'] = "PyYAML no disponible"
        
        return status
    
    def _initialize_plugin(self):
        """Inicializar funcionalidades del plugin"""
        try:
            Output.Console(self.plugin_name, "Plugin YAML inicializado correctamente")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error inicializando plugin: {e}")
    
    def _log_dependency_warnings(self):
        """Registra advertencias de dependencias faltantes"""
        Output.Console(self.plugin_name, "Dependencias faltantes detectadas")
        Output.Console(self.plugin_name, "   Instala PyYAML: pip install pyyaml")
        
        if not self.dependency_status.get('pyyaml', False):
            Output.Console(self.plugin_name, "   PyYAML no está disponible")