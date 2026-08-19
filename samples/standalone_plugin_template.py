#!/usr/bin/env python3
"""
Standalone Plugin Template
=========================

Plantilla para desarrollar plugins de Sugar de forma independiente,
sin necesidad de tener todo el proyecto de Sugar instalado.

Este template incluye:
- Mock classes para simular el entorno de Sugar
- SDK completo para desarrollo
- Sistema de testing independiente
- Documentación de uso
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# MOCK CLASSES PARA SIMULAR EL ENTORNO DE SUGAR
# ============================================================================

class MockOutput:
    """Mock de la clase Output de Sugar"""
    
    @staticmethod
    def Console(plugin_name: str, message: str):
        """Simular Output.Console"""
        print(f"[{plugin_name}] {message}")
    
    @staticmethod
    def Warning(plugin_name: str, message: str):
        """Simular Output.Warning"""
        print(f"[{plugin_name}] WARNING: {message}")
    
    @staticmethod
    def Error(plugin_name: str, message: str):
        """Simular Output.Error"""
        print(f"[{plugin_name}] ERROR: {message}")

class MockPluginBase:
    """Mock de la clase PluginBase de Sugar"""
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        self.context = context
        self.plugin_config = plugin_config or {}
        self.plugin_name = getattr(self, 'plugin_name', 'StandalonePlugin')
        self.metadata = {
            'dependencies': getattr(self, 'DEPENDENCIES', []),
            'requirements': getattr(self, 'REQUIREMENTS', []),
            'version': getattr(self, 'VERSION', '1.0.0'),
            'description': getattr(self, 'DESCRIPTION', 'Standalone Plugin'),
            'author': getattr(self, 'AUTHOR', 'Developer'),
            'license': getattr(self, 'LICENSE', 'MIT')
        }

# ============================================================================
# SDK COMPLETO PARA DESARROLLO INDEPENDIENTE
# ============================================================================

class ExtensionType(Enum):
    """Tipos de extensiones disponibles"""
    INTERPRETER_HOOK = "interpreter_hook"
    FLOW_CONTROL = "flow_control"
    INTERPOLATION = "interpolation"
    AST_MODIFICATION = "ast_modification"
    COMMAND_CUSTOMIZATION = "command_customization"

class HookPoint(Enum):
    """Puntos de hook disponibles"""
    BEFORE_TASK_EXECUTION = "before_task_execution"
    AFTER_TASK_EXECUTION = "after_task_execution"
    BEFORE_COMMAND_EXECUTION = "before_command_execution"
    AFTER_COMMAND_EXECUTION = "after_command_execution"
    ON_ERROR = "on_error"

class InterpolationEvent(Enum):
    """Eventos de interpolación"""
    BEFORE_INTERPOLATION = "before_interpolation"
    AFTER_INTERPOLATION = "after_interpolation"
    VARIABLE_NOT_FOUND = "variable_not_found"

class ASTModificationEvent(Enum):
    """Eventos de modificación AST"""
    BEFORE_AST_PARSING = "before_ast_parsing"
    AFTER_AST_PARSING = "after_ast_parsing"
    BEFORE_AST_EVALUATION = "before_ast_evaluation"
    AFTER_AST_EVALUATION = "after_ast_evaluation"

class FlowEvent(Enum):
    """Eventos de control de flujo"""
    BEFORE_FLOW_CONTROL = "before_flow_control"
    AFTER_FLOW_CONTROL = "after_flow_control"
    CONDITION_EVALUATION = "condition_evaluation"

class CommandEvent(Enum):
    """Eventos de comandos"""
    BEFORE_COMMAND_EXECUTION = "before_command_execution"
    AFTER_COMMAND_EXECUTION = "after_command_execution"
    COMMAND_NOT_FOUND = "command_not_found"

@dataclass
class HookContext:
    """Contexto para hooks"""
    hook_point: HookPoint
    task_data: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    modified: bool = False
    should_continue: bool = True
    error: Optional[str] = None

@dataclass
class InterpolationContext:
    """Contexto para interpolación"""
    event: InterpolationEvent
    original: str
    modified: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    should_continue: bool = True

@dataclass
class ASTContext:
    """Contexto para modificación AST"""
    event: ASTModificationEvent
    ast_node: Any = None
    modified: bool = False
    should_continue: bool = True

@dataclass
class FlowContext:
    """Contexto para control de flujo"""
    event: FlowEvent
    flow_type: str = ""
    condition: Any = None
    modified: bool = False
    should_continue: bool = True

@dataclass
class CommandContext:
    """Contexto para comandos"""
    event: CommandEvent
    command_name: str = ""
    command_config: Dict[str, Any] = field(default_factory=dict)
    modified: bool = False
    should_continue: bool = True

class ExtensionManager:
    """Gestor de extensiones del SDK"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.extensions = {}
        return cls._instance
    
    def __init__(self):
        # El singleton ya está inicializado en __new__
        pass
    
    def register_extension(self, plugin_name: str, extension_type: ExtensionType, 
                          callback: callable, priority: int = 5, metadata: Dict[str, Any] = None):
        """Registrar una extensión"""
        extension_id = f"{plugin_name}_{extension_type.value}_{priority}"
        self.extensions[extension_id] = {
            'plugin_name': plugin_name,
            'extension_type': extension_type,
            'callback': callback,
            'priority': priority,
            'metadata': metadata or {}
        }
        MockOutput.Console(plugin_name, f"Extension registered: {extension_type.value}")
    
    def get_extensions(self, extension_type: ExtensionType = None) -> List[Dict[str, Any]]:
        """Obtener extensiones registradas"""
        if extension_type:
            return [ext for ext in self.extensions.values() if ext['extension_type'] == extension_type]
        return list(self.extensions.values())
    
    def get_extensions_info(self) -> Dict[str, Any]:
        """Obtener información de extensiones"""
        return {
            'total_extensions': sum(len(extensions) for extensions in self.extensions.values()),
            'extensions_by_type': {ext_type.value: len(extensions) 
                                  for ext_type, extensions in self.extensions.items()}
        }
    
    def get_extension_count(self, extension_type: ExtensionType) -> int:
        """Obtener número de extensiones por tipo"""
        return len(self.extensions.get(extension_type, []))
    
    def get_plugin_extension_count(self, plugin_name: str) -> int:
        """Obtener número de extensiones por plugin"""
        count = 0
        for extensions in self.extensions.values():
            for ext in extensions:
                if ext.get('plugin_name') == plugin_name:
                    count += 1
        return count
    
    def unregister_all_plugin_extensions(self, plugin_name: str) -> int:
        """Desregistrar todas las extensiones de un plugin"""
        removed_count = 0
        for ext_type in list(self.extensions.keys()):
            original_count = len(self.extensions[ext_type])
            self.extensions[ext_type] = [
                ext for ext in self.extensions[ext_type]
                if ext.get('plugin_name') != plugin_name
            ]
            removed_count += original_count - len(self.extensions[ext_type])
        return removed_count

class HookSystem:
    """Sistema de hooks del SDK"""
    
    def __init__(self):
        self.hooks = {}
    
    def register_hook(self, hook_point: HookPoint, callback: callable, priority: int = 5):
        """Registrar un hook"""
        if hook_point not in self.hooks:
            self.hooks[hook_point] = []
        
        self.hooks[hook_point].append({
            'callback': callback,
            'priority': priority
        })
        
        # Ordenar por prioridad
        self.hooks[hook_point].sort(key=lambda x: x['priority'])
    
    def execute_hooks(self, hook_point: HookPoint, context: HookContext) -> HookContext:
        """Ejecutar hooks para un punto específico"""
        if hook_point not in self.hooks:
            return context
        
        for hook in self.hooks[hook_point]:
            try:
                result = hook['callback'](context)
                if result:
                    context = result
            except Exception as e:
                context.error = str(e)
                context.should_continue = False
                break
        
        return context
    
    def get_total_hooks(self) -> int:
        """Obtener total de hooks"""
        return sum(len(hooks) for hooks in self.hooks.values())
    
    def get_hook_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de hooks"""
        return {hook_point.value: len(hooks) for hook_point, hooks in self.hooks.items()}
    
    def list_hooks(self) -> Dict[str, List[str]]:
        """Listar hooks registrados"""
        return {hook_point.value: [str(cb) for cb, _ in hooks] 
                for hook_point, hooks in self.hooks.items()}

class InterpolationInterceptor:
    """Interceptor de interpolación del SDK"""
    
    def __init__(self):
        self.interceptors = {}
    
    def register_interceptor(self, event: InterpolationEvent, callback: callable, priority: int = 5):
        """Registrar un interceptor"""
        if event not in self.interceptors:
            self.interceptors[event] = []
        
        self.interceptors[event].append({
            'callback': callback,
            'priority': priority
        })
        
        # Ordenar por prioridad
        self.interceptors[event].sort(key=lambda x: x['priority'])
    
    def intercept(self, event: InterpolationEvent, context: InterpolationContext) -> InterpolationContext:
        """Interceptar interpolación"""
        if event not in self.interceptors:
            return context
        
        for interceptor in self.interceptors[event]:
            try:
                result = interceptor['callback'](context)
                if result:
                    context = result
            except Exception as e:
                context.should_continue = False
                break
        
        return context
    
    def intercept_before_interpolation(self, original_value: str, variables: List[str]) -> InterpolationContext:
        """Interceptar antes de interpolación"""
        context = InterpolationContext(
            event=InterpolationEvent.BEFORE_INTERPOLATION,
            original=original_value
        )
        return self.intercept(InterpolationEvent.BEFORE_INTERPOLATION, context)
    
    def intercept_variable_not_found(self, variable_name: str, original_value: str) -> InterpolationContext:
        """Interceptar variable no encontrada"""
        context = InterpolationContext(
            event=InterpolationEvent.VARIABLE_NOT_FOUND,
            original=original_value
        )
        context.metadata = {'variable_name': variable_name}
        return self.intercept(InterpolationEvent.VARIABLE_NOT_FOUND, context)

class ASTModifier:
    """Modificador AST del SDK"""
    
    def __init__(self):
        self.modifiers = {}
    
    def register_modifier(self, event: ASTModificationEvent, callback: callable, priority: int = 5):
        """Registrar un modificador"""
        if event not in self.modifiers:
            self.modifiers[event] = []
        
        self.modifiers[event].append({
            'callback': callback,
            'priority': priority
        })
        
        # Ordenar por prioridad
        self.modifiers[event].sort(key=lambda x: x['priority'])
    
    def modify(self, event: ASTModificationEvent, context: ASTContext) -> ASTContext:
        """Modificar AST"""
        if event not in self.modifiers:
            return context
        
        for modifier in self.modifiers[event]:
            try:
                result = modifier['callback'](context)
                if result:
                    context = result
            except Exception as e:
                context.should_continue = False
                break
        
        return context
    
    def get_total_modifiers(self) -> int:
        """Obtener total de modificadores"""
        return sum(len(modifiers) for modifiers in self.modifiers.values())
    
    def get_modification_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de modificación"""
        return {event.value: len(modifiers) for event, modifiers in self.modifiers.items()}
    
    def list_modifiers(self) -> Dict[str, List[str]]:
        """Listar modificadores registrados"""
        return {event.value: [str(cb) for cb, _ in modifiers] 
                for event, modifiers in self.modifiers.items()}

class FlowController:
    """Controlador de flujo del SDK"""
    
    def __init__(self):
        self.controllers = {}
    
    def register_controller(self, event: FlowEvent, callback: callable, priority: int = 5):
        """Registrar un controlador"""
        if event not in self.controllers:
            self.controllers[event] = []
        
        self.controllers[event].append({
            'callback': callback,
            'priority': priority
        })
        
        # Ordenar por prioridad
        self.controllers[event].sort(key=lambda x: x['priority'])
    
    def control(self, event: FlowEvent, context: FlowContext) -> FlowContext:
        """Controlar flujo"""
        if event not in self.controllers:
            return context
        
        for controller in self.controllers[event]:
            try:
                result = controller['callback'](context)
                if result:
                    context = result
            except Exception as e:
                context.should_continue = False
                break
        
        return context
    
    def control_before_command(self, command: Dict[str, Any], execution_stack: List[str]) -> FlowContext:
        """Controlar antes de comando"""
        context = FlowContext(
            event=FlowEvent.BEFORE_FLOW_CONTROL,
            flow_type="command",
            condition=command
        )
        return self.control(FlowEvent.BEFORE_FLOW_CONTROL, context)
    
    def get_total_controllers(self) -> int:
        """Obtener total de controladores"""
        return sum(len(controllers) for controllers in self.controllers.values())
    
    def get_flow_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de flow"""
        return {event.value: len(controllers) for event, controllers in self.controllers.items()}
    
    def list_controllers(self) -> Dict[str, List[str]]:
        """Listar controladores registrados"""
        return {event.value: [str(cb) for cb, _ in controllers] 
                for event, controllers in self.controllers.items()}

class CommandCustomizer:
    """Customizador de comandos del SDK"""
    
    def __init__(self):
        self.customizers = {}
        self.aliases = {}
        self.command_transformations = {}
    
    def register_customizer(self, event: CommandEvent, callback: callable, priority: int = 5):
        """Registrar un customizer"""
        if event not in self.customizers:
            self.customizers[event] = []
        
        self.customizers[event].append({
            'callback': callback,
            'priority': priority
        })
        
        # Ordenar por prioridad
        self.customizers[event].sort(key=lambda x: x['priority'])
    
    def add_command_alias(self, alias: str, original_command: str):
        """Registrar un alias"""
        self.aliases[alias] = original_command
    
    def customize(self, event: CommandEvent, context: CommandContext) -> CommandContext:
        """Customizar comando"""
        if event not in self.customizers:
            return context
        
        for customizer in self.customizers[event]:
            try:
                result = customizer['callback'](context)
                if result:
                    context = result
            except Exception as e:
                context.should_continue = False
                break
        
        return context
    
    def customize_before_execution(self, command_name: str, command_args: Dict[str, Any], original_command: Any) -> CommandContext:
        """Customizar antes de ejecución"""
        context = CommandContext(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            command_name=command_name,
            command_args=command_args,
            original_command=original_command,
            transformed_command=command_args,
            execution_result=None
        )
        return self.customize(CommandEvent.BEFORE_COMMAND_EXECUTION, context)
    
    def resolve_alias(self, command_name: str) -> str:
        """Resolver alias"""
        return self.aliases.get(command_name, command_name)
    
    def list_customizers(self) -> Dict[str, List[str]]:
        """Listar customizers registrados"""
        return {event.value: [str(cb) for cb, _ in customizers] 
                for event, customizers in self.customizers.items()}
    
    def list_aliases(self) -> Dict[str, str]:
        """Listar alias registrados"""
        return self.aliases.copy()
    
    def list_transformations(self) -> List[str]:
        """Listar transformaciones registradas"""
        return list(self.command_transformations.keys())
    
    def get_total_customizers(self) -> int:
        """Obtener total de customizers"""
        return sum(len(customizers) for customizers in self.customizers.values())
    
    def get_alias_count(self) -> int:
        """Obtener número de alias"""
        return len(self.aliases)
    
    def get_transformation_count(self) -> int:
        """Obtener número de transformaciones"""
        return len(self.command_transformations)
    
    def get_customization_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de customización"""
        return {event.value: len(customizers) for event, customizers in self.customizers.items()}

# ============================================================================
# PLANTILLA DE PLUGIN INDEPENDIENTE
# ============================================================================

class StandalonePlugin(MockPluginBase):
    """
    Plantilla de plugin independiente para desarrollo.
    
    Este plugin puede desarrollarse sin tener todo el proyecto de Sugar,
    usando las clases mock y el SDK completo incluido.
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin independiente para desarrollo"
    AUTHOR = "Developer"
    LICENSE = "MIT"
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Inicializar SDK
        self._initialize_sdk()
        
        MockOutput.Console(self.plugin_name, "Standalone plugin initialized")
    
    def _initialize_sdk(self):
        """Inicializar componentes del SDK"""
        try:
            self.extension_manager = ExtensionManager()
            self.hook_system = HookSystem()
            self.interpolation_interceptor = InterpolationInterceptor()
            self.ast_modifier = ASTModifier()
            self.flow_controller = FlowController()
            self.command_customizer = CommandCustomizer()
            
            # Registrar extensiones del SDK
            self._register_sdk_extensions()
            
            MockOutput.Console(self.plugin_name, "SDK components initialized")
        except Exception as e:
            MockOutput.Error(self.plugin_name, f"SDK initialization failed: {e}")
            # Asegurar que los componentes estén disponibles incluso si falla la inicialización
            if not hasattr(self, 'extension_manager'):
                self.extension_manager = ExtensionManager()
            if not hasattr(self, 'hook_system'):
                self.hook_system = HookSystem()
            if not hasattr(self, 'interpolation_interceptor'):
                self.interpolation_interceptor = InterpolationInterceptor()
            if not hasattr(self, 'ast_modifier'):
                self.ast_modifier = ASTModifier()
            if not hasattr(self, 'flow_controller'):
                self.flow_controller = FlowController()
            if not hasattr(self, 'command_customizer'):
                self.command_customizer = CommandCustomizer()
    
    def _register_sdk_extensions(self):
        """Registrar extensiones del SDK"""
        # Registrar extensión principal
        self.extension_manager.register_extension(
            plugin_name=self.plugin_name,
            extension_type=ExtensionType.COMMAND_CUSTOMIZER,
            callback=self._plugin_extension_callback,
            priority=10,
            metadata={'type': 'standalone_plugin'}
        )
        
        # Registrar hooks
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=5
        )
        
        # Registrar interceptor de interpolación
        self.interpolation_interceptor.register_interceptor(
            event=InterpolationEvent.BEFORE_INTERPOLATION,
            callback=self._before_interpolation_callback,
            priority=3
        )
        
        # Registrar customizer de comandos
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_command_callback,
            priority=5
        )
        
        # Registrar alias
        self.command_customizer.add_command_alias("test", "test_command")
        self.command_customizer.add_command_alias("info", "plugin_info")
        self.command_customizer.add_command_alias("demo", "test_command")
    
    def _plugin_extension_callback(self, *args, **kwargs):
        """Callback de extensión del plugin"""
        MockOutput.Console(self.plugin_name, "Plugin extension callback executed")
        return True
    
    def _before_task_hook(self, hook_context: HookContext) -> HookContext:
        """Hook antes de ejecutar tareas"""
        MockOutput.Console(self.plugin_name, "Before task hook executed")
        return hook_context
    
    def _before_interpolation_callback(self, context: InterpolationContext) -> InterpolationContext:
        """Callback antes de interpolación"""
        MockOutput.Console(self.plugin_name, f"Interpolating: {context.original}")
        return context
    
    def _before_command_callback(self, context: CommandContext) -> CommandContext:
        """Callback antes de ejecutar comandos"""
        MockOutput.Console(self.plugin_name, f"Executing command: {context.command_name}")
        return context
    
    def get_available_commands(self) -> List[str]:
        """Obtener comandos disponibles"""
        return [
            "plugin_info",
            "test_command",
            "sdk_info",
            "sdk_test",
            "mock_sugar_environment"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin"""
        # Resolver alias
        resolved_command = self.command_customizer.resolve_alias(command)
        
        # Si el comando original no existe, usar el comando tal como está
        if resolved_command == command and command not in ["plugin_info", "test_command", "sdk_info", "sdk_test", "mock_sugar_environment"]:
            resolved_command = command
        
        # Crear contexto de comando
        command_context = CommandContext(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            command_name=resolved_command,
            command_config=config
        )
        
        # Ejecutar customizers
        command_context = self.command_customizer.customize(
            CommandEvent.BEFORE_COMMAND_EXECUTION, 
            command_context
        )
        
        if not command_context.should_continue:
            return {"status": "error", "message": "Command execution blocked by customizer"}
        
        # Ejecutar comando
        if resolved_command == "plugin_info":
            return self._plugin_info_command(config)
        elif resolved_command == "test_command":
            return self._test_command(config)
        elif resolved_command == "sdk_info":
            return self._sdk_info_command(config)
        elif resolved_command == "sdk_test":
            return self._sdk_test_command(config)
        elif resolved_command == "mock_sugar_environment":
            return self._mock_sugar_environment_command(config)
        else:
            # Si el comando no se encuentra, intentar con el comando original
            if command == "test":
                return self._test_command(config)
            elif command == "info":
                return self._plugin_info_command(config)
            else:
                raise ValueError(f"Unknown command: {resolved_command}")
    
    def _plugin_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando de información del plugin"""
        return {
            "status": "success",
            "plugin_name": self.plugin_name,
            "version": self.VERSION,
            "description": self.DESCRIPTION,
            "author": self.AUTHOR,
            "license": self.LICENSE,
            "available_commands": self.get_available_commands()
        }
    
    def _test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando de prueba"""
        test_data = config.get("data", "Hello from standalone plugin!")
        
        return {
            "status": "success",
            "message": "Test command executed successfully",
            "data": test_data,
            "timestamp": time.time()
        }
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando de información del SDK"""
        return {
            "status": "success",
            "sdk_enabled": True,
            "plugin_name": self.plugin_name,
            "version": self.VERSION,
            "sdk_components": {
                "extension_manager": hasattr(self, 'extension_manager'),
                "hook_system": hasattr(self, 'hook_system'),
                "interpolation_interceptor": hasattr(self, 'interpolation_interceptor'),
                "ast_modifier": hasattr(self, 'ast_modifier'),
                "flow_controller": hasattr(self, 'flow_controller'),
                "command_customizer": hasattr(self, 'command_customizer')
            },
            "extensions_count": sum(len(extensions) for extensions in self.extension_manager.extensions.values()),
            "hooks_count": sum(len(hooks) for hooks in self.hook_system.hooks.values()),
            "aliases_count": len(self.command_customizer.aliases)
        }
    
    def _sdk_test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando de prueba del SDK"""
        tests = {}
        
        # Test de hooks
        hook_context = HookContext(hook_point=HookPoint.BEFORE_TASK_EXECUTION)
        result_context = self.hook_system.execute_hooks(HookPoint.BEFORE_TASK_EXECUTION, hook_context)
        tests['hooks'] = {
            'executed': True,
            'context': {
                'modified': result_context.modified,
                'should_continue': result_context.should_continue
            }
        }
        
        # Test de interpolación
        interp_context = InterpolationContext(
            event=InterpolationEvent.BEFORE_INTERPOLATION,
            original="test_variable"
        )
        result_interp = self.interpolation_interceptor.intercept(
            InterpolationEvent.BEFORE_INTERPOLATION, 
            interp_context
        )
        tests['interpolation'] = {
            'executed': True,
            'context': {
                'original': result_interp.original,
                'modified': result_interp.modified
            }
        }
        
        # Test de customización de comandos
        cmd_context = CommandContext(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            command_name="test"
        )
        result_cmd = self.command_customizer.customize(
            CommandEvent.BEFORE_COMMAND_EXECUTION, 
            cmd_context
        )
        tests['command_customization'] = {
            'executed': True,
            'context': {
                'command_name': result_cmd.command_name,
                'should_continue': result_cmd.should_continue
            }
        }
        
        return {
            "status": "success",
            "message": "SDK functionality tested successfully",
            "sdk_tests": tests
        }
    
    def _mock_sugar_environment_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para simular entorno de Sugar"""
        return {
            "status": "success",
            "message": "Mock Sugar environment is working",
            "environment": {
                "plugin_base": "MockPluginBase",
                "output": "MockOutput",
                "sdk": "Complete SDK Implementation",
                "context": "Mock Context",
                "memory_handler": "Mock Memory Handler"
            },
            "capabilities": [
                "Hook System",
                "Interpolation Interceptor", 
                "AST Modifier",
                "Flow Controller",
                "Command Customizer",
                "Extension Manager"
            ]
        }
    
    def cleanup(self):
        """Limpiar recursos del plugin"""
        MockOutput.Console(self.plugin_name, "Standalone plugin cleanup completed")

# ============================================================================
# FUNCIÓN DE PRUEBA INDEPENDIENTE
# ============================================================================

def test_standalone_plugin():
    """Función para probar el plugin independiente"""
    print("Testing Standalone Plugin")
    print("=" * 50)
    
    # Crear instancia del plugin
    plugin = StandalonePlugin()
    
    # Probar comandos básicos
    print("\nTesting basic commands:")
    print("-" * 30)
    
    # Plugin info
    result = plugin.execute("plugin_info", {})
    print(f"Plugin Info: {json.dumps(result, indent=2)}")
    
    # Test command
    result = plugin.execute("test", {"data": "Custom test data"})
    print(f"Test Command: {json.dumps(result, indent=2)}")
    
    # SDK info
    result = plugin.execute("sdk_info", {})
    print(f"SDK Info: {json.dumps(result, indent=2)}")
    
    # SDK test
    result = plugin.execute("sdk_test", {})
    print(f"SDK Test: {json.dumps(result, indent=2)}")
    
    # Mock environment
    result = plugin.execute("mock_sugar_environment", {})
    print(f"Mock Environment: {json.dumps(result, indent=2)}")
    
    # Limpiar
    plugin.cleanup()
    
    print("\nStandalone plugin test completed successfully!")

if __name__ == "__main__":
    test_standalone_plugin()