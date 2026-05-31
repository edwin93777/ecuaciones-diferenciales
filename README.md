# Modelos de Ecuaciones Diferenciales

Aplicación web académica desarrollada con **Flask**, **Python** y **SymPy** para resolver y explicar modelos básicos de ecuaciones diferenciales de primer orden. El sistema está organizado por módulos matemáticos reutilizables, genera pasos de solución en formato LaTeX y permite evaluar casos con datos completos o conservar expresiones simbólicas cuando faltan datos del enunciado.

## Propósito del sistema

El objetivo principal es apoyar el estudio de ecuaciones diferenciales mediante una interfaz que no solo entrega un resultado numérico, sino que también muestra el modelo usado, la fórmula general, la inferencia de constantes, la evaluación simbólica y la justificación matemática del procedimiento.

La aplicación está pensada para ejercicios de crecimiento, decaimiento, enfriamiento, mezclas y Carbono-14. Cada módulo recibe datos desde formularios dinámicos, procesa la información en el backend y devuelve una respuesta estructurada para mostrar fórmulas, pasos y resultados en pantalla.

## Tecnologías principales

| Tecnología | Uso dentro del sistema |
|---|---|
| Python | Lenguaje principal del backend. |
| Flask | Servidor web, rutas HTTP y renderizado inicial de la interfaz. |
| SymPy | Construcción simbólica de fórmulas, expresiones, derivadas, simplificaciones y salida LaTeX. |
| MathJax | Renderizado visual de fórmulas LaTeX en el navegador. |
| JavaScript | Manejo dinámico de módulos, formularios, peticiones y resultados. |
| CSS | Diseño visual responsivo de la interfaz. |
| Gunicorn | Servidor WSGI usado para producción en Render. |

## Módulos matemáticos

### Crecimiento

Incluye modelos donde una magnitud aumenta de acuerdo con una tasa proporcional o con una entrada externa controlada.

- Crecimiento proporcional.
- Interés continuo.
- Crecimiento con entrada constante.
- Caída con resistencia del aire.

### Decaimiento

Resuelve situaciones donde una cantidad disminuye proporcionalmente a su valor actual.

- Decaimiento radiactivo.
- Absorción o eliminación de medicamento.
- Descarga de capacitor.
- Atenuación de intensidad de luz.

### Enfriamiento por Ley de Newton

Modela la temperatura de un cuerpo que se acerca a la temperatura ambiente.

- Enfriamiento hacia el ambiente.
- Calentamiento hacia el ambiente.
- Inferencia de la constante `k` desde una medición conocida.
- Evaluación de temperatura en un tiempo dado.
- Cálculo del tiempo necesario para alcanzar una temperatura objetivo.

### Mezclas

Modela tanques con entrada y salida de líquido, usando balance de soluto.

- Mezcla con volumen constante.
- Mezcla con volumen variable.
- Concentración de entrada.
- Concentración de salida fija cuando el enunciado la define.
- Cantidad de soluto, concentración y valor límite.

### Carbono-14

Módulo especializado para datación por vida media.

- Modelo diferencial `dM/dt = -kM`.
- Vida media por defecto de `5730` años.
- Cantidad restante en un tiempo determinado.
- Porcentaje restante en un tiempo determinado.
- Edad de una muestra desde porcentaje restante.
- Edad de una muestra desde cantidad inicial y cantidad restante.
- Función simbólica general `M(t)=M0e^(-kt)`.

## Documentación interna en la interfaz

El sistema incluye módulos de documentación visibles desde el menú principal.

### Python

Describe la organización del backend, las rutas Flask, los modelos, las validaciones y el formato de respuestas JSON.

### SymPy

Explica el motor simbólico usado por el sistema. Incluye fragmentos internos de código para crecimiento, decaimiento, Newton, mezclas, derivaciones y Carbono-14. Los fragmentos resaltan funciones y operaciones de SymPy como:

- `sp.Symbol` y `sp.symbols`.
- `sp.Float`.
- `sp.exp`.
- `sp.log`.
- `sp.diff`.
- `sp.Eq`.
- `sp.simplify`.
- `sp.latex`.
- `.subs`.
- `sp.N`.
- Operadores simbólicos como `*`, `/` y `**`.

## Arquitectura del proyecto

```text
backend/
  app.py
  modelos/
    carbono14.py
    crecimiento.py
    decaimiento.py
    enfriamiento.py
    formulas_simbolicas.py
    mezclas.py
  routes/
    carbono14_routes.py
    crecimiento_routes.py
    decaimiento_routes.py
    enfriamiento_routes.py
    mezclas_routes.py
  utils/
    derivaciones.py
    formato.py
    respuesta.py
    simbolico.py
    validacion.py
frontend/
  templates/
    index.html
  static/
    css/
      global.css
    js/
      main.js
      modelos.js
docs/
  autorizacion_profesor.md
  documentacion_python.md
  documentacion_sympy.md
  objetivo_modelos.md
run.py
requirements.txt
render.yaml
Procfile
.python-version
```

## Flujo de funcionamiento

1. El usuario selecciona un módulo matemático en la interfaz.
2. El navegador construye el formulario correspondiente a la variante elegida.
3. JavaScript envía los datos al backend mediante rutas relativas como `/resolver/crecimiento`, `/resolver/mezclas` o `/resolver/carbono14`.
4. Flask recibe la petición y la delega al modelo matemático correspondiente.
5. El modelo valida datos, construye expresiones con SymPy, calcula constantes cuando es posible y genera pasos en LaTeX.
6. El backend devuelve una respuesta JSON homogénea.
7. El frontend muestra resultado, constantes, advertencias, fórmulas y procedimiento paso a paso.

## Rutas principales

| Ruta | Método | Función |
|---|---:|---|
| `/` | GET | Muestra la aplicación web. |
| `/salud` | GET | Devuelve el estado básico del servicio. |
| `/resolver/crecimiento` | POST | Resuelve modelos de crecimiento. |
| `/resolver/decaimiento` | POST | Resuelve modelos de decaimiento. |
| `/resolver/enfriamiento` | POST | Resuelve modelos de Ley de Newton. |
| `/resolver/mezclas` | POST | Resuelve modelos de mezclas. |
| `/resolver/carbono14` | POST | Resuelve el modelo de Carbono-14. |

## Ejecución local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

En sistemas Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Despliegue en Render

El proyecto queda preparado para ejecutarse en Render como servicio web Python. La aplicación no depende de direcciones del equipo local; el frontend consume rutas relativas del mismo dominio donde se publique el backend.

```text
Build command: pip install -r requirements.txt
Start command: gunicorn run:app
```

La versión de Python se define en `.python-version` y también en `render.yaml` mediante `PYTHON_VERSION`.

## Autoría y autorización académica

Desarrollado por **Edwin Bolaños**.

El proyecto incluye autorización académica para que el profesor **Tito Amauryt** pueda usar, presentar, adaptar, modificar, explicar, enseñar, compartir y distribuir el sistema con fines pedagógicos e institucionales.

## Almacenamiento del navegador

La aplicación no utiliza cookies de seguimiento. Solo usa `localStorage` para recordar la aceptación del aviso legal mostrado en la interfaz.
