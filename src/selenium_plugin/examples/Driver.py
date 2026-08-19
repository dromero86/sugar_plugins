"""
Driver Component for Selenium Plugin
==================================

Handles web element interaction and driver management.
"""

import time
from typing import Any, Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from Sugar.Lang.Utils.Output import Output

class Driver:
    """
    Driver component for Selenium plugin.
    
    Handles web element interaction, waiting, and driver management.
    """
    
    def __init__(self, plugin):
        """
        Initialize the Driver component.
        
        Args:
            plugin: Parent Selenium plugin instance
        """
        self.plugin = plugin
        self.driver = None
        self.wait_timeout = 10
        
        Output.Console("SeleniumDriver", "Driver component initialized")
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a driver command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        Output.Console("SeleniumDriver", f"Executing driver command: {command}")
        
        try:
            if command == "click":
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
            elif command == "scroll_to":
                return self._scroll_to(config)
            elif command == "hover":
                return self._hover_element(config)
            elif command == "drag_and_drop":
                return self._drag_and_drop(config)
            elif command == "upload_file":
                return self._upload_file(config)
            else:
                Output.Console("SeleniumDriver", f"Unknown driver command: {command}")
                return None
                
        except Exception as e:
            Output.Console("SeleniumDriver", f"Error executing driver command '{command}': {str(e)}")
            raise
    
    def _get_driver(self):
        """Get the current web driver instance."""
        if not self.driver:
            # Try to get driver from browser component
            if hasattr(self.plugin, 'browser') and hasattr(self.plugin.browser, 'driver'):
                self.driver = self.plugin.browser.driver
            else:
                raise RuntimeError("No web driver available")
        return self.driver
    
    def _find_element_by_selector(self, selector: str, by: str = By.CSS_SELECTOR):
        """Find element using selector and locator strategy."""
        driver = self._get_driver()
        return driver.find_element(by, selector)
    
    def _click_element(self, config: Dict[str, Any]) -> bool:
        """Click on an element."""
        selector = config.get("selector")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for click command")
        
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
        element = self._find_element_by_selector(selector, locator)
        element.click()
        
        return True
    
    def _type_text(self, config: Dict[str, Any]) -> bool:
        """Type text into an element."""
        selector = config.get("selector")
        text = config.get("text", "")
        clear_first = config.get("clear", True)
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for type command")
        
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
        element = self._find_element_by_selector(selector, locator)
        
        if clear_first:
            element.clear()
        
        element.send_keys(text)
        return True
    
    def _clear_element(self, config: Dict[str, Any]) -> bool:
        """Clear an element's content."""
        selector = config.get("selector")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for clear command")
        
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
        element = self._find_element_by_selector(selector, locator)
        element.clear()
        
        return True
    
    def _submit_form(self, config: Dict[str, Any]) -> bool:
        """Submit a form."""
        selector = config.get("selector")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for submit command")
        
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
        element = self._find_element_by_selector(selector, locator)
        element.submit()
        
        return True
    
    def _select_option(self, config: Dict[str, Any]) -> bool:
        """Select an option from a dropdown."""
        selector = config.get("selector")
        value = config.get("value")
        text = config.get("text")
        index = config.get("index")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for select command")
        
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
        element = self._find_element_by_selector(selector, locator)
        select = Select(element)
        
        if value is not None:
            select.select_by_value(value)
        elif text is not None:
            select.select_by_visible_text(text)
        elif index is not None:
            select.select_by_index(index)
        else:
            raise ValueError("Either value, text, or index must be provided for select command")
        
        return True
    
    def _find_element(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single element and return its properties."""
        selector = config.get("selector")
        by = config.get("by", "css")
        attributes = config.get("attributes", ["text", "tag_name", "is_displayed", "is_enabled"])
        
        if not selector:
            raise ValueError("Selector is required for find_element command")
        
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
        element = self._find_element_by_selector(selector, locator)
        
        result = {}
        for attr in attributes:
            if attr == "text":
                result["text"] = element.text
            elif attr == "tag_name":
                result["tag_name"] = element.tag_name
            elif attr == "is_displayed":
                result["is_displayed"] = element.is_displayed()
            elif attr == "is_enabled":
                result["is_enabled"] = element.is_enabled()
            else:
                result[attr] = element.get_attribute(attr)
        
        return result
    
    def _find_elements(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple elements and return their properties."""
        selector = config.get("selector")
        by = config.get("by", "css")
        attributes = config.get("attributes", ["text", "tag_name"])
        
        if not selector:
            raise ValueError("Selector is required for find_elements command")
        
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
        elements = driver.find_elements(locator, selector)
        
        results = []
        for element in elements:
            result = {}
            for attr in attributes:
                if attr == "text":
                    result["text"] = element.text
                elif attr == "tag_name":
                    result["tag_name"] = element.tag_name
                else:
                    result[attr] = element.get_attribute(attr)
            results.append(result)
        
        return results
    
    def _wait_for_element(self, config: Dict[str, Any]) -> bool:
        """Wait for an element to be present."""
        selector = config.get("selector")
        timeout = config.get("timeout", self.wait_timeout)
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for wait_for_element command")
        
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
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((locator, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def _wait_for_clickable(self, config: Dict[str, Any]) -> bool:
        """Wait for an element to be clickable."""
        selector = config.get("selector")
        timeout = config.get("timeout", self.wait_timeout)
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for wait_for_clickable command")
        
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
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((locator, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def _scroll_to(self, config: Dict[str, Any]) -> bool:
        """Scroll to an element."""
        selector = config.get("selector")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for scroll_to command")
        
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
        element = self._find_element_by_selector(selector, locator)
        driver = self._get_driver()
        
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return True
    
    def _hover_element(self, config: Dict[str, Any]) -> bool:
        """Hover over an element."""
        selector = config.get("selector")
        by = config.get("by", "css")
        
        if not selector:
            raise ValueError("Selector is required for hover command")
        
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
        element = self._find_element_by_selector(selector, locator)
        driver = self._get_driver()
        
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        return True
    
    def _drag_and_drop(self, config: Dict[str, Any]) -> bool:
        """Drag and drop an element."""
        source_selector = config.get("source")
        target_selector = config.get("target")
        source_by = config.get("source_by", "css")
        target_by = config.get("target_by", "css")
        
        if not source_selector or not target_selector:
            raise ValueError("Source and target selectors are required for drag_and_drop command")
        
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
        
        source_locator = by_map.get(source_by.lower(), By.CSS_SELECTOR)
        target_locator = by_map.get(target_by.lower(), By.CSS_SELECTOR)
        
        source_element = self._find_element_by_selector(source_selector, source_locator)
        target_element = self._find_element_by_selector(target_selector, target_locator)
        driver = self._get_driver()
        
        actions = ActionChains(driver)
        actions.drag_and_drop(source_element, target_element).perform()
        return True
    
    def _upload_file(self, config: Dict[str, Any]) -> bool:
        """Upload a file using a file input element."""
        selector = config.get("selector")
        file_path = config.get("file_path")
        by = config.get("by", "css")
        
        if not selector or not file_path:
            raise ValueError("Selector and file_path are required for upload_file command")
        
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
        element = self._find_element_by_selector(selector, locator)
        element.send_keys(file_path)
        
        return True 