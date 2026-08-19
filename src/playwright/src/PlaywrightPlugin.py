"""
Playwright Plugin Implementation
==============================

Main plugin class for Playwright automation functionality.
Provides modern web automation capabilities through Sugar's plugin system.
"""

from typing import Any, Dict, List, Optional
from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

from .Browser import Browser
from .Page import Page
from .Playwright import Playwright

class PlaywrightPlugin(PluginBase):
    """
    Playwright automation plugin for Sugar.
    
    Provides modern web automation capabilities including:
    - Browser management (Chromium, Firefox, WebKit)
    - Page interaction
    - Element manipulation
    - Network interception
    - Mobile emulation
    - Screenshot and video capture
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Playwright web automation plugin for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["playwright"]
    REQUIREMENTS = ["playwright>=1.40.0"]
    
    # Requerimientos del sistema
    SYSTEM_DEPENDENCIES = []
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 2,
        "min_disk_gb": 1,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": True,
        "write_access": ["/tmp", "./screenshots", "./videos"],
        "read_access": ["./downloads"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Playwright plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Verificar dependencias al inicializar
        self.dependency_status = self._check_all_dependencies()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Initialize components
        self.browser = Browser(self)
        self.page = Page(self)
        self.playwright = Playwright(self)
        self.meta_config = {}  # Store meta configuration
        self.browser_config = {}  # Store browser configuration
        
        Output.Console(self.plugin_name, "Playwright plugin components initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for Playwright plugin configuration.
        Called by the meta plugin to configure Playwright before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process browser configuration
            browser_config = config.get("browser", {})
            if browser_config:
                self.browser_config = browser_config
                Output.Console(self.plugin_name, f"Browser configuration stored: {browser_config}")
            
            # Process options
            options = config.get("options", [])
            if options:
                self.browser_config["options"] = options
                Output.Console(self.plugin_name, f"Browser options configured: {len(options)} options")
            
            # Process headless setting
            headless = config.get("headless", True)
            self.browser_config["headless"] = headless
            Output.Console(self.plugin_name, f"Headless mode: {headless}")
            
            # Process slow_mo setting
            slow_mo = config.get("slow_mo", 0)
            if slow_mo > 0:
                self.browser_config["slow_mo"] = slow_mo
                Output.Console(self.plugin_name, f"Slow motion enabled: {slow_mo}ms")
            
            # Apply configuration to browser component
            if hasattr(self.browser, 'configure'):
                self.browser.configure(self.browser_config)
            
            return {
                "success": True,
                "browser_configured": bool(self.browser_config),
                "options_count": len(options),
                "headless_enabled": headless,
                "slow_mo": slow_mo
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available Playwright commands.
        
        Returns:
            List of available command names
        """
        return [
            # Browser management
            "launch_browser",
            "close_browser",
            "new_context",
            "close_context",
            "new_page",
            "close_page",
            
            # Navigation
            "goto",
            "go_back",
            "go_forward",
            "reload",
            
            # Element interaction
            "click",
            "type",
            "fill",
            "clear",
            "select_option",
            "check",
            "uncheck",
            "press",
            
            # Element finding
            "locator",
            "get_by_text",
            "get_by_role",
            "get_by_label",
            "get_by_placeholder",
            "get_by_test_id",
            
            # Waiting
            "wait_for_load_state",
            "wait_for_url",
            "wait_for_selector",
            "wait_for_element",
            
            # JavaScript
            "evaluate",
            "evaluate_handle",
            "get_content",
            "get_title",
            "get_url",
            
            # Screenshots and videos
            "screenshot",
            "screenshot_element",
            "start_video",
            "stop_video",
            
            # Network
            "route",
            "unroute",
            "set_extra_http_headers",
            
            # Cookies and storage
            "get_cookies",
            "add_cookies",
            "clear_cookies",
            "get_local_storage",
            "set_local_storage",
            "clear_local_storage",
            
            # Advanced
            "scroll_to",
            "hover",
            "drag_and_drop",
            "upload_file",
            "download_file",
            "emulate_device",
            "set_viewport_size",
            "set_geolocation",
            "set_permissions"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a Playwright command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        Output.Console(self.plugin_name, f"Executing command: {command}")
        
        # Verificar dependencias antes de comandos críticos
        if command in ["launch_browser", "new_context", "new_page"] and not self.dependency_status['all_satisfied']:
            raise RuntimeError("Dependencias no satisfechas para comandos de navegador")
        
        # Interpolate variables in config
        interpolated_config = self.interpolate_variables(config)
        
        try:
            # Route command to appropriate component
            if command in ["launch_browser", "close_browser", "new_context", "close_context"]:
                return self.browser.execute(command, interpolated_config)
            elif command in ["new_page", "close_page", "goto", "go_back", "go_forward", "reload", 
                           "wait_for_load_state", "wait_for_url", "get_content", "get_title", "get_url"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["click", "type", "fill", "clear", "select_option", "check", "uncheck", "press",
                           "locator", "get_by_text", "get_by_role", "get_by_label", "get_by_placeholder", 
                           "get_by_test_id", "wait_for_selector", "wait_for_element", "scroll_to", "hover",
                           "drag_and_drop", "upload_file", "download_file"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["evaluate", "evaluate_handle", "screenshot", "screenshot_element"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["route", "unroute", "set_extra_http_headers"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["get_cookies", "add_cookies", "clear_cookies", "get_local_storage", 
                           "set_local_storage", "clear_local_storage"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["emulate_device", "set_viewport_size", "set_geolocation", "set_permissions"]:
                return self.page.execute(command, interpolated_config)
            elif command in ["start_video", "stop_video"]:
                return self.browser.execute(command, interpolated_config)
            else:
                Output.Console(self.plugin_name, f"Unknown command: {command}")
                return None
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing command '{command}': {str(e)}")
            raise
    
    def cleanup(self):
        """
        Cleanup Playwright resources.
        """
        try:
            if hasattr(self.browser, 'browser') and self.browser.browser:
                self.browser.browser.close()
            if hasattr(self.playwright, 'playwright') and self.playwright.playwright:
                self.playwright.playwright.stop()
            Output.Console(self.plugin_name, "Playwright resources cleaned up")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error during cleanup: {str(e)}")
        finally:
            super().cleanup()
