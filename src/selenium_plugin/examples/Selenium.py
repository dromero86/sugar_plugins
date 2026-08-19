"""
Selenium Component for Selenium Plugin
====================================

Handles navigation, JavaScript execution, and page information.
"""

import time
from typing import Any, Dict, Optional
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Sugar.Lang.Utils.Output import Output

class Selenium:
    """
    Selenium component for Selenium plugin.
    
    Handles navigation, JavaScript execution, and page information retrieval.
    """
    
    def __init__(self, plugin):
        """
        Initialize the Selenium component.
        
        Args:
            plugin: Parent Selenium plugin instance
        """
        self.plugin = plugin
        self.wait_timeout = 10
        
        Output.Console("SeleniumCore", "Selenium component initialized")
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a Selenium command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        Output.Console("SeleniumCore", f"Executing Selenium command: {command}")
        
        try:
            if command == "navigate":
                return self._navigate(config)
            elif command == "go_back":
                return self._go_back(config)
            elif command == "go_forward":
                return self._go_forward(config)
            elif command == "refresh":
                return self._refresh(config)
            elif command == "execute_script":
                return self._execute_script(config)
            elif command == "get_page_source":
                return self._get_page_source(config)
            elif command == "get_title":
                return self._get_title(config)
            elif command == "get_url":
                return self._get_url(config)
            else:
                Output.Console("SeleniumCore", f"Unknown Selenium command: {command}")
                return None
                
        except Exception as e:
            Output.Console("SeleniumCore", f"Error executing Selenium command '{command}': {str(e)}")
            raise
    
    def _get_driver(self):
        """Get the current web driver instance."""
        if hasattr(self.plugin, 'browser') and hasattr(self.plugin.browser, 'driver'):
            return self.plugin.browser.driver
        else:
            raise RuntimeError("No web driver available")
    
    def _navigate(self, config: Dict[str, Any]) -> bool:
        """Navigate to a URL."""
        url = config.get("url")
        wait_for_load = config.get("wait_for_load", True)
        timeout = config.get("timeout", self.wait_timeout)
        
        if not url:
            raise ValueError("URL is required for navigate command")
        
        driver = self._get_driver()
        driver.get(url)
        
        if wait_for_load:
            self._wait_for_page_load(timeout)
        
        Output.Console("SeleniumCore", f"Navigated to: {url}")
        return True
    
    def _go_back(self, config: Dict[str, Any]) -> bool:
        """Go back in browser history."""
        driver = self._get_driver()
        driver.back()
        Output.Console("SeleniumCore", "Navigated back")
        return True
    
    def _go_forward(self, config: Dict[str, Any]) -> bool:
        """Go forward in browser history."""
        driver = self._get_driver()
        driver.forward()
        Output.Console("SeleniumCore", "Navigated forward")
        return True
    
    def _refresh(self, config: Dict[str, Any]) -> bool:
        """Refresh the current page."""
        driver = self._get_driver()
        driver.refresh()
        Output.Console("SeleniumCore", "Page refreshed")
        return True
    
    def _execute_script(self, config: Dict[str, Any]) -> Any:
        """Execute JavaScript code."""
        script = config.get("script")
        arguments = config.get("arguments", [])
        
        if not script:
            raise ValueError("Script is required for execute_script command")
        
        driver = self._get_driver()
        result = driver.execute_script(script, *arguments)
        
        Output.Console("SeleniumCore", "JavaScript executed successfully")
        return result
    
    def _get_page_source(self, config: Dict[str, Any]) -> str:
        """Get the page source HTML."""
        driver = self._get_driver()
        page_source = driver.page_source
        return page_source
    
    def _get_title(self, config: Dict[str, Any]) -> str:
        """Get the page title."""
        driver = self._get_driver()
        title = driver.title
        return title
    
    def _get_url(self, config: Dict[str, Any]) -> str:
        """Get the current URL."""
        driver = self._get_driver()
        current_url = driver.current_url
        return current_url
    
    def _wait_for_page_load(self, timeout: int = 10):
        """Wait for the page to load completely."""
        driver = self._get_driver()
        
        try:
            # Wait for document ready state
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for jQuery if present
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script("return jQuery.active == 0")
                )
            except:
                # jQuery not present or not active, continue
                pass
                
        except Exception as e:
            Output.Console("SeleniumCore", f"Warning: Page load wait timeout: {str(e)}")
    
    def wait_for_element(self, selector: str, by: str = "css", timeout: int = 10):
        """Wait for an element to be present."""
        from selenium.webdriver.common.by import By
        
        by_map = {
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH,
            "tag": By.TAG_NAME,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }
        
        locator = by_map.get(by.lower(), By.CSS_SELECTOR)
        driver = self._get_driver()
        
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((locator, selector))
            )
            return element
        except Exception as e:
            Output.Console("SeleniumCore", f"Element not found: {selector}")
            raise
    
    def wait_for_clickable(self, selector: str, by: str = "css", timeout: int = 10):
        """Wait for an element to be clickable."""
        from selenium.webdriver.common.by import By
        
        by_map = {
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH,
            "tag": By.TAG_NAME,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }
        
        locator = by_map.get(by.lower(), By.CSS_SELECTOR)
        driver = self._get_driver()
        
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((locator, selector))
            )
            return element
        except Exception as e:
            Output.Console("SeleniumCore", f"Element not clickable: {selector}")
            raise 