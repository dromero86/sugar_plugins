"""
Utilidades para el Plugin Serial.
================================

Utilidades para detección de plataforma, mapeo de puertos y validación.
"""

import platform
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

class SerialUtils:
    """Utilidades para el plugin serial."""
    
    @staticmethod
    def detect_platform() -> str:
        """Detecta el sistema operativo actual."""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
    
    @staticmethod
    def normalize_port_name(port: str) -> str:
        """Normaliza el nombre del puerto según la plataforma."""
        platform_type = SerialUtils.detect_platform()
        
        if platform_type == "windows":
            # Windows: COM1, COM2, etc.
            if not port.upper().startswith("COM"):
                if port.isdigit():
                    return f"COM{port}"
                else:
                    return f"COM{port}"
            return port.upper()
        
        elif platform_type == "linux":
            # Linux: /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0, etc.
            if not port.startswith("/dev/"):
                if port.startswith("tty"):
                    return f"/dev/{port}"
                else:
                    return f"/dev/tty{port}"
            return port
        
        elif platform_type == "macos":
            # macOS: /dev/cu.usbserial, /dev/cu.usbmodem, etc.
            if not port.startswith("/dev/"):
                if port.startswith("cu."):
                    return f"/dev/{port}"
                else:
                    return f"/dev/cu.{port}"
            return port
        
        return port
    
    @staticmethod
    def validate_baudrate(baudrate: int) -> bool:
        """Valida que la velocidad de baudios sea válida."""
        valid_baudrates = [
            50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
            9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
            576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
            3000000, 3500000, 4000000
        ]
        return baudrate in valid_baudrates
    
    @staticmethod
    def validate_parity(parity: str) -> bool:
        """Valida que la paridad sea válida."""
        valid_parities = ["NONE", "EVEN", "ODD", "MARK", "SPACE"]
        return parity.upper() in valid_parities
    
    @staticmethod
    def validate_stopbits(stopbits: int) -> bool:
        """Valida que los bits de parada sean válidos."""
        return stopbits in [1, 2]
    
    @staticmethod
    def validate_bytesize(bytesize: int) -> bool:
        """Valida que el tamaño de bytes sea válido."""
        return bytesize in [5, 6, 7, 8]
    
    @staticmethod
    def parse_encoding(encoding: str) -> str:
        """Parsea y valida la codificación."""
        valid_encodings = ["utf-8", "ascii", "latin1", "cp1252", "hex", "binary"]
        if encoding.lower() in valid_encodings:
            return encoding.lower()
        return "utf-8"  # Default
    
    @staticmethod
    def encode_data(data: str, encoding: str) -> bytes:
        """Codifica datos según la codificación especificada."""
        if encoding == "hex":
            # Remover espacios y convertir hex a bytes
            hex_data = data.replace(" ", "").replace("\\x", "")
            return bytes.fromhex(hex_data)
        elif encoding == "binary":
            # Convertir secuencias de escape a bytes
            return data.encode('latin1').decode('unicode_escape').encode('latin1')
        else:
            return data.encode(encoding)
    
    @staticmethod
    def decode_data(data: bytes, encoding: str) -> str:
        """Decodifica datos según la codificación especificada."""
        if encoding == "hex":
            return data.hex().upper()
        elif encoding == "binary":
            return data.decode('latin1')
        else:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                return data.decode('utf-8', errors='replace')
    
    @staticmethod
    def parse_eol(eol: str) -> bytes:
        """Parsea caracteres de fin de línea."""
        eol_mapping = {
            "\\n": b"\n",
            "\\r": b"\r", 
            "\\r\\n": b"\r\n",
            "\\0": b"\0",
            "": b""
        }
        return eol_mapping.get(eol, eol.encode('unicode_escape'))
    
    @staticmethod
    def get_port_info(port: str) -> Dict[str, Any]:
        """Obtiene información detallada de un puerto."""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            for port_info in ports:
                if port_info.device == port:
                    return {
                        "device": port_info.device,
                        "description": port_info.description,
                        "hwid": port_info.hwid,
                        "vid": port_info.vid,
                        "pid": port_info.pid,
                        "serial_number": port_info.serial_number,
                        "manufacturer": port_info.manufacturer,
                        "product": port_info.product,
                        "interface": port_info.interface
                    }
        except ImportError:
            pass
        
        return {
            "device": port,
            "description": "Unknown device",
            "hwid": "Unknown",
            "vid": None,
            "pid": None,
            "serial_number": None,
            "manufacturer": None,
            "product": None,
            "interface": None
        }
    
    @staticmethod
    def list_available_ports() -> List[Dict[str, Any]]:
        """Lista todos los puertos serie disponibles."""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            port_list = []
            for port_info in ports:
                port_list.append({
                    "device": port_info.device,
                    "description": port_info.description,
                    "hwid": port_info.hwid,
                    "vid": port_info.vid,
                    "pid": port_info.pid,
                    "serial_number": port_info.serial_number,
                    "manufacturer": port_info.manufacturer,
                    "product": port_info.product,
                    "interface": port_info.interface
                })
            
            return port_list
        except ImportError:
            return []
    
    @staticmethod
    def filter_ports(ports: List[Dict[str, Any]], filter_type: str = None) -> List[Dict[str, Any]]:
        """Filtra puertos por tipo."""
        if not filter_type:
            return ports
        
        filter_type = filter_type.upper()
        filtered_ports = []
        
        for port in ports:
            description = port.get("description", "").upper()
            manufacturer = port.get("manufacturer", "").upper()
            product = port.get("product", "").upper()
            
            if filter_type == "USB":
                if any(keyword in description for keyword in ["USB", "SERIAL"]):
                    filtered_ports.append(port)
            elif filter_type == "BLUETOOTH":
                if any(keyword in description for keyword in ["BLUETOOTH", "BT"]):
                    filtered_ports.append(port)
            elif filter_type == "VIRTUAL":
                if any(keyword in description for keyword in ["VIRTUAL", "VCP"]):
                    filtered_ports.append(port)
            elif filter_type == "FTDI":
                if "FTDI" in manufacturer or "FTDI" in product:
                    filtered_ports.append(port)
            elif filter_type == "PROLIFIC":
                if "PROLIFIC" in manufacturer or "PROLIFIC" in product:
                    filtered_ports.append(port)
        
        return filtered_ports