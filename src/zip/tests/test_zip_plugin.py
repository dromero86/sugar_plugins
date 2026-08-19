#!/usr/bin/env python3
"""
Test Suite para Zip Plugin
=========================

Tests unitarios y de integración para el plugin Zip.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importar el plugin
from ..zip_plugin import ZipPlugin


class TestZipPlugin(unittest.TestCase):
    """Test cases para ZipPlugin"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.plugin = ZipPlugin()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_files = []
        
        # Crear archivos de prueba
        self._create_test_files()
    
    def tearDown(self):
        """Limpieza después de cada test"""
        # Limpiar archivos de prueba
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Limpiar directorio temporal
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def _create_test_files(self):
        """Crear archivos de prueba"""
        # Archivo de texto simple
        text_file = self.temp_dir / "test.txt"
        with open(text_file, 'w') as f:
            f.write("Este es un archivo de prueba para el plugin Zip")
        self.test_files.append(text_file)
        
        # Archivo con más contenido
        large_file = self.temp_dir / "large.txt"
        with open(large_file, 'w') as f:
            for i in range(100):
                f.write(f"Línea {i}: Contenido de prueba para compresión\n")
        self.test_files.append(large_file)
        
        # Subdirectorio con archivos
        subdir = self.temp_dir / "subdir"
        subdir.mkdir(exist_ok=True)
        
        subfile = subdir / "subfile.txt"
        with open(subfile, 'w') as f:
            f.write("Archivo en subdirectorio")
        self.test_files.append(subfile)
    
    def test_plugin_initialization(self):
        """Test de inicialización del plugin"""
        self.assertEqual(self.plugin.plugin_name, "ZipPlugin")
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertIsNotNone(self.plugin.temp_dir)
        self.assertTrue(self.plugin.temp_dir.exists())
    
    def test_supported_formats(self):
        """Test de formatos soportados"""
        expected_formats = ['zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', 'gz', 'bz2', 'xz']
        
        for fmt in expected_formats:
            self.assertIn(fmt, self.plugin.SUPPORTED_FORMATS)
            self.assertIn('extensions', self.plugin.SUPPORTED_FORMATS[fmt])
            self.assertIn('description', self.plugin.SUPPORTED_FORMATS[fmt])
    
    def test_format_detection(self):
        """Test de detección de formatos"""
        test_cases = [
            ('test.zip', 'zip'),
            ('test.tar', 'tar'),
            ('test.tar.gz', 'tar.gz'),
            ('test.tgz', 'tar.gz'),
            ('test.tar.bz2', 'tar.bz2'),
            ('test.tbz2', 'tar.bz2'),
            ('test.tar.xz', 'tar.xz'),
            ('test.txz', 'tar.xz'),
            ('test.gz', 'gz'),
            ('test.bz2', 'bz2'),
            ('test.xz', 'xz'),
            ('test.unknown', 'zip'),  # Por defecto
            ('', 'zip'),  # Vacío
        ]
        
        for file_path, expected_format in test_cases:
            detected = self.plugin._detect_format(file_path)
            self.assertEqual(detected, expected_format, 
                           f"Error detectando formato para {file_path}")
    
    def test_compress_zip(self):
        """Test de compresión ZIP"""
        source = str(self.temp_dir)
        destination = str(self.temp_dir / "test.zip")
        
        result = self.plugin.execute("zip_compress", {
            'source': source,
            'destination': destination,
            'format': 'zip',
            'compression_level': 6
        })
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['format'], 'zip')
        self.assertTrue(os.path.exists(destination))
        self.assertGreater(result['compressed_size'], 0)
    
    def test_compress_targz(self):
        """Test de compresión TAR.GZ"""
        source = str(self.temp_dir)
        destination = str(self.temp_dir / "test.tar.gz")
        
        result = self.plugin.execute("zip_compress", {
            'source': source,
            'destination': destination,
            'format': 'tar.gz',
            'compression_level': 6
        })
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['format'], 'tar.gz')
        self.assertTrue(os.path.exists(destination))
        self.assertGreater(result['compressed_size'], 0)
    
    def test_extract_zip(self):
        """Test de extracción ZIP"""
        # Primero crear un archivo ZIP
        source = str(self.temp_dir)
        zip_file = str(self.temp_dir / "test.zip")
        
        compress_result = self.plugin.execute("zip_compress", {
            'source': source,
            'destination': zip_file,
            'format': 'zip'
        })
        
        self.assertEqual(compress_result['status'], 'success')
        
        # Ahora extraer
        extract_dir = str(self.temp_dir / "extracted")
        extract_result = self.plugin.execute("zip_extract", {
            'source': zip_file,
            'destination': extract_dir
        })
        
        self.assertEqual(extract_result['status'], 'success')
        self.assertTrue(os.path.exists(extract_dir))
        self.assertGreater(extract_result['extracted_files'], 0)
    
    def test_info_command(self):
        """Test del comando info"""
        # Crear archivo ZIP
        source = str(self.temp_dir)
        zip_file = str(self.temp_dir / "test.zip")
        
        self.plugin.execute("zip_compress", {
            'source': source,
            'destination': zip_file,
            'format': 'zip'
        })
        
        # Obtener información
        info_result = self.plugin.execute("zip_info", {
            'source': zip_file
        })
        
        self.assertEqual(info_result['status'], 'success')
        self.assertEqual(info_result['format'], 'zip')
        self.assertGreater(info_result['size'], 0)
        self.assertIn('size_human', info_result)
        self.assertGreater(info_result['files_count'], 0)
    
    def test_list_command(self):
        """Test del comando list"""
        # Crear archivo ZIP
        source = str(self.temp_dir)
        zip_file = str(self.temp_dir / "test.zip")
        
        self.plugin.execute("zip_compress", {
            'source': source,
            'destination': zip_file,
            'format': 'zip'
        })
        
        # Listar contenido
        list_result = self.plugin.execute("zip_list", {
            'source': zip_file
        })
        
        self.assertEqual(list_result['status'], 'success')
        self.assertEqual(list_result['format'], 'zip')
        self.assertGreater(list_result['files_count'], 0)
        self.assertIsInstance(list_result['files'], list)
        self.assertGreater(len(list_result['files']), 0)
    
    def test_test_command(self):
        """Test del comando test"""
        # Crear archivo ZIP
        source = str(self.temp_dir)
        zip_file = str(self.temp_dir / "test.zip")
        
        self.plugin.execute("zip_compress", {
            'source': source,
            'destination': zip_file,
            'format': 'zip'
        })
        
        # Verificar integridad
        test_result = self.plugin.execute("zip_test", {
            'source': zip_file
        })
        
        self.assertEqual(test_result['status'], 'success')
        self.assertEqual(test_result['format'], 'zip')
        self.assertTrue(test_result['is_valid'])
    
    def test_convert_command(self):
        """Test del comando convert"""
        # Crear archivo ZIP
        source = str(self.temp_dir)
        zip_file = str(self.temp_dir / "test.zip")
        
        self.plugin.execute("zip_compress", {
            'source': source,
            'destination': zip_file,
            'format': 'zip'
        })
        
        # Convertir a TAR.GZ
        tar_gz_file = str(self.temp_dir / "test.tar.gz")
        convert_result = self.plugin.execute("zip_convert", {
            'source': zip_file,
            'destination': tar_gz_file,
            'target_format': 'tar.gz'
        })
        
        self.assertEqual(convert_result['status'], 'success')
        self.assertEqual(convert_result['format'], 'tar.gz')
        self.assertTrue(os.path.exists(tar_gz_file))
    
    def test_sdk_info_command(self):
        """Test del comando sdk_info"""
        sdk_result = self.plugin.execute("sdk_info", {})
        
        self.assertEqual(sdk_result['status'], 'success')
        self.assertEqual(sdk_result['plugin_name'], 'ZipPlugin')
        self.assertEqual(sdk_result['version'], '1.0.0')
        self.assertIn('sdk_components', sdk_result)
        self.assertIn('sdk_stats', sdk_result)
    
    def test_list_formats_command(self):
        """Test del comando list_formats"""
        formats_result = self.plugin.execute("list_formats", {})
        
        self.assertEqual(formats_result['status'], 'success')
        self.assertIn('supported_formats', formats_result)
        self.assertIn('total_formats', formats_result)
        self.assertEqual(formats_result['total_formats'], 8)
    
    def test_test_sdk_command(self):
        """Test del comando test_sdk"""
        sdk_test_result = self.plugin.execute("test_sdk", {})
        
        self.assertEqual(sdk_test_result['status'], 'success')
        self.assertIn('sdk_tests', sdk_test_result)
        self.assertIn('message', sdk_test_result)
    
    def test_error_handling(self):
        """Test de manejo de errores"""
        # Test con archivo inexistente
        result = self.plugin.execute("zip_info", {
            'source': '/archivo/inexistente.zip'
        })
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_size_calculation(self):
        """Test de cálculo de tamaños"""
        # Test archivo individual
        file_size = self.plugin._get_size(str(self.test_files[0]))
        self.assertGreater(file_size, 0)
        
        # Test directorio
        dir_size = self.plugin._get_size(str(self.temp_dir))
        self.assertGreater(dir_size, 0)
    
    def test_file_counting(self):
        """Test de conteo de archivos"""
        # Test archivo individual
        file_count = self.plugin._count_files(str(self.test_files[0]))
        self.assertEqual(file_count, 1)
        
        # Test directorio
        dir_count = self.plugin._count_files(str(self.temp_dir))
        self.assertGreater(dir_count, 1)
    
    def test_compression_ratio_calculation(self):
        """Test de cálculo de ratio de compresión"""
        test_data = {
            'original_size': 1000,
            'compressed_size': 500
        }
        
        ratio = self.plugin._calculate_compression_ratio(test_data)
        self.assertEqual(ratio, 50.0)
        
        # Test con valores extremos
        test_data_zero = {
            'original_size': 0,
            'compressed_size': 0
        }
        
        ratio_zero = self.plugin._calculate_compression_ratio(test_data_zero)
        self.assertEqual(ratio_zero, 0)
    
    def test_size_formatting(self):
        """Test de formateo de tamaños"""
        test_cases = [
            (0, "0B"),
            (1024, "1.0KB"),
            (1024*1024, "1.0MB"),
            (1024*1024*1024, "1.0GB"),
        ]
        
        for size_bytes, expected in test_cases:
            formatted = self.plugin._format_size(size_bytes)
            self.assertEqual(formatted, expected)


if __name__ == '__main__':
    unittest.main()