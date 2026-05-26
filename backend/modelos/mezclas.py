"""Módulo de mezclas en tanques.

Contiene variantes de volumen constante y volumen variable dentro del mismo
método, en lugar de crear un módulo por ejercicio.

Ajuste académico aplicado:
    La concentración de salida puede ingresarse de forma opcional. Si no se
    proporciona, se usa el modelo clásico donde la concentración de salida es
    la concentración instantánea del tanque, A(t)/V(t). Si se proporciona, el
    sistema evalúa una salida fija r_s c_s sin bloquear el modelo.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

from backend.modelos.formulas_simbolicas import formula_mezclas
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
    expresion_mezcla_volumen_constante,
    expresion_mezcla_volumen_variable,
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

MODULO = "mezclas"


def _hay_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _obtener_concentracion_salida(datos: dict[str, Any]) -> float | None:
    """Obtiene concentración de salida fija cuando el usuario la proporciona."""
    if not _hay_valor(datos, "concentracion_salida", "c_salida", "cs", "c_out"):
        return None
    return validar_no_negativo(
        obtener_valor(datos, ("concentracion_salida", "c_salida", "cs", "c_out"), "concentración de salida"),
        "Concentración de salida",
    )


def _datos_base(datos: dict[str, Any]) -> tuple[float, float, float, float, float, float | None]:
    sal_inicial = validar_no_negativo(
        obtener_valor(datos, ("sal_inicial", "cantidad_inicial", "A0"), "cantidad inicial de soluto"),
        "Cantidad inicial de soluto",
    )
    volumen_inicial = validar_positivo(
        obtener_valor(datos, ("volumen_inicial", "V0"), "volumen inicial"),
        "Volumen inicial",
    )
    caudal_entrada = validar_no_negativo(
        obtener_valor(datos, ("caudal_entrada", "r_entrada", "rin"), "caudal de entrada"),
        "Caudal de entrada",
    )
    caudal_salida = validar_no_negativo(
        obtener_valor(datos, ("caudal_salida", "r_salida", "rout"), "caudal de salida"),
        "Caudal de salida",
    )
    concentracion_entrada = validar_no_negativo(
        obtener_valor(datos, ("concentracion_entrada", "c_entrada", "cin"), "concentración de entrada"),
        "Concentración de entrada",
    )
    concentracion_salida = _obtener_concentracion_salida(datos)
    if caudal_entrada == 0 and caudal_salida == 0:
        raise ErrorValidacion("Al menos uno de los caudales debe ser mayor que cero.")
    return sal_inicial, volumen_inicial, caudal_entrada, caudal_salida, concentracion_entrada, concentracion_salida


def _resolver_volumen_constante_con_salida_fija(
    datos: dict[str, Any],
    sal_inicial: float,
    volumen_inicial: float,
    caudal_entrada: float,
    caudal_salida: float,
    concentracion_entrada: float,
    concentracion_salida: float,
) -> dict[str, Any]:
    """Resuelve dA/dt = r_e c_e - r_s c_s cuando c_s se ingresa explícitamente."""
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad"))
    entrada_soluto = caudal_entrada * concentracion_entrada
    salida_soluto = caudal_salida * concentracion_salida
    pendiente = entrada_soluto - salida_soluto
    variable_t = crear_variable("t")
    expresion_sympy = sal_inicial + pendiente * variable_t

    def cantidad(tiempo: float) -> float:
        return evaluar(expresion_sympy, variable_t, tiempo)

    a0 = formatear_numero(sal_inicial)
    v0 = formatear_numero(volumen_inicial)
    rin = formatear_numero(caudal_entrada)
    rout = formatear_numero(caudal_salida)
    cin = formatear_numero(concentracion_entrada)
    cs = formatear_numero(concentracion_salida)
    entrada = formatear_numero(entrada_soluto)
    salida = formatear_numero(salida_soluto)
    m = formatear_numero(pendiente)

    pasos = [
        crear_paso(
            "Modelo diferencial con salida fija",
            "Como se ingresó concentración de salida, la salida de soluto se evalúa como r_s c_s. Si no se ingresa, el modelo clásico usa A/V.",
            r"\frac{dA}{dt}=r_ec_e-r_sc_s",
        ),
        crear_paso(
            "Sustitución de datos",
            "Se reemplazan concentración de entrada, concentración de salida y caudales.",
            rf"\begin{{gathered}}"
            rf"V={v0},\quad r_e={rin},\quad c_e={cin},\quad r_s={rout},\quad c_s={cs}\\[6px]"
            rf"\frac{{dA}}{{dt}}={rin}({cin})-{rout}({cs})={entrada}-{salida}\\[6px]"
            rf"\boxed{{\frac{{dA}}{{dt}}={m}}}"
            rf"\end{{gathered}}",
        ),
        crear_paso(
            "Integración directa",
            "Con entrada y salida fijas, la cantidad cambia linealmente respecto al tiempo.",
            rf"\begin{{gathered}}A(t)=A_0+({m})t\\[6px]\boxed{{A(t)={a0}+({m})t}}\end{{gathered}}",
        ),
        crear_paso(
            "Chequeo simbólico con SymPy",
            "La expresión lineal se conserva como fórmula matemática antes de evaluar.",
            paso_sympy("A", variable_t, expresion_sympy),
        ),
    ]

    constantes = {
        "entrada_soluto": redondear(entrada_soluto),
        "salida_soluto": redondear(salida_soluto),
        "pendiente": redondear(pendiente),
        "volumen": redondear(volumen_inicial),
        "concentracion_salida": redondear(concentracion_salida),
    }

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante y concentración de salida fija",
            tipo="funcion",
            resultado=f"A(t)={a0}+({m})t",
            resultado_latex=rf"A(t)={a0}+({m})t",
            unidad="función",
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("cantidad", "valor_en_tiempo", "sal"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo)
        concentracion = valor / volumen_inicial
        tx = formatear_numero(tiempo_objetivo)
        pasos.append(crear_paso(
            "Cantidad solicitada",
            "Se evalúa la función lineal en el tiempo indicado.",
            rf"\boxed{{A({tx})={a0}+({m})({tx})\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante y concentración de salida fija",
            tipo="cantidad",
            resultado=redondear(valor),
            unidad="kg de soluto",
            constantes=constantes,
            pasos=pasos,
            metadatos={"concentracion": redondear(concentracion)},
        )

    if tipo_calculo in ("concentracion", "concentracion_en_tiempo"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo) / volumen_inicial
        tx = formatear_numero(tiempo_objetivo)
        pasos.append(crear_paso(
            "Concentración solicitada",
            "Como el volumen es constante, la concentración se obtiene dividiendo A(t) entre V.",
            rf"\boxed{{C({tx})=\frac{{A({tx})}}{{{v0}}}\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante y concentración de salida fija",
            tipo="concentracion",
            resultado=redondear(valor),
            unidad="kg/L",
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("limite", "equilibrio"):
        if abs(pendiente) < 1e-12:
            resultado = sal_inicial
            resultado_latex = rf"\lim_{{t\to\infty}}A(t)={a0}"
            unidad = "kg de soluto"
        elif pendiente > 0:
            resultado = "La cantidad crece linealmente sin límite finito."
            resultado_latex = r"\lim_{t\to\infty}A(t)=+\infty"
            unidad = "comportamiento"
        else:
            resultado = "El modelo lineal tiende a valores negativos; físicamente debe detenerse cuando A(t)=0."
            resultado_latex = r"A(t)=0\quad\Rightarrow\quad t=\frac{A_0}{r_sc_s-r_ec_e}"
            unidad = "comportamiento"
        pasos.append(crear_paso(
            "Comportamiento límite",
            "Con concentración de salida fija no aparece equilibrio exponencial; el comportamiento depende de la pendiente neta.",
            resultado_latex,
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante y concentración de salida fija",
            tipo="limite",
            resultado=redondear(resultado) if isinstance(resultado, (int, float)) else resultado,
            resultado_latex=resultado_latex,
            unidad=unidad,
            constantes=constantes,
            pasos=pasos,
        )

    raise ErrorValidacion("Tipo de cálculo inválido para mezclas con volumen constante.")


def _resolver_volumen_constante(datos: dict[str, Any]) -> dict[str, Any]:
    sal_inicial, volumen_inicial, caudal_entrada, caudal_salida, concentracion_entrada, concentracion_salida = _datos_base(datos)
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad"))

    if abs(caudal_entrada - caudal_salida) > 1e-9:
        raise ErrorValidacion("Para la variante volumen_constante, el caudal de entrada debe ser igual al caudal de salida.")
    if caudal_salida == 0:
        raise ErrorValidacion("En volumen constante debe existir caudal de salida.")
    if concentracion_salida is not None:
        return _resolver_volumen_constante_con_salida_fija(
            datos,
            sal_inicial,
            volumen_inicial,
            caudal_entrada,
            caudal_salida,
            concentracion_entrada,
            concentracion_salida,
        )

    constante_salida = caudal_salida / volumen_inicial
    entrada_soluto = caudal_entrada * concentracion_entrada
    equilibrio = entrada_soluto / constante_salida
    coeficiente_inicial = sal_inicial - equilibrio
    variable_t = crear_variable("t")
    expresion_sympy = expresion_mezcla_volumen_constante(sal_inicial, equilibrio, constante_salida, variable_t)

    def cantidad(tiempo: float) -> float:
        return evaluar(expresion_sympy, variable_t, tiempo)

    a0 = formatear_numero(sal_inicial)
    v0 = formatear_numero(volumen_inicial)
    rin = formatear_numero(caudal_entrada)
    rout = formatear_numero(caudal_salida)
    cin = formatear_numero(concentracion_entrada)
    alfa = formatear_numero(constante_salida, DECIMALES_CONSTANTE)
    entrada = formatear_numero(entrada_soluto)
    limite = formatear_numero(equilibrio)
    coef = formatear_numero(coeficiente_inicial)

    pasos = [
        crear_paso(
            "Modelo diferencial",
            "La cantidad de soluto cambia por entrada menos salida. Como los caudales son iguales, el volumen permanece constante.",
            r"\frac{dA}{dt}=r_e c_e-r_s\frac{A}{V}",
        ),
        crear_paso(
            "Sustitución del modelo",
            "Se reemplazan caudales, concentración y volumen.",
            rf"\begin{{gathered}}V={v0},\quad r_e={rin},\quad r_s={rout},\quad c_e={cin}\\[6px]"
            rf"\frac{{dA}}{{dt}}={rin}({cin})-{rout}\frac{{A}}{{{v0}}}\\[6px]"
            rf"\boxed{{\frac{{dA}}{{dt}}={entrada}-{alfa}A}}\end{{gathered}}",
        ),
        crear_paso(
            "Solución de la EDO lineal",
            "La solución se aproxima a un equilibrio donde entrada y salida se compensan.",
            rf"\begin{{gathered}}A(t)=A_\infty+(A_0-A_\infty)e^{{-({alfa})t}}\\[6px]"
            rf"A_\infty=\frac{{r_e c_e}}{{r_s/V}}={limite}\\[6px]"
            rf"\boxed{{A(t)={limite}+({coef})e^{{-{alfa}t}}}}\end{{gathered}}",
        ),
        crear_paso(
            "Chequeo simbólico con SymPy",
            "La cantidad de soluto se representa de forma simbólica antes de evaluar o calcular el límite.",
            paso_sympy("A", variable_t, expresion_sympy),
        ),
    ]

    constantes = {
        "entrada_soluto": redondear(entrada_soluto),
        "coeficiente_salida": redondear(constante_salida, DECIMALES_CONSTANTE),
        "limite": redondear(equilibrio),
        "volumen": redondear(volumen_inicial),
    }

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante",
            tipo="funcion",
            resultado=f"A(t)={limite}+({coef})e^(-{alfa}t)",
            resultado_latex=rf"A(t)={limite}+({coef})e^{{-{alfa}t}}",
            unidad="función",
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("cantidad", "valor_en_tiempo", "sal"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo)
        concentracion = valor / volumen_inicial
        pasos.append(crear_paso(
            "Cantidad solicitada",
            "Se evalúa la función A(t) en el tiempo indicado.",
            rf"\boxed{{A({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante",
            tipo="cantidad",
            resultado=redondear(valor),
            unidad="kg de soluto",
            constantes=constantes,
            pasos=pasos,
            metadatos={"concentracion": redondear(concentracion)},
        )

    if tipo_calculo in ("concentracion", "concentracion_en_tiempo"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo) / volumen_inicial
        pasos.append(crear_paso(
            "Concentración solicitada",
            "La concentración es la cantidad de soluto dividida entre el volumen.",
            rf"\boxed{{C({formatear_numero(tiempo_objetivo)})=\frac{{A({formatear_numero(tiempo_objetivo)})}}{{{v0}}}\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante",
            tipo="concentracion",
            resultado=redondear(valor),
            unidad="kg/L",
            constantes=constantes,
            pasos=pasos,
        )

    if tipo_calculo in ("limite", "equilibrio"):
        pasos.append(crear_paso(
            "Límite del modelo",
            "Cuando t crece, el término exponencial tiende a cero.",
            rf"\lim_{{t\to\infty}}A(t)=\boxed{{{limite}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_constante",
            modelo="Mezclas con volumen constante",
            tipo="limite",
            resultado=redondear(equilibrio),
            unidad="kg de soluto",
            constantes=constantes,
            pasos=pasos,
        )

    raise ErrorValidacion("Tipo de cálculo inválido para mezclas con volumen constante.")


def _resolver_volumen_variable_con_salida_fija(
    datos: dict[str, Any],
    sal_inicial: float,
    volumen_inicial: float,
    caudal_entrada: float,
    caudal_salida: float,
    concentracion_entrada: float,
    concentracion_salida: float,
) -> dict[str, Any]:
    """Resuelve volumen variable con salida de concentración fija."""
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad"))
    delta_volumen = caudal_entrada - caudal_salida
    entrada_soluto = caudal_entrada * concentracion_entrada
    salida_soluto = caudal_salida * concentracion_salida
    pendiente = entrada_soluto - salida_soluto
    variable_t = crear_variable("t")
    expresion_sympy = sal_inicial + pendiente * variable_t

    def volumen(tiempo: float) -> float:
        return volumen_inicial + delta_volumen * tiempo

    def cantidad(tiempo: float) -> float:
        volumen_actual = volumen(tiempo)
        if volumen_actual <= 0:
            raise ErrorValidacion("El tanque queda vacío antes o justo en el tiempo solicitado.")
        return evaluar(expresion_sympy, variable_t, tiempo)

    a0 = formatear_numero(sal_inicial)
    v0 = formatear_numero(volumen_inicial)
    rin = formatear_numero(caudal_entrada)
    rout = formatear_numero(caudal_salida)
    cin = formatear_numero(concentracion_entrada)
    cs = formatear_numero(concentracion_salida)
    delta = formatear_numero(delta_volumen)
    m = formatear_numero(pendiente)

    tiempo_vaciado = None
    advertencias: list[str] = []
    if delta_volumen < 0:
        tiempo_vaciado = volumen_inicial / (caudal_salida - caudal_entrada)
        advertencias.append(f"El tanque se vacía en t={formatear_numero(tiempo_vaciado)} si no se detiene el proceso.")

    pasos = [
        crear_paso(
            "Modelo diferencial con volumen variable y salida fija",
            "El volumen cambia con el tiempo y la salida de soluto se calcula con la concentración de salida ingresada.",
            r"\frac{dA}{dt}=r_ec_e-r_sc_s,\qquad V(t)=V_0+(r_e-r_s)t",
        ),
        crear_paso(
            "Sustitución de datos",
            "Se reemplazan caudales, concentraciones y volumen inicial.",
            rf"\begin{{gathered}}V(t)={v0}+({delta})t\\[6px]"
            rf"\frac{{dA}}{{dt}}={rin}({cin})-{rout}({cs})\\[6px]"
            rf"\boxed{{A(t)={a0}+({m})t}}\end{{gathered}}",
        ),
        crear_paso(
            "Concentración dentro del tanque",
            "Para concentración se divide la cantidad calculada entre el volumen actual.",
            rf"\boxed{{C(t)=\frac{{A(t)}}{{V(t)}}=\frac{{{a0}+({m})t}}{{{v0}+({delta})t}}}}",
        ),
        crear_paso(
            "Chequeo simbólico con SymPy",
            "SymPy conserva la expresión de cantidad antes de evaluar o dividir por el volumen.",
            paso_sympy("A", variable_t, expresion_sympy),
        ),
    ]

    constantes = {
        "delta_volumen": redondear(delta_volumen),
        "entrada_soluto": redondear(entrada_soluto),
        "salida_soluto": redondear(salida_soluto),
        "pendiente": redondear(pendiente),
        "concentracion_salida": redondear(concentracion_salida),
    }
    if tiempo_vaciado is not None and isfinite(tiempo_vaciado):
        constantes["tiempo_vaciado"] = redondear(tiempo_vaciado)

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable y concentración de salida fija",
            tipo="funcion",
            resultado=f"A(t)={a0}+({m})t, V(t)={v0}+({delta})t",
            resultado_latex=rf"A(t)={a0}+({m})t,\qquad V(t)={v0}+({delta})t",
            unidad="función",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    if tipo_calculo in ("cantidad", "valor_en_tiempo", "sal"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo)
        volumen_actual = volumen(tiempo_objetivo)
        tx = formatear_numero(tiempo_objetivo)
        pasos.append(crear_paso(
            "Cantidad solicitada",
            "Se evalúa A(t) y se verifica el volumen actual del tanque.",
            rf"\begin{{gathered}}V({tx})={formatear_numero(volumen_actual)}\\[6px]\boxed{{A({tx})\approx {formatear_numero(valor)}}}\end{{gathered}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable y concentración de salida fija",
            tipo="cantidad",
            resultado=redondear(valor),
            unidad="kg de soluto",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
            metadatos={"volumen_actual": redondear(volumen_actual), "concentracion": redondear(valor / volumen_actual)},
        )

    if tipo_calculo in ("concentracion", "concentracion_en_tiempo"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor_cantidad = cantidad(tiempo_objetivo)
        volumen_actual = volumen(tiempo_objetivo)
        valor = valor_cantidad / volumen_actual
        tx = formatear_numero(tiempo_objetivo)
        pasos.append(crear_paso(
            "Concentración solicitada",
            "Se divide la cantidad de soluto entre el volumen actual.",
            rf"\boxed{{C({tx})=\frac{{A({tx})}}{{V({tx})}}\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable y concentración de salida fija",
            tipo="concentracion",
            resultado=redondear(valor),
            unidad="kg/L",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    if tipo_calculo in ("limite", "equilibrio"):
        if delta_volumen > 0:
            limite_concentracion = pendiente / delta_volumen
            resultado = f"La concentración tiende a {formatear_numero(limite_concentracion)} kg/L si el proceso continúa sin restricciones físicas."
            resultado_latex = rf"\lim_{{t\to\infty}}C(t)=\frac{{r_ec_e-r_sc_s}}{{r_e-r_s}}={formatear_numero(limite_concentracion)}"
        else:
            resultado = "No existe límite infinito físico: el tanque se vacía en tiempo finito."
            resultado_latex = r"V(t)=0\quad\text{en tiempo finito}"
        pasos.append(crear_paso(
            "Comportamiento límite",
            "El límite se analiza con la relación entre la pendiente de soluto y la pendiente de volumen.",
            resultado_latex,
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable y concentración de salida fija",
            tipo="limite",
            resultado=resultado,
            resultado_latex=resultado_latex,
            unidad="comportamiento",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    raise ErrorValidacion("Tipo de cálculo inválido para mezclas con volumen variable.")


def _resolver_volumen_variable(datos: dict[str, Any]) -> dict[str, Any]:
    sal_inicial, volumen_inicial, caudal_entrada, caudal_salida, concentracion_entrada, concentracion_salida = _datos_base(datos)
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad"))
    delta_volumen = caudal_entrada - caudal_salida
    if abs(delta_volumen) < 1e-9:
        return _resolver_volumen_constante({**datos, "variante": "volumen_constante"})
    if caudal_entrada <= 0:
        raise ErrorValidacion("La variante de volumen variable requiere caudal de entrada positivo.")
    if concentracion_salida is not None:
        return _resolver_volumen_variable_con_salida_fija(
            datos,
            sal_inicial,
            volumen_inicial,
            caudal_entrada,
            caudal_salida,
            concentracion_entrada,
            concentracion_salida,
        )

    exponente = caudal_salida / delta_volumen
    coeficiente_inicial = sal_inicial - concentracion_entrada * volumen_inicial
    variable_t = crear_variable("t")
    expresion_sympy = expresion_mezcla_volumen_variable(
        sal_inicial,
        volumen_inicial,
        concentracion_entrada,
        delta_volumen,
        exponente,
        variable_t,
    )

    def volumen(tiempo: float) -> float:
        return volumen_inicial + delta_volumen * tiempo

    def cantidad(tiempo: float) -> float:
        volumen_actual = volumen(tiempo)
        if volumen_actual <= 0:
            raise ErrorValidacion("El tanque queda vacío antes o justo en el tiempo solicitado.")
        return evaluar(expresion_sympy, variable_t, tiempo)

    a0 = formatear_numero(sal_inicial)
    v0 = formatear_numero(volumen_inicial)
    rin = formatear_numero(caudal_entrada)
    rout = formatear_numero(caudal_salida)
    cin = formatear_numero(concentracion_entrada)
    delta = formatear_numero(delta_volumen)
    m = formatear_numero(exponente, DECIMALES_CONSTANTE)
    coef = formatear_numero(coeficiente_inicial)

    tiempo_vaciado = None
    advertencias: list[str] = []
    if delta_volumen < 0:
        tiempo_vaciado = volumen_inicial / (caudal_salida - caudal_entrada)
        advertencias.append(f"El tanque se vacía en t={formatear_numero(tiempo_vaciado)} si no se detiene el proceso.")

    pasos = [
        crear_paso(
            "Modelo diferencial",
            "Como los caudales no son iguales, el volumen cambia con el tiempo.",
            r"\frac{dA}{dt}=r_e c_e-r_s\frac{A}{V(t)},\qquad V(t)=V_0+(r_e-r_s)t",
        ),
        crear_paso(
            "Sustitución del volumen variable",
            "Se reemplazan los datos de entrada del tanque.",
            rf"\begin{{gathered}}V(t)={v0}+({delta})t\\[6px]"
            rf"\frac{{dA}}{{dt}}={rin}({cin})-{rout}\frac{{A}}{{{v0}+({delta})t}}\end{{gathered}}",
        ),
        crear_paso(
            "Solución del modelo lineal",
            "Usando el factor integrante del volumen variable, se obtiene una expresión cerrada para A(t).",
            rf"\boxed{{A(t)={cin}V(t)+({a0}-{cin}\cdot {v0})\left(\frac{{{v0}}}{{V(t)}}\right)^{{{m}}}}}",
        ),
        crear_paso(
            "Chequeo simbólico con SymPy",
            "SymPy mantiene la expresión con V(t) variable antes de evaluar la cantidad o concentración.",
            paso_sympy("A", variable_t, expresion_sympy),
        ),
    ]

    constantes = {
        "delta_volumen": redondear(delta_volumen),
        "exponente": redondear(exponente, DECIMALES_CONSTANTE),
        "coeficiente_inicial": redondear(coeficiente_inicial),
    }
    if tiempo_vaciado is not None and isfinite(tiempo_vaciado):
        constantes["tiempo_vaciado"] = redondear(tiempo_vaciado)

    if tipo_calculo in ("funcion", "solucion", "solucion_particular"):
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable",
            tipo="funcion",
            resultado=f"A(t)={cin}V(t)+({coef})({v0}/V(t))^{m}, V(t)={v0}+({delta})t",
            resultado_latex=rf"A(t)={cin}V(t)+({coef})\left(\frac{{{v0}}}{{V(t)}}\right)^{{{m}}},\quad V(t)={v0}+({delta})t",
            unidad="función",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    if tipo_calculo in ("cantidad", "valor_en_tiempo", "sal"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        valor = cantidad(tiempo_objetivo)
        volumen_actual = volumen(tiempo_objetivo)
        pasos.append(crear_paso(
            "Cantidad solicitada",
            "Se evalúa la solución con el volumen correspondiente al tiempo indicado.",
            rf"\begin{{gathered}}V({formatear_numero(tiempo_objetivo)})={formatear_numero(volumen_actual)}\\[6px]"
            rf"\boxed{{A({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}\end{{gathered}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable",
            tipo="cantidad",
            resultado=redondear(valor),
            unidad="kg de soluto",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
            metadatos={"volumen_actual": redondear(volumen_actual), "concentracion": redondear(valor / volumen_actual)},
        )

    if tipo_calculo in ("concentracion", "concentracion_en_tiempo"):
        tiempo_objetivo = validar_no_negativo(obtener_valor(datos, ("tiempo_objetivo", "tiempo"), "tiempo objetivo"), "Tiempo objetivo")
        volumen_actual = volumen(tiempo_objetivo)
        valor = cantidad(tiempo_objetivo) / volumen_actual
        pasos.append(crear_paso(
            "Concentración solicitada",
            "Se calcula C(t)=A(t)/V(t).",
            rf"\boxed{{C({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable",
            tipo="concentracion",
            resultado=redondear(valor),
            unidad="kg/L",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    if tipo_calculo in ("limite", "equilibrio"):
        if delta_volumen > 0:
            resultado = f"La concentración tiende a {formatear_numero(concentracion_entrada)} kg/L y la cantidad crece sin cota porque el volumen aumenta."
            resultado_latex = rf"\lim_{{t\to\infty}}C(t)={formatear_numero(concentracion_entrada)}"
        else:
            resultado = "No existe límite infinito físico: el tanque se vacía en tiempo finito."
            resultado_latex = r"V(t)=0\quad\text{en tiempo finito}"
        pasos.append(crear_paso(
            "Comportamiento límite",
            "En volumen variable el límite depende de si el tanque se llena o se vacía.",
            rf"V(t)={v0}+({delta})t",
        ))
        return crear_respuesta_modelo(
            modulo=MODULO,
            variante="volumen_variable",
            modelo="Mezclas con volumen variable",
            tipo="limite",
            resultado=resultado,
            resultado_latex=resultado_latex,
            unidad="comportamiento",
            constantes=constantes,
            pasos=pasos,
            advertencias=advertencias,
        )

    raise ErrorValidacion("Tipo de cálculo inválido para mezclas con volumen variable.")


def resolver_mezclas(datos: dict[str, Any]) -> dict[str, Any]:
    """Método único del módulo mezclas que evalúa sus variantes internas."""
    try:
        variante = normalizar_texto(datos.get("variante", "volumen_constante"))
        tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad"))
        if tipo_calculo in ("formula_simbolica", "formula_general", "planteamiento"):
            return formula_mezclas({**datos, "variante": variante})
        if variante in ("volumen_constante", "tanque_constante", "mezcla_constante"):
            return _resolver_volumen_constante(datos)
        if variante in ("volumen_variable", "tanque_variable", "mezcla_variable"):
            return _resolver_volumen_variable(datos)
        raise ErrorValidacion(f"Variante no soportada en mezclas: {variante}.")
    except (ErrorValidacion, ValueError, ZeroDivisionError) as error:
        return crear_respuesta_error(str(error))
