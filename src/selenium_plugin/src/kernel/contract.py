"""
Contrato de la capa kernel
==========================

Dataclasses que son el unico idioma que cruza las capas del plugin:
el adaptador Sugar (L4) construye un SessionSpec y lo pasa a la capa de
sesion/keeper (L1-L3). No depende de Sugar ni de IPC.

La normalizacion desde el `meta` de Sugar acepta una sintaxis neutral
(agnostica al navegador): el desarrollador declara `driver` y capacidades
semanticas, y BrowserFactory las traduce al motor correspondiente.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionSpec:
    """Parametros necesarios para crear una sesion de navegador."""

    browser: str = 'chrome'
    headless: bool = False
    detach: bool = False
    options: List[str] = field(default_factory=list)
    prefs: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 10
    implicit_wait: int = 5
    driver_path: Optional[str] = None
    binary: Optional[str] = None
    profile: Optional[str] = None
    download_dir: Optional[str] = None
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    extensions: List[str] = field(default_factory=list)
    permissions: Dict[str, str] = field(default_factory=dict)
    exclude_switches: List[str] = field(default_factory=list)
    experimental_options: Dict[str, Any] = field(default_factory=dict)
    anti_detection: bool = False
    stealth: bool = False
    fingerprint: Dict[str, Any] = field(default_factory=dict)
    timezone: Optional[str] = None
    locale: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None
    accept_language: Optional[str] = None
    humanize: Optional[Dict[str, Any]] = None
    profiles: List[str] = field(default_factory=list)
    profile_strategy: str = 'first'
    bidi: bool = False
    proxy_user: Optional[str] = None
    proxy_pass: Optional[str] = None
    network_block: List[str] = field(default_factory=list)
    network_headers: Dict[str, str] = field(default_factory=dict)
    downloads: bool = False
    on_unsupported: str = 'warn'
    log_file: Optional[str] = None

    @classmethod
    def from_meta(cls, meta: Optional[Dict[str, Any]]) -> 'SessionSpec':
        """Normaliza el meta de Sugar a un SessionSpec neutral.

        Acepta tanto la sintaxis unificada (driver + identity/downloads/
        network/overrides) como las claves planas legacy.
        """
        meta = meta or {}
        identity = dict(meta.get('identity') or {})

        driver_field = meta.get('driver')
        driver_bin = None
        if isinstance(driver_field, str):
            browser_name = driver_field
        elif isinstance(driver_field, dict):
            browser_name = meta.get('browser')
            driver_bin = driver_field.get('bin')
        else:
            browser_name = meta.get('browser')
        browser_name = str(browser_name or 'chrome').lower()

        def pick(key: str, default: Any = None) -> Any:
            if meta.get(key) is not None:
                return meta[key]
            if identity.get(key) is not None:
                return identity[key]
            return default

        humanize_raw = meta.get('humanize')
        if humanize_raw is True:
            humanize: Optional[Dict[str, Any]] = {}
        elif isinstance(humanize_raw, dict):
            humanize = dict(humanize_raw)
        else:
            humanize = None

        proxy_raw = pick('proxy')
        proxy_server = proxy_user = proxy_pass = None
        if isinstance(proxy_raw, dict):
            proxy_server = proxy_raw.get('server')
            if not proxy_server and proxy_raw.get('host') and proxy_raw.get('port'):
                proxy_server = f"{proxy_raw.get('scheme', 'http')}://{proxy_raw['host']}:{proxy_raw['port']}"
            proxy_user = proxy_raw.get('username')
            proxy_pass = proxy_raw.get('password')
        else:
            proxy_server = proxy_raw
        proxy_user = meta.get('proxy_user', proxy_user)
        proxy_pass = meta.get('proxy_pass', proxy_pass)

        downloads_raw = meta.get('downloads')
        download_dir = meta.get('download_dir')
        downloads_enabled = False
        if isinstance(downloads_raw, dict):
            download_dir = downloads_raw.get('dir', download_dir)
            downloads_enabled = bool(downloads_raw.get('enabled', bool(download_dir)))
        elif downloads_raw is True:
            downloads_enabled = True

        network_raw = meta.get('network') or {}
        network_block = list(meta.get('network_block') or network_raw.get('block') or [])
        network_headers = dict(network_raw.get('headers') or {})

        overrides = (meta.get('overrides') or {}).get(browser_name, {}) or {}
        options = list(meta.get('options', []) or []) + list(overrides.get('options', []) or [])
        prefs = {**(meta.get('prefs') or {}), **(overrides.get('prefs') or {})}
        experimental_options = {
            **(meta.get('experimental_options') or {}),
            **(overrides.get('experimental_options') or {}),
        }
        exclude_switches = (
            list(meta.get('exclude_switches', []) or [])
            + list(overrides.get('exclude_switches', []) or [])
        )

        driver_path = meta.get('driver_path') or identity.get('driver_path') or driver_bin

        return cls(
            browser=browser_name,
            headless=bool(meta.get('headless', False)),
            detach=bool(meta.get('detach', False)),
            options=options,
            prefs=prefs,
            timeout=meta.get('timeout', 10),
            implicit_wait=meta.get('implicit_wait', 5),
            driver_path=driver_path,
            binary=pick('binary'),
            profile=pick('profile'),
            download_dir=download_dir,
            proxy=proxy_server,
            user_agent=pick('user_agent'),
            extensions=list(pick('extensions', []) or []),
            permissions=dict(pick('permissions', {}) or {}),
            exclude_switches=exclude_switches,
            experimental_options=experimental_options,
            anti_detection=bool(meta.get('anti_detection', False)),
            stealth=bool(meta.get('stealth', False)),
            fingerprint=dict(meta.get('fingerprint', {}) or {}),
            timezone=pick('timezone'),
            locale=pick('locale'),
            geolocation=pick('geolocation'),
            accept_language=pick('accept_language'),
            humanize=humanize,
            profiles=list(pick('profiles', []) or []),
            profile_strategy=pick('profile_strategy', 'first'),
            bidi=bool(meta.get('bidi', False)) or bool(proxy_user) or bool(network_block),
            proxy_user=proxy_user,
            proxy_pass=proxy_pass,
            network_block=network_block,
            network_headers=network_headers,
            downloads=downloads_enabled,
            on_unsupported=str(meta.get('on_unsupported', 'warn')).lower(),
            log_file=meta.get('log_file'),
        )

    def cache_key(self) -> str:
        """Identidad estable de la sesion para el registry de keepers."""
        return '|'.join([
            self.browser,
            str(self.headless),
            ','.join(self.options),
            ','.join(sorted(f'{k}={v}' for k, v in self.prefs.items())),
            str(self.driver_path or ''),
            str(self.binary or ''),
            str(self.profile or ''),
            str(self.download_dir or ''),
            str(self.proxy or ''),
            str(self.user_agent or ''),
            ','.join(self.extensions),
            ','.join(sorted(f'{k}={v}' for k, v in self.permissions.items())),
            ','.join(self.exclude_switches),
            ','.join(sorted(f'{k}={v}' for k, v in self.experimental_options.items())),
            str(self.anti_detection),
            str(self.stealth),
            ','.join(sorted(f'{k}={v}' for k, v in self.fingerprint.items())),
            str(self.timezone or ''),
            str(self.locale or ''),
            str(self.geolocation or ''),
            str(self.accept_language or ''),
            str(self.humanize),
            ','.join(self.profiles),
            self.profile_strategy,
            str(self.bidi),
            str(self.proxy_user or ''),
            ','.join(self.network_block),
            ','.join(sorted(f'{k}={v}' for k, v in self.network_headers.items())),
            str(self.downloads),
            self.on_unsupported,
            str(self.log_file or ''),
        ])
