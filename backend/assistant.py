from backend.cag import apply_context
from backend.knowledge import retrieve_snippets


def answer_question(user_id, question, context_store=None):
    snippets = retrieve_snippets(question)

    if not snippets:
        base_answer = "No encontre informacion suficiente en la base de conocimiento del curso."
        sources = []
    else:
        source_text = " ".join(item["content"] for item in snippets)
        base_answer = f"Segun la base de conocimiento del curso: {source_text}"
        sources = [item["id"] for item in snippets]

    context_items = []
    if context_store is not None:
        try:
            context_items = context_store.list_for_user(user_id)
        except NotImplementedError:
            context_items = []

    enriched = apply_context(user_id, question, base_answer, context_items)

    return {
        "user_id": user_id,
        "answer": enriched["answer"],
        "sources": sources,
        "context_used": enriched["context_used"],
    }
