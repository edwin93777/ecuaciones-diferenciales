"""Aplicación Flask para modelos de ecuaciones diferenciales desplegable en Render."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template
from backend.routes.crecimiento_routes import crecimiento_bp
from backend.routes.decaimiento_routes import decaimiento_bp
from backend.routes.enfriamiento_routes import enfriamiento_bp
from backend.routes.mezclas_routes import mezclas_bp

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"


def crear_app() -> Flask:
    """Crea la aplicación usando rutas relativas compatibles con Render."""
    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
    )
    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.get("/salud")
    def salud():
        return {
            "estado": "ok",
            "modo": "produccion_render",
            "modulos": ["crecimiento", "decaimiento", "enfriamiento", "mezclas", "python", "sympy", "autorizacion"],
            "objetivo": "montar modelos y variantes, incluir fórmulas simbólicas con datos incompletos y documentación técnica",
        }, 200

    app.register_blueprint(crecimiento_bp)
    app.register_blueprint(decaimiento_bp)
    app.register_blueprint(enfriamiento_bp)
    app.register_blueprint(mezclas_bp)

    return app


app = crear_app()


if __name__ == "__main__":
    import os
    puerto = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto, debug=False)
