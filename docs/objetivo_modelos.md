# Objetivo corregido del proyecto

El proyecto no busca resolver casos como páginas aisladas. La intención correcta es montar modelos matemáticos reutilizables agrupados por familias:

1. Crecimiento.
2. Decaimiento.
3. Enfriamiento por Ley de Newton.
4. Mezclas.

Cada familia contiene variantes seleccionables desde la lista dinámica del frontend. Por ejemplo, decaimiento contiene radiactividad, absorción de medicamento, descarga de capacitor e intensidad de luz. Todas se resuelven con una misma estructura base `y' = -ky`, cambiando nombres, unidades y parámetros.

## Ajustes técnicos incluidos

- Uso de `sympy` como motor simbólico para construir expresiones matemáticas y generar LaTeX.
- Pasos humanos resumidos: modelo, sustitución, constante, función particular y evaluación.
- Interfaz dark con enfoque matemático.
- Botones laterales limpios: no contienen enunciados largos ni agrupaciones extensas.
- Estructura preparada para Render con `Procfile`, `render.yaml`, `requirements.txt` y `gunicorn run:app`.

Este diseño evita duplicación, mejora la mantenibilidad y permite explicar al profesor que el sistema está construido por modelos reutilizables, no por ejercicios quemados en el código.

## Ajuste de presentación

El desplazamiento invisible se limita al listado lateral de módulos. La documentación y los resultados matemáticos ya no quedan encerrados en contenedores internos con altura máxima, lo cual mejora la lectura en pantallas grandes, portátiles y dispositivos móviles.

Además, el bloque de resultado final se representa también en LaTeX cuando el modelo no envía una fórmula específica. Esto mantiene coherencia visual entre los pasos intermedios y la respuesta final.
