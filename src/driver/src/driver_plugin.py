"""
Driver Plugin Implementation
===========================

Main implementation of the Driver plugin for Sugar.
Provides browser automation capabilities using Selenium WebDriver.
"""

import time
from typing import Any, Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class DriverPlugin(PluginBase):
    """
    Driver plugin for Sugar.
    
    Provides browser automation capabilities including:
    - Browser initialization and management
    - Element interaction (click, type, select)
    - Element finding and waiting
    - JavaScript execution
    - Page navigation
    - Screenshot capture
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Browser automation plugin for Sugar with Selenium WebDriver"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["selenium", "webdriver-manager"]
    REQUIREMENTS = ["selenium>=4.0.0", "webdriver-manager>=3.8.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Driver plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Driver state
        self.driver = None
        self.options = None
        self.service = None
        self.disabled = False
        self.meta_config = {}  # Store meta configuration
        self.driver_config = {}  # Store driver configuration
        
        Output.Console(self.plugin_name, "Driver plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for Driver plugin configuration.
        Called by the meta plugin to configure driver before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process driver configuration
            driver_config = config.get("driver", {})
            if driver_config:
                self.driver_config = driver_config
                Output.Console(self.plugin_name, f"Driver configuration stored: {driver_config}")
            
            # Process options
            options = config.get("options", [])
            if options:
                self.driver_config["options"] = options
                Output.Console(self.plugin_name, f"Browser options configured: {len(options)} options")
            
            # Process detach setting
            detach = config.get("detach", False)
            if detach:
                self.driver_config["detach"] = detach
                Output.Console(self.plugin_name, "Browser detach mode enabled")
            
            # Process browser type
            browser_type = config.get("browser", "chrome")
            self.driver_config["browser"] = browser_type
            Output.Console(self.plugin_name, f"Browser type configured: {browser_type}")
            
            return {
                "success": True,
                "driver_configured": bool(self.driver_config),
                "options_count": len(options),
                "detach_enabled": detach,
                "browser_type": browser_type
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available driver commands.
        
        Returns:
            List of available command names
        """
        return [
            # Browser management
            "initialize",
            "close",
            "quit",
            "disable",
            "enable",
            
            # Navigation
            "get",
            "back",
            "forward",
            "refresh",
            
            # Element interaction
            "click",
            "type",
            "clear",
            "submit",
            "select",
            
            # Element finding
            "find_element",
            "find_elements",
            "wait_for_element",
            "wait_for_clickable",
            
            # JavaScript
            "execute_script",
            "get_page_source",
            "get_title",
            "get_url",
            
            # Screenshots
            "take_screenshot",
            "save_screenshot",
            
            # Browser info
            "get_cookies",
            "add_cookie",
            "delete_cookie",
            "delete_all_cookies"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a driver command.
        
        Args:
            command: Command to execute
            config: Configuration for the command
            
        Returns:
            Command result
        """
        try:
            if command == "initialize":
                return self._initialize_driver(config)
            elif command == "close":
                return self._close_browser(config)
            elif command == "quit":
                return self._quit_browser(config)
            elif command == "disable":
                return self._disable_driver(config)
            elif command == "enable":
                return self._enable_driver(config)
            elif command == "get":
                return self._navigate_to(config)
            elif command == "back":
                return self._go_back(config)
            elif command == "forward":
                return self._go_forward(config)
            elif command == "refresh":
                return self._refresh_page(config)
            elif command == "click":
                return self._click_element(config)
            elif command == "type":
                return self._type_text(config)
            elif command == "clear":
                return self._clear_element(config)
            elif command == "submit":
                return self._submit_form(config)
            elif command == "select":
                return self._select_option(config)
            elif command == "find_element":
                return self._find_element(config)
            elif command == "find_elements":
                return self._find_elements(config)
            elif command == "wait_for_element":
                return self._wait_for_element(config)
            elif command == "wait_for_clickable":
                return self._wait_for_clickable(config)
            elif command == "execute_script":
                return self._execute_script(config)
            elif command == "get_page_source":
                return self._get_page_source(config)
            elif command == "get_title":
                return self._get_title(config)
            elif command == "get_url":
                return self._get_url(config)
            elif command == "take_screenshot":
                return self._take_screenshot(config)
            elif command == "save_screenshot":
                return self._save_screenshot(config)
            elif command == "get_cookies":
                return self._get_cookies(config)
            elif command == "add_cookie":
                return self._add_cookie(config)
            elif command == "delete_cookie":
                return self._delete_cookie(config)
            elif command == "delete_all_cookies":
                return self._delete_all_cookies(config)
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            raise
    
    def _initialize_driver(self, config: Dict[str, Any]) -> bool:
        """Initialize the WebDriver."""
        # Check if driver is enabled via meta plugin
        if hasattr(self.context, 'plugin_manager'):
            meta_plugin = self.context.plugin_manager.get_plugin("meta")
            if meta_plugin and not meta_plugin.is_driver_enabled():
                Output.Console(self.plugin_name, "Driver DISABLED by meta plugin")
                return False
        
        if self.disabled:
            Output.Console(self.plugin_name, "Driver DISABLED (will not initialize)")
            return False
        
        try:
            # Get driver configuration from meta plugin if available
            if hasattr(self.context, 'plugin_manager'):
                meta_plugin = self.context.plugin_manager.get_plugin("meta")
                if meta_plugin:
                    meta_config = meta_plugin.get_driver_config()
                    # Merge meta config with provided config
                    driver_config = {**meta_config.get("driver", {}), **config.get("driver", {})}
                    options_list = meta_config.get("options", []) + config.get("driver", {}).get("options", [])
                    detach = meta_config.get("detach", False) or config.get("driver", {}).get("detach", False)
                else:
                    driver_config = config.get("driver", {})
                    options_list = driver_config.get("options", [])
                    detach = driver_config.get("detach", False)
            else:
                driver_config = config.get("driver", {})
                options_list = driver_config.get("options", [])
                detach = driver_config.get("detach", False)
            
            driver_type = driver_config.get("type", "chrome")
            
            if driver_type == "chrome":
                # Configure Chrome options
                self.options = Options()
                for option in options_list:
                    self.options.add_argument(option)
                
                # Configure detach if present
                if detach:
                    self.options.add_experimental_option("detach", True)
                
                # Configure service
                driver_bin = driver_config.get("bin")
                if driver_bin:
                    self.service = Service(executable_path=driver_bin)
                
                # Create driver
                self.driver = webdriver.Chrome(
                    service=self.service,
                    options=self.options
                )
            
            Output.Console(self.plugin_name, f"Driver initialized: {driver_type}")
            return True
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Failed to initialize driver: {str(e)}")
            raise
    
    def _close_browser(self, config: Dict[str, Any]) -> bool:
        """Close the current browser window."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.close()
            Output.Console(self.plugin_name, "Browser window closed")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error closing browser: {str(e)}")
            return False
    
    def _quit_browser(self, config: Dict[str, Any]) -> bool:
        """Quit the browser completely."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.quit()
            self.driver = None
            Output.Console(self.plugin_name, "Browser quit")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error quitting browser: {str(e)}")
            return False
    
    def _disable_driver(self, config: Dict[str, Any]) -> bool:
        """Disable the driver."""
        self.disabled = True
        Output.Console(self.plugin_name, "Driver disabled")
        return True
    
    def _enable_driver(self, config: Dict[str, Any]) -> bool:
        """Enable the driver."""
        self.disabled = False
        Output.Console(self.plugin_name, "Driver enabled")
        return True
    
    def _navigate_to(self, config: Dict[str, Any]) -> bool:
        """Navigate to a URL."""
        # Check if driver is enabled via meta plugin
        if hasattr(self.context, 'plugin_manager'):
            meta_plugin = self.context.plugin_manager.get_plugin("meta")
            if meta_plugin and not meta_plugin.is_driver_enabled():
                Output.Console(self.plugin_name, "Driver DISABLED by meta plugin")
                return False
        
        if self.disabled or not self.driver:
            return False
        
        url = config.get("url")
        if not url:
            raise ValueError("URL required")
        
        try:
            self.driver.get(url)
            self._on_ready()
            Output.Console(self.plugin_name, f"Navigated to: {url}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error navigating to {url}: {str(e)}")
            raise
    
    def _go_back(self, config: Dict[str, Any]) -> bool:
        """Go back in browser history."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.back()
            Output.Console(self.plugin_name, "Went back in history")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error going back: {str(e)}")
            return False
    
    def _go_forward(self, config: Dict[str, Any]) -> bool:
        """Go forward in browser history."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.forward()
            Output.Console(self.plugin_name, "Went forward in history")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error going forward: {str(e)}")
            return False
    
    def _refresh_page(self, config: Dict[str, Any]) -> bool:
        """Refresh the current page."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.refresh()
            Output.Console(self.plugin_name, "Page refreshed")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error refreshing page: {str(e)}")
            return False
    
    def _click_element(self, config: Dict[str, Any]) -> bool:
        """Click on an element."""
        # Check if driver is enabled via meta plugin
        if hasattr(self.context, 'plugin_manager'):
            meta_plugin = self.context.plugin_manager.get_plugin("meta")
            if meta_plugin and not meta_plugin.is_driver_enabled():
                Output.Console(self.plugin_name, "Driver DISABLED by meta plugin")
                return False
        
        if self.disabled or not self.driver:
            return False
        
        selector = config.get("selector")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            element.click()
            Output.Console(self.plugin_name, f"Clicked element: {selector}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error clicking element {selector}: {str(e)}")
            raise
    
    def _type_text(self, config: Dict[str, Any]) -> bool:
        """Type text into an element."""
        if self.disabled or not self.driver:
            return False
        
        selector = config.get("selector")
        text = config.get("text", "")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            element.clear()
            element.send_keys(text)
            Output.Console(self.plugin_name, f"Typed text into: {selector}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error typing text into {selector}: {str(e)}")
            raise
    
    def _clear_element(self, config: Dict[str, Any]) -> bool:
        """Clear an element."""
        if self.disabled or not self.driver:
            return False
        
        selector = config.get("selector")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            element.clear()
            Output.Console(self.plugin_name, f"Cleared element: {selector}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error clearing element {selector}: {str(e)}")
            raise
    
    def _submit_form(self, config: Dict[str, Any]) -> bool:
        """Submit a form."""
        if self.disabled or not self.driver:
            return False
        
        selector = config.get("selector")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            element.submit()
            Output.Console(self.plugin_name, f"Submitted form: {selector}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error submitting form {selector}: {str(e)}")
            raise
    
    def _select_option(self, config: Dict[str, Any]) -> bool:
        """Select an option from a dropdown."""
        if self.disabled or not self.driver:
            return False
        
        selector = config.get("selector")
        value = config.get("value")
        text = config.get("text")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        if not value and not text:
            raise ValueError("Either value or text required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            select = Select(element)
            
            if value:
                select.select_by_value(value)
            elif text:
                select.select_by_visible_text(text)
            
            Output.Console(self.plugin_name, f"Selected option in: {selector}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error selecting option in {selector}: {str(e)}")
            raise
    
    def _find_element(self, config: Dict[str, Any]) -> Any:
        """Find a single element."""
        if self.disabled or not self.driver:
            return None
        
        selector = config.get("selector")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = self._find_element_by_locator(selector, locator_type)
            return element
        except Exception as e:
            Output.Console(self.plugin_name, f"Error finding element {selector}: {str(e)}")
            raise
    
    def _find_elements(self, config: Dict[str, Any]) -> List[Any]:
        """Find multiple elements."""
        if self.disabled or not self.driver:
            return []
        
        selector = config.get("selector")
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            elements = self._find_elements_by_locator(selector, locator_type)
            return elements
        except Exception as e:
            Output.Console(self.plugin_name, f"Error finding elements {selector}: {str(e)}")
            raise
    
    def _wait_for_element(self, config: Dict[str, Any]) -> Any:
        """Wait for an element to be present."""
        if self.disabled or not self.driver:
            return None
        
        selector = config.get("selector")
        timeout = config.get("timeout", 10)
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((self._get_by_locator(locator_type), selector))
            )
            return element
        except TimeoutException:
            Output.Console(self.plugin_name, f"Timeout waiting for element: {selector}")
            return None
        except Exception as e:
            Output.Console(self.plugin_name, f"Error waiting for element {selector}: {str(e)}")
            raise
    
    def _wait_for_clickable(self, config: Dict[str, Any]) -> Any:
        """Wait for an element to be clickable."""
        if self.disabled or not self.driver:
            return None
        
        selector = config.get("selector")
        timeout = config.get("timeout", 10)
        locator_type = config.get("locator", "css")
        
        if not selector:
            raise ValueError("Selector required")
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((self._get_by_locator(locator_type), selector))
            )
            return element
        except TimeoutException:
            Output.Console(self.plugin_name, f"Timeout waiting for clickable element: {selector}")
            return None
        except Exception as e:
            Output.Console(self.plugin_name, f"Error waiting for clickable element {selector}: {str(e)}")
            raise
    
    def _execute_script(self, config: Dict[str, Any]) -> Any:
        """Execute JavaScript code."""
        if self.disabled or not self.driver:
            return None
        
        script = config.get("script")
        if not script:
            raise ValueError("Script required")
        
        try:
            result = self.driver.execute_script(script)
            Output.Console(self.plugin_name, f"Executed JavaScript: {script[:50]}...")
            return result
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing JavaScript: {str(e)}")
            raise
    
    def _get_page_source(self, config: Dict[str, Any]) -> str:
        """Get the page source."""
        if self.disabled or not self.driver:
            return ""
        
        try:
            source = self.driver.page_source
            return source
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting page source: {str(e)}")
            raise
    
    def _get_title(self, config: Dict[str, Any]) -> str:
        """Get the page title."""
        if self.disabled or not self.driver:
            return ""
        
        try:
            title = self.driver.title
            return title
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting page title: {str(e)}")
            raise
    
    def _get_url(self, config: Dict[str, Any]) -> str:
        """Get the current URL."""
        if self.disabled or not self.driver:
            return ""
        
        try:
            url = self.driver.current_url
            return url
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting current URL: {str(e)}")
            raise
    
    def _take_screenshot(self, config: Dict[str, Any]) -> bytes:
        """Take a screenshot."""
        if self.disabled or not self.driver:
            return b""
        
        try:
            screenshot = self.driver.get_screenshot_as_png()
            Output.Console(self.plugin_name, "Screenshot taken")
            return screenshot
        except Exception as e:
            Output.Console(self.plugin_name, f"Error taking screenshot: {str(e)}")
            raise
    
    def _save_screenshot(self, config: Dict[str, Any]) -> str:
        """Save a screenshot to file."""
        if self.disabled or not self.driver:
            return ""
        
        path = config.get("path", "screenshot.png")
        
        try:
            self.driver.save_screenshot(path)
            Output.Console(self.plugin_name, f"Screenshot saved to: {path}")
            return path
        except Exception as e:
            Output.Console(self.plugin_name, f"Error saving screenshot: {str(e)}")
            raise
    
    def _get_cookies(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all cookies."""
        if self.disabled or not self.driver:
            return []
        
        try:
            cookies = self.driver.get_cookies()
            return cookies
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting cookies: {str(e)}")
            raise
    
    def _add_cookie(self, config: Dict[str, Any]) -> bool:
        """Add a cookie."""
        if self.disabled or not self.driver:
            return False
        
        cookie = config.get("cookie")
        if not cookie:
            raise ValueError("Cookie required")
        
        try:
            self.driver.add_cookie(cookie)
            Output.Console(self.plugin_name, f"Added cookie: {cookie.get('name', 'unknown')}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error adding cookie: {str(e)}")
            raise
    
    def _delete_cookie(self, config: Dict[str, Any]) -> bool:
        """Delete a cookie."""
        if self.disabled or not self.driver:
            return False
        
        name = config.get("name")
        if not name:
            raise ValueError("Cookie name required")
        
        try:
            self.driver.delete_cookie(name)
            Output.Console(self.plugin_name, f"Deleted cookie: {name}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error deleting cookie: {str(e)}")
            raise
    
    def _delete_all_cookies(self, config: Dict[str, Any]) -> bool:
        """Delete all cookies."""
        if self.disabled or not self.driver:
            return False
        
        try:
            self.driver.delete_all_cookies()
            Output.Console(self.plugin_name, "Deleted all cookies")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error deleting all cookies: {str(e)}")
            raise
    
    def _find_element_by_locator(self, selector: str, locator_type: str):
        """Find element by locator type."""
        by = self._get_by_locator(locator_type)
        return self.driver.find_element(by, selector)
    
    def _find_elements_by_locator(self, selector: str, locator_type: str):
        """Find elements by locator type."""
        by = self._get_by_locator(locator_type)
        return self.driver.find_elements(by, selector)
    
    def _get_by_locator(self, locator_type: str):
        """Get By locator from string."""
        locator_map = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH
        }
        return locator_map.get(locator_type.lower(), By.CSS_SELECTOR)
    
    def _on_ready(self, timeout: int = 60):
        """Wait for page to be ready."""
        if self.disabled or not self.driver:
            return
        
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            Output.Console(self.plugin_name, f"Error waiting for page ready: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        Output.Console(self.plugin_name, "Driver plugin cleanup completed")