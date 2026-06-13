"""Pruebas propias del ContextStore (TDD: escritas antes de implementar).

Decisiones de diseño que estas pruebas fijan:
- Persistencia en JSON con threading.Lock (server es ThreadingHTTPServer).
- Formato de item: {"key": ..., "value": ...} exacto (lo exige el contrato).
- Key duplicada: SOBRESCRIBE el valor (el contexto refleja la preferencia mas reciente).
- Usuario sin contexto: lista vacia, no error.
- user_id o key vacios: ValueError.
"""

import json
import tempfile
import threading
import unittest
from pathlib import Path

from backend.context_store import ContextStore


class ContextStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.tmpdir.name) / "context.json"
        self.store = ContextStore(storage_path=self.storage_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_save_returns_truthy_and_persists_to_disk(self):
        result = self.store.save("ana", "preferred_style", "analogias")

        self.assertTrue(result)
        on_disk = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self.assertIn("ana", on_disk)

    def test_list_for_user_returns_exact_contract_format(self):
        self.store.save("ana", "project", "monolito moderno")

        items = self.store.list_for_user("ana")

        self.assertEqual(items, [{"key": "project", "value": "monolito moderno"}])

    def test_user_without_context_gets_empty_list(self):
        self.assertEqual(self.store.list_for_user("nadie"), [])

    def test_duplicate_key_overwrites_value(self):
        self.store.save("luis", "audience", "experto")
        self.store.save("luis", "audience", "principiante")

        items = self.store.list_for_user("luis")

        self.assertEqual(items, [{"key": "audience", "value": "principiante"}])

    def test_context_is_isolated_per_user(self):
        self.store.save("ana", "k", "valor de ana")
        self.store.save("luis", "k", "valor de luis")

        self.assertEqual(self.store.list_for_user("ana"), [{"key": "k", "value": "valor de ana"}])
        self.assertEqual(self.store.list_for_user("luis"), [{"key": "k", "value": "valor de luis"}])

    def test_persistence_survives_new_instance(self):
        self.store.save("ana", "tema", "redes")

        reloaded = ContextStore(storage_path=self.storage_path)

        self.assertEqual(reloaded.list_for_user("ana"), [{"key": "tema", "value": "redes"}])

    def test_empty_user_or_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.store.save("", "k", "v")
        with self.assertRaises(ValueError):
            self.store.save("ana", "", "v")

    def test_concurrent_saves_do_not_corrupt_file(self):
        def worker(i):
            self.store.save(f"user-{i % 3}", f"key-{i}", f"value-{i}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(30)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # El archivo debe seguir siendo JSON valido y contener los 30 registros
        on_disk = json.loads(self.storage_path.read_text(encoding="utf-8"))
        total = sum(len(items) for items in on_disk.values())
        self.assertEqual(total, 30)


class ApplyContextTest(unittest.TestCase):
    def test_returns_base_answer_when_no_context(self):
        from backend.cag import apply_context

        result = apply_context("ana", "Que es CAG?", "respuesta base", [])

        self.assertEqual(result["answer"], "respuesta base")
        self.assertEqual(result["context_used"], [])

    def test_incorporates_values_and_reports_keys(self):
        from backend.cag import apply_context

        result = apply_context(
            "luis",
            "Que es CAG?",
            "respuesta base",
            [{"key": "audience", "value": "explicar como principiante"}],
        )

        self.assertIn("principiante", result["answer"].lower())
        self.assertIn("audience", result["context_used"])


if __name__ == "__main__":
    unittest.main()
