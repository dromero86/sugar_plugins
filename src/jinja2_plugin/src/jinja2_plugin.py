"""
Jinja2 Plugin for Sugar

This plugin provides Jinja2 templating capabilities as a proper Sugar plugin.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from jinja2 import Environment, StrictUndefined, TemplateError

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class Jinja2Plugin(PluginBase):
    """
    Jinja2 Plugin for Sugar
    
    This plugin provides Jinja2 templating capabilities that can be used
    in task flows with the syntax:
    {
      "jinja2": {
        "operator": "parser",
        "template": "template string",
        "result": "variable_name"
      }
    }
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Jinja2 templating for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []
    REQUIREMENTS = ["Jinja2>=3.1.0", "MarkupSafe>=2.1.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Jinja2 Plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Initialize Jinja2 environment
        self.jinja_env = self._create_environment()
        self._template_cache = {}
        
        Output.Console(self.plugin_name, "Jinja2 Plugin initialized")
    
    def _create_environment(self) -> Environment:
        """Create and configure Jinja2 environment"""
        env = Environment(
            autoescape=True,
            undefined=StrictUndefined,
            extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Registrar filtros personalizados
        env.filters.update(self._get_custom_filters())
        
        # Registrar funciones personalizadas
        env.globals.update(self._get_custom_functions())
        
        return env
    
    def _get_custom_filters(self) -> Dict[str, callable]:
        """Get custom filters for Sugar integration"""
        return {
            'json': lambda x: json.dumps(x, indent=2, ensure_ascii=False),
            'format_currency': self._format_currency,
            'format_date': self._format_date,
            'format_datetime': self._format_datetime,
            'percentage': lambda x: f"{x * 100:.1f}%",
            'safe_html': lambda x: x,
            'truncate': self._truncate,
            'round': lambda x, precision=0: round(float(x), precision),
            'upper': lambda x: str(x).upper() if x else '',
            'lower': lambda x: str(x).lower() if x else '',
            'title': lambda x: str(x).title() if x else '',
            'capitalize': lambda x: str(x).capitalize() if x else '',
            'default': lambda x, default='': x if x else default,
            'length': lambda x: len(x) if hasattr(x, '__len__') else 0,
            'sum': lambda x, attribute=None: self._sum_filter(x, attribute),
            'map': lambda x, attribute=None: self._map_filter(x, attribute),
            'selectattr': lambda x, attr, test, value=None: self._selectattr_filter(x, attr, test, value),
            'unique': lambda x: list(dict.fromkeys(x)) if x else [],
            'sort': lambda x, attribute=None, reverse=False: self._sort_filter(x, attribute, reverse),
            'slice': lambda x, start, end=None: x[start:end] if x else [],
            'list': lambda x: list(x) if x else [],
            'dict': lambda x: dict(x) if x else {},
            'int': lambda x: int(x) if x else 0,
            'float': lambda x: float(x) if x else 0.0,
            'str': lambda x: str(x) if x else '',
            'bool': lambda x: bool(x),
            'abs': lambda x: abs(x) if isinstance(x, (int, float)) else x,
            'min': lambda x: min(x) if x else None,
            'max': lambda x: max(x) if x else None,
            'avg': lambda x: sum(x) / len(x) if x else 0,
            'count': lambda x, value=None: x.count(value) if hasattr(x, 'count') else 0,
            'replace': lambda x, old, new: str(x).replace(old, new) if x else '',
            'split': lambda x, delimiter=' ': str(x).split(delimiter) if x else [],
            'join': lambda x, delimiter=' ': delimiter.join(str(item) for item in x) if x else '',
            'strip': lambda x: str(x).strip() if x else '',
            'lstrip': lambda x: str(x).lstrip() if x else '',
            'rstrip': lambda x: str(x).rstrip() if x else '',
        }
    
    def _get_custom_functions(self) -> Dict[str, callable]:
        """Get custom functions for Sugar integration"""
        return {
            'get_variable': self._get_variable,
            'format_datetime': self._format_datetime,
            'calculate_total': self._calculate_total,
            'is_empty': self._is_empty,
            'now': datetime.now,
            'today': lambda: datetime.now().date(),
            'range': range,
            'len': len,
            'type': type,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'dir': dir,
            'vars': vars,
            'locals': locals,
            'globals': globals,
        }
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available Jinja2 commands.
        
        Returns:
            List of available command names
        """
        return [
            "parser",
            "validate",
            "info",
            "clear_cache"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a Jinja2 command.
        
        Args:
            command: Command to execute
            config: Configuration for the command
            
        Returns:
            Command result
        """
        try:
            if command == "parser":
                return self._parse_template(config)
            elif command == "validate":
                return self._validate_template(config)
            elif command == "info":
                return self._get_template_info(config)
            elif command == "clear_cache":
                return self._clear_cache(config)
            else:
                Output.Console(self.plugin_name, f"Unknown Jinja2 command: {command}")
                return {"success": False, "error": f"Unknown command: {command}"}
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_template(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and render a Jinja2 template.
        
        Args:
            config: Configuration with template and result variable
            
        Returns:
            Processing result
        """
        try:
            template = config.get("template")
            result_var = config.get("result")
            
            if not template:
                return {"success": False, "error": "Template not provided"}
            
            if not result_var:
                return {"success": False, "error": "Result variable not provided"}
            
            # Get memory handler from context
            memory_handler = getattr(self.context, 'memory_handler', None)
            if not memory_handler:
                return {"success": False, "error": "Memory handler not available"}
            
            # Build context from memory
            context = self._build_context(memory_handler)
            
            # Process template
            result = self._render_template(template, context)
            
            # Store result in memory
            memory_handler.set_variable(result_var, result)
            
            Output.Console(self.plugin_name, f"Jinja2 template processed and stored in '{result_var}'")
            return {
                "success": True,
                "template": template,
                "result": result,
                "result_variable": result_var
            }
                
        except Exception as e:
            return {"success": False, "error": f"Template processing error: {str(e)}"}
    
    def _render_template(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template.
        
        Args:
            template_string: The template string to render
            context: Context variables
            
        Returns:
            The rendered template string
        """
        try:
            # Check cache first
            template_hash = hash(template_string)
            if template_hash in self._template_cache:
                template = self._template_cache[template_hash]
            else:
                template = self.jinja_env.from_string(template_string)
                self._template_cache[template_hash] = template
            
            return template.render(**context)
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Jinja2 rendering failed: {e}")
            raise
    
    def _build_context(self, memory_handler) -> Dict[str, Any]:
        """Build context from memory handler"""
        context = {}
        
        try:
            if hasattr(memory_handler, 'stack') and memory_handler.stack:
                context.update(memory_handler.stack[-1])
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting memory variables: {e}")
        
        return context
    
    def _validate_template(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a Jinja2 template.
        
        Args:
            config: Configuration with template
            
        Returns:
            Validation result
        """
        try:
            template = config.get("template", "")
            
            result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'template_type': self._detect_template_type(template),
                'variables_used': [],
                'jinja2_features': []
            }
            
            # Extract variables used
            jinja2_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', template)
            result['variables_used'] = [var.strip() for var in jinja2_vars]
            
            # Check for Jinja2 features
            if re.search(r'\{%\s*if\s+', template):
                result['jinja2_features'].append('conditionals')
            if re.search(r'\{%\s*for\s+', template):
                result['jinja2_features'].append('loops')
            if re.search(r'\{\{[^}]+\|[^}]+\}\}', template):
                result['jinja2_features'].append('filters')
            if re.search(r'\{%\s*(block|extends|include)', template):
                result['jinja2_features'].append('template_inheritance')
            
            # Validate Jinja2 syntax
            try:
                self.jinja_env.from_string(template)
            except TemplateError as e:
                result['valid'] = False
                result['errors'].append(f"Jinja2 syntax error: {str(e)}")
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'template_type': 'unknown',
                'variables_used': [],
                'jinja2_features': []
            }
    
    def _get_template_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a template.
        
        Args:
            config: Configuration with template
            
        Returns:
            Template information
        """
        try:
            template = config.get("template", "")
            
            info = {
                'length': len(template),
                'template_type': self._detect_template_type(template),
                'variable_count': 0,
                'jinja2_features': [],
                'complexity': 'simple'
            }
            
            # Count variables
            jinja2_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', template)
            info['variable_count'] = len(jinja2_vars)
            
            # Check features
            if re.search(r'\{%\s*if\s+', template):
                info['jinja2_features'].append('conditionals')
            if re.search(r'\{%\s*for\s+', template):
                info['jinja2_features'].append('loops')
            if re.search(r'\{\{[^}]+\|[^}]+\}\}', template):
                info['jinja2_features'].append('filters')
            if re.search(r'\{%\s*(block|extends|include)', template):
                info['jinja2_features'].append('template_inheritance')
            
            # Determine complexity
            if len(info['jinja2_features']) > 2 or info['variable_count'] > 10:
                info['complexity'] = 'complex'
            elif len(info['jinja2_features']) > 0 or info['variable_count'] > 5:
                info['complexity'] = 'moderate'
            
            return info
            
        except Exception as e:
            return {
                'error': str(e),
                'length': 0,
                'template_type': 'unknown',
                'variable_count': 0,
                'jinja2_features': [],
                'complexity': 'unknown'
            }
    
    def _clear_cache(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clear template cache.
        
        Args:
            config: Configuration (unused)
            
        Returns:
            Clear result
        """
        try:
            cache_size = len(self._template_cache)
            self._template_cache.clear()
            Output.Console(self.plugin_name, f"Template cache cleared ({cache_size} templates)")
            return {"success": True, "cache_size_before": cache_size, "cache_size_after": 0}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _detect_template_type(self, text: str) -> str:
        """Detect the type of template syntax used in the text"""
        if not text:
            return 'basic'
        
        jinja2_patterns = [
            r'\{%\s*(if|for|while|with|block|macro|set|include|extends)',
            r'\{\{\s*[^}]+\|[^}]+\}\}',
            r'\{\{\s*[^}]+\s*\+\s*[^}]+\}\}',
            r'\{\{\s*loop\.',
        ]
        
        basic_patterns = [
            r'\{\{[^}]+\}\}',
            r'\$\{[^}]+\}',
            r'\$[a-zA-Z_][a-zA-Z0-9_]*'
        ]
        
        has_jinja2 = any(re.search(pattern, text) for pattern in jinja2_patterns)
        has_basic = any(re.search(pattern, text) for pattern in basic_patterns)
        
        if has_jinja2 and has_basic:
            return 'mixed'
        elif has_jinja2:
            return 'jinja2'
        elif has_basic:
            return 'basic'
        else:
            return 'basic'
    
    def _get_variable(self, var_path: str) -> Any:
        """Get variable value (for Jinja2 functions)"""
        # This is a placeholder - in practice, this would need access to the current memory handler
        return None
    
    # Custom filter implementations
    def _format_currency(self, value: Union[int, float], currency: str = "EUR") -> str:
        """Format value as currency"""
        try:
            if currency == "EUR":
                return f"€{value:,.2f}"
            elif currency == "USD":
                return f"${value:,.2f}"
            else:
                return f"{value:,.2f} {currency}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_date(self, value: Any, format_str: str = "%Y-%m-%d") -> str:
        """Format date value"""
        try:
            if isinstance(value, str):
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return dt.strftime(format_str)
                    except ValueError:
                        continue
            elif hasattr(value, 'strftime'):
                return value.strftime(format_str)
            return str(value)
        except Exception:
            return str(value)
    
    def _format_datetime(self, value: Any, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime value"""
        return self._format_date(value, format_str)
    
    def _truncate(self, value: str, length: int = 50, suffix: str = "...") -> str:
        """Truncate string to specified length"""
        if not value:
            return ""
        value_str = str(value)
        if len(value_str) <= length:
            return value_str
        return value_str[:length] + suffix
    
    def _sum_filter(self, items: list, attribute: Optional[str] = None) -> Union[int, float]:
        """Sum filter with optional attribute"""
        if not items:
            return 0
        try:
            if attribute:
                return sum(item.get(attribute, 0) for item in items)
            else:
                return sum(items)
        except (TypeError, ValueError):
            return 0
    
    def _map_filter(self, items: list, attribute: Optional[str] = None) -> list:
        """Map filter with optional attribute"""
        if not items:
            return []
        try:
            if attribute:
                return [item.get(attribute) for item in items]
            else:
                return list(items)
        except (TypeError, AttributeError):
            return []
    
    def _selectattr_filter(self, items: list, attr: str, test: str, value: Any = None) -> list:
        """Select items by attribute test"""
        if not items:
            return []
        
        def test_func(item):
            try:
                item_value = item.get(attr) if isinstance(item, dict) else getattr(item, attr, None)
                if test == 'equalto':
                    return item_value == value
                elif test == 'ge':
                    return item_value >= value
                elif test == 'gt':
                    return item_value > value
                elif test == 'le':
                    return item_value <= value
                elif test == 'lt':
                    return item_value < value
                elif test == 'ne':
                    return item_value != value
                elif test == 'true':
                    return bool(item_value)
                elif test == 'false':
                    return not bool(item_value)
                else:
                    return bool(item_value)
            except (TypeError, AttributeError):
                return False
        
        return [item for item in items if test_func(item)]
    
    def _sort_filter(self, items: list, attribute: Optional[str] = None, reverse: bool = False) -> list:
        """Sort filter with optional attribute"""
        if not items:
            return []
        try:
            if attribute:
                return sorted(items, key=lambda x: x.get(attribute, 0), reverse=reverse)
            else:
                return sorted(items, reverse=reverse)
        except (TypeError, AttributeError):
            return items
    
    def _calculate_total(self, items: list, attribute: str = "price") -> Union[int, float]:
        """Calculate total of items by attribute"""
        return self._sum_filter(items, attribute)
    
    def _is_empty(self, value: Any) -> bool:
        """Check if value is empty"""
        if value is None:
            return True
        if isinstance(value, (str, list, dict)):
            return len(value) == 0
        return False 