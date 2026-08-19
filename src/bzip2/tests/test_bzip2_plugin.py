"""
Tests para el plugin bzip2.
"""

import unittest
import tempfile
import os
import bz2
from pathlib import Path
from unittest.mock import Mock, patch

# Importar el plugin
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from bzip2_plugin import Bzip2Plugin

class TestBzip2Plugin(unittest.TestCase):
    """Tests para el plugin Bzip2."""
    
    def setUp(self):
        """Configurar el entorno de pruebas."""
        self.plugin = Bzip2Plugin()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        self.compressed_file = os.path.join(self.temp_dir, "test.txt.bz2")
        
        # Crear archivo de prueba
        with open(self.test_file, 'w') as f:
            f.write("Este es un archivo de prueba para el plugin bzip2.\n" * 100)
    
    def tearDown(self):
        """Limpiar después de las pruebas."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_initialization(self):
        """Probar inicialización del plugin."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Plugin para compresión y descompresión de archivos usando bzip2 con el SDK")
    
    def test_get_available_commands(self):
        """Probar obtención de comandos disponibles."""
        commands = self.plugin.get_available_commands()
        expected_commands = [
            "bzip2_compress", "bzip2_decompress", "bzip2_info", 
            "bzip2_test", "bzip2_convert", "bzip2_merge", 
            "bzip2_split", "sdk_info", "test_sdk"
        ]
        
        for command in expected_commands:
            self.assertIn(command, commands)
    
    def test_compress_command(self):
        """Probar comando de compresión."""
        config = {
            'source': self.test_file,
            'destination': self.compressed_file,
            'compression_level': 6
        }
        
        result = self.plugin.execute("bzip2_compress", config)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(self.compressed_file))
        self.assertGreater(result['compression_ratio'], 0)
        self.assertGreater(result['processing_time'], 0)
    
    def test_decompress_command(self):
        """Probar comando de descompresión."""
        # Primero comprimir
        compress_config = {
            'source': self.test_file,
            'destination': self.compressed_file,
            'compression_level': 6
        }
        self.plugin.execute("bzip2_compress", compress_config)
        
        # Luego descomprimir
        decompress_config = {
            'source': self.compressed_file,
            'destination': os.path.join(self.temp_dir, "decompressed.txt")
        }
        
        result = self.plugin.execute("bzip2_decompress", decompress_config)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(decompress_config['destination']))
    
    def test_info_command(self):
        """Probar comando de información."""
        # Primero comprimir
        compress_config = {
            'source': self.test_file,
            'destination': self.compressed_file,
            'compression_level': 6
        }
        self.plugin.execute("bzip2_compress", compress_config)
        
        # Obtener información
        info_config = {
            'source': self.compressed_file
        }
        
        result = self.plugin.execute("bzip2_info", info_config)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['is_valid_bzip2'])
        self.assertGreater(result['file_size'], 0)
    
    def test_test_command(self):
        """Probar comando de prueba de integridad."""
        # Primero comprimir
        compress_config = {
            'source': self.test_file,
            'destination': self.compressed_file,
            'compression_level': 6
        }
        self.plugin.execute("bzip2_compress", compress_config)
        
        # Probar integridad
        test_config = {
            'source': self.compressed_file
        }
        
        result = self.plugin.execute("bzip2_test", test_config)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['is_valid'])
        self.assertGreater(result['decompressed_size'], 0)
    
    def test_sdk_info_command(self):
        """Probar comando de información del SDK."""
        config = {}
        
        result = self.plugin.execute("sdk_info", config)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['plugin_name'], 'bzip2')
        self.assertEqual(result['version'], '1.0.0')
        self.assertIsInstance(result['sdk_components'], list)
    
    def test_test_sdk_command(self):
        """Probar comando de prueba del SDK."""
        config = {}
        
        result = self.plugin.execute("test_sdk", config)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('tests', result)
        self.assertIsInstance(result['tests'], dict)
    
    def test_invalid_command(self):
        """Probar comando inválido."""
        config = {}
        
        with self.assertRaises(ValueError):
            self.plugin.execute("invalid_command", config)
    
    def test_compression_levels(self):
        """Probar diferentes niveles de compresión."""
        for level in [1, 6, 9]:
            compressed_file = os.path.join(self.temp_dir, f"test_level_{level}.bz2")
            config = {
                'source': self.test_file,
                'destination': compressed_file,
                'compression_level': level
            }
            
            result = self.plugin.execute("bzip2_compress", config)
            
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['compression_level'], level)
            self.assertTrue(os.path.exists(compressed_file))
    
    def test_calculate_compression_ratio(self):
        """Probar cálculo de ratio de compresión."""
        result = {
            'original_size': 1000,
            'compressed_size': 500
        }
        
        ratio = self.plugin._calculate_compression_ratio(result)
        self.assertEqual(ratio, 50.0)
    
    def test_get_size(self):
        """Probar obtención de tamaño de archivo."""
        size = self.plugin._get_size(self.test_file)
        self.assertGreater(size, 0)
    
    def test_validate_bzip2_params(self):
        """Probar validación de parámetros."""
        # Parámetros válidos
        valid_command = {
            'name': 'bzip2_compress',
            'source': self.test_file,
            'destination': self.compressed_file
        }
        self.assertTrue(self.plugin._validate_bzip2_params(valid_command))
        
        # Parámetros inválidos - falta source
        invalid_command = {
            'name': 'bzip2_compress',
            'destination': self.compressed_file
        }
        self.assertFalse(self.plugin._validate_bzip2_params(invalid_command))
        
        # Parámetros inválidos - archivo no existe
        invalid_command = {
            'name': 'bzip2_compress',
            'source': 'archivo_inexistente.txt',
            'destination': self.compressed_file
        }
        self.assertFalse(self.plugin._validate_bzip2_params(invalid_command))

if __name__ == '__main__':
    unittest.main()
