"""Normalizacion de config y contrato de resultado de los componentes."""


def normalize_config(config, required=()):
    """Valida que la config sea un objeto y tenga las claves requeridas."""
    if not isinstance(config, dict):
        raise ValueError("La config del componente debe ser un objeto")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError("Faltan claves de config: " + ", ".join(missing))
    return config


def ok(**fields):
    """Resultado exitoso del contrato comun."""
    return {"status": "ok", **fields}


def error(message, **fields):
    """Resultado de error del contrato comun."""
    return {"status": "error", "error": message, **fields}
