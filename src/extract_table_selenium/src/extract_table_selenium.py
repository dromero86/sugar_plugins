"""
Extract Table Selenium Plugin Implementation
===========================================

Main implementation of the Selenium-based table extraction plugin.
Provides comprehensive table extraction capabilities using Selenium WebDriver.
"""

import json
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, WebDriverException,
        StaleElementReferenceException, ElementClickInterceptedException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

class ExtractTableSeleniumPlugin(PluginBase):
    """
    Selenium-based HTML table extraction plugin for Sugar.
    
    Provides advanced table extraction capabilities with support for:
    - Dynamic content and JavaScript-rendered tables
    - Complex table structures (colspan, rowspan)
    - Pagination and infinite scroll
    - Data filtering and transformation
    - Validation and error handling
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Selenium-based HTML table extraction with advanced features"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Plugin dependencies
    DEPENDENCIES = ["selenium", "webdriver-manager"]
    REQUIREMENTS = ["selenium>=4.0.0", "webdriver-manager>=3.8.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the ExtractTableSeleniumPlugin."""
        super().__init__(context, plugin_config)
        
        # Default browser configuration
        self.default_browser_config = {
            "browser": "chrome",
            "headless": True,
            "timeout": 30,
            "implicit_wait": 10,
            "window_size": "1920x1080",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Merge with plugin config
        self.browser_config = {**self.default_browser_config, **self.plugin_config}
        
        # WebDriver instance
        self.driver = None
        self.wait = None
        
        # Plugin state
        self.is_initialized = False
        self.meta_config = {}  # Store meta configuration
        
        Output.Console(self.plugin_name, "ExtractTableSeleniumPlugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for ExtractTableSelenium plugin configuration.
        Called by the meta plugin to configure browser settings before execution.
        
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
                # Update browser config with meta settings
                self.browser_config.update(browser_config)
                Output.Console(self.plugin_name, f"Browser configuration updated: {browser_config}")
            
            # Process options
            options = config.get("options", [])
            if options:
                self.browser_config["options"] = options
                Output.Console(self.plugin_name, f"Browser options configured: {len(options)} options")
            
            # Process timeout settings
            timeout = config.get("timeout")
            if timeout:
                self.browser_config["timeout"] = timeout
                Output.Console(self.plugin_name, f"Timeout configured: {timeout}")
            
            # Process window size
            window_size = config.get("window_size")
            if window_size:
                self.browser_config["window_size"] = window_size
                Output.Console(self.plugin_name, f"Window size configured: {window_size}")
            
            # Process user agent
            user_agent = config.get("user_agent")
            if user_agent:
                self.browser_config["user_agent"] = user_agent
                Output.Console(self.plugin_name, f"User agent configured: {user_agent}")
            
            return {
                "success": True,
                "browser_configured": bool(browser_config),
                "options_count": len(options),
                "timeout": self.browser_config.get("timeout"),
                "window_size": self.browser_config.get("window_size")
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_commands(self) -> List[str]:
        """Return available commands for this plugin."""
        return [
            "extract_table",
            "navigate_to",
            "wait_for_element",
            "scroll_to_element",
            "click_element",
            "get_page_source",
            "take_screenshot",
            "close_browser"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Execute a plugin operator."""
        try:
            if operator == "extract_table":
                return self._extract_table(config)
            elif operator == "navigate_to":
                return self._navigate_to(config)
            elif operator == "wait_for_element":
                return self._wait_for_element(config)
            elif operator == "scroll_to_element":
                return self._scroll_to_element(config)
            elif operator == "click_element":
                return self._click_element(config)
            elif operator == "get_page_source":
                return self._get_page_source(config)
            elif operator == "take_screenshot":
                return self._take_screenshot(config)
            elif operator == "close_browser":
                return self._close_browser(config)
            else:
                raise ValueError(f"Unknown operator: {operator}")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing operator '{operator}': {e}")
            raise
    
    def _initialize_driver(self) -> bool:
        """Initialize the WebDriver if not already done."""
        if self.is_initialized and self.driver:
            return True
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not available. Please install it with: pip install selenium webdriver-manager")
        
        try:
            browser = self.browser_config.get("browser", "chrome").lower()
            headless = self.browser_config.get("headless", True)
            timeout = self.browser_config.get("timeout", 30)
            implicit_wait = self.browser_config.get("implicit_wait", 10)
            window_size = self.browser_config.get("window_size", "1920x1080")
            user_agent = self.browser_config.get("user_agent", "")
            
            if browser == "chrome":
                options = ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                if user_agent:
                    options.add_argument(f"--user-agent={user_agent}")
                
                # Try to use webdriver-manager for automatic driver management
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    from selenium.webdriver.chrome.service import Service
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except ImportError:
                    # Fallback to system ChromeDriver
                    self.driver = webdriver.Chrome(options=options)
                    
            elif browser == "firefox":
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                if user_agent:
                    options.set_preference("general.useragent.override", user_agent)
                
                try:
                    from webdriver_manager.firefox import GeckoDriverManager
                    from selenium.webdriver.firefox.service import Service
                    service = Service(GeckoDriverManager().install())
                    self.driver = webdriver.Firefox(service=service, options=options)
                except ImportError:
                    self.driver = webdriver.Firefox(options=options)
                    
            elif browser == "edge":
                options = EdgeOptions()
                if headless:
                    options.add_argument("--headless")
                if user_agent:
                    options.add_argument(f"--user-agent={user_agent}")
                
                try:
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    from selenium.webdriver.edge.service import Service
                    service = Service(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=service, options=options)
                except ImportError:
                    self.driver = webdriver.Edge(options=options)
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
            # Configure driver
            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_window_size(*map(int, window_size.split('x')))
            
            # Create WebDriverWait instance
            self.wait = WebDriverWait(self.driver, timeout)
            
            self.is_initialized = True
            Output.Console(self.plugin_name, f"WebDriver initialized for {browser}")
            return True
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Failed to initialize WebDriver: {e}")
            return False
    
    def _extract_table(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from HTML table using Selenium."""
        try:
            # Initialize driver if needed
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            # Extract configuration parameters
            selector = self.interpolate_variables(config.get("selector", "table"))
            result_var = config.get("id", "table_data")
            
            # Get table configuration
            table_config = config.get("config", {})
            filters = config.get("filters", {})
            transform = config.get("transform", {})
            pagination = config.get("pagination", {})
            validation = config.get("validation", {})
            complex_config = config.get("complex", {})
            
            # Navigate to URL if provided
            url = config.get("url")
            if url:
                url = self.interpolate_variables(url)
                self.driver.get(url)
                Output.Console(self.plugin_name, f"Navigated to: {url}")
            
            # Wait for table to be present
            wait_time = config.get("wait", 5)
            if wait_time > 0:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    Output.Console(self.plugin_name, f"Table found with selector: {selector}")
                except TimeoutException:
                    Output.Console(self.plugin_name, f"Timeout waiting for table: {selector}")
            
            # Extract table data
            extracted_data = self._extract_table_data(
                selector, table_config, filters, transform, 
                pagination, validation, complex_config
            )
            
            # Store result in Sugar memory
            if self.context and hasattr(self.context, 'memory_handler'):
                self.context.memory_handler.set_variable(result_var, extracted_data)
                Output.Console(self.plugin_name, f"Table data stored in variable: {result_var}")
            
            return {
                "success": True,
                "data": extracted_data,
                "rows_extracted": len(extracted_data) if isinstance(extracted_data, list) else 0,
                "result_variable": result_var
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error extracting table: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    def _extract_table_data(self, selector: str, config: Dict, filters: Dict, 
                           transform: Dict, pagination: Dict, validation: Dict, 
                           complex_config: Dict) -> List[Dict]:
        """Extract and process table data."""
        try:
            # Find table element
            table_element = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # Handle pagination if configured
            if pagination:
                return self._extract_with_pagination(table_element, config, filters, 
                                                   transform, pagination, validation, complex_config)
            else:
                return self._extract_single_table(table_element, config, filters, 
                                                transform, validation, complex_config)
                
        except NoSuchElementException:
            Output.Console(self.plugin_name, f"Table not found with selector: {selector}")
            return []
        except Exception as e:
            Output.Console(self.plugin_name, f"Error extracting table data: {e}")
            return []
    
    def _extract_single_table(self, table_element, config: Dict, filters: Dict, 
                             transform: Dict, validation: Dict, complex_config: Dict) -> List[Dict]:
        """Extract data from a single table."""
        # Get table configuration
        headers_config = config.get("headers", "first_row")
        format_type = config.get("format", "objects")
        scope = config.get("scope", "tbody")
        
        # Determine table scope
        if scope == "tbody":
            rows = table_element.find_elements(By.CSS_SELECTOR, "tbody tr")
        elif scope == "thead":
            rows = table_element.find_elements(By.CSS_SELECTOR, "thead tr")
        elif scope == "tfoot":
            rows = table_element.find_elements(By.CSS_SELECTOR, "tfoot tr")
        elif scope == "all":
            rows = table_element.find_elements(By.CSS_SELECTOR, "tr")
        else:
            # Custom CSS selector
            rows = table_element.find_elements(By.CSS_SELECTOR, scope)
        
        if not rows:
            Output.Console(self.plugin_name, "No rows found in table")
            return []
        
        # Extract headers
        headers = self._extract_headers(rows, headers_config, complex_config)
        
        # Extract and filter rows
        raw_data = self._extract_rows(rows, headers, filters, complex_config)
        
        # Apply transformations
        transformed_data = self._apply_transformations(raw_data, transform)
        
        # Apply validation
        validated_data = self._apply_validation(transformed_data, validation)
        
        # Format output
        return self._format_output(validated_data, format_type, headers)
    
    def _extract_headers(self, rows: List, headers_config: Any, complex_config: Dict) -> List[str]:
        """Extract table headers based on configuration."""
        if isinstance(headers_config, list):
            return headers_config
        elif headers_config == "none":
            return []
        elif headers_config == "skip":
            return []
        else:  # "first_row" or default
            if rows:
                header_row = rows[0]
                header_cells = header_row.find_elements(By.CSS_SELECTOR, "th, td")
                headers = [cell.text.strip() for cell in header_cells]
                
                # Handle multi-header strategy
                header_depth = complex_config.get("header_depth", 1)
                if header_depth > 1 and len(rows) >= header_depth:
                    return self._extract_multi_headers(rows[:header_depth], complex_config)
                
                return headers
            return []
    
    def _extract_multi_headers(self, header_rows: List, complex_config: Dict) -> List[str]:
        """Extract headers from multiple header rows."""
        strategy = complex_config.get("multi_header_strategy", "combine")
        
        if strategy == "combine":
            combined_headers = []
            for row in header_rows:
                cells = row.find_elements(By.CSS_SELECTOR, "th, td")
                row_headers = [cell.text.strip() for cell in cells]
                combined_headers.extend(row_headers)
            return combined_headers
        else:  # hierarchy
            # For hierarchy, we'll use the last header row as primary headers
            last_row = header_rows[-1]
            cells = last_row.find_elements(By.CSS_SELECTOR, "th, td")
            return [cell.text.strip() for cell in cells]
    
    def _extract_rows(self, rows: List, headers: List, filters: Dict, complex_config: Dict) -> List[Dict]:
        """Extract data from table rows with filtering."""
        data = []
        start_row = 0
        
        # Apply row filters
        skip_rows = filters.get("skip_rows", 0)
        max_rows = filters.get("max_rows")
        skip_footer = filters.get("skip_footer", 0)
        row_index_filter = filters.get("row_index", "all")
        
        # Adjust start row based on headers and skip_rows
        if headers and len(rows) > 0:
            start_row = 1  # Skip header row
        start_row += skip_rows
        
        # Calculate end row
        end_row = len(rows) - skip_footer
        if max_rows:
            end_row = min(end_row, start_row + max_rows)
        
        for i, row in enumerate(rows[start_row:end_row], start_row):
            # Apply row index filter
            if row_index_filter == "even" and i % 2 != 0:
                continue
            elif row_index_filter == "odd" and i % 2 == 0:
                continue
            
            # Extract row data
            row_data = self._extract_row_data(row, headers, complex_config)
            
            # Apply row condition filter
            if "row_condition" in filters:
                if not self._evaluate_row_condition(row_data, filters["row_condition"], i):
                    continue
            
            # Apply column filters
            if not self._apply_column_filters(row_data, filters):
                continue
            
            data.append(row_data)
        
        return data
    
    def _extract_row_data(self, row_element, headers: List, complex_config: Dict) -> Dict:
        """Extract data from a single row."""
        cells = row_element.find_elements(By.CSS_SELECTOR, "th, td")
        row_data = {}
        
        for i, cell in enumerate(cells):
            # Handle colspan and rowspan
            colspan = int(cell.get_attribute("colspan") or 1)
            rowspan = int(cell.get_attribute("rowspan") or 1)
            
            cell_text = cell.text.strip()
            
            # Handle complex table structures
            colspan_strategy = complex_config.get("colspan", "merge")
            rowspan_strategy = complex_config.get("rowspan", "fill")
            
            if colspan > 1 and colspan_strategy == "merge":
                # Repeat the value across spanned columns
                for j in range(colspan):
                    if i + j < len(headers):
                        key = headers[i + j] if headers else str(i + j)
                        row_data[key] = cell_text
            elif colspan > 1 and colspan_strategy == "skip":
                # Skip spanned columns
                continue
            elif colspan > 1 and colspan_strategy == "null":
                # Fill with null values
                for j in range(colspan):
                    if i + j < len(headers):
                        key = headers[i + j] if headers else str(i + j)
                        row_data[key] = None
            else:
                # Normal cell
                if i < len(headers):
                    key = headers[i] if headers else str(i)
                    row_data[key] = cell_text
        
        return row_data
    
    def _evaluate_row_condition(self, row_data: Dict, condition: str, row_index: int) -> bool:
        """Evaluate a row condition."""
        try:
            # Create a safe evaluation context
            context = {
                "row": row_data,
                "index": row_index,
                "values": list(row_data.values())
            }
            
            # Simple condition evaluation (basic implementation)
            # In a real implementation, you'd want a more robust expression evaluator
            condition = condition.replace("{{row[", "row_data.get(").replace("]}}", ", '')")
            condition = condition.replace("{{index}}", str(row_index))
            
            # This is a simplified evaluation - in production, use a proper expression parser
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            Output.Console(self.plugin_name, f"Error evaluating row condition: {e}")
            return True  # Default to include row on error
    
    def _apply_column_filters(self, row_data: Dict, filters: Dict) -> bool:
        """Apply column-based filters to a row."""
        # Skip columns filter
        skip_columns = filters.get("skip_columns", [])
        if skip_columns:
            for col_index in skip_columns:
                if str(col_index) in row_data:
                    del row_data[str(col_index)]
        
        # Required columns filter
        required_columns = filters.get("required_columns", [])
        if required_columns:
            for col_index in required_columns:
                col_key = str(col_index)
                if col_key not in row_data or not row_data[col_key]:
                    return False
        
        # Minimum columns filter
        min_columns = filters.get("min_columns")
        if min_columns and len(row_data) < min_columns:
            return False
        
        return True
    
    def _apply_transformations(self, data: List[Dict], transform: Dict) -> List[Dict]:
        """Apply data transformations."""
        if not transform:
            return data
        
        transformed_data = []
        
        for row in data:
            transformed_row = row.copy()
            
            # Column transformations
            columns_transform = transform.get("columns", {})
            for col_key, transform_func in columns_transform.items():
                if col_key in transformed_row:
                    transformed_row[col_key] = self._apply_column_transform(
                        transformed_row[col_key], transform_func
                    )
            
            # Custom transformations
            custom_transform = transform.get("custom", {})
            for new_key, expression in custom_transform.items():
                transformed_row[new_key] = self._evaluate_custom_expression(expression, row)
            
            # Column renaming
            rename_map = transform.get("rename", {})
            for old_key, new_key in rename_map.items():
                if old_key in transformed_row:
                    transformed_row[new_key] = transformed_row.pop(old_key)
            
            transformed_data.append(transformed_row)
        
        return transformed_data
    
    def _apply_column_transform(self, value: Any, transform_func: str) -> Any:
        """Apply a transformation function to a column value."""
        if not value:
            return value
        
        try:
            if transform_func == "parse_int":
                return int(str(value).replace(",", ""))
            elif transform_func == "parse_float":
                return float(str(value).replace(",", ""))
            elif transform_func == "trim":
                return str(value).strip()
            elif transform_func == "lowercase":
                return str(value).lower()
            elif transform_func == "uppercase":
                return str(value).upper()
            elif transform_func.startswith("parse_currency"):
                # Extract currency code and parse
                currency_code = "USD"  # Default
                if "(" in transform_func and ")" in transform_func:
                    currency_code = transform_func.split("(")[1].split(")")[0]
                return self._parse_currency(value, currency_code)
            elif transform_func.startswith("parse_date"):
                # Extract date format and parse
                date_format = "%Y-%m-%d"  # Default
                if "(" in transform_func and ")" in transform_func:
                    date_format = transform_func.split("(")[1].split(")")[0]
                return self._parse_date(value, date_format)
            elif transform_func.startswith("regex_replace"):
                # Extract pattern and replacement
                if "(" in transform_func and ")" in transform_func:
                    pattern = transform_func.split("(")[1].split(")")[0]
                    return re.sub(pattern, "", str(value))
            elif transform_func.startswith("substring"):
                # Extract start and end indices
                if "(" in transform_func and ")" in transform_func:
                    indices = transform_func.split("(")[1].split(")")[0].split(",")
                    start = int(indices[0].strip())
                    end = int(indices[1].strip()) if len(indices) > 1 else None
                    return str(value)[start:end]
            elif transform_func.startswith("default"):
                # Extract default value
                if "(" in transform_func and ")" in transform_func:
                    default_value = transform_func.split("(")[1].split(")")[0]
                    return value if value else default_value
            
            return value
        except Exception as e:
            Output.Console(self.plugin_name, f"Error applying transform {transform_func}: {e}")
            return value
    
    def _evaluate_custom_expression(self, expression: str, row_data: Dict) -> Any:
        """Evaluate a custom transformation expression."""
        try:
            # Replace row references
            for key, value in row_data.items():
                expression = expression.replace(f"{{{{row.{key}}}}}", str(value))
            
            # Handle special functions
            if "generate_uuid()" in expression:
                expression = expression.replace("generate_uuid()", f"'{str(uuid.uuid4())}'")
            elif "now(" in expression and ")" in expression:
                # Extract date format
                start = expression.find("now(") + 4
                end = expression.find(")", start)
                date_format = expression[start:end]
                current_time = datetime.now().strftime(date_format)
                expression = expression.replace(f"now({date_format})", f"'{current_time}'")
            
            # Safe evaluation
            return eval(expression, {"__builtins__": {}}, {})
        except Exception as e:
            Output.Console(self.plugin_name, f"Error evaluating custom expression: {e}")
            return None
    
    def _parse_currency(self, value: str, currency_code: str) -> float:
        """Parse currency value."""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', str(value))
            return float(cleaned)
        except:
            return 0.0
    
    def _parse_date(self, value: str, date_format: str) -> str:
        """Parse date value."""
        try:
            # This is a simplified date parser
            # In production, you'd want a more robust date parsing library
            return value  # Return as string for now
        except:
            return value
    
    def _apply_validation(self, data: List[Dict], validation: Dict) -> List[Dict]:
        """Apply data validation."""
        if not validation:
            return data
        
        validated_data = []
        on_error = validation.get("on_error", "skip_row")
        
        for row in data:
            try:
                # Required fields validation
                required_fields = validation.get("required", [])
                for field in required_fields:
                    if field not in row or not row[field]:
                        if on_error == "abort":
                            raise ValueError(f"Required field missing: {field}")
                        elif on_error == "null_value":
                            row[field] = None
                        elif on_error == "skip_row":
                            raise ValueError(f"Required field missing: {field}")
                
                # Type validation
                type_specs = validation.get("types", {})
                for field, expected_type in type_specs.items():
                    if field in row:
                        if not self._validate_type(row[field], expected_type):
                            if on_error == "abort":
                                raise ValueError(f"Invalid type for field {field}")
                            elif on_error == "null_value":
                                row[field] = None
                            elif on_error == "skip_row":
                                raise ValueError(f"Invalid type for field {field}")
                
                validated_data.append(row)
                
            except ValueError as e:
                if on_error == "skip_row":
                    Output.Console(self.plugin_name, f"Skipping row due to validation error: {e}")
                    continue
                else:
                    raise
        
        return validated_data
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate if a value matches the expected type."""
        try:
            if expected_type == "string":
                return isinstance(value, str)
            elif expected_type == "number":
                return isinstance(value, (int, float))
            elif expected_type == "integer":
                return isinstance(value, int)
            elif expected_type == "boolean":
                return isinstance(value, bool)
            elif expected_type == "date":
                # Simplified date validation
                return isinstance(value, str) and len(value) > 0
            elif expected_type == "currency":
                return isinstance(value, (int, float)) or (isinstance(value, str) and re.match(r'[\d.,]+', value))
            else:
                return True
        except:
            return False
    
    def _format_output(self, data: List[Dict], format_type: str, headers: List[str]) -> Any:
        """Format the output data according to the specified format."""
        if format_type == "arrays":
            # Convert to array format
            if headers:
                return [headers] + [[row.get(header, "") for header in headers] for row in data]
            else:
                return [[row.get(str(i), "") for i in range(len(row))] for row in data]
        elif format_type == "key_value":
            # Convert to key-value format using first column as key
            if headers and data:
                key_field = headers[0]
                return {row.get(key_field, str(i)): row for i, row in enumerate(data)}
            else:
                return {str(i): row for i, row in enumerate(data)}
        else:  # "objects" (default)
            return data
    
    def _extract_with_pagination(self, table_element, config: Dict, filters: Dict, 
                                transform: Dict, pagination: Dict, validation: Dict, 
                                complex_config: Dict) -> List[Dict]:
        """Extract data with pagination support."""
        all_data = []
        current_page = 1
        max_pages = pagination.get("max_pages", 10)
        page_load_wait = pagination.get("page_load_wait", 2)
        stop_condition = pagination.get("stop_condition")
        
        while current_page <= max_pages:
            # Extract current page data
            page_data = self._extract_single_table(table_element, config, filters, 
                                                 transform, validation, complex_config)
            all_data.extend(page_data)
            
            # Check stop condition
            if stop_condition and self._evaluate_stop_condition(page_data, stop_condition):
                break
            
            # Try to go to next page
            next_page_selector = pagination.get("next_page")
            if next_page_selector:
                if not self._navigate_to_next_page(next_page_selector, page_load_wait):
                    break
            
            current_page += 1
        
        return all_data
    
    def _evaluate_stop_condition(self, page_data: List[Dict], condition: str) -> bool:
        """Evaluate pagination stop condition."""
        try:
            # Simple condition evaluation
            if condition == "no_more_data" and not page_data:
                return True
            elif condition.startswith("row_count_less_than"):
                min_rows = int(condition.split("_")[-1])
                return len(page_data) < min_rows
            else:
                # Custom condition evaluation
                return eval(condition, {"__builtins__": {}}, {"data": page_data})
        except Exception as e:
            Output.Console(self.plugin_name, f"Error evaluating stop condition: {e}")
            return False
    
    def _navigate_to_next_page(self, next_page_selector: str, wait_time: int) -> bool:
        """Navigate to the next page."""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, next_page_selector)
            
            # Check if button is clickable
            if not next_button.is_enabled() or not next_button.is_displayed():
                return False
            
            # Scroll to element and click
            self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(0.5)
            
            next_button.click()
            time.sleep(wait_time)
            
            return True
        except (NoSuchElementException, ElementClickInterceptedException):
            return False
        except Exception as e:
            Output.Console(self.plugin_name, f"Error navigating to next page: {e}")
            return False
    
    def _navigate_to(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            url = self.interpolate_variables(config.get("url"))
            if not url:
                raise ValueError("URL is required")
            
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            self.driver.get(url)
            
            # Wait for page load
            wait_time = config.get("wait", 5)
            if wait_time > 0:
                time.sleep(wait_time)
            
            return {"success": True, "url": url}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _wait_for_element(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for an element to be present."""
        try:
            selector = self.interpolate_variables(config.get("selector"))
            timeout = config.get("timeout", 30)
            
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            return {"success": True, "element_found": True}
            
        except TimeoutException:
            return {"success": False, "error": "Element not found within timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _scroll_to_element(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll to an element."""
        try:
            selector = self.interpolate_variables(config.get("selector"))
            
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _click_element(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Click an element."""
        try:
            selector = self.interpolate_variables(config.get("selector"))
            wait_after = config.get("wait_after", 1)
            
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            
            if wait_after > 0:
                time.sleep(wait_after)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_page_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current page source."""
        try:
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            page_source = self.driver.page_source
            result_var = config.get("id", "page_source")
            
            if self.context and hasattr(self.context, 'memory_handler'):
                self.context.memory_handler.set_variable(result_var, page_source)
            
            return {"success": True, "result_variable": result_var}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _take_screenshot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            if not self._initialize_driver():
                raise Exception("Failed to initialize WebDriver")
            
            filename = config.get("filename", f"screenshot_{int(time.time())}.png")
            self.driver.save_screenshot(filename)
            
            return {"success": True, "filename": filename}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _close_browser(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Close the browser."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.is_initialized = False
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Clean up plugin resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.is_initialized = False
            Output.Console(self.plugin_name, "Plugin cleanup completed")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error during cleanup: {e}")