"""
Conexión Serie.
==============

Manejo de conexiones serie individuales con pyserial.
"""

import serial
import threading
import time
from typing import Dict, Any, Optional, List
from .SerialUtils import SerialUtils

class SerialConnection:
    """Maneja una conexión serie individual."""
    
    def __init__(self, port: str, **kwargs):
        """
        Inicializa una conexión serie.
        
        Args:
            port: Puerto serie
            **kwargs: Parámetros de configuración
        """
        self.port = SerialUtils.normalize_port_name(port)
        self.connection = None
        self.is_connected = False
        self.config = {
            'baudrate': kwargs.get('baudrate', 9600),
            'timeout': kwargs.get('timeout', 1.0),
            'parity': kwargs.get('parity', 'NONE'),
            'stopbits': kwargs.get('stopbits', 1),
            'bytesize': kwargs.get('bytesize', 8),
            'xonxoff': kwargs.get('xonxoff', False),
            'rtscts': kwargs.get('rtscts', False),
            'dsrdtr': kwargs.get('dsrdtr', False)
        }
        self.lock = threading.Lock()
        self.last_error = None
    
    def connect(self) -> bool:
        """
        Establece la conexión serie.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if self.is_connected:
                    return True
                
                # Validar parámetros
                if not SerialUtils.validate_baudrate(self.config['baudrate']):
                    raise ValueError(f"Velocidad de baudios inválida: {self.config['baudrate']}")
                
                if not SerialUtils.validate_parity(self.config['parity']):
                    raise ValueError(f"Paridad inválida: {self.config['parity']}")
                
                if not SerialUtils.validate_stopbits(self.config['stopbits']):
                    raise ValueError(f"Bits de parada inválidos: {self.config['stopbits']}")
                
                if not SerialUtils.validate_bytesize(self.config['bytesize']):
                    raise ValueError(f"Tamaño de bytes inválido: {self.config['bytesize']}")
                
                # Crear conexión
                self.connection = serial.Serial(
                    port=self.port,
                    baudrate=self.config['baudrate'],
                    timeout=self.config['timeout'],
                    parity=self.config['parity'],
                    stopbits=self.config['stopbits'],
                    bytesize=self.config['bytesize'],
                    xonxoff=self.config['xonxoff'],
                    rtscts=self.config['rtscts'],
                    dsrdtr=self.config['dsrdtr']
                )
                
                self.is_connected = True
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Cierra la conexión serie.
        
        Returns:
            True si la desconexión fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    return True
                
                self.connection.close()
                self.connection = None
                self.is_connected = False
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def write(self, data: str, encoding: str = "utf-8") -> bool:
        """
        Envía datos al puerto serie.
        
        Args:
            data: Datos a enviar
            encoding: Codificación de los datos
            
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                encoded_data = SerialUtils.encode_data(data, encoding)
                bytes_written = self.connection.write(encoded_data)
                self.connection.flush()
                
                self.last_error = None
                return bytes_written > 0
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def read(self, size: int = 1, timeout: Optional[float] = None) -> str:
        """
        Lee datos del puerto serie.
        
        Args:
            size: Número de bytes a leer
            timeout: Timeout específico para esta lectura
            
        Returns:
            Datos leídos como string
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                # Configurar timeout temporal si se especifica
                original_timeout = self.connection.timeout
                if timeout is not None:
                    self.connection.timeout = timeout
                
                try:
                    data = self.connection.read(size)
                    return data.decode('utf-8', errors='replace')
                finally:
                    # Restaurar timeout original
                    self.connection.timeout = original_timeout
                
        except Exception as e:
            self.last_error = str(e)
            return ""
    
    def read_line(self, eol: str = "\\n", timeout: Optional[float] = None) -> str:
        """
        Lee una línea completa del puerto serie.
        
        Args:
            eol: Caracteres de fin de línea
            timeout: Timeout específico para esta lectura
            
        Returns:
            Línea leída
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                # Configurar timeout temporal si se especifica
                original_timeout = self.connection.timeout
                if timeout is not None:
                    self.connection.timeout = timeout
                
                try:
                    eol_bytes = SerialUtils.parse_eol(eol)
                    line = self.connection.readline()
                    return line.decode('utf-8', errors='replace').rstrip()
                finally:
                    # Restaurar timeout original
                    self.connection.timeout = original_timeout
                
        except Exception as e:
            self.last_error = str(e)
            return ""
    
    def read_until(self, terminator: str, timeout: Optional[float] = None) -> str:
        """
        Lee datos hasta encontrar un terminador.
        
        Args:
            terminator: Terminador a buscar
            timeout: Timeout específico para esta lectura
            
        Returns:
            Datos leídos hasta el terminador
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                # Configurar timeout temporal si se especifica
                original_timeout = self.connection.timeout
                if timeout is not None:
                    self.connection.timeout = timeout
                
                try:
                    terminator_bytes = terminator.encode('utf-8')
                    data = self.connection.read_until(terminator_bytes)
                    return data.decode('utf-8', errors='replace')
                finally:
                    # Restaurar timeout original
                    self.connection.timeout = original_timeout
                
        except Exception as e:
            self.last_error = str(e)
            return ""
    
    def read_bytes(self, size: int, timeout: Optional[float] = None) -> bytes:
        """
        Lee un número específico de bytes.
        
        Args:
            size: Número de bytes a leer
            timeout: Timeout específico para esta lectura
            
        Returns:
            Bytes leídos
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                # Configurar timeout temporal si se especifica
                original_timeout = self.connection.timeout
                if timeout is not None:
                    self.connection.timeout = timeout
                
                try:
                    return self.connection.read(size)
                finally:
                    # Restaurar timeout original
                    self.connection.timeout = original_timeout
                
        except Exception as e:
            self.last_error = str(e)
            return b""
    
    def flush(self) -> bool:
        """
        Limpia los buffers de entrada y salida.
        
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                self.connection.flushInput()
                self.connection.flushOutput()
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def configure(self, **kwargs) -> bool:
        """
        Configura parámetros del puerto serie.
        
        Args:
            **kwargs: Parámetros a configurar
            
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                # Actualizar configuración
                for key, value in kwargs.items():
                    if key in self.config:
                        self.config[key] = value
                
                # Aplicar configuración
                if 'baudrate' in kwargs:
                    self.connection.baudrate = kwargs['baudrate']
                if 'parity' in kwargs:
                    self.connection.parity = kwargs['parity']
                if 'stopbits' in kwargs:
                    self.connection.stopbits = kwargs['stopbits']
                if 'bytesize' in kwargs:
                    self.connection.bytesize = kwargs['bytesize']
                if 'timeout' in kwargs:
                    self.connection.timeout = kwargs['timeout']
                if 'xonxoff' in kwargs:
                    self.connection.xonxoff = kwargs['xonxoff']
                if 'rtscts' in kwargs:
                    self.connection.rtscts = kwargs['rtscts']
                if 'dsrdtr' in kwargs:
                    self.connection.dsrdtr = kwargs['dsrdtr']
                
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def set_dtr(self, state: bool) -> bool:
        """
        Controla la línea DTR.
        
        Args:
            state: Estado de DTR (True/False)
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                self.connection.dtr = state
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def set_rts(self, state: bool) -> bool:
        """
        Controla la línea RTS.
        
        Args:
            state: Estado de RTS (True/False)
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                self.connection.rts = state
                self.last_error = None
                return True
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_cts(self) -> bool:
        """
        Lee el estado de la línea CTS.
        
        Returns:
            Estado de CTS
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                return self.connection.cts
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_dsr(self) -> bool:
        """
        Lee el estado de la línea DSR.
        
        Returns:
            Estado de DSR
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                return self.connection.dsr
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_ri(self) -> bool:
        """
        Lee el estado de la línea RI.
        
        Returns:
            Estado de RI
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                return self.connection.ri
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_cd(self) -> bool:
        """
        Lee el estado de la línea CD.
        
        Returns:
            Estado de CD
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    raise RuntimeError("Conexión no establecida")
                
                return self.connection.cd
                
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual de la conexión.
        
        Returns:
            Diccionario con el estado de la conexión
        """
        try:
            with self.lock:
                if not self.is_connected or not self.connection:
                    return {
                        "connected": False,
                        "port": self.port,
                        "error": self.last_error
                    }
                
                return {
                    "connected": True,
                    "port": self.port,
                    "baudrate": self.connection.baudrate,
                    "timeout": self.connection.timeout,
                    "parity": self.connection.parity,
                    "stopbits": self.connection.stopbits,
                    "bytesize": self.connection.bytesize,
                    "xonxoff": self.connection.xonxoff,
                    "rtscts": self.connection.rtscts,
                    "dsrdtr": self.connection.dsrdtr,
                    "cts": self.connection.cts,
                    "dsr": self.connection.dsr,
                    "ri": self.connection.ri,
                    "cd": self.connection.cd,
                    "dtr": self.connection.dtr,
                    "rts": self.connection.rts,
                    "in_waiting": self.connection.in_waiting,
                    "out_waiting": self.connection.out_waiting,
                    "error": self.last_error
                }
                
        except Exception as e:
            return {
                "connected": False,
                "port": self.port,
                "error": str(e)
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada del puerto.
        
        Returns:
            Diccionario con información del puerto
        """
        port_info = SerialUtils.get_port_info(self.port)
        port_info.update({
            "connected": self.is_connected,
            "config": self.config.copy(),
            "last_error": self.last_error
        })
        return port_info