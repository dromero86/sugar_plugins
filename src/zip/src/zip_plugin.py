"""
Zip Plugin
==========

Plugin completo para compresión y descompresión de archivos usando el SDK.
Demuestra el uso del SDK para interceptar comandos y modificar el comportamiento.
"""

import os
import zipfile
import tarfile
import gzip
import bz2
import lzma
import shutil
import tempfile
import json
import time
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

class ZipPlugin(PluginBase):
    """
    Plugin Zip que utiliza el SDK para manejar compresión y descompresión
    de archivos con múltiples formatos y opciones.
    
    Formatos soportados:
    - ZIP (zipfile)
    - TAR (tarfile)
    - GZIP (gzip)
    - BZIP2 (bz2)
    - LZMA/XZ (lzma)
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin para compresión y descompresión de archivos usando el SDK"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Formatos soportados
    SUPPORTED_FORMATS = {
        'zip': {
            'extensions': ['.zip'],
            'description': 'ZIP archive format',
            'compression_levels': range(0, 10),
            'default_compression': 6
        },
        'tar': {
            'extensions': ['.tar'],
            'description': 'TAR archive format',
            'compression_levels': [None],
            'default_compression': None
        },
        'tar.gz': {
            'extensions': ['.tar.gz', '.tgz'],
            'description': 'Gzipped TAR archive',
            'compression_levels': range(1, 10),
            'default_compression': 6
        },
        'tar.bz2': {
            'extensions': ['.tar.bz2', '.tbz2'],
            'description': 'Bzip2 compressed TAR archive',
            'compression_levels': range(1, 10),
            'default_compression': 6
        },
        'tar.xz': {
            'extensions': ['.tar.xz', '.txz'],
            'description': 'XZ compressed TAR archive',
            'compression_levels': range(0, 10),
            'default_compression': 6
        },
        'gz': {
            'extensions': ['.gz'],
            'description': 'Gzip compressed file',
            'compression_levels': range(1, 10),
            'default_compression': 6
        },
        'bz2': {
            'extensions': ['.bz2'],
            'description': 'Bzip2 compressed file',
            'compression_levels': range(1, 10),
            'default_compression': 6
        },
        'xz': {
            'extensions': ['.xz'],
            'description': 'XZ compressed file',
            'compression_levels': range(0, 10),
            'default_compression': 6
        }
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Inicializar SDK
        self.sdk = self._initialize_sdk()
        
        # Configuración del plugin
        self.config = plugin_config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "sugar_zip_plugin"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Registrar extensiones del SDK
        self._register_sdk_extensions()
        
        Output.Console(self.plugin_name, "Zip Plugin initialized with SDK integration")
    
    def _initialize_sdk(self):
        """Inicializar todos los componentes del SDK"""
        return {
            'extension_manager': ExtensionManager(),
            'hook_system': HookSystem(),
            'interpolation_interceptor': InterpolationInterceptor(),
            'ast_modifier': ASTModifier(),
            'flow_controller': FlowController(),
            'command_customizer': CommandCustomizer()
        }
    
    def _register_sdk_extensions(self):
        """Registrar todas las extensiones del SDK"""
        
        try:
            # 1. Registrar hooks para interceptar comandos zip
            self.sdk['hook_system'].register_hook(
                hook_point=HookPoint.BEFORE_COMMAND,
                callback=self._before_zip_command_hook,
                priority=10
            )
            
            self.sdk['hook_system'].register_hook(
                hook_point=HookPoint.AFTER_COMMAND,
                callback=self._after_zip_command_hook,
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
                callback=self._customize_zip_command,
                priority=8
            )
            
            # 4. Agregar alias de comandos
            self.sdk['command_customizer'].add_command_alias("compress", "zip_compress")
            self.sdk['command_customizer'].add_command_alias("extract", "zip_extract")
            self.sdk['command_customizer'].add_command_alias("pack", "zip_compress")
            self.sdk['command_customizer'].add_command_alias("unpack", "zip_extract")
            
            # 5. Registrar extensiones en el manager
            self.sdk['extension_manager'].register_extension(
                plugin_name=self.plugin_name,
                extension_type=ExtensionType.COMMAND_CUSTOMIZER,
                callback=self._zip_extension_callback,
                priority=10,
                metadata={'type': 'zip_operations'}
            )
            
            Output.Console(self.plugin_name, "SDK extensions registered successfully")
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Warning: SDK extensions registration failed: {e}")
            # Continue without SDK extensions if registration fails
    
    def _before_zip_command_hook(self, hook_context):
        """Hook ejecutado antes de comandos zip"""
        command = hook_context.current_command
        
        if isinstance(command, dict) and command.get('name') in ['zip_compress', 'zip_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"Before zip command: {command.get('name')}")
            
            # Validar parámetros
            if not self._validate_zip_params(command):
                hook_context.should_abort = True
                hook_context.data['error'] = 'Invalid zip parameters'
                return hook_context
            
            # Agregar información de contexto
            hook_context.data['zip_plugin_info'] = {
                'plugin': self.plugin_name,
                'timestamp': time.time(),
                'command': command.get('name'),
                'format': command.get('format', 'auto')
            }
        
        return hook_context
    
    def _after_zip_command_hook(self, hook_context):
        """Hook ejecutado después de comandos zip"""
        command = hook_context.current_command
        result = hook_context.data.get('result', {})
        
        if isinstance(command, dict) and command.get('name') in ['zip_compress', 'zip_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"After zip command: {command.get('name')} -> {result}")
            
            # Agregar estadísticas
            if isinstance(result, dict):
                result['zip_plugin_processed'] = True
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
    
    def _customize_zip_command(self, context):
        """Customizar comandos zip antes de la ejecución"""
        command_name = context.command_name
        command_args = context.command_args
        
        if command_name in ['zip_compress', 'zip_extract', 'compress', 'extract']:
            Output.Console(self.plugin_name, f"Customizing zip command: {command_name}")
            
            # Auto-detectar formato si no se especifica
            if 'format' not in command_args or command_args['format'] == 'auto':
                command_args['format'] = self._detect_format(command_args.get('source', ''))
            
            # Establecer compresión por defecto
            if 'compression_level' not in command_args:
                format_info = self.SUPPORTED_FORMATS.get(command_args['format'], {})
                command_args['compression_level'] = format_info.get('default_compression', 6)
            
            # Validar y normalizar rutas
            if 'source' in command_args:
                command_args['source'] = os.path.abspath(command_args['source'])
            
            if 'destination' in command_args:
                command_args['destination'] = os.path.abspath(command_args['destination'])
            
            context.transformed_command = command_args
            Output.Console(self.plugin_name, f"Customized command args: {command_args}")
        
        return context
    
    def _zip_extension_callback(self, *args, **kwargs):
        """Callback de extensión para operaciones zip"""
        Output.Console(self.plugin_name, f"Zip extension callback executed")
        return {'zip_extension_executed': True, 'timestamp': time.time()}
    
    def _validate_zip_params(self, command):
        """Validar parámetros de comandos zip"""
        try:
            if command.get('name') == 'zip_compress':
                required = ['source', 'destination']
            elif command.get('name') == 'zip_extract':
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
            return 'zip'
        
        file_path = str(file_path).lower()
        
        for format_name, format_info in self.SUPPORTED_FORMATS.items():
            for extension in format_info['extensions']:
                if file_path.endswith(extension):
                    return format_name
        
        return 'zip'  # Por defecto
    
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
            "zip_compress",          # Comprimir archivos
            "zip_extract",           # Extraer archivos
            "zip_info",              # Información de archivo comprimido
            "zip_list",              # Listar contenido
            "zip_test",              # Probar integridad
            "zip_convert",           # Convertir entre formatos
            "zip_merge",             # Combinar archivos
            "zip_split",             # Dividir archivos grandes
            "sdk_info",              # Información del SDK
            "list_formats",          # Listar formatos soportados
            "test_sdk"               # Probar funcionalidades del SDK
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin"""
        if operator == "zip_compress":
            return self._compress_command(config)
        elif operator == "zip_extract":
            return self._extract_command(config)
        elif operator == "zip_info":
            return self._info_command(config)
        elif operator == "zip_list":
            return self._list_command(config)
        elif operator == "zip_test":
            return self._test_command(config)
        elif operator == "zip_convert":
            return self._convert_command(config)
        elif operator == "zip_merge":
            return self._merge_command(config)
        elif operator == "zip_split":
            return self._split_command(config)
        elif operator == "sdk_info":
            return self._sdk_info_command(config)
        elif operator == "list_formats":
            return self._list_formats_command(config)
        elif operator == "test_sdk":
            return self._test_sdk_command(config)
        else:
            raise ValueError(f"Comando desconocido: {operator}")
    
    def _compress_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comprimir archivos o directorios"""
        source = config.get('source')
        destination = config.get('destination')
        format_type = config.get('format', 'auto')
        compression_level = config.get('compression_level', 6)
        password = config.get('password')
        include_hidden = config.get('include_hidden', False)
        
        if format_type == 'auto':
            format_type = self._detect_format(destination)
        
        Output.Console(self.plugin_name, f"Compressing {source} to {destination} (format: {format_type})")
        
        try:
            start_time = time.time()
            original_size = self._get_size(source)
            
            if format_type == 'zip':
                result = self._compress_zip(source, destination, compression_level, password, include_hidden)
            elif format_type == 'tar':
                result = self._compress_tar(source, destination, None, include_hidden)
            elif format_type == 'tar.gz':
                result = self._compress_tar(source, destination, 'gz', include_hidden, compression_level)
            elif format_type == 'tar.bz2':
                result = self._compress_tar(source, destination, 'bz2', include_hidden, compression_level)
            elif format_type == 'tar.xz':
                result = self._compress_tar(source, destination, 'xz', include_hidden, compression_level)
            elif format_type == 'gz':
                result = self._compress_single_file(source, destination, 'gz', compression_level)
            elif format_type == 'bz2':
                result = self._compress_single_file(source, destination, 'bz2', compression_level)
            elif format_type == 'xz':
                result = self._compress_single_file(source, destination, 'xz', compression_level)
            else:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            compressed_size = os.path.getsize(destination)
            end_time = time.time()
            
            result.update({
                'status': 'success',
                'source': source,
                'destination': destination,
                'format': format_type,
                'compression_level': compression_level,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': self._calculate_compression_ratio({
                    'original_size': original_size,
                    'compressed_size': compressed_size
                }),
                'processing_time': round(end_time - start_time, 2)
            })
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination,
                'format': format_type
            }
    
    def _extract_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extraer archivos comprimidos"""
        source = config.get('source')
        destination = config.get('destination')
        password = config.get('password')
        overwrite = config.get('overwrite', False)
        
        format_type = self._detect_format(source)
        
        Output.Console(self.plugin_name, f"Extracting {source} to {destination} (format: {format_type})")
        
        try:
            start_time = time.time()
            compressed_size = os.path.getsize(source)
            
            if format_type == 'zip':
                result = self._extract_zip(source, destination, password, overwrite)
            elif format_type in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
                result = self._extract_tar(source, destination, overwrite)
            elif format_type in ['gz', 'bz2', 'xz']:
                result = self._extract_single_file(source, destination, overwrite)
            else:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            extracted_size = self._get_size(destination)
            end_time = time.time()
            
            result.update({
                'status': 'success',
                'source': source,
                'destination': destination,
                'format': format_type,
                'compressed_size': compressed_size,
                'extracted_size': extracted_size,
                'processing_time': round(end_time - start_time, 2)
            })
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination,
                'format': format_type
            }
    
    def _compress_zip(self, source, destination, compression_level, password, include_hidden):
        """Comprimir en formato ZIP"""
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            if os.path.isfile(source):
                zipf.write(source, os.path.basename(source))
            else:
                for root, dirs, files in os.walk(source):
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        files = [f for f in files if not f.startswith('.')]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source)
                        zipf.write(file_path, arcname)
        
        return {'method': 'zip', 'files_count': self._count_files(source)}
    
    def _compress_tar(self, source, destination, compression, include_hidden, compression_level=6):
        """Comprimir en formato TAR"""
        mode_map = {
            'gz': 'w:gz',
            'bz2': 'w:bz2', 
            'xz': 'w:xz',
            None: 'w'
        }
        
        mode = mode_map.get(compression)
        if compression == 'gz':
            mode = f'w:gz'
        elif compression == 'bz2':
            mode = f'w:bz2'
        elif compression == 'xz':
            mode = f'w:xz'
        
        with tarfile.open(destination, mode, compresslevel=compression_level) as tar:
            if os.path.isfile(source):
                tar.add(source, arcname=os.path.basename(source))
            else:
                tar.add(source, arcname=os.path.basename(source), filter=lambda info: None if not include_hidden and info.name.startswith('.') else info)
        
        return {'method': f'tar_{compression or "none"}', 'files_count': self._count_files(source)}
    
    def _compress_single_file(self, source, destination, format_type, compression_level):
        """Comprimir archivo individual"""
        if not os.path.isfile(source):
            raise ValueError(f"Source must be a file for {format_type} compression")
        
        compressors = {
            'gz': lambda f: gzip.open(f, 'wt', compresslevel=compression_level),
            'bz2': lambda f: bz2.open(f, 'wt', compresslevel=compression_level),
            'xz': lambda f: lzma.open(f, 'wt', preset=compression_level)
        }
        
        with open(source, 'rb') as infile:
            with compressors[format_type](destination) as outfile:
                shutil.copyfileobj(infile, outfile)
        
        return {'method': format_type, 'files_count': 1}
    
    def _extract_zip(self, source, destination, password, overwrite):
        """Extraer archivo ZIP"""
        with zipfile.ZipFile(source, 'r') as zipf:
            if password:
                zipf.setpassword(password.encode())
            
            zipf.extractall(destination)
        
        return {'method': 'zip', 'extracted_files': len(zipf.namelist())}
    
    def _extract_tar(self, source, destination, overwrite):
        """Extraer archivo TAR"""
        with tarfile.open(source, 'r:*') as tar:
            tar.extractall(destination)
        
        return {'method': 'tar', 'extracted_files': len(tar.getmembers())}
    
    def _extract_single_file(self, source, destination, overwrite):
        """Extraer archivo individual comprimido"""
        decompressors = {
            'gz': lambda f: gzip.open(f, 'rb'),
            'bz2': lambda f: bz2.open(f, 'rb'),
            'xz': lambda f: lzma.open(f, 'rb')
        }
        
        format_type = self._detect_format(source)
        if format_type in decompressors:
            with decompressors[format_type](source) as infile:
                with open(destination, 'wb') as outfile:
                    shutil.copyfileobj(infile, outfile)
        
        return {'method': format_type, 'extracted_files': 1}
    
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
    
    def _info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información de archivo comprimido"""
        source = config.get('source')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        format_type = self._detect_format(source)
        file_size = os.path.getsize(source)
        
        info = {
            'status': 'success',
            'file': source,
            'format': format_type,
            'size': file_size,
            'size_human': self._format_size(file_size)
        }
        
        try:
            if format_type == 'zip':
                with zipfile.ZipFile(source, 'r') as zipf:
                    info.update({
                        'files_count': len(zipf.namelist()),
                        'files': zipf.namelist()[:10],  # Primeros 10 archivos
                        'is_encrypted': any(zipf.getinfo(f).flag_bits & 0x1 for f in zipf.namelist())
                    })
            elif format_type in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
                with tarfile.open(source, 'r:*') as tar:
                    info.update({
                        'files_count': len(tar.getmembers()),
                        'files': [m.name for m in tar.getmembers()[:10]]
                    })
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _list_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Listar contenido de archivo comprimido"""
        source = config.get('source')
        password = config.get('password')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        format_type = self._detect_format(source)
        
        try:
            if format_type == 'zip':
                with zipfile.ZipFile(source, 'r') as zipf:
                    if password:
                        zipf.setpassword(password.encode())
                    files = zipf.namelist()
            elif format_type in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
                with tarfile.open(source, 'r:*') as tar:
                    files = [m.name for m in tar.getmembers()]
            else:
                return {'status': 'error', 'error': 'Format not supported for listing'}
            
            return {
                'status': 'success',
                'file': source,
                'format': format_type,
                'files_count': len(files),
                'files': files
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Probar integridad de archivo comprimido"""
        source = config.get('source')
        password = config.get('password')
        
        if not os.path.exists(source):
            return {'status': 'error', 'error': 'File not found'}
        
        format_type = self._detect_format(source)
        
        try:
            if format_type == 'zip':
                with zipfile.ZipFile(source, 'r') as zipf:
                    if password:
                        zipf.setpassword(password.encode())
                    bad_file = zipf.testzip()
                    is_valid = bad_file is None
            elif format_type in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
                with tarfile.open(source, 'r:*') as tar:
                    tar.getmembers()  # Esto fallará si el archivo está corrupto
                    is_valid = True
            else:
                return {'status': 'error', 'error': 'Format not supported for testing'}
            
            return {
                'status': 'success',
                'file': source,
                'format': format_type,
                'is_valid': is_valid,
                'bad_file': bad_file if format_type == 'zip' else None
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'is_valid': False}
    
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
        """Combinar múltiples archivos comprimidos"""
        sources = config.get('sources', [])
        destination = config.get('destination')
        format_type = config.get('format', 'zip')
        
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
                'format': format_type
            })
            
            # Limpiar
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return compress_result
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'status': 'error', 'error': str(e)}
    
    def _split_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Dividir archivo comprimido grande"""
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
            
            return {
                'status': 'success',
                'source': source,
                'parts': parts,
                'total_parts': len(parts),
                'max_size': max_size
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Información del SDK"""
        return {
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
            'message': 'Zip Plugin SDK information retrieved'
        }
    
    def _list_formats_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Listar formatos soportados"""
        return {
            'status': 'success',
            'supported_formats': self.SUPPORTED_FORMATS,
            'total_formats': len(self.SUPPORTED_FORMATS)
        }
    
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
        
        return {
            'status': 'success',
            'sdk_tests': results,
            'message': 'SDK functionality tested successfully'
        }
    
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
        Output.Console(self.plugin_name, "Cleaning up Zip Plugin...")
        
        # Limpiar extensiones del SDK
        self.sdk['extension_manager'].unregister_all_plugin_extensions(self.plugin_name)
        
        # Limpiar directorio temporal
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        Output.Console(self.plugin_name, "Zip Plugin cleanup completed")