"""
Capa de sesion: fabrica de drivers
==================================

Concentra la definicion de navegadores soportados y la creacion del
webdriver (options, service, driver-manager). No conoce Sugar ni IPC;
solo recibe un SessionSpec del kernel. Los paths de los drivers los
resuelve webdriver-manager, nunca se hardcodean.
"""

import os
import random
import sys
import threading
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from Sugar.Lang.Utils.Output import Output

# Bootstrap: permite importar 'kernel'/'session' tanto si el plugin se
# carga como paquete (selenium_plugin.src.*) como si se carga como modulo
# top-level (tests con src/ en sys.path).
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec
from session import Stealth, Logging
from session.Support import unsupported


# Navegadores soportados
SUPPORTED_BROWSERS: Dict[str, Dict[str, Any]] = {
    'chrome': {
        'name': 'Chrome',
        'service': ChromeService,
        'options': ChromeOptions,
        'driver_manager': ChromeDriverManager,
        'headless_support': True,
        'detach_support': True,
        'platforms': ['linux', 'windows', 'macos'],
    },
    'firefox': {
        'name': 'Firefox',
        'service': FirefoxService,
        'options': FirefoxOptions,
        'driver_manager': GeckoDriverManager,
        'headless_support': True,
        'detach_support': False,
        'platforms': ['linux', 'windows', 'macos'],
    },
    'edge': {
        'name': 'Edge',
        'service': EdgeService,
        'options': EdgeOptions,
        'driver_manager': EdgeChromiumDriverManager,
        'headless_support': True,
        'detach_support': True,
        'platforms': ['linux', 'windows', 'macos'],
    },
}


FIREFOX_UNSUPPORTED_FLAGS = {'--no-sandbox', '--disable-dev-shm-usage'}

# Parchea navigator.webdriver antes de que corran los scripts de la pagina.
# Solo aplicable en Chromium (via CDP).
ANTI_DETECTION_SCRIPT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"


class BrowserFactory:
    """Crea un webdriver a partir de un SessionSpec."""

    @staticmethod
    def create(spec: SessionSpec, plugin_name: str = 'Selenium') -> Tuple[Any, Dict[str, Any]]:
        """Crea el driver, registrando cualquier fallo con contexto."""
        try:
            return BrowserFactory._create(spec, plugin_name)
        except Exception as e:
            Logging.log_failure(plugin_name, f"crear driver '{spec.browser}'", e, spec.log_file)
            raise

    @staticmethod
    def _create(spec: SessionSpec, plugin_name: str = 'Selenium') -> Tuple[Any, Dict[str, Any]]:
        browser_name = spec.browser
        if browser_name not in SUPPORTED_BROWSERS:
            raise ValueError(f"Navegador no soportado: {browser_name}")

        browser_config = SUPPORTED_BROWSERS[browser_name]
        options = browser_config['options']()
        BrowserFactory._apply_bidi(options, spec, plugin_name)
        BrowserFactory._apply_downloads(options, spec, plugin_name)
        window_size = BrowserFactory._apply_browser_options(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_prefs(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_profile(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_compat_options(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_chromium_options(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_anti_detection_options(options, spec, browser_name, plugin_name)
        BrowserFactory._set_no_proxy()

        service_kwargs = BrowserFactory._service_kwargs(browser_name)
        driver_path = BrowserFactory._resolve_driver_path(spec, browser_config, plugin_name)

        Output.Console(plugin_name, f"DEBUG: Creando driver de {browser_config['name']}...")
        driver_class = getattr(webdriver, browser_config['name'])
        service = browser_config['service'](executable_path=driver_path, **service_kwargs)
        driver = driver_class(service=service, options=options)
        driver.implicitly_wait(spec.implicit_wait)

        BrowserFactory._install_firefox_addons(driver, spec, browser_name, plugin_name)
        BrowserFactory._install_anti_detection(driver, spec, browser_name, plugin_name)
        Stealth.install(driver, spec, browser_name, plugin_name)

        if window_size:
            driver.set_window_size(
                window_size.get('width', 1280), window_size.get('height', 720)
            )
            Output.Console(plugin_name, f"DEBUG: Tamano de ventana aplicado: {window_size}")

        BrowserFactory._apply_humanized_window(driver, spec, plugin_name)

        Output.Console(plugin_name, f"Driver {browser_config['name']} inicializado correctamente")
        return driver, browser_config

    @staticmethod
    def _apply_humanized_window(driver, spec: SessionSpec, plugin_name: str) -> None:
        """Tamano de ventana aleatorio dentro de un rango (humanize)."""
        humanize = spec.humanize or {}
        width_range = humanize.get('window_width_range')
        height_range = humanize.get('window_height_range')
        if not (width_range and height_range):
            return
        width = random.randint(int(width_range[0]), int(width_range[1]))
        height = random.randint(int(height_range[0]), int(height_range[1]))
        driver.set_window_size(width, height)
        Output.Console(plugin_name, f"DEBUG: Ventana aleatoria: {width}x{height}")

    @staticmethod
    def _apply_browser_options(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> Optional[Dict[str, int]]:
        headless = spec.headless
        custom_options = spec.options

        # El detach lo maneja el keeper (software), no la opcion nativa de
        # Chromium: asi es uniforme entre navegadores y driver.quit()
        # realmente cierra el browser.
        if browser_name == 'chrome':
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        elif browser_name == 'firefox':
            if headless:
                options.add_argument('--headless')

        elif browser_name == 'edge':
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')

        # Firefox no entiende flags estilo Chromium: '--no-sandbox' no
        # existe, y '--width=N'/'--height=N' (con '=') rompen el arranque
        # de Marionette porque espera '-width N' con espacio. Para tamano
        # de ventana usamos driver.set_window_size().
        window_size = None
        for option in custom_options:
            key, _, value = option.partition('=')
            if key in ('--width', '--height') and value:
                window_size = window_size or {}
                window_size['width' if key == '--width' else 'height'] = int(value)
                Output.Console(plugin_name, f"DEBUG: Opcion '{option}' aplicada como tamano de ventana")
                continue
            if browser_name == 'firefox' and key in FIREFOX_UNSUPPORTED_FLAGS:
                Output.Console(plugin_name, f"DEBUG: Opcion '{option}' ignorada, no soportada por Firefox")
                continue
            options.add_argument(option)
            Output.Console(plugin_name, f"DEBUG: Agregada opcion: {option}")

        return window_size

    @staticmethod
    def _apply_prefs(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        custom_prefs = dict(spec.prefs)

        # Por defecto, que Firefox no intente usar el proxy configurado a
        # nivel sistema/escritorio (network.proxy.type=5 es el default de
        # Firefox: "usar la configuracion del sistema").
        if browser_name == 'firefox' and 'network.proxy.type' not in custom_prefs:
            custom_prefs = {**custom_prefs, 'network.proxy.type': 0}

        if custom_prefs and hasattr(options, 'set_preference'):
            for pref_key, pref_value in custom_prefs.items():
                options.set_preference(pref_key, pref_value)
                Output.Console(plugin_name, f"DEBUG: Agregada preferencia: {pref_key}={pref_value}")
        elif custom_prefs:
            unsupported(spec, plugin_name, f"'prefs' no soportado para navegador {browser_name}, ignorado")

    @staticmethod
    def _apply_profile(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        """Carga un perfil de usuario existente.

        Chrome/Edge usan el flag --user-data-dir; Firefox no tiene flag
        equivalente y necesita options.profile = FirefoxProfile(ruta).
        Si no hay 'profile' pero si 'profiles' (pool), se elige uno segun
        profile_strategy.
        """
        profile = BrowserFactory._effective_profile(spec)
        if not profile:
            return
        if not os.path.isdir(profile):
            raise ValueError(f"Perfil de usuario no encontrado: {profile}")

        if browser_name == 'firefox':
            options.profile = profile
        elif browser_name in ('chrome', 'edge'):
            options.add_argument(f'--user-data-dir={profile}')
        else:
            unsupported(spec, plugin_name, f"'profile' no soportado para navegador {browser_name}, ignorado")
            return
        Output.Console(plugin_name, f"DEBUG: Perfil de usuario aplicado: {profile}")

    _profile_counter = 0
    _profile_lock = threading.Lock()

    @staticmethod
    def _effective_profile(spec: SessionSpec) -> Optional[str]:
        if spec.profile:
            return spec.profile
        if not spec.profiles:
            return None
        if spec.profile_strategy == 'random':
            return random.choice(spec.profiles)
        if spec.profile_strategy == 'round_robin':
            with BrowserFactory._profile_lock:
                index = BrowserFactory._profile_counter % len(spec.profiles)
                BrowserFactory._profile_counter += 1
            return spec.profiles[index]
        return spec.profiles[0]

    @staticmethod
    def _apply_compat_options(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        """Opciones comunes a todos los navegadores, mapeadas al equivalente
        de cada motor (flags en Chromium, prefs en Firefox)."""
        if spec.binary:
            options.binary_location = spec.binary
            Output.Console(plugin_name, f"DEBUG: Binario de navegador: {spec.binary}")

        if spec.user_agent:
            BrowserFactory._apply_user_agent(options, spec.user_agent, browser_name, plugin_name, spec)

        if spec.accept_language and browser_name == 'firefox':
            options.set_preference('intl.accept_languages', spec.accept_language)

        if spec.proxy:
            BrowserFactory._apply_proxy(options, spec.proxy, browser_name, plugin_name, spec)

        BrowserFactory._apply_extensions(options, spec, browser_name, plugin_name)
        BrowserFactory._apply_pref_maps(options, spec, browser_name, plugin_name)

    @staticmethod
    def _apply_bidi(options, spec: SessionSpec, plugin_name: str) -> None:
        """Habilita la capability webSocketUrl para conectar por BiDi."""
        if not spec.bidi:
            return
        try:
            options.set_capability('webSocketUrl', True)
            Output.Console(plugin_name, "DEBUG: BiDi habilitado (webSocketUrl)")
        except Exception as e:  # noqa: BLE001
            Output.Console(plugin_name, f"ADVERTENCIA: no se pudo habilitar BiDi: {e}")

    @staticmethod
    def _apply_downloads(options, spec: SessionSpec, plugin_name: str) -> None:
        """Habilita la API de descargas de WebDriver (se:downloadsEnabled)."""
        if not spec.downloads:
            return
        try:
            options.set_capability('se:downloadsEnabled', True)
            Output.Console(plugin_name, "DEBUG: Descargas WebDriver habilitadas (se:downloadsEnabled)")
        except Exception as e:  # noqa: BLE001
            Output.Console(plugin_name, f"ADVERTENCIA: no se pudo habilitar downloads: {e}")

    @staticmethod
    def _apply_user_agent(options, user_agent: str, browser_name: str, plugin_name: str, spec: Optional[SessionSpec] = None) -> None:
        if browser_name in ('chrome', 'edge'):
            options.add_argument(f'--user-agent={user_agent}')
        elif browser_name == 'firefox':
            options.set_preference('general.useragent.override', user_agent)
        else:
            unsupported(spec, plugin_name, f"'user_agent' no soportado para navegador {browser_name}, ignorado")
            return
        Output.Console(plugin_name, f"DEBUG: User-Agent aplicado: {user_agent}")

    @staticmethod
    def _apply_proxy(options, proxy: str, browser_name: str, plugin_name: str, spec: Optional[SessionSpec] = None) -> None:
        parsed = urlparse(proxy if '://' in proxy else f'http://{proxy}')
        host = parsed.hostname
        port = parsed.port
        scheme = (parsed.scheme or 'http').lower()
        if not host or not port:
            raise ValueError(f"Proxy invalido (se espera scheme://host:port): {proxy}")
        if parsed.username:
            Output.Console(plugin_name, "ADVERTENCIA: proxy con credenciales: no soportado de forma nativa, se omiten usuario/password")

        if browser_name in ('chrome', 'edge'):
            options.add_argument(f'--proxy-server={scheme}://{host}:{port}')
        elif browser_name == 'firefox':
            prefs = {'network.proxy.type': 1}
            if scheme in ('socks', 'socks4', 'socks5'):
                prefs['network.proxy.socks'] = host
                prefs['network.proxy.socks_port'] = port
                prefs['network.proxy.socks_version'] = 4 if scheme == 'socks4' else 5
            else:
                prefs.update({
                    'network.proxy.http': host,
                    'network.proxy.http_port': port,
                    'network.proxy.ssl': host,
                    'network.proxy.ssl_port': port,
                    'network.proxy.share_proxy_settings': True,
                })
            for key, value in prefs.items():
                options.set_preference(key, value)
        else:
            unsupported(spec, plugin_name, f"'proxy' no soportado para navegador {browser_name}, ignorado")
            return
        Output.Console(plugin_name, f"DEBUG: Proxy aplicado: {scheme}://{host}:{port}")

    @staticmethod
    def _apply_extensions(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        if not spec.extensions:
            return
        for extension in spec.extensions:
            if not os.path.exists(extension):
                raise ValueError(f"Extension no encontrada: {extension}")
        if browser_name in ('chrome', 'edge'):
            for extension in spec.extensions:
                options.add_extension(extension)
                Output.Console(plugin_name, f"DEBUG: Extension agregada: {extension}")
        elif browser_name == 'firefox':
            Output.Console(plugin_name, "DEBUG: Extensiones de Firefox se instalan post-sesion con install_addon")
        else:
            unsupported(spec, plugin_name, f"'extensions' no soportado para navegador {browser_name}, ignorado")

    @staticmethod
    def _install_firefox_addons(driver, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        if browser_name != 'firefox' or not spec.extensions:
            return
        for extension in spec.extensions:
            try:
                driver.install_addon(extension, temporary=True)
                Output.Console(plugin_name, f"DEBUG: Extension de Firefox instalada: {extension}")
            except Exception as e:  # noqa: BLE001 - best-effort
                Logging.log_failure(plugin_name, f"instalar extension Firefox '{extension}'", e, spec.log_file)

    @staticmethod
    def _apply_chromium_options(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        """Aplica exclude_switches y experimental_options (solo Chromium)."""
        if browser_name not in ('chrome', 'edge'):
            if spec.exclude_switches or spec.experimental_options:
                unsupported(spec, plugin_name, f"exclude_switches/experimental_options solo para Chromium, ignorados en {browser_name}")
            return

        for name, value in (spec.experimental_options or {}).items():
            if name == 'prefs':
                merged = dict(options.experimental_options.get('prefs', {}))
                merged.update(value)
                options.add_experimental_option('prefs', merged)
            else:
                options.add_experimental_option(name, value)

        if spec.exclude_switches:
            existing = list(options.experimental_options.get('excludeSwitches', []))
            merged = list(dict.fromkeys(existing + list(spec.exclude_switches)))
            options.add_experimental_option('excludeSwitches', merged)

        if spec.experimental_options or spec.exclude_switches:
            Output.Console(plugin_name, f"DEBUG: Opciones experimentales de Chromium aplicadas")

    @staticmethod
    def _apply_anti_detection_options(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        """Aplica flags/prefs para reducir la deteccion de automatizacion."""
        if not spec.anti_detection:
            return

        if browser_name in ('chrome', 'edge'):
            options.add_argument('--disable-blink-features=AutomationControlled')
            existing = list(options.experimental_options.get('excludeSwitches', []))
            merged = list(dict.fromkeys(existing + ['enable-automation']))
            options.add_experimental_option('excludeSwitches', merged)
            options.add_experimental_option('useAutomationExtension', False)
            Output.Console(plugin_name, "DEBUG: anti_detection aplicado (Chromium)")
        elif browser_name == 'firefox':
            options.set_preference('dom.webdriver.enabled', False)
            Output.Console(plugin_name, "ADVERTENCIA: anti_detection en Firefox es best-effort; navigator.webdriver puede seguir visible en versiones actuales")
        else:
            unsupported(spec, plugin_name, f"anti_detection no soportado para navegador {browser_name}")

    @staticmethod
    def _install_anti_detection(driver, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        """Registra el script anti-deteccion via CDP (solo Chromium)."""
        if not spec.anti_detection or browser_name not in ('chrome', 'edge'):
            return
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": ANTI_DETECTION_SCRIPT})
            Output.Console(plugin_name, "DEBUG: anti_detection: script CDP registrado")
        except Exception as e:  # noqa: BLE001 - no debe tumbar la sesion
            Output.Console(plugin_name, f"ADVERTENCIA: no se pudo registrar el script anti_detection: {e}")

    @staticmethod
    def _apply_pref_maps(options, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
        prefs: Dict[str, Any] = {}
        if spec.download_dir:
            os.makedirs(spec.download_dir, exist_ok=True)
            prefs.update(BrowserFactory._download_dir_prefs(spec.download_dir, browser_name))
        if spec.permissions:
            prefs.update(BrowserFactory._permissions_prefs(spec.permissions, browser_name, plugin_name))
        if not prefs:
            return

        if browser_name in ('chrome', 'edge'):
            merged = dict(options.experimental_options.get('prefs', {}))
            merged.update(prefs)
            options.add_experimental_option('prefs', merged)
        elif browser_name == 'firefox':
            for key, value in prefs.items():
                options.set_preference(key, value)
        else:
            unsupported(spec, plugin_name, f"prefs de compatibilidad no soportadas para navegador {browser_name}, ignoradas")
            return
        Output.Console(plugin_name, f"DEBUG: Prefs de compatibilidad aplicadas: {sorted(prefs.keys())}")

    @staticmethod
    def _download_dir_prefs(download_dir: str, browser_name: str) -> Dict[str, Any]:
        path = os.path.abspath(download_dir)
        if browser_name in ('chrome', 'edge'):
            return {
                'download.default_directory': path,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True,
            }
        if browser_name == 'firefox':
            return {
                'browser.download.folderList': 2,
                'browser.download.dir': path,
                'browser.download.useDownloadDir': True,
                'browser.download.manager.showWhenStarting': False,
                'browser.helperApps.neverAsk.saveToDisk': 'application/octet-stream,application/pdf,text/csv,application/zip',
            }
        return {}

    PERMISSION_MAP = {
        'geolocation': ('profile.default_content_setting_values.geolocation', 'permissions.default.geo'),
        'notifications': ('profile.default_content_setting_values.notifications', 'permissions.default.desktop-notification'),
        'camera': ('profile.default_content_setting_values.media_stream_camera', 'permissions.default.camera'),
        'microphone': ('profile.default_content_setting_values.media_stream_mic', 'permissions.default.microphone'),
    }
    PERMISSION_VALUES = {'allow': 1, 'block': 2, 'ask': 0}

    @staticmethod
    def _permissions_prefs(permissions: Dict[str, str], browser_name: str, plugin_name: str = 'Selenium') -> Dict[str, Any]:
        prefs: Dict[str, Any] = {}
        for name, setting in permissions.items():
            value = BrowserFactory.PERMISSION_VALUES.get(str(setting).lower())
            mapping = BrowserFactory.PERMISSION_MAP.get(name)
            if value is None:
                Output.Console(plugin_name, f"ADVERTENCIA: valor de permiso invalido para '{name}': {setting} (usar allow/block/ask)")
                continue
            if mapping is None:
                Output.Console(plugin_name, f"ADVERTENCIA: permiso no soportado: {name}")
                continue
            chrome_key, firefox_key = mapping
            key = chrome_key if browser_name in ('chrome', 'edge') else firefox_key if browser_name == 'firefox' else None
            if key:
                prefs[key] = value
        return prefs

    @staticmethod
    def _set_no_proxy() -> None:
        # Evitar que un proxy del sistema intercepte la conexion local
        # Selenium<->driver (localhost). Ver:
        # https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#invalidsessionidexception
        for no_proxy_var in ('no_proxy', 'NO_PROXY'):
            existing = os.environ.get(no_proxy_var, '')
            hosts = {h.strip() for h in existing.split(',') if h.strip()}
            hosts.update({'127.0.0.1', 'localhost'})
            os.environ[no_proxy_var] = ','.join(sorted(hosts))

    @staticmethod
    def _service_kwargs(browser_name: str) -> Dict[str, Any]:
        service_kwargs: Dict[str, Any] = {}
        if browser_name == 'firefox':
            service_kwargs['service_args'] = ['--host', '127.0.0.1']
            service_kwargs['log_output'] = '/tmp/sugar_geckodriver_debug.log'
        return service_kwargs

    @staticmethod
    def _resolve_driver_path(spec: SessionSpec, browser_config: Dict[str, Any], plugin_name: str) -> str:
        driver_path = spec.driver_path
        if driver_path and os.path.exists(driver_path):
            Output.Console(plugin_name, f"DEBUG: Usando driver personalizado: {driver_path}")
            return driver_path

        Output.Console(plugin_name, "DEBUG: Descargando driver automaticamente...")
        driver_manager = browser_config['driver_manager']()
        driver_path = driver_manager.install()
        Output.Console(plugin_name, f"DEBUG: Driver descargado en: {driver_path}")
        return driver_path
