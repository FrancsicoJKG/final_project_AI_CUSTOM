"""Modulo CAG: aplica el contexto persistente del usuario a la respuesta base.

Devuelve un dict {"answer", "context_used"} en lugar de solo texto:
el modulo que aplica el contexto es el que sabe que keys aplico, y asi
assistant.py no duplica esa logica (separacion de responsabilidades).
"""


def apply_context(user_id, question, base_answer, context_items):
    if not context_items:
        return {"answer": base_answer, "context_used": []}

    notes = "; ".join(
        f"{item['key']}: {item['value']}" for item in context_items
    )
    answer = f"{base_answer} Tomando en cuenta tu contexto ({notes})."

    return {
        "answer": answer,
        "context_used": [item["key"] for item in context_items],
    }
