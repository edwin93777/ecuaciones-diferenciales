# Documentación SymPy actualizada

El proyecto usa SymPy como motor simbólico para evitar fórmulas escritas a mano sin trazabilidad matemática. Las expresiones se construyen como objetos simbólicos, se evalúan con sustituciones controladas y se convierten a LaTeX para la interfaz.

## Versión objetivo

- SymPy: `1.14.0` en `requirements.txt`.
- La versión se mantiene fijada para despliegues reproducibles.

## Funciones simbólicas nuevas

En `backend/utils/simbolico.py` se agregaron utilidades para Carbono-14:

- `constante_decaimiento_por_vida_media(vida_media)`: construye `k = ln(2) / vida_media`.
- `expresion_carbono14(cantidad_inicial, vida_media, variable)`: construye `M(t)=M0*exp(-(ln(2)/vida_media)t)`.
- `expresion_porcentaje_carbono14(vida_media, variable)`: construye `P(t)=100*exp(-(ln(2)/vida_media)t)`.

## Nuevo módulo Carbono-14

El módulo `backend/modelos/carbono14.py` usa SymPy para:

1. Plantear `dM/dt=-kM`.
2. Resolver `M(t)=Ce^{-kt}`.
3. Aplicar `M(0)=M0`.
4. Usar la vida media `M(5730)=M0/2`.
5. Despejar `k=ln(2)/5730`.
6. Evaluar cantidad, porcentaje o edad de la muestra.

## Interfaz pedagógica

Los bloques de código que usan variables o funciones de SymPy ahora resaltan visualmente esas partes y muestran una viñeta informativa que explica qué hace el fragmento, para qué sirve y qué resultado debe producir.


## Viñetas explicativas por fragmento

Las viñetas de los bloques de código ahora explican las funciones y operadores simbólicos que aparecen realmente en cada fragmento. Si el bloque usa `sp.log`, la viñeta explica que SymPy representa el logaritmo natural `ln`; si aparece `sp.exp`, explica cómo se conserva una exponencial simbólica como `e^(-kt)`; si aparece `sp.sqrt`, la viñeta queda preparada para explicar raíces simbólicas; y si el fragmento contiene productos como `constante_k * variable` o `t * l`, se aclara que SymPy construye un producto algebraico interno, no una simple cadena de texto.

También se documentan `sp.Symbol`, `sp.Expr`, `sp.Float`, `sp.latex`, `.subs`, `sp.N`, `sp.Eq`, `sp.solve`, `sp.simplify`, `sp.integrate`, `sp.diff`, `sp.Rational` y operadores como `/`, `**`, `+` y el signo negativo en exponentes de decaimiento. El objetivo es que el estudiante pueda defender no solo la fórmula final, sino la forma exacta en que SymPy la representa, la opera, la sustituye y la convierte a LaTeX.
