"""
Capa de sesion: sesion de navegador
====================================

Dueno del webdriver y de los operadores de Selenium. No conoce Sugar
(solo usa Output para logging) ni el transporte del keeper. Recibe
configuracion ya interpolada desde la capa de arriba.
"""

import base64
import datetime
import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    NoAlertPresentException,
)

from Sugar.Lang.Utils.Output import Output

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec
from session import Humanize, Stealth, Logging
from session.BrowserFactory import BrowserFactory, SUPPORTED_BROWSERS


class BrowserSession:
    """Sesion de navegador reutilizable e independiente de Sugar."""

    def __init__(self, plugin_name: str = 'Selenium'):
        self.plugin_name = plugin_name
        self.driver = None
        self.browser_config: Optional[Dict[str, Any]] = None
        self.wait_timeout = 10
        self.implicit_wait = 5
        self.humanize: Optional[Dict[str, Any]] = None
        self.log_file: Optional[str] = None
        self._driver_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def initialize(self, spec: SessionSpec):
        """Crea el driver a partir del spec."""
        self.wait_timeout = spec.timeout
        self.implicit_wait = spec.implicit_wait
        self.humanize = spec.humanize
        self.log_file = spec.log_file
        self.driver, self.browser_config = BrowserFactory.create(spec, self.plugin_name)
        return self.driver

    def ensure_driver(self, spec: SessionSpec):
        """Inicializa el driver una sola vez, con lock para concurrencia."""
        with self._driver_lock:
            if self.driver is None:
                self.initialize(spec)
        return self.driver

    def quit(self) -> None:
        """Cierra la sesion del navegador."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def cleanup(self) -> None:
        """Limpia recursos de la sesion."""
        self.quit()

    # ------------------------------------------------------------------
    # Dispatch de operadores
    # ------------------------------------------------------------------
    def execute_command(self, command: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un operador de Selenium sobre la sesion actual."""
        try:
            if command == 'open':
                url = config.get('url')
                if url and not self._validate_url(url):
                    Output.Console(self.plugin_name, f"ADVERTENCIA: URL puede estar malformada: {url}")

            elif command == 'javascript':
                from_file = config.get('from_file')
                if from_file and not self._validate_file_path(from_file):
                    Output.Console(self.plugin_name, f"ADVERTENCIA: Archivo JavaScript no encontrado: {from_file}")

            if command == 'click':
                return self._execute_click(config)
            elif command == 'open':
                return self._execute_open(config)
            elif command == 'javascript':
                return self._execute_javascript(config)
            elif command == 'type':
                return self._execute_type(config)
            elif command == 'wait':
                return self._execute_wait(config)
            elif command == 'screenshot':
                return self._execute_screenshot(config)
            elif command == 'navigate':
                return self._execute_navigate(config)
            elif command == 'find':
                return self._execute_find(config)
            elif command == 'submit':
                return self._execute_submit(config)
            elif command == 'clear':
                return self._execute_clear(config)
            elif command == 'select':
                return self._execute_select(config)
            elif command == 'hover':
                return self._execute_hover(config)
            elif command == 'drag_and_drop':
                return self._execute_drag_and_drop(config)
            elif command == 'pdf':
                return self._execute_pdf(config)
            elif command == 'dblclick':
                return self._execute_dblclick(config)
            elif command == 'rightclick':
                return self._execute_rightclick(config)
            elif command == 'keys':
                return self._execute_keys(config)
            elif command == 'scroll':
                return self._execute_scroll(config)
            elif command == 'upload':
                return self._execute_upload(config)
            elif command == 'download':
                return self._execute_download(config)
            elif command == 'cookies':
                return self._execute_cookies(config)
            elif command == 'window':
                return self._execute_window(config)
            elif command == 'frame':
                return self._execute_frame(config)
            elif command == 'alert':
                return self._execute_alert(config)
            elif command == 'page':
                return self._execute_page(config)
            elif command == 'state':
                return self._execute_state(config)
            elif command == 'quit':
                return self._execute_quit(config)
            elif command == 'storage':
                return self._execute_storage(config)
            elif command == 'timeouts':
                return self._execute_timeouts(config)
            elif command == 'actions':
                return self._execute_actions(config)
            elif command == 'element':
                return self._execute_element(config)
            elif command == 'shadow':
                return self._execute_shadow(config)
            elif command == 'cdp':
                return self._execute_cdp(config)
            elif command == 'network':
                return self._execute_network(config)
            elif command == 'capabilities':
                return self._execute_capabilities(config)
            elif command == 'storage_state':
                return self._execute_storage_state(config)
            elif command == 'challenge':
                return self._execute_challenge(config)
            elif command == 'bidi':
                return self._execute_bidi(config)
            elif command == 'downloads':
                return self._execute_downloads(config)
            else:
                raise ValueError(f"Comando no soportado: {command}")

        except Exception as e:
            Logging.log_failure(self.plugin_name, f"operador '{command}'", e, self.log_file)
            return {"error": str(e), "success": False}

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------
    def _execute_click(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta clic en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación click")

        Output.Console(self.plugin_name, f"DEBUG: Selector: {selector}")

        element = self._find_element(selector)
        if self.humanize:
            (ActionChains(self.driver)
                .move_to_element(element)
                .pause(Humanize.between_operators_delay(self.humanize))
                .click()
                .perform())
        else:
            element.click()

        result_key = config.get('id', 'clicked')
        return {result_key: True, "success": True}

    def _execute_open(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Abre navegador y URL."""
        Output.Console(self.plugin_name, "DEBUG: Ejecutando _execute_open()")

        url = config.get('url')
        Output.Console(self.plugin_name, f"DEBUG: URL a abrir: {url}")

        if not url:
            Output.Console(self.plugin_name, "ERROR: URL requerida para operación open")
            raise ValueError("URL requerida para operación open")

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

        result_key = config.get('id', 'opened')
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
            is_async = bool(config.get('async', False))
            script_args = config.get('args', []) or []
            if is_async:
                result = self.driver.execute_async_script(code, *script_args)
            else:
                result = self.driver.execute_script(code, *script_args)
            Output.Console(self.plugin_name, f"Código JavaScript ejecutado exitosamente")
        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR: Error ejecutando JavaScript: {str(e)}")
            raise

        result_key = config.get('id', 'js_result')
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

        if self.humanize and value:
            delay = Humanize.typing_delay(self.humanize)
            for char in value:
                element.send_keys(char)
                time.sleep(delay)
        else:
            element.send_keys(value)

        if enter:
            element.send_keys(Keys.RETURN)

        result_key = config.get('id', 'typed')
        return {result_key: True, "success": True, "value": value}

    DEFAULT_WAIT_KEYS = {
        'element': 'element_found',
        'clickable': 'clickable',
        'invisible': 'invisible',
        'invisibility_of_element': 'invisible',
        'url_changes': 'url_changed',
        'title_contains': 'title_matched',
        'title_is': 'title_matched',
        'visible': 'visible',
        'visibility_of': 'visible',
        'visibility_of_all_elements_located': 'visible_all',
        'visibility_of_any_elements_located': 'visible_any',
        'all_present': 'all_present',
        'text_present': 'text_present',
        'text_present_value': 'text_present_value',
        'text_to_be_present_in_element_attribute': 'text_attribute',
        'selected': 'selected',
        'element_selection_state_to_be': 'selection_state',
        'element_located_selection_state_to_be': 'selection_state',
        'staleness': 'stale',
        'alert_present': 'alert_present',
        'frame_available': 'frame_available',
        'window_count': 'window_count',
        'new_window': 'new_window',
        'url_contains': 'url_contains',
        'url_matches': 'url_matches',
        'url_to_be': 'url_to_be',
        'attribute_contains': 'attribute_contains',
        'all_of': 'all_of',
        'any_of': 'any_of',
        'none_of': 'none_of',
    }

    def _require(self, config: Dict[str, Any], *keys: str) -> None:
        for key in keys:
            if config.get(key) is None:
                raise ValueError(f"'{key}' requerido para wait {config.get('type')}")

    def _wait_condition(self, config: Dict[str, Any]):
        """Construye la ExpectedCondition para un tipo de wait."""
        wait_type = config.get('type')

        if wait_type == 'element':
            self._require(config, 'selector')
            return EC.presence_of_element_located(self._resolve_by(config['selector']))
        if wait_type == 'clickable':
            self._require(config, 'selector')
            return EC.element_to_be_clickable(self._resolve_by(config['selector']))
        if wait_type == 'invisible':
            self._require(config, 'selector')
            return EC.invisibility_of_element_located(self._resolve_by(config['selector']))
        if wait_type == 'invisibility_of_element':
            self._require(config, 'selector')
            return EC.invisibility_of_element(self._find_element(config['selector']))
        if wait_type == 'visible':
            self._require(config, 'selector')
            return EC.visibility_of_element_located(self._resolve_by(config['selector']))
        if wait_type == 'visibility_of':
            self._require(config, 'selector')
            return EC.visibility_of(self._find_element(config['selector']))
        if wait_type == 'visibility_of_all_elements_located':
            self._require(config, 'selector')
            return EC.visibility_of_all_elements_located(self._resolve_by(config['selector']))
        if wait_type == 'visibility_of_any_elements_located':
            self._require(config, 'selector')
            return EC.visibility_of_any_elements_located(self._resolve_by(config['selector']))
        if wait_type == 'all_present':
            self._require(config, 'selector')
            return EC.presence_of_all_elements_located(self._resolve_by(config['selector']))
        if wait_type == 'text_present':
            self._require(config, 'selector', 'text')
            return EC.text_to_be_present_in_element(self._resolve_by(config['selector']), config['text'])
        if wait_type == 'text_present_value':
            self._require(config, 'selector', 'text')
            return EC.text_to_be_present_in_element_value(self._resolve_by(config['selector']), config['text'])
        if wait_type == 'text_to_be_present_in_element_attribute':
            self._require(config, 'selector', 'attribute', 'text')
            return EC.text_to_be_present_in_element_attribute(self._resolve_by(config['selector']), config['attribute'], config['text'])
        if wait_type == 'selected':
            self._require(config, 'selector')
            return EC.element_to_be_selected(self._find_element(config['selector']))
        if wait_type == 'element_selection_state_to_be':
            self._require(config, 'selector', 'selected')
            return EC.element_selection_state_to_be(self._find_element(config['selector']), bool(config['selected']))
        if wait_type == 'element_located_selection_state_to_be':
            self._require(config, 'selector', 'selected')
            return EC.element_located_selection_state_to_be(self._resolve_by(config['selector']), bool(config['selected']))
        if wait_type == 'staleness':
            self._require(config, 'selector')
            return EC.staleness_of(self._find_element(config['selector']))
        if wait_type == 'alert_present':
            return EC.alert_is_present()
        if wait_type == 'frame_available':
            self._require(config, 'selector')
            return EC.frame_to_be_available_and_switch_to_it(self._resolve_by(config['selector']))
        if wait_type == 'window_count':
            self._require(config, 'count')
            return EC.number_of_windows_to_be(int(config['count']))
        if wait_type == 'new_window':
            return EC.new_window_is_opened(list(self.driver.window_handles))
        if wait_type == 'url_changes':
            return EC.url_changes(config.get('from_url', self.driver.current_url))
        if wait_type == 'url_contains':
            fragment = config.get('url') or config.get('fragment')
            if not fragment:
                raise ValueError("'url' requerido para wait url_contains")
            return EC.url_contains(fragment)
        if wait_type == 'url_matches':
            self._require(config, 'pattern')
            return EC.url_matches(config['pattern'])
        if wait_type == 'url_to_be':
            self._require(config, 'url')
            return EC.url_to_be(config['url'])
        if wait_type == 'title_contains':
            self._require(config, 'title')
            return EC.title_contains(config['title'])
        if wait_type == 'title_is':
            self._require(config, 'title')
            return EC.title_is(config['title'])
        if wait_type == 'attribute_contains':
            self._require(config, 'selector', 'attribute')
            return EC.element_attribute_to_include(self._resolve_by(config['selector']), config['attribute'])
        if wait_type in ('all_of', 'any_of', 'none_of'):
            conditions = config.get('conditions') or []
            if not conditions:
                raise ValueError(f"'conditions' requerido para wait {wait_type}")
            built = [self._wait_condition(condition) for condition in conditions]
            return getattr(EC, wait_type)(*built)

        raise ValueError(f"Tipo de espera no soportado: {wait_type}")

    def _execute_wait(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Espera condiciones (tiempo o ExpectedConditions)."""
        wait_type = config.get('type', 'time')

        if wait_type == 'time':
            seconds = config.get('seconds', 1)
            time.sleep(seconds)
            result_key = config.get('id', 'waited')
            return {result_key: True, "success": True, "seconds": seconds}

        condition = self._wait_condition(config)
        WebDriverWait(self.driver, self.wait_timeout).until(condition)

        result_key = config.get('id', self.DEFAULT_WAIT_KEYS.get(wait_type, wait_type))
        result: Dict[str, Any] = {result_key: True, "success": True}
        if wait_type in ('url_changes', 'url_contains', 'url_matches', 'url_to_be'):
            result['url'] = self.driver.current_url
        elif wait_type in ('title_contains', 'title_is'):
            result['title'] = self.driver.title
        elif wait_type == 'all_present':
            result['count'] = len(self.driver.find_elements(*self._resolve_by(config['selector'])))
        return result

    def _execute_screenshot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Captura pantalla (de toda la página, o de un elemento si se pasa 'selector').

        encoding: 'file' (default, guarda en 'file'), 'base64' o 'png'.
        """
        encoding = config.get('encoding', 'file')
        selector = config.get('selector')

        if encoding in ('base64', 'png'):
            if selector:
                element = self._find_element(selector)
                value = element.screenshot_as_base64 if encoding == 'base64' else base64.b64encode(element.screenshot_as_png).decode('ascii')
            else:
                value = self.driver.get_screenshot_as_base64() if encoding == 'base64' else base64.b64encode(self.driver.get_screenshot_as_png()).decode('ascii')
            result_key = config.get('id', 'screenshot')
            return {result_key: value, "success": True, "encoding": encoding}

        file_path = config.get('file', f"screenshot_{int(time.time())}.png")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        if selector:
            element = self._find_element(selector)
            element.screenshot(file_path)
        else:
            self.driver.save_screenshot(file_path)

        result_key = config.get('id', 'screenshot')
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

        result_key = config.get('id', 'navigated')
        return {result_key: True, "success": True, "action": action}

    def _execute_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Información de la página actual: url, title, source."""
        info = {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "source": self.driver.page_source,
        }

        result_key = config.get('id', 'page')
        return {result_key: info, "success": True}

    def _execute_state(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Chequea el estado de un elemento: is_displayed, is_enabled, is_selected."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación state")

        try:
            element = self._find_element(selector)
        except ValueError:
            info = {"exists": False, "displayed": False, "enabled": False, "selected": False}
            result_key = config.get('id', 'state')
            return {result_key: info, "success": True}

        info = {
            "exists": True,
            "displayed": element.is_displayed(),
            "enabled": element.is_enabled(),
            "selected": element.is_selected(),
        }

        result_key = config.get('id', 'state')
        return {result_key: info, "success": True}

    def _execute_find(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Busca elementos. 'within' limita la busqueda a un contenedor."""
        selector = config.get('selector')
        multiple = config.get('multiple', False)
        attribute = config.get('attribute')
        within = config.get('within')

        if not selector:
            raise ValueError("Selector requerido para operación find")

        def describe(el):
            info = {"text": el.text, "tag": el.tag_name}
            if attribute:
                info["attribute"] = el.get_attribute(attribute)
            return info

        if multiple:
            by, value = self._resolve_by(selector)
            root = self._find_element(within) if within else self.driver
            elements = root.find_elements(by, value)
            result = [describe(el) for el in elements]
        else:
            element = self._find_element(selector, within=within)
            result = describe(element)

        result_key = config.get('id', 'found')
        return {result_key: result, "success": True}

    def _execute_submit(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Envía formulario."""
        selector = config.get('selector')

        if selector:
            element = self._find_element(selector)
            element.submit()
        else:
            self.driver.find_element(By.TAG_NAME, "body").submit()

        result_key = config.get('id', 'submitted')
        return {result_key: True, "success": True}

    def _execute_clear(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia campo."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación clear")

        element = self._find_element(selector)
        element.clear()

        result_key = config.get('id', 'cleared')
        return {result_key: True, "success": True}

    def _execute_select(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Selecciona/deselecciona opciones o lista las opciones de un <select>."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación select")

        element = self._find_element(selector)
        select = Select(element)
        action = config.get('action', 'select')
        result_key = config.get('id', 'selected')

        if action == 'select':
            value = config.get('value')
            text = config.get('text')
            index = config.get('index')
            if value:
                select.select_by_value(value)
            elif text:
                select.select_by_visible_text(text)
            elif index is not None:
                select.select_by_index(index)
            else:
                raise ValueError("Se requiere value, text o index para operación select")
            return {result_key: True, "success": True}

        if action == 'deselect_all':
            select.deselect_all()
            return {result_key: True, "success": True}
        if action == 'deselect_value':
            select.deselect_by_value(config['value'])
            return {result_key: True, "success": True}
        if action == 'deselect_text':
            select.deselect_by_visible_text(config['text'])
            return {result_key: True, "success": True}
        if action == 'deselect_index':
            select.deselect_by_index(config['index'])
            return {result_key: True, "success": True}
        if action == 'options':
            return {result_key: [option.text for option in select.options], "success": True}
        if action == 'selected':
            return {result_key: [option.text for option in select.all_selected_options], "success": True}
        if action == 'first_selected':
            return {result_key: select.first_selected_option.text, "success": True}

        raise ValueError(f"Acción de select no soportada: {action}")

    def _execute_hover(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Pasa el mouse sobre elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación hover")

        element = self._find_element(selector)
        ActionChains(self.driver).move_to_element(element).perform()

        result_key = config.get('id', 'hovered')
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

        result_key = config.get('id', 'dragged')
        return {result_key: True, "success": True}

    def _execute_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Imprime la página actual a PDF (comando 'Print Page' de WebDriver)."""
        file_path = config.get('file', f"page_{int(time.time())}.pdf")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        pdf_base64 = self.driver.print_page()
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(pdf_base64))

        result_key = config.get('id', 'pdf')
        return {result_key: file_path, "success": True}

    def _execute_dblclick(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Doble clic en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación dblclick")

        element = self._find_element(selector)
        ActionChains(self.driver).double_click(element).perform()

        result_key = config.get('id', 'dblclicked')
        return {result_key: True, "success": True}

    def _execute_rightclick(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Clic derecho (context click) en elemento."""
        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación rightclick")

        element = self._find_element(selector)
        ActionChains(self.driver).context_click(element).perform()

        result_key = config.get('id', 'rightclicked')
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

        result_key = config.get('id', 'keys_sent')
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
            if self.humanize and y:
                step = Humanize.scroll_step(self.humanize)
                remaining = y
                while remaining != 0:
                    delta = min(step, remaining) if remaining > 0 else max(-step, remaining)
                    self.driver.execute_script(f"window.scrollBy({x}, {delta});")
                    remaining -= delta
                    time.sleep(Humanize.between_operators_delay(self.humanize))
            else:
                self.driver.execute_script(f"window.scrollBy({x}, {y});")

        elif scroll_type == 'to_position':
            x = config.get('x', 0)
            y = config.get('y', 0)
            self.driver.execute_script(f"window.scrollTo({x}, {y});")

        else:
            raise ValueError(f"Tipo de scroll no soportado: {scroll_type}")

        result_key = config.get('id', 'scrolled')
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

        result_key = config.get('id', 'uploaded')
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

        result_key = config.get('id', 'downloaded')
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
            result_key = config.get('id', 'cookies')
            return {result_key: cookies, "success": True}

        elif action == 'add':
            if 'name' in config and 'value' in config:
                cookie = self._build_cookie_dict(config)
                self.driver.add_cookie(cookie)
                result_key = config.get('id', 'cookie_added')
                return {result_key: True, "success": True}

            elif 'cookies' in config:
                cookies = config['cookies']
                if not isinstance(cookies, list):
                    raise ValueError("cookies debe ser un array")

                added_count = 0
                for cookie_data in cookies:
                    cookie = self._build_cookie_dict(cookie_data)
                    self.driver.add_cookie(cookie)
                    added_count += 1

                result_key = config.get('id', 'cookies_added')
                return {result_key: added_count, "success": True}

            else:
                raise ValueError("Se requiere name/value o cookies array para add")

        elif action == 'delete':
            name = config.get('name')
            if not name:
                raise ValueError("Nombre de cookie requerido para delete")

            self.driver.delete_cookie(name)
            result_key = config.get('id', 'cookie_deleted')
            return {result_key: True, "success": True}

        elif action == 'clear':
            self.driver.delete_all_cookies()
            result_key = config.get('id', 'cookies_cleared')
            return {result_key: True, "success": True}

        elif action == 'get_by_name':
            name = config.get('name')
            if not name:
                raise ValueError("Nombre de cookie requerido para get_by_name")

            cookie = self.driver.get_cookie(name)
            result_key = config.get('id', 'cookie_by_name')
            return {result_key: cookie, "success": True}

        elif action == 'get_by_domain':
            domain = config.get('domain')
            if not domain:
                raise ValueError("Dominio requerido para get_by_domain")

            all_cookies = self.driver.get_cookies()
            domain_cookies = [cookie for cookie in all_cookies if cookie.get("domain") == domain]
            result_key = config.get('id', 'cookies_by_domain')
            return {result_key: domain_cookies, "success": True}

        else:
            raise ValueError(f"Acción de cookies no soportada: {action}")

    def _build_cookie_dict(self, cookie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construye diccionario de cookie con propiedades completas."""
        cookie = {
            'name': cookie_data['name'],
            'value': cookie_data['value']
        }

        if 'domain' in cookie_data:
            cookie['domain'] = cookie_data['domain']
        if 'path' in cookie_data:
            cookie['path'] = cookie_data['path']
        if 'expiry' in cookie_data:
            expiry = cookie_data['expiry']
            if isinstance(expiry, str):
                try:
                    dt = datetime.datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                    cookie['expiry'] = int(dt.timestamp())
                except (ValueError, TypeError):
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
        result_key = config.get('id', 'window_action')

        if action == 'switch':
            window_handle = config.get('handle')
            if window_handle:
                self.driver.switch_to.window(window_handle)
            else:
                self.driver.switch_to.window(self.driver.window_handles[-1])

        elif action == 'close':
            self.driver.close()

        elif action == 'maximize':
            self.driver.maximize_window()

        elif action == 'minimize':
            self.driver.minimize_window()

        elif action == 'fullscreen':
            self.driver.fullscreen_window()

        elif action == 'new':
            self.driver.switch_to.new_window(config.get('type', 'tab'))

        elif action == 'handles':
            return {result_key: self.driver.window_handles, "success": True, "action": action}

        elif action == 'rect':
            return {result_key: self.driver.get_window_rect(), "success": True, "action": action}

        elif action == 'set_rect':
            rect = {k: config[k] for k in ('x', 'y', 'width', 'height') if k in config}
            self.driver.set_window_rect(**rect)

        elif action == 'position':
            return {result_key: self.driver.get_window_position(), "success": True, "action": action}

        elif action == 'set_position':
            self.driver.set_window_position(config.get('x'), config.get('y'))

        elif action == 'size':
            return {result_key: self.driver.get_window_size(), "success": True, "action": action}

        elif action == 'set_size':
            self.driver.set_window_size(config.get('width'), config.get('height'))

        else:
            raise ValueError(f"Acción de ventana no soportada: {action}")

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
                self.driver.switch_to.default_content()

        elif action == 'parent':
            self.driver.switch_to.parent_frame()

        elif action == 'default':
            self.driver.switch_to.default_content()

        else:
            raise ValueError(f"Acción de frame no soportada: {action}")

        result_key = config.get('id', 'frame_action')
        return {result_key: True, "success": True, "action": action}

    def _execute_alert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar alertas."""
        action = config.get('action', 'accept')
        text_value = None

        try:
            alert = self.driver.switch_to.alert

            if action == 'accept':
                alert.accept()
            elif action == 'dismiss':
                alert.dismiss()
            elif action == 'send_keys':
                text = config.get('text', '')
                alert.send_keys(text)
            elif action in ('text', 'get_text'):
                text_value = alert.text
            else:
                raise ValueError(f"Acción de alerta no soportada: {action}")

        except NoAlertPresentException:
            pass

        result_key = config.get('id', 'alert_action')
        if action in ('text', 'get_text'):
            return {result_key: text_value, "success": True, "action": action}
        return {result_key: True, "success": True, "action": action}

    def _execute_quit(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Cierra la sesión del navegador a mitad de script. La próxima
        operación selenium que se ejecute levanta un driver nuevo."""
        self.quit()

        result_key = config.get('id', 'quit')
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
            result_key = config.get('id', 'storage_value')
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
            result_key = config.get('id', 'storage')
            return {result_key: value, "success": True}

        elif action == 'set':
            key = config.get('key')
            value = config.get('value')
            if not key:
                raise ValueError("'key' requerido para storage set")
            self.driver.execute_script(
                f"window.{js_storage}.setItem(arguments[0], arguments[1]);", key, value
            )
            result_key = config.get('id', 'storage_set')
            return {result_key: True, "success": True}

        elif action == 'remove':
            key = config.get('key')
            if not key:
                raise ValueError("'key' requerido para storage remove")
            self.driver.execute_script(
                f"window.{js_storage}.removeItem(arguments[0]);", key
            )
            result_key = config.get('id', 'storage_removed')
            return {result_key: True, "success": True}

        elif action == 'clear':
            self.driver.execute_script(f"window.{js_storage}.clear();")
            result_key = config.get('id', 'storage_cleared')
            return {result_key: True, "success": True}

        else:
            raise ValueError(f"Acción de storage no soportada: {action}")

    def _execute_timeouts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura timeouts de page load / script / implicit."""
        if 'page_load' in config:
            self.driver.set_page_load_timeout(config['page_load'])
        if 'script' in config:
            self.driver.set_script_timeout(config['script'])
        if 'implicit' in config:
            self.implicit_wait = config['implicit']
            self.driver.implicitly_wait(config['implicit'])
        result_key = config.get('id', 'timeouts')
        return {result_key: True, "success": True}

    def _execute_actions(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una secuencia de acciones de bajo nivel (ActionChains).

        'sequence' es una lista de pasos, cada uno con 'type' y sus
        parametros: move_to_element, move_by_offset,
        move_to_element_with_offset, click, click_and_hold, release,
        drag_and_drop, drag_and_drop_by_offset, scroll_by_amount,
        scroll_from_origin, key_down, key_up, send_keys, pause.
        """
        sequence = config.get('sequence')
        if not sequence:
            raise ValueError("'sequence' requerido para operación actions")

        chains = ActionChains(self.driver)
        for step in sequence:
            step_type = step.get('type')
            selector = step.get('selector')

            if step_type == 'move_to_element':
                chains.move_to_element(self._find_element(selector))
            elif step_type == 'move_by_offset':
                chains.move_by_offset(step.get('x', 0), step.get('y', 0))
            elif step_type == 'move_to_element_with_offset':
                chains.move_to_element_with_offset(self._find_element(selector), step.get('x', 0), step.get('y', 0))
            elif step_type == 'click':
                chains.click(self._find_element(selector) if selector else None)
            elif step_type == 'click_and_hold':
                chains.click_and_hold(self._find_element(selector) if selector else None)
            elif step_type == 'release':
                chains.release(self._find_element(selector) if selector else None)
            elif step_type == 'drag_and_drop':
                chains.drag_and_drop(self._find_element(step['source']), self._find_element(step['target']))
            elif step_type == 'drag_and_drop_by_offset':
                chains.drag_and_drop_by_offset(self._find_element(selector), step.get('x', 0), step.get('y', 0))
            elif step_type == 'scroll_by_amount':
                chains.scroll_by_amount(step.get('x', 0), step.get('y', 0))
            elif step_type == 'scroll_from_origin':
                if step.get('origin'):
                    scroll_origin = ScrollOrigin.from_element(self._find_element(step['origin']))
                else:
                    scroll_origin = ScrollOrigin.from_viewport(step.get('origin_x', 0), step.get('origin_y', 0))
                chains.scroll_from_origin(scroll_origin, step.get('x', 0), step.get('y', 0))
            elif step_type == 'key_down':
                chains.key_down(self._resolve_key(step['key']), self._find_element(selector) if selector else None)
            elif step_type == 'key_up':
                chains.key_up(self._resolve_key(step['key']), self._find_element(selector) if selector else None)
            elif step_type == 'send_keys':
                keys = [self._resolve_key(k) for k in (step.get('keys') if isinstance(step.get('keys'), list) else [step.get('keys')])]
                if selector:
                    chains.send_keys_to_element(self._find_element(selector), *keys)
                else:
                    chains.send_keys(*keys)
            elif step_type == 'pause':
                chains.pause(step.get('seconds', 1))
            else:
                raise ValueError(f"Paso de actions no soportado: {step_type}")

        chains.perform()
        result_key = config.get('id', 'actions')
        return {result_key: True, "success": True, "steps": len(sequence)}

    def _resolve_key(self, value):
        """Resuelve un nombre de tecla especial (ENTER, TAB, ...) o deja el string."""
        if not isinstance(value, str):
            return value
        return getattr(Keys, value.upper(), value)

    def _execute_element(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Propiedades/atributos de un elemento: property, dom_attribute,
        css, rect, size, location, aria_role, accessible_name, text, tag,
        o 'active' (elemento activo, sin selector)."""
        action = config.get('action')

        if action == 'active':
            element = self.driver.switch_to.active_element
            result_key = config.get('id', 'active')
            return {result_key: {"tag": element.tag_name, "text": element.text}, "success": True, "action": action}

        selector = config.get('selector')
        if not selector:
            raise ValueError("Selector requerido para operación element")
        element = self._find_element(selector)

        name = config.get('name')
        if action == 'property':
            value = element.get_property(name)
        elif action == 'dom_attribute':
            value = element.get_dom_attribute(name)
        elif action == 'css':
            value = element.value_of_css_property(name)
        elif action == 'rect':
            value = element.rect
        elif action == 'size':
            value = element.size
        elif action == 'location':
            value = element.location
        elif action == 'aria_role':
            value = element.aria_role
        elif action == 'accessible_name':
            value = element.accessible_name
        elif action == 'text':
            value = element.text
        elif action == 'tag':
            value = element.tag_name
        elif action == 'parent':
            parent = element.find_element(By.XPATH, '..')
            value = {"tag": parent.tag_name, "text": parent.text}
        elif action == 'scrolled_location':
            value = element.location_once_scrolled_into_view
        elif action == 'id':
            value = element.id
        else:
            raise ValueError(f"Acción de element no soportada: {action}")

        result_key = config.get('id', action or 'element')
        return {result_key: value, "success": True, "action": action}

    def _execute_shadow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Busca un elemento dentro del shadow DOM de 'host'."""
        host_selector = config.get('host')
        inner_selector = config.get('selector')
        if not host_selector or not inner_selector:
            raise ValueError("'host' y 'selector' requeridos para operación shadow")

        host = self._find_element(host_selector)
        root = host.shadow_root
        by, value = self._resolve_by(inner_selector)
        element = root.find_element(by, value)

        info = {"text": element.text, "tag": element.tag_name}
        attribute = config.get('attribute')
        if attribute:
            info["attribute"] = element.get_attribute(attribute)
        result_key = config.get('id', 'shadow')
        return {result_key: info, "success": True}

    def _execute_cdp(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un comando CDP (solo navegadores Chromium)."""
        if not self._is_chromium():
            raise ValueError("CDP solo esta soportado en navegadores Chromium (chrome/edge)")
        command = config.get('command')
        if not command:
            raise ValueError("'command' requerido para operación cdp")
        result = self.driver.execute_cdp_cmd(command, config.get('params', {}) or {})
        result_key = config.get('id', 'cdp')
        return {result_key: result, "success": True}

    def _execute_network(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Condiciones de red (solo navegadores Chromium)."""
        if not self._is_chromium():
            raise ValueError("'network' solo esta soportado en navegadores Chromium (chrome/edge)")
        action = config.get('action', 'get')
        result_key = config.get('id', 'network')
        if action == 'get':
            return {result_key: self.driver.get_network_conditions(), "success": True}
        if action == 'set':
            conditions = {k: config[k] for k in ('offline', 'latency', 'download_throughput', 'upload_throughput') if k in config}
            self.driver.set_network_conditions(**conditions)
            return {result_key: True, "success": True}
        raise ValueError(f"Acción de network no soportada: {action}")

    def _is_chromium(self) -> bool:
        name = (getattr(self.driver, 'name', '') or '').lower()
        return name in ('chrome', 'chromium', 'msedge', 'chrome-headless-shell', 'edge')

    def _execute_capabilities(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Devuelve las capabilities de la sesion y el nombre del navegador."""
        info = {"browserName": self.driver.name, "capabilities": self.driver.capabilities}
        result_key = config.get('id', 'capabilities')
        return {result_key: info, "success": True}

    def _execute_storage_state(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta/importa cookies + localStorage + sessionStorage."""
        action = config.get('action', 'export')
        result_key = config.get('id', 'storage_state')

        if action == 'export':
            state = {
                "cookies": self.driver.get_cookies(),
                "localStorage": self._read_web_storage('localStorage'),
                "sessionStorage": self._read_web_storage('sessionStorage'),
            }
            file_path = config.get('file')
            if file_path:
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f)
                return {result_key: file_path, "success": True}
            return {result_key: state, "success": True}

        if action == 'import':
            state = config.get('state')
            if state is None and config.get('file'):
                with open(config['file'], 'r', encoding='utf-8') as f:
                    state = json.load(f)
            state = state or {}
            for cookie in state.get('cookies', []) or []:
                self.driver.add_cookie(cookie)
            for storage_name in ('localStorage', 'sessionStorage'):
                data = state.get(storage_name) or {}
                if data:
                    try:
                        self.driver.execute_script(
                            f"var d=arguments[0];for(var k in d){{{storage_name}.setItem(k,d[k]);}}", data
                        )
                    except Exception as e:  # noqa: BLE001 - origen opaco (data:, about:)
                        Output.Console(self.plugin_name, f"ADVERTENCIA: no se pudo escribir {storage_name}: {e}")
            return {result_key: True, "success": True}

        raise ValueError(f"Acción de storage_state no soportada: {action}")

    def _read_web_storage(self, storage_name: str) -> Dict[str, Any]:
        """Lee localStorage/sessionStorage; devuelve {} si el origen no lo permite."""
        try:
            return self.driver.execute_script(
                f"var o={{}};for(var i=0;i<{storage_name}.length;i++){{var k={storage_name}.key(i);o[k]={storage_name}.getItem(k);}}return o;"
            )
        except Exception as e:  # noqa: BLE001 - origen opaco (data:, about:)
            Output.Console(self.plugin_name, f"ADVERTENCIA: no se pudo leer {storage_name}: {e}")
            return {}

    CHALLENGE_MARKERS = {
        'cloudflare': ['just a moment', 'attention required', 'checking your browser', '__cf_chl', 'cf-challenge', 'cf_chl_opt'],
        'akamai': ['access denied', '_abck', 'akamai bot manager'],
        'datadome': ['datadome', 'dd_cookie'],
        'perimeterx': ['px-captcha', 'perimeterx', '_px'],
    }

    def _detect_challenge(self) -> Optional[str]:
        try:
            blob = ((self.driver.title or '') + ' ' + (self.driver.page_source or '')).lower()
        except Exception:
            return None
        for provider, markers in self.CHALLENGE_MARKERS.items():
            if any(marker in blob for marker in markers):
                return provider
        return None

    def _execute_challenge(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta (y opcionalmente espera a que desaparezca) un challenge anti-bot."""
        action = config.get('action', 'detect')
        result_key = config.get('id', 'challenge')

        if action == 'detect':
            provider = self._detect_challenge()
            return {result_key: {"detected": provider is not None, "provider": provider}, "success": True}

        if action == 'wait':
            timeout = config.get('timeout', self.wait_timeout)
            deadline = time.time() + timeout
            while time.time() < deadline:
                provider = self._detect_challenge()
                if provider is None:
                    return {result_key: {"detected": False, "provider": None}, "success": True}
                time.sleep(1)
            provider = self._detect_challenge()
            return {
                result_key: {"detected": provider is not None, "provider": provider},
                "success": False,
                "error": f"Challenge no resuelto: {provider}",
            }

        raise ValueError(f"Acción de challenge no soportada: {action}")

    def _execute_bidi(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comandos WebDriver BiDi (requiere meta.bidi=true)."""
        if not self.driver.caps.get('webSocketUrl'):
            raise ValueError("BiDi no habilitado; usar meta.bidi=true")

        action = config.get('action')
        result_key = config.get('id', 'bidi')
        context = config.get('context') or self.driver.current_window_handle

        if action == 'execute':
            args = config.get('args') or []
            return {result_key: self.driver.script.execute(config['function'], *args), "success": True}
        if action == 'navigate':
            return {result_key: self.driver.browsing_context.navigate(context, config['url'], config.get('wait')), "success": True}
        if action == 'reload':
            return {result_key: self.driver.browsing_context.reload(context, config.get('ignore_cache'), config.get('wait')), "success": True}
        if action == 'screenshot':
            return {result_key: self.driver.browsing_context.capture_screenshot(context, origin=config.get('origin', 'viewport')), "success": True}
        if action == 'print':
            return {result_key: self.driver.browsing_context.print(context), "success": True}
        if action == 'set_permission':
            self.driver.permissions.set_permission(config['descriptor'], config['state'], config['origin'])
            return {result_key: True, "success": True}
        if action == 'cookies':
            result = self.driver.storage.get_cookies()
            return {result_key: self._to_jsonable(getattr(result, 'cookies', result)), "success": True}
        if action == 'block':
            def _block(request):
                request.fail_request()
            patterns = [Stealth.url_pattern(p) for p in (config.get('patterns') or [])]
            for pattern in patterns:
                self.driver.network.add_request_handler('before_request', _block, url_patterns=[pattern])
            return {result_key: True, "success": True}
        if action == 'add_auth':
            self.driver.network.add_auth_handler(config['username'], config.get('password', ''))
            return {result_key: True, "success": True}

        if action == 'context_create':
            return {result_key: self.driver.browsing_context.create(config.get('type', 'tab'), config.get('reference'), config.get('background', False), config.get('user_context')), "success": True}
        if action == 'context_close':
            self.driver.browsing_context.close(context, config.get('prompt_unload', False))
            return {result_key: True, "success": True}
        if action == 'context_activate':
            self.driver.browsing_context.activate(context)
            return {result_key: True, "success": True}
        if action == 'context_tree':
            return {result_key: self._to_jsonable(self.driver.browsing_context.get_tree(config.get('max_depth'), config.get('root'))), "success": True}
        if action == 'locate_nodes':
            nodes = self.driver.browsing_context.locate_nodes(context, config['locator'], config.get('max_node_count'))
            return {result_key: self._to_jsonable(nodes), "success": True}
        if action == 'set_viewport':
            self.driver.browsing_context.set_viewport(context=context, viewport=config.get('viewport'), device_pixel_ratio=config.get('device_pixel_ratio'))
            return {result_key: True, "success": True}
        if action == 'traverse_history':
            return {result_key: self.driver.browsing_context.traverse_history(context, int(config.get('delta', 0))), "success": True}
        if action == 'handle_prompt':
            self.driver.browsing_context.handle_user_prompt(context, config.get('accept'), config.get('text'))
            return {result_key: True, "success": True}

        if action == 'emulate_geolocation':
            from selenium.webdriver.common.bidi.emulation import GeolocationCoordinates
            coordinates = GeolocationCoordinates(
                latitude=float(config['latitude']),
                longitude=float(config['longitude']),
                accuracy=float(config.get('accuracy', 1.0)),
            )
            self.driver.emulation.set_geolocation_override(coordinates=coordinates, contexts=[context])
            return {result_key: True, "success": True}

        if action == 'user_context_create':
            return {result_key: self.driver.browser.create_user_context(), "success": True}
        if action == 'user_contexts':
            return {result_key: self.driver.browser.get_user_contexts(), "success": True}
        if action == 'user_context_remove':
            self.driver.browser.remove_user_context(config['user_context'])
            return {result_key: True, "success": True}
        if action == 'client_windows':
            return {result_key: self._to_jsonable(self.driver.browser.get_client_windows()), "success": True}

        if action == 'extension_install':
            result = self.driver.webextension.install(path=config['path'])
            return {result_key: self._to_jsonable(result), "success": True}
        if action == 'extension_uninstall':
            self.driver.webextension.uninstall(config['extension'])
            return {result_key: True, "success": True}

        if action == 'pin':
            return {result_key: self.driver.script.pin(config['script']), "success": True}
        if action == 'unpin':
            self.driver.script.unpin(config['script'])
            return {result_key: True, "success": True}
        if action == 'pinned':
            return {result_key: self._to_jsonable(self.driver.get_pinned_scripts()), "success": True}

        if action == 'input_keys':
            from selenium.webdriver.common.bidi.input import KeySourceActions, KeyDownAction, KeyUpAction
            actions = []
            for char in config.get('keys', ''):
                actions.append(KeyDownAction(value=char))
                actions.append(KeyUpAction(value=char))
            self.driver.input.perform_actions(context, [KeySourceActions(id='keyboard', actions=actions)])
            return {result_key: True, "success": True}
        if action == 'input_release':
            self.driver.input.release_actions(context)
            return {result_key: True, "success": True}

        raise ValueError(f"Acción de bidi no soportada: {action}")

    def _to_jsonable(self, obj: Any) -> Any:
        """Convierte objetos BiDi (no serializables) a dict/list/str."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {key: self._to_jsonable(value) for key, value in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._to_jsonable(item) for item in obj]
        if hasattr(obj, '__dict__'):
            return {key: self._to_jsonable(value) for key, value in vars(obj).items() if not key.startswith('_')}
        return str(obj)

    def _execute_downloads(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """API de descargas de WebDriver (requiere meta.downloads=true)."""
        if 'se:downloadsEnabled' not in self.driver.capabilities:
            raise ValueError("Descargas no habilitadas; usar meta.downloads=true")
        action = config.get('action', 'list')
        result_key = config.get('id', 'downloads')
        if action == 'list':
            return {result_key: self.driver.get_downloadable_files(), "success": True}
        if action == 'get':
            self.driver.download_file(config['name'], config['target'])
            return {result_key: True, "success": True}
        if action == 'clear':
            self.driver.delete_downloadable_files()
            return {result_key: True, "success": True}
        raise ValueError(f"Acción de downloads no soportada: {action}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_by(self, selector: str) -> tuple:
        """
        Determina el mecanismo de localización (By.XPATH o By.CSS_SELECTOR)
        a partir del selector recibido.

        Convenciones soportadas:
          - Prefijo explícito 'xpath=...' -> XPath, sin el prefijo.
          - Selectores que empiezan con '//', './/' o '(' -> XPath.
          - Cualquier otro caso -> CSS selector.
        """
        if selector.startswith('xpath='):
            return By.XPATH, selector[len('xpath='):]
        if selector.startswith(('//', './/', '(')):
            return By.XPATH, selector
        return By.CSS_SELECTOR, selector

    def _find_element(self, selector: str, within: Optional[str] = None):
        """Encuentra elemento con manejo de errores. Si 'within' se pasa,
        busca dentro de ese elemento contenedor."""
        by, value = self._resolve_by(selector)
        try:
            if within:
                root = self._find_element(within)
                return root.find_element(by, value)
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


__all__ = ['BrowserSession', 'SUPPORTED_BROWSERS']
