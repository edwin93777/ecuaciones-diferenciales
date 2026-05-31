"""Modelo especializado de datación por Carbono-14.

El módulo formaliza la información del parcial mostrado en la imagen:

* la cantidad de carbono-14 disminuye con rapidez proporcional a la cantidad
  presente;
* la vida media es de 5730 años;
* después de una vida media queda la mitad de la cantidad inicial.

La implementación usa SymPy para construir expresiones, despejar constantes,
generar LaTeX y evaluar resultados numéricos solo cuando los datos son
suficientes.
"""
from __future__ import annotations

from typing import Any

import sympy as sp

from backend.utils.formato import (
    DECIMALES_CONSTANTE,
    crear_paso,
    crear_respuesta_modelo,
    formatear_numero,
    redondear,
)
from backend.utils.simbolico import (
    constante_decaimiento_por_vida_media,
    crear_variable,
    decimal,
    evaluar,
    expresion_carbono14,
    expresion_porcentaje_carbono14,
    igualdad_funcion,
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

MODULO = "carbono14"
VARIANTE = "vida_media_5730"
VIDA_MEDIA_CARBONO_14 = 5730.0

TIPOS_FORMULA = {"formula_simbolica", "formula_general", "planteamiento"}
TIPOS_FUNCION = {"funcion", "solucion", "solucion_particular", "modelo"}
TIPOS_CANTIDAD = {"cantidad_en_tiempo", "valor_en_tiempo", "cantidad"}
TIPOS_PORCENTAJE = {"porcentaje_en_tiempo", "porcentaje"}
TIPOS_EDAD_POR_PORCENTAJE = {"edad_por_porcentaje", "tiempo_por_porcentaje"}
TIPOS_EDAD_POR_CANTIDAD = {"edad_por_cantidad", "tiempo_por_cantidad", "tiempo_objetivo"}
TIPOS_VIDA_MEDIA = {"vida_media", "semivida", "constante"}


def _hay_valor(datos: dict[str, Any], *campos: str) -> bool:
    return any(datos.get(campo) not in (None, "") for campo in campos)


def _obtener_vida_media(datos: dict[str, Any]) -> float:
    """Obtiene la vida media del enunciado o usa 5730 años por defecto."""
    if _hay_valor(datos, "vida_media", "semivida"):
        return validar_positivo(obtener_valor(datos, ("vida_media", "semivida"), "vida media"), "Vida media")
    return VIDA_MEDIA_CARBONO_14


def _crear_pasos_base(vida_media: float, cantidad_inicial: float | None = None) -> list[dict[str, str]]:
    vida = formatear_numero(vida_media)
    simbolo_inicial = formatear_numero(cantidad_inicial) if cantidad_inicial is not None else "M_0"
    constante_k = constante_decaimiento_por_vida_media(vida_media)
    constante_k_latex = sp.latex(constante_k)
    return [
        crear_paso(
            "Modelo diferencial del Carbono-14",
            "La cantidad de Carbono-14 no disminuye por una resta fija, sino en proporción a lo que todavía queda. Por eso se escribe una derivada negativa: mientras mayor sea M(t), mayor será la rapidez de desintegración; cuando M(t) baja, la rapidez también baja.",
            r"\frac{dM}{dt}=-kM,\qquad k>0",
        ),
        crear_paso(
            "Separación de variables",
            "Se colocan los términos que dependen de M en un lado y los términos que dependen del tiempo en el otro. Esta separación convierte la ecuación diferencial en dos integrales directas y permite pasar del cambio instantáneo a una función explícita.",
            r"\frac{dM}{M}=-k\,dt\;\Longrightarrow\;\int\frac{dM}{M}=\int-k\,dt\;\Longrightarrow\;\ln|M|=-kt+C_1",
        ),
        crear_paso(
            "Solución general",
            "Después de integrar aparece ln|M|. Al aplicar exponencial, la constante de integración se transforma en una constante multiplicativa C; por eso la solución toma forma exponencial decreciente.",
            r"M(t)=Ce^{-kt}",
        ),
        crear_paso(
            "Condición inicial",
            "La condición inicial significa que al comienzo del proceso todavía está la cantidad original. Al reemplazar t=0, la exponencial vale 1 y se concluye que C es exactamente M0.",
            rf"M(0)=M_0\Rightarrow C=M_0\Rightarrow M(t)={simbolo_inicial}e^{{-kt}}",
        ),
        crear_paso(
            "Uso de la vida media de 5730 años",
            "La vida media entregada en el parcial funciona como una medición de referencia: al sustituir t=5730, el modelo debe devolver M0/2. Esa igualdad permite cancelar M0, aplicar logaritmo natural y despejar la constante k sin asumirla manualmente.",
            rf"\begin{{gathered}}M({vida})=\frac{{M_0}}{{2}}\\[4px]\frac{{M_0}}{{2}}=M_0e^{{-k({vida})}}\\[4px]\frac12=e^{{-k({vida})}}\\[4px]\ln\left(\frac12\right)=-k({vida})\\[4px]\boxed{{k=\frac{{\ln 2}}{{{vida}}}\approx {formatear_numero(float(sp.N(constante_k)), DECIMALES_CONSTANTE)}}}\end{{gathered}}",
        ),
        crear_paso(
            "Función del Carbono-14",
            "Con k ya calculada desde la vida media, se reemplaza en la solución particular. El resultado final puede escribirse como exponencial natural o como potencia de 1/2; ambas formas representan el mismo decaimiento.",
            rf"\boxed{{M(t)=M_0e^{{-\left({constante_k_latex}\right)t}}=M_0\left(\frac12\right)^{{t/{vida}}}}}",
        ),
    ]


def _respuesta_formula_simbolica(vida_media: float) -> dict[str, Any]:
    variable_t = crear_variable("t")
    cantidad_inicial = sp.Symbol("M_0", positive=True)
    constante_k = constante_decaimiento_por_vida_media(vida_media)
    expresion = cantidad_inicial * sp.exp(-constante_k * variable_t)
    pasos = _crear_pasos_base(vida_media)
    pasos.append(
        crear_paso(
            "Salida simbólica generada con SymPy",
            "SymPy mantiene M0 y t como símbolos cuando el usuario solo solicita el planteamiento. Así el sistema muestra una fórmula académica completa, evita inventar cantidades y deja la expresión lista para sustituir valores después.",
            rf"\boxed{{{igualdad_funcion('M', variable_t, expresion)}}}",
        )
    )
    return crear_respuesta_modelo(
        modulo=MODULO,
        variante=VARIANTE,
        modelo="Modelo del Carbono-14 con vida media de 5730 años",
        tipo="formula_simbolica",
        resultado=f"M(t)={sp.latex(expresion)}",
        resultado_latex=igualdad_funcion("M", variable_t, expresion),
        unidad="fórmula simbólica",
        constantes={"vida_media": vida_media, "k": redondear(float(sp.N(constante_k)), DECIMALES_CONSTANTE)},
        pasos=pasos,
        advertencias=[
            "Modo simbólico: M0 y t se conservan como variables porque el cálculo solicitado no exige datos numéricos.",
            "La vida media base del Carbono-14 usada por defecto es 5730 años.",
        ],
        metadatos={"fuente_modelo": "imagen_parcial_carbono_14", "variable_independiente": "tiempo_en_años"},
    )


def resolver_carbono14(datos: dict[str, Any]) -> dict[str, Any]:
    """Resuelve datación por Carbono-14 con vida media y SymPy."""
    try:
        variante = normalizar_texto(datos.get("variante", VARIANTE)) or VARIANTE
        if variante not in {VARIANTE, "carbono14", "carbono_14", "datacion"}:
            raise ErrorValidacion(f"Variante no soportada en Carbono-14: {variante}.")

        tipo_calculo = normalizar_texto(datos.get("tipo_calculo", "cantidad_en_tiempo"))
        vida_media_es_por_defecto = not _hay_valor(datos, "vida_media", "semivida")
        vida_media = _obtener_vida_media(datos)
        constante_k = constante_decaimiento_por_vida_media(vida_media)
        constante_k_num = float(sp.N(constante_k))
        variable_t = crear_variable("t")

        if tipo_calculo in TIPOS_FORMULA:
            return _respuesta_formula_simbolica(vida_media)

        pasos = _crear_pasos_base(vida_media)
        constantes = {
            "vida_media": redondear(vida_media),
            "k": redondear(constante_k_num, DECIMALES_CONSTANTE),
        }
        advertencias_base = []
        if vida_media_es_por_defecto:
            advertencias_base.append(
                "La vida media se dejó vacía; se usó automáticamente 5730 años, que es el dato del modelo de Carbono-14 del parcial."
            )

        if tipo_calculo in TIPOS_FUNCION:
            cantidad_inicial_es_por_defecto = not _hay_valor(datos, "cantidad_inicial", "masa_inicial", "M0")
            cantidad_inicial = validar_positivo(
                obtener_valor(datos, ("cantidad_inicial", "masa_inicial", "M0"), "cantidad inicial"),
                "Cantidad inicial",
            ) if not cantidad_inicial_es_por_defecto else 1.0
            advertencias_funcion = [*advertencias_base]
            if cantidad_inicial_es_por_defecto:
                advertencias_funcion.append(
                    "La cantidad inicial se dejó vacía en el modo función; se usó M0=1 como referencia relativa para construir el modelo."
                )
            expresion = expresion_carbono14(cantidad_inicial, vida_media, variable_t)
            pasos.append(
                crear_paso(
                    "Función particular construida con SymPy",
                    "Se construye M(t) con la cantidad inicial proporcionada o con M0=1 si el usuario solo quiere una función relativa. La constante k viene de la vida media, por lo que el modelo queda coherente con el enunciado del Carbono-14.",
                    paso_sympy("M", variable_t, expresion),
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Función particular del Carbono-14",
                tipo="funcion",
                resultado=f"M(t)={formatear_numero(cantidad_inicial)}e^(-{formatear_numero(constante_k_num, DECIMALES_CONSTANTE)}t)",
                resultado_latex=igualdad_funcion("M", variable_t, expresion),
                unidad=datos.get("unidad", "unidades"),
                constantes={**constantes, "M0": redondear(cantidad_inicial)},
                pasos=pasos,
                advertencias=advertencias_funcion,
            )

        if tipo_calculo in TIPOS_CANTIDAD:
            cantidad_inicial = validar_positivo(
                obtener_valor(datos, ("cantidad_inicial", "masa_inicial", "M0"), "cantidad inicial"),
                "Cantidad inicial",
            )
            tiempo_objetivo = validar_no_negativo(
                obtener_valor(datos, ("tiempo_objetivo", "tiempo", "t"), "tiempo objetivo"),
                "Tiempo objetivo",
            )
            expresion = expresion_carbono14(cantidad_inicial, vida_media, variable_t)
            valor = evaluar(expresion, variable_t, tiempo_objetivo)
            pasos.append(
                crear_paso(
                    "Evaluación de cantidad restante",
                    "Se reemplaza el tiempo solicitado dentro de la función M(t). SymPy evalúa la exponencial con k=ln(2)/vida_media y devuelve la cantidad que debería quedar después de ese número de años.",
                    rf"\begin{{gathered}}M({formatear_numero(tiempo_objetivo)})={formatear_numero(cantidad_inicial)}e^{{-{formatear_numero(constante_k_num, DECIMALES_CONSTANTE)}({formatear_numero(tiempo_objetivo)})}}\\[4px]\boxed{{M({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}}}\end{{gathered}}",
                )
            )
            pasos.append(
                crear_paso(
                    "Verificación simbólica con SymPy",
                    "La expresión que se evalúa numéricamente también se conserva en LaTeX. Esto permite revisar que el resultado mostrado proviene exactamente de la fórmula simbólica y no de una operación aislada.",
                    paso_sympy("M", variable_t, expresion),
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Cantidad restante de Carbono-14",
                tipo="cantidad_en_tiempo",
                resultado=redondear(valor),
                resultado_latex=rf"M({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(valor)}",
                unidad=datos.get("unidad", "unidades"),
                constantes={**constantes, "M0": redondear(cantidad_inicial)},
                pasos=pasos,
                advertencias=advertencias_base,
            )

        if tipo_calculo in TIPOS_PORCENTAJE:
            tiempo_objetivo = validar_no_negativo(
                obtener_valor(datos, ("tiempo_objetivo", "tiempo", "t"), "tiempo objetivo"),
                "Tiempo objetivo",
            )
            expresion = expresion_porcentaje_carbono14(vida_media, variable_t)
            porcentaje = evaluar(expresion, variable_t, tiempo_objetivo)
            pasos.append(
                crear_paso(
                    "Porcentaje restante",
                    "Para calcular porcentaje no hace falta conocer la masa original. El sistema toma M0=100 como referencia relativa, evalúa el decaimiento y expresa el resultado como porcentaje restante.",
                    rf"\begin{{gathered}}P(t)=100e^{{-kt}}\\[4px]P({formatear_numero(tiempo_objetivo)})=100e^{{-{formatear_numero(constante_k_num, DECIMALES_CONSTANTE)}({formatear_numero(tiempo_objetivo)})}}\\[4px]\boxed{{P({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(porcentaje)}\%}}\end{{gathered}}",
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Porcentaje restante de Carbono-14",
                tipo="porcentaje_en_tiempo",
                resultado=redondear(porcentaje),
                resultado_latex=rf"P({formatear_numero(tiempo_objetivo)})\approx {formatear_numero(porcentaje)}\%",
                unidad="%",
                constantes=constantes,
                pasos=pasos,
                advertencias=advertencias_base,
            )

        if tipo_calculo in TIPOS_EDAD_POR_PORCENTAJE:
            porcentaje_restante = validar_positivo(
                obtener_valor(datos, ("porcentaje_restante", "porcentaje", "fraccion_porcentual"), "porcentaje restante"),
                "Porcentaje restante",
            )
            if porcentaje_restante > 100:
                raise ErrorValidacion("El porcentaje restante no puede ser mayor que 100%.")
            tiempo = float(sp.N(sp.log(decimal(100) / decimal(porcentaje_restante)) / constante_k))
            pasos.append(
                crear_paso(
                    "Edad desde porcentaje restante",
                    "Se parte del porcentaje medido actualmente y se despeja el tiempo. El logaritmo natural aparece porque la variable t está en el exponente de la función de decaimiento.",
                    rf"\begin{{gathered}}{formatear_numero(porcentaje_restante)}=100e^{{-kt}}\\[4px]t=\frac{{\ln\left(\frac{{100}}{{{formatear_numero(porcentaje_restante)}}}\right)}}{{k}}\\[4px]\boxed{{t\approx {formatear_numero(tiempo)}\;\text{{años}}}}\end{{gathered}}",
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Datación por porcentaje de Carbono-14",
                tipo="edad_por_porcentaje",
                resultado=redondear(tiempo),
                resultado_latex=rf"t\approx {formatear_numero(tiempo)}\;\text{{años}}",
                unidad="años",
                constantes=constantes,
                pasos=pasos,
                advertencias=advertencias_base,
            )

        if tipo_calculo in TIPOS_EDAD_POR_CANTIDAD:
            cantidad_inicial = validar_positivo(
                obtener_valor(datos, ("cantidad_inicial", "masa_inicial", "M0"), "cantidad inicial"),
                "Cantidad inicial",
            )
            cantidad_restante = validar_positivo(
                obtener_valor(datos, ("cantidad_restante", "cantidad_objetivo", "masa_restante", "Mf"), "cantidad restante"),
                "Cantidad restante",
            )
            if cantidad_restante > cantidad_inicial:
                raise ErrorValidacion("La cantidad restante no puede ser mayor que la cantidad inicial.")
            tiempo = float(sp.N(sp.log(decimal(cantidad_inicial) / decimal(cantidad_restante)) / constante_k))
            pasos.append(
                crear_paso(
                    "Edad desde cantidad restante",
                    "Se compara la cantidad inicial M0 con la cantidad restante Mf. Si Mf es menor o igual que M0, se puede aplicar logaritmo natural para calcular cuántos años debieron pasar para llegar a esa proporción.",
                    rf"\begin{{gathered}}{formatear_numero(cantidad_restante)}={formatear_numero(cantidad_inicial)}e^{{-kt}}\\[4px]t=\frac{{\ln\left(\frac{{{formatear_numero(cantidad_inicial)}}}{{{formatear_numero(cantidad_restante)}}}\right)}}{{k}}\\[4px]\boxed{{t\approx {formatear_numero(tiempo)}\;\text{{años}}}}\end{{gathered}}",
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Datación por cantidad de Carbono-14",
                tipo="edad_por_cantidad",
                resultado=redondear(tiempo),
                resultado_latex=rf"t\approx {formatear_numero(tiempo)}\;\text{{años}}",
                unidad="años",
                constantes={**constantes, "M0": redondear(cantidad_inicial), "Mf": redondear(cantidad_restante)},
                pasos=pasos,
                advertencias=advertencias_base,
            )

        if tipo_calculo in TIPOS_VIDA_MEDIA:
            pasos.append(
                crear_paso(
                    "Vida media del Carbono-14",
                    "La vida media resume el comportamiento del Carbono-14: cada 5730 años la muestra conserva la mitad de lo que tenía al inicio de ese intervalo. A partir de ese dato se obtiene k y se justifica todo el modelo.",
                    rf"\boxed{{t_{{1/2}}={formatear_numero(vida_media)}\;\text{{años}}}}\qquad \boxed{{k=\frac{{\ln 2}}{{{formatear_numero(vida_media)}}}}}",
                )
            )
            return crear_respuesta_modelo(
                modulo=MODULO,
                variante=VARIANTE,
                modelo="Vida media del Carbono-14",
                tipo="vida_media",
                resultado=redondear(vida_media),
                resultado_latex=rf"t_{{1/2}}={formatear_numero(vida_media)}\;\text{{años}}",
                unidad="años",
                constantes=constantes,
                pasos=pasos,
                advertencias=advertencias_base,
            )

        raise ErrorValidacion("Tipo de cálculo inválido para el módulo Carbono-14.")
    except (ErrorValidacion, ValueError, ZeroDivisionError) as error:
        return crear_respuesta_error(str(error))
