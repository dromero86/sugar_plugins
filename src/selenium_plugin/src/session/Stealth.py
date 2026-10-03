"""
Capa de sesion: stealth / fingerprint
=====================================

Genera el script de stealth y aplica overrides de emulacion. En Chromium
usa CDP; lo que no tiene equivalente se avisa. BiDi se usa para auth de
proxy e interceptacion de red (cross-browser).
"""

import json
import os
import sys
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from Sugar.Lang.Utils.Output import Output

from kernel.contract import SessionSpec
from session.Support import unsupported
from session import Logging


def _safe(plugin_name: str, spec: SessionSpec, context: str, fn) -> None:
    """Ejecuta una feature best-effort: si falla, se registra y se sigue."""
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        Logging.log_failure(plugin_name, context, e, spec.log_file)


def url_pattern(pattern: Any) -> Dict[str, Any]:
    """Convierte un patron de URL a la forma que espera BiDi.

    Acepta dict (se usa tal cual), URL completa (http/https) o glob
    (con '*', se interpreta como pathname).
    """
    if isinstance(pattern, dict):
        return pattern
    if isinstance(pattern, str) and pattern.startswith(('http://', 'https://')):
        parsed = urlparse(pattern)
        result: Dict[str, Any] = {"type": "pattern"}
        if parsed.scheme:
            result["protocol"] = parsed.scheme
        if parsed.hostname:
            result["hostname"] = parsed.hostname
        if parsed.path:
            result["pathname"] = parsed.path
        return result
    if isinstance(pattern, str) and '*' in pattern:
        # Algunos navegadores (Firefox) exigen escapar '*' en el patron.
        return {"type": "pattern", "pathname": pattern.replace('*', '\\*')}
    return {"type": "string", "pattern": pattern}


DEFAULT_LANGUAGES = ['en-US', 'en']
DEFAULT_WEBGL_VENDOR = 'Intel Inc.'
DEFAULT_WEBGL_RENDERER = 'Intel Iris OpenGL Engine'


def _webgl_override(vendor: str, renderer: str) -> str:
    return (
        "(function(){"
        "const gp=WebGLRenderingContext.prototype.getParameter;"
        "WebGLRenderingContext.prototype.getParameter=function(p){"
        f"if(p===37445)return {json.dumps(vendor)};if(p===37446)return {json.dumps(renderer)};"
        "return gp.call(this,p);};"
        "})();"
    )


def _canvas_noise() -> str:
    return (
        "(function(){"
        "const t=HTMLCanvasElement.prototype.toDataURL;"
        "HTMLCanvasElement.prototype.toDataURL=function(){"
        "const c=this.getContext('2d');"
        "if(c){c.fillStyle='rgba(0,0,0,0.01)';c.fillRect(0,0,1,1);}"
        "return t.apply(this,arguments);};"
        "})();"
    )


def _audio_noise() -> str:
    return (
        "(function(){"
        "const o=AnalyserNode.prototype.getFloatFrequencyData;"
        "AnalyserNode.prototype.getFloatFrequencyData=function(a){"
        "o.call(this,a);for(let i=0;i<a.length;i++)a[i]+=(Math.random()-0.5)*1e-4;};"
        "})();"
    )


def _firefox_webdriver_override() -> str:
    """Oculta navigator.webdriver en Firefox sin delatar el parche.

    Se define el getter en Navigator.prototype (no en la instancia) y se
    registra el parche de Function.prototype.toString para que el getter
    siga respondiendo '[native code]' ante un chequeo de integridad.
    """
    return (
        "(function(){"
        "var orig=Function.prototype.toString;"
        "var patched=new WeakSet();"
        "var native='function () { [native code] }';"
        "var toString=function(){"
        "if(patched.has(this))return native;"
        "return orig.call(this);};"
        "patched.add(toString);"
        "Function.prototype.toString=toString;"
        "var getter=function(){return undefined;};"
        "patched.add(getter);"
        "try{Object.defineProperty(Navigator.prototype,'webdriver',{get:getter,configurable:true});}catch(e){}"
        "})();"
    )


def _build_chromium_script(fp: Dict[str, Any]) -> str:
    parts = ["Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"]

    if fp.get('chrome', True):
        parts.append("window.chrome = window.chrome || {runtime:{}};")

    if fp.get('plugins', True):
        parts.append(
            "Object.defineProperty(navigator,'plugins',{get:()=>"
            "[{name:'Chrome PDF Plugin'},{name:'Chrome PDF Viewer'},{name:'Native Client'}]});"
        )

    languages = fp.get('languages') or DEFAULT_LANGUAGES
    parts.append(f"Object.defineProperty(navigator,'languages',{{get:()=>{json.dumps(languages)}}});")

    if fp.get('platform'):
        parts.append(f"Object.defineProperty(navigator,'platform',{{get:()=>{json.dumps(fp['platform'])}}});")
    if fp.get('hardware_concurrency'):
        parts.append(f"Object.defineProperty(navigator,'hardwareConcurrency',{{get:()=>{int(fp['hardware_concurrency'])}}});")
    if fp.get('device_memory'):
        parts.append(f"Object.defineProperty(navigator,'deviceMemory',{{get:()=>{int(fp['device_memory'])}}});")

    parts.append(
        "(function(){"
        "if(navigator.permissions&&navigator.permissions.query){"
        "const o=navigator.permissions.query.bind(navigator.permissions);"
        "navigator.permissions.query=(p)=>p&&p.name==='notifications'"
        "?Promise.resolve({state:Notification.permission}):o(p);}"
        "})();"
    )

    if fp.get('webgl', True):
        parts.append(_webgl_override(
            fp.get('webgl_vendor', DEFAULT_WEBGL_VENDOR),
            fp.get('webgl_renderer', DEFAULT_WEBGL_RENDERER),
        ))

    if fp.get('canvas_noise'):
        parts.append(_canvas_noise())

    if fp.get('audio_noise'):
        parts.append(_audio_noise())

    return "\n".join(parts)


def _build_firefox_script(fp: Dict[str, Any]) -> str:
    """Stealth minimo y coherente para Firefox.

    No se emulan rasgos de Chrome (window.chrome, plugins PDF de Chrome,
    deviceMemory): un Firefox que los exponga es en si mismo un indicio.
    Solo se neutraliza navigator.webdriver y se aplican las claves del
    fingerprint que el usuario pidio explicitamente.
    """
    parts = [_firefox_webdriver_override()]

    if fp.get('languages'):
        parts.append(f"Object.defineProperty(navigator,'languages',{{get:()=>{json.dumps(fp['languages'])}}});")
    if fp.get('platform'):
        parts.append(f"Object.defineProperty(navigator,'platform',{{get:()=>{json.dumps(fp['platform'])}}});")
    if fp.get('hardware_concurrency'):
        parts.append(f"Object.defineProperty(navigator,'hardwareConcurrency',{{get:()=>{int(fp['hardware_concurrency'])}}});")
    if fp.get('webgl'):
        parts.append(_webgl_override(
            fp.get('webgl_vendor', DEFAULT_WEBGL_VENDOR),
            fp.get('webgl_renderer', DEFAULT_WEBGL_RENDERER),
        ))
    if fp.get('canvas_noise'):
        parts.append(_canvas_noise())
    if fp.get('audio_noise'):
        parts.append(_audio_noise())

    return "\n".join(parts)


def build_script(fingerprint: Optional[Dict[str, Any]], browser: str = 'chrome') -> str:
    """Construye el JS de stealth a partir del fingerprint configurado."""
    fp = fingerprint or {}
    if browser == 'firefox':
        return _build_firefox_script(fp)
    return _build_chromium_script(fp)


def build_preload_function(fingerprint: Optional[Dict[str, Any]], browser: str = 'firefox') -> str:
    """Envuelve el script de stealth en una function declaration.

    BiDi (script.addPreloadScript / driver.script.pin) espera una funcion,
    no una lista de sentencias: se usa para inyectar en Firefox antes de
    que corran los scripts de la pagina.
    """
    return "() => {\n" + build_script(fingerprint, browser=browser) + "\n}"


def _is_chromium(driver) -> bool:
    name = (getattr(driver, 'name', '') or '').lower()
    return name in ('chrome', 'chromium', 'msedge', 'chrome-headless-shell', 'edge')


def install(driver, spec: SessionSpec, browser_name: str, plugin_name: str) -> None:
    """Instala stealth + emulacion post-sesion."""
    if spec.bidi:
        _install_bidi(driver, spec, plugin_name)

    if _is_chromium(driver):
        _install_chromium(driver, spec, plugin_name)
        return

    if browser_name == 'firefox':
        _install_firefox(driver, spec, plugin_name)
        return

    if spec.stealth or spec.fingerprint or spec.timezone or spec.locale or spec.geolocation:
        unsupported(spec, plugin_name, f"stealth/emulacion no soportada para navegador {browser_name}")


def _install_firefox(driver, spec: SessionSpec, plugin_name: str) -> None:
    """Stealth para Firefox via BiDi preload script.

    Firefox no soporta CDP. Selenium 4.11+ expone driver.script.pin()
    (BiDi script.addPreloadScript), que inyecta en cada documento antes
    de los scripts de la pagina; es el unico punto donde se puede
    neutralizar navigator.webdriver a tiempo.
    """
    if spec.stealth or spec.fingerprint:
        script = build_preload_function(spec.fingerprint, browser='firefox')
        _safe(plugin_name, spec, "stealth preload (BiDi/Firefox)", lambda: driver.script.pin(script))
        Output.Console(plugin_name, "DEBUG: stealth Firefox registrado (BiDi preload)")

    if spec.geolocation:
        _install_firefox_geolocation(driver, spec, plugin_name)

    if spec.timezone or spec.locale:
        unsupported(
            spec, plugin_name,
            "timezone/locale override no esta expuesto por Selenium para Firefox "
            "(se usa el del sistema/perfil)",
        )


def _install_firefox_geolocation(driver, spec: SessionSpec, plugin_name: str) -> None:
    def _apply() -> None:
        from selenium.webdriver.common.bidi.emulation import GeolocationCoordinates
        coords = GeolocationCoordinates(
            latitude=spec.geolocation.get('latitude'),
            longitude=spec.geolocation.get('longitude'),
            accuracy=spec.geolocation.get('accuracy', 100),
        )
        driver.emulation.set_geolocation_override(
            coordinates=coords, contexts=[driver.current_window_handle]
        )
    _safe(plugin_name, spec, "geolocation override (BiDi/Firefox)", _apply)


def _install_chromium(driver, spec: SessionSpec, plugin_name: str) -> None:
    if spec.stealth or spec.fingerprint:
        _safe(plugin_name, spec, "stealth script (CDP)", lambda: driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": build_script(spec.fingerprint)}
        ))
        Output.Console(plugin_name, "DEBUG: stealth script registrado (CDP)")

    if spec.timezone:
        _safe(plugin_name, spec, "timezone override (CDP)", lambda: driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride", {"timezoneId": spec.timezone}
        ))
    if spec.locale:
        _safe(plugin_name, spec, "locale override (CDP)", lambda: driver.execute_cdp_cmd(
            "Emulation.setLocaleOverride", {"locale": spec.locale}
        ))
    if spec.geolocation:
        params = {
            "latitude": spec.geolocation.get('latitude'),
            "longitude": spec.geolocation.get('longitude'),
            "accuracy": spec.geolocation.get('accuracy', 100),
        }
        _safe(plugin_name, spec, "geolocation override (CDP)", lambda: driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride", params
        ))
    if spec.accept_language or spec.network_headers:
        headers = dict(spec.network_headers or {})
        if spec.accept_language:
            headers.setdefault('Accept-Language', spec.accept_language)
        _safe(plugin_name, spec, "headers extra (CDP)", lambda: driver.execute_cdp_cmd("Network.enable", {}))
        _safe(plugin_name, spec, "headers extra (CDP)", lambda: driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders", {"headers": headers}
        ))


def _install_bidi(driver, spec: SessionSpec, plugin_name: str) -> None:
    try:
        if spec.proxy_user is not None:
            driver.network.add_auth_handler(spec.proxy_user, spec.proxy_pass or '')
            Output.Console(plugin_name, "DEBUG: BiDi auth handler registrado")

        for pattern in spec.network_block:
            def _block(request):
                request.fail_request()
            driver.network.add_request_handler(
                'before_request', _block, url_patterns=[url_pattern(pattern)]
            )
            Output.Console(plugin_name, f"DEBUG: BiDi bloqueando requests: {pattern}")
    except Exception as e:  # noqa: BLE001 - BiDi es opcional
        Logging.log_failure(plugin_name, "configurar BiDi", e, spec.log_file)
