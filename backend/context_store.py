"""Almacenamiento persistente de contexto CAG.

Decisiones de diseno:
- Persistencia en JSON sobre disco: el enunciado exige contexto persistente.
- threading.Lock: el server es ThreadingHTTPServer, multiples requests pueden
  escribir a la vez; el lock protege el ciclo leer-modificar-escribir.
- Key duplicada sobrescribe: el contexto representa la preferencia ACTUAL del usuario.
- Formato de item {"key": ..., "value": ...}: contrato exigido por la validacion.
"""

import json
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORAGE_PATH = PROJECT_ROOT / "data" / "context_store.json"


class ContextStore:
    def __init__(self, storage_path=DEFAULT_STORAGE_PATH):
        self.storage_path = Path(storage_path)
        self._lock = threading.Lock()

    def save(self, user_id, key, value):
        if not user_id or not key:
            raise ValueError("user_id and key are required")

        with self._lock:
            data = self._read()
            items = data.setdefault(user_id, [])

            for item in items:
                if item["key"] == key:
                    item["value"] = value
                    break
            else:
                items.append({"key": key, "value": value})

            self._write(data)

        return True

    def list_for_user(self, user_id):
        with self._lock:
            data = self._read()
        return list(data.get(user_id, []))

    def _read(self):
        if not self.storage_path.exists():
            return {}
        raw = self.storage_path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)

    def _write(self, data):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
