"""
PDF Helper Components
====================

Componentes auxiliares para el plugin PDF.
"""

import os
import tempfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PDFMetadata:
    """Estructura para metadatos de PDF."""
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    modification_date: str = ""
    keywords: str = ""

@dataclass
class PDFPageInfo:
    """Información de una página PDF."""
    page_number: int
    width: float
    height: float
    rotation: int
    text_content: str = ""
    image_count: int = 0

class PDFHelper:
    """Clase auxiliar para operaciones comunes de PDF."""
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Valida que el archivo existe y es un PDF."""
        if not file_path:
            return False
        
        if not os.path.exists(file_path):
            return False
        
        # Verificar extensión
        if not file_path.lower().endswith('.pdf'):
            return False
        
        return True
    
    @staticmethod
    def create_temp_directory(prefix: str = 'sugar_pdf_') -> str:
        """Crea un directorio temporal para archivos PDF."""
        return tempfile.mkdtemp(prefix=prefix)
    
    @staticmethod
    def clean_temp_files(temp_dir: str) -> None:
        """Limpia archivos temporales."""
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatea el tamaño de archivo en formato legible."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def extract_metadata(reader) -> Dict[str, Any]:
        """Extrae metadatos del PDF."""
        metadata = {}
        
        if hasattr(reader, 'metadata') and reader.metadata:
            for key, value in reader.metadata.items():
                if key.startswith('/'):
                    key = key[1:]  # Remover slash inicial
                metadata[key] = str(value) if value else ""
        
        return metadata