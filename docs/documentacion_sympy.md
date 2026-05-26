# SymPy como motor simbólico del sistema

El proyecto prioriza SymPy en la construcción de los modelos matemáticos. La aplicación no se limita a imprimir resultados numéricos: primero crea expresiones simbólicas, conserva parámetros cuando faltan datos, genera fórmulas en LaTeX y evalúa únicamente cuando la información del enunciado es suficiente.

El flujo técnico es consecutivo: el usuario ingresa datos, Flask recibe la petición, Python valida la entrada, el modelo identifica la variante, SymPy crea variables y expresiones, el backend intenta inferir constantes como `k` si existe una medición posterior, y finalmente la respuesta JSON devuelve resultado, pasos, fórmula y metadatos.

Los archivos centrales son:

- `backend/utils/simbolico.py`: motor de construcción simbólica.
- `backend/modelos/formulas_simbolicas.py`: respuestas cuando faltan datos.
- `backend/modelos/*.py`: lógica de cada familia de modelos.
- `backend/utils/derivaciones.py`: pasos matemáticos previos a la fórmula general.

El sistema no pretende resolver cualquier EDO arbitraria ingresada libremente. Su alcance es académico y controlado: crecimiento, decaimiento, enfriamiento por Ley de Newton y mezclas. Esta decisión permite explicar mejor cada fórmula, mantener el código auditable y evitar respuestas falsas cuando faltan datos.
