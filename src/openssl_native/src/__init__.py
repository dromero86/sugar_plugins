"""
Wrapper para el plugin OpenSSL Native.
"""

from Sugar.Lang.Plugins.PluginBase import PluginBase

try:
    from .openssl_plugin_native import *
except ImportError:
    # Si no se puede importar el archivo .pyx, crear una implementación básica
    class OpenSSLNativePlugin(PluginBase):
        def __init__(self, context=None):
            super().__init__(context)
            self.name = "openssl_native"
            self.version = "1.0.0"
            self.description = "OpenSSL Native Plugin"
        
        def execute(self, command, config):
            raise NotImplementedError("Plugin OpenSSL Native no disponible")
        
        def get_available_commands(self):
            return []
