"""
Tests for YAML Plugin
"""

import unittest
import tempfile
import os
import sys
import yaml
from pathlib import Path

# Agregar el directorio raíz al path para importar Sugar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from plugins.src.yaml.YAMLPlugin import YAMLPlugin


class TestYAMLPlugin(unittest.TestCase):
    """Test cases for YAML Plugin"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.plugin = YAMLPlugin()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "YAML support for Sugar Language - write Sugar scripts using YAML syntax")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_available_commands(self):
        """Test available commands"""
        commands = self.plugin.get_available_commands()
        expected_commands = [
            "process_file",
            "convert_json_to_yaml", 
            "validate_yaml",
            "convert_directory",
            "register_cli"
        ]
        
        for command in expected_commands:
            self.assertIn(command, commands)
    
    def test_yaml_parsing(self):
        """Test YAML parsing functionality"""
        yaml_content = """
task:
  - print:
      text: "Test YAML parsing"
  - let:
      name: "test_var"
      value: "success"
  - print:
      text: "{{test_var}}"
"""
        
        # Crear archivo YAML temporal
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # Probar parsing
        result = self.plugin.execute("process_file", {"file_path": yaml_file})
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Archivo YAML parseado", result["message"])
    
    def test_yaml_vs_json_equivalence(self):
        """Test that YAML and JSON produce equivalent structures"""
        yaml_content = """
task:
  - print:
      text: "Hello"
  - let:
      name: "var1"
      value: 42
  - simple:
      operator: "add"
      a: 10
      b: 20
      result: "sum"
"""
        
        json_content = {
            "task": [
                {
                    "print": {
                        "text": "Hello"
                    }
                },
                {
                    "let": {
                        "name": "var1",
                        "value": 42
                    }
                },
                {
                    "simple": {
                        "operator": "add",
                        "a": 10,
                        "b": 20,
                        "result": "sum"
                    }
                }
            ]
        }
        
        # Parsear YAML
        yaml_data = yaml.safe_load(yaml_content)
        
        # Comparar estructuras
        self.assertEqual(yaml_data, json_content)
    
    def test_yaml_advanced_features(self):
        """Test advanced YAML features"""
        yaml_content = """
# Anclajes y referencias
config: &db_config
  host: "localhost"
  port: 5432

# Variables con listas
variables:
  features:
    - "YAML"
    - "JSON"
    - "AST"

task:
  - let:
      name: "db_settings"
      value: "{{config}}"
  - print:
      text: "Features: {{variables.features}}"
"""
        
        data = yaml.safe_load(yaml_content)
        
        # Verificar anclajes
        self.assertIn('config', data)
        self.assertIn('variables', data)
        self.assertIn('task', data)
        
        # Verificar que las referencias funcionan
        self.assertEqual(data['config']['host'], "localhost")
        self.assertEqual(data['config']['port'], 5432)
        self.assertEqual(len(data['variables']['features']), 3)
    
    def test_convert_json_to_yaml(self):
        """Test JSON to YAML conversion"""
        json_content = {
            "task": [
                {
                    "print": {
                        "text": "Hello from JSON"
                    }
                },
                {
                    "let": {
                        "name": "message",
                        "value": "Converted from JSON"
                    }
                }
            ]
        }
        
        # Crear archivo JSON temporal
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, 'w') as f:
            import json
            json.dump(json_content, f)
        
        # Convertir a YAML
        result = self.plugin.execute("convert_json_to_yaml", {
            "json_file": json_file,
            "yaml_file": os.path.join(self.temp_dir, "test.yaml")
        })
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Convertido", result["message"])
        
        # Verificar que el archivo YAML se creó
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        self.assertTrue(os.path.exists(yaml_file))
        
        # Verificar que el contenido es válido
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        self.assertEqual(yaml_data, json_content)
    
    def test_validate_yaml(self):
        """Test YAML validation"""
        # Crear archivo YAML válido
        yaml_content = """
task:
  - print:
      text: "Valid YAML"
"""
        
        yaml_file = os.path.join(self.temp_dir, "valid.yaml")
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # Validar YAML válido
        result = self.plugin.execute("validate_yaml", {"yaml_file": yaml_file})
        self.assertEqual(result["status"], "success")
        self.assertIn("YAML válido", result["message"])
        
        # Crear archivo YAML inválido
        invalid_yaml_content = """
task:
  - print:
      text: "Invalid YAML
      missing_quote: true
"""
        
        invalid_yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_yaml_file, 'w') as f:
            f.write(invalid_yaml_content)
        
        # Validar YAML inválido
        with self.assertRaises(ValueError):
            self.plugin.execute("validate_yaml", {"yaml_file": invalid_yaml_file})
    
    def test_convert_directory(self):
        """Test directory conversion"""
        # Crear archivos JSON temporales
        json_files = [
            ("file1.json", {"task": [{"print": {"text": "File 1"}}]}),
            ("file2.json", {"task": [{"print": {"text": "File 2"}}]}),
            ("subdir/file3.json", {"task": [{"print": {"text": "File 3"}}]})
        ]
        
        for filename, content in json_files:
            filepath = os.path.join(self.temp_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                import json
                json.dump(content, f)
        
        # Convertir directorio
        result = self.plugin.execute("convert_directory", {
            "input_dir": self.temp_dir,
            "recursive": True
        })
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["converted_count"], 3)
        self.assertEqual(result["total_count"], 3)
        
        # Verificar que los archivos YAML se crearon
        for filename, _ in json_files:
            yaml_file = os.path.join(self.temp_dir, filename.replace('.json', '.yaml'))
            self.assertTrue(os.path.exists(yaml_file))
    
    def test_file_not_found_error(self):
        """Test error handling for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            self.plugin.execute("process_file", {"file_path": "nonexistent.yaml"})
        
        with self.assertRaises(FileNotFoundError):
            self.plugin.execute("convert_json_to_yaml", {"json_file": "nonexistent.json"})
        
        with self.assertRaises(FileNotFoundError):
            self.plugin.execute("validate_yaml", {"yaml_file": "nonexistent.yaml"})
    
    def test_missing_parameters(self):
        """Test error handling for missing parameters"""
        with self.assertRaises(ValueError):
            self.plugin.execute("process_file", {})
        
        with self.assertRaises(ValueError):
            self.plugin.execute("convert_json_to_yaml", {})
        
        with self.assertRaises(ValueError):
            self.plugin.execute("validate_yaml", {})
    
    def test_invalid_command(self):
        """Test error handling for invalid commands"""
        with self.assertRaises(ValueError):
            self.plugin.execute("invalid_command", {})
    
    def test_dependencies(self):
        """Test dependency checking"""
        # Verificar que PyYAML está disponible
        try:
            import yaml
            self.assertTrue(True, "PyYAML is available")
        except ImportError:
            self.fail("PyYAML is not available")
    
    def test_plugin_configuration(self):
        """Test plugin configuration"""
        self.assertIn("pyyaml", self.plugin.DEPENDENCIES)
        self.assertIn("pyyaml>=6.0", self.plugin.REQUIREMENTS)
        self.assertEqual(self.plugin.SYSTEM_DEPENDENCIES, [])
        
        # Verificar requerimientos de hardware
        self.assertIn("min_ram_gb", self.plugin.HARDWARE_REQUIREMENTS)
        self.assertIn("min_disk_gb", self.plugin.HARDWARE_REQUIREMENTS)
        self.assertIn("min_cpu_cores", self.plugin.HARDWARE_REQUIREMENTS)
        
        # Verificar requerimientos de permisos
        self.assertIn("network_access", self.plugin.PERMISSION_REQUIREMENTS)
        self.assertIn("write_access", self.plugin.PERMISSION_REQUIREMENTS)
        self.assertIn("read_access", self.plugin.PERMISSION_REQUIREMENTS)


class TestYAMLPluginIntegration(unittest.TestCase):
    """Integration tests for YAML Plugin"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.plugin = YAMLPlugin()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow: JSON -> YAML -> Validation -> Processing"""
        # 1. Crear archivo JSON
        json_content = {
            "task": [
                {
                    "print": {
                        "text": "Workflow test"
                    }
                },
                {
                    "let": {
                        "name": "workflow_var",
                        "value": "success"
                    }
                }
            ]
        }
        
        json_file = os.path.join(self.temp_dir, "workflow.json")
        with open(json_file, 'w') as f:
            import json
            json.dump(json_content, f)
        
        # 2. Convertir a YAML
        yaml_file = os.path.join(self.temp_dir, "workflow.yaml")
        result = self.plugin.execute("convert_json_to_yaml", {
            "json_file": json_file,
            "yaml_file": yaml_file
        })
        
        self.assertEqual(result["status"], "success")
        
        # 3. Validar YAML
        result = self.plugin.execute("validate_yaml", {"yaml_file": yaml_file})
        self.assertEqual(result["status"], "success")
        
        # 4. Procesar YAML
        result = self.plugin.execute("process_file", {"file_path": yaml_file})
        self.assertEqual(result["status"], "success")
        
        # 5. Verificar contenido
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        self.assertEqual(yaml_data, json_content)


if __name__ == "__main__":
    # Ejecutar tests
    unittest.main(verbosity=2)