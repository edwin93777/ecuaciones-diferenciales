from flask import Blueprint, request

from backend.modelos.carbono14 import resolver_carbono14
from backend.utils.respuesta import responder_modelo

carbono14_bp = Blueprint("carbono14", __name__, url_prefix="/resolver")


@carbono14_bp.post("/carbono14")
def resolver():
    return responder_modelo(resolver_carbono14(request.get_json(silent=True) or {}))
