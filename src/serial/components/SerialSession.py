"""
Sesión Serie.
============

Manejo de sesiones serie con nombres y configuración persistente.
"""

import threading
import time
from typing import Dict, Any, Optional, Callable
from .SerialConnection import SerialConnection

class SerialSession:
    """Maneja una sesión serie con nombre y configuración."""
    
    def __init__(self, name: str, port: str, **kwargs):
        """
        Inicializa una sesión serie.
        
        Args:
            name: Nombre de la sesión
            port: Puerto serie
            **kwargs: Parámetros de configuración
        """
        self.name = name
        self.connection = SerialConnection(port, **kwargs)
        self.auto_reconnect = kwargs.get('auto_reconnect', False)
        self.reconnect_attempts = kwargs.get('reconnect_attempts', 3)
        self.reconnect_delay = kwargs.get('reconnect_delay', 1.0)
        self.created_at = time.time()
        self.last_activity = time.time()
        self.activity_count = 0
        self.lock = threading.Lock()
        self.callbacks = {
            'on_connect': [],
            'on_disconnect': [],
            'on_error': [],
            'on_data_received': [],
            'on_data_sent': []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """
        Agrega un callback para un evento.
        
        Args:
            event: Tipo de evento
            callback: Función callback
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def remove_callback(self, event: str, callback: Callable):
        """
        Remueve un callback para un evento.
        
        Args:
            event: Tipo de evento
            callback: Función callback
        """
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
    
    def _trigger_callbacks(self, event: str, *args, **kwargs):
        """Ejecuta callbacks para un evento."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(self, *args, **kwargs)
                except Exception as e:
                    print(f"Error en callback {event}: {e}")
    
    def connect(self) -> bool:
        """
        Establece la conexión de la sesión.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        with self.lock:
            success = self.connection.connect()
            if success:
                self._trigger_callbacks('on_connect')
            else:
                self._trigger_callbacks('on_error', self.connection.last_error)
            return success
    
    def disconnect(self) -> bool:
        """
        Cierra la conexión de la sesión.
        
        Returns:
            True si la desconexión fue exitosa, False en caso contrario
        """
        with self.lock:
            success = self.connection.disconnect()
            if success:
                self._trigger_callbacks('on_disconnect')
            return success
    
    def write(self, data: str, encoding: str = "utf-8") -> bool:
        """
        Envía datos a través de la sesión.
        
        Args:
            data: Datos a enviar
            encoding: Codificación de los datos
            
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        with self.lock:
            if not self.connection.is_connected and self.auto_reconnect:
                if not self._reconnect():
                    return False
            
            success = self.connection.write(data, encoding)
            if success:
                self.last_activity = time.time()
                self.activity_count += 1
                self._trigger_callbacks('on_data_sent', data)
            else:
                self._trigger_callbacks('on_error', self.connection.last_error)
            return success
    
    def read(self, size: int = 1, timeout: Optional[float] = None) -> str:
        """
        Lee datos de la sesión.
        
        Args:
            size: Número de bytes a leer
            timeout: Timeout específico para esta lectura
            
        Returns:
            Datos leídos
        """
        with self.lock:
            if not self.connection.is_connected and self.auto_reconnect:
                if not self._reconnect():
                    return ""
            
            data = self.connection.read(size, timeout)
            if data:
                self.last_activity = time.time()
                self.activity_count += 1
                self._trigger_callbacks('on_data_received', data)
            return data
    
    def read_line(self, eol: str = "\\n", timeout: Optional[float] = None) -> str:
        """
        Lee una línea de la sesión.
        
        Args:
            eol: Caracteres de fin de línea
            timeout: Timeout específico para esta lectura
            
        Returns:
            Línea leída
        """
        with self.lock:
            if not self.connection.is_connected and self.auto_reconnect:
                if not self._reconnect():
                    return ""
            
            line = self.connection.read_line(eol, timeout)
            if line:
                self.last_activity = time.time()
                self.activity_count += 1
                self._trigger_callbacks('on_data_received', line)
            return line
    
    def read_until(self, terminator: str, timeout: Optional[float] = None) -> str:
        """
        Lee datos hasta encontrar un terminador.
        
        Args:
            terminator: Terminador a buscar
            timeout: Timeout específico para esta lectura
            
        Returns:
            Datos leídos hasta el terminador
        """
        with self.lock:
            if not self.connection.is_connected and self.auto_reconnect:
                if not self._reconnect():
                    return ""
            
            data = self.connection.read_until(terminator, timeout)
            if data:
                self.last_activity = time.time()
                self.activity_count += 1
                self._trigger_callbacks('on_data_received', data)
            return data
    
    def read_bytes(self, size: int, timeout: Optional[float] = None) -> bytes:
        """
        Lee bytes de la sesión.
        
        Args:
            size: Número de bytes a leer
            timeout: Timeout específico para esta lectura
            
        Returns:
            Bytes leídos
        """
        with self.lock:
            if not self.connection.is_connected and self.auto_reconnect:
                if not self._reconnect():
                    return b""
            
            data = self.connection.read_bytes(size, timeout)
            if data:
                self.last_activity = time.time()
                self.activity_count += 1
                self._trigger_callbacks('on_data_received', data)
            return data
    
    def flush(self) -> bool:
        """
        Limpia los buffers de la sesión.
        
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        with self.lock:
            return self.connection.flush()
    
    def configure(self, **kwargs) -> bool:
        """
        Configura la sesión.
        
        Args:
            **kwargs: Parámetros a configurar
            
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        with self.lock:
            return self.connection.configure(**kwargs)
    
    def set_dtr(self, state: bool) -> bool:
        """
        Controla DTR de la sesión.
        
        Args:
            state: Estado de DTR
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        with self.lock:
            return self.connection.set_dtr(state)
    
    def set_rts(self, state: bool) -> bool:
        """
        Controla RTS de la sesión.
        
        Args:
            state: Estado de RTS
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        with self.lock:
            return self.connection.set_rts(state)
    
    def get_cts(self) -> bool:
        """
        Lee CTS de la sesión.
        
        Returns:
            Estado de CTS
        """
        with self.lock:
            return self.connection.get_cts()
    
    def get_dsr(self) -> bool:
        """
        Lee DSR de la sesión.
        
        Returns:
            Estado de DSR
        """
        with self.lock:
            return self.connection.get_dsr()
    
    def get_ri(self) -> bool:
        """
        Lee RI de la sesión.
        
        Returns:
            Estado de RI
        """
        with self.lock:
            return self.connection.get_ri()
    
    def get_cd(self) -> bool:
        """
        Lee CD de la sesión.
        
        Returns:
            Estado de CD
        """
        with self.lock:
            return self.connection.get_cd()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la sesión.
        
        Returns:
            Estado de la sesión
        """
        with self.lock:
            status = self.connection.get_status()
            status.update({
                "name": self.name,
                "created_at": self.created_at,
                "last_activity": self.last_activity,
                "activity_count": self.activity_count,
                "auto_reconnect": self.auto_reconnect,
                "reconnect_attempts": self.reconnect_attempts,
                "reconnect_delay": self.reconnect_delay
            })
            return status
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la sesión.
        
        Returns:
            Información de la sesión
        """
        with self.lock:
            info = self.connection.get_info()
            info.update({
                "name": self.name,
                "created_at": self.created_at,
                "last_activity": self.last_activity,
                "activity_count": self.activity_count,
                "auto_reconnect": self.auto_reconnect,
                "reconnect_attempts": self.reconnect_attempts,
                "reconnect_delay": self.reconnect_delay,
                "callbacks": {event: len(callbacks) for event, callbacks in self.callbacks.items()}
            })
            return info
    
    def _reconnect(self) -> bool:
        """
        Intenta reconectar la sesión.
        
        Returns:
            True si la reconexión fue exitosa, False en caso contrario
        """
        for attempt in range(self.reconnect_attempts):
            try:
                if self.connection.connect():
                    self._trigger_callbacks('on_connect')
                    return True
                time.sleep(self.reconnect_delay)
            except Exception as e:
                self._trigger_callbacks('on_error', str(e))
                time.sleep(self.reconnect_delay)
        
        return False
    
    def is_connected(self) -> bool:
        """
        Verifica si la sesión está conectada.
        
        Returns:
            True si está conectada, False en caso contrario
        """
        with self.lock:
            return self.connection.is_connected
    
    def cleanup(self):
        """Limpia recursos de la sesión."""
        with self.lock:
            self.disconnect()
            self.callbacks.clear()