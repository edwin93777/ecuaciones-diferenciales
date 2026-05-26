"""Derivaciones matemáticas base para enriquecer las respuestas del backend.

Estas secciones se agregan antes de los pasos numéricos de cada modelo para que
la aplicación muestre de dónde sale la fórmula general usada por cada variante.
Se mantienen como texto/LaTeX estático porque la lógica dinámica y segura de
cálculo sigue viviendo en los módulos de modelos y en ``utils.simbolico``.
"""
from __future__ import annotations

from copy import deepcopy

Paso = dict[str, str]


DERIVACIONES: dict[tuple[str, str], list[Paso]] = {
    ("crecimiento", "crecimiento_proporcional"): [
        {
            "titulo": "Modelo diferencial proporcional",
            "descripcion": "La hipótesis dice que la rapidez de cambio es proporcional a la cantidad presente. Por eso se plantea una EDO separable de primer orden.",
            "latex": r"\frac{dP}{dt}=kP",
        },
        {
            "titulo": "Separación e integración",
            "descripcion": "Se separan las variables para integrar población en un lado y tiempo en el otro.",
            "latex": r"\frac{1}{P}\,dP=k\,dt\;\Longrightarrow\;\int\frac{1}{P}\,dP=\int k\,dt\;\Longrightarrow\;\ln|P|=kt+C",
        },
        {
            "titulo": "Despeje de la solución general",
            "descripcion": "Al aplicar exponencial, la constante aditiva se transforma en una constante multiplicativa positiva.",
            "latex": r"P(t)=Ce^{kt}",
        },
        {
            "titulo": "Condición inicial y constante C",
            "descripcion": "La condición inicial determina la constante de integración.",
            "latex": r"P(0)=P_0\;\Longrightarrow\;C=P_0\;\Longrightarrow\;P(t)=P_0e^{kt}",
        },
        {
            "titulo": "Inferencia de k cuando existe un dato conocido",
            "descripcion": "Si se conoce una medición posterior, el sistema despeja k sin obligar al usuario a escribirla manualmente.",
            "latex": r"P(t_1)=P_1\;\Longrightarrow\;P_1=P_0e^{kt_1}\;\Longrightarrow\;k=\frac{1}{t_1}\ln\left(\frac{P_1}{P_0}\right)",
        },
    ],
    ("crecimiento", "interes_continuo"): [
        {
            "titulo": "Modelo de capital con capitalización continua",
            "descripcion": "El capital crece proporcionalmente al capital disponible. La tasa porcentual se transforma a tasa decimal antes de construir la expresión.",
            "latex": r"\frac{dS}{dt}=rS",
        },
        {
            "titulo": "Separación de variables",
            "descripcion": "El procedimiento es análogo al crecimiento poblacional, reemplazando la población por el capital.",
            "latex": r"\frac{1}{S}\,dS=r\,dt\;\Longrightarrow\;\ln|S|=rt+C",
        },
        {
            "titulo": "Fórmula general y condición inicial",
            "descripcion": "La condición S(0)=S0 convierte la constante de integración en el capital inicial.",
            "latex": r"S(t)=Ce^{rt},\quad S(0)=S_0\Rightarrow C=S_0\Rightarrow S(t)=S_0e^{rt}",
        },
        {
            "titulo": "Uso de la tasa porcentual",
            "descripcion": "Cuando el usuario ingresa una tasa en porcentaje, el backend la transforma a decimal para evitar confusiones entre 6 y 0.06.",
            "latex": r"r=\frac{\text{tasa porcentual}}{100}",
        },
    ],
    ("crecimiento", "entrada_constante"): [
        {
            "titulo": "Modelo lineal con fuente externa",
            "descripcion": "La población no solo crece proporcionalmente; además recibe una entrada constante b por unidad de tiempo.",
            "latex": r"\frac{dP}{dt}=kP+b\;\Longleftrightarrow\;\frac{dP}{dt}-kP=b",
        },
        {
            "titulo": "Factor integrante",
            "descripcion": "La ecuación lineal se resuelve multiplicando por el factor integrante asociado a -k.",
            "latex": r"\mu(t)=e^{\int -k\,dt}=e^{-kt}",
        },
        {
            "titulo": "Integración del producto",
            "descripcion": "Al multiplicar por el factor integrante, el lado izquierdo se convierte en una derivada exacta.",
            "latex": r"e^{-kt}\frac{dP}{dt}-ke^{-kt}P=be^{-kt}\;\Longrightarrow\;\frac{d}{dt}\left(Pe^{-kt}\right)=be^{-kt}",
        },
        {
            "titulo": "Solución general",
            "descripcion": "Después de integrar y despejar P(t), aparece una parte exponencial y un término de equilibrio desplazado.",
            "latex": r"Pe^{-kt}=\int be^{-kt}dt=-\frac{b}{k}e^{-kt}+C\;\Longrightarrow\;P(t)=Ce^{kt}-\frac{b}{k}",
        },
        {
            "titulo": "Condición inicial y constante C",
            "descripcion": "La condición inicial permite reemplazar C por una expresión en términos de P0, b y k.",
            "latex": r"P(0)=P_0\Rightarrow P_0=C-\frac{b}{k}\Rightarrow C=P_0+\frac{b}{k}\Rightarrow P(t)=\left(P_0+\frac{b}{k}\right)e^{kt}-\frac{b}{k}",
        },
    ],
    ("crecimiento", "caida_resistencia"): [
        {
            "titulo": "Modelo físico de caída con resistencia lineal",
            "descripcion": "La gravedad aumenta la velocidad y la resistencia proporcional a la velocidad la reduce.",
            "latex": r"\frac{dv}{dt}=g-kv\;\Longleftrightarrow\;\frac{dv}{dt}+kv=g",
        },
        {
            "titulo": "Factor integrante",
            "descripcion": "La ecuación es lineal de primer orden y se resuelve con factor integrante.",
            "latex": r"\mu(t)=e^{\int k\,dt}=e^{kt}",
        },
        {
            "titulo": "Integración",
            "descripcion": "Al multiplicar por e^{kt}, el lado izquierdo queda como derivada de ve^{kt}.",
            "latex": r"\frac{d}{dt}\left(ve^{kt}\right)=ge^{kt}\;\Longrightarrow\;ve^{kt}=\frac{g}{k}e^{kt}+C",
        },
        {
            "titulo": "Solución general y condición inicial",
            "descripcion": "Al despejar y aplicar v(0)=v0 se obtiene la fórmula particular usada por el sistema.",
            "latex": r"v(t)=\frac{g}{k}+Ce^{-kt},\quad v(0)=v_0\Rightarrow C=v_0-\frac{g}{k}\Rightarrow v(t)=\frac{g}{k}+\left(v_0-\frac{g}{k}\right)e^{-kt}",
        },
        {
            "titulo": "Comprobación de velocidad límite",
            "descripcion": "Cuando t crece, el término exponencial desaparece y queda la velocidad terminal.",
            "latex": r"\lim_{t\to\infty}v(t)=\frac{g}{k}",
        },
    ],
    ("decaimiento", "decaimiento_radiactivo"): [
        {
            "titulo": "Modelo de pérdida proporcional",
            "descripcion": "La cantidad disminuye proporcionalmente a la cantidad presente; por eso el signo es negativo.",
            "latex": r"\frac{dA}{dt}=-kA,\quad k>0",
        },
        {
            "titulo": "Separación e integración",
            "descripcion": "Se separan variables y se integra para construir la función exponencial decreciente.",
            "latex": r"\frac{1}{A}\,dA=-k\,dt\Rightarrow \ln|A|=-kt+C",
        },
        {
            "titulo": "Fórmula general y condición inicial",
            "descripcion": "La condición inicial A(0)=A0 determina la constante C multiplicativa.",
            "latex": r"A(t)=Ce^{-kt},\quad A(0)=A_0\Rightarrow C=A_0\Rightarrow A(t)=A_0e^{-kt}",
        },
        {
            "titulo": "Inferencia de k y vida media",
            "descripcion": "Con una medición posterior se despeja k; con k se calcula el tiempo para llegar a la mitad.",
            "latex": r"k=\frac{1}{t_1}\ln\left(\frac{A_0}{A_1}\right),\qquad t_{1/2}=\frac{\ln 2}{k}",
        },
    ],
    ("decaimiento", "absorcion_medicamento"): [
        {
            "titulo": "Modelo de eliminación del medicamento",
            "descripcion": "La concentración baja a una tasa proporcional a la concentración actual.",
            "latex": r"\frac{dC}{dt}=-kC",
        },
        {
            "titulo": "Integración separable",
            "descripcion": "El método es separable y produce una función exponencial decreciente.",
            "latex": r"\int\frac{1}{C}\,dC=\int -k\,dt\Rightarrow \ln|C|=-kt+C_1",
        },
        {
            "titulo": "Función de concentración",
            "descripcion": "La condición C(0)=C0 fija la constante de integración.",
            "latex": r"C(t)=C_0e^{-kt}",
        },
        {
            "titulo": "Tiempo para una concentración objetivo",
            "descripcion": "Para saber cuándo se alcanza un valor objetivo, se despeja el tiempo con logaritmo natural.",
            "latex": r"C_f=C_0e^{-kt}\Rightarrow t=\frac{1}{k}\ln\left(\frac{C_0}{C_f}\right)",
        },
    ],
    ("decaimiento", "descarga_capacitor"): [
        {
            "titulo": "Modelo eléctrico RC",
            "descripcion": "La carga del capacitor disminuye proporcionalmente a la carga presente. En circuitos RC, la constante de decaimiento es 1/(RC).",
            "latex": r"\frac{dq}{dt}=-\frac{1}{RC}q",
        },
        {
            "titulo": "Separación de variables",
            "descripcion": "La ecuación se resuelve como un decaimiento exponencial, pero manteniendo R y C si no son conocidos.",
            "latex": r"\frac{1}{q}\,dq=-\frac{1}{RC}\,dt\Rightarrow \ln|q|=-\frac{t}{RC}+C_1",
        },
        {
            "titulo": "Solución general",
            "descripcion": "Al aplicar exponencial se obtiene la forma general de descarga.",
            "latex": r"q(t)=Ce^{-t/(RC)}",
        },
        {
            "titulo": "Condición inicial",
            "descripcion": "La carga inicial q(0)=q0 determina la constante C.",
            "latex": r"q(0)=q_0\Rightarrow C=q_0\Rightarrow q(t)=q_0e^{-t/(RC)}",
        },
        {
            "titulo": "Tiempo para una carga objetivo",
            "descripcion": "Si se busca cuándo queda una carga qf, se despeja t con logaritmos.",
            "latex": r"q_f=q_0e^{-t/(RC)}\Rightarrow t=RC\ln\left(\frac{q_0}{q_f}\right)",
        },
    ],
    ("decaimiento", "intensidad_luz"): [
        {
            "titulo": "Modelo de atenuación de luz",
            "descripcion": "La intensidad disminuye proporcionalmente a la intensidad que queda al avanzar una distancia x.",
            "latex": r"\frac{dI}{dx}=-kI",
        },
        {
            "titulo": "Integración con distancia",
            "descripcion": "Se usa x como variable independiente, pero el procedimiento es el mismo del decaimiento exponencial.",
            "latex": r"\frac{1}{I}\,dI=-k\,dx\Rightarrow \ln|I|=-kx+C",
        },
        {
            "titulo": "Función de intensidad",
            "descripcion": "La intensidad inicial determina la constante multiplicativa.",
            "latex": r"I(x)=I_0e^{-kx}",
        },
        {
            "titulo": "Inferencia de k desde un porcentaje",
            "descripcion": "Si a una distancia x1 queda cierto porcentaje de la intensidad, k se obtiene de la razón I1/I0.",
            "latex": r"I_1=I_0e^{-kx_1}\Rightarrow k=\frac{1}{x_1}\ln\left(\frac{I_0}{I_1}\right)",
        },
    ],
    ("enfriamiento", "newton_constante"): [
        {
            "titulo": "Ley de enfriamiento de Newton",
            "descripcion": "La temperatura cambia proporcionalmente a la diferencia entre la temperatura del objeto y la temperatura ambiente.",
            "latex": r"\frac{dT}{dt}=-k(T-T_a)",
        },
        {
            "titulo": "Cambio de variable",
            "descripcion": "Se define u=T-Ta para convertir el modelo en una ecuación separable de decaimiento.",
            "latex": r"u=T-T_a\Rightarrow \frac{du}{dt}=\frac{dT}{dt}=-ku",
        },
        {
            "titulo": "Solución para la diferencia térmica",
            "descripcion": "La diferencia con el ambiente disminuye exponencialmente.",
            "latex": r"u(t)=Ce^{-kt}",
        },
        {
            "titulo": "Regreso a temperatura y condición inicial",
            "descripcion": "Al volver a T y aplicar T(0)=T0 se obtiene la fórmula general de Newton.",
            "latex": r"T(t)-T_a=Ce^{-kt},\quad T(0)=T_0\Rightarrow C=T_0-T_a\Rightarrow T(t)=T_a+(T_0-T_a)e^{-kt}",
        },
        {
            "titulo": "Inferencia de k",
            "descripcion": "Si se conoce una temperatura posterior, la constante se despeja con una razón de diferencias térmicas.",
            "latex": r"T_1=T_a+(T_0-T_a)e^{-kt_1}\Rightarrow k=-\frac{1}{t_1}\ln\left(\frac{T_1-T_a}{T_0-T_a}\right)",
        },
    ],
    ("enfriamiento", "calentamiento_newton"): [
        {
            "titulo": "Modelo de acercamiento al ambiente",
            "descripcion": "El mismo modelo sirve para calentamiento cuando el ambiente está por encima del objeto: la diferencia térmica tiende a cero.",
            "latex": r"\frac{dT}{dt}=-k(T-T_a)",
        },
        {
            "titulo": "Diferencia térmica como variable",
            "descripcion": "La variable u=T-Ta puede ser negativa al inicio, pero su magnitud disminuye exponencialmente.",
            "latex": r"u=T-T_a\Rightarrow u'= -ku\Rightarrow u(t)=Ce^{-kt}",
        },
        {
            "titulo": "Fórmula general",
            "descripcion": "La condición inicial produce la misma fórmula estructural usada en enfriamiento.",
            "latex": r"T(t)=T_a+(T_0-T_a)e^{-kt}",
        },
        {
            "titulo": "Equilibrio térmico",
            "descripcion": "A largo plazo el exponencial desaparece y la temperatura se acerca a la del ambiente.",
            "latex": r"\lim_{t\to\infty}T(t)=T_a",
        },
    ],
    ("mezclas", "volumen_constante"): [
        {
            "titulo": "Balance de soluto",
            "descripcion": "La cantidad de sal cambia por la sal que entra menos la sal que sale.",
            "latex": r"\frac{dA}{dt}=\text{entrada}-\text{salida}",
        },
        {
            "titulo": "Entrada de soluto",
            "descripcion": "La entrada se calcula como concentración de entrada por caudal de entrada.",
            "latex": r"\text{entrada}=r_ec_e",
        },
        {
            "titulo": "Salida con volumen constante",
            "descripcion": "Si el tanque está bien mezclado, la concentración interna es A/V y la salida de soluto es caudal por concentración interna.",
            "latex": r"\text{salida}=r_s\frac{A}{V}",
        },
        {
            "titulo": "Ecuación diferencial lineal",
            "descripcion": "Cuando los caudales son iguales, el volumen permanece constante y aparece una EDO lineal.",
            "latex": r"\frac{dA}{dt}=r_ec_e-\frac{r_s}{V}A",
        },
        {
            "titulo": "Solución alrededor del equilibrio",
            "descripcion": "Si re=rs=r, el equilibrio es A∞=Vc_e y la solución decae hacia ese valor.",
            "latex": r"A(t)=Vc_e+(A_0-Vc_e)e^{-(r/V)t}",
        },
    ],
    ("mezclas", "volumen_variable"): [
        {
            "titulo": "Volumen variable del tanque",
            "descripcion": "Cuando entran y salen caudales distintos, el volumen cambia linealmente con el tiempo.",
            "latex": r"V(t)=V_0+(r_e-r_s)t",
        },
        {
            "titulo": "Balance de soluto",
            "descripcion": "La entrada de soluto es constante si la concentración de entrada y el caudal de entrada son constantes; la salida depende de A/V(t).",
            "latex": r"\frac{dA}{dt}=r_ec_e-r_s\frac{A}{V(t)}",
        },
        {
            "titulo": "Ecuación lineal con coeficiente variable",
            "descripcion": "La ecuación se escribe en forma estándar para resolverla con factor integrante.",
            "latex": r"\frac{dA}{dt}+\frac{r_s}{V_0+(r_e-r_s)t}A=r_ec_e",
        },
        {
            "titulo": "Estructura de solución usada",
            "descripcion": "El sistema conserva una expresión simbólica dependiente de V(t), que SymPy puede evaluar cuando el tiempo objetivo existe.",
            "latex": r"A(t)=c_eV(t)+(A_0-c_eV_0)\left(\frac{V_0}{V(t)}\right)^{\frac{r_s}{r_e-r_s}}",
        },
    ],
}


_ALIASES: dict[tuple[str, str], tuple[str, str]] = {
    ("decaimiento", "default"): ("decaimiento", "decaimiento_radiactivo"),
}


def obtener_pasos_derivacion(modulo: str, variante: str) -> list[Paso]:
    """Obtiene una copia de los pasos teóricos para no mutar la plantilla global."""
    clave = (modulo, variante)
    if clave not in DERIVACIONES and clave in _ALIASES:
        clave = _ALIASES[clave]
    return deepcopy(DERIVACIONES.get(clave, []))
