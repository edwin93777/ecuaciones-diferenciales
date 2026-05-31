"""Motor simbólico del proyecto usando SymPy.

El sistema mantiene los cálculos numéricos controlados, pero construye las
funciones principales con SymPy para generar fórmulas LaTeX consistentes y
validar simbólicamente las expresiones de cada modelo.
"""
from __future__ import annotations

from typing import Final

import sympy as sp

PRECISION_SIMBOLICA: Final[int] = 15


def crear_variable(nombre: str = "t") -> sp.Symbol:
    """Crea una variable simbólica real."""
    return sp.symbols(nombre, real=True)


def decimal(valor: float | int) -> sp.Float:
    """Convierte un número Python en número SymPy con precisión controlada."""
    return sp.Float(float(valor), PRECISION_SIMBOLICA)


def latex(expresion: sp.Expr) -> str:
    """Convierte una expresión SymPy a LaTeX."""
    return sp.latex(expresion)


def evaluar(expresion: sp.Expr, variable: sp.Symbol, valor: float | int) -> float:
    """Evalúa una expresión simbólica en un punto y retorna float."""
    return float(sp.N(expresion.subs(variable, decimal(valor))))


def expresion_crecimiento_exponencial(cantidad_inicial: float, constante_k: float, variable: sp.Symbol) -> sp.Expr:
    return decimal(cantidad_inicial) * sp.exp(decimal(constante_k) * variable)


def expresion_decaimiento_exponencial(cantidad_inicial: float, constante_k: float, variable: sp.Symbol) -> sp.Expr:
    return decimal(cantidad_inicial) * sp.exp(-decimal(constante_k) * variable)


def expresion_crecimiento_entrada_constante(cantidad_inicial: float, constante_k: float, entrada_constante: float, variable: sp.Symbol) -> sp.Expr:
    k = decimal(constante_k)
    b = decimal(entrada_constante)
    return (decimal(cantidad_inicial) + b / k) * sp.exp(k * variable) - b / k


def expresion_caida_resistencia(velocidad_inicial: float, gravedad: float, constante_k: float, variable: sp.Symbol) -> sp.Expr:
    k = decimal(constante_k)
    velocidad_limite = decimal(gravedad) / k
    return velocidad_limite + (decimal(velocidad_inicial) - velocidad_limite) * sp.exp(-k * variable)


def expresion_newton(temperatura_inicial: float, temperatura_ambiente: float, constante_k: float, variable: sp.Symbol) -> sp.Expr:
    return decimal(temperatura_ambiente) + (decimal(temperatura_inicial) - decimal(temperatura_ambiente)) * sp.exp(-decimal(constante_k) * variable)


def expresion_mezcla_volumen_constante(sal_inicial: float, equilibrio: float, alfa: float, variable: sp.Symbol) -> sp.Expr:
    return decimal(equilibrio) + (decimal(sal_inicial) - decimal(equilibrio)) * sp.exp(-decimal(alfa) * variable)


def expresion_mezcla_volumen_variable(
    sal_inicial: float,
    volumen_inicial: float,
    concentracion_entrada: float,
    delta_volumen: float,
    exponente: float,
    variable: sp.Symbol,
) -> sp.Expr:
    volumen = decimal(volumen_inicial) + decimal(delta_volumen) * variable
    return decimal(concentracion_entrada) * volumen + (
        decimal(sal_inicial) - decimal(concentracion_entrada) * decimal(volumen_inicial)
    ) * (decimal(volumen_inicial) / volumen) ** decimal(exponente)


def constante_decaimiento_por_vida_media(vida_media: float | int) -> sp.Expr:
    """Construye k = ln(2) / vida_media con SymPy."""
    return sp.log(2) / decimal(vida_media)


def expresion_carbono14(cantidad_inicial: float, vida_media: float, variable: sp.Symbol) -> sp.Expr:
    """Construye M(t)=M0*exp(-(ln(2)/vida_media)t) para Carbono-14."""
    constante_k = constante_decaimiento_por_vida_media(vida_media)
    return decimal(cantidad_inicial) * sp.exp(-constante_k * variable)


def expresion_porcentaje_carbono14(vida_media: float, variable: sp.Symbol) -> sp.Expr:
    """Construye P(t)=100*exp(-(ln(2)/vida_media)t)."""
    constante_k = constante_decaimiento_por_vida_media(vida_media)
    return decimal(100) * sp.exp(-constante_k * variable)


def igualdad_funcion(nombre: str, variable: sp.Symbol, expresion: sp.Expr) -> str:
    """Devuelve una igualdad tipo f(t)=... en LaTeX."""
    return rf"{nombre}({sp.latex(variable)})={sp.latex(expresion)}"


def paso_sympy(nombre: str, variable: sp.Symbol, expresion: sp.Expr) -> str:
    """Bloque LaTeX compacto para mostrar la función que SymPy evaluará."""
    return rf"\boxed{{{igualdad_funcion(nombre, variable, expresion)}}}"
