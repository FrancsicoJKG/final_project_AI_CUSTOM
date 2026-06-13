# PROMPTS.md — Registro cronológico de uso de IA

Herramienta utilizada: Claude (Anthropic). Modelo de trabajo del curso: la IA asiste,
el estudiante dirige, decide, verifica y explica. Cada entrada documenta un intercambio
real; las capturas correspondientes están en `docs/evidencias/`.

---

## Entrada 1 — Análisis de la arquitectura y ubicación del módulo CAG

- **Fecha:** 12/06/2026
- **Objetivo del prompt:** Entender dónde insertar el módulo CAG en el proyecto base
  y qué comportamientos exactos exige el contrato de validación, antes de escribir código.
- **Prompt usado (resumen):** Pedí análisis del proyecto base (backend, frontend, tests)
  y del contrato `test_cag_contract.py`, indicando que la decisión de diseño la tomaría yo.
- **Respuesta recibida (resumen):** La IA identificó los tres puntos de inserción
  (`context_store.py`, `cag.py` y el cableado faltante en `assistant.py`), extrajo el
  contrato exacto de los tests de validación (formato `{"key","value"}`, código 201,
  `context_used` con las keys) y me presentó tres opciones de persistencia con pros y
  contras: dict en memoria, JSON+Lock y SQLite.
- **Decisión humana:** Elegí **JSON + threading.Lock** porque el enunciado exige contexto
  persistente (descarta memoria), el server es `ThreadingHTTPServer` (requiere protección
  contra escrituras concurrentes) y SQLite era sobre-ingeniería para un key/value por usuario.
- **Cambios en el proyecto:** Ninguno todavía (fase de análisis).
- **Verificación aplicada:** Ejecuté las pruebas base antes de modificar: 3/3 OK
  (captura: `docs/evidencias/[nombre].png`).

---

## Entrada 2 — TDD: suite de pruebas propias en rojo

- **Fecha:** 12/06/2026
- **Objetivo del prompt:** Obtener una suite de pruebas propias para `ContextStore` y
  `apply_context` que fijara el contrato ANTES de implementar (TDD).
- **Prompt usado (resumen):** Confirmé la decisión JSON+Lock y pedí los tests primero.
- **Respuesta recibida (resumen):** 10 pruebas en `tests/own/test_context_store.py`
  cubriendo: contrato exacto del formato, persistencia en disco, aislamiento por usuario,
  key duplicada, usuario sin contexto, validación de entradas y concurrencia (30 hilos).
  La IA propuso dos decisiones de diseño y me pidió confirmarlas o rechazarlas.
- **Decisión humana:** Confirmé que (a) una key duplicada **sobrescribe** el valor
  (el contexto representa la preferencia actual del usuario) y (b) `apply_context`
  devuelve un dict `{"answer","context_used"}` para no duplicar lógica en el assistant.
- **Cambios en el proyecto:** Creé `tests/own/` y agregué la suite.
- **Verificación aplicada:** Ejecuté la suite contra el código base en mi máquina:
  **10/10 en rojo** (`TypeError` / `NotImplementedError`), como exige TDD
  (captura: `docs/evidencias/[nombre].png`). Commit: `[hash]`.

---

## Entrada 3 — Implementación hasta el verde

- **Fecha:** 12/06/2026
- **Objetivo del prompt:** Implementar `ContextStore`, `apply_context` y el cableado
  en `assistant.py`/`server.py` hasta que pasaran las tres suites.
- **Prompt usado (resumen):** Compartí la salida del rojo reproducida localmente y
  pedí la implementación según las decisiones confirmadas.
- **Respuesta recibida (resumen):** Implementación de los 4 archivos con justificación
  de cada decisión: lock sobre el ciclo leer-modificar-escribir, `storage_path`
  parametrizable (tests usan archivo temporal, server usa el real), degradación al
  comportamiento base si no hay contexto, y cambio de una sola línea en `server.py`.
- **Decisión humana:** Revisé el código antes de copiarlo; verifiqué que `server.py`
  solo cambiara una línea y que las pruebas base no se modificaran. [Agregar aquí
  cualquier ajuste propio que hayas hecho.]
- **Cambios en el proyecto:** `backend/context_store.py`, `backend/cag.py`,
  `backend/assistant.py`, `backend/server.py`. Commits incrementales: `[hashes]`.
- **Verificación aplicada:** Tres suites en verde en mi máquina: own 10/10,
  base 3/3, validación oficial 3/3 (capturas en `docs/evidencias/`). Probé el flujo
  completo en el frontend: guardé contexto vía `curl`, pregunté "¿Qué es CAG?" y
  obtuve el answer enriquecido con `context_used: ["audience"]`
  (captura: `docs/evidencias/demo-cag-respuesta-enriquecida.png`).

---

## Entrada 4 — Escenarios BDD

- **Fecha:** 12/06/2026
- **Objetivo del prompt:** Generar el borrador de escenarios Gherkin a partir del
  contrato de validación y de mis decisiones de diseño.
- **Prompt usado (resumen):** Pedí los escenarios BDD indicando que yo los revisaría
  y ajustaría antes de incorporarlos.
- **Respuesta recibida (resumen):** 5 escenarios en `docs/bdd/cag.feature`: los 3 del
  contrato (guardar, recuperar, influir) más 2 derivados de mis decisiones (usuario
  sin contexto y key duplicada que actualiza).
- **Decisión humana:** [Describir tu revisión: qué ajustaste, qué validaste, o por qué
  los aceptaste tal cual. Hacé al menos un cambio de redacción propio.]
- **Cambios en el proyecto:** `docs/bdd/cag.feature`. Commit: `[hash]`.
- **Verificación aplicada:** Trazabilidad BDD→TDD: los escenarios 1-3 se verifican con
  `scripts/validate_student_cag.sh` y los escenarios 4-5 con `tests/own/test_context_store.py`.

---

## Entrada 5 — [Pull Request / revisión final]

- **Fecha:** [fecha]
- **Objetivo del prompt:** [ej. revisión del PR como si fuera el profesor]
- **Prompt usado:** [...]
- **Respuesta recibida:** [...]
- **Decisión humana:** [...]
- **Cambios en el proyecto:** [...]
- **Verificación aplicada:** [...]
