"""
Tests for PDF Plugin
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

# Importar el plugin
from ..src.pdf_plugin import PDFPlugin
from ..components.pdf_helper import PDFHelper

class TestPDFPlugin(unittest.TestCase):
    """Tests para el plugin PDF."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.plugin = PDFPlugin()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        # Limpiar archivos temporales
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_initialization(self):
        """Test de inicialización del plugin."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Plugin para manipulación completa de documentos PDF usando el SDK")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
    
    def test_available_commands(self):
        """Test de comandos disponibles."""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertIn("read_pdf", commands)
        self.assertIn("create_pdf", commands)
        self.assertIn("extract_text", commands)
        self.assertIn("merge_pdfs", commands)
        self.assertIn("analyze_pdf", commands)
        self.assertIn("check_dependencies", commands)
    
    def test_check_dependencies(self):
        """Test de verificación de dependencias."""
        result = self.plugin.execute("check_dependencies", {})
        self.assertIsInstance(result, dict)
        self.assertIn("plugin_name", result)
        self.assertIn("version", result)
        self.assertIn("dependency_status", result)
        self.assertEqual(result["status"], "success")
    
    def test_test_functionality(self):
        """Test de funcionalidad del plugin."""
        result = self.plugin.execute("test_functionality", {})
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
    
    def test_invalid_command(self):
        """Test de comando inválido."""
        with self.assertRaises(ValueError):
            self.plugin.execute("invalid_command", {})
    
    def test_read_pdf_invalid_file(self):
        """Test de lectura de PDF con archivo inválido."""
        config = {"file_path": "archivo_inexistente.pdf"}
        with self.assertRaises(FileNotFoundError):
            self.plugin.execute("read_pdf", config)
    
    def test_create_pdf_missing_output_path(self):
        """Test de creación de PDF sin ruta de salida."""
        config = {"title": "Test"}
        with self.assertRaises(ValueError):
            self.plugin.execute("create_pdf", config)
    
    def test_merge_pdfs_missing_files(self):
        """Test de combinación de PDFs sin archivos."""
        config = {"output_path": "output.pdf"}
        with self.assertRaises(ValueError):
            self.plugin.execute("merge_pdfs", config)
    
    def test_analyze_pdf_missing_file(self):
        """Test de análisis de PDF sin archivo."""
        config = {}
        with self.assertRaises(ValueError):
            self.plugin.execute("analyze_pdf", config)

class TestPDFHelper(unittest.TestCase):
    """Tests para el helper del plugin PDF."""
    
    def test_validate_file_path(self):
        """Test de validación de rutas de archivo."""
        # Test con archivo inexistente
        self.assertFalse(PDFHelper.validate_file_path("archivo_inexistente.pdf"))
        
        # Test con archivo que no es PDF
        with tempfile.NamedTemporaryFile(suffix=".txt") as f:
            self.assertFalse(PDFHelper.validate_file_path(f.name))
        
        # Test con archivo PDF válido (crear uno temporal)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(b"%PDF-1.4\n%Test PDF\n")
            f.flush()
            self.assertTrue(PDFHelper.validate_file_path(f.name))
    
    def test_create_temp_directory(self):
        """Test de creación de directorio temporal."""
        temp_dir = PDFHelper.create_temp_directory()
        self.assertTrue(os.path.exists(temp_dir))
        self.assertTrue(os.path.isdir(temp_dir))
        
        # Limpiar
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_format_file_size(self):
        """Test de formateo de tamaño de archivo."""
        self.assertEqual(PDFHelper.format_file_size(1024), "1.0 KB")
        self.assertEqual(PDFHelper.format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(PDFHelper.format_file_size(1024 * 1024 * 1024), "1.0 GB")
        self.assertEqual(PDFHelper.format_file_size(500), "500 B")
    
    def test_extract_metadata(self):
        """Test de extracción de metadatos."""
        # Mock del reader
        mock_reader = Mock()
        mock_reader.metadata = {
            "/Title": "Test Document",
            "/Author": "Test Author",
            "/Subject": "Test Subject"
        }
        
        metadata = PDFHelper.extract_metadata(mock_reader)
        self.assertEqual(metadata["Title"], "Test Document")
        self.assertEqual(metadata["Author"], "Test Author")
        self.assertEqual(metadata["Subject"], "Test Subject")

if __name__ == "__main__":
    unittest.main()