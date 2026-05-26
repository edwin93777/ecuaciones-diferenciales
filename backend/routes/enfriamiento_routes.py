from flask import Blueprint, request

from backend.modelos.enfriamiento import resolver_enfriamiento
from backend.utils.respuesta import responder_modelo

enfriamiento_bp = Blueprint("enfriamiento", __name__, url_prefix="/resolver")


@enfriamiento_bp.post("/enfriamiento")
def resolver():
    return responder_modelo(resolver_enfriamiento(request.get_json(silent=True) or {}))
