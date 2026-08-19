"""
Browser Component for Playwright Plugin
======================================

Handles browser management operations including:
- Browser launching and closing
- Context management
- Browser configuration
"""

from typing import Any, Dict, Optional
from Sugar.Lang.Utils.Output import Output

class Browser:
    """
    Browser management component for Playwright plugin.
    """
    
    def __init__(self, plugin):
        """
        Initialize Browser component.
        
        Args:
            plugin: Reference to the main plugin instance
        """
        self.plugin = plugin
        self.browser = None
        self.context = None
        self.browser_type = "chromium"  # Default browser
        self.config = {}
        
        Output.Console(self.plugin.plugin_name, "Browser component initialized")
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure browser settings.
        
        Args:
            config: Browser configuration
        """
        self.config = config
        self.browser_type = config.get("browser_type", "chromium")
        Output.Console(self.plugin.plugin_name, f"Browser configured: {self.browser_type}")
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute browser-related commands.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        try:
            if command == "launch_browser":
                return self._launch_browser(config)
            elif command == "close_browser":
                return self._close_browser(config)
            elif command == "new_context":
                return self._new_context(config)
            elif command == "close_context":
                return self._close_context(config)
            elif command == "start_video":
                return self._start_video(config)
            elif command == "stop_video":
                return self._stop_video(config)
            else:
                Output.Console(self.plugin.plugin_name, f"Unknown browser command: {command}")
                return None
                
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error in browser command '{command}': {str(e)}")
            raise
    
    def _launch_browser(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Launch a browser instance.
        
        Args:
            config: Launch configuration
            
        Returns:
            Launch result
        """
        try:
            from playwright.sync_api import sync_playwright
            
            # Get browser type from config or use default
            browser_type = config.get("browser_type", self.browser_type)
            
            # Get launch options
            headless = config.get("headless", True)
            slow_mo = config.get("slow_mo", 0)
            args = config.get("args", [])
            
            # Launch playwright
            self.playwright = sync_playwright().start()
            
            # Select browser type
            if browser_type == "chromium":
                browser_class = self.playwright.chromium
            elif browser_type == "firefox":
                browser_class = self.playwright.firefox
            elif browser_type == "webkit":
                browser_class = self.playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Launch browser
            self.browser = browser_class.launch(
                headless=headless,
                slow_mo=slow_mo,
                args=args
            )
            
            Output.Console(self.plugin.plugin_name, f"Browser launched: {browser_type}")
            
            result = {
                "success": True,
                "browser_type": browser_type,
                "headless": headless,
                "slow_mo": slow_mo
            }
            
            # Store result in variable if specified
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error launching browser: {str(e)}")
            raise
    
    def _close_browser(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close the browser instance.
        
        Args:
            config: Close configuration
            
        Returns:
            Close result
        """
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                Output.Console(self.plugin.plugin_name, "Browser closed")
            
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                self.playwright = None
                Output.Console(self.plugin.plugin_name, "Playwright stopped")
            
            result = {"success": True, "message": "Browser closed successfully"}
            
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error closing browser: {str(e)}")
            raise
    
    def _new_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new browser context.
        
        Args:
            config: Context configuration
            
        Returns:
            Context creation result
        """
        try:
            if not self.browser:
                raise RuntimeError("Browser not launched. Call launch_browser first.")
            
            # Context options
            viewport = config.get("viewport", {"width": 1280, "height": 720})
            user_agent = config.get("user_agent")
            locale = config.get("locale")
            timezone_id = config.get("timezone_id")
            permissions = config.get("permissions", [])
            
            # Create context
            context_options = {
                "viewport": viewport
            }
            
            if user_agent:
                context_options["user_agent"] = user_agent
            if locale:
                context_options["locale"] = locale
            if timezone_id:
                context_options["timezone_id"] = timezone_id
            if permissions:
                context_options["permissions"] = permissions
            
            self.context = self.browser.new_context(**context_options)
            
            Output.Console(self.plugin.plugin_name, "New browser context created")
            
            result = {
                "success": True,
                "viewport": viewport,
                "user_agent": user_agent,
                "locale": locale,
                "timezone_id": timezone_id,
                "permissions": permissions
            }
            
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error creating context: {str(e)}")
            raise
    
    def _close_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close the browser context.
        
        Args:
            config: Close context configuration
            
        Returns:
            Close context result
        """
        try:
            if self.context:
                self.context.close()
                self.context = None
                Output.Console(self.plugin.plugin_name, "Browser context closed")
            
            result = {"success": True, "message": "Context closed successfully"}
            
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error closing context: {str(e)}")
            raise
    
    def _start_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start video recording.
        
        Args:
            config: Video configuration
            
        Returns:
            Video start result
        """
        try:
            if not self.context:
                raise RuntimeError("No context available. Create context first.")
            
            video_path = config.get("path", "./videos/recording.webm")
            video_size = config.get("size", {"width": 1280, "height": 720})
            
            # Create video directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            # Start video recording
            self.context.start_video_recording(
                path=video_path,
                size=video_size
            )
            
            Output.Console(self.plugin.plugin_name, f"Video recording started: {video_path}")
            
            result = {
                "success": True,
                "video_path": video_path,
                "video_size": video_size
            }
            
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error starting video: {str(e)}")
            raise
    
    def _stop_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop video recording.
        
        Args:
            config: Stop video configuration
            
        Returns:
            Video stop result
        """
        try:
            if not self.context:
                raise RuntimeError("No context available.")
            
            # Stop video recording
            video_path = self.context.stop_video_recording()
            
            Output.Console(self.plugin.plugin_name, f"Video recording stopped: {video_path}")
            
            result = {
                "success": True,
                "video_path": video_path
            }
            
            if "result" in config:
                self.plugin.set_variable(config["result"], result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error stopping video: {str(e)}")
            raise
