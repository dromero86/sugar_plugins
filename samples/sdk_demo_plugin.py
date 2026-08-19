"""
SDK Demo Plugin
==============

Plugin de demostración que muestra cómo usar el SDK para extender
el comportamiento del intérprete, flow, interpolaciones y otros componentes.
"""

import json
import time
from typing import Any, Dict, List, Optional
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    InterpolationInterceptor, InterpolationEvent,
    ASTModifier, ASTModificationEvent,
    FlowController, FlowEvent,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

class SDKDemoPlugin(PluginBase):
    """
    Plugin de demostración del SDK que muestra cómo extender
    el comportamiento del intérprete de Sugar.
    
    Este plugin registra múltiples extensiones que demuestran:
    - Hooks del intérprete
    - Interceptores de interpolación
    - Modificadores de AST
    - Controladores de flow
    - Customizadores de comandos
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin de demostración del SDK para extender el intérprete"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Obtener instancias del SDK
        self.extension_manager = ExtensionManager()
        self.hook_system = HookSystem()
        self.interpolation_interceptor = InterpolationInterceptor()
        self.ast_modifier = ASTModifier()
        self.flow_controller = FlowController()
        self.command_customizer = CommandCustomizer()
        
        # Registrar todas las extensiones
        self._register_extensions()
        
        Output.Console(self.plugin_name, "SDK Demo Plugin initialized with all extensions")
    
    def _register_extensions(self):
        """Registrar todas las extensiones del plugin"""
        
        # 1. Registrar extensiones en el ExtensionManager
        self.extension_manager.register_extension(
            plugin_name=self.plugin_name,
            extension_type=ExtensionType.INTERPRETER_HOOK,
            callback=self._interpreter_hook_callback,
            priority=10,
            metadata={'type': 'demo_hook'}
        )
        
        # 2. Registrar hooks en el HookSystem
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=5
        )
        
        self.hook_system.register_hook(
            hook_point=HookPoint.AFTER_TASK_EXECUTION,
            callback=self._after_task_hook,
            priority=5
        )
        
        # 3. Registrar interceptores de interpolación
        self.interpolation_interceptor.register_interceptor(
            event=InterpolationEvent.BEFORE_INTERPOLATION,
            callback=self._before_interpolation_callback,
            priority=3
        )
        
        self.interpolation_interceptor.register_interceptor(
            event=InterpolationEvent.VARIABLE_NOT_FOUND,
            callback=self._variable_not_found_callback,
            priority=5
        )
        
        # 4. Registrar modificadores de AST
        self.ast_modifier.register_modifier(
            event=ASTModificationEvent.BEFORE_PARSING,
            callback=self._before_ast_parsing_callback,
            priority=2
        )
        
        # 5. Registrar controladores de flow
        self.flow_controller.register_controller(
            event=FlowEvent.BEFORE_COMMAND,
            callback=self._before_command_flow_callback,
            priority=4
        )
        
        # 6. Registrar customizadores de comandos
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_command_execution_callback,
            priority=6
        )
        
        # 7. Agregar alias de comandos
        self.command_customizer.add_command_alias("demo", "hello")
        self.command_customizer.add_command_alias("test", "system_info")
        
        Output.Console(self.plugin_name, "All SDK extensions registered successfully")
    
    def _interpreter_hook_callback(self, *args, **kwargs):
        """Callback para hooks del intérprete"""
        Output.Console(self.plugin_name, f"Interpreter hook executed with args: {args}")
        return {'interpreter_hook_executed': True, 'timestamp': time.time()}
    
    def _before_task_hook(self, hook_context):
        """Hook ejecutado antes de cada tarea"""
        task = hook_context.data.get('task', {})
        Output.Console(self.plugin_name, f"Before task hook: {task.get('name', 'unknown')}")
        
        # Agregar información adicional al contexto
        hook_context.data['demo_plugin_info'] = {
            'plugin': self.plugin_name,
            'timestamp': time.time(),
            'task_count': len(hook_context.data.get('execution_stack', []))
        }
        
        return hook_context
    
    def _after_task_hook(self, hook_context):
        """Hook ejecutado después de cada tarea"""
        task = hook_context.data.get('task', {})
        result = hook_context.data.get('result', {})
        Output.Console(self.plugin_name, f"After task hook: {task.get('name', 'unknown')} -> {result}")
        
        # Modificar el resultado si es necesario
        if isinstance(result, dict):
            result['demo_plugin_processed'] = True
            result['processing_time'] = time.time()
        
        return hook_context
    
    def _before_interpolation_callback(self, context):
        """Callback ejecutado antes de la interpolación"""
        Output.Console(self.plugin_name, f"Before interpolation: {context.original_value}")
        
        # Ejemplo: agregar un prefijo a ciertas variables
        if context.original_value.startswith('${demo_'):
            context.interpolated_value = f"DEMO_{context.original_value}"
            context.modified = True
            Output.Console(self.plugin_name, f"Modified interpolation: {context.interpolated_value}")
        
        return context
    
    def _variable_not_found_callback(self, context):
        """Callback ejecutado cuando no se encuentra una variable"""
        variable_name = context.metadata.get('variable_name', 'unknown')
        Output.Console(self.plugin_name, f"Variable not found: {variable_name}")
        
        # Ejemplo: proporcionar un valor por defecto para ciertas variables
        if variable_name.startswith('demo_'):
            context.interpolated_value = f"default_value_for_{variable_name}"
            context.modified = True
            Output.Console(self.plugin_name, f"Provided default value: {context.interpolated_value}")
        
        return context
    
    def _before_ast_parsing_callback(self, context):
        """Callback ejecutado antes del parsing del AST"""
        Output.Console(self.plugin_name, f"Before AST parsing: {type(context.node)}")
        
        # Ejemplo: agregar metadatos al contexto
        if context.metadata is None:
            context.metadata = {}
        context.metadata['demo_plugin_parsing'] = True
        context.metadata['parsing_timestamp'] = time.time()
        
        return context
    
    def _before_command_flow_callback(self, context):
        """Callback de control de flujo antes de comandos"""
        command = context.current_command
        Output.Console(self.plugin_name, f"Before command flow: {command}")
        
        # Ejemplo: agregar información de contexto
        if context.metadata is None:
            context.metadata = {}
        context.metadata['demo_plugin_flow'] = True
        context.metadata['command_timestamp'] = time.time()
        
        return context
    
    def _before_command_execution_callback(self, context):
        """Callback ejecutado antes de la ejecución de comandos"""
        command_name = context.command_name
        command_args = context.command_args
        Output.Console(self.plugin_name, f"Before command execution: {command_name} with args: {command_args}")
        
        # Ejemplo: modificar argumentos de comandos específicos
        if command_name == "hello":
            if 'name' not in command_args:
                command_args['name'] = 'SDK Demo Plugin'
                context.transformed_command = command_args
                Output.Console(self.plugin_name, f"Modified command args: {command_args}")
        
        return context
    
    def get_available_commands(self) -> List[str]:
        """Obtener comandos disponibles del plugin"""
        return [
            "sdk_info",              # Información del SDK
            "list_extensions",       # Listar extensiones registradas
            "test_hooks",           # Probar hooks
            "test_interpolation",   # Probar interpolación
            "test_flow_control",    # Probar control de flujo
            "test_command_custom",  # Probar customización de comandos
            "clear_extensions",     # Limpiar extensiones
            "stats"                 # Estadísticas del SDK
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin"""
        if command == "sdk_info":
            return self._sdk_info_command(config)
        elif command == "list_extensions":
            return self._list_extensions_command(config)
        elif command == "test_hooks":
            return self._test_hooks_command(config)
        elif command == "test_interpolation":
            return self._test_interpolation_command(config)
        elif command == "test_flow_control":
            return self._test_flow_control_command(config)
        elif command == "test_command_custom":
            return self._test_command_custom_command(config)
        elif command == "clear_extensions":
            return self._clear_extensions_command(config)
        elif command == "stats":
            return self._stats_command(config)
        else:
            raise ValueError(f"Comando desconocido: {command}")
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para obtener información del SDK"""
        return {
            'status': 'success',
            'plugin_name': self.plugin_name,
            'version': self.VERSION,
            'sdk_components': {
                'extension_manager': 'ExtensionManager',
                'hook_system': 'HookSystem',
                'interpolation_interceptor': 'InterpolationInterceptor',
                'ast_modifier': 'ASTModifier',
                'flow_controller': 'FlowController',
                'command_customizer': 'CommandCustomizer'
            },
            'message': 'SDK Demo Plugin information retrieved'
        }
    
    def _list_extensions_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para listar extensiones registradas"""
        return {
            'status': 'success',
            'extensions': self.extension_manager.get_extensions_info(),
            'hooks': self.hook_system.list_hooks(),
            'interceptors': self.interpolation_interceptor.list_interceptors(),
            'modifiers': self.ast_modifier.list_modifiers(),
            'controllers': self.flow_controller.list_controllers(),
            'customizers': self.command_customizer.list_customizers(),
            'aliases': self.command_customizer.list_aliases(),
            'transformations': self.command_customizer.list_transformations()
        }
    
    def _test_hooks_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar hooks"""
        # Simular ejecución de hooks
        hook_context = self.hook_system.execute_hooks(
            HookPoint.BEFORE_TASK_EXECUTION,
            task={'name': 'test_task', 'type': 'demo'},
            execution_stack=['main', 'test']
        )
        
        return {
            'status': 'success',
            'hook_executed': True,
            'hook_context': {
                'modified': hook_context.modified,
                'should_continue': hook_context.should_continue,
                'data': hook_context.data
            },
            'hook_stats': self.hook_system.get_hook_stats()
        }
    
    def _test_interpolation_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar interceptores de interpolación"""
        # Probar interpolación normal
        context1 = self.interpolation_interceptor.intercept_before_interpolation(
            "Hello ${name}",
            ["name"]
        )
        
        # Probar variable no encontrada
        context2 = self.interpolation_interceptor.intercept_variable_not_found(
            "demo_missing_var",
            "Hello ${demo_missing_var}"
        )
        
        return {
            'status': 'success',
            'interpolation_tests': {
                'normal_interpolation': {
                    'original': context1.original_value,
                    'modified': context1.modified,
                    'result': context1.interpolated_value
                },
                'variable_not_found': {
                    'variable': context2.metadata.get('variable_name'),
                    'modified': context2.modified,
                    'result': context2.interpolated_value
                }
            },
            'interception_stats': self.interpolation_interceptor.get_interception_stats()
        }
    
    def _test_flow_control_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar control de flujo"""
        # Simular control de flujo
        flow_context = self.flow_controller.control_before_command(
            {'name': 'test_command', 'args': ['arg1', 'arg2']},
            ['main', 'test_flow']
        )
        
        return {
            'status': 'success',
            'flow_control_executed': True,
            'flow_context': {
                'should_continue': flow_context.should_continue,
                'should_skip': flow_context.should_skip,
                'should_abort': flow_context.should_abort,
                'metadata': flow_context.metadata
            },
            'flow_stats': self.flow_controller.get_flow_stats()
        }
    
    def _test_command_custom_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar customización de comandos"""
        # Probar customización de comando
        command_context = self.command_customizer.customize_before_execution(
            "hello",
            {"name": "World"},
            "original_command"
        )
        
        return {
            'status': 'success',
            'command_customization_executed': True,
            'command_context': {
                'command_name': command_context.command_name,
                'command_args': command_context.command_args,
                'should_continue': command_context.should_continue,
                'metadata': command_context.metadata
            },
            'customization_stats': self.command_customizer.get_customization_stats(),
            'aliases': self.command_customizer.list_aliases()
        }
    
    def _clear_extensions_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para limpiar extensiones"""
        # Limpiar extensiones del plugin
        removed_extensions = self.extension_manager.unregister_all_plugin_extensions(self.plugin_name)
        
        return {
            'status': 'success',
            'extensions_cleared': True,
            'removed_extensions': removed_extensions,
            'message': f'Cleared {removed_extensions} extensions for plugin {self.plugin_name}'
        }
    
    def _stats_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para obtener estadísticas del SDK"""
        return {
            'status': 'success',
            'sdk_statistics': {
                'extension_manager': {
                    'total_extensions': sum(
                        self.extension_manager.get_extension_count(ext_type)
                        for ext_type in ExtensionType
                    ),
                    'plugin_extensions': self.extension_manager.get_plugin_extension_count(self.plugin_name)
                },
                'hook_system': {
                    'total_hooks': self.hook_system.get_total_hooks(),
                    'hook_stats': self.hook_system.get_hook_stats()
                },
                'interpolation_interceptor': {
                    'total_interceptors': self.interpolation_interceptor.get_total_interceptors(),
                    'interception_stats': self.interpolation_interceptor.get_interception_stats()
                },
                'ast_modifier': {
                    'total_modifiers': self.ast_modifier.get_total_modifiers(),
                    'modification_stats': self.ast_modifier.get_modification_stats()
                },
                'flow_controller': {
                    'total_controllers': self.flow_controller.get_total_controllers(),
                    'flow_stats': self.flow_controller.get_flow_stats()
                },
                'command_customizer': {
                    'total_customizers': self.command_customizer.get_total_customizers(),
                    'alias_count': self.command_customizer.get_alias_count(),
                    'transformation_count': self.command_customizer.get_transformation_count(),
                    'customization_stats': self.command_customizer.get_customization_stats()
                }
            }
        }
    
    def cleanup(self):
        """Limpiar extensiones al desactivar el plugin"""
        Output.Console(self.plugin_name, "Cleaning up SDK Demo Plugin extensions...")
        
        # Limpiar todas las extensiones del plugin
        self.extension_manager.unregister_all_plugin_extensions(self.plugin_name)
        
        Output.Console(self.plugin_name, "SDK Demo Plugin cleanup completed")