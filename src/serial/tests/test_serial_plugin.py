"""
Tests para SerialPlugin.
========================

Tests unitarios para el plugin principal de comunicación serie.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Agregar el directorio del plugin al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.SerialPlugin import SerialPlugin

class TestSerialPlugin(unittest.TestCase):
    """Tests para SerialPlugin."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.plugin = SerialPlugin()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        self.plugin.cleanup()
    
    def test_plugin_initialization(self):
        """Test inicialización del plugin."""
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Plugin de comunicación serie universal para Sugar con soporte multiplataforma")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
        self.assertIn("serial", self.plugin.DEPENDENCIES)
        self.assertIn("pyserial>=3.5", self.plugin.REQUIREMENTS)
    
    def test_get_available_commands(self):
        """Test obtención de comandos disponibles."""
        commands = self.plugin.get_available_commands()
        
        # Verificar comandos de conexión
        self.assertIn("connect", commands)
        self.assertIn("disconnect", commands)
        self.assertIn("list_ports", commands)
        self.assertIn("test_connection", commands)
        
        # Verificar comandos de comunicación
        self.assertIn("write", commands)
        self.assertIn("read", commands)
        self.assertIn("read_line", commands)
        self.assertIn("read_until", commands)
        self.assertIn("read_bytes", commands)
        self.assertIn("flush", commands)
        
        # Verificar comandos de configuración
        self.assertIn("configure", commands)
        self.assertIn("get_config", commands)
        self.assertIn("set_timeout", commands)
        self.assertIn("set_baudrate", commands)
        self.assertIn("set_parity", commands)
        self.assertIn("set_stopbits", commands)
        self.assertIn("set_bytesize", commands)
        
        # Verificar comandos de control de líneas
        self.assertIn("set_dtr", commands)
        self.assertIn("set_rts", commands)
        self.assertIn("get_cts", commands)
        self.assertIn("get_dsr", commands)
        self.assertIn("get_ri", commands)
        self.assertIn("get_cd", commands)
        
        # Verificar comandos de monitoreo
        self.assertIn("get_status", commands)
        self.assertIn("get_info", commands)
        self.assertIn("monitor", commands)
        self.assertIn("log_activity", commands)
    
    def test_unknown_command(self):
        """Test comando desconocido."""
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("unknown_command", {})
        
        self.assertIn("Comando desconocido", str(context.exception))
    
    @patch('serial.tools.list_ports.comports')
    def test_list_ports(self, mock_comports):
        """Test listado de puertos."""
        # Mock de puertos
        mock_port = MagicMock()
        mock_port.device = "COM1"
        mock_port.description = "USB Serial Port"
        mock_port.hwid = "USB\\VID_1234&PID_5678"
        mock_port.vid = 0x1234
        mock_port.pid = 0x5678
        mock_port.serial_number = "123456"
        mock_port.manufacturer = "Test Manufacturer"
        mock_port.product = "Test Product"
        mock_port.interface = "USB"
        
        mock_comports.return_value = [mock_port]
        
        config = {"include_info": True}
        result = self.plugin.execute("list_ports", config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["ports"]), 1)
        self.assertEqual(result["ports"][0]["device"], "COM1")
    
    def test_list_ports_with_filter(self):
        """Test listado de puertos con filtro."""
        with patch('serial.tools.list_ports.comports') as mock_comports:
            # Mock de puertos
            mock_port = MagicMock()
            mock_port.device = "COM1"
            mock_port.description = "USB Serial Port"
            mock_port.hwid = "USB\\VID_1234&PID_5678"
            mock_port.vid = 0x1234
            mock_port.pid = 0x5678
            mock_port.serial_number = "123456"
            mock_port.manufacturer = "Test Manufacturer"
            mock_port.product = "Test Product"
            mock_port.interface = "USB"
            
            mock_comports.return_value = [mock_port]
            
            config = {"filter": "USB"}
            result = self.plugin.execute("list_ports", config)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["count"], 1)
    
    def test_connect_missing_port(self):
        """Test conexión sin puerto especificado."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("connect", config)
        
        self.assertIn("Parámetro 'port' es requerido", str(context.exception))
    
    def test_disconnect_missing_session(self):
        """Test desconexión sin sesión especificada."""
        config = {}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("disconnect", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_write_missing_session(self):
        """Test escritura sin sesión especificada."""
        config = {"data": "test data"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("write", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_write_missing_data(self):
        """Test escritura sin datos especificados."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("write", config)
        
        self.assertIn("Parámetro 'data' es requerido", str(context.exception))
    
    def test_read_missing_session(self):
        """Test lectura sin sesión especificada."""
        config = {}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("read", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_read_until_missing_terminator(self):
        """Test lectura hasta terminador sin terminador especificado."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("read_until", config)
        
        self.assertIn("Parámetro 'terminator' es requerido", str(context.exception))
    
    def test_read_bytes_missing_size(self):
        """Test lectura de bytes sin tamaño especificado."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("read_bytes", config)
        
        self.assertIn("Parámetro 'size' es requerido", str(context.exception))
    
    def test_configure_missing_session(self):
        """Test configuración sin sesión especificada."""
        config = {"baudrate": 115200}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("configure", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_set_dtr_missing_session(self):
        """Test control DTR sin sesión especificada."""
        config = {"state": True}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("set_dtr", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_set_dtr_missing_state(self):
        """Test control DTR sin estado especificado."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("set_dtr", config)
        
        self.assertIn("Parámetro 'state' es requerido", str(context.exception))
    
    def test_set_rts_missing_session(self):
        """Test control RTS sin sesión especificada."""
        config = {"state": True}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("set_rts", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_set_rts_missing_state(self):
        """Test control RTS sin estado especificado."""
        config = {"session": "test_session"}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("set_rts", config)
        
        self.assertIn("Parámetro 'state' es requerido", str(context.exception))
    
    def test_monitor_missing_session(self):
        """Test monitoreo sin sesión especificada."""
        config = {}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("monitor", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_log_activity_missing_session(self):
        """Test logs de actividad sin sesión especificada."""
        config = {}
        
        with self.assertRaises(ValueError) as context:
            self.plugin.execute("log_activity", config)
        
        self.assertIn("Parámetro 'session' es requerido", str(context.exception))
    
    def test_meta_hook_empty_config(self):
        """Test meta hook con configuración vacía."""
        config = {}
        result = self.plugin.meta_hook(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["sessions_configured"], 0)
        self.assertEqual(result["auto_connected"], 0)
    
    def test_meta_hook_with_sessions(self):
        """Test meta hook con sesiones configuradas."""
        config = {
            "options": {
                "session1": {
                    "port": "COM1",
                    "baudrate": 9600,
                    "auto_connect": False
                },
                "session2": {
                    "port": "COM2", 
                    "baudrate": 115200,
                    "auto_connect": True
                }
            }
        }
        
        with patch.object(self.plugin, '_auto_connect_session') as mock_auto_connect:
            result = self.plugin.meta_hook(config)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["sessions_configured"], 2)
            self.assertEqual(result["auto_connected"], 1)
            
            # Verificar que se llamó auto_connect para session2
            mock_auto_connect.assert_called_once_with("session2", config["options"]["session2"])
    
    def test_meta_hook_auto_connect_error(self):
        """Test meta hook con error en auto-conexión."""
        config = {
            "options": {
                "session1": {
                    "port": "COM1",
                    "baudrate": 9600,
                    "auto_connect": True
                }
            }
        }
        
        with patch.object(self.plugin, '_auto_connect_session', side_effect=Exception("Connection failed")):
            result = self.plugin.meta_hook(config)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["sessions_configured"], 1)
            self.assertEqual(result["auto_connected"], 0)
    
    def test_cleanup(self):
        """Test limpieza del plugin."""
        # Agregar algunas sesiones y monitores mock
        self.plugin.sessions["test_session"] = Mock()
        self.plugin.monitors["test_monitor"] = Mock()
        
        # Ejecutar cleanup
        self.plugin.cleanup()
        
        # Verificar que se limpiaron las estructuras
        self.assertEqual(len(self.plugin.sessions), 0)
        self.assertEqual(len(self.plugin.monitors), 0)
        self.assertEqual(len(self.plugin.meta_config), 0)
        self.assertEqual(len(self.plugin.preconfigured_sessions), 0)

if __name__ == '__main__':
    unittest.main()