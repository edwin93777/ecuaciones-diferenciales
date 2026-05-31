from flask import Blueprint, request

from backend.modelos.decaimiento import resolver_decaimiento
from backend.utils.respuesta import responder_modelo

decaimiento_bp = Blueprint("decaimiento", __name__, url_prefix="/resolver")


@decaimiento_bp.post("/decaimiento")
def resolver():
    return responder_modelo(resolver_decaimiento(request.get_json(silent=True) or {}))
