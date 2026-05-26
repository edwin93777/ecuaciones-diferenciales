# Modelos de Ecuaciones Diferenciales · Flask + SymPy · listo para Render

Proyecto académico para montar modelos de ecuaciones diferenciales por módulos, no por ejercicios aislados.

## Enfoque corregido

La aplicación mantiene cuatro módulos matemáticos principales:

- **Crecimiento**
- **Decaimiento**
- **Enfriamiento por Ley de Newton**
- **Mezclas**

Las variantes se seleccionan desde una lista dinámica dentro de cada módulo. El objetivo no es guardar respuestas fijas de ejercicios, sino montar modelos reutilizables que puedan operar con datos completos o incompletos.


## Mejoras añadidas en esta versión

Esta versión refuerza el enfoque simbólico y pedagógico del sistema:

- SymPy queda marcado como prioridad de modelado en las respuestas del backend.
- Cada respuesta matemática incorpora una derivación base antes de los pasos numéricos.
- Cada módulo y variante tiene un botón `?` con explicación completa del modelo.
- Cada input tiene un botón `?` con explicación del dato esperado.
- Las ventanas informativas incluyen fórmula general, proceso de obtención, comprobación y ejemplo por defecto del sistema.
- El módulo de documentación SymPy fue ampliado para explicar el flujo completo de construcción simbólica.
- La interfaz se adaptó a celulares con menú lateral ocultable mediante botón de hamburguesa.
- Se agregó `pytest.ini` para ejecutar pruebas directamente con `pytest -q`.

## Constante k no obligatoria

La constante `k` ya no es obligatoria. La aplicación sigue esta lógica:

1. Si `k` se entrega directamente, se usa.
2. Si `k` no se entrega pero puede inferirse con una medición conocida, se calcula.
3. Si `k` no se entrega y no puede inferirse, el sistema responde simbólicamente con SymPy.

Ejemplos:

```text
P(8)=500e^(8k)
q(t)=10e^(-t/(RC))
v∞=g/k
```

## Corrección de descarga de capacitor

La descarga de capacitor ahora opera en tres escenarios:

```text
1. Con k directa:
   q(t)=q0e^(-kt)

2. Con R y C:
   k=1/(RC)
   q(t)=q0e^(-t/(RC))

3. Sin k, R ni C:
   q(t)=q0e^(-t/(RC))
   t=RC ln(q0/qf)
```

## Módulos matemáticos

### Crecimiento

- crecimiento poblacional proporcional;
- interés compuesto continuo;
- crecimiento con entrada constante;
- caída con resistencia del aire.

### Decaimiento

- decaimiento radiactivo;
- absorción/eliminación de medicamento;
- descarga de capacitor;
- intensidad de luz.

### Enfriamiento

- enfriamiento hacia ambiente;
- calentamiento hacia ambiente.

### Mezclas

- volumen constante;
- volumen variable.

## Módulos documento

Se añadieron módulos tipo documento dentro de la interfaz:

- **Python**: documentación general del lenguaje y explicación de cómo se usó en el backend.
- **SymPy**: explicación detallada del motor simbólico, uso de variables indeterminadas, LaTeX, EDO y propósito académico.
- **Autoría y permiso**: desarrollador, autorización concedida al profesor Tito Amauryt y aviso de almacenamiento local.

## Uso de SymPy

SymPy se utiliza para:

- construir expresiones simbólicas;
- conservar variables indeterminadas como `k`, `C`, `R`, `t`, `P0`, `Ta` o `RC`;
- generar salidas LaTeX;
- evaluar funciones cuando sí hay datos completos;
- evitar inventar constantes cuando el enunciado no las proporciona.

## Despliegue en Render

El proyecto está preparado para ejecutarse como una única aplicación Flask servida por Gunicorn. El frontend usa rutas relativas contra el mismo dominio publicado, por ejemplo `/resolver/crecimiento`, `/resolver/decaimiento`, `/resolver/enfriamiento` y `/resolver/mezclas`; por eso no depende de direcciones locales ni de puertos fijos del equipo del estudiante.

Configuración recomendada en Render:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn run:app
Runtime: Python 3.11.9
```

El puerto se toma automáticamente desde la variable de entorno `PORT`, que Render inyecta durante la ejecución.

## Estructura

```text
backend/
  app.py
  modelos/
    crecimiento.py
    decaimiento.py
    enfriamiento.py
    mezclas.py
    formulas_simbolicas.py
  routes/
  utils/
    derivaciones.py
frontend/
  templates/index.html
  static/css/global.css
  static/js/modelos.js
  static/js/main.js
docs/
  documentacion_python.md
  documentacion_sympy.md
  autorizacion_profesor.md
tests/
  test_modelos.py
run.py
```

## Autoría y autorización

Desarrollado por **Edwin Bolaños**.

Se autoriza al profesor **Tito Amauryt** para publicar, usar, adaptar, presentar, explicar, enseñar y distribuir este proyecto con fines académicos, pedagógicos e institucionales.

## Cookies y almacenamiento local

La aplicación no usa cookies de seguimiento. Solo utiliza `localStorage` para recordar el aviso legal aceptado por el usuario.

