# Documentación Scrum — Examen Final: Integración CAG

Equipo: Francisco Jacob Martínez Díaz (Product Owner + Developer).
Marco de trabajo: Scrum adaptado a equipo de una persona, 2 sprints cortos.

---

## Product Backlog

| ID | Historia de usuario | Prioridad | Sprint |
|----|---------------------|-----------|--------|
| HU-01 | Como evaluador, quiero que las pruebas base pasen sin modificaciones, para garantizar que el proyecto base no se rompió. | Alta | 1 |
| HU-02 | Como desarrollador, quiero un análisis de la arquitectura y del contrato de validación, para decidir el diseño del módulo CAG con fundamento. | Alta | 1 |
| HU-03 | Como usuario del asistente, quiero guardar contexto personal (key/value), para que el sistema recuerde mis preferencias. | Alta | 1 |
| HU-04 | Como usuario del asistente, quiero consultar mi contexto guardado, para verificar qué recuerda el sistema de mí. | Alta | 1 |
| HU-05 | Como usuario del asistente, quiero que mis preguntas se respondan tomando en cuenta mi contexto, para recibir respuestas adaptadas. | Alta | 2 |
| HU-06 | Como evaluador, quiero escenarios BDD y pruebas propias TDD, para verificar el comportamiento del módulo CAG. | Alta | 1-2 |
| HU-07 | Como evaluador, quiero documentación final (README, PROMPTS, evidencias) y un PR revisado, para auditar el proceso. | Media | 2 |

---

## Sprint 1 — Análisis, diseño y almacenamiento de contexto

**Objetivo del sprint:** Tener el `ContextStore` implementado con persistencia real,
respaldado por pruebas propias escritas primero (TDD), sin romper las pruebas base.

**Planificación (Sprint Planning):**
- Ejecutar pruebas base y confirmar 3/3 (HU-01).
- Analizar arquitectura y contrato de validación; decidir persistencia (HU-02).
  - Decisión tomada: JSON + threading.Lock. Justificación en PROMPTS.md, Entrada 1.
- Escribir suite TDD de `ContextStore` y verificar rojo (HU-06).
- Implementar `ContextStore` hasta verde (HU-03, HU-04).

**Ejecución:**
- [12/06] Pruebas base: 3/3 OK antes de modificar (evidencia: `docs/evidencias/[...]`).
- [12/06] Análisis de puntos de inserción: `context_store.py`, `cag.py`, `assistant.py`.
- [12/06] Suite propia creada: 10 pruebas, todas en rojo contra el código base.
- [12/06] `ContextStore` implementado (JSON + Lock, key duplicada sobrescribe).

**Cierre (Sprint Review / Retro):**
- Completado: HU-01, HU-02, HU-03, HU-04 y la parte TDD de HU-06.
- Lo que funcionó: escribir los tests primero fijó el contrato y evitó retrabajos;
  el formato exacto `{"key","value"}` lo dictaron los tests de validación.
- A mejorar: [completar con tu experiencia real, ej. tiempos, entorno Windows/Git Bash].

---

## Sprint 2 — Integración CAG, BDD y cierre del proceso

**Objetivo del sprint:** Conectar el contexto al flujo de respuestas (RAG+CAG),
validar el contrato oficial, completar artefactos BDD y documentación final.

**Planificación (Sprint Planning):**
- Implementar `apply_context` y cablear `assistant.py`/`server.py` (HU-05).
- Pasar la validación oficial `validate_student_cag.sh` (HU-05).
- Redactar escenarios Gherkin con trazabilidad a las pruebas (HU-06).
- Demo en frontend con evidencias; README, PROMPTS.md, PR y merge (HU-07).

**Ejecución:**
- [12/06] `apply_context` devuelve `{"answer","context_used"}`; `assistant.py` orquesta
  RAG + CAG con degradación segura si no hay contexto.
- [12/06] Tres suites en verde: own 10/10, base 3/3, validación 3/3.
- [12/06] Demo frontend: contexto guardado, answer enriquecido, `context_used` poblado
  (evidencia: `docs/evidencias/demo-cag-respuesta-enriquecida.png`).
- [12/06] BDD: 5 escenarios en `docs/bdd/cag.feature` (3 del contrato + 2 de diseño).
- [fecha] PR `feature/cag-integration` → main: revisión y merge (evidencias: `[...]`).

**Cierre (Sprint Review / Retro):**
- Completado: HU-05, HU-06, HU-07.
- Lo que funcionó: [completar].
- A mejorar: [completar].

---

## Definición de Hecho (DoD)

Una historia se considera terminada cuando: las pruebas base siguen en verde,
las pruebas propias relacionadas pasan, la validación oficial pasa (si aplica),
el cambio está commiteado con mensaje descriptivo y la evidencia está capturada
en `docs/evidencias/` cuando corresponde.
