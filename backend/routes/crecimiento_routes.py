from flask import Blueprint, request

from backend.modelos.crecimiento import resolver_crecimiento
from backend.utils.respuesta import responder_modelo

crecimiento_bp = Blueprint("crecimiento", __name__, url_prefix="/resolver")


@crecimiento_bp.post("/crecimiento")
def resolver():
    return responder_modelo(resolver_crecimiento(request.get_json(silent=True) or {}))
