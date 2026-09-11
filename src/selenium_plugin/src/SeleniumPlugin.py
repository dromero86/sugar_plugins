"""
Selenium Plugin Implementation v2.0
==================================

Plugin principal para automatización web con Selenium usando sintaxis @selenium/.
Proporciona capacidades de automatización web a través del sistema de plugins de Sugar.

Características principales:
- Sintaxis unificada @selenium/
- Soporte completo de navegadores (Chrome, Firefox, Edge, Safari, Opera, IE)
- Sistema avanzado de cookies con arrays y propiedades completas
- 19 operadores disponibles
- Descarga automática de drivers
- Gestión robusta de errores
- Interpolación completa de variables {{variable}}
- Soporte para selectores dinámicos y JavaScript con variables
"""

import os
import time
import base64
import json
import datetime
import threading
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, ElementNotInteractableException,
    NoAlertPresentException
)

# Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Edge
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

# Safari (macOS only - not available on Linux)
# from selenium.webdriver.safari.service import Service as SafariService
# from selenium.webdriver.safari.options import Options as SafariOptions

# Opera (deprecated - removed in Selenium 4.x)
# from selenium.webdriver.opera.options import Options as OperaOptions

# Internet Explorer (deprecated - removed in newer versions)
# from selenium.webdriver.ie.service import Service as IEService
# from selenium.webdriver.ie.options import Options as IEOptions

# WebDriver Manager para todos los navegadores
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.safari import SafariDriverManager  # Safari macOS only
# from webdriver_manager.opera import OperaDriverManager  # Opera deprecated
# from webdriver_manager.internet_explorer import IEDriverManager  # IE deprecated

from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

class SeleniumPlugin(PluginBase):
    """
    Plugin de automatización Selenium para Sugar v2.0.
    
    Sintaxis soportada:
    {
      "selenium": {
        "operator": "command",
        ...
      }
    }
    
    Operadores disponibles:
    - click: Hacer clic en elementos
    - open: Abrir navegador y URL
    - javascript: Ejecutar código JavaScript
    - type: Escribir texto
    - wait: Esperar condiciones
    - screenshot: Capturar pantalla
    - navigate: Navegación básica
    - find: Buscar elementos
    - submit: Enviar formularios
    - clear: Limpiar campos
    - select: Seleccionar opciones
    - hover: Pasar el mouse
    - scroll: Desplazamiento
    - upload: Subir archivos
    - download: Descargar archivos
    - cookies: Gestión de cookies
    - window: Gestión de ventanas
    - frame: Cambiar frames
    - alert: Manejar alertas
    - page: Información de la página actual (url, title, source)
    - state: Estado de un elemento (displayed, enabled, selected)
    - dblclick: Doble clic en elemento
    - rightclick: Clic derecho (context click) en elemento
    - keys: Enviar teclas especiales (ENTER, ESCAPE, TAB, etc.)
    - quit: Cerrar la sesión del navegador a mitad de script
    - storage: Gestión de localStorage/sessionStorage
    - drag_and_drop: Arrastrar un elemento hasta otro
    - pdf: Imprimir la página actual a PDF
    """
    
    VERSION = "2.1.0"
    DESCRIPTION = "Plugin Selenium para Sugar con sintaxis @selenium/"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["selenium>=4.0.0", "webdriver-manager>=3.8.0"]
    
    # Navegadores soportados
    SUPPORTED_BROWSERS = {
        'chrome': {
            'name': 'Chrome',
            'service': ChromeService,
            'options': ChromeOptions,
            'driver_manager': ChromeDriverManager,
            'headless_support': True,
            'detach_support': True,
            'platforms': ['linux', 'windows', 'macos']
        },
        'firefox': {
            'name': 'Firefox',
            'service': FirefoxService,
            'options': FirefoxOptions,
            'driver_manager': GeckoDriverManager,
            'headless_support': True,
            'detach_support': False,
            'platforms': ['linux', 'windows', 'macos']
        },
        'edge': {
            'name': 'Edge',
            'service': EdgeService,
            'options': EdgeOptions,
            'driver_manager': EdgeChromiumDriverManager,
            'headless_support': True,
            'detach_support': True,
            'platforms': ['linux', 'windows', 'macos']
        },



    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Inicializa el plugin de Selenium."""
        super().__init__(context, plugin_config)
        
        self.driver = None
        self.browser_config = None
        self.wait_timeout = 10
        self.implicit_wait = 5
        self.output = Output()
        # Una sola instancia de plugin (y por lo tanto un solo self.driver)
        # es compartida si Sugar ejecuta tareas selenium en paralelo
        # (thread/parallel). Este lock evita que dos threads inicialicen
        # el driver al mismo tiempo y se pisen entre sí; no hace que las
        # operaciones sobre un mismo driver ya inicializado sean paralelas
        # entre sí (Selenium/WebDriver no soporta eso de todos modos).
        self._driver_lock = threading.Lock()
        
    def get_available_commands(self) -> List[str]:
        """
        Retorna la lista de comandos disponibles del plugin.
        
        Returns:
            Lista de nombres de comandos soportados
        """
        return [
            "selenium"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta un operador de Selenium.
        
        Args:
            operator: El operador a ejecutar (siempre 'selenium')
            config: Configuración del operador
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            Output.Console(self.plugin_name, f"DEBUG: Ejecutando plugin Selenium con operator: {operator}")
            Output.Console(self.plugin_name, f"DEBUG: Config recibida: {config}")
            
            if operator != 'selenium':
                raise ValueError(f"Operador no soportado: {operator}")
            
            selenium_config = config.get('selenium', config)
            command = selenium_config.get('operator')
            
            Output.Console(self.plugin_name, f"DEBUG: Comando a ejecutar: {command}")
            Output.Console(self.plugin_name, f"DEBUG: Config selenium: {selenium_config}")
            
            if not command:
                raise ValueError("Operador 'operator' requerido en configuración selenium")
            
            # Inicializar driver si no existe. Con lock para evitar que dos
            # threads (tareas selenium en paralelo) inicialicen el driver
            # al mismo tiempo y se pisen entre sí.
            with self._driver_lock:
                if self.driver is None:
                    Output.Console(self.plugin_name, "DEBUG: Driver no existe, inicializando...")
                    self._initialize_driver()
                else:
                    Output.Console(self.plugin_name, "DEBUG: Driver ya existe, reutilizando...")
            
            # Ejecutar comando
            Output.Console(self.plugin_name, f"DEBUG: Ejecutando comando: {command}")
            result = self._execute_command(command, selenium_config)
            
            Output.Console(self.plugin_name, f"DEBUG: Resultado del comando: {result}")
            return result
            
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR en plugin Selenium: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _initialize_driver(self):
        """Inicializa el driver de Selenium según la configuración."""
        Output.Console(self.plugin_name, "DEBUG: Iniciando _initialize_driver()")
        
        if not hasattr(self, 'context') or not self.context:
            Output.Console(self.plugin_name, "ERROR: Contexto no disponible para inicializar driver")
            raise ValueError("Contexto no disponible para inicializar driver")
        
        # Obtener configuración del contexto
        meta = getattr(self.context, 'meta', {})
        browser_name = meta.get('browser', 'chrome').lower()
        
        Output.Console(self.plugin_name, f"DEBUG: Browser configurado: {browser_name}")
        Output.Console(self.plugin_name, f"DEBUG: Meta config: {meta}")
        
        if browser_name not in self.SUPPORTED_BROWSERS:
            Output.Console(self.plugin_name, f"ERROR: Navegador no soportado: {browser_name}")
            raise ValueError(f"Navegador no soportado: {browser_name}")
        
        browser_config = self.SUPPORTED_BROWSERS[browser_name]
        self.browser_config = browser_config
        
        Output.Console(self.plugin_name, f"DEBUG: Browser config obtenido: {browser_config}")
        
        # Configurar opciones
        options = browser_config['options']()
        
        # Configuraciones básicas
        headless = meta.get('headless', False)
        detach = meta.get('detach', False)
        custom_options = meta.get('options', [])
        
        # Aplicar opciones según navegador
        if browser_name == 'chrome':
            if headless:
                options.add_argument('--headless')
            if detach:
                options.add_experimental_option("detach", True)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
        elif browser_name == 'firefox':
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
        elif browser_name == 'edge':
            if headless:
                options.add_argument('--headless')
            if detach:
                options.add_experimental_option("detach", True)
            options.add_argument('--no-sandbox')

        # Aplicar opciones personalizadas
        for option in custom_options:
            options.add_argument(option)
            Output.Console(self.plugin_name, f"DEBUG: Agregada opción: {option}")
        
        # Configurar timeouts
        self.wait_timeout = meta.get('timeout', 10)
        self.implicit_wait = meta.get('implicit_wait', 5)
        
        Output.Console(self.plugin_name, f"DEBUG: Timeout configurado: {self.wait_timeout}")
        Output.Console(self.plugin_name, f"DEBUG: Implicit wait configurado: {self.implicit_wait}")
        
        # Obtener driver path
        driver_path = meta.get('driver', {}).get('bin')
        
        Output.Console(self.plugin_name, f"DEBUG: Driver path configurado: {driver_path}")
        
        try:
            if driver_path and os.path.exists(driver_path):
                # Usar driver personalizado
                Output.Console(self.plugin_name, f"DEBUG: Usando driver personalizado: {driver_path}")
                service = browser_config['service'](executable_path=driver_path)
            else:
                # Descargar driver automáticamente
                Output.Console(self.plugin_name, "DEBUG: Descargando driver automáticamente...")
                driver_manager = browser_config['driver_manager']()
                driver_path = driver_manager.install()
                service = browser_config['service'](executable_path=driver_path)
                Output.Console(self.plugin_name, f"DEBUG: Driver descargado en: {driver_path}")
            
            # Crear driver
            Output.Console(self.plugin_name, f"DEBUG: Creando driver de {browser_config['name']}...")
            driver_class = getattr(webdriver, browser_config['name'])
            self.driver = driver_class(service=service, options=options)
            self.driver.implicitly_wait(self.implicit_wait)
            
            Output.Console(self.plugin_name, f"Driver {browser_config['name']} inicializado correctamente")
            Output.Console(self.plugin_name, f"DEBUG: Driver creado exitosamente: {self.driver}")
            
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR al inicializar driver {browser_config['name']}: {str(e)}")
            raise Exception(f"Error al inicializar driver {browser_config['name']}: {str(e)}")
    
    def _execute_command(self, command: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un comando específico de Selenium."""
        try:
            # Verificar estado del contexto y variables disponibles
            self._debug_context_state()
            
            # Interpolar variables en la configuración antes de ejecutar
            interpolated_config = self._interpolate_config(config)
            
            # Registrar resumen de interpolaciones
            self._log_interpolation_summary(config)
            
            # Validaciones específicas por comando
            if command == 'open':
                url = interpolated_config.get('url')
                if url and not self._validate_url(url):
                    Output.Console(self.plugin_name, f"ADVERTENCIA: URL puede estar malformada: {url}")
            
            elif command == 'javascript':
                from_file = interpolated_config.get('from_file')
                if from_file and not self._validate_file_path(from_file):
                    Output.Console(self.plugin_name, f"ADVERTENCIA: Archivo JavaScript no encontrado: {from_file}")
            
            # Ejecutar comando
            if command == 'click':
                return self._execute_click(interpolated_config)
            elif command == 'open':
                return self._execute_open(interpolated_config)
            elif command == 'javascript':
                return self._execute_javascript(interpolated_config)
            elif command == 'type':
                return self._execute_type(interpolated_config)
            elif command == 'wait':
                return self._execute_wait(interpolated_config)
            elif command == 'screenshot':
                return self._execute_screenshot(interpolated_config)
            elif command == 'navigate':
                return self._execute_navigate(interpolated_config)
            elif command == 'find':
                return self._execute_find(interpolated_config)
            elif command == 'submit':
                return self._execute_submit(interpolated_config)
            elif command == 'clear':
                return self._execute_clear(interpolated_config)
            elif command == 'select':
                return self._execute_select(interpolated_config)
            elif command == 'hover':
                return self._execute_hover(interpolated_config)
            elif command == 'drag_and_drop':
                return self._execute_drag_and_drop(interpolated_config)
            elif command == 'pdf':
                return self._execute_pdf(interpolated_config)
            elif command == 'dblclick':
                return self._execute_dblclick(interpolated_config)
            elif command == 'rightclick':
                return self._execute_rightclick(interpolated_config)
            elif command == 'keys':
                return self._execute_keys(interpolated_config)
            elif command == 'scroll':
                return self._execute_scroll(interpolated_config)
            elif command == 'upload':
                return self._execute_upload(interpolated_config)
            elif command == 'download':
                return self._execute_download(interpolated_config)
            elif command == 'cookies':
                return self._execute_cookies(interpolated_config)
            elif command == 'window':
                return self._execute_window(interpolated_config)
            elif command == 'frame':
                return self._execute_frame(interpolated_config)
            elif command == 'alert':
                return self._execute_alert(interpolated_config)
            elif command == 'page':
                return self._execute_page(interpolated_config)
            elif command == 'state':
                return self._execute_state(interpolated_config)
            elif command == 'quit':
                return self._execute_quit(interpolated_config)
            elif command == 'storage':
                return self._execute_storage(interpolated_config)
            else:
                raise ValueError(f"Comando no soportado: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error ejecutando comando {command}: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _interpolate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Interpola variables en la configuración usando el sistema de Sugar."""
        if not isinstance(config, dict):
            return config
        
        Output.Console(self.plugin_name, f"DEBUG: Interpolando configuración: {config}")
        
        interpolated = {}
        failed_interpolations = []
        
        for key, value in config.items():
            if isinstance(value, str):
                # Interpolar variables en strings
                original_value = value
                try:
                    interpolated_value = self.interpolate_variables(value)
                    interpolated[key] = interpolated_value
                    
                    # Detectar interpolaciones fallidas
                    if "{{" in interpolated_value and "}}" in interpolated_value:
                        failed_interpolations.append(f"{key}: {interpolated_value}")
                    
                    if original_value != interpolated_value:
                        Output.Console(self.plugin_name, f"DEBUG: Interpolado '{key}': '{original_value}' -> '{interpolated_value}'")
                    else:
                        Output.Console(self.plugin_name, f"DEBUG: No se detectaron variables para interpolar en '{key}': '{original_value}'")
                        
                except Exception as e:
                    Output.Console(self.plugin_name, f"ERROR interpolando '{key}': {str(e)}")
                    interpolated[key] = original_value
                    
            elif isinstance(value, dict):
                # Interpolar recursivamente en diccionarios
                interpolated[key] = self._interpolate_config(value)
            elif isinstance(value, list):
                # Interpolar en listas
                interpolated[key] = [
                    self._interpolate_config(item) if isinstance(item, dict)
                    else self.interpolate_variables(item) if isinstance(item, str)
                    else item for item in value
                ]
            else:
                # Mantener otros tipos sin cambios
                interpolated[key] = value
        
        # Reportar interpolaciones fallidas
        if failed_interpolations:
            Output.Console(self.plugin_name, f"ADVERTENCIA: Interpolaciones fallidas detectadas: {failed_interpolations}")
        
        Output.Console(self.plugin_name, f"DEBUG: Configuración interpolada: {interpolated}")
        return interpolated
    
    def _execute_click(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta clic en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación click")

        Output.Console(self.plugin_name, f"DEBUG: Selector: {selector}")

        element = self._find_element(selector)
        element.click()
        
        result_key = config.get('result', 'clicked')
        return {result_key: True, "success": True}
    
    def _execute_open(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Abre navegador y URL."""
        Output.Console(self.plugin_name, "DEBUG: Ejecutando _execute_open()")
        
        url = config.get('url')
        Output.Console(self.plugin_name, f"DEBUG: URL a abrir: {url}")
        
        if not url:
            Output.Console(self.plugin_name, "ERROR: URL requerida para operación open")
            raise ValueError("URL requerida para operación open")
        
        # Validar formato de URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                Output.Console(self.plugin_name, f"ADVERTENCIA: URL puede estar malformada: {url}")
        except Exception as e:
            Output.Console(self.plugin_name, f"ADVERTENCIA: Error validando URL {url}: {str(e)}")
        
        try:
            Output.Console(self.plugin_name, f"DEBUG: Navegando a URL: {url}")
            self.driver.get(url)
            Output.Console(self.plugin_name, f"Página abierta exitosamente: {url}")
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR: Error navegando a URL {url}: {str(e)}")
            raise
        
        result_key = config.get('result', 'opened')
        Output.Console(self.plugin_name, f"DEBUG: Result key: {result_key}")
        
        return {result_key: True, "success": True, "url": url}
    
    def _execute_javascript(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta código JavaScript."""
        code = config.get('code')
        from_file = config.get('from_file')
        from_string = config.get('from_string')
        
        if from_file:
            file_path = Path(from_file)
            Output.Console(self.plugin_name, f"DEBUG: Intentando cargar archivo JavaScript: {file_path}")
            
            if not file_path.exists():
                Output.Console(self.plugin_name, f"ERROR: Archivo JavaScript no encontrado: {from_file}")
                raise FileNotFoundError(f"Archivo JavaScript no encontrado: {from_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                Output.Console(self.plugin_name, f"Archivo JavaScript cargado exitosamente: {from_file}")
            except Exception as e:
                Output.Console(self.plugin_name, f"ERROR: Error leyendo archivo JavaScript {from_file}: {str(e)}")
                raise
                
        elif from_string:
            code = from_string
            Output.Console(self.plugin_name, f"DEBUG: Usando código JavaScript from_string: {code[:100]}...")
        elif not code:
            raise ValueError("Código JavaScript requerido (code, from_file, o from_string)")
        
        try:
            result = self.driver.execute_script(code)
            Output.Console(self.plugin_name, f"Código JavaScript ejecutado exitosamente")
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR: Error ejecutando JavaScript: {str(e)}")
            raise
        
        result_key = config.get('result', 'js_result')
        return {result_key: result, "success": True}
    
    def _execute_type(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Escribe texto en elemento."""
        selector = config.get('selector')
        value = config.get('value', '')
        enter = config.get('enter', False)
        
        if not selector:
            raise ValueError("Selector requerido para operación type")

        Output.Console(self.plugin_name, f"DEBUG: Selector CSS: {selector}")
        Output.Console(self.plugin_name, f"DEBUG: Value: {value}")
        
        element = self._find_element(selector)
        element.clear()
        element.send_keys(value)
        
        if enter:
            element.send_keys(Keys.RETURN)
        
        result_key = config.get('result', 'typed')
        return {result_key: True, "success": True, "value": value}
    
    def _execute_wait(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Espera condiciones."""
        wait_type = config.get('type', 'time')
        
        if wait_type == 'time':
            seconds = config.get('seconds', 1)
            time.sleep(seconds)
            result_key = config.get('result', 'waited')
            return {result_key: True, "success": True, "seconds": seconds}
            
        elif wait_type == 'element':
            selector = config.get('selector')
            if not selector:
                raise ValueError("Selector requerido para wait element")
            
            wait = WebDriverWait(self.driver, self.wait_timeout)
            element = wait.until(EC.presence_of_element_located(self._resolve_by(selector)))

            result_key = config.get('result', 'element_found')
            return {result_key: True, "success": True}
            
        elif wait_type == 'clickable':
            selector = config.get('selector')
            if not selector:
                raise ValueError("Selector requerido para wait clickable")
            
            wait = WebDriverWait(self.driver, self.wait_timeout)
            element = wait.until(EC.element_to_be_clickable(self._resolve_by(selector)))

            result_key = config.get('result', 'clickable')
            return {result_key: True, "success": True}

        elif wait_type == 'invisible':
            selector = config.get('selector')
            if not selector:
                raise ValueError("Selector requerido para wait invisible")

            wait = WebDriverWait(self.driver, self.wait_timeout)
            wait.until(EC.invisibility_of_element_located(self._resolve_by(selector)))

            result_key = config.get('result', 'invisible')
            return {result_key: True, "success": True}

        elif wait_type == 'url_changes':
            # 'from_url' es la URL de referencia contra la que se espera el
            # cambio; si no se pasa, se toma la URL actual al momento de
            # empezar a esperar.
            from_url = config.get('from_url', self.driver.current_url)

            wait = WebDriverWait(self.driver, self.wait_timeout)
            wait.until(EC.url_changes(from_url))

            result_key = config.get('result', 'url_changed')
            return {result_key: True, "success": True, "url": self.driver.current_url}

        elif wait_type == 'title_contains':
            title = config.get('title')
            if not title:
                raise ValueError("'title' requerido para wait title_contains")

            wait = WebDriverWait(self.driver, self.wait_timeout)
            wait.until(EC.title_contains(title))

            result_key = config.get('result', 'title_matched')
            return {result_key: True, "success": True, "title": self.driver.title}

        else:
            raise ValueError(f"Tipo de espera no soportado: {wait_type}")
    
    def _execute_screenshot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Captura pantalla (de toda la página, o de un elemento si se pasa 'selector')."""
        file_path = config.get('file', f"screenshot_{int(time.time())}.png")
        selector = config.get('selector')

        # Crear directorio si no existe
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        if selector:
            element = self._find_element(selector)
            element.screenshot(file_path)
        else:
            self.driver.save_screenshot(file_path)

        result_key = config.get('result', 'screenshot')
        return {result_key: file_path, "success": True}
    
    def _execute_navigate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Navegación básica."""
        action = config.get('action', 'refresh')
        
        if action == 'refresh':
            self.driver.refresh()
        elif action == 'back':
            self.driver.back()
        elif action == 'forward':
            self.driver.forward()
        else:
            raise ValueError(f"Acción de navegación no soportada: {action}")
        
        result_key = config.get('result', 'navigated')
        return {result_key: True, "success": True, "action": action}

    def _execute_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Información de la página actual: url, title, source."""
        info = {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "source": self.driver.page_source,
        }

        result_key = config.get('result', 'page')
        return {result_key: info, "success": True}

    def _execute_state(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Chequea el estado de un elemento: is_displayed, is_enabled, is_selected."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación state")

        try:
            element = self._find_element(selector)
        except ValueError:
            # Elemento no encontrado: no está visible/habilitado/seleccionado.
            info = {"exists": False, "displayed": False, "enabled": False, "selected": False}
            result_key = config.get('result', 'state')
            return {result_key: info, "success": True}

        info = {
            "exists": True,
            "displayed": element.is_displayed(),
            "enabled": element.is_enabled(),
            "selected": element.is_selected(),
        }

        result_key = config.get('result', 'state')
        return {result_key: info, "success": True}

    def _execute_find(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Busca elementos."""
        selector = config.get('selector')
        multiple = config.get('multiple', False)
        attribute = config.get('attribute')

        if not selector:
            raise ValueError("Selector requerido para operación find")

        def describe(el):
            info = {"text": el.text, "tag": el.tag_name}
            if attribute:
                info["attribute"] = el.get_attribute(attribute)
            return info

        if multiple:
            by, value = self._resolve_by(selector)
            elements = self.driver.find_elements(by, value)
            result = [describe(el) for el in elements]
        else:
            element = self._find_element(selector)
            result = describe(element)

        result_key = config.get('result', 'found')
        return {result_key: result, "success": True}
    
    def _execute_submit(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Envía formulario."""
        selector = config.get('selector')
        
        if selector:
            element = self._find_element(selector)
            element.submit()
        else:
            # Enviar formulario activo
            self.driver.find_element(By.TAG_NAME, "body").submit()
        
        result_key = config.get('result', 'submitted')
        return {result_key: True, "success": True}
    
    def _execute_clear(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia campo."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación clear")
        
        element = self._find_element(selector)
        element.clear()
        
        result_key = config.get('result', 'cleared')
        return {result_key: True, "success": True}
    
    def _execute_select(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Selecciona opción."""
        selector = config.get('selector')
        value = config.get('value')
        text = config.get('text')
        index = config.get('index')
        
        if not selector:
            raise ValueError("Selector requerido para operación select")
        
        element = self._find_element(selector)
        select = Select(element)
        
        if value:
            select.select_by_value(value)
        elif text:
            select.select_by_visible_text(text)
        elif index is not None:
            select.select_by_index(index)
        else:
            raise ValueError("Se requiere value, text o index para operación select")
        
        result_key = config.get('result', 'selected')
        return {result_key: True, "success": True}
    
    def _execute_hover(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Pasa el mouse sobre elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación hover")
        
        element = self._find_element(selector)
        ActionChains(self.driver).move_to_element(element).perform()
        
        result_key = config.get('result', 'hovered')
        return {result_key: True, "success": True}

    def _execute_drag_and_drop(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Arrastra el elemento 'source' hasta el elemento 'target'. Usa
        eventos de mouse simulados (ActionChains.drag_and_drop), que
        funcionan con drag-and-drop implementado a mano con mousedown/
        mousemove/mouseup; el drag-and-drop nativo HTML5 (atributo
        draggable + eventos dragstart/drop) no siempre responde a esto,
        es una limitación conocida de Selenium/WebDriver, no de este plugin.
        """
        source_selector = config.get('source')
        target_selector = config.get('target')
        if not source_selector:
            raise ValueError("'source' requerido para operación drag_and_drop")
        if not target_selector:
            raise ValueError("'target' requerido para operación drag_and_drop")

        source = self._find_element(source_selector)
        target = self._find_element(target_selector)
        ActionChains(self.driver).drag_and_drop(source, target).perform()

        result_key = config.get('result', 'dragged')
        return {result_key: True, "success": True}

    def _execute_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Imprime la página actual a PDF (comando 'Print Page' de WebDriver)."""
        file_path = config.get('file', f"page_{int(time.time())}.pdf")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        pdf_base64 = self.driver.print_page()
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(pdf_base64))

        result_key = config.get('result', 'pdf')
        return {result_key: file_path, "success": True}

    def _execute_dblclick(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Doble clic en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación dblclick")

        element = self._find_element(selector)
        ActionChains(self.driver).double_click(element).perform()

        result_key = config.get('result', 'dblclicked')
        return {result_key: True, "success": True}

    def _execute_rightclick(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Clic derecho (context click) en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación rightclick")

        element = self._find_element(selector)
        ActionChains(self.driver).context_click(element).perform()

        result_key = config.get('result', 'rightclicked')
        return {result_key: True, "success": True}

    def _execute_keys(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una o más teclas especiales (ENTER, ESCAPE, TAB, flechas, etc.)
        a un elemento, o al elemento activo si no se pasa 'selector'.

        'keys' acepta un nombre de tecla (ej. 'ENTER') o una lista de
        nombres (ej. ['CONTROL', 'a']) — deben coincidir con atributos de
        selenium.webdriver.common.keys.Keys (case-insensitive).
        """
        selector = config.get('selector')
        key_names = config.get('keys')
        if not key_names:
            raise ValueError("'keys' requerido para operación keys")
        if isinstance(key_names, str):
            key_names = [key_names]

        resolved_keys = []
        for name in key_names:
            key_value = getattr(Keys, name.upper(), None)
            if key_value is None:
                raise ValueError(f"Tecla no reconocida: {name}")
            resolved_keys.append(key_value)

        if selector:
            element = self._find_element(selector)
            element.send_keys(*resolved_keys)
        else:
            ActionChains(self.driver).send_keys(*resolved_keys).perform()

        result_key = config.get('result', 'keys_sent')
        return {result_key: True, "success": True}

    def _execute_scroll(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Desplazamiento."""
        scroll_type = config.get('type', 'to_element')
        
        if scroll_type == 'to_element':
            selector = config.get('selector')
            if not selector:
                raise ValueError("Selector requerido para scroll to_element")
            
            element = self._find_element(selector)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            
        elif scroll_type == 'by_pixels':
            x = config.get('x', 0)
            y = config.get('y', 0)
            self.driver.execute_script(f"window.scrollBy({x}, {y});")
            
        elif scroll_type == 'to_position':
            x = config.get('x', 0)
            y = config.get('y', 0)
            self.driver.execute_script(f"window.scrollTo({x}, {y});")
            
        else:
            raise ValueError(f"Tipo de scroll no soportado: {scroll_type}")
        
        result_key = config.get('result', 'scrolled')
        return {result_key: True, "success": True}
    
    def _execute_upload(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sube archivo."""
        selector = config.get('selector')
        file_path = config.get('file')
        
        if not selector:
            raise ValueError("Selector requerido para operación upload")
        if not file_path:
            raise ValueError("Archivo requerido para operación upload")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        element = self._find_element(selector)
        element.send_keys(os.path.abspath(file_path))
        
        result_key = config.get('result', 'uploaded')
        return {result_key: True, "success": True, "file": file_path}
    
    def _execute_download(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Descarga archivo."""
        url = config.get('url')
        file_path = config.get('file')
        timeout = config.get('timeout', 10)

        if not url:
            raise ValueError("URL requerida para operación download")
        if not file_path:
            raise ValueError("Ruta de archivo requerida para operación download")

        # Crear directorio si no existe
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Descargar usando JavaScript. NOTA: esto hace que el navegador
        # guarde el archivo en SU carpeta de descargas por defecto, no
        # necesariamente en 'file_path' — eso depende de que el navegador
        # esté configurado (vía meta.options/prefs) para descargar
        # directamente ahí. Por eso el resultado se verifica en disco en
        # vez de asumir éxito.
        script = f"""
        var link = document.createElement('a');
        link.href = '{url}';
        link.download = '{os.path.basename(file_path)}';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        """

        self.driver.execute_script(script)

        result_key = config.get('result', 'downloaded')
        deadline = time.time() + timeout
        while time.time() < deadline:
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                return {result_key: True, "success": True, "file": file_path}
            time.sleep(0.5)

        return {
            result_key: False,
            "success": False,
            "file": file_path,
            "error": (
                f"El navegador no guardó el archivo en '{file_path}' dentro de {timeout}s. "
                "Esta operación depende de que el navegador esté configurado para descargar "
                "directamente en esa ruta (ver meta.options/prefs de descarga)."
            ),
        }
    
    def _execute_cookies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Gestión de cookies."""
        action = config.get('action', 'get')
        
        if action == 'get':
            cookies = self.driver.get_cookies()
            result_key = config.get('result', 'cookies')
            return {result_key: cookies, "success": True}
            
        elif action == 'add':
            # Cookie individual
            if 'name' in config and 'value' in config:
                cookie = self._build_cookie_dict(config)
                self.driver.add_cookie(cookie)
                result_key = config.get('result', 'cookie_added')
                return {result_key: True, "success": True}
            
            # Array de cookies
            elif 'cookies' in config:
                cookies = config['cookies']
                if not isinstance(cookies, list):
                    raise ValueError("cookies debe ser un array")
                
                added_count = 0
                for cookie_data in cookies:
                    cookie = self._build_cookie_dict(cookie_data)
                    self.driver.add_cookie(cookie)
                    added_count += 1
                
                result_key = config.get('result', 'cookies_added')
                return {result_key: added_count, "success": True}
            
            else:
                raise ValueError("Se requiere name/value o cookies array para add")
                
        elif action == 'delete':
            name = config.get('name')
            if not name:
                raise ValueError("Nombre de cookie requerido para delete")
            
            self.driver.delete_cookie(name)
            result_key = config.get('result', 'cookie_deleted')
            return {result_key: True, "success": True}
            
        elif action == 'clear':
            self.driver.delete_all_cookies()
            result_key = config.get('result', 'cookies_cleared')
            return {result_key: True, "success": True}
            
        elif action == 'get_by_name':
            name = config.get('name')
            if not name:
                raise ValueError("Nombre de cookie requerido para get_by_name")
            
            cookie = self.driver.get_cookie(name)
            result_key = config.get('result', 'cookie_by_name')
            return {result_key: cookie, "success": True}
            
        elif action == 'get_by_domain':
            domain = config.get('domain')
            if not domain:
                raise ValueError("Dominio requerido para get_by_domain")
            
            all_cookies = self.driver.get_cookies()
            domain_cookies = [cookie for cookie in all_cookies if cookie.get("domain") == domain]
            result_key = config.get('result', 'cookies_by_domain')
            return {result_key: domain_cookies, "success": True}
        
        else:
            raise ValueError(f"Acción de cookies no soportada: {action}")
    
    def _build_cookie_dict(self, cookie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construye diccionario de cookie con propiedades completas."""
        cookie = {
            'name': cookie_data['name'],
            'value': cookie_data['value']
        }
        
        # Propiedades opcionales
        if 'domain' in cookie_data:
            cookie['domain'] = cookie_data['domain']
        if 'path' in cookie_data:
            cookie['path'] = cookie_data['path']
        if 'expiry' in cookie_data:
            expiry = cookie_data['expiry']
            if isinstance(expiry, str):
                # Convertir string a timestamp
                try:
                    dt = datetime.datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                    cookie['expiry'] = int(dt.timestamp())
                except (ValueError, TypeError):
                    # Si no se puede parsear, usar como está
                    cookie['expiry'] = expiry
            else:
                cookie['expiry'] = expiry
        if 'secure' in cookie_data:
            cookie['secure'] = bool(cookie_data['secure'])
        if 'httpOnly' in cookie_data:
            cookie['httpOnly'] = bool(cookie_data['httpOnly'])
        
        return cookie
    
    def _execute_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Gestión de ventanas."""
        action = config.get('action', 'switch')
        
        if action == 'switch':
            window_handle = config.get('handle')
            if window_handle:
                self.driver.switch_to.window(window_handle)
            else:
                # Cambiar a la última ventana
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
        elif action == 'close':
            self.driver.close()
            
        elif action == 'maximize':
            self.driver.maximize_window()
            
        elif action == 'minimize':
            self.driver.minimize_window()
            
        else:
            raise ValueError(f"Acción de ventana no soportada: {action}")
        
        result_key = config.get('result', 'window_action')
        return {result_key: True, "success": True, "action": action}
    
    def _execute_frame(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Cambiar frames."""
        action = config.get('action', 'switch')
        
        if action == 'switch':
            frame_id = config.get('id')
            frame_name = config.get('name')
            frame_index = config.get('index')
            
            if frame_id:
                self.driver.switch_to.frame(frame_id)
            elif frame_name:
                self.driver.switch_to.frame(frame_name)
            elif frame_index is not None:
                self.driver.switch_to.frame(frame_index)
            else:
                # Volver al frame principal
                self.driver.switch_to.default_content()
                
        else:
            raise ValueError(f"Acción de frame no soportada: {action}")
        
        result_key = config.get('result', 'frame_action')
        return {result_key: True, "success": True, "action": action}
    
    def _execute_alert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar alertas."""
        action = config.get('action', 'accept')
        
        try:
            alert = self.driver.switch_to.alert
            
            if action == 'accept':
                alert.accept()
            elif action == 'dismiss':
                alert.dismiss()
            elif action == 'send_keys':
                text = config.get('text', '')
                alert.send_keys(text)
            else:
                raise ValueError(f"Acción de alerta no soportada: {action}")

        except NoAlertPresentException:
            # No hay alerta activa
            pass
        
        result_key = config.get('result', 'alert_action')
        return {result_key: True, "success": True, "action": action}

    def _execute_quit(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Cierra la sesión del navegador a mitad de script. La próxima
        operación selenium que se ejecute levanta un driver nuevo."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        result_key = config.get('result', 'quit')
        return {result_key: True, "success": True}

    def _execute_storage(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Gestión de localStorage/sessionStorage (mismo patrón que 'cookies')."""
        storage_type = config.get('type', 'local')
        if storage_type not in ('local', 'session'):
            raise ValueError(f"Tipo de storage no soportado: {storage_type}")
        js_storage = 'localStorage' if storage_type == 'local' else 'sessionStorage'

        action = config.get('action', 'get')

        if action == 'get':
            key = config.get('key')
            if not key:
                raise ValueError("'key' requerido para storage get")
            value = self.driver.execute_script(
                f"return window.{js_storage}.getItem(arguments[0]);", key
            )
            result_key = config.get('result', 'storage_value')
            return {result_key: value, "success": True}

        elif action == 'get_all':
            script = f"""
            var s = window.{js_storage};
            var out = {{}};
            for (var i = 0; i < s.length; i++) {{
                var k = s.key(i);
                out[k] = s.getItem(k);
            }}
            return out;
            """
            value = self.driver.execute_script(script)
            result_key = config.get('result', 'storage')
            return {result_key: value, "success": True}

        elif action == 'set':
            key = config.get('key')
            value = config.get('value')
            if not key:
                raise ValueError("'key' requerido para storage set")
            self.driver.execute_script(
                f"window.{js_storage}.setItem(arguments[0], arguments[1]);", key, value
            )
            result_key = config.get('result', 'storage_set')
            return {result_key: True, "success": True}

        elif action == 'remove':
            key = config.get('key')
            if not key:
                raise ValueError("'key' requerido para storage remove")
            self.driver.execute_script(
                f"window.{js_storage}.removeItem(arguments[0]);", key
            )
            result_key = config.get('result', 'storage_removed')
            return {result_key: True, "success": True}

        elif action == 'clear':
            self.driver.execute_script(f"window.{js_storage}.clear();")
            result_key = config.get('result', 'storage_cleared')
            return {result_key: True, "success": True}

        else:
            raise ValueError(f"Acción de storage no soportada: {action}")

    def _resolve_by(self, selector: str) -> tuple:
        """
        Determina el mecanismo de localización (By.XPATH o By.CSS_SELECTOR)
        a partir del selector recibido.

        Convenciones soportadas:
          - Prefijo explícito 'xpath=...' -> XPath, sin el prefijo.
          - Selectores que empiezan con '//', './/' o '(' -> XPath (formas
            típicas de una expresión XPath).
          - Cualquier otro caso -> CSS selector (comportamiento previo).
        """
        if selector.startswith('xpath='):
            return By.XPATH, selector[len('xpath='):]
        if selector.startswith(('//', './/', '(')):
            return By.XPATH, selector
        return By.CSS_SELECTOR, selector

    def _find_element(self, selector: str):
        """Encuentra elemento con manejo de errores."""
        by, value = self._resolve_by(selector)
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            raise ValueError(f"Elemento no encontrado: {selector}")

    def _validate_url(self, url: str) -> bool:
        """Valida formato básico de URL."""
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except ValueError:
            return False
    
    def _validate_file_path(self, file_path: str) -> bool:
        """Valida que la ruta de archivo existe y es legible."""
        if not file_path or not isinstance(file_path, str):
            return False
        
        path = Path(file_path)
        return path.exists() and path.is_file() and path.stat().st_size > 0
    
    def _log_interpolation_summary(self, config: Dict[str, Any]) -> None:
        """Registra un resumen de las interpolaciones realizadas."""
        interpolation_count = 0
        interpolated_fields = []
        
        def count_interpolations(obj, path=""):
            nonlocal interpolation_count
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and "{{" in value and "}}" in value:
                        interpolation_count += 1
                        interpolated_fields.append(current_path)
                    elif isinstance(value, (dict, list)):
                        count_interpolations(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    count_interpolations(item, current_path)
        
        count_interpolations(config)
        
        if interpolation_count > 0:
            Output.Console(self.plugin_name, f"RESUMEN: {interpolation_count} campos interpolados: {interpolated_fields}")
        else:
            Output.Console(self.plugin_name, "RESUMEN: No se detectaron interpolaciones")
    
    def cleanup(self):
        """Limpia recursos del plugin."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
    
    def _debug_context_state(self):
        """Depura el estado del contexto y las variables disponibles."""
        try:
            if not self.context:
                Output.Console(self.plugin_name, "DEBUG: Contexto no disponible")
                return
            
            Output.Console(self.plugin_name, "DEBUG: === ESTADO DEL CONTEXTO ===")
            
            # Verificar memory_handler
            if hasattr(self.context, 'memory_handler'):
                Output.Console(self.plugin_name, "memory_handler disponible")
                
                # Verificar variables en el scope actual
                if hasattr(self.context.memory_handler, 'get'):
                    current_vars = self.context.memory_handler.get()
                    if current_vars:
                        Output.Console(self.plugin_name, f"DEBUG: Variables en scope actual: {list(current_vars[-1].keys()) if current_vars[-1] else '{}'}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay variables en scope actual")
                
                # Verificar variables globales
                if hasattr(self.context.memory_handler, 'vars'):
                    global_vars = self.context.memory_handler.vars
                    if global_vars:
                        Output.Console(self.plugin_name, f"DEBUG: Variables globales: {list(global_vars.keys())}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay variables globales")
                
                # Verificar loop actual
                if hasattr(self.context.memory_handler, 'current_loop'):
                    current_loop = self.context.memory_handler.current_loop
                    if current_loop:
                        Output.Console(self.plugin_name, f"DEBUG: Loop actual: {current_loop}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay loop activo")
            else:
                Output.Console(self.plugin_name, "memory_handler no disponible")
            
            Output.Console(self.plugin_name, "DEBUG: === FIN ESTADO DEL CONTEXTO ===")
            
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR en _debug_context_state: {str(e)}") 