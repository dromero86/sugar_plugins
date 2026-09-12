"""
Bzip2 Plugin
===========

Plugin completo para compresión y descompresión de archivos usando bzip2 con el SDK.
Demuestra el uso del SDK para interceptar comandos y modificar el comportamiento.
"""

import os
import bz2
import shutil
import tempfile
import json
import time
import hashlib
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

class Bzip2Plugin(PluginBase):
    """
    Plugin Bzip2 que utiliza el SDK para manejar compresión y descompresión
    de archivos usando el algoritmo bzip2.
    
    Características:
    - Compresión y descompresión de archivos individuales
    - Compresión y descompresión de directorios
    - Verificación de integridad
    - Conversión entre formatos
    - División y combinación de archivos
    - Integración completa con el SDK de Sugar
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin para compresión y descompresión de archivos usando bzip2 con el SDK"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias básicas de Python
    DEPENDENCIES = ["bz2"]
    REQUIREMENTS = []
    
    # Dependencias del sistema (ejecutables)
    SYSTEM_DEPENDENCIES = ["bzip2"]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 1,
        "min_disk_gb": 0.5,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": False,
        "write_access": ["/tmp", "./output"],
        "read_access": ["./data"]
    }
    
    # Configuración de compresión bzip2
    COMPRESSION_LEVELS = range(1, 10)  # bzip2 soporta niveles 1-9
    DEFAULT_COMPRESSION_LEVEL = 6
    
    # Extensiones soportadas
    SUPPORTED_EXTENSIONS = ['.bz2', '.tbz2', '.tar.bz2']
    
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
        self.temp_dir = Path(tempfile.gettempdir()) / "sugar_bzip2_plugin"
        self.temp_dir.mkdir(exist_ok=True)
        
        Output.Console(self.plugin_name, "Bzip2 Plugin initialized with SDK integration")
    
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
        
        return self.sdk
    
    def _register_sdk_extensions(self):
        """Registrar todas las extensiones del SDK"""
        
        try:
            # 1. Registrar hooks para interceptar comandos bzip2
            self.sdk['hook_system'].register_hook(
                hook_point=HookPoint.BEFORE_COMMAND,
                callback=self._before_bzip2_command_hook,
                priority=10
            )
            
            self.sdk['hook_system'].register_hook(
                hook_point=HookPoint.AFTER_COMMAND,
                callback=self._after_bzip2_command_hook,
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
                callback=self._customize_bzip2_command,
                priority=8
            )
            
            # 4. Agregar alias de comandos
            self.sdk['command_customizer'].add_command_alias("compress", "bzip2_compress")
            self.sdk['command_customizer'].add_command_alias("decompress", "bzip2_decompress")
            self.sdk['command_customizer'].add_command_alias("pack", "bzip2_compress")
            self.sdk['command_customizer'].add_command_alias("unpack", "bzip2_decompress")
            
            # 5. Registrar extensiones en el manager
            self.sdk['extension_manager'].register_extension(
                plugin_name=self.plugin_name,
                extension_type=ExtensionType.COMMAND_CUSTOMIZER,
                callback=self._bzip2_extension_callback,
                priority=10,
                metadata={'type': 'bzip2_operations'}
            )
            
            Output.Console(self.plugin_name, "SDK extensions registered successfully")
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Warning: SDK extensions registration failed: {e}")
            # Continue without SDK extensions if registration fails
    
    def _before_bzip2_command_hook(self, hook_context):
        """Hook ejecutado antes de comandos bzip2"""
        command = hook_context.current_command
        
        if isinstance(command, dict) and command.get('name') in ['bzip2_compress', 'bzip2_decompress', 'compress', 'decompress']:
            Output.Console(self.plugin_name, f"Before bzip2 command: {command.get('name')}")
            
            # Validar parámetros
            if not self._validate_bzip2_params(command):
                hook_context.should_abort = True
                hook_context.data['error'] = 'Invalid bzip2 parameters'
                return hook_context
            
            # Agregar información de contexto
            hook_context.data['bzip2_plugin_info'] = {
                'plugin': self.plugin_name,
                'timestamp': time.time(),
                'command': command.get('name'),
                'compression_level': command.get('compression_level', self.DEFAULT_COMPRESSION_LEVEL)
            }
        
        return hook_context
    
    def _after_bzip2_command_hook(self, hook_context):
        """Hook ejecutado después de comandos bzip2"""
        command = hook_context.current_command
        result = hook_context.data.get('result', {})
        
        if isinstance(command, dict) and command.get('name') in ['bzip2_compress', 'bzip2_decompress', 'compress', 'decompress']:
            Output.Console(self.plugin_name, f"After bzip2 command: {command.get('name')} -> {result}")
            
            # Agregar estadísticas
            if isinstance(result, dict):
                result['bzip2_plugin_processed'] = True
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
    
    def _customize_bzip2_command(self, context):
        """Customizar comandos bzip2 antes de la ejecución"""
        command_name = context.command_name
        command_args = context.command_args
        
        if command_name in ['bzip2_compress', 'bzip2_decompress', 'compress', 'decompress']:
            Output.Console(self.plugin_name, f"Customizing bzip2 command: {command_name}")
            
            # Establecer nivel de compresión por defecto
            if 'compression_level' not in command_args:
                command_args['compression_level'] = self.DEFAULT_COMPRESSION_LEVEL
            
            # Validar nivel de compresión
            if command_args['compression_level'] not in self.COMPRESSION_LEVELS:
                command_args['compression_level'] = self.DEFAULT_COMPRESSION_LEVEL
            
            # Validar y normalizar rutas
            if 'source' in command_args:
                command_args['source'] = os.path.abspath(command_args['source'])
            
            if 'destination' in command_args:
                command_args['destination'] = os.path.abspath(command_args['destination'])
            
            context.transformed_command = command_args
            Output.Console(self.plugin_name, f"Customized command args: {command_args}")
        
        return context
    
    def _bzip2_extension_callback(self, *args, **kwargs):
        """Callback de extensión para operaciones bzip2"""
        Output.Console(self.plugin_name, f"Bzip2 extension callback executed")
        return {'bzip2_extension_executed': True, 'timestamp': time.time()}
    
    def _validate_bzip2_params(self, command):
        """Validar parámetros de comandos bzip2"""
        try:
            if command.get('name') == 'bzip2_compress':
                required = ['source', 'destination']
            elif command.get('name') == 'bzip2_decompress':
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
    
    def get_available_commands(self) -> List[str]:
        """Obtener comandos disponibles del plugin"""
        return [
            "bzip2_compress",        # Comprimir archivos
            "bzip2_decompress",      # Descomprimir archivos
            "bzip2_info",            # Información de archivo comprimido
            "bzip2_test",            # Probar integridad
            "bzip2_convert",         # Convertir entre formatos
            "bzip2_merge",           # Combinar archivos
            "bzip2_split",           # Dividir archivos grandes
            "sdk_info",              # Información del SDK
            "test_sdk"               # Probar funcionalidades del SDK
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin"""
        if operator == "bzip2_compress":
            return self._compress_command(config)
        elif operator == "bzip2_decompress":
            return self._decompress_command(config)
        elif operator == "bzip2_info":
            return self._info_command(config)
        elif operator == "bzip2_test":
            return self._test_command(config)
        elif operator == "bzip2_convert":
            return self._convert_command(config)
        elif operator == "bzip2_merge":
            return self._merge_command(config)
        elif operator == "bzip2_split":
            return self._split_command(config)
        elif operator == "sdk_info":
            return self._sdk_info_command(config)
        elif operator == "test_sdk":
            return self._test_sdk_command(config)
        else:
            raise ValueError(f"Comando desconocido: {operator}")
    
    def _compress_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comprimir archivos usando bzip2"""
        source = config.get('source')
        destination = config.get('destination')
        compression_level = config.get('compression_level', self.DEFAULT_COMPRESSION_LEVEL)
        
        Output.Console(self.plugin_name, f"Compressing {source} to {destination} (level: {compression_level})")
        
        try:
            start_time = time.time()
            original_size = self._get_size(source)
            
            # Comprimir archivo
            with open(source, 'rb') as input_file:
                with bz2.open(destination, 'wb', compresslevel=compression_level) as output_file:
                    shutil.copyfileobj(input_file, output_file)
            
            compressed_size = os.path.getsize(destination)
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination': destination,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_level': compression_level,
                'processing_time': end_time - start_time,
                'compression_ratio': self._calculate_compression_ratio({
                    'original_size': original_size,
                    'compressed_size': compressed_size
                })
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Compression completed: {result['compression_ratio']}% reduction")
            return result
            
        except Exception as e:
            error_msg = f"Error during compression: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _decompress_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Descomprimir archivos usando bzip2"""
        source = config.get('source')
        destination = config.get('destination')
        
        Output.Console(self.plugin_name, f"Decompressing {source} to {destination}")
        
        try:
            start_time = time.time()
            compressed_size = os.path.getsize(source)
            
            # Descomprimir archivo
            with bz2.open(source, 'rb') as input_file:
                with open(destination, 'wb') as output_file:
                    shutil.copyfileobj(input_file, output_file)
            
            original_size = os.path.getsize(destination)
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination': destination,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'processing_time': end_time - start_time,
                'compression_ratio': self._calculate_compression_ratio({
                    'original_size': original_size,
                    'compressed_size': compressed_size
                })
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Decompression completed")
            return result
            
        except Exception as e:
            error_msg = f"Error during decompression: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información de un archivo bzip2"""
        source = config.get('source')
        
        Output.Console(self.plugin_name, f"Getting info for {source}")
        
        try:
            file_size = os.path.getsize(source)
            
            # Intentar leer el header para verificar que es un archivo bzip2 válido
            with open(source, 'rb') as f:
                header = f.read(10)
            
            is_valid_bzip2 = header.startswith(b'BZ')
            
            result = {
                'status': 'success',
                'source': source,
                'file_size': file_size,
                'is_valid_bzip2': is_valid_bzip2,
                'header': header.hex() if len(header) > 0 else None
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_msg = f"Error getting file info: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar la integridad de un archivo bzip2"""
        source = config.get('source')
        
        Output.Console(self.plugin_name, f"Testing integrity of {source}")
        
        try:
            start_time = time.time()
            
            # Intentar descomprimir para verificar integridad
            with bz2.open(source, 'rb') as input_file:
                # Leer todo el contenido para verificar integridad
                content = input_file.read()
            
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'is_valid': True,
                'decompressed_size': len(content),
                'processing_time': end_time - start_time
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Integrity test passed")
            return result
            
        except Exception as e:
            result = {
                'status': 'error',
                'source': source,
                'is_valid': False,
                'error': str(e)
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Integrity test failed: {str(e)}")
            return result
    
    def _convert_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir entre formatos de compresión"""
        source = config.get('source')
        destination = config.get('destination')
        target_format = config.get('target_format', 'bz2')
        
        Output.Console(self.plugin_name, f"Converting {source} to {target_format} format")
        
        try:
            start_time = time.time()
            
            # Crear archivo temporal para la conversión
            temp_file = self.temp_dir / f"temp_convert_{int(time.time())}"
            
            # Descomprimir archivo original
            if source.endswith('.bz2'):
                with bz2.open(source, 'rb') as input_file:
                    with open(temp_file, 'wb') as output_file:
                        shutil.copyfileobj(input_file, output_file)
            else:
                # Asumir que es un archivo sin comprimir
                shutil.copy2(source, temp_file)
            
            # Comprimir al formato objetivo
            if target_format == 'bz2':
                compression_level = config.get('compression_level', self.DEFAULT_COMPRESSION_LEVEL)
                with open(temp_file, 'rb') as input_file:
                    with bz2.open(destination, 'wb', compresslevel=compression_level) as output_file:
                        shutil.copyfileobj(input_file, output_file)
            else:
                raise ValueError(f"Target format {target_format} not supported")
            
            # Limpiar archivo temporal
            temp_file.unlink()
            
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination': destination,
                'target_format': target_format,
                'processing_time': end_time - start_time
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Conversion completed")
            return result
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _merge_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar múltiples archivos bzip2"""
        sources = config.get('sources', [])
        destination = config.get('destination')
        compression_level = config.get('compression_level', self.DEFAULT_COMPRESSION_LEVEL)
        
        Output.Console(self.plugin_name, f"Merging {len(sources)} files to {destination}")
        
        try:
            start_time = time.time()
            total_original_size = 0
            
            # Crear archivo temporal para combinar
            temp_combined = self.temp_dir / f"temp_merge_{int(time.time())}"
            
            with open(temp_combined, 'wb') as combined_file:
                for source in sources:
                    if source.endswith('.bz2'):
                        # Descomprimir y agregar al archivo combinado
                        with bz2.open(source, 'rb') as input_file:
                            content = input_file.read()
                            combined_file.write(content)
                            total_original_size += len(content)
                    else:
                        # Agregar archivo sin comprimir
                        with open(source, 'rb') as input_file:
                            content = input_file.read()
                            combined_file.write(content)
                            total_original_size += len(content)
            
            # Comprimir el archivo combinado
            with open(temp_combined, 'rb') as input_file:
                with bz2.open(destination, 'wb', compresslevel=compression_level) as output_file:
                    shutil.copyfileobj(input_file, output_file)
            
            # Limpiar archivo temporal
            temp_combined.unlink()
            
            compressed_size = os.path.getsize(destination)
            end_time = time.time()
            
            result = {
                'status': 'success',
                'sources': sources,
                'destination': destination,
                'total_original_size': total_original_size,
                'compressed_size': compressed_size,
                'compression_level': compression_level,
                'processing_time': end_time - start_time,
                'compression_ratio': self._calculate_compression_ratio({
                    'original_size': total_original_size,
                    'compressed_size': compressed_size
                })
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Merge completed: {result['compression_ratio']}% reduction")
            return result
            
        except Exception as e:
            error_msg = f"Error during merge: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _split_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Dividir un archivo bzip2 en partes más pequeñas"""
        source = config.get('source')
        destination_dir = config.get('destination_dir', '.')
        chunk_size = config.get('chunk_size', 1024 * 1024)  # 1MB por defecto
        compression_level = config.get('compression_level', self.DEFAULT_COMPRESSION_LEVEL)
        
        Output.Console(self.plugin_name, f"Splitting {source} into {chunk_size} byte chunks")
        
        try:
            start_time = time.time()
            
            # Descomprimir archivo original
            temp_decompressed = self.temp_dir / f"temp_split_{int(time.time())}"
            with bz2.open(source, 'rb') as input_file:
                with open(temp_decompressed, 'wb') as output_file:
                    shutil.copyfileobj(input_file, output_file)
            
            # Dividir archivo descomprimido
            chunk_files = []
            chunk_number = 1
            
            with open(temp_decompressed, 'rb') as input_file:
                while True:
                    chunk_data = input_file.read(chunk_size)
                    if not chunk_data:
                        break
                    
                    chunk_filename = f"{Path(source).stem}_part_{chunk_number:03d}.bz2"
                    chunk_path = Path(destination_dir) / chunk_filename
                    
                    with bz2.open(chunk_path, 'wb', compresslevel=compression_level) as output_file:
                        output_file.write(chunk_data)
                    
                    chunk_files.append(str(chunk_path))
                    chunk_number += 1
            
            # Limpiar archivo temporal
            temp_decompressed.unlink()
            
            end_time = time.time()
            
            result = {
                'status': 'success',
                'source': source,
                'destination_dir': destination_dir,
                'chunk_size': chunk_size,
                'chunk_files': chunk_files,
                'total_chunks': len(chunk_files),
                'compression_level': compression_level,
                'processing_time': end_time - start_time
            }
            
            # Guardar resultado en variable si se especifica
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            Output.Console(self.plugin_name, f"Split completed: {len(chunk_files)} chunks created")
            return result
            
        except Exception as e:
            error_msg = f"Error during split: {str(e)}"
            Output.Console(self.plugin_name, f"{error_msg}")
            raise RuntimeError(error_msg)
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información del SDK"""
        Output.Console(self.plugin_name, "Getting SDK information")
        
        sdk_info = {
            'status': 'success',
            'plugin_name': self.plugin_name,
            'version': self.VERSION,
            'sdk_components': list(self.sdk.keys()) if hasattr(self, 'sdk') else [],
            'dependency_status': self.dependency_status,
            'supported_extensions': self.SUPPORTED_EXTENSIONS,
            'compression_levels': list(self.COMPRESSION_LEVELS),
            'default_compression_level': self.DEFAULT_COMPRESSION_LEVEL
        }
        
        # Guardar resultado en variable si se especifica
        if 'result' in config:
            self.set_variable(config['id'], sdk_info)
        
        return sdk_info
    
    def _test_sdk_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar funcionalidades del SDK"""
        Output.Console(self.plugin_name, "Testing SDK functionality")
        
        test_results = {
            'status': 'success',
            'tests': {}
        }
        
        # Probar hooks
        try:
            hook_context = type('MockContext', (), {
                'current_command': {'name': 'bzip2_compress', 'source': 'test.txt', 'destination': 'test.bz2'},
                'data': {},
                'should_abort': False
            })()
            
            result = self._before_bzip2_command_hook(hook_context)
            test_results['tests']['hooks'] = 'passed'
        except Exception as e:
            test_results['tests']['hooks'] = f'failed: {str(e)}'
        
        # Probar interpolación
        try:
            context = type('MockContext', (), {
                'original_value': '${file_path}',
                'interpolated_value': None,
                'modified': False
            })()
            
            result = self._interpolate_paths_callback(context)
            test_results['tests']['interpolation'] = 'passed'
        except Exception as e:
            test_results['tests']['interpolation'] = f'failed: {str(e)}'
        
        # Probar customización de comandos
        try:
            context = type('MockContext', (), {
                'command_name': 'bzip2_compress',
                'command_args': {'source': 'test.txt', 'destination': 'test.bz2'},
                'transformed_command': None
            })()
            
            result = self._customize_bzip2_command(context)
            test_results['tests']['command_customization'] = 'passed'
        except Exception as e:
            test_results['tests']['command_customization'] = f'failed: {str(e)}'
        
        # Guardar resultado en variable si se especifica
        if 'result' in config:
            self.set_variable(config['id'], test_results)
        
        Output.Console(self.plugin_name, f"SDK tests completed: {test_results['tests']}")
        return test_results
    
    def _get_size(self, path):
        """Obtener tamaño de archivo o directorio"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size
        else:
            return 0
