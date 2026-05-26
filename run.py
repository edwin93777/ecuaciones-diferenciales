from __future__ import annotations

import os

from backend.app import crear_app

app = crear_app()


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", "5000"))
    modo_debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=puerto, debug=modo_debug)
