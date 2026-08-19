"""
Tests para el plugin RAR de Sugar
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Importar el plugin
from ..src.rar_plugin import RarPlugin


class TestRarPlugin(unittest.TestCase):
    """Tests para el plugin RAR"""
    
    def setUp(self):
        """Configurar el entorno de prueba"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.plugin = RarPlugin()
        
        # Crear archivos de prueba
        self.test_file = self.temp_dir / "test_file.txt"
        self.test_file.write_text("Este es un archivo de prueba para el plugin RAR")
        
        self.test_dir = self.temp_dir / "test_dir"
        self.test_dir.mkdir()
        
        (self.test_dir / "file1.txt").write_text("Archivo 1")
        (self.test_dir / "file2.txt").write_text("Archivo 2")
    
    def tearDown(self):
        """Limpiar el entorno de prueba"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if hasattr(self.plugin, 'cleanup'):
            self.plugin.cleanup()
    
    def test_plugin_initialization(self):
        """Probar inicialización del plugin"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Plugin para compresión y descompresión de archivos RAR usando el SDK")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
    
    def test_get_available_commands(self):
        """Probar obtención de comandos disponibles"""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertIn("rar_compress", commands)
        self.assertIn("rar_extract", commands)
        self.assertIn("rar_info", commands)
        self.assertIn("rar_list", commands)
        self.assertIn("rar_test", commands)
    
    def test_detect_format(self):
        """Probar detección de formato"""
        # Probar con archivo .rar
        format_result = self.plugin._detect_format("archivo.rar")
        self.assertEqual(format_result, "rar")
        
        # Probar con archivo sin extensión
        format_result = self.plugin._detect_format("archivo")
        self.assertEqual(format_result, "rar")  # Por defecto
        
        # Probar con archivo vacío
        format_result = self.plugin._detect_format("")
        self.assertEqual(format_result, "rar")  # Por defecto
    
    def test_calculate_compression_ratio(self):
        """Probar cálculo de ratio de compresión"""
        # Probar con valores válidos
        result = {
            'original_size': 1000,
            'compressed_size': 500
        }
        ratio = self.plugin._calculate_compression_ratio(result)
        self.assertEqual(ratio, 50.0)
        
        # Probar con valores cero
        result = {
            'original_size': 0,
            'compressed_size': 0
        }
        ratio = self.plugin._calculate_compression_ratio(result)
        self.assertEqual(ratio, 0)
        
        # Probar con valores faltantes
        result = {}
        ratio = self.plugin._calculate_compression_ratio(result)
        self.assertEqual(ratio, 0)
    
    def test_get_size(self):
        """Probar obtención de tamaño de archivos"""
        # Probar con archivo
        size = self.plugin._get_size(str(self.test_file))
        self.assertGreater(size, 0)
        
        # Probar con directorio
        size = self.plugin._get_size(str(self.test_dir))
        self.assertGreater(size, 0)
        
        # Probar con archivo inexistente
        size = self.plugin._get_size("archivo_inexistente.txt")
        self.assertEqual(size, 0)
    
    def test_count_files(self):
        """Probar conteo de archivos"""
        # Probar con archivo
        count = self.plugin._count_files(str(self.test_file))
        self.assertEqual(count, 1)
        
        # Probar con directorio
        count = self.plugin._count_files(str(self.test_dir))
        self.assertEqual(count, 2)  # file1.txt y file2.txt
        
        # Probar con archivo inexistente
        count = self.plugin._count_files("archivo_inexistente.txt")
        self.assertEqual(count, 0)
    
    def test_format_size(self):
        """Probar formateo de tamaños"""
        # Probar bytes
        formatted = self.plugin._format_size(1024)
        self.assertEqual(formatted, "1.0KB")
        
        # Probar megabytes
        formatted = self.plugin._format_size(1048576)
        self.assertEqual(formatted, "1.0MB")
        
        # Probar cero
        formatted = self.plugin._format_size(0)
        self.assertEqual(formatted, "0B")
    
    def test_validate_rar_params(self):
        """Probar validación de parámetros"""
        # Probar comando válido
        command = {
            'name': 'rar_compress',
            'source': str(self.test_file),
            'destination': 'output.rar'
        }
        result = self.plugin._validate_rar_params(command)
        self.assertTrue(result)
        
        # Probar comando sin parámetros requeridos
        command = {
            'name': 'rar_compress',
            'source': str(self.test_file)
            # Falta destination
        }
        result = self.plugin._validate_rar_params(command)
        self.assertFalse(result)
        
        # Probar comando con archivo inexistente
        command = {
            'name': 'rar_compress',
            'source': 'archivo_inexistente.txt',
            'destination': 'output.rar'
        }
        result = self.plugin._validate_rar_params(command)
        self.assertFalse(result)
    
    @patch('rarfile.RarFile')
    def test_info_command(self, mock_rarfile):
        """Probar comando de información"""
        # Configurar mock
        mock_rar = Mock()
        mock_rar.namelist.return_value = ['file1.txt', 'file2.txt']
        mock_rar.needs_password.return_value = False
        mock_rar.infolist.return_value = [
            Mock(filename='file1.txt', file_size=100, compress_size=50, date_time=(2023, 1, 1, 0, 0, 0), flag_bits=0),
            Mock(filename='file2.txt', file_size=200, compress_size=100, date_time=(2023, 1, 1, 0, 0, 0), flag_bits=0)
        ]
        mock_rarfile.return_value.__enter__.return_value = mock_rar
        
        # Probar comando
        config = {'source': str(self.test_file)}
        result = self.plugin._info_command(config)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['format'], 'rar')
        self.assertEqual(result['files_count'], 2)
        self.assertFalse(result['is_encrypted'])
    
    @patch('rarfile.RarFile')
    def test_list_command(self, mock_rarfile):
        """Probar comando de listado"""
        # Configurar mock
        mock_rar = Mock()
        mock_rar.namelist.return_value = ['file1.txt', 'file2.txt']
        mock_rarfile.return_value.__enter__.return_value = mock_rar
        
        # Probar comando
        config = {'source': str(self.test_file)}
        result = self.plugin._list_command(config)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['format'], 'rar')
        self.assertEqual(result['files_count'], 2)
        self.assertEqual(result['files'], ['file1.txt', 'file2.txt'])
    
    @patch('rarfile.RarFile')
    def test_test_command(self, mock_rarfile):
        """Probar comando de prueba de integridad"""
        # Configurar mock
        mock_rar = Mock()
        mock_rar.infolist.return_value = [
            Mock(filename='file1.txt'),
            Mock(filename='file2.txt')
        ]
        mock_rar.read.return_value = b"test data"
        mock_rarfile.return_value.__enter__.return_value = mock_rar
        
        # Probar comando
        config = {'source': str(self.test_file)}
        result = self.plugin._test_command(config)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['files_tested'], 2)
    
    def test_sdk_info_command(self):
        """Probar comando de información del SDK"""
        config = {}
        result = self.plugin._sdk_info_command(config)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['plugin_name'], 'rar')
        self.assertEqual(result['version'], '1.0.0')
        self.assertIn('sdk_components', result)
        self.assertIn('sdk_stats', result)
    
    def test_list_formats_command(self):
        """Probar comando de listado de formatos"""
        config = {}
        result = self.plugin._list_formats_command(config)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('supported_formats', result)
        self.assertIn('total_formats', result)
        self.assertGreater(result['total_formats'], 0)
    
    def test_check_dependencies_command(self):
        """Probar comando de verificación de dependencias"""
        config = {}
        result = self.plugin._check_dependencies_command(config)
        
        self.assertIn('python_dependencies', result)
        self.assertIn('system_dependencies', result)
        self.assertIn('all_satisfied', result)


if __name__ == '__main__':
    unittest.main()
