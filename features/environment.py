"""Configuracion de behave: levanta el backend real en un hilo antes de los
escenarios y lo apaga al final. Usa un ContextStore con archivo temporal para
no contaminar data/context_store.json."""

import tempfile
import threading
from pathlib import Path

import backend.server as server_module
from backend.context_store import ContextStore
from backend.server import create_server


def before_all(context):
    context.tmpdir = tempfile.TemporaryDirectory()
    context.storage_path = Path(context.tmpdir.name) / "context.json"

    # Reemplaza el store global del server por uno con almacenamiento temporal
    server_module.context_store = ContextStore(storage_path=context.storage_path)

    context.server = create_server(port=0)
    context.port = context.server.server_address[1]
    context.base_url = f"http://127.0.0.1:{context.port}"

    context.thread = threading.Thread(target=context.server.serve_forever, daemon=True)
    context.thread.start()


def after_all(context):
    context.server.shutdown()
    context.server.server_close()
    context.tmpdir.cleanup()
