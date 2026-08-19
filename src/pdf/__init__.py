"""
PDF Plugin for Sugar
===================

Plugin para manipulación completa de documentos PDF.
Incluye lectura, escritura, extracción de texto, imágenes, metadatos,
y operaciones avanzadas de manipulación de PDFs.
"""

from .src.pdf_plugin import PDFPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__all__ = ["PDFPlugin"]