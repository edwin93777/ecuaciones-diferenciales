"""Utilidades de formato para respuestas matemáticas."""
from __future__ import annotations

from math import isfinite

DECIMALES_RESULTADO = 6
DECIMALES_CONSTANTE = 8


def formatear_numero(valor: float | int, decimales: int = DECIMALES_RESULTADO) -> str:
    """Devuelve números limpios para fórmulas LaTeX y textos."""
    numero = float(valor)
    if not isfinite(numero):
        return str(numero)

    if abs(numero - round(numero)) < 10 ** (-(decimales + 1)):
        return str(int(round(numero)))

    texto = f"{numero:.{decimales}f}".rstrip("0").rstrip(".")
    return texto if texto not in ("-0", "") else "0"


def redondear(valor: float | int, decimales: int = DECIMALES_RESULTADO) -> float:
    """Redondea valores numéricos manteniendo tipo float."""
    return round(float(valor), decimales)



def _escapar_texto_latex(valor: str) -> str:
    """Escapa caracteres comunes para colocar texto dentro de \text{...}."""
    reemplazos = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "_": r"\_",
        "^": r"\^{}",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "~": r"\~{}",
    }
    return "".join(reemplazos.get(caracter, caracter) for caracter in str(valor))


def _crear_latex_resultado_generico(resultado: float | str | None, unidad: str = "") -> str | None:
    """Genera una salida LaTeX final cuando un modelo no envía una específica.

    Los pasos de cada modelo ya contienen LaTeX detallado; esta función garantiza
    que el bloque de resultado final también tenga representación matemática.
    """
    if resultado is None:
        return None

    unidad_limpia = str(unidad or "").strip()
    if isinstance(resultado, (int, float)):
        valor = formatear_numero(resultado)
        if unidad_limpia:
            return rf"\boxed{{{valor}\;\text{{{_escapar_texto_latex(unidad_limpia)}}}}}"
        return rf"\boxed{{{valor}}}"

    texto = str(resultado).strip()
    if not texto:
        return None

    texto_latex = _escapar_texto_latex(texto)
    if unidad_limpia:
        unidad_latex = _escapar_texto_latex(unidad_limpia)
        return rf"\boxed{{\text{{{texto_latex}}}\;\text{{{unidad_latex}}}}}"
    return rf"\boxed{{\text{{{texto_latex}}}}}"


def crear_paso(titulo: str, descripcion: str, latex: str) -> dict[str, str]:
    """Crea un bloque homogéneo para mostrar la solución paso a paso."""
    return {"titulo": titulo, "descripcion": descripcion, "latex": latex}


def crear_respuesta_modelo(
    *,
    modulo: str,
    variante: str,
    modelo: str,
    tipo: str,
    resultado: float | str | None,
    unidad: str = "",
    resultado_latex: str | None = None,
    constantes: dict[str, float | str] | None = None,
    pasos: list[dict[str, str]] | None = None,
    advertencias: list[str] | None = None,
    metadatos: dict[str, float | str] | None = None,
) -> dict:
    """Estandariza la respuesta de todos los modelos."""
    metadatos_finales = {
        "motor_matematico": "SymPy",
        "prioridad_modelado": "construccion_simbolica_con_sympy",
    }
    metadatos_finales.update(metadatos or {})

    pasos_modelo = pasos or []
    try:
        from backend.utils.derivaciones import obtener_pasos_derivacion

        derivacion = obtener_pasos_derivacion(modulo, variante)
    except Exception:
        # La respuesta del modelo no debe fallar si el bloque pedagógico opcional
        # tiene un problema de importación durante un despliegue parcial.
        derivacion = []

    pasos_finales = derivacion + pasos_modelo

    return {
        "modulo": modulo,
        "variante": variante,
        "modelo": modelo,
        "tipo": tipo,
        "resultado": resultado,
        "resultado_latex": resultado_latex or _crear_latex_resultado_generico(resultado, unidad),
        "unidad": unidad,
        "constantes": constantes or {},
        "pasos": pasos_finales,
        "advertencias": advertencias or [],
        "metadatos": metadatos_finales,
    }
