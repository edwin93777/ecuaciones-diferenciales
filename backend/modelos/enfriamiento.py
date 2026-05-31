"""Módulo de enfriamiento por Ley de Newton."""
from __future__ import annotations

from math import exp, log
from typing import Any

from backend.modelos.formulas_simbolicas import formula_enfriamiento
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
    expresion_newton,
    paso_sympy,
)
from backend.utils.validacion import (
    ErrorValidacion,
    crear_respuesta_error,
    normalizar_texto,
    obtener_valor,
    validar_no_negativo,
    validar_numero,
    validar_positivo,
)

MODULO = "enfriamiento"


def _hay_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _inferir_k(temperatura_inicial: float, temperatura_ambiente: float, temperatura_conocida: float, tiempo_conocido: float) -> float:
    diferencia_inicial = temperatura_inicial - temperatura_ambiente
    diferencia_conocida = temperatura_conocida - temperatura_ambiente

    if diferencia_inicial == 0:
        raise ErrorValidacion("La temperatura inicial no puede ser igual a la temperatura ambiente.")
    if diferencia_inicial * diferencia_conocida <= 0:
        raise ErrorValidacion("La temperatura conocida debe estar del mismo lado de la temperatura ambiente que la inicial.")
    if abs(diferencia_conocida) >= abs(diferencia_inicial):
        raise ErrorValidacion("La temperatura debe acercarse a la ambiente; la diferencia conocida debe ser menor.")

    return -log(diferencia_conocida / diferencia_inicial) / tiempo_conocido


def resolver_enfriamiento(datos: dict[str, Any]) -> dict[str, Any]:
    """Método único del módulo enfriamiento que evalúa variantes de Newton."""
    try:
        variante = normalizar_texto(datos.get("variante", "newton_constante"))
        if variante not in ("newton_constante", "ley_newton", "calentamiento_newton"):
            raise ErrorValidacion(f"Variante no soportada en enfriamiento: {variante}.")

        tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "temperatura"))
        if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
            return formula_enfriamiento(datos)
        if not (_hay_valor(datos, "temperatura_inicial", "T0") and _hay_valor(datos, "temperatura_ambiente", "Ta")):
            return formula_enfriamiento(datos)
        temperatura_inicial = validar_numero(obtener_valor(datos, ("temperatura_inicial", "T0"), "temperatura inicial"), "Temperatura inicial")
        temperatura_ambiente = validar_numero(obtener_valor(datos, ("temperatura_ambiente", "Ta"), "temperatura ambiente"), "Temperatura ambiente")

        if _hay_valor(datos, "constante_k", "k"):
            constante_k = validar_positivo(obtener_valor(datos, ("constante_k", "k"), "constante k"), "Constante k")
            pasos_constante = [crear_paso(
                "Constante entregada",
                "La constante de enfriamiento fue ingresada directamente.",
                rf"\boxed{{k={formatear_numero(constante_k, DECIMALES_CONSTANTE)}}}",
            )]
        else:
            if not (_hay_valor(datos, "temperatura_transcurrida", "temperatura_conocida", "T1") and _hay_valor(datos, "tiempo_transcurrido", "tiempo_conocido")):
                return formula_enfriamiento(datos)
            temperatura_conocida = validar_numero(obtener_valor(datos, ("temperatura_transcurrida", "temperatura_conocida", "T1"), "temperatura conocida"), "Temperatura conocida")
            tiempo_conocido = validar_positivo(obtener_valor(datos, ("tiempo_transcurrido", "tiempo_conocido"), "tiempo conocido"), "Tiempo conocido")
            constante_k = _inferir_k(temperatura_inicial, temperatura_ambiente, temperatura_conocida, tiempo_conocido)
            pasos_constante = [crear_paso(
                "Inferencia de k",
                "Se usa la medición conocida para calcular la constante de Newton.",
                rf"\begin{{gathered}}"
                rf"T(t)=T_a+(T_0-T_a)e^{{-kt}}\\[6px]"
                rf"{formatear_numero(temperatura_conocida)}={formatear_numero(temperatura_ambiente)}+({formatear_numero(temperatura_inicial)}-{formatear_numero(temperatura_ambiente)})e^{{-k({formatear_numero(tiempo_conocido)})}}\\[6px]"
                rf"k=-\frac{{1}}{{{formatear_numero(tiempo_conocido)}}}\ln\left(\frac{{{formatear_numero(temperatura_conocida)}-{formatear_numero(temperatura_ambiente)}}}{{{formatear_numero(temperatura_inicial)}-{formatear_numero(temperatura_ambiente)}}}\right)\\[6px]"
                rf"\boxed{{k={formatear_numero(constante_k, DECIMALES_CONSTANTE)}}}"
                rf"\end{{gathered}}",
            )]

        t0 = formatear_numero(temperatura_inicial)
        ta = formatear_numero(temperatura_ambiente)
        diferencia = formatear_numero(temperatura_inicial - temperatura_ambiente)
        k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
        variable_t = crear_variable("t")
        expresion_sympy = expresion_newton(temperatura_inicial, temperatura_ambiente, constante_k, variable_t)

        def funcion(tiempo: float) -> float:
            return evaluar(expresion_sympy, variable_t, tiempo)

        pasos = [
            crear_paso(
                "Modelo diferencial",
                "La temperatura cambia proporcionalmente a la diferencia entre el objeto y el ambiente.",
                r"\frac{dT}{dt}=-k(T-T_a)",
            ),
            crear_paso(
                "Solución general",
                "Se desplaza la variable respecto a la temperatura ambiente y se integra.",
                r"\begin{gathered}U=T-T_a\\[6px]"
                r"\frac{dU}{dt}=-kU\\[6px]"
                r"U(t)=Ce^{-kt}\\[6px]"
                r"\boxed{T(t)=T_a+Ce^{-kt}}\end{gathered}",
            ),
            crear_paso(
                "Condición inicial",
                "Con T(0)=T0, la constante C es la diferencia inicial con el ambiente.",
                rf"\begin{{gathered}}{t0}={ta}+C\\[6px]\boxed{{C={diferencia}}}\end{{gathered}}",
            ),
            *pasos_constante,
            crear_paso(
                "Función particular",
                "Se reemplazan la temperatura ambiente, la diferencia inicial y k.",
                rf"\boxed{{T(t)={ta}+({diferencia})e^{{-{k}t}}}}",
            ),
            crear_paso(
                "Chequeo simbólico con SymPy",
                "La función de Newton se conserva simbólicamente antes de evaluar temperatura, tiempo o límite.",
                paso_sympy("T", variable_t, expresion_sympy),
            ),
        ]

        constantes = {
            "k": redondear(constante_k, DECIMALES_CONSTANTE),
            "Ta": redondear(temperatura_ambiente),
            "C": redondear(temperatura_inicial - temperatura_ambiente),
        }

        if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante="newton_constante",
                modelo="Ley de enfriamiento de Newton: T'=-k(T-Ta)",
                tipo="funcion",
                resultado=f"T(t)={ta}+({diferencia})e^(-{k}t)",
                unidad="función",
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("temperatura", "valor_en_tiempo"):
            if not _hay_valor(datos, "tiempo_objetivo", "tiempo"):
                return formula_enfriamiento(datos)
            tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
            temperatura = funcion(tiempo_objetivo)
            pasos.append(crear_paso(
                "Temperatura solicitada",
                "Se evalúa el modelo en el tiempo indicado.",
                rf"\boxed{{T({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(temperatura)}}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante="newton_constante",
                modelo="Ley de enfriamiento de Newton: T'=-k(T-Ta)",
                tipo="temperatura",
                resultado=redondear(temperatura),
                unidad="°C",
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("tiempo_objetivo", "tiempo", "tiempo_para_temperatura"):
            if not _hay_valor(datos, "temperatura_objetivo", "T_objetivo"):
                return formula_enfriamiento(datos)
            temperatura_objetivo = validar_numero(obtener_valor(datos, ("temperatura_objetivo", "T_objetivo"), "temperatura objetivo"), "Temperatura objetivo")
            diferencia_inicial = temperatura_inicial - temperatura_ambiente
            diferencia_objetivo = temperatura_objetivo - temperatura_ambiente
            if diferencia_inicial * diferencia_objetivo <= 0:
                raise ErrorValidacion("La temperatura objetivo debe estar del mismo lado de la temperatura ambiente que la inicial.")
            if abs(diferencia_objetivo) > abs(diferencia_inicial):
                raise ErrorValidacion("La temperatura objetivo debe estar entre la inicial y la ambiente.")
            tiempo = -log(diferencia_objetivo / diferencia_inicial) / constante_k
            pasos.append(crear_paso(
                "Tiempo para alcanzar una temperatura",
                "Se despeja t usando logaritmo natural.",
                rf"\begin{{gathered}}{formatear_numero(temperatura_objetivo)}={ta}+({diferencia})e^{{-{k}t}}\\[6px]"
                rf"t=-\frac{{1}}{{{k}}}\ln\left(\frac{{{formatear_numero(temperatura_objetivo)}-{ta}}}{{{diferencia}}}\right)\\[6px]"
                rf"\boxed{{t\approx {formatear_numero(tiempo)}}}\end{{gathered}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante="newton_constante",
                modelo="Ley de enfriamiento de Newton: T'=-k(T-Ta)",
                tipo="tiempo_objetivo",
                resultado=redondear(tiempo),
                unidad="unidades de tiempo",
                constantes=constantes,
                pasos=pasos,
            )

        if tipo_calculo in ("equilibrio", "limite"):
            pasos.append(crear_paso(
                "Comportamiento límite",
                "Cuando el tiempo crece, la temperatura del objeto se aproxima a la del ambiente.",
                rf"\lim_{{t\to\infty}}T(t)=\boxed{{T_a={ta}}}",
            ))
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante="newton_constante",
                modelo="Ley de enfriamiento de Newton: T'=-k(T-Ta)",
                tipo="equilibrio",
                resultado=redondear(temperatura_ambiente),
                unidad="°C",
                constantes=constantes,
                pasos=pasos,
            )

        raise ErrorValidacion("Tipo de cálculo inválido para enfriamiento.")
    except (ErrorValidacion, ValueError, ZeroDivisionError) as error:
        return crear_respuesta_error(str(error))
