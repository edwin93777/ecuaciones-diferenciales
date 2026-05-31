from flask import Blueprint, request

from backend.modelos.mezclas import resolver_mezclas
from backend.utils.respuesta import responder_modelo

mezclas_bp = Blueprint("mezclas", __name__, url_prefix="/resolver")


@mezclas_bp.post("/mezclas")
def resolver():
    return responder_modelo(resolver_mezclas(request.get_json(silent=True) or {}))
