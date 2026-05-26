"""Adaptador HTTP para respuestas de modelos."""
from __future__ import annotations

from flask import jsonify


def responder_modelo(resultado: dict):
    estado = 400 if resultado.get("error") else 200
    return jsonify(resultado), estado
