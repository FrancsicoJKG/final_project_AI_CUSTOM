"""Step definitions para features/cag.feature.

Cada paso del Gherkin se traduce en llamadas HTTP reales contra el backend
levantado por environment.py. Asi el feature se ejecuta de punta a punta.
"""

import json
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from behave import step

from backend.knowledge import load_knowledge_base


def _post(context, path, payload):
    request = Request(
        f"{context.base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = json.loads(error.read().decode("utf-8"))
        error.close()
        return error.code, body


def _get(context, path):
    try:
        with urlopen(f"{context.base_url}{path}", timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = json.loads(error.read().decode("utf-8"))
        error.close()
        return error.code, body


# --- Antecedentes ---

@step('que el backend está corriendo en http://127.0.0.1:8000')
def step_backend_running(context):
    status, body = _get(context, "/health")
    assert status == 200 and body["status"] == "ok"


@step('la base de conocimiento del curso está cargada')
def step_knowledge_loaded(context):
    assert len(load_knowledge_base()) > 0


# --- Acciones de contexto ---

@step('envío POST a /api/context con user_id "{user_id}", key "{key}" y value "{value}"')
def step_post_context(context, user_id, key, value):
    context.status, context.body = _post(
        context, "/api/context", {"user_id": user_id, "key": key, "value": value}
    )


@step('que el usuario "{user_id}" guardó la key "{key}" con value "{value}"')
def step_user_saved(context, user_id, key, value):
    status, _ = _post(
        context, "/api/context", {"user_id": user_id, "key": key, "value": value}
    )
    assert status == 201


@step('"{user_id}" guarda nuevamente la key "{key}" con value "{value}"')
def step_user_saves_again(context, user_id, key, value):
    context.status, context.body = _post(
        context, "/api/context", {"user_id": user_id, "key": key, "value": value}
    )


@step('consulto GET /api/context?user_id={user_id}')
def step_get_context(context, user_id):
    context.status, context.body = _get(
        context, f"/api/context?user_id={quote(user_id)}"
    )


@step('que el usuario "{user_id}" no tiene contexto guardado')
def step_user_without_context(context, user_id):
    status, body = _get(context, f"/api/context?user_id={quote(user_id)}")
    assert status == 200 and body["context"] == []


# --- Preguntas al asistente ---

@step('"{user_id}" pregunta "{question}" vía POST /api/ask')
def step_ask(context, user_id, question):
    context.status, context.body = _post(
        context, "/api/ask", {"user_id": user_id, "question": question}
    )


# --- Verificaciones ---

@step('la respuesta tiene código {code:d}')
def step_status_code(context, code):
    assert context.status == code, f"esperaba {code}, recibí {context.status}"


@step('el cuerpo contiene "saved" con valor verdadero')
def step_saved_true(context):
    assert context.body["saved"] is True


@step('el contexto queda persistido en disco en data/context_store.json')
def step_persisted_on_disk(context):
    on_disk = json.loads(context.storage_path.read_text(encoding="utf-8"))
    assert len(on_disk) > 0


@step('el campo "context" contiene el item con key "{key}" y value "{value}"')
def step_context_contains(context, key, value):
    assert {"key": key, "value": value} in context.body["context"]


@step('el contexto de "{user_id}" no incluye items de otros usuarios')
def step_context_isolated(context, user_id):
    _post(context, "/api/context",
          {"user_id": "otro-usuario", "key": "marcador", "value": "no debe filtrarse"})
    status, body = _get(context, f"/api/context?user_id={quote(user_id)}")
    assert {"key": "marcador", "value": "no debe filtrarse"} not in body["context"]


@step('el answer incluye el texto "{text}"')
def step_answer_includes(context, text):
    assert text.lower() in context.body["answer"].lower()


@step('el campo "context_used" incluye la key "{key}"')
def step_context_used_includes(context, key):
    assert key in context.body["context_used"]


@step('el campo "sources" sigue incluyendo los documentos recuperados por RAG')
def step_sources_present(context):
    assert len(context.body["sources"]) > 0


@step('el answer es la respuesta base de la base de conocimiento')
def step_answer_is_base(context):
    assert context.body["answer"].startswith("Segun la base de conocimiento")
    assert "Tomando en cuenta tu contexto" not in context.body["answer"]


@step('el campo "context_used" es una lista vacía')
def step_context_used_empty(context):
    assert context.body["context_used"] == []


@step('el campo "context" contiene exactamente un item con key "{key}"')
def step_exactly_one_key(context, key):
    matches = [i for i in context.body["context"] if i["key"] == key]
    assert len(matches) == 1, f"esperaba 1 item con key {key}, hay {len(matches)}"
    context.last_match = matches[0]


@step('su value es "{value}"')
def step_match_value(context, value):
    assert context.last_match["value"] == value
