"""
Utilidades para el plugin RAR
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union


class RarUtils:
    """Clase de utilidades para el plugin RAR"""
    
    @staticmethod
    def find_rar_tool() -> Optional[str]:
        """Buscar la herramienta RAR en el sistema"""
        # Buscar unrar primero
        unrar_path = shutil.which("unrar")
        if unrar_path:
            return unrar_path
        
        # Buscar rar como alternativa
        rar_path = shutil.which("rar")
        if rar_path:
            return rar_path
        
        # Rutas específicas de Windows
        if os.name == 'nt':
            windows_paths = [
                "C:\\Program Files\\WinRAR\\UnRAR.exe",
                "C:\\Program Files\\WinRAR\\RAR.exe",
                "C:\\Program Files (x86)\\WinRAR\\UnRAR.exe",
                "C:\\Program Files (x86)\\WinRAR\\RAR.exe"
            ]
            
            for path in windows_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """Obtener tamaño de archivo o directorio"""
        path = Path(path)
        
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total
        return 0
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Formatear tamaño en bytes a formato legible"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def count_files(path: Union[str, Path]) -> int:
        """Contar archivos en directorio"""
        path = Path(path)
        
        if path.is_file():
            return 1
        elif path.is_dir():
            count = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    count += 1
            return count
        return 0
    
    @staticmethod
    def create_temp_directory(prefix: str = "sugar_rar_") -> Path:
        """Crear directorio temporal"""
        temp_dir = Path(tempfile.gettempdir()) / f"{prefix}{os.getpid()}"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: Union[str, Path]) -> bool:
        """Limpiar directorio temporal"""
        try:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_file_path(path: Union[str, Path]) -> bool:
        """Validar que un archivo existe"""
        return Path(path).exists()
    
    @staticmethod
    def validate_directory_path(path: Union[str, Path]) -> bool:
        """Validar que un directorio existe"""
        path_obj = Path(path)
        return path_obj.exists() and path_obj.is_dir()
    
    @staticmethod
    def ensure_directory_exists(path: Union[str, Path]) -> bool:
        """Asegurar que un directorio existe"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_extension(path: Union[str, Path]) -> str:
        """Obtener extensión de archivo"""
        return Path(path).suffix.lower()
    
    @staticmethod
    def is_rar_file(path: Union[str, Path]) -> bool:
        """Verificar si un archivo es RAR"""
        extension = RarUtils.get_file_extension(path)
        return extension == '.rar'
    
    @staticmethod
    def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calcular ratio de compresión"""
        if original_size == 0:
            return 0.0
        
        ratio = (1 - (compressed_size / original_size)) * 100
        return round(ratio, 2)
    
    @staticmethod
    def get_system_info() -> Dict[str, any]:
        """Obtener información del sistema"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/')._asdict()
        }
    
    @staticmethod
    def check_python_dependency(package_name: str) -> Dict[str, any]:
        """Verificar dependencia de Python"""
        try:
            module = __import__(package_name)
            return {
                'name': package_name,
                'status': 'installed',
                'version': getattr(module, '__version__', 'unknown')
            }
        except ImportError:
            return {
                'name': package_name,
                'status': 'missing',
                'version': None
            }
    
    @staticmethod
    def check_system_dependency(command: str) -> Dict[str, any]:
        """Verificar dependencia del sistema"""
        path = shutil.which(command)
        return {
            'name': command,
            'status': 'installed' if path else 'missing',
            'path': path
        }
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizar nombre de archivo"""
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Eliminar espacios al inicio y final
        filename = filename.strip()
        
        # Si está vacío, usar nombre por defecto
        if not filename:
            filename = "unnamed_file"
        
        return filename
    
    @staticmethod
    def get_unique_filename(base_path: Union[str, Path], filename: str) -> Path:
        """Obtener nombre de archivo único"""
        base_path = Path(base_path)
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            if counter == 1:
                new_filename = f"{name}{ext}"
            else:
                new_filename = f"{name}_{counter}{ext}"
            
            full_path = base_path / new_filename
            if not full_path.exists():
                return full_path
            
            counter += 1
    
    @staticmethod
    def split_path(path: Union[str, Path]) -> List[str]:
        """Dividir ruta en componentes"""
        return Path(path).parts
    
    @staticmethod
    def join_paths(*paths: Union[str, Path]) -> Path:
        """Unir rutas de manera segura"""
        return Path(*paths)
    
    @staticmethod
    def is_hidden_file(path: Union[str, Path]) -> bool:
        """Verificar si un archivo está oculto"""
        path_obj = Path(path)
        return path_obj.name.startswith('.')
    
    @staticmethod
    def filter_hidden_files(files: List[Union[str, Path]], include_hidden: bool = False) -> List[Path]:
        """Filtrar archivos ocultos"""
        if include_hidden:
            return [Path(f) for f in files]
        else:
            return [Path(f) for f in files if not RarUtils.is_hidden_file(f)]
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, any]:
        """Obtener información detallada de un archivo"""
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            return {'error': 'File not found'}
        
        stat = path_obj.stat()
        
        return {
            'name': path_obj.name,
            'path': str(path_obj),
            'size': stat.st_size,
            'size_human': RarUtils.format_size(stat.st_size),
            'is_file': path_obj.is_file(),
            'is_dir': path_obj.is_dir(),
            'is_hidden': RarUtils.is_hidden_file(path_obj),
            'extension': path_obj.suffix,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'permissions': oct(stat.st_mode)[-3:]
        }
