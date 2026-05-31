"""Validaciones de entrada para los modelos de ecuaciones diferenciales."""
from __future__ import annotations

from typing import Any, Iterable


class ErrorValidacion(ValueError):
    """Error controlado para entradas inválidas del usuario."""


def crear_respuesta_error(mensaje: str, codigo: str = "entrada_invalida") -> dict[str, Any]:
    return {"error": True, "codigo": codigo, "mensaje": mensaje}


def validar_campo_requerido(datos: dict[str, Any], campo: str) -> None:
    if campo not in datos or datos[campo] in (None, ""):
        raise ErrorValidacion(f"El campo '{campo}' es obligatorio.")


def obtener_valor(datos: dict[str, Any], posibles_campos: Iterable[str], nombre: str) -> Any:
    for campo in posibles_campos:
        if campo in datos and datos[campo] not in (None, ""):
            return datos[campo]
    raise ErrorValidacion(f"Falta el valor requerido: {nombre}.")


def validar_numero(valor: Any, nombre: str) -> float:
    try:
        numero = float(str(valor).replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise ErrorValidacion(f"{nombre} debe ser un número válido.") from exc
    return numero


def validar_positivo(valor: Any, nombre: str) -> float:
    numero = validar_numero(valor, nombre)
    if numero <= 0:
        raise ErrorValidacion(f"{nombre} debe ser mayor que cero.")
    return numero


def validar_no_negativo(valor: Any, nombre: str) -> float:
    numero = validar_numero(valor, nombre)
    if numero < 0:
        raise ErrorValidacion(f"{nombre} no puede ser negativo.")
    return numero


def normalizar_texto(valor: Any) -> str:
    return str(valor or "").strip().lower().replace(" ", "_").replace("-", "_")
