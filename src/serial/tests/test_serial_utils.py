"""
Tests para SerialUtils.
======================

Tests unitarios para las utilidades del plugin serial.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Agregar el directorio del plugin al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from components.SerialUtils import SerialUtils

class TestSerialUtils(unittest.TestCase):
    """Tests para SerialUtils."""
    
    def test_detect_platform(self):
        """Test detección de plataforma."""
        platform = SerialUtils.detect_platform()
        self.assertIn(platform, ["windows", "linux", "macos", "unknown"])
    
    def test_normalize_port_name_windows(self):
        """Test normalización de puertos en Windows."""
        with patch.object(SerialUtils, 'detect_platform', return_value='windows'):
            # Test puerto COM
            result = SerialUtils.normalize_port_name("COM1")
            self.assertEqual(result, "COM1")
            
            # Test número solo
            result = SerialUtils.normalize_port_name("1")
            self.assertEqual(result, "COM1")
            
            # Test minúsculas
            result = SerialUtils.normalize_port_name("com3")
            self.assertEqual(result, "COM3")
    
    def test_normalize_port_name_linux(self):
        """Test normalización de puertos en Linux."""
        with patch.object(SerialUtils, 'detect_platform', return_value='linux'):
            # Test puerto completo
            result = SerialUtils.normalize_port_name("/dev/ttyUSB0")
            self.assertEqual(result, "/dev/ttyUSB0")
            
            # Test puerto sin /dev/
            result = SerialUtils.normalize_port_name("ttyUSB0")
            self.assertEqual(result, "/dev/ttyUSB0")
            
            # Test puerto sin tty
            result = SerialUtils.normalize_port_name("USB0")
            self.assertEqual(result, "/dev/ttyUSB0")
    
    def test_normalize_port_name_macos(self):
        """Test normalización de puertos en macOS."""
        with patch.object(SerialUtils, 'detect_platform', return_value='macos'):
            # Test puerto completo
            result = SerialUtils.normalize_port_name("/dev/cu.usbserial")
            self.assertEqual(result, "/dev/cu.usbserial")
            
            # Test puerto sin /dev/
            result = SerialUtils.normalize_port_name("cu.usbserial")
            self.assertEqual(result, "/dev/cu.usbserial")
            
            # Test puerto sin cu.
            result = SerialUtils.normalize_port_name("usbserial")
            self.assertEqual(result, "/dev/cu.usbserial")
    
    def test_validate_baudrate(self):
        """Test validación de velocidad de baudios."""
        # Velocidades válidas
        self.assertTrue(SerialUtils.validate_baudrate(9600))
        self.assertTrue(SerialUtils.validate_baudrate(115200))
        self.assertTrue(SerialUtils.validate_baudrate(57600))
        
        # Velocidades inválidas
        self.assertFalse(SerialUtils.validate_baudrate(12345))
        self.assertFalse(SerialUtils.validate_baudrate(0))
        self.assertFalse(SerialUtils.validate_baudrate(-1))
    
    def test_validate_parity(self):
        """Test validación de paridad."""
        # Paridades válidas
        self.assertTrue(SerialUtils.validate_parity("NONE"))
        self.assertTrue(SerialUtils.validate_parity("EVEN"))
        self.assertTrue(SerialUtils.validate_parity("ODD"))
        self.assertTrue(SerialUtils.validate_parity("MARK"))
        self.assertTrue(SerialUtils.validate_parity("SPACE"))
        
        # Paridades inválidas
        self.assertFalse(SerialUtils.validate_parity("INVALID"))
        self.assertFalse(SerialUtils.validate_parity(""))
        self.assertFalse(SerialUtils.validate_parity("none"))  # minúsculas
    
    def test_validate_stopbits(self):
        """Test validación de bits de parada."""
        # Bits válidos
        self.assertTrue(SerialUtils.validate_stopbits(1))
        self.assertTrue(SerialUtils.validate_stopbits(2))
        
        # Bits inválidos
        self.assertFalse(SerialUtils.validate_stopbits(0))
        self.assertFalse(SerialUtils.validate_stopbits(3))
        self.assertFalse(SerialUtils.validate_stopbits(-1))
    
    def test_validate_bytesize(self):
        """Test validación de tamaño de bytes."""
        # Tamaños válidos
        self.assertTrue(SerialUtils.validate_bytesize(5))
        self.assertTrue(SerialUtils.validate_bytesize(6))
        self.assertTrue(SerialUtils.validate_bytesize(7))
        self.assertTrue(SerialUtils.validate_bytesize(8))
        
        # Tamaños inválidos
        self.assertFalse(SerialUtils.validate_bytesize(4))
        self.assertFalse(SerialUtils.validate_bytesize(9))
        self.assertFalse(SerialUtils.validate_bytesize(0))
    
    def test_parse_encoding(self):
        """Test parseo de codificación."""
        # Codificaciones válidas
        self.assertEqual(SerialUtils.parse_encoding("utf-8"), "utf-8")
        self.assertEqual(SerialUtils.parse_encoding("ASCII"), "ascii")
        self.assertEqual(SerialUtils.parse_encoding("HEX"), "hex")
        self.assertEqual(SerialUtils.parse_encoding("BINARY"), "binary")
        
        # Codificación inválida (debe retornar default)
        self.assertEqual(SerialUtils.parse_encoding("invalid"), "utf-8")
    
    def test_encode_data(self):
        """Test codificación de datos."""
        # Codificación UTF-8
        result = SerialUtils.encode_data("Hello", "utf-8")
        self.assertEqual(result, b"Hello")
        
        # Codificación ASCII
        result = SerialUtils.encode_data("Hello", "ascii")
        self.assertEqual(result, b"Hello")
        
        # Codificación HEX
        result = SerialUtils.encode_data("48656C6C6F", "hex")
        self.assertEqual(result, b"Hello")
        
        # Codificación BINARY
        result = SerialUtils.encode_data("\\x48\\x65\\x6C\\x6C\\x6F", "binary")
        self.assertEqual(result, b"Hello")
    
    def test_decode_data(self):
        """Test decodificación de datos."""
        # Decodificación UTF-8
        result = SerialUtils.decode_data(b"Hello", "utf-8")
        self.assertEqual(result, "Hello")
        
        # Decodificación ASCII
        result = SerialUtils.decode_data(b"Hello", "ascii")
        self.assertEqual(result, "Hello")
        
        # Decodificación HEX
        result = SerialUtils.decode_data(b"Hello", "hex")
        self.assertEqual(result, "48656C6C6F")
        
        # Decodificación BINARY
        result = SerialUtils.decode_data(b"Hello", "binary")
        self.assertEqual(result, "Hello")
    
    def test_parse_eol(self):
        """Test parseo de caracteres de fin de línea."""
        # EOL válidos
        self.assertEqual(SerialUtils.parse_eol("\\n"), b"\\n")
        self.assertEqual(SerialUtils.parse_eol("\\r"), b"\\r")
        self.assertEqual(SerialUtils.parse_eol("\\r\\n"), b"\\r\\n")
        self.assertEqual(SerialUtils.parse_eol("\\0"), b"\\0")
        self.assertEqual(SerialUtils.parse_eol(""), b"")
    
    @patch('serial.tools.list_ports.comports')
    def test_list_available_ports(self, mock_comports):
        """Test listado de puertos disponibles."""
        # Mock de puertos
        mock_port1 = MagicMock()
        mock_port1.device = "COM1"
        mock_port1.description = "USB Serial Port"
        mock_port1.hwid = "USB\\VID_1234&PID_5678"
        mock_port1.vid = 0x1234
        mock_port1.pid = 0x5678
        mock_port1.serial_number = "123456"
        mock_port1.manufacturer = "Test Manufacturer"
        mock_port1.product = "Test Product"
        mock_port1.interface = "USB"
        
        mock_comports.return_value = [mock_port1]
        
        ports = SerialUtils.list_available_ports()
        
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0]["device"], "COM1")
        self.assertEqual(ports[0]["description"], "USB Serial Port")
        self.assertEqual(ports[0]["vid"], 0x1234)
        self.assertEqual(ports[0]["pid"], 0x5678)
    
    def test_filter_ports(self):
        """Test filtrado de puertos."""
        ports = [
            {
                "device": "COM1",
                "description": "USB Serial Port",
                "manufacturer": "FTDI",
                "product": "FT232R"
            },
            {
                "device": "COM2", 
                "description": "Bluetooth Serial Port",
                "manufacturer": "Microsoft",
                "product": "Bluetooth"
            },
            {
                "device": "COM3",
                "description": "Virtual Serial Port",
                "manufacturer": "Virtual",
                "product": "VCP"
            }
        ]
        
        # Filtro USB
        usb_ports = SerialUtils.filter_ports(ports, "USB")
        self.assertEqual(len(usb_ports), 1)
        self.assertEqual(usb_ports[0]["device"], "COM1")
        
        # Filtro Bluetooth
        bt_ports = SerialUtils.filter_ports(ports, "BLUETOOTH")
        self.assertEqual(len(bt_ports), 1)
        self.assertEqual(bt_ports[0]["device"], "COM2")
        
        # Filtro Virtual
        virtual_ports = SerialUtils.filter_ports(ports, "VIRTUAL")
        self.assertEqual(len(virtual_ports), 1)
        self.assertEqual(virtual_ports[0]["device"], "COM3")
        
        # Filtro FTDI
        ftdi_ports = SerialUtils.filter_ports(ports, "FTDI")
        self.assertEqual(len(ftdi_ports), 1)
        self.assertEqual(ftdi_ports[0]["device"], "COM1")
        
        # Sin filtro
        all_ports = SerialUtils.filter_ports(ports)
        self.assertEqual(len(all_ports), 3)

if __name__ == '__main__':
    unittest.main()