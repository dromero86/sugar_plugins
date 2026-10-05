"""Estado de sesion del plugin (holder del screen y del registry)."""


class Session:
    """Holder compartido por los componentes: screen, registry y bridge."""

    def __init__(self):
        self.initialized = False
        self.original_screen = None
        self.registry = None
        self.call_function = None
        self.register_function = None
        self.invoke_anonymous = None
