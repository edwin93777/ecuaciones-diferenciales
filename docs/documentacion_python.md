# Documentación Python actualizada

El proyecto usa Python como capa de backend para recibir datos del navegador, validar entradas, seleccionar el modelo matemático y entregar respuestas JSON con pasos en LaTeX.

## Versión objetivo

- Python objetivo para Render: `python-3.14.3`.
- Archivo actualizado: `runtime.txt`.
- La estructura del código conserva compatibilidad con `from __future__ import annotations`, type hints modernos y separación por módulos.

## Módulos principales

- `backend/app.py`: inicializa Flask y registra los blueprints.
- `backend/routes/*_routes.py`: expone rutas HTTP pequeñas y auditables.
- `backend/modelos/*`: resuelve cada familia matemática.
- `backend/modelos/carbono14.py`: nuevo módulo especializado para el modelo de Carbono-14 del parcial.
- `backend/utils/simbolico.py`: concentra funciones compartidas con SymPy.
- `backend/utils/formato.py`: estandariza pasos, constantes, resultado y LaTeX.

## Flujo de ejecución

1. El frontend envía `variante`, `tipo_calculo` y campos del formulario.
2. La ruta Flask recibe JSON y delega al modelo correspondiente.
3. El modelo valida datos y construye expresiones con SymPy.
4. El backend devuelve resultado, constantes, pasos, advertencias y metadatos.
5. MathJax renderiza las fórmulas LaTeX en la interfaz.


## Ajuste de campos opcionales y requeridos en Carbono-14

El formulario del módulo Carbono-14 fue revisado para que los campos no aparezcan como opcionales cuando el cálculo realmente los necesita. La vida media se conserva como opcional porque el modelo puede usar 5730 años por defecto; la unidad también es opcional porque solo etiqueta el resultado. En cambio, `cantidad_inicial`, `tiempo_objetivo`, `porcentaje_restante` y `cantidad_restante` son requeridos únicamente en los tipos de cálculo donde participan directamente en la operación matemática.
