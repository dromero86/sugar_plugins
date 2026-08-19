"""
Browser Component for Selenium Plugin
==================================

Handles browser management, screenshots, and browser-level operations.
"""

import os
import time
from typing import Any, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from Sugar.Lang.Utils.Output import Output

class Browser:
    """
    Browser component for Selenium plugin.
    
    Handles browser initialization, management, and browser-level operations.
    """
    
    def __init__(self, plugin):
        """
        Initialize the Browser component.
        
        Args:
            plugin: Parent Selenium plugin instance
        """
        self.plugin = plugin
        self.driver = None
        self.browser_type = None
        
        Output.Console("SeleniumBrowser", "Browser component initialized")
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a browser command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        Output.Console("SeleniumBrowser", f"Executing browser command: {command}")
        
        try:
            if command == "open_browser":
                return self._open_browser(config)
            elif command == "close_browser":
                return self._close_browser(config)
            elif command == "quit_browser":
                return self._quit_browser(config)
            elif command == "switch_window":
                return self._switch_window(config)
            elif command == "switch_frame":
                return self._switch_frame(config)
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
            elif command == "clear_cookies":
                return self._clear_cookies(config)
            else:
                Output.Console("SeleniumBrowser", f"Unknown browser command: {command}")
                return None
                
        except Exception as e:
            Output.Console("SeleniumBrowser", f"Error executing browser command '{command}': {str(e)}")
            raise
    
    def _open_browser(self, config: Dict[str, Any]) -> bool:
        """Open a new browser instance."""
        browser_type = config.get("browser", "chrome").lower()
        headless = config.get("headless", False)
        window_size = config.get("window_size", "1920,1080")
        user_agent = config.get("user_agent")
        proxy = config.get("proxy")
        download_path = config.get("download_path")
        
        try:
            if browser_type == "chrome":
                self.driver = self._create_chrome_driver(
                    headless, window_size, user_agent, proxy, download_path
                )
            elif browser_type == "firefox":
                self.driver = self._create_firefox_driver(
                    headless, window_size, user_agent, proxy, download_path
                )
            elif browser_type == "edge":
                self.driver = self._create_edge_driver(
                    headless, window_size, user_agent, proxy, download_path
                )
            elif browser_type == "safari":
                self.driver = self._create_safari_driver(
                    headless, window_size, user_agent, proxy, download_path
                )
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            self.browser_type = browser_type
            
            # Set window size
            width, height = map(int, window_size.split(','))
            self.driver.set_window_size(width, height)
            
            Output.Console("SeleniumBrowser", f"Browser {browser_type} opened successfully")
            return True
            
        except Exception as e:
            Output.Console("SeleniumBrowser", f"Error opening browser: {str(e)}")
            raise
    
    def _create_chrome_driver(self, headless: bool, window_size: str, 
                            user_agent: Optional[str], proxy: Optional[str], 
                            download_path: Optional[str]) -> webdriver.Chrome:
        """Create Chrome driver with options."""
        options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        if download_path:
            prefs = {"download.default_directory": download_path}
            options.add_experimental_option("prefs", prefs)
        
        # Use webdriver-manager to handle driver installation
        service = webdriver.chrome.service.Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self, headless: bool, window_size: str,
                             user_agent: Optional[str], proxy: Optional[str],
                             download_path: Optional[str]) -> webdriver.Firefox:
        """Create Firefox driver with options."""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        if user_agent:
            options.set_preference("general.useragent.override", user_agent)
        
        if proxy:
            host, port = proxy.split(":")
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", host)
            options.set_preference("network.proxy.http_port", int(port))
            options.set_preference("network.proxy.ssl", host)
            options.set_preference("network.proxy.ssl_port", int(port))
        
        if download_path:
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_path)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                                 "application/pdf,application/zip,text/plain")
        
        # Use webdriver-manager to handle driver installation
        service = webdriver.firefox.service.Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def _create_edge_driver(self, headless: bool, window_size: str,
                          user_agent: Optional[str], proxy: Optional[str],
                          download_path: Optional[str]) -> webdriver.Edge:
        """Create Edge driver with options."""
        options = EdgeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={window_size}")
        
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        if download_path:
            prefs = {"download.default_directory": download_path}
            options.add_experimental_option("prefs", prefs)
        
        # Use webdriver-manager to handle driver installation
        service = webdriver.edge.service.Service(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    def _create_safari_driver(self, headless: bool, window_size: str,
                            user_agent: Optional[str], proxy: Optional[str],
                            download_path: Optional[str]) -> webdriver.Safari:
        """Create Safari driver with options."""
        options = SafariOptions()
        
        # Safari doesn't support headless mode in the same way
        if headless:
            Output.Console("SeleniumBrowser", "Warning: Safari doesn't support headless mode")
        
        # Safari options are more limited
        return webdriver.Safari(options=options)
    
    def _close_browser(self, config: Dict[str, Any]) -> bool:
        """Close the current browser window."""
        if self.driver:
            self.driver.close()
            Output.Console("SeleniumBrowser", "Browser window closed")
            return True
        return False
    
    def _quit_browser(self, config: Dict[str, Any]) -> bool:
        """Quit the browser completely."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.browser_type = None
            Output.Console("SeleniumBrowser", "Browser quit completely")
            return True
        return False
    
    def _switch_window(self, config: Dict[str, Any]) -> bool:
        """Switch to a different window or tab."""
        window_handle = config.get("window_handle")
        window_index = config.get("window_index")
        window_title = config.get("window_title")
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        if window_handle:
            self.driver.switch_to.window(window_handle)
        elif window_index is not None:
            handles = self.driver.window_handles
            if 0 <= window_index < len(handles):
                self.driver.switch_to.window(handles[window_index])
            else:
                raise ValueError(f"Invalid window index: {window_index}")
        elif window_title:
            current_handle = self.driver.current_window_handle
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if window_title in self.driver.title:
                    return True
            # If not found, switch back to original
            self.driver.switch_to.window(current_handle)
            raise ValueError(f"Window with title '{window_title}' not found")
        else:
            raise ValueError("Either window_handle, window_index, or window_title must be provided")
        
        return True
    
    def _switch_frame(self, config: Dict[str, Any]) -> bool:
        """Switch to a frame or iframe."""
        frame_selector = config.get("frame_selector")
        frame_index = config.get("frame_index")
        frame_name = config.get("frame_name")
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        if frame_selector:
            from selenium.webdriver.common.by import By
            frame_element = self.driver.find_element(By.CSS_SELECTOR, frame_selector)
            self.driver.switch_to.frame(frame_element)
        elif frame_index is not None:
            self.driver.switch_to.frame(frame_index)
        elif frame_name:
            self.driver.switch_to.frame(frame_name)
        else:
            # Switch to default content
            self.driver.switch_to.default_content()
        
        return True
    
    def _take_screenshot(self, config: Dict[str, Any]) -> bytes:
        """Take a screenshot and return as bytes."""
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        screenshot_bytes = self.driver.get_screenshot_as_png()
        Output.Console("SeleniumBrowser", "Screenshot taken")
        return screenshot_bytes
    
    def _save_screenshot(self, config: Dict[str, Any]) -> str:
        """Take a screenshot and save to file."""
        file_path = config.get("file_path", f"screenshot_{int(time.time())}.png")
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
        
        self.driver.save_screenshot(file_path)
        Output.Console("SeleniumBrowser", f"Screenshot saved to: {file_path}")
        return file_path
    
    def _get_cookies(self, config: Dict[str, Any]) -> list:
        """Get all cookies."""
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        cookies = self.driver.get_cookies()
        return cookies
    
    def _add_cookie(self, config: Dict[str, Any]) -> bool:
        """Add a cookie."""
        name = config.get("name")
        value = config.get("value")
        domain = config.get("domain")
        path = config.get("path", "/")
        
        if not name or not value:
            raise ValueError("Cookie name and value are required")
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        cookie_dict = {
            "name": name,
            "value": value,
            "path": path
        }
        
        if domain:
            cookie_dict["domain"] = domain
        
        self.driver.add_cookie(cookie_dict)
        Output.Console("SeleniumBrowser", f"Cookie '{name}' added")
        return True
    
    def _delete_cookie(self, config: Dict[str, Any]) -> bool:
        """Delete a specific cookie."""
        name = config.get("name")
        
        if not name:
            raise ValueError("Cookie name is required")
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        self.driver.delete_cookie(name)
        Output.Console("SeleniumBrowser", f"Cookie '{name}' deleted")
        return True
    
    def _clear_cookies(self, config: Dict[str, Any]) -> bool:
        """Clear all cookies."""
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        self.driver.delete_all_cookies()
        Output.Console("SeleniumBrowser", "All cookies cleared")
        return True 