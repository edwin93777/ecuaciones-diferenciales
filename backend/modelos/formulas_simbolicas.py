"""Fórmulas simbólicas para casos con datos incompletos.

Cuando el estudiante no recibe todos los datos numéricos, el sistema no debe
inventar constantes ni detenerse de forma brusca. Este módulo usa SymPy para
construir el planteamiento algebraico que resolvería el ítem, conservando
variables indeterminadas como k, C, R, t, P0, Ta o RC.
"""
from __future__ import annotations

from typing import Any

import sympy as sp

from backend.utils.formato import crear_paso, crear_respuesta_modelo, formatear_numero
from backend.utils.validacion import normalizar_texto

MODULO_FORMULA = "formula_simbolica"


def _tiene_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _numero_o_simbolo(datos: dict[str, Any], campos: tuple[str, ...], simbolo: str) -> sp.Expr:
    for campo in campos:
        valor = datos.get(campo)
        if valor not in (None, ""):
            try:
                return sp.Float(float(str(valor).replace(",", ".")), 12)
            except (TypeError, ValueError):
                return sp.Symbol(simbolo, real=True)
    return sp.Symbol(simbolo, real=True)


def _simbolo_tiempo(datos: dict[str, Any], campos: tuple[str, ...] = ("tiempo_objetivo", "tiempo", "distancia_objetivo"), simbolo: str = "t") -> sp.Expr:
    return _numero_o_simbolo(datos, campos, simbolo)


def _latex_igualdad(nombre: str, variable: sp.Symbol | sp.Expr, expresion: sp.Expr) -> str:
    return rf"{nombre}({sp.latex(variable)})={sp.latex(expresion)}"


def _respuesta_formula(
    *,
    modulo: str,
    variante: str,
    modelo: str,
    resultado: str,
    pasos: list[dict[str, str]],
    resultado_latex: str | None = None,
) -> dict[str, Any]:
    return crear_respuesta_modelo(
        modulo=modulo,
        variante=variante,
        modelo=modelo,
        tipo=MODULO_FORMULA,
        resultado=resultado,
        resultado_latex=resultado_latex,
        unidad="fórmula simbólica",
        constantes={},
        pasos=pasos,
        advertencias=[
            "Modo simbólico: se conservan variables indeterminadas porque no se entregaron todos los datos numéricos.",
            "El sistema muestra la fórmula correcta antes de sustituir valores. Matemáticas con casco, no con chanclas.",
        ],
        metadatos={"uso": "planteamiento_con_datos_incompletos"},
    )


def formula_crecimiento(datos: dict[str, Any]) -> dict[str, Any]:
    variante = normalizar_texto(datos.get("variante", "crecimiento_proporcional"))
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "formula_simbolica"))
    t = sp.Symbol("t", real=True)
    tx = _simbolo_tiempo(datos, simbolo="t_x")
    k = _numero_o_simbolo(datos, ("constante_k", "k"), "k")

    if variante in ("entrada_constante", "crecimiento_entrada_constante", "lineal_entrada"):
        p0 = _numero_o_simbolo(datos, ("cantidad_inicial", "poblacion_inicial"), "P_0")
        b = _numero_o_simbolo(datos, ("entrada_constante", "b"), "b")
        expresion = (p0 + b / k) * sp.exp(k * t) - b / k
        expresion_objetivo = expresion.subs(t, tx)
        pasos = [
            crear_paso("Identificación del modelo", "Existe crecimiento proporcional más una entrada externa constante.", r"\frac{dP}{dt}=kP+b"),
            crear_paso("Solución simbólica general", "Se resuelve como EDO lineal de primer orden; si k o b no aparecen en el enunciado, quedan como parámetros.", r"\begin{gathered}\frac{dP}{dt}-kP=b\\[4px]P(t)=Ce^{kt}-\frac{b}{k}\end{gathered}"),
            crear_paso("Aplicación de condición inicial", "Con P(0)=P_0, la constante C se conserva simbólica si P_0, b o k no tienen valor numérico.", rf"\begin{{gathered}}P_0=C-\frac{{b}}{{k}}\\[4px]C=P_0+\frac{{b}}{{k}}\\[4px]\boxed{{{_latex_igualdad('P', t, expresion)}}}\end{{gathered}}"),
            crear_paso("Ítem particular", "Si el ejercicio pide la población en un tiempo concreto, se reemplaza solo ese tiempo y los demás parámetros quedan vivos.", rf"\boxed{{{_latex_igualdad('P', tx, expresion_objetivo)}}}"),
        ]
        return _respuesta_formula(
            modulo="crecimiento",
            variante="entrada_constante",
            modelo="Crecimiento con entrada constante con parámetros indeterminados",
            resultado=f"P({sp.latex(tx)})={sp.latex(expresion_objetivo)}" if tipo_calculo in ("valor_en_tiempo", "cantidad", "poblacion") else "P(t)=(P0+b/k)e^(kt)-b/k",
            resultado_latex=_latex_igualdad("P", tx if tipo_calculo in ("valor_en_tiempo", "cantidad", "poblacion") else t, expresion_objetivo if tipo_calculo in ("valor_en_tiempo", "cantidad", "poblacion") else expresion),
            pasos=pasos,
        )

    if variante in ("caida_resistencia", "velocidad_limite"):
        v0 = _numero_o_simbolo(datos, ("velocidad_inicial", "cantidad_inicial"), "v_0")
        g = _numero_o_simbolo(datos, ("gravedad", "g"), "g")
        expresion = g / k + (v0 - g / k) * sp.exp(-k * t)
        expresion_objetivo = expresion.subs(t, tx)
        velocidad_limite = g / k
        pasos = [
            crear_paso("Identificación del modelo", "La gravedad actúa como entrada constante y la resistencia resta velocidad proporcionalmente.", r"\frac{dv}{dt}=g-kv"),
            crear_paso("Solución simbólica", "Aunque no se conozca k, la fórmula queda planteada y lista para sustituir datos cuando aparezcan.", r"\begin{gathered}\frac{dv}{dt}+kv=g\\[4px]v(t)=\frac{g}{k}+Ce^{-kt}\end{gathered}"),
            crear_paso("Condición inicial", "Con v(0)=v_0 se obtiene la constante de integración sin necesidad de valor numérico.", rf"\begin{{gathered}}v_0=\frac{{g}}{{k}}+C\\[4px]C=v_0-\frac{{g}}{{k}}\\[4px]\boxed{{{_latex_igualdad('v', t, expresion)}}}\end{{gathered}}"),
            crear_paso("Velocidad límite", "Si el ítem solo pide la velocidad límite, no se necesita tiempo ni velocidad inicial.", rf"\boxed{{v_\infty=\lim_{{t\to\infty}}v(t)={sp.latex(velocidad_limite)}}}"),
            crear_paso("Ítem particular", "Si se entrega un tiempo pero falta k, queda una velocidad simbólica evaluada en ese tiempo.", rf"\boxed{{{_latex_igualdad('v', tx, expresion_objetivo)}}}"),
        ]
        es_limite = tipo_calculo in ("velocidad_limite", "limite", "equilibrio")
        return _respuesta_formula(
            modulo="crecimiento",
            variante="caida_resistencia",
            modelo="Caída con resistencia del aire con parámetros indeterminados",
            resultado=f"v∞={sp.latex(velocidad_limite)}" if es_limite else f"v({sp.latex(tx)})={sp.latex(expresion_objetivo)}",
            resultado_latex=rf"v_\infty={sp.latex(velocidad_limite)}" if es_limite else _latex_igualdad("v", tx, expresion_objetivo),
            pasos=pasos,
        )

    if variante in ("interes_continuo", "interes_compuesto_continuo"):
        s0 = _numero_o_simbolo(datos, ("capital_inicial", "cantidad_inicial"), "S_0")
        # Si llega tasa_porcentual, se conserva como r simbólica en el documento; el cálculo numérico lo hace el módulo principal.
        r = _numero_o_simbolo(datos, ("constante_k", "k", "tasa", "tasa_porcentual"), "r")
        expresion = s0 * sp.exp(r * t)
        expresion_objetivo = expresion.subs(t, tx)
        pasos = [
            crear_paso("Modelo", "El capital crece proporcionalmente al capital presente.", r"\frac{dS}{dt}=rS"),
            crear_paso("Separación e integración", "Se integra sin obligar a conocer numéricamente la tasa.", r"\begin{gathered}\frac{dS}{S}=r\,dt\\[4px]\ln|S|=rt+C_1\end{gathered}"),
            crear_paso("Fórmula simbólica", "Con S(0)=S_0 queda el modelo continuo.", rf"\boxed{{{_latex_igualdad('S', t, expresion)}}}"),
            crear_paso("Ítem particular", "Si el enunciado da una tasa en porcentaje, se usa r=i/100 antes de evaluar.", rf"\boxed{{{_latex_igualdad('S', tx, expresion_objetivo)}}}"),
        ]
        return _respuesta_formula(modulo="crecimiento", variante="interes_continuo", modelo="Interés continuo simbólico", resultado=f"S({sp.latex(tx)})={sp.latex(expresion_objetivo)}", resultado_latex=_latex_igualdad("S", tx, expresion_objetivo), pasos=pasos)

    p0 = _numero_o_simbolo(datos, ("cantidad_inicial", "poblacion_inicial"), "P_0")
    expresion = p0 * sp.exp(k * t)
    expresion_objetivo = expresion.subs(t, tx)
    pasos = [
        crear_paso("Modelo proporcional", "La razón de cambio es proporcional a la cantidad actual.", r"\frac{dP}{dt}=kP"),
        crear_paso("Integración manual resumida", "Se separan variables y se integra.", r"\begin{gathered}\frac{dP}{P}=k\,dt\\[4px]\ln|P|=kt+C_1\\[4px]P(t)=Ce^{kt}\end{gathered}"),
        crear_paso("Condición inicial simbólica", "Con P(0)=P_0, la constante C se mantiene como P_0 si no hay dato numérico.", rf"\boxed{{{_latex_igualdad('P', t, expresion)}}}"),
        crear_paso("Fórmula para encontrar k", "Si luego aparece una medición P(t_1)=P_1, se despeja k.", r"\boxed{k=\frac{\ln(P_1/P_0)}{t_1}}"),
        crear_paso("Ítem particular", "Si solo se pide un tiempo objetivo, se sustituye ese tiempo y k puede quedar indeterminada.", rf"\boxed{{{_latex_igualdad('P', tx, expresion_objetivo)}}}"),
    ]
    return _respuesta_formula(modulo="crecimiento", variante="crecimiento_proporcional", modelo="Crecimiento proporcional simbólico", resultado=f"P({sp.latex(tx)})={sp.latex(expresion_objetivo)}", resultado_latex=_latex_igualdad("P", tx, expresion_objetivo), pasos=pasos)


def formula_decaimiento(datos: dict[str, Any]) -> dict[str, Any]:
    variante = normalizar_texto(datos.get("variante", "decaimiento_radiactivo"))
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "formula_simbolica"))
    t = sp.Symbol("x", real=True) if variante == "intensidad_luz" else sp.Symbol("t", real=True)
    tx = _simbolo_tiempo(datos, ("distancia_objetivo", "tiempo_objetivo", "tiempo"), "x_f" if variante == "intensidad_luz" else "t_f")

    if variante in ("descarga_capacitor", "capacitor", "descarga"):
        q0 = _numero_o_simbolo(datos, ("cantidad_inicial", "carga_inicial"), "q_0")
        qf = _numero_o_simbolo(datos, ("cantidad_objetivo", "carga_objetivo"), "q_f")
        if _tiene_valor(datos, "constante_k", "k"):
            k = _numero_o_simbolo(datos, ("constante_k", "k"), "k")
            expresion = q0 * sp.exp(-k * t)
            expresion_objetivo = expresion.subs(t, tx)
            tiempo_objetivo = sp.log(q0 / qf) / k
            constante = r"k"
            modelo_latex = r"\frac{dq}{dt}=-kq"
            resultado_texto = f"q({sp.latex(tx)})={sp.latex(expresion_objetivo)}" if tipo_calculo not in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad") else f"t={sp.latex(tiempo_objetivo)}"
            resultado_latex = _latex_igualdad("q", tx, expresion_objetivo) if tipo_calculo not in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad") else rf"t={sp.latex(tiempo_objetivo)}"
        else:
            hay_resistencia = _tiene_valor(datos, "resistencia", "R")
            hay_capacitancia = _tiene_valor(datos, "capacitancia", "C")
            if hay_resistencia and hay_capacitancia:
                resistencia = _numero_o_simbolo(datos, ("resistencia", "R"), "R")
                capacitancia = _numero_o_simbolo(datos, ("capacitancia", "C"), "C")
                producto_rc = resistencia * capacitancia
            else:
                # Se usa un único símbolo RC para respetar la notación estándar del circuito.
                # Esto evita que SymPy reordene R*C como C R en la salida LaTeX.
                producto_rc = sp.Symbol("RC", real=True)
            expresion = q0 * sp.exp(-t / producto_rc)
            expresion_objetivo = expresion.subs(t, tx)
            tiempo_objetivo = producto_rc * sp.log(q0 / qf)
            constante = r"\frac{1}{RC}"
            modelo_latex = r"\frac{dq}{dt}=-\frac{1}{RC}q"
            if tipo_calculo not in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad"):
                resultado_texto = f"q({sp.latex(tx)})={sp.latex(q0)}e^(-{sp.latex(tx)}/(RC))"
                resultado_latex = _latex_igualdad("q", tx, expresion_objetivo)
            else:
                resultado_texto = f"t=RC ln({sp.latex(q0)}/{sp.latex(qf)})"
                resultado_latex = rf"t={sp.latex(tiempo_objetivo)}"
        pasos = [
            crear_paso("Modelo de descarga", "El enunciado puede dar solo la ecuación y una condición inicial; RC puede quedar indeterminado.", modelo_latex),
            crear_paso("Solución general", "La constante de decaimiento puede escribirse como k o como 1/(RC).", rf"q(t)=Ce^{{-({constante})t}}"),
            crear_paso("Condición inicial", "Con q(0)=q_0 se reemplaza la constante de integración.", rf"\boxed{{{_latex_igualdad('q', t, expresion)}}}"),
            crear_paso("Evaluación simbólica", "Aunque no se conozca R, C o k, el tiempo solicitado sí puede sustituirse.", rf"\boxed{{{_latex_igualdad('q', tx, expresion_objetivo)}}}"),
            crear_paso("Tiempo para una carga objetivo", "Si el ítem pide cuándo q(t)=q_f, se despeja t sin inventar RC.", rf"\boxed{{t={sp.latex(tiempo_objetivo)}}}"),
        ]
        return _respuesta_formula(modulo="decaimiento", variante="descarga_capacitor", modelo="Descarga de capacitor con RC indeterminado", resultado=resultado_texto, resultado_latex=resultado_latex, pasos=pasos)

    simbolo = "I" if variante == "intensidad_luz" else ("C" if variante == "absorcion_medicamento" else "A")
    y0 = _numero_o_simbolo(datos, ("cantidad_inicial", "intensidad_inicial"), f"{simbolo}_0")
    yf = _numero_o_simbolo(datos, ("cantidad_objetivo", "intensidad_objetivo"), f"{simbolo}_f")
    k = _numero_o_simbolo(datos, ("constante_k", "k"), "k")
    expresion = y0 * sp.exp(-k * t)
    expresion_objetivo = expresion.subs(t, tx)
    tiempo_objetivo = sp.log(y0 / yf) / k
    vida_media = sp.log(2) / k
    pasos = [
        crear_paso("Modelo de decaimiento", "La cantidad disminuye proporcionalmente a la cantidad presente.", rf"\frac{{d{simbolo}}}{{dt}}=-k{simbolo}"),
        crear_paso("Solución general", "Se separan variables y se integra, dejando k indeterminada si no se conoce.", rf"\begin{{gathered}}\frac{{d{simbolo}}}{{{simbolo}}}=-k\,dt\\[4px]\ln|{simbolo}|=-kt+C_1\\[4px]{simbolo}(t)=Ce^{{-kt}}\end{{gathered}}"),
        crear_paso("Condición inicial", "Con el dato inicial se obtiene la forma particular simbólica.", rf"\boxed{{{_latex_igualdad(simbolo, t, expresion)}}}"),
        crear_paso("Evaluación simbólica", "Si se da un tiempo o distancia objetivo, se reemplaza ese valor aunque k quede indeterminada.", rf"\boxed{{{_latex_igualdad(simbolo, tx, expresion_objetivo)}}}"),
        crear_paso("Fórmulas útiles", "Sirven cuando el ítem pide vida media o tiempo para una cantidad objetivo sin resolver todo numéricamente.", rf"\boxed{{t_{{1/2}}={sp.latex(vida_media)}}}\qquad \boxed{{t={sp.latex(tiempo_objetivo)}}}"),
    ]
    if tipo_calculo in ("vida_media", "semivida"):
        resultado = f"t1/2={sp.latex(vida_media)}"
        resultado_latex = rf"t_{{1/2}}={sp.latex(vida_media)}"
    elif tipo_calculo in ("tiempo_objetivo", "tiempo", "tiempo_para_cantidad"):
        resultado = f"t={sp.latex(tiempo_objetivo)}"
        resultado_latex = rf"t={sp.latex(tiempo_objetivo)}"
    else:
        resultado = f"{simbolo}({sp.latex(tx)})={sp.latex(expresion_objetivo)}"
        resultado_latex = _latex_igualdad(simbolo, tx, expresion_objetivo)
    return _respuesta_formula(modulo="decaimiento", variante=variante or "decaimiento_radiactivo", modelo="Decaimiento simbólico", resultado=resultado, resultado_latex=resultado_latex, pasos=pasos)


def formula_enfriamiento(datos: dict[str, Any]) -> dict[str, Any]:
    tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "formula_simbolica"))
    t = sp.Symbol("t", real=True)
    tx = _simbolo_tiempo(datos, ("tiempo_objetivo", "tiempo"), "t_x")
    temperatura_ambiente = _numero_o_simbolo(datos, ("temperatura_ambiente", "Ta"), "T_a")
    temperatura_inicial = _numero_o_simbolo(datos, ("temperatura_inicial", "T0"), "T_0")
    temperatura_objetivo = _numero_o_simbolo(datos, ("temperatura_objetivo", "T_objetivo"), "T_f")
    k = _numero_o_simbolo(datos, ("constante_k", "k"), "k")
    expresion = temperatura_ambiente + (temperatura_inicial - temperatura_ambiente) * sp.exp(-k * t)
    expresion_objetivo = expresion.subs(t, tx)
    tiempo_para_temperatura = -sp.log((temperatura_objetivo - temperatura_ambiente) / (temperatura_inicial - temperatura_ambiente)) / k
    pasos = [
        crear_paso("Modelo de Newton", "El cambio térmico depende de la diferencia entre objeto y ambiente.", r"\frac{dT}{dt}=-k(T-T_a)"),
        crear_paso("Cambio de variable", "Se define U=T-T_a para convertirlo en un decaimiento exponencial.", r"\begin{gathered}U=T-T_a\\[4px]\frac{dU}{dt}=-kU\\[4px]U(t)=Ce^{-kt}\end{gathered}"),
        crear_paso("Fórmula simbólica", "Con T(0)=T_0 queda planteada la ley de Newton.", rf"\boxed{{{_latex_igualdad('T', t, expresion)}}}"),
        crear_paso("Evaluación simbólica", "Si existe un tiempo objetivo, se sustituye sin exigir que k sea numérica.", rf"\boxed{{{_latex_igualdad('T', tx, expresion_objetivo)}}}"),
        crear_paso("Fórmula para encontrar k", "Si luego se conoce T(t_1)=T_1, se despeja la constante sin cambiar el modelo.", r"\boxed{k=-\frac{1}{t_1}\ln\left(\frac{T_1-T_a}{T_0-T_a}\right)}"),
        crear_paso("Tiempo para temperatura objetivo", "Si piden cuándo se llega a una temperatura, se despeja t simbólicamente.", rf"\boxed{{t={sp.latex(tiempo_para_temperatura)}}}"),
    ]
    if tipo_calculo in ("tiempo_objetivo", "tiempo", "tiempo_para_temperatura"):
        resultado = f"t={sp.latex(tiempo_para_temperatura)}"
        resultado_latex = rf"t={sp.latex(tiempo_para_temperatura)}"
    elif tipo_calculo in ("equilibrio", "limite"):
        resultado = f"lim T(t)={sp.latex(temperatura_ambiente)}"
        resultado_latex = rf"\lim_{{t\to\infty}}T(t)={sp.latex(temperatura_ambiente)}"
    else:
        resultado = f"T({sp.latex(tx)})={sp.latex(expresion_objetivo)}"
        resultado_latex = _latex_igualdad("T", tx, expresion_objetivo)
    return _respuesta_formula(modulo="enfriamiento", variante="newton_constante", modelo="Ley de Newton simbólica", resultado=resultado, resultado_latex=resultado_latex, pasos=pasos)


def formula_mezclas(datos: dict[str, Any]) -> dict[str, Any]:
    variante = normalizar_texto(datos.get("variante", "volumen_constante"))
    t = sp.Symbol("t", real=True)
    a0, v0, re, rs, ce, cs = sp.symbols("A_0 V_0 r_e r_s c_e c_s", positive=True)
    usa_salida_fija = _tiene_valor(datos, "concentracion_salida", "c_salida", "cs", "c_out")

    if variante in ("volumen_variable", "tanque_variable", "mezcla_variable"):
        volumen = v0 + (re - rs) * t
        if usa_salida_fija:
            expresion = a0 + (re * ce - rs * cs) * t
            concentracion = expresion / volumen
            pasos = [
                crear_paso("Modelo de mezcla", "El volumen cambia y se ingresó una concentración de salida fija.", r"\frac{dA}{dt}=r_ec_e-r_sc_s,\qquad V(t)=V_0+(r_e-r_s)t"),
                crear_paso("Integración simbólica", "Como entrada y salida de soluto son constantes, A(t) queda lineal.", rf"\boxed{{{_latex_igualdad('A', t, expresion)}}}"),
                crear_paso("Concentración", "La concentración del tanque se calcula dividiendo la cantidad entre el volumen actual.", rf"\boxed{{C(t)={sp.latex(concentracion)}}}"),
            ]
            return _respuesta_formula(
                modulo="mezclas",
                variante="volumen_variable",
                modelo="Mezcla con volumen variable y concentración de salida fija simbólica",
                resultado="A(t)=A0+(re·ce-rs·cs)t",
                resultado_latex=_latex_igualdad("A", t, expresion),
                pasos=pasos,
            )

        expresion = ce * volumen + (a0 - ce * v0) * (v0 / volumen) ** (rs / (re - rs))
        pasos = [
            crear_paso("Modelo de mezcla", "El volumen cambia porque los caudales de entrada y salida no son iguales.", r"\frac{dA}{dt}=r_ec_e-r_s\frac{A}{V(t)},\qquad V(t)=V_0+(r_e-r_s)t"),
            crear_paso("Solución simbólica", "El factor integrante genera una fórmula cerrada para A(t).", rf"\boxed{{{_latex_igualdad('A', t, expresion)}}}"),
            crear_paso("Concentración", "Si el ítem pide concentración, se divide la cantidad de soluto entre el volumen.", r"\boxed{C(t)=\frac{A(t)}{V(t)}}"),
        ]
        return _respuesta_formula(modulo="mezclas", variante="volumen_variable", modelo="Mezcla con volumen variable simbólica", resultado="A(t)=ceV(t)+(A0-ceV0)(V0/V(t))^(rs/(re-rs))", resultado_latex=_latex_igualdad("A", t, expresion), pasos=pasos)

    v, r = sp.symbols("V r", positive=True)
    if usa_salida_fija:
        expresion = a0 + (r * ce - r * cs) * t
        pasos = [
            crear_paso("Modelo de mezcla", "En volumen constante con concentración de salida fija se evalúa entrada menos salida constante.", r"\frac{dA}{dt}=rc_e-rc_s"),
            crear_paso("Integración simbólica", "La cantidad cambia linealmente porque la diferencia de soluto por minuto es constante.", rf"\boxed{{{_latex_igualdad('A', t, expresion)}}}"),
            crear_paso("Concentración", "Si el ítem pide concentración, se divide entre el volumen constante.", r"\boxed{C(t)=\frac{A(t)}{V}}"),
        ]
        return _respuesta_formula(
            modulo="mezclas",
            variante="volumen_constante",
            modelo="Mezcla con volumen constante y concentración de salida fija simbólica",
            resultado="A(t)=A0+r(ce-cs)t",
            resultado_latex=_latex_igualdad("A", t, expresion),
            pasos=pasos,
        )

    equilibrio = v * ce
    expresion = equilibrio + (a0 - equilibrio) * sp.exp(-(r / v) * t)
    pasos = [
        crear_paso("Modelo de mezcla", "En volumen constante se cumple r_e=r_s=r y el volumen no cambia.", r"\frac{dA}{dt}=rc_e-r\frac{A}{V}"),
        crear_paso("Equilibrio", "El equilibrio ocurre cuando entrada y salida de soluto se compensan.", r"0=rc_e-r\frac{A_{\infty}}{V}\quad\Rightarrow\quad A_{\infty}=Vc_e"),
        crear_paso("Fórmula simbólica", "La solución se expresa alrededor del equilibrio.", rf"\boxed{{{_latex_igualdad('A', t, expresion)}}}"),
        crear_paso("Límite", "Si el ítem pide el límite, no hace falta evaluar tiempos.", r"\boxed{\lim_{t\to\infty}A(t)=Vc_e}"),
    ]
    return _respuesta_formula(modulo="mezclas", variante="volumen_constante", modelo="Mezcla con volumen constante simbólica", resultado="A(t)=Vce+(A0-Vce)e^(-(r/V)t)", resultado_latex=_latex_igualdad("A", t, expresion), pasos=pasos)
