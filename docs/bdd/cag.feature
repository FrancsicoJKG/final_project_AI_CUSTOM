# language: es
Característica: Memoria contextual persistente (CAG)
  Como estudiante del curso
  Quiero que el asistente guarde y use mi contexto personal
  Para recibir respuestas adaptadas a mis preferencias en consultas futuras

  Antecedentes:
    Dado que el backend está corriendo en http://127.0.0.1:8000
    Y la base de conocimiento del curso está cargada

  Escenario: Guardar contexto de un usuario
    Cuando envío POST a /api/context con user_id "ana", key "preferred_style" y value "explicaciones con analogias"
    Entonces la respuesta tiene código 201
    Y el cuerpo contiene "saved" con valor verdadero
    Y el contexto queda persistido en disco en data/context_store.json

  Escenario: Recuperar el contexto guardado de un usuario
    Dado que el usuario "ana" guardó la key "project" con value "usa arquitectura monolitica moderna"
    Cuando consulto GET /api/context?user_id=ana
    Entonces la respuesta tiene código 200
    Y el campo "context" contiene el item con key "project" y value "usa arquitectura monolitica moderna"
    Y el contexto de "ana" no incluye items de otros usuarios

  Escenario: El contexto influye en una respuesta posterior
    Dado que el usuario "luis" guardó la key "audience" con value "explicar como principiante"
    Cuando "luis" pregunta "¿Qué es CAG?" vía POST /api/ask
    Entonces la respuesta tiene código 200
    Y el answer incluye el texto "principiante"
    Y el campo "context_used" incluye la key "audience"
    Y el campo "sources" sigue incluyendo los documentos recuperados por RAG

  Escenario: Usuario sin contexto recibe la respuesta base sin alteraciones
    Dado que el usuario "nuevo-01" no tiene contexto guardado
    Cuando "nuevo-01" pregunta "¿Qué es RAG?" vía POST /api/ask
    Entonces la respuesta tiene código 200
    Y el answer es la respuesta base de la base de conocimiento
    Y el campo "context_used" es una lista vacía

  Escenario: Una key duplicada actualiza la preferencia del usuario
    Dado que el usuario "ana" guardó la key "audience" con value "experto"
    Cuando "ana" guarda nuevamente la key "audience" con value "principiante"
    Y consulto GET /api/context?user_id=ana
    Entonces el campo "context" contiene exactamente un item con key "audience"
    Y su value es "principiante"
