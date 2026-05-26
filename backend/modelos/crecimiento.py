"""Módulo de crecimiento y modelos lineales con entrada constante.

El objetivo de este módulo no es resolver ejercicios aislados, sino montar
modelos reutilizables. Las variantes internas se evalúan dentro de un mismo
método: crecimiento proporcional, interés continuo, crecimiento con entrada
constante y caída con resistencia del aire.

Regla académica importante:
    La constante k NO es obligatoria. Si no se entrega k y tampoco hay datos
    suficientes para inferirla, el módulo responde con una fórmula simbólica
    usando SymPy en lugar de bloquear el proceso.
"""
from __future__ import annotations

from math import log
from typing import Any

from backend.modelos.formulas_simbolicas import formula_crecimiento
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
    expresion_caida_resistencia,
    expresion_crecimiento_entrada_constante,
    expresion_crecimiento_exponencial,
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

MODULO = "crecimiento"


def _hay_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _respuesta_simbolica(datos: dict[str, Any], variante: str) -> dict[str, Any]:
    """Devuelve el planteamiento simbólico conservando los datos disponibles."""
    return formula_crecimiento({**datos, "variante": variante})


def _obtener_constante_crecimiento(
    datos: dict[str, Any],
    cantidad_inicial: float,
) -> tuple[float | None, list[dict[str, str]]]:
    """Obtiene k directamente, la infiere o devuelve None si debe quedar simbólica."""
    pasos: list[dict[str, str]] = []

    if _hay_valor(datos, "constante_k", "k"):
        constante_k = validar_positivo(obtener_valor(datos, ("constante_k", "k"), "constante k"), "Constante k")
        pasos.append(crear_paso(
            "Constante entregada",
            "La constante de proporcionalidad fue ingresada directamente.",
            rf"\boxed{{k={formatear_numero(constante_k, DECIMALES_CONSTANTE)}}}",
        ))
        return constante_k, pasos

    if not (_hay_valor(datos, "tiempo_transcurrido", "tiempo_conocido") and _hay_valor(datos, "cantidad_transcurrida", "cantidad_conocida")):
        pasos.append(crear_paso(
            "Constante k no entregada",
            "No se fuerza un valor inventado: k queda como parámetro simbólico del modelo.",
            r"\boxed{k\;\text{indeterminada}}",
        ))
        return None, pasos

    tiempo_conocido = validar_positivo(
        obtener_valor(datos, ("tiempo_transcurrido", "tiempo_conocido"), "tiempo conocido"),
        "Tiempo conocido",
    )
    cantidad_conocida = validar_positivo(
        obtener_valor(datos, ("cantidad_transcurrida", "cantidad_conocida"), "cantidad conocida"),
        "Cantidad conocida",
    )
    if cantidad_conocida <= cantidad_inicial:
        raise ErrorValidacion("Para crecimiento proporcional, la cantidad conocida debe ser mayor que la inicial.")

    constante_k = log(cantidad_conocida / cantidad_inicial) / tiempo_conocido
    p0 = formatear_numero(cantidad_inicial)
    p1 = formatear_numero(cantidad_conocida)
    t1 = formatear_numero(tiempo_conocido)
    k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
    pasos.append(crear_paso(
        "Inferencia de k",
        "Como no se ingresó k, se calcula usando una observación posterior.",
        rf"\begin{{gathered}}"
        rf"P({t1})={p1},\quad P(0)={p0}\\[6px]"
        rf"{p1}={p0}e^{{k({t1})}}\\[6px]"
        rf"k=\frac{{\ln\left(\frac{{{p1}}}{{{p0}}}\right)}}{{{t1}}}\\[6px]"
        rf"\boxed{{k={k}}}"
        rf"\end{{gathered}}",
    ))
    return constante_k, pasos


def _resolver_exponencial_base(datos: dict[str, Any], variante: str, etiqueta: str, simbolo: str = "P") -> dict[str, Any]:
    """Evalúa modelos de la forma y' = ky; si k falta, responde simbólicamente."""
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "valor_en_tiempo"))
    if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
        return _respuesta_simbolica(datos, variante)

    if not _hay_valor(datos, "cantidad_inicial", "capital_inicial", "poblacion_inicial"):
        return _respuesta_simbolica(datos, variante)

    cantidad_inicial = validar_positivo(
        obtener_valor(datos, ("cantidad_inicial", "capital_inicial", "poblacion_inicial"), "cantidad inicial"),
        "Cantidad inicial",
    )
    constante_k, pasos_constante = _obtener_constante_crecimiento(datos, cantidad_inicial)
    if constante_k is None:
        return _respuesta_simbolica(datos, variante)

    variable_t = crear_variable("t")
    expresion_sympy = expresion_crecimiento_exponencial(cantidad_inicial, constante_k, variable_t)
    y0 = formatear_numero(cantidad_inicial)
    k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
    pasos = [
        crear_paso(
            "Modelo diferencial",
            "La razón de cambio es proporcional a la cantidad presente.",
            rf"\frac{{d{simbolo}}}{{dt}}=k{simbolo}",
        ),
        crear_paso(
            "Solución general del modelo",
            "Se separan variables, se integra y se obtiene el modelo exponencial.",
            rf"\begin{{gathered}}"
            rf"\frac{{d{simbolo}}}{{{simbolo}}}=k\,dt\\[6px]"
            rf"\int \frac{{d{simbolo}}}{{{simbolo}}}=\int k\,dt\\[6px]"
            rf"\ln|{simbolo}|=kt+C_1\\[6px]"
            rf"\boxed{{{simbolo}(t)=Ce^{{kt}}}}"
            rf"\end{{gathered}}",
        ),
        crear_paso(
            "Condición inicial",
            "Al evaluar en t=0, la constante C queda igual a la cantidad inicial.",
            rf"\begin{{gathered}}{simbolo}(0)=Ce^{{0}}=C\\[6px]\boxed{{C={y0}}}\end{{gathered}}",
        ),
        *pasos_constante,
        crear_paso(
            "Función particular",
            "Se reemplazan C y k en la solución general.",
            rf"\boxed{{{simbolo}(t)={y0}e^{{{k}t}}}}",
        ),
        crear_paso(
            "Chequeo simbólico con SymPy",
            "Antes de evaluar, la función se representa simbólicamente para conservar una salida LaTeX limpia.",
            paso_sympy(simbolo, variable_t, expresion_sympy),
        ),
    ]

    constantes = {"k": redondear(constante_k, DECIMALES_CONSTANTE), "C": redondear(cantidad_inicial)}

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante=variante,
            modelo=etiqueta,
            tipo="funcion",
            resultado=f"{simbolo}(t)={y0}e^({k}t)",
            unidad="función",
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("valor_en_tiempo", "cantidad", "poblacion", "monto"):
        if not _hay_valor(datos, "tiempo_objetivo", "tiempo"):
            return _respuesta_simbolica(datos, variante)
        tiempo_objetivo = validar_no_negativo(
            obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"),
            "Tiempo objetivo",
        )
        valor = evaluar(expresion_sympy, variable_t, tiempo_objetivo)
        tx = formatear_numero(tiempo_objetivo)
        pasos.append(crear_paso(
            "Evaluación del modelo",
            "Se evalúa la función particular en el tiempo solicitado.",
            rf"\begin{{gathered}}{simbolo}({tx})={y0}e^{{{k}({tx})}}\\[6px]"
            rf"\boxed{{{simbolo}({tx})\approx {formatear_numero(valor)}}}\end{{gathered}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante=variante,
            modelo=etiqueta,
            tipo="valor_en_tiempo",
            resultado=redondear(valor),
            unidad=datos.get("unidad", "unidades"),
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad"):
        if not _hay_valor(datos, "cantidad_objetivo", "poblacion_objetivo", "monto_objetivo"):
            return _respuesta_simbolica(datos, variante)
        cantidad_objetivo = validar_positivo(
            obtener_valor(datos, ("cantidad_objetivo", "poblacion_objetivo", "monto_objetivo"), "cantidad objetivo"),
            "Cantidad objetivo",
        )
        if cantidad_objetivo < cantidad_inicial:
            raise ErrorValidacion("En crecimiento proporcional, la cantidad objetivo debe ser mayor o igual que la inicial.")
        tiempo = log(cantidad_objetivo / cantidad_inicial) / constante_k
        objetivo = formatear_numero(cantidad_objetivo)
        pasos.append(crear_paso(
            "Tiempo para alcanzar una cantidad",
            "Se despeja t aplicando logaritmo natural.",
            rf"\begin{{gathered}}{objetivo}={y0}e^{{{k}t}}\\[6px]"
            rf"t=\frac{{\ln\left(\frac{{{objetivo}}}{{{y0}}}\right)}}{{{k}}}\\[6px]"
            rf"\boxed{{t\approx {formatear_numero(tiempo)}}}\end{{gathered}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante=variante,
            modelo=etiqueta,
            tipo="tiempo_objetivo",
            resultado=redondear(tiempo),
            unidad="unidades de tiempo",
            constantes=constantes,
            pasos=pasos,
        )

    raise ErrorValidacion("Tipo de cálculo inválido para la variante exponencial de crecimiento.")


def _resolver_interes_continuo(datos: dict[str, Any]) -> dict[str, Any]:
    """Evalúa S' = rS usando tasa continua anual. La tasa puede quedar simbólica."""
    datos_normalizados = dict(datos)
    if not _hay_valor(datos_normalizados, "constante_k", "k"):
        if _hay_valor(datos_normalizados, "tasa_porcentual", "tasa"):
            tasa_porcentual = validar_positivo(
                obtener_valor(datos_normalizados, ("tasa_porcentual", "tasa"), "tasa porcentual"),
                "Tasa porcentual",
            )
            datos_normalizados["constante_k"] = tasa_porcentual / 100
        else:
            return _respuesta_simbolica(datos_normalizados, "interes_continuo")
    datos_normalizados.setdefault("unidad", "dinero")
    return _resolver_exponencial_base(
        datos_normalizados,
        variante="interes_continuo",
        etiqueta="Interés compuesto continuo: S'=rS",
        simbolo="S",
    )


def _resolver_entrada_constante(datos: dict[str, Any]) -> dict[str, Any]:
    """Evalúa P' = kP + b. Si k no llega, muestra la fórmula simbólica."""
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "valor_en_tiempo"))
    if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
        return _respuesta_simbolica(datos, "entrada_constante")
    if not (_hay_valor(datos, "cantidad_inicial", "poblacion_inicial") and _hay_valor(datos, "constante_k", "k") and _hay_valor(datos, "entrada_constante", "b")):
        return _respuesta_simbolica(datos, "entrada_constante")

    cantidad_inicial = validar_positivo(obtener_valor(datos, ("cantidad_inicial", "poblacion_inicial"), "cantidad inicial"), "Cantidad inicial")
    constante_k = validar_positivo(obtener_valor(datos, ("constante_k", "k"), "constante k"), "Constante k")
    entrada_constante = validar_no_negativo(obtener_valor(datos, ("entrada_constante", "b"), "entrada constante"), "Entrada constante")

    variable_t = crear_variable("t")
    expresion_sympy = expresion_crecimiento_entrada_constante(cantidad_inicial, constante_k, entrada_constante, variable_t)
    p0 = formatear_numero(cantidad_inicial)
    k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
    b = formatear_numero(entrada_constante)
    equilibrio = -entrada_constante / constante_k

    def funcion(tiempo: float) -> float:
        return evaluar(expresion_sympy, variable_t, tiempo)

    pasos = [
        crear_paso("Modelo diferencial", "La población crece proporcionalmente y además recibe una entrada constante.", r"\frac{dP}{dt}=kP+b"),
        crear_paso("Solución general", "Es una EDO lineal de primer orden con término independiente constante.", r"\begin{gathered}\frac{dP}{dt}-kP=b\\[6px]P(t)=Ce^{kt}-\frac{b}{k}\end{gathered}"),
        crear_paso("Condición inicial", "Se aplica P(0)=P0 para calcular C.", rf"\begin{{gathered}}{p0}=C-\frac{{{b}}}{{{k}}}\\[6px]\boxed{{C={formatear_numero(cantidad_inicial + entrada_constante / constante_k)}}}\end{{gathered}}"),
        crear_paso("Función particular", "Se sustituyen los parámetros del modelo.", rf"\boxed{{P(t)=\left({p0}+\frac{{{b}}}{{{k}}}\right)e^{{{k}t}}-\frac{{{b}}}{{{k}}}}}"),
        crear_paso("Chequeo simbólico con SymPy", "La variante lineal se deja como expresión simbólica y luego se evalúa numéricamente.", paso_sympy("P", variable_t, expresion_sympy)),
    ]

    constantes = {
        "k": redondear(constante_k, DECIMALES_CONSTANTE),
        "b": redondear(entrada_constante),
        "C": redondear(cantidad_inicial + entrada_constante / constante_k),
        "equilibrio_matematico": redondear(equilibrio),
    }

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(modulo=MODULO, variante="entrada_constante", modelo="Crecimiento con entrada constante: P'=kP+b", tipo="funcion", resultado=f"P(t)=({p0}+{b}/{k})e^({k}t)-{b}/{k}", unidad="función", constantes=constantes, pasos=pasos)

    if tipo_calculo in ("valor_en_tiempo", "cantidad", "poblacion"):
        if not _hay_valor(datos, "tiempo_objetivo", "tiempo"):
            return _respuesta_simbolica(datos, "entrada_constante")
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = funcion(tiempo_objetivo)
        pasos.append(crear_paso("Evaluación del modelo", "Se reemplaza el tiempo solicitado en la función particular.", rf"\boxed{{P({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}"))
        return crear_respuesta_modelo(modulo=MODULO, variante="entrada_constante", modelo="Crecimiento con entrada constante: P'=kP+b", tipo="valor_en_tiempo", resultado=redondear(valor), unidad=datos.get("unidad", "individuos"), constantes=constantes, pasos=pasos)

    raise ErrorValidacion("Tipo de cálculo inválido para crecimiento con entrada constante.")


def _resolver_caida_resistencia(datos: dict[str, Any]) -> dict[str, Any]:
    """Evalúa v' = g - kv. Si k falta, deja v(t) y v∞ simbólicas."""
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "valor_en_tiempo"))
    if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
        return _respuesta_simbolica(datos, "caida_resistencia")
    if not (_hay_valor(datos, "velocidad_inicial", "cantidad_inicial") and _hay_valor(datos, "gravedad", "g") and _hay_valor(datos, "constante_k", "k")):
        return _respuesta_simbolica(datos, "caida_resistencia")

    velocidad_inicial = validar_no_negativo(obtener_valor(datos, ("velocidad_inicial", "cantidad_inicial"), "velocidad inicial"), "Velocidad inicial")
    gravedad = validar_positivo(obtener_valor(datos, ("gravedad", "g"), "gravedad"), "Gravedad")
    constante_k = validar_positivo(obtener_valor(datos, ("constante_k", "k"), "constante k"), "Constante k")
    velocidad_limite = gravedad / constante_k
    variable_t = crear_variable("t")
    expresion_sympy = expresion_caida_resistencia(velocidad_inicial, gravedad, constante_k, variable_t)

    v0 = formatear_numero(velocidad_inicial)
    g = formatear_numero(gravedad)
    k = formatear_numero(constante_k, DECIMALES_CONSTANTE)
    vl = formatear_numero(velocidad_limite)

    def funcion(tiempo: float) -> float:
        return evaluar(expresion_sympy, variable_t, tiempo)

    pasos = [
        crear_paso("Modelo diferencial", "La aceleración disminuye por una resistencia proporcional a la velocidad.", r"\frac{dv}{dt}=g-kv"),
        crear_paso("Solución general", "Es una EDO lineal con equilibrio en la velocidad límite.", r"\begin{gathered}\frac{dv}{dt}+kv=g\\[6px]v(t)=\frac{g}{k}+Ce^{-kt}\end{gathered}"),
        crear_paso("Condición inicial", "Se aplica v(0)=v0 para encontrar C.", rf"\begin{{gathered}}{v0}=\frac{{{g}}}{{{k}}}+C\\[6px]\boxed{{C={formatear_numero(velocidad_inicial - velocidad_limite)}}}\end{{gathered}}"),
        crear_paso("Función particular", "Se reemplazan los parámetros en el modelo de velocidad.", rf"\boxed{{v(t)={vl}+({v0}-{vl})e^{{-{k}t}}}}"),
        crear_paso("Chequeo simbólico con SymPy", "SymPy conserva la forma simbólica de la velocidad antes de evaluar o tomar el límite.", paso_sympy("v", variable_t, expresion_sympy)),
    ]

    constantes = {"g": redondear(gravedad), "k": redondear(constante_k, DECIMALES_CONSTANTE), "velocidad_limite": redondear(velocidad_limite)}

    if tipo_calculo in ("velocidad_limite", "limite", "equilibrio"):
        pasos.append(crear_paso("Velocidad límite", "Cuando t tiende a infinito, el término exponencial desaparece.", rf"\lim_{{t\to\infty}}v(t)=\frac{{g}}{{k}}=\boxed{{{vl}}}"))
        return crear_respuesta_modelo(modulo=MODULO, variante="caida_resistencia", modelo="Caída con resistencia del aire: v'=g-kv", tipo="velocidad_limite", resultado=redondear(velocidad_limite), unidad="m/s", constantes=constantes, pasos=pasos)

    if tipo_calculo in ("valor_en_tiempo", "velocidad"):
        if not _hay_valor(datos, "tiempo_objetivo", "tiempo"):
            return _respuesta_simbolica(datos, "caida_resistencia")
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = funcion(tiempo_objetivo)
        pasos.append(crear_paso("Evaluación de velocidad", "Se evalúa la función en el tiempo solicitado.", rf"\boxed{{v({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}"))
        return crear_respuesta_modelo(modulo=MODULO, variante="caida_resistencia", modelo="Caída con resistencia del aire: v'=g-kv", tipo="valor_en_tiempo", resultado=redondear(valor), unidad="m/s", constantes=constantes, pasos=pasos)

    if tipo_calculo in ("funcion", "solucion"):
        return crear_respuesta_modelo(modulo=MODULO, variante="caida_resistencia", modelo="Caída con resistencia del aire: v'=g-kv", tipo="funcion", resultado=f"v(t)={vl}+({v0}-{vl})e^(-{k}t)", unidad="función", constantes=constantes, pasos=pasos)

    raise ErrorValidacion("Tipo de cálculo inválido para caída con resistencia del aire.")


def resolver_crecimiento(datos: dict[str, Any]) -> dict[str, Any]:
    """Método único del módulo crecimiento que evalúa sus variantes internas."""
    try:
        variante = normalizar_texto(datos.get("variante", "crecimiento_proporcional"))
        tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "valor_en_tiempo"))
        if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
            return formula_crecimiento(datos)
        if variante in ("crecimiento_proporcional", "poblacional", "exp_base"):
            return _resolver_exponencial_base(datos, variante="crecimiento_proporcional", etiqueta="Crecimiento proporcional: P'=kP", simbolo="P")
        if variante in ("interes_continuo", "interes_compuesto_continuo"):
            return _resolver_interes_continuo(datos)
        if variante in ("entrada_constante", "crecimiento_entrada_constante", "lineal_entrada"):
            return _resolver_entrada_constante(datos)
        if variante in ("caida_resistencia", "velocidad_limite"):
            return _resolver_caida_resistencia(datos)
        raise ErrorValidacion(f"Variante no soportada en crecimiento: {variante}.")
    except (ErrorValidacion, ValueError, ZeroDivisionError) as error:
        return crear_respuesta_error(str(error))
