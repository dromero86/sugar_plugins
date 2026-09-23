"""
Capa keeper: protocolo de mensajes
==================================

Mensajes request/response que viajan entre el cliente (adaptador) y el
keeper que posee la sesion. Es un contrato plano, serializable, para no
acoplar el transporte (thread local hoy, socket/proceso a futuro).
"""

OP_EXECUTE = 'execute'
OP_DETACH = 'detach'
OP_QUIT = 'quit'
OP_PING = 'ping'

OPS = {OP_EXECUTE, OP_DETACH, OP_QUIT, OP_PING}


def make_request(request_id: int, op: str, **payload) -> dict:
    return {'id': request_id, 'op': op, **payload}


def make_response(request_id: int, ok: bool, result=None, error=None) -> dict:
    return {'id': request_id, 'ok': ok, 'result': result, 'error': error}
