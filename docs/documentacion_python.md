# Python en la aplicación

Python organiza el backend completo del sistema. Flask expone rutas, los modelos resuelven cada familia matemática, las utilidades validan entradas y SymPy construye las expresiones simbólicas. Esta separación mantiene el proyecto más claro, escalable y fácil de explicar en una exposición académica.

La estructura principal es:

- `backend/app.py`: crea la aplicación Flask y registra módulos.
- `backend/routes`: recibe peticiones HTTP y llama a los modelos.
- `backend/modelos`: contiene la lógica matemática.
- `backend/utils`: contiene validación, formato, respuesta y motor simbólico.
- `tests`: verifica que los modelos respondan correctamente.

Las respuestas del backend usan un formato uniforme con resultado, unidad, constantes, pasos en LaTeX, advertencias y metadatos. Esto permite que el frontend sea genérico y que cualquier modelo pueda renderizarse sin duplicar lógica.
