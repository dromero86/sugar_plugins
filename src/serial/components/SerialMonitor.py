"""
Monitor Serie.
==============

Sistema de monitoreo en tiempo real para puertos serie.
"""

import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from .SerialSession import SerialSession

class SerialMonitor:
    """Sistema de monitoreo para sesiones serie."""
    
    def __init__(self, session: SerialSession):
        """
        Inicializa el monitor.
        
        Args:
            session: Sesión serie a monitorear
        """
        self.session = session
        self.is_monitoring = False
        self.monitor_thread = None
        self.duration = None
        self.start_time = None
        self.log_file = None
        self.log_handler = None
        self.filter_pattern = None
        self.callbacks = {
            'on_data': [],
            'on_error': [],
            'on_start': [],
            'on_stop': []
        }
        self.data_buffer = []
        self.max_buffer_size = 1000
        self.lock = threading.Lock()
    
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
    
    def start_monitoring(self, duration: Optional[float] = None, 
                        log_file: Optional[str] = None,
                        filter_pattern: Optional[str] = None) -> bool:
        """
        Inicia el monitoreo.
        
        Args:
            duration: Duración del monitoreo en segundos
            log_file: Archivo para guardar logs
            filter_pattern: Patrón para filtrar datos
            
        Returns:
            True si el monitoreo se inició correctamente, False en caso contrario
        """
        if self.is_monitoring:
            return False
        
        self.duration = duration
        self.start_time = time.time()
        self.filter_pattern = filter_pattern
        
        # Configurar logging si se especifica archivo
        if log_file:
            self.log_file = Path(log_file)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Configurar logger
            logger = logging.getLogger(f"serial_monitor_{self.session.name}")
            logger.setLevel(logging.INFO)
            
            # Crear handler para archivo
            self.log_handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            self.log_handler.setFormatter(formatter)
            logger.addHandler(self.log_handler)
        
        # Iniciar thread de monitoreo
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self._trigger_callbacks('on_start')
        return True
    
    def stop_monitoring(self) -> bool:
        """
        Detiene el monitoreo.
        
        Returns:
            True si el monitoreo se detuvo correctamente, False en caso contrario
        """
        if not self.is_monitoring:
            return False
        
        self.is_monitoring = False
        
        # Esperar a que termine el thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        # Limpiar logging
        if self.log_handler:
            logger = logging.getLogger(f"serial_monitor_{self.session.name}")
            logger.removeHandler(self.log_handler)
            self.log_handler.close()
            self.log_handler = None
        
        self._trigger_callbacks('on_stop')
        return True
    
    def _monitor_loop(self):
        """Loop principal de monitoreo."""
        logger = None
        if self.log_file:
            logger = logging.getLogger(f"serial_monitor_{self.session.name}")
        
        try:
            while self.is_monitoring:
                # Verificar duración
                if self.duration and (time.time() - self.start_time) >= self.duration:
                    break
                
                # Leer datos disponibles
                if self.session.connection.is_connected:
                    try:
                        # Leer datos disponibles
                        in_waiting = self.session.connection.connection.in_waiting
                        if in_waiting > 0:
                            data = self.session.read(in_waiting)
                            if data:
                                # Aplicar filtro si existe
                                if self._should_log_data(data):
                                    self._process_data(data, logger)
                    except Exception as e:
                        self._trigger_callbacks('on_error', str(e))
                        if logger:
                            logger.error(f"Error en monitoreo: {e}")
                
                time.sleep(0.1)  # Pequeña pausa para no sobrecargar CPU
                
        except Exception as e:
            self._trigger_callbacks('on_error', str(e))
            if logger:
                logger.error(f"Error crítico en monitoreo: {e}")
        finally:
            self.is_monitoring = False
    
    def _should_log_data(self, data: str) -> bool:
        """
        Verifica si los datos deben ser registrados según el filtro.
        
        Args:
            data: Datos a verificar
            
        Returns:
            True si los datos deben ser registrados, False en caso contrario
        """
        if not self.filter_pattern:
            return True
        
        try:
            import re
            return bool(re.search(self.filter_pattern, data, re.IGNORECASE))
        except Exception:
            return True
    
    def _process_data(self, data: str, logger: Optional[logging.Logger]):
        """
        Procesa datos recibidos.
        
        Args:
            data: Datos recibidos
            logger: Logger para escribir logs
        """
        with self.lock:
            # Agregar a buffer
            self.data_buffer.append({
                'timestamp': time.time(),
                'data': data,
                'session': self.session.name
            })
            
            # Limitar tamaño del buffer
            if len(self.data_buffer) > self.max_buffer_size:
                self.data_buffer.pop(0)
        
        # Ejecutar callbacks
        self._trigger_callbacks('on_data', data)
        
        # Escribir a log si existe
        if logger:
            logger.info(f"Data: {data.strip()}")
    
    def get_buffer(self) -> List[Dict[str, Any]]:
        """
        Obtiene el buffer de datos.
        
        Returns:
            Lista de datos en el buffer
        """
        with self.lock:
            return self.data_buffer.copy()
    
    def clear_buffer(self):
        """Limpia el buffer de datos."""
        with self.lock:
            self.data_buffer.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado del monitor.
        
        Returns:
            Estado del monitor
        """
        with self.lock:
            return {
                "is_monitoring": self.is_monitoring,
                "duration": self.duration,
                "start_time": self.start_time,
                "elapsed_time": time.time() - self.start_time if self.start_time else 0,
                "log_file": str(self.log_file) if self.log_file else None,
                "filter_pattern": self.filter_pattern,
                "buffer_size": len(self.data_buffer),
                "max_buffer_size": self.max_buffer_size,
                "session_name": self.session.name
            }
    
    def cleanup(self):
        """Limpia recursos del monitor."""
        self.stop_monitoring()
        self.clear_buffer()
        self.callbacks.clear()