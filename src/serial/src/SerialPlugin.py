"""
Plugin Serial Principal.
========================

Plugin de comunicación serie universal para Sugar con soporte completo
para Windows COM, Linux TTY y macOS cu.*, incluyendo todos los casos
de uso de comunicación serie.
"""

import time
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

from ..components.SerialConnection import SerialConnection
from ..components.SerialSession import SerialSession
from ..components.SerialMonitor import SerialMonitor
from ..components.SerialUtils import SerialUtils

class SerialPlugin(PluginBase):
    """
    Plugin de comunicación serie universal para Sugar.
    
    Proporciona funcionalidad completa para comunicación serie incluyendo:
    - Conexión y desconexión de puertos serie
    - Lectura y escritura de datos
    - Configuración de parámetros serie
    - Control de líneas de control
    - Monitoreo en tiempo real
    - Sistema de sesiones con nombres
    - Integración con sistema meta de Sugar
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin de comunicación serie universal para Sugar con soporte multiplataforma"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["serial", "serial.tools"]
    REQUIREMENTS = ["pyserial>=3.5"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el plugin serial.
        
        Args:
            context: Contexto de Sugar
            plugin_config: Configuración del plugin
        """
        super().__init__(context, plugin_config)
        
        # Inicializar componentes
        self.sessions: Dict[str, SerialSession] = {}
        self.monitors: Dict[str, SerialMonitor] = {}
        self.meta_config = {}
        self.preconfigured_sessions = {}
        self.lock = threading.Lock()
        
        # Verificar dependencias
        self.dependency_status = self._check_all_dependencies()
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Output.Console(self.plugin_name, "Plugin Serial inicializado")
    
    def get_available_commands(self) -> List[str]:
        """Retorna lista de comandos disponibles."""
        return [
            # Comandos de conexión
            "connect", "disconnect", "list_ports", "test_connection",
            # Comandos de comunicación
            "write", "read", "read_line", "read_until", "read_bytes", "flush",
            # Comandos de configuración
            "configure", "get_config", "set_timeout", "set_baudrate", 
            "set_parity", "set_stopbits", "set_bytesize",
            # Comandos de control de líneas
            "set_dtr", "set_rts", "get_cts", "get_dsr", "get_ri", "get_cd",
            # Comandos de monitoreo
            "get_status", "get_info", "monitor", "log_activity"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Ejecuta un comando del plugin.
        
        Args:
            operator: Comando a ejecutar
            config: Configuración del comando
            
        Returns:
            Resultado del comando
        """
        try:
            # Comandos de conexión
            if operator == "connect":
                return self._connect(config)
            elif operator == "disconnect":
                return self._disconnect(config)
            elif operator == "list_ports":
                return self._list_ports(config)
            elif operator == "test_connection":
                return self._test_connection(config)
            
            # Comandos de comunicación
            elif operator == "write":
                return self._write(config)
            elif operator == "read":
                return self._read(config)
            elif operator == "read_line":
                return self._read_line(config)
            elif operator == "read_until":
                return self._read_until(config)
            elif operator == "read_bytes":
                return self._read_bytes(config)
            elif operator == "flush":
                return self._flush(config)
            
            # Comandos de configuración
            elif operator == "configure":
                return self._configure(config)
            elif operator == "get_config":
                return self._get_config(config)
            elif operator == "set_timeout":
                return self._set_timeout(config)
            elif operator == "set_baudrate":
                return self._set_baudrate(config)
            elif operator == "set_parity":
                return self._set_parity(config)
            elif operator == "set_stopbits":
                return self._set_stopbits(config)
            elif operator == "set_bytesize":
                return self._set_bytesize(config)
            
            # Comandos de control de líneas
            elif operator == "set_dtr":
                return self._set_dtr(config)
            elif operator == "set_rts":
                return self._set_rts(config)
            elif operator == "get_cts":
                return self._get_cts(config)
            elif operator == "get_dsr":
                return self._get_dsr(config)
            elif operator == "get_ri":
                return self._get_ri(config)
            elif operator == "get_cd":
                return self._get_cd(config)
            
            # Comandos de monitoreo
            elif operator == "get_status":
                return self._get_status(config)
            elif operator == "get_info":
                return self._get_info(config)
            elif operator == "monitor":
                return self._monitor(config)
            elif operator == "log_activity":
                return self._log_activity(config)
            
            else:
                raise ValueError(f"Comando desconocido: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error ejecutando comando '{operator}': {str(e)}")
            raise
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook para configuración del plugin serial.
        Configura sesiones predefinidas antes de la ejecución.
        
        Args:
            config: Configuración desde la sección meta
            
        Returns:
            Resultado de la configuración
        """
        try:
            Output.Console(self.plugin_name, f"Procesando meta hook: {config}")
            
            # Almacenar configuración meta
            self.meta_config = config
            
            # Procesar opciones
            options = config.get("options", {})
            
            # Procesar sesiones preconfiguradas
            for session_name, session_config in options.items():
                if isinstance(session_config, dict):
                    self.preconfigured_sessions[session_name] = session_config
                    Output.Console(self.plugin_name, f"Sesión preconfigurada: {session_name}")
                    
                    # Auto-conectar si está habilitado
                    if session_config.get("auto_connect", False):
                        try:
                            self._auto_connect_session(session_name, session_config)
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-conexión falló para {session_name}: {str(e)}")
            
            return {
                "success": True,
                "sessions_configured": len(options),
                "auto_connected": len([s for s in options.values() if s.get("auto_connect", False)])
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error en meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Métodos de conexión
    def _connect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece conexión serie."""
        port = config.get("port")
        if not port:
            raise ValueError("Parámetro 'port' es requerido")
        
        session_name = config.get("session", f"session_{port}")
        
        # Parámetros de configuración
        connection_config = {
            'baudrate': config.get('baudrate', 9600),
            'timeout': config.get('timeout', 1.0),
            'parity': config.get('parity', 'NONE'),
            'stopbits': config.get('stopbits', 1),
            'bytesize': config.get('bytesize', 8),
            'xonxoff': config.get('xonxoff', False),
            'rtscts': config.get('rtscts', False),
            'dsrdtr': config.get('dsrdtr', False),
            'auto_reconnect': config.get('auto_reconnect', False),
            'reconnect_attempts': config.get('reconnect_attempts', 3),
            'reconnect_delay': config.get('reconnect_delay', 1.0)
        }
        
        with self.lock:
            # Crear o reutilizar sesión
            if session_name in self.sessions:
                session = self.sessions[session_name]
                if session.is_connected():
                    return {"success": True, "message": f"Sesión '{session_name}' ya está conectada"}
            else:
                session = SerialSession(session_name, port, **connection_config)
                self.sessions[session_name] = session
            
            # Conectar
            success = session.connect()
            if success:
                result = {"success": True, "message": f"Conectado a {port}", "session": session_name}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _disconnect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Cierra conexión serie."""
        session_name = config.get("session")
        force = config.get("force", False)
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            success = session.disconnect()
            
            if success or force:
                if force:
                    session.cleanup()
                    del self.sessions[session_name]
                result = {"success": True, "message": f"Sesión '{session_name}' desconectada"}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _list_ports(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lista puertos serie disponibles."""
        include_info = config.get("include_info", True)
        filter_type = config.get("filter")
        
        ports = SerialUtils.list_available_ports()
        
        if filter_type:
            ports = SerialUtils.filter_ports(ports, filter_type)
        
        if not include_info:
            ports = [{"device": port["device"]} for port in ports]
        
        result = {
            "success": True,
            "ports": ports,
            "count": len(ports),
            "platform": SerialUtils.detect_platform()
        }
        
        # Guardar resultado en variable si se especifica
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba conectividad a un puerto."""
        port = config.get("port")
        if not port:
            raise ValueError("Parámetro 'port' es requerido")
        
        # Parámetros de prueba
        test_config = {
            'baudrate': config.get('baudrate', 9600),
            'timeout': config.get('timeout', 2.0),
            'parity': config.get('parity', 'NONE'),
            'stopbits': config.get('stopbits', 1),
            'bytesize': config.get('bytesize', 8)
        }
        
        # Crear conexión temporal
        connection = SerialConnection(port, **test_config)
        success = connection.connect()
        
        if success:
            connection.disconnect()
            result = {"success": True, "message": f"Puerto {port} accesible"}
        else:
            result = {"success": False, "error": connection.last_error}
        
        # Guardar resultado en variable si se especifica
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Métodos de comunicación
    def _write(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Envía datos al puerto serie."""
        session_name = config.get("session")
        data = config.get("data")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        if not data:
            raise ValueError("Parámetro 'data' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            encoding = config.get("encoding", "utf-8")
            add_newline = config.get("add_newline", False)
            
            if add_newline:
                data += "\\n"
            
            success = session.write(data, encoding)
            
            if success:
                result = {"success": True, "message": f"Datos enviados a {session_name}", "bytes_sent": len(data)}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _read(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee datos del puerto serie."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            size = config.get("size", 1)
            timeout = config.get("timeout")
            encoding = config.get("encoding", "utf-8")
            strip_whitespace = config.get("strip_whitespace", False)
            
            data = session.read(size, timeout)
            
            if strip_whitespace:
                data = data.strip()
            
            result = {
                "success": True,
                "data": data,
                "bytes_read": len(data),
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _read_line(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee una línea del puerto serie."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            eol = config.get("eol", "\\n")
            timeout = config.get("timeout")
            encoding = config.get("encoding", "utf-8")
            
            line = session.read_line(eol, timeout)
            
            result = {
                "success": True,
                "line": line,
                "bytes_read": len(line),
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _read_until(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee datos hasta encontrar un terminador."""
        session_name = config.get("session")
        terminator = config.get("terminator")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        if not terminator:
            raise ValueError("Parámetro 'terminator' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            timeout = config.get("timeout")
            encoding = config.get("encoding", "utf-8")
            
            data = session.read_until(terminator, timeout)
            
            result = {
                "success": True,
                "data": data,
                "bytes_read": len(data),
                "terminator": terminator,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _read_bytes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee bytes del puerto serie."""
        session_name = config.get("session")
        size = config.get("size")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        if not size:
            raise ValueError("Parámetro 'size' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            timeout = config.get("timeout")
            encoding = config.get("encoding", "hex")
            
            data_bytes = session.read_bytes(size, timeout)
            data_str = SerialUtils.decode_data(data_bytes, encoding)
            
            result = {
                "success": True,
                "data": data_str,
                "data_bytes": data_bytes.hex().upper(),
                "bytes_read": len(data_bytes),
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _flush(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia buffers del puerto serie."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            success = session.flush()
            
            if success:
                result = {"success": True, "message": f"Buffers limpiados en {session_name}"}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    # Métodos de configuración
    def _configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura parámetros del puerto serie."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            
            # Parámetros de configuración
            config_params = {}
            if "baudrate" in config:
                config_params["baudrate"] = config["baudrate"]
            if "parity" in config:
                config_params["parity"] = config["parity"]
            if "stopbits" in config:
                config_params["stopbits"] = config["stopbits"]
            if "bytesize" in config:
                config_params["bytesize"] = config["bytesize"]
            if "timeout" in config:
                config_params["timeout"] = config["timeout"]
            if "xonxoff" in config:
                config_params["xonxoff"] = config["xonxoff"]
            if "rtscts" in config:
                config_params["rtscts"] = config["rtscts"]
            if "dsrdtr" in config:
                config_params["dsrdtr"] = config["dsrdtr"]
            
            success = session.configure(**config_params)
            
            if success:
                result = {"success": True, "message": f"Sesión '{session_name}' configurada", "config": config_params}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene configuración actual del puerto serie."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            status = session.get_status()
            
            result = {
                "success": True,
                "config": {
                    "baudrate": status.get("baudrate"),
                    "timeout": status.get("timeout"),
                    "parity": status.get("parity"),
                    "stopbits": status.get("stopbits"),
                    "bytesize": status.get("bytesize"),
                    "xonxoff": status.get("xonxoff"),
                    "rtscts": status.get("rtscts"),
                    "dsrdtr": status.get("dsrdtr")
                },
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _set_timeout(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece timeout del puerto serie."""
        return self._configure({"session": config.get("session"), "timeout": config.get("timeout")})
    
    def _set_baudrate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece velocidad de baudios del puerto serie."""
        return self._configure({"session": config.get("session"), "baudrate": config.get("baudrate")})
    
    def _set_parity(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece paridad del puerto serie."""
        return self._configure({"session": config.get("session"), "parity": config.get("parity")})
    
    def _set_stopbits(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece bits de parada del puerto serie."""
        return self._configure({"session": config.get("session"), "stopbits": config.get("stopbits")})
    
    def _set_bytesize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece tamaño de bytes del puerto serie."""
        return self._configure({"session": config.get("session"), "bytesize": config.get("bytesize")})
    
    # Métodos de control de líneas
    def _set_dtr(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Controla línea DTR."""
        session_name = config.get("session")
        state = config.get("state")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        if state is None:
            raise ValueError("Parámetro 'state' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            success = session.set_dtr(state)
            
            if success:
                result = {"success": True, "message": f"DTR {'activado' if state else 'desactivado'} en {session_name}"}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _set_rts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Controla línea RTS."""
        session_name = config.get("session")
        state = config.get("state")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        if state is None:
            raise ValueError("Parámetro 'state' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            success = session.set_rts(state)
            
            if success:
                result = {"success": True, "message": f"RTS {'activado' if state else 'desactivado'} en {session_name}"}
            else:
                result = {"success": False, "error": session.connection.last_error}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_cts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee estado de línea CTS."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            cts_state = session.get_cts()
            
            result = {
                "success": True,
                "cts": cts_state,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_dsr(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee estado de línea DSR."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            dsr_state = session.get_dsr()
            
            result = {
                "success": True,
                "dsr": dsr_state,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_ri(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee estado de línea RI."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            ri_state = session.get_ri()
            
            result = {
                "success": True,
                "ri": ri_state,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_cd(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee estado de línea CD."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            cd_state = session.get_cd()
            
            result = {
                "success": True,
                "cd": cd_state,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    # Métodos de monitoreo
    def _get_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene estado de sesión o todas las sesiones."""
        session_name = config.get("session")
        
        with self.lock:
            if session_name:
                # Estado de sesión específica
                if session_name not in self.sessions:
                    return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
                
                status = self.sessions[session_name].get_status()
                result = {"success": True, "status": status}
            else:
                # Estado de todas las sesiones
                all_status = {}
                for name, session in self.sessions.items():
                    all_status[name] = session.get_status()
                
                result = {
                    "success": True,
                    "sessions": all_status,
                    "total_sessions": len(self.sessions),
                    "active_sessions": len([s for s in self.sessions.values() if s.is_connected()])
                }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _get_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información detallada de sesión o todas las sesiones."""
        session_name = config.get("session")
        
        with self.lock:
            if session_name:
                # Información de sesión específica
                if session_name not in self.sessions:
                    return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
                
                info = self.sessions[session_name].get_info()
                result = {"success": True, "info": info}
            else:
                # Información de todas las sesiones
                all_info = {}
                for name, session in self.sessions.items():
                    all_info[name] = session.get_info()
                
                result = {
                    "success": True,
                    "sessions": all_info,
                    "total_sessions": len(self.sessions),
                    "platform": SerialUtils.detect_platform()
                }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _monitor(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia monitoreo de sesión."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.sessions:
                return {"success": False, "error": f"Sesión '{session_name}' no encontrada"}
            
            session = self.sessions[session_name]
            
            # Crear o reutilizar monitor
            if session_name in self.monitors:
                monitor = self.monitors[session_name]
                if monitor.is_monitoring:
                    return {"success": False, "error": f"Monitor ya activo para {session_name}"}
            else:
                monitor = SerialMonitor(session)
                self.monitors[session_name] = monitor
            
            # Configurar monitor
            duration = config.get("duration")
            log_file = config.get("log_file")
            filter_pattern = config.get("filter")
            
            success = monitor.start_monitoring(duration, log_file, filter_pattern)
            
            if success:
                result = {"success": True, "message": f"Monitor iniciado para {session_name}"}
            else:
                result = {"success": False, "error": "No se pudo iniciar el monitor"}
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _log_activity(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene logs de actividad de monitor."""
        session_name = config.get("session")
        
        if not session_name:
            raise ValueError("Parámetro 'session' es requerido")
        
        with self.lock:
            if session_name not in self.monitors:
                return {"success": False, "error": f"Monitor no encontrado para {session_name}"}
            
            monitor = self.monitors[session_name]
            buffer_data = monitor.get_buffer()
            status = monitor.get_status()
            
            result = {
                "success": True,
                "buffer": buffer_data,
                "buffer_size": len(buffer_data),
                "monitor_status": status,
                "session": session_name
            }
            
            # Guardar resultado en variable si se especifica
            if "result" in config:
                self.set_variable(config["id"], result)
            
            return result
    
    def _auto_connect_session(self, session_name: str, session_config: Dict[str, Any]):
        """Auto-conecta una sesión preconfigurada."""
        try:
            # Crear configuración de conexión
            connection_config = {
                'port': session_config.get('port'),
                'baudrate': session_config.get('baudrate', 9600),
                'timeout': session_config.get('timeout', 1.0),
                'parity': session_config.get('parity', 'NONE'),
                'stopbits': session_config.get('stopbits', 1),
                'bytesize': session_config.get('bytesize', 8),
                'xonxoff': session_config.get('xonxoff', False),
                'rtscts': session_config.get('rtscts', False),
                'dsrdtr': session_config.get('dsrdtr', False),
                'auto_reconnect': session_config.get('auto_reconnect', False),
                'reconnect_attempts': session_config.get('reconnect_attempts', 3),
                'reconnect_delay': session_config.get('reconnect_delay', 1.0)
            }
            
            # Crear y conectar sesión
            session = SerialSession(session_name, connection_config['port'], **connection_config)
            self.sessions[session_name] = session
            
            success = session.connect()
            if success:
                Output.Console(self.plugin_name, f"Auto-conexión exitosa: {session_name}")
            else:
                Output.Console(self.plugin_name, f"Auto-conexión falló: {session_name} - {session.connection.last_error}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error en auto-conexión {session_name}: {str(e)}")
    
    def cleanup(self):
        """Limpia recursos del plugin."""
        with self.lock:
            # Detener todos los monitores
            for monitor in self.monitors.values():
                monitor.cleanup()
            self.monitors.clear()
            
            # Desconectar todas las sesiones
            for session in self.sessions.values():
                session.cleanup()
            self.sessions.clear()
            
            # Limpiar configuración
            self.meta_config.clear()
            self.preconfigured_sessions.clear()
        
        Output.Console(self.plugin_name, "Plugin Serial limpiado")