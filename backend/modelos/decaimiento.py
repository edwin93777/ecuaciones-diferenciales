"""Módulo de decaimiento exponencial.

Agrupa radiactividad, absorción de medicamento, descarga de capacitor e
intensidad de luz, porque todas son variantes de y' = -ky.
"""
from __future__ import annotations

from math import exp, log
from typing import Any

from backend.modelos.formulas_simbolicas import formula_decaimiento
from backend.utils.formato import (
    DECIMALES_CONSTANTE,
    crear_paso,
    crear_respuesta_modelo,
    formatear_numero,
    redondear,
)
from backend.utils.simbolico import (
    crear_variable,
    evaluar,
    expresion_decaimiento_exponencial,
    paso_sympy,
)
from backend.utils.validacion import (
    ErrorValidacion,
    crear_respuesta_error,
    normalizar_texto,
    obtener_valor,
    validar_no_negativo,
    validar_positivo,
)

MODULO = "decaimiento"

CONFIG_VARIANTES = {
    "decaimiento_radiactivo": {
        "modelo": "Decaimiento radiactivo: A'=-kA",
        "simbolo": "A",
        "unidad": "g",
        "descripcion": "La sustancia se desintegra a una tasa proporcional a la cantidad presente.",
    },
    "absorcion_medicamento": {
        "modelo": "Absorción / eliminación de medicamento: C'=-kC",
        "simbolo": "C",
        "unidad": "mg",
        "descripcion": "La concentración del medicamento disminuye proporcionalmente a su concentración actual.",
    },
    "descarga_capacitor": {
        "modelo": "Descarga de capacitor: q'=-(1/RC)q",
        "simbolo": "q",
        "unidad": "coulombs",
        "descripcion": "La carga del capacitor disminuye proporcionalmente a la carga presente.",
    },
    "intensidad_luz": {
        "modelo": "Intensidad de luz: I'=-kI",
        "simbolo": "I",
        "unidad": "% de intensidad inicial",
        "descripcion": "La intensidad disminuye proporcionalmente a la intensidad presente al avanzar la distancia.",
    },
}

ALIAS_VARIANTES = {
    "radiactivo": "decaimiento_radiactivo",
    "radioactivo": "decaimiento_radiactivo",
    "decaimiento": "decaimiento_radiactivo",
    "medicamento": "absorcion_medicamento",
    "absorcion": "absorcion_medicamento",
    "capacitor": "descarga_capacitor",
    "descarga": "descarga_capacitor",
    "luz": "intensidad_luz",
    "intensidad": "intensidad_luz",
}


def _normalizar_variante(variante: str) -> str:
    variante = normalizar_texto(variante)
    return ALIAS_VARIANTES.get(variante, variante or "decaimiento_radiactivo")


def _hay_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _obtener_constante_decaimiento(
    datos: dict[str, Any],
    cantidad_inicial: float,
    variante: str,
) -> tuple[float | None, list[dict[str, str]]]:
    """Obtiene k directamente, por RC, por medición o la deja indeterminada."""
    pasos: list[dict[str, str]] = []

    if variante == "descarga_capacitor" and _hay_valor(datos, "resistencia") and _hay_valor(datos, "capacitancia"):
        resistencia = validar_positivo(datos["resistencia"], "Resistencia")
        capacitancia = validar_positivo(datos["capacitancia"], "Capacitancia")
        constante_k = 1 / (resistencia * capacitancia)
        pasos.append(crear_paso(
            "Constante del circuito RC",
            "Para la descarga de capacitor, la constante de decaimiento es 1/(RC).",
            rf"\boxed{{k=\frac{{1}}{{RC}}=\frac{{1}}{{{formatear_numero(resistencia)}\cdot {formatear_numero(capacitancia)}}}={formatear_numero(constante_k, DECIMALES_CONSTANTE)}}}",
        ))
        return constante_k, pasos

    if _hay_valor(datos, "constante_k", "k"):
        constante_k = validar_positivo(obtener_valor(datos, ("constante_k", "k"), "constante k"), "Constante k")
        pasos.append(crear_paso(
            "Constante entregada",
            "La constante de decaimiento fue ingresada directamente.",
            rf"\boxed{{k={formatear_numero(constante_k, DECIMALES_CONSTANTE)}}}",
        ))
        return constante_k, pasos

    if not (_hay_valor(datos, "tiempo_transcurrido", "distancia_transcurrida", "tiempo_conocido") and _hay_valor(datos, "cantidad_transcurrida", "cantidad_restante", "cantidad_conocida")):
        pasos.append(crear_paso(
            "Constante k no entregada",
            "No se conoce k ni existe una medición suficiente para inferirla; por eso se conserva simbólica.",
            r"\boxed{k\;\text{indeterminada}}",
        ))
        return None, pasos

    tiempo_conocido = validar_positivo(obtener_valor(datos, ("tiempo_transcurrido", "distancia_transcurrida", "tiempo_conocido"), "tiempo o distancia conocida"), "Tiempo o distancia conocida")
    cantidad_conocida = validar_positivo(obtener_valor(datos, ("cantidad_transcurrida", "cantidad_restante", "cantidad_conocida"), "cantidad restante"), "Cantidad restante")
    if cantidad_conocida >= cantidad_inicial:
        raise ErrorValidacion("En decaimiento, la cantidad conocida debe ser menor que la cantidad inicial.")

    constante_k = log(cantidad_inicial / cantidad_conocida) / tiempo_conocido
    y0 = formatear_numero(cantidad_inicial)
    y1 = formatear_numero(cantidad_conocida)
    t1 = formatear_numero(tiempo_conocido)
    k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
    pasos.append(crear_paso(
        "Inferencia de k",
        "Como no se ingresó k, se calcula con una medición posterior.",
        rf"\begin{{gathered}}"
        rf"Y({t1})={y1},\quad Y(0)={y0}\\[6px]"
        rf"{y1}={y0}e^{{-k({t1})}}\\[6px]"
        rf"k=\frac{{\ln\left(\frac{{{y0}}}{{{y1}}}\right)}}{{{t1}}}\\[6px]"
        rf"\boxed{{k={k}}}"
        rf"\end{{gathered}}",
    ))
    return constante_k, pasos


def resolver_decaimiento(datos: dict[str, Any]) -> dict[str, Any]:
    """Método único del módulo decaimiento que evalúa sus variantes internas."""
    try:
        variante = _normalizar_variante(datos.get("variante", "decaimiento_radiactivo"))
        if variante not in CONFIG_VARIANTES:
            raise ErrorValidacion(f"Variante no soportada en decaimiento: {variante}.")

        config = CONFIG_VARIANTES[variante]
        simbolo = config["simbolo"]
        tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "valor_en_tiempo"))
        if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
            return formula_decaimiento({**datos, "variante": variante})
        if not _hay_valor(datos, "cantidad_inicial", "carga_inicial", "intensidad_inicial"):
            return formula_decaimiento({**datos, "variante": variante})
        cantidad_inicial = validar_positivo(obtener_valor(datos, ("cantidad_inicial", "carga_inicial", "intensidad_inicial"), "cantidad inicial"), "Cantidad inicial")
        constante_k, pasos_constante = _obtener_constante_decaimiento(datos, cantidad_inicial, variante)
        if constante_k is None:
            return formula_decaimiento({**datos, "variante": variante})

        variable_t = crear_variable("x" if variante == "intensidad_luz" else "t")
        expresion_sympy = expresion_decaimiento_exponencial(cantidad_inicial, constante_k, variable_t)
        y0 = formatear_numero(cantidad_inicial)
        k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
        vida_media = log(2) / constante_k

        pasos = [
            crear_paso(
                "Modelo diferencial",
                config["descripcion"],
                rf"\frac{{d{simbolo}}}{{dt}}=-k{simbolo}",
            ),
            crear_paso(
                "Solución general",
                "Se separan variables, se integra y se obtiene una exponencial decreciente.",
                rf"\begin{{gathered}}"
                rf"\frac{{d{simbolo}}}{{{simbolo}}}=-k\,dt\\[6px]"
                rf"\int\frac{{d{simbolo}}}{{{simbolo}}}=\int -k\,dt\\[6px]"
                rf"\ln|{simbolo}|=-kt+C_1\\[6px]"
                rf"\boxed{{{simbolo}(t)=Ce^{{-kt}}}}"
                rf"\end{{gathered}}",
            ),
            crear_paso(
                "Condición inicial",
                "Al evaluar en t=0, la constante C corresponde a la cantidad inicial.",
                rf"\begin{{gathered}}{simbolo}(0)=Ce^0=C\\[6px]\boxed{{C={y0}}}\end{{gathered}}",
            ),
            *pasos_constante,
            crear_paso(
                "Función particular",
                "Se reemplazan C y k en la solución del modelo.",
                rf"\boxed{{{simbolo}({str(variable_t)})={y0}e^{{-{k}{str(variable_t)}}}}}",
            ),
            crear_paso(
                "Chequeo simbólico con SymPy",
                "La expresión se conserva simbólicamente para evaluar tiempo, distancia, vida media o función.",
                paso_sympy(simbolo, variable_t, expresion_sympy),
            ),
        ]

        constantes = {"k": redondear(constante_k, DECIMALES_CONSTANTE), "C": redondear(cantidad_inicial), "vida_media": redondear(vida_media)}

        if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=variante,
                modelo=config["modelo"],
                tipo="funcion",
                resultado=f"{simbolo}(t)={y0}e^(-{k}t)",
                unidad="función",
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("valor_en_tiempo", "cantidad", "carga", "intensidad"):
            if not _hay_valor(datos, "tiempo_objetivo", "distancia_objetivo", "tiempo"):
                return formula_decaimiento({**datos, "variante": variante})
            tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "distancia_objetivo", "tiempo"), "tiempo o distancia objetivo"), "Tiempo o distancia objetivo")
            valor = evaluar(expresion_sympy, variable_t, tiempo_objetivo)
            pasos.append(crear_paso(
                "Evaluación del modelo",
                "Se evalúa la función particular en el tiempo o distancia solicitada.",
                rf"\begin{{gathered}}{simbolo}({formatear_numero(tiempo_objetivo)})={y0}e^{{-{k}({formatear_numero(tiempo_objetivo)})}}\\[6px]"
                rf"\boxed{{{simbolo}({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}\end{{gathered}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=variante,
                modelo=config["modelo"],
                tipo="valor_en_tiempo",
                resultado=redondear(valor),
                unidad=datos.get("unidad", config["unidad"]),
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad"):
            if not _hay_valor(datos, "cantidad_objetivo", "carga_objetivo", "intensidad_objetivo"):
                return formula_decaimiento({**datos, "variante": variante})
            cantidad_objetivo = validar_positivo(obtener_valor(datos, ("cantidad_objetivo", "carga_objetivo", "intensidad_objetivo"), "cantidad objetivo"), "Cantidad objetivo")
            if cantidad_objetivo >= cantidad_inicial:
                raise ErrorValidacion("En decaimiento, la cantidad objetivo debe ser menor que la cantidad inicial.")
            tiempo = log(cantidad_inicial / cantidad_objetivo) / constante_k
            objetivo = formatear_numero(cantidad_objetivo)
            pasos.append(crear_paso(
                "Tiempo para alcanzar una cantidad",
                "Se despeja t aplicando logaritmo natural.",
                rf"\begin{{gathered}}{objetivo}={y0}e^{{-{k}t}}\\[6px]"
                rf"t=\frac{{\ln\left(\frac{{{y0}}}{{{objetivo}}}\right)}}{{{k}}}\\[6px]"
                rf"\boxed{{t\approx {formatear_numero(tiempo)}}}\end{{gathered}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=variante,
                modelo=config["modelo"],
                tipo="tiempo_objetivo",
                resultado=redondear(tiempo),
                unidad="unidades de tiempo/distancia",
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("vida_media", "semivida"):
            pasos.append(crear_paso(
                "Vida media",
                "La vida media es el tiempo requerido para que quede la mitad de la cantidad inicial.",
                rf"\begin{{gathered}}\frac{{{y0}}}{{2}}={y0}e^{{-kt}}\\[6px]"
                rf"\boxed{{t_{{1/2}}=\frac{{\ln 2}}{{k}}={formatear_numero(vida_media)}}}\end{{gathered}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=variante,
                modelo=config["modelo"],
                tipo="vida_media",
                resultado=redondear(vida_media),
                unidad="unidades de tiempo",
                constantes=constantes,
                pasos=pasos,
            )

        raise ErrorValidacion("Tipo de cálculo inválido para decaimiento.")
    except (ErrorValidacion, ValueError, ZeroDivisionError) as error:
        return crear_respuesta_error(str(error))
