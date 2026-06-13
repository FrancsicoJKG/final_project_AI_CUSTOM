# Examen Final — Integración de módulo CAG (Context-Augmented Generation)

**Curso:** Inteligencia Artificial — Universidad Mariano Gálvez de Guatemala
**Estudiante:** Francisco Jacob Martínez Díaz — Carné 9989-22-18777
**Fork:** [https://github.com/FrancsicoJKG/final_project_AI_CUSTOM.git]
**Repositorio base:** https://github.com/rortizs/final_project_AI_CUSTOM.git

---

## 1. Planteamiento del problema

El proyecto base es un asistente monolítico (frontend HTML/JS + backend Python
sin frameworks) que responde preguntas del curso mediante recuperación tipo RAG
sobre una base documental pequeña (`data/knowledge_base.json`). Su limitación:
**no conserva contexto persistente del usuario** — responde igual a todos y
olvida todo entre sesiones. Guardar o consultar contexto devolvía error 501
(`NotImplementedError`).

Este trabajo integra un módulo **CAG (Context-Augmented Generation)** que
guarda, recupera y utiliza contexto por usuario para mejorar respuestas
posteriores, cumpliendo el contrato oficial de validación sin romper las
pruebas base ni la arquitectura original.

## 2. Arquitectura de la solución (RAG + CAG)

```
POST /api/ask {user_id, question}
        │
        ▼
assistant.answer_question()          ← orquestador
        │
        ├── knowledge.retrieve_snippets()      [RAG: ya existía]
        │       └── data/knowledge_base.json
        │
        ├── context_store.list_for_user()      [CAG: implementado]
        │       └── data/context_store.json    (persistencia en disco)
        │
        └── cag.apply_context()                [CAG: implementado]
                └── respuesta enriquecida + context_used
```

Separación de responsabilidades:

| Módulo | Responsabilidad |
|---|---|
| `backend/knowledge.py` | Recuperación documental (RAG). Sin cambios. |
| `backend/context_store.py` | Persistencia del contexto por usuario (JSON + Lock). |
| `backend/cag.py` | Aplicar el contexto a la respuesta base y reportar las keys usadas. |
| `backend/assistant.py` | Orquestar RAG + CAG. Degrada al comportamiento base si no hay contexto. |
| `backend/server.py` | Rutas HTTP. Un solo cambio: pasa el `context_store` a `answer_question`. |

## 3. Decisiones de diseño

1. **Persistencia con JSON + `threading.Lock`.** El enunciado exige contexto
   *persistente* (descarta un dict en memoria) y el server es
   `ThreadingHTTPServer`, que atiende requests en hilos concurrentes: el lock
   protege el ciclo completo leer-modificar-escribir. SQLite se evaluó y se
   descartó por sobre-ingeniería para un almacén key/value por usuario.
   La decisión se respalda con una prueba de concurrencia de 30 hilos.

2. **Key duplicada sobrescribe.** El contexto representa la preferencia
   *actual* del usuario: si cambia `audience` de "experto" a "principiante",
   las respuestas usan lo más reciente. Verificado por prueba propia y
   escenario BDD.

3. **`apply_context` devuelve `{"answer", "context_used"}`.** El módulo que
   aplica el contexto es el que sabe qué keys aplicó; devolver solo texto
   obligaría al assistant a duplicar esa lógica.

4. **`storage_path` parametrizable** en `ContextStore`: las pruebas usan
   archivos temporales y el server usa `data/context_store.json`, sin tocar
   el código del server (que instancia `ContextStore()` sin argumentos).

## 4. Cómo ejecutar el proyecto

Requisitos: Python 3.10+ (probado con 3.14). Sin dependencias para el runtime;
`behave` solo para los escenarios BDD.

```bash
# Backend (desde la raíz del proyecto)
PYTHONPATH=. python3 -m backend.server
# → Backend running at http://127.0.0.1:8000

# Frontend: abrir frontend/index.html en el navegador
```

Nota: `http://127.0.0.1:8000/` responde `{"error": "not found"}` porque el
backend es una API sin ruta raíz; sus endpoints son `/health`, `/api/ask` y
`/api/context`. La interfaz es `frontend/index.html`.

### API

```bash
# Guardar contexto
curl -X POST http://127.0.0.1:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student-01", "key": "audience", "value": "explicar como principiante"}'

# Consultar contexto
curl "http://127.0.0.1:8000/api/context?user_id=student-01"

# Preguntar (la respuesta incorpora el contexto guardado)
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student-01", "question": "¿Qué es CAG?"}'
```

## 5. Pruebas (TDD + BDD)

```bash
# 1) Pruebas base del profesor (deben pasar sin modificaciones): 3/3
./scripts/run_base_tests.sh

# 2) Pruebas propias (TDD, escritas antes de implementar): 10/10
PYTHONPATH=. python3 -m unittest discover -s tests/own -p 'test_*.py'

# 3) Validación oficial del contrato CAG: 3/3
./scripts/validate_student_cag.sh

# 4) Escenarios BDD ejecutables (Gherkin + behave): 5 escenarios / 35 pasos
pip install behave
PYTHONPATH=. python3 -m behave features/
```

Proceso TDD seguido: la suite propia se escribió primero y se verificó en
**rojo** (10/10 errores contra el código base); la implementación se desarrolló
hasta dejarla en **verde** sin modificar las pruebas. Evidencias en
`docs/evidencias/`.

Los escenarios BDD (`docs/bdd/cag.feature`) se ejecutan de punta a punta:
`features/environment.py` levanta el backend real con un almacén temporal y
`features/steps/cag_steps.py` traduce cada paso Gherkin a llamadas HTTP.

Trazabilidad SDD→BDD→TDD: escenarios 1-3 ↔ `tests/validation/`;
escenarios 4-5 ↔ `tests/own/test_context_store.py`.

## 6. Estructura del repositorio

```
backend/            código fuente (RAG existente + CAG implementado)
frontend/           interfaz HTML/JS
data/               base de conocimiento + almacén de contexto (runtime)
tests/base/         pruebas base del profesor
tests/own/          pruebas propias (TDD)
tests/validation/   contrato oficial CAG
features/           BDD ejecutable (behave)
docs/bdd/           escenarios Gherkin
docs/scrum/         backlog, sprints, retrospectivas
docs/evidencias/    capturas del proceso y verificaciones
scripts/            runners de pruebas
PROMPTS.md          registro cronológico de uso de IA
README.md           este documento
```

## 7. Proceso y evidencias

- **Scrum:** 2 sprints documentados en `docs/scrum/SCRUM.md` (backlog,
  planificación, ejecución y cierre).
- **Pull Request:** `feature/cag-integration` → `main` del fork, con revisión
  y merge ([link al PR]).
- **Uso de IA:** registrado cronológicamente en `PROMPTS.md` bajo el modelo
  del curso (la IA asiste; el estudiante dirige, decide, verifica y explica).
- **Evidencias:** `docs/evidencias/` — pruebas base previas, TDD en rojo,
  suites en verde, demo del frontend con respuesta enriquecida, persistencia
  tras reinicio del server y ejecución de behave.

## 8. Demo rápida (flujo CAG completo)

1. Levantar el backend y abrir el frontend.
2. Guardar contexto para `student-01` (curl de la sección 4).
3. Preguntar "¿Qué es CAG?" → la respuesta incluye
   *"Tomando en cuenta tu contexto (audience: explicar como principiante)"*
   y `context_used: ["audience"]`; el Panel CAG muestra el contexto guardado.
4. Preguntar con otro usuario (`invitado-99`) → respuesta base sin contexto.
5. Reiniciar el server y repetir con `student-01` → el contexto persiste
   (vive en `data/context_store.json`, no en memoria).
