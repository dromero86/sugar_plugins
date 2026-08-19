"""
Bzip2 Helper
============

Clases auxiliares para el plugin bzip2.
"""

import os
import bz2
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

class Bzip2Helper:
    """
    Clase auxiliar para operaciones bzip2.
    """
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """Calcular hash de un archivo"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def validate_bzip2_file(file_path: str) -> Dict[str, Any]:
        """Validar que un archivo es un bzip2 válido"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
            
            is_valid = header.startswith(b'BZ')
            
            return {
                'is_valid': is_valid,
                'header': header.hex() if len(header) > 0 else None,
                'file_size': os.path.getsize(file_path)
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'file_size': 0
            }
    
    @staticmethod
    def get_compression_stats(original_size: int, compressed_size: int) -> Dict[str, Any]:
        """Calcular estadísticas de compresión"""
        if original_size == 0:
            return {
                'compression_ratio': 0,
                'space_saved': 0,
                'space_saved_percent': 0
            }
        
        compression_ratio = (1 - (compressed_size / original_size)) * 100
        space_saved = original_size - compressed_size
        space_saved_percent = (space_saved / original_size) * 100
        
        return {
            'compression_ratio': round(compression_ratio, 2),
            'space_saved': space_saved,
            'space_saved_percent': round(space_saved_percent, 2)
        }
    
    @staticmethod
    def estimate_compression_time(file_size: int, compression_level: int) -> float:
        """Estimar tiempo de compresión basado en tamaño y nivel"""
        # Estimación aproximada: 1MB por segundo en nivel 6
        base_time_per_mb = 1.0
        level_factor = compression_level / 6.0
        
        size_mb = file_size / (1024 * 1024)
        estimated_time = size_mb * base_time_per_mb * level_factor
        
        return round(estimated_time, 2)
    
    @staticmethod
    def get_optimal_compression_level(file_size: int, file_type: str = 'unknown') -> int:
        """Determinar nivel de compresión óptimo basado en tipo y tamaño de archivo"""
        # Para archivos de texto, usar compresión más alta
        if file_type in ['text', 'log', 'json', 'xml', 'csv']:
            if file_size < 1024 * 1024:  # < 1MB
                return 9
            elif file_size < 10 * 1024 * 1024:  # < 10MB
                return 8
            else:
                return 7
        
        # Para archivos binarios, usar compresión moderada
        elif file_type in ['binary', 'image', 'video', 'audio']:
            if file_size < 1024 * 1024:  # < 1MB
                return 6
            else:
                return 5
        
        # Por defecto
        else:
            return 6
    
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detectar tipo de archivo basado en extensión y contenido"""
        ext = Path(file_path).suffix.lower()
        
        # Mapeo de extensiones a tipos
        text_extensions = {'.txt', '.log', '.json', '.xml', '.csv', '.md', '.py', '.js', '.html', '.css'}
        binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mp3', '.wav', '.exe', '.dll'}
        
        if ext in text_extensions:
            return 'text'
        elif ext in binary_extensions:
            return 'binary'
        else:
            # Intentar detectar por contenido
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(1024)
                
                # Verificar si es texto
                try:
                    sample.decode('utf-8')
                    return 'text'
                except UnicodeDecodeError:
                    return 'binary'
            except:
                return 'unknown'
    
    @staticmethod
    def create_backup_filename(original_path: str) -> str:
        """Crear nombre de archivo de respaldo"""
        path = Path(original_path)
        timestamp = int(time.time())
        return str(path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}")
    
    @staticmethod
    def cleanup_temp_files(temp_dir: str, max_age_hours: int = 24) -> int:
        """Limpiar archivos temporales antiguos"""
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for file_path in temp_path.glob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except:
                        pass
        
        return cleaned_count
