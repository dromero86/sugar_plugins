"""
RAR Plugin
==========

Plugin completo para compresión y descompresión de archivos RAR usando el SDK.
Demuestra el uso del SDK para interceptar comandos y modificar el comportamiento.
"""

import os
import rarfile
import tempfile
import json
import time
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    InterpolationInterceptor, InterpolationEvent,
    ASTModifier, ASTModificationEvent,
    FlowController, FlowEvent,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

class RarPlugin(PluginBase):
    """
    Plugin RAR que utiliza el SDK para manejar compresión y descompresión
    de archivos RAR con múltiples opciones y funcionalidades avanzadas.
    
    Formatos soportados:
    - RAR (rarfile)
    - RAR5 (rarfile con soporte RAR5)
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin para compresión y descompresión de archivos RAR usando el SDK"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias de Python
    DEPENDENCIES = ["rarfile"]
    REQUIREMENTS = ["rarfile>=4.0"]
    
    # Dependencias del sistema (ejecutables)
    SYSTEM_DEPENDENCIES = ["unrar", "rar"]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 2,
        "min_disk_gb": 1,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": False,
        "write_access": ["/tmp", "./output"],
        "read_access": ["./data"]
    }
    
    # Formatos soportados
    SUPPORTED_FORMATS = {
        'rar': {
            'extensions': ['.rar'],
            'description': 'RAR archive format',
            'compression_levels': range(0, 6),
            'default_compression': 3
        },
        'rar5': {
            'extensions': ['.rar'],
            'description': 'RAR5 archive format',
            'compression_levels': range(0, 6),
            'default_compression': 3
        }
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
        
        # Configuración del plugin
        self.config = plugin_config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "sugar_rar_plugin"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configurar rarfile
        self._configure_rarfile()
        
        Output.Console(self.plugin_name, "RAR Plugin initialized with SDK integration")
    
    def _configure_rarfile(self):
        """Configurar rarfile para el sistema"""
        try:
            # Configurar rutas de unrar/rar
            if os.name == 'nt':  # Windows
                rarfile.UNRAR_TOOL = "C:\\Program Files\\WinRAR\\UnRAR.exe"
            else:  # Linux/Unix
                # Buscar unrar en PATH
                import shutil
                unrar_path = shutil.which("unrar")
                if unrar_path:
                    rarfile.UNRAR_TOOL = unrar_path
                else:
                    # Intentar con rar
                    rar_path = shutil.which("rar")
                    if rar_path:
                        rarfile.UNRAR_TOOL = rar_path
            
            Output.Console(self.plugin_name, f"RAR tool configured: {rarfile.UNRAR_TOOL}")
        except Exception as e:
            Output.Console(self.plugin_name, f"Warning: Could not configure RAR tool: {e}")
    
    def _initialize_sdk(self):
        """Inicializar todos los componentes del SDK"""
        self.sdk = {
            'extension_manager': ExtensionManager(),
            'hook_system': HookSystem(),
            'interpolation_interceptor': InterpolationInterceptor(),
            'ast_modifier': ASTModifier(),
            'flow_controller': FlowController(),
            'command_customizer': CommandCustomizer()
        }
        
        # Registrar extensiones del SDK
        self._register_sdk_extensions()
    
    def _register_sdk_extensions(self):
        """Registrar todas las extensiones del SDK"""
        
        # 1. Registrar hooks para interceptar comandos rar
        self.sdk['hook_system'].register_hook(
            hook_point=HookPoint.BEFORE_COMMAND,
            callback=self._before_rar_command_hook,
            priority=10
        )
        
        self.sdk['hook_system'].register_hook(
            hook_point=HookPoint.AFTER_COMMAND,
            callback=self._after_rar_command_hook,
            priority=10
        )
        
        # 2. Registrar interceptores de interpolación para rutas
        self.sdk['interpolation_interceptor'].register_interceptor(
            event=InterpolationEvent.BEFORE_INTERPOLATION,
            callback=self._interpolate_paths_callback,
            priority=5
        )
        
        # 3. Registrar customizadores de comandos
        self.sdk['command_customizer'].register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._customize_rar_command,
            priority=8
        )
        
        # 4. Agregar alias de comandos
        self.sdk['command_customizer'].add_command_alias("compress", "rar_compress")
        self.sdk['command_customizer'].add_command_alias("extract", "rar_extract")
        self.sdk['command_customizer'].add_command_alias("pack", "rar_compress")
        self.sdk['command_customizer'].add_command_alias("unpack", "rar_extract")
        
        # 5. Registrar extensiones en el manager
        self.sdk['extension_manager'].register_extension(
            plugin_name=self.plugin_name,
            extension_type=ExtensionType.COMMAND_CUSTOMIZER,
            callback=self._rar_extension_callback,
            priority=10,
            metadata={'type': 'rar_operations'}
        )
        
        Output.Console(self.plugin_name, "SDK extensions registered successfully")
    
    def get_available_commands(self) -> List[str]:
        """Obtener comandos disponibles del plugin"""
        return [
            "rar_compress",          # Comprimir archivos
            "rar_extract",           # Extraer archivos
            "rar_info",              # Información de archivo RAR
            "rar_list",              # Listar contenido
            "rar_test",              # Probar integridad
            "rar_convert",           # Convertir entre formatos
            "rar_merge",             # Combinar archivos
            "rar_split",             # Dividir archivos grandes
            "sdk_info",              # Información del SDK
            "list_formats",          # Listar formatos soportados
            "test_sdk",              # Probar funcionalidades del SDK
            "check_dependencies",    # Verificar dependencias
            "system_info",           # Información del sistema
            "test_functionality"     # Probar funcionalidad
        ]
    
    def _before_rar_command_hook(self, hook_context):
        """Hook ejecutado antes de comandos rar"""
        command = hook_context.current_command
        
        if isinstance(command, dict) and command.get('name') in ['rar_compress', 'rar_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"Before RAR command: {command.get('name')}")
            
            # Validar parámetros
            if not self._validate_rar_params(command):
                hook_context.should_abort = True
                hook_context.data['error'] = 'Invalid RAR parameters'
                return hook_context
            
            # Agregar información de contexto
            hook_context.data['rar_plugin_info'] = {
                'plugin': self.plugin_name,
                'timestamp': time.time(),
                'command': command.get('name'),
                'format': command.get('format', 'rar')
            }
        
        return hook_context
    
    def _after_rar_command_hook(self, hook_context):
        """Hook ejecutado después de comandos rar"""
        command = hook_context.current_command
        result = hook_context.data.get('result', {})
        
        if isinstance(command, dict) and command.get('name') in ['rar_compress', 'rar_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"After RAR command: {command.get('name')} -> {result}")
            
            # Agregar estadísticas
            if isinstance(result, dict):
                result['rar_plugin_processed'] = True
                result['processing_time'] = time.time()
                result['compression_ratio'] = self._calculate_compression_ratio(result)
        
        return hook_context
    
    def _interpolate_paths_callback(self, context):
        """Callback para interpolación de rutas"""
        if '${' in context.original_value and any(path_keyword in context.original_value.lower() for path_keyword in ['path', 'file', 'dir', 'folder']):
            Output.Console(self.plugin_name, f"Interpolating path: {context.original_value}")
            
            # Expandir rutas relativas
            if context.original_value.startswith('./') or context.original_value.startswith('../'):
                expanded_path = os.path.abspath(context.original_value)
                context.interpolated_value = expanded_path
                context.modified = True
                Output.Console(self.plugin_name, f"Expanded path: {expanded_path}")
        
        return context
    
    def _customize_rar_command(self, context):
        """Customizar comandos rar antes de la ejecución"""
        command_name = context.command_name
        command_args = context.command_args
        
        if command_name in ['rar_compress', 'rar_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"Customizing RAR command: {command_name}")
            
            # Auto-detectar formato si no se especifica
            if 'format' not in command_args or command_args['format'] == 'auto':
                command_args['format'] = self._detect_format(command_args.get('source', ''))
            
            # Establecer compresión por defecto
            if 'compression_level' not in command_args:
                format_info = self.SUPPORTED_FORMATS.get(command_args['format'], {})
                command_args['compression_level'] = format_info.get('default_compression', 3)
            
            # Validar y normalizar rutas
            if 'source' in command_args:
                command_args['source'] = os.path.abspath(command_args['source'])
            
            if 'destination' in command_args:
                command_args['destination'] = os.path.abspath(command_args['destination'])
            
            context.transformed_command = command_args
            Output.Console(self.plugin_name, f"Customized command args: {command_args}")
        
        return context
    
    def _rar_extension_callback(self, *args, **kwargs):
        """Callback de extensión para operaciones rar"""
        Output.Console(self.plugin_name, f"RAR extension callback executed")
        return {'rar_extension_executed': True, 'timestamp': time.time()}
    
    def _validate_rar_params(self, command):
        """Validar parámetros de comandos rar"""
        try:
            if command.get('name') == 'rar_compress':
                required = ['source', 'destination']
            elif command.get('name') == 'rar_extract':
                required = ['source', 'destination']
            else:
                return True
            
            for param in required:
                if param not in command:
                    Output.Console(self.plugin_name, f"Missing required parameter: {param}")
                    return False
            
            # Validar que el archivo fuente existe
            source = command.get('source')
            if not os.path.exists(source):
                Output.Console(self.plugin_name, f"Source file does not exist: {source}")
                return False
            
            return True
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Validation error: {e}")
            return False
    
    def _detect_format(self, file_path):
        """Detectar formato basado en la extensión del archivo"""
        if not file_path:
            return 'rar'
        
        file_path = str(file_path).lower()
        
        for format_name, format_info in self.SUPPORTED_FORMATS.items():
            for extension in format_info['extensions']:
                if file_path.endswith(extension):
                    return format_name
        
        return 'rar'  # Por defecto
    
    def _calculate_compression_ratio(self, result):
        """Calcular ratio de compresión"""
        try:
            original_size = result.get('original_size', 0)
            compressed_size = result.get('compressed_size', 0)
            
            if original_size > 0 and compressed_size > 0:
                ratio = (1 - (compressed_size / original_size)) * 100
                return round(ratio, 2)
            
            return 0
        except:
            return 0
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin"""
        if command == "rar_compress":
            return self._compress_command(config)
        elif command == "rar_extract":
            return self._extract_command(config)
        elif command == "rar_info":
            return self._info_command(config)
        elif command == "rar_list":
            return self._list_command(config)
        elif command == "rar_test":
            return self._test_command(config)
        elif command == "rar_convert":
            return self._convert_command(config)
        elif command == "rar_merge":
            return self._merge_command(config)
        elif command == "rar_split":
            return self._split_command(config)
        elif command == "sdk_info":
            return self._sdk_info_command(config)
        elif command == "list_formats":
            return self._list_formats_command(config)
        elif command == "test_sdk":
            return self._test_sdk_command(config)
        elif command == "check_dependencies":
            return self._check_dependencies_command(config)
        elif command == "system_info":
            return self._system_info_command(config)
        elif command == "test_functionality":
            return self._test_functionality_command(config)
        else:
            raise ValueError(f"Comando desconocido: {command}")
    
    def _compress_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comprimir archivos o directorios en formato RAR"""
        source = config.get('source')
        destination = config.get('destination')
        compression_level = config.get('compression_level', 3)
        password = config.get('password')
        include_hidden = config.get('include_hidden', False)
        
        Output.Console(self.plugin_name, f"Compressing {source} to {destination}")
        
        try:
            start_time = time.time()
            original_size = self._get_size(source)
            
            # Usar rarfile para crear archivo RAR
            with rarfile.RarFile(destination, 'w') as rar:
                if os.path.isfile(source):
                    rar.write(source, os.path.basename(source))
                else:
                    for root, dirs, files in os.walk(source):
                        if not include_hidden:
                            dirs[:] = [d for d in dirs if not d.startswith('.')]
                            files = [f for f in files if not f.startswith('.')]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source)
                            rar.write(file_path, arcname)
            
            compressed_size = os.path.getsize(destination)
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination': destination,
                'format': 'rar',
                'compression_level': compression_level,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': self._calculate_compression_ratio({
                    'original_size': original_size,
                    'compressed_size': compressed_size
                }),
                'processing_time': round(end_time - start_time, 2),
                'files_count': self._count_files(source)
            }
            
            if "result" in config:
                self.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination,
                'format': 'rar'
            }
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _extract_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extraer archivos RAR"""
        source = config.get('source')
        destination = config.get('destination')
        password = config.get('password')
        overwrite = config.get('overwrite', False)
        
        Output.Console(self.plugin_name, f"Extracting {source} to {destination}")
        
        try:
            start_time = time.time()
            compressed_size = os.path.getsize(source)
            
            with rarfile.RarFile(source, 'r') as rar:
                if password:
                    rar.setpassword(password)
                
                rar.extractall(destination)
                extracted_files = len(rar.namelist())
            
            extracted_size = self._get_size(destination)
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination': destination,
                'format': 'rar',
                'compressed_size': compressed_size,
                'extracted_size': extracted_size,
                'extracted_files': extracted_files,
                'processing_time': round(end_time - start_time, 2)
            }
            
            if "result" in config:
                self.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination,
                'format': 'rar'
            }
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información de archivo RAR"""
        source = config.get('source')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        file_size = os.path.getsize(source)
        
        try:
            with rarfile.RarFile(source, 'r') as rar:
                info = {
                    'status': 'success',
                    'file': source,
                    'format': 'rar',
                    'size': file_size,
                    'size_human': self._format_size(file_size),
                    'files_count': len(rar.namelist()),
                    'files': rar.namelist()[:10],  # Primeros 10 archivos
                    'is_encrypted': rar.needs_password(),
                    'comment': rar.comment if hasattr(rar, 'comment') else None
                }
                
                # Información detallada de archivos
                file_details = []
                for info in rar.infolist()[:5]:  # Primeros 5 archivos
                    file_details.append({
                        'name': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                        'date_time': info.date_time,
                        'is_encrypted': info.flag_bits & 0x1
                    })
                
                info['file_details'] = file_details
                
                if "result" in config:
                    self.set_variable(config["result"], info)
                
                return info
                
        except Exception as e:
            error_result = {'status': 'error', 'error': str(e)}
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _list_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Listar contenido de archivo RAR"""
        source = config.get('source')
        password = config.get('password')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        try:
            with rarfile.RarFile(source, 'r') as rar:
                if password:
                    rar.setpassword(password)
                
                files = rar.namelist()
                
                result = {
                    'status': 'success',
                    'file': source,
                    'format': 'rar',
                    'files_count': len(files),
                    'files': files
                }
                
                if "result" in config:
                    self.set_variable(config["result"], result)
                
                return result
                
        except Exception as e:
            error_result = {'status': 'error', 'error': str(e)}
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar integridad de archivo RAR"""
        source = config.get('source')
        password = config.get('password')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        try:
            with rarfile.RarFile(source, 'r') as rar:
                if password:
                    rar.setpassword(password)
                
                # Probar lectura de todos los archivos
                for info in rar.infolist():
                    rar.read(info.filename)
                
                result = {
                    'status': 'success',
                    'file': source,
                    'format': 'rar',
                    'is_valid': True,
                    'files_tested': len(rar.infolist())
                }
                
                if "result" in config:
                    self.set_variable(config["result"], result)
                
                return result
                
        except Exception as e:
            error_result = {
                'status': 'error', 
                'error': str(e), 
                'is_valid': False
            }
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _convert_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir entre formatos"""
        source = config.get('source')
        destination = config.get('destination')
        target_format = config.get('target_format')
        
        if not target_format:
            return {'status': 'error', 'error': 'target_format is required'}
        
        # Extraer temporalmente
        temp_dir = self.temp_dir / f"convert_{int(time.time())}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extraer
            extract_result = self._extract_command({
                'source': source,
                'destination': str(temp_dir)
            })
            
            if extract_result.get('status') != 'success':
                return extract_result
            
            # Comprimir en nuevo formato
            compress_result = self._compress_command({
                'source': str(temp_dir),
                'destination': destination,
                'format': target_format
            })
            
            # Limpiar
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return compress_result
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'status': 'error', 'error': str(e)}
    
    def _merge_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar múltiples archivos RAR"""
        sources = config.get('sources', [])
        destination = config.get('destination')
        
        if not sources or len(sources) < 2:
            return {'status': 'error', 'error': 'At least 2 sources required'}
        
        temp_dir = self.temp_dir / f"merge_{int(time.time())}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extraer todos los archivos
            all_files = []
            for source in sources:
                extract_dir = temp_dir / f"extract_{len(all_files)}"
                extract_dir.mkdir()
                
                extract_result = self._extract_command({
                    'source': source,
                    'destination': str(extract_dir)
                })
                
                if extract_result.get('status') != 'success':
                    return extract_result
                
                all_files.extend(list(extract_dir.rglob('*')))
            
            # Comprimir todo junto
            compress_result = self._compress_command({
                'source': str(temp_dir),
                'destination': destination,
                'format': 'rar'
            })
            
            # Limpiar
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return compress_result
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'status': 'error', 'error': str(e)}
    
    def _split_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Dividir archivo RAR grande"""
        source = config.get('source')
        destination_dir = config.get('destination_dir')
        max_size = config.get('max_size', 100 * 1024 * 1024)  # 100MB por defecto
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        file_size = os.path.getsize(source)
        if file_size <= max_size:
            return {'status': 'error', 'error': 'File is already smaller than max_size'}
        
        try:
            parts = []
            part_num = 1
            
            with open(source, 'rb') as infile:
                while True:
                    chunk = infile.read(max_size)
                    if not chunk:
                        break
                    
                    part_file = os.path.join(destination_dir, f"{os.path.basename(source)}.part{part_num:03d}")
                    
                    with open(part_file, 'wb') as outfile:
                        outfile.write(chunk)
                    
                    parts.append(part_file)
                    part_num += 1
            
            result = {
                'status': 'success',
                'source': source,
                'parts': parts,
                'total_parts': len(parts),
                'max_size': max_size
            }
            
            if "result" in config:
                self.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            error_result = {'status': 'error', 'error': str(e)}
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Información del SDK"""
        result = {
            'status': 'success',
            'plugin_name': self.plugin_name,
            'version': self.VERSION,
            'sdk_components': {
                'extension_manager': 'ExtensionManager',
                'hook_system': 'HookSystem',
                'interpolation_interceptor': 'InterpolationInterceptor',
                'ast_modifier': 'ASTModifier',
                'flow_controller': 'FlowController',
                'command_customizer': 'CommandCustomizer'
            },
            'sdk_stats': {
                'hooks_registered': self.sdk['hook_system'].get_total_hooks(),
                'interceptors_registered': self.sdk['interpolation_interceptor'].get_total_interceptors(),
                'customizers_registered': self.sdk['command_customizer'].get_total_customizers(),
                'aliases_registered': self.sdk['command_customizer'].get_alias_count()
            },
            'message': 'RAR Plugin SDK information retrieved'
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _list_formats_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Listar formatos soportados"""
        result = {
            'status': 'success',
            'supported_formats': self.SUPPORTED_FORMATS,
            'total_formats': len(self.SUPPORTED_FORMATS)
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _test_sdk_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar funcionalidades del SDK"""
        results = {}
        
        # Probar hooks
        hook_context = self.sdk['hook_system'].execute_hooks(
            HookPoint.BEFORE_COMMAND,
            command={'name': 'test_command', 'args': {'test': True}},
            execution_stack=['test']
        )
        results['hooks'] = {
            'executed': True,
            'context': {
                'modified': hook_context.modified,
                'should_continue': hook_context.should_continue,
                'data': hook_context.data
            }
        }
        
        # Probar interpolación
        interp_context = self.sdk['interpolation_interceptor'].intercept_before_interpolation(
            "Test path: ${test_path}",
            ["test_path"]
        )
        results['interpolation'] = {
            'executed': True,
            'context': {
                'original': interp_context.original_value,
                'modified': interp_context.modified,
                'result': interp_context.interpolated_value
            }
        }
        
        # Probar customización de comandos
        cmd_context = self.sdk['command_customizer'].customize_before_execution(
            "test_command",
            {"test": True},
            "original_command"
        )
        results['command_customization'] = {
            'executed': True,
            'context': {
                'command_name': cmd_context.command_name,
                'should_continue': cmd_context.should_continue,
                'metadata': cmd_context.metadata
            }
        }
        
        result = {
            'status': 'success',
            'sdk_tests': results,
            'message': 'SDK functionality tested successfully'
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _check_dependencies_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar dependencias del plugin"""
        result = self.dependency_status.copy()
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _system_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Información del sistema"""
        import platform
        import psutil
        
        result = {
            'status': 'success',
            'system': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor()
            },
            'hardware': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/')._asdict()
            },
            'rar_tool': rarfile.UNRAR_TOOL if hasattr(rarfile, 'UNRAR_TOOL') else 'Not configured'
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _test_functionality_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar funcionalidad del plugin"""
        test_results = {}
        
        # Crear archivo de prueba
        test_file = self.temp_dir / "test_file.txt"
        test_file.write_text("This is a test file for RAR plugin functionality testing.")
        
        # Crear archivo RAR de prueba
        test_rar = self.temp_dir / "test.rar"
        
        try:
            # Probar compresión
            compress_result = self._compress_command({
                'source': str(test_file),
                'destination': str(test_rar)
            })
            test_results['compression'] = compress_result.get('status') == 'success'
            
            # Probar extracción
            extract_dir = self.temp_dir / "extract_test"
            extract_dir.mkdir(exist_ok=True)
            
            extract_result = self._extract_command({
                'source': str(test_rar),
                'destination': str(extract_dir)
            })
            test_results['extraction'] = extract_result.get('status') == 'success'
            
            # Probar información
            info_result = self._info_command({
                'source': str(test_rar)
            })
            test_results['info'] = info_result.get('status') == 'success'
            
            # Probar listado
            list_result = self._list_command({
                'source': str(test_rar)
            })
            test_results['listing'] = list_result.get('status') == 'success'
            
            # Limpiar
            test_file.unlink(missing_ok=True)
            test_rar.unlink(missing_ok=True)
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            all_tests_passed = all(test_results.values())
            
            result = {
                'status': 'success' if all_tests_passed else 'partial_success',
                'tests': test_results,
                'all_tests_passed': all_tests_passed,
                'message': 'RAR plugin functionality tested successfully' if all_tests_passed else 'Some tests failed'
            }
            
            if "result" in config:
                self.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            # Limpiar en caso de error
            test_file.unlink(missing_ok=True)
            test_rar.unlink(missing_ok=True)
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'tests': test_results
            }
            
            if "result" in config:
                self.set_variable(config["result"], error_result)
            
            return error_result
    
    def _get_size(self, path):
        """Obtener tamaño total de archivo o directorio"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total += os.path.getsize(filepath)
            return total
        return 0
    
    def _count_files(self, path):
        """Contar archivos en directorio"""
        if os.path.isfile(path):
            return 1
        elif os.path.isdir(path):
            count = 0
            for root, dirs, files in os.walk(path):
                count += len(files)
            return count
        return 0
    
    def _format_size(self, size_bytes):
        """Formatear tamaño en bytes a formato legible"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def cleanup(self):
        """Limpiar recursos del plugin"""
        Output.Console(self.plugin_name, "Cleaning up RAR Plugin...")
        
        # Limpiar extensiones del SDK
        if hasattr(self, 'sdk'):
            self.sdk['extension_manager'].unregister_all_plugin_extensions(self.plugin_name)
        
        # Limpiar directorio temporal
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        Output.Console(self.plugin_name, "RAR Plugin cleanup completed")
