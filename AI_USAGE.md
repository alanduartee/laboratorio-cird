# AI Usage Log — Diplomado IA (LegacyPay & Proyecto Final)

Este documento registra la trazabilidad completa y la auditoría humana aplicada a cada artefacto de especificación, arquitectura, código, evaluación y gobernanza generado con la asistencia de Inteligencia Artificial a lo largo de todo el diplomado.

---

## Entrada 1 · 21-jul-2026 · Documento de Requisitos del Producto (PRD)

**Objetivo:** Generar un primer borrador de PRD para la funcionalidad de Historial de Transacciones de LegacyPay.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Prompt 1 estructurado con hechos aprobados (LegacyPay como pasarela B2B, rango de 90 días, filtros por fecha, estado y monto, paginación obligatoria, prohibición de exponer PAN completo o CVV, datos sintéticos).

**Salida obtenida:** 
- Archivo `PRD_v1.md` estructurado con Visión, Alcance, Usuarios, Entidades, Historias de Usuario (HU-01) y Preguntas Abiertas.

**Problema detectado:** 
1. **Alucinación de alcance:** La IA incluyó la exportación de resultados a archivos CSV (CA-01.4 en v1) como un criterio de aceptación del alcance actual.
2. **Sobre-diseño de entidades:** La IA incluyó "Filtro" como una entidad del dominio en la sección de datos.

**Cambio realizado por mí:** 
1. Eliminé la exportación a CSV de las historias de usuario y la moví explícitamente a la sección "Fuera de Alcance" en `PRD.md`.
2. Eliminé "Filtro" de la lista de entidades de base de datos, aclarando que se trata de parámetros de consulta de la petición HTTP.
3. Formateé las preguntas abiertas y explicité los supuestos de negocio.

**Evidencia o criterio utilizado:** 
- El pedido de negocio de LegacyPay especifica únicamente la consulta paginada en pantalla con filtros mínimos. La exportación externa requiere infraestructura y decisiones no aprobadas en la v1.

**Pregunta todavía abierta:** 
- ¿Existen roles diferenciados dentro del comercio (ej. Operador vs Administrador) con permisos de lectura restringidos?

---

## Entrada 2 · 21-jul-2026 · Modelo Entidad-Relación (ERD)

**Objetivo:** Generar un modelo entidad-relación lógico simplificado en formato Mermaid a partir de `PRD.md`.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Prompt 2 con restricciones de no convertir sustantivos simples en tablas, no incluir PAN completo ni CVV, e incluir supuestos explícitos.

**Salida obtenida:** 
- Diagrama Mermaid inicial propuesto en `erd.md` con entidades `COMERCIO`, `TRANSACCION`, `ESTADO_TRANSACCION` y `EXPORTACION`.

**Problema detectado:** 
1. **Entidad fuera de alcance:** La IA generó la tabla `EXPORTACION` derivándola de la alucinación previa del PRD_v1.
2. **Normalización excesiva:** La IA aisló el estado en la tabla `ESTADO_TRANSACCION`, agregando complejidad innecesaria para un atributo enumerable simple.

**Cambio realizado por mí:** 
1. Eliminé por completo la entidad `EXPORTACION`.
2. Convertí `estado_transaccion` en un atributo tipo cadena/enum dentro de la tabla `TRANSACCION`.
3. Verifiqué que solo se exponga `masked_pan` y redacté los supuestos de cardinalidad `1:N`.

**Evidencia o criterio utilizado:** 
- El principio de diseño ágil y las instrucciones del prompt prohíben sobre-diseños de base de datos para funcionalidades básicas de consulta filtrada.

**Pregunta todavía abierta:** 
- ¿Se requiere una entidad separada para el manejo de reembolsos/devoluciones o se tratarán como un estado de transacción en la v1?

---

## Entrada 3 · 21-jul-2026 · Diagrama de Secuencia

**Objetivo:** Generar el diagrama de secuencia Mermaid para la consulta paginada de historial de transacciones basada en `PRD.md` (HU-01).

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Prompt 3 con lista explícita de participantes (Comercio, API, Auth, Service, DB), exigencia de flujo feliz, consulta paginada y al menos un flujo alternativo de error.

**Salida obtenida:** 
- Diagrama Mermaid inicial propuesto en `sequence_historial.md` con flujo síncrono lineal sin validación explícita de seguridad previa.

**Problema detectado:** 
1. **Omisión de componente de seguridad:** La IA conectó la API directamente con el servicio de base de datos sin consultar al componente de `Autorización`.
2. **Falta de flujos de excepción:** El modelo únicamente graficó el camino feliz (200 OK), ignorando la validación del límite de 90 días.

**Cambio realizado por mí:** 
1. Reordené el diagrama para incluir el `Servicio de Autorización` como paso obligatorio antes de consultar el servicio de dominio.
2. Agregué los bloques alternativos (`alt / else`) para capturar las respuestas de error HTTP 401 (token inválido) y HTTP 400 (exceso del rango de 90 días).
3. Aseguré que los nombres de los atributos retornados coincidan con el modelo `erd.md`.

**Evidencia o criterio utilizado:** 
- Principio de Arquitectura Segura (Security by Design) y la regla RN-01 definida en `PRD.md`.

**Pregunta todavía abierta:** 
- ¿Cuál es la estrategia de manejo de timeouts cuando la base de datos tarda en responder consultas con filtros amplios?

---

## Entrada 4 · 21-jul-2026 · Registro de Decisión de Arquitectura (ADR)

**Objetivo:** Elaborar el borrador del ADR 0001 para seleccionar la estrategia de paginación del historial de transacciones en LegacyPay.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Prompt 4 con la restricción explícita de no inventar SLAs ni benchmarks no aprobados y evaluar alternativas bajo criterios de rendimiento, facilidad de implementación, UX y costo de cambio.

**Salida obtenida:** 
- Borrador inicial en `0001-paginacion.md` recomendando Keyset Pagination e inventando un SLA de respuesta menor a 50 ms y benchmarks no realizados.

**Problema detectado:** 
1. **Alucinación de métricas:** La IA inventó métricas de rendimiento y SLAs que no fueron aprobados ni probados en el proyecto.
2. **Subestimación de fricción B2B:** El modelo priorizó la teoría de rendimiento sobre la usabilidad e integración práctica para los comercios en la v1.

**Cambio realizado por mí:** 
1. Eliminé todos los benchmarks e inventos de SLA.
2. Cambié la decisión propuesta a **Paginación Basada en Offset** acotada a `page_size = 100` por facilidad de integración B2B y acotamiento a 90 días.
3. Explicité las consecuencias negativas honestas (posible degradación en páginas muy profundas) y añadí la sección de "Evidencia Pendiente" (pruebas de carga) y las condiciones de revisión.

**Evidencia o criterio utilizado:** 
- Estándares del formato ADR profesional y la restricción explícita del prompt de no asumir SLAs sin evidencia previa.

**Pregunta todavía abierta:** 
- ¿Qué porcentaje de consultas efectivas de los comercios llegan a requerir una paginación superior a la página 50?

---

## Entrada 5 · 6-ago-2026 · Contratos Pydantic v2 del Endpoint (`app/schemas/historial.py`)

**Objetivo:** Generar el modelo de datos Pydantic v2 para el contrato de validación de entrada del endpoint de Historial de Transacciones a partir del PRD y diagramas de arquitectura.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- `#file:docs/prd/PRD.md` y `#file:docs/architecture/diagrams/sequence_historial.md`.
- Stack: Python 3.12, FastAPI, Pydantic v2, Clean Architecture en `app/schemas/`.

**Salida obtenida:** 
- Primer borrador generado en `app/schemas/transaction_create_request.py` y versión definitiva en `app/schemas/historial.py`.

**Problema detectado:** 
1. **Scope Drift y alucinación de método (🔴 Crítico):** La IA inicialmente intentó modelar un endpoint de creación `POST /transactions` con el esquema `TransactionCreateRequest`, desviándose del requerimiento central del PRD que exige una consulta de historial `GET /api/v1/transacciones`.
2. **Vulnerabilidades semánticas y de seguridad (🔴 Crítico):** En el borrador de creación, la IA permitió que el cliente enviara `created_at` (riesgo de falsificación de timestamps), `status=approved` (riesgo de bypass de pasarela de pago), `authorization_code` (debe ser asignado internamente por el autorizador) y `pan_last4` (el cliente nunca envía sólo last4 en creación, sino PAN tokenizado).
3. **Tipos no idiomáticos (🟠 Medio):** Uso de expresiones regulares para emular enumeraciones en vez del tipo nativo `Literal[...]` de Python/Pydantic v2.

**Cambio realizado por mí:** 
1. Preservé el artefacto auditado `app/schemas/transaction_create_request.py` documentando los 9 hallazgos críticos detectados para trazabilidad del aprendizaje en el diplomado.
2. Definí el schema formal `HistorialQueryParams` en `app/schemas/historial.py` con `desde: date`, `hasta: date`, `estado: Literal["pending", "approved", "rejected", "refunded", "cancelled"] | None = None`, `page_size: int = Field(default=50, ge=1, le=100)` y `cursor: str | None = None`.
3. Implementé `@field_validator("hasta")` para restringir la ventana a un máximo estricto de 90 días respecto a `desde` (lanzando `ValueError("El rango excede el máximo permitido (90 días)")`) y validar que `hasta >= desde`.
4. Configuré `model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)` para rechazar parámetros ajenos al contrato.

**Evidencia o criterio utilizado:** 
- Especificación funcional del PRD (Historia INVEST #1 y regla de retención de 90 días), y el principio arquitectónico de "Pydantic como escudo contenedor" para frenar datos inválidos antes de que alcancen los servicios de dominio o la base de datos.

**Pregunta todavía abierta:** 
- ¿Se requerirá a mediano plazo admitir filtros de estados múltiples en simultáneo (por ejemplo, consultar transacciones "pending" y "rejected" en la misma petición)?

---

## Entrada 6 · 6-ago-2026 · Tests TDD y Pantalla Roja (`tests/test_transaction_create_endpoint.py`)

**Objetivo:** Diseñar y ejecutar la suite de pruebas unitarias/integración con `TestClient` antes de escribir el código de implementación, garantizando un ciclo auténtico de TDD (Pantalla Roja).

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- `#file:docs/prd/PRD.md`, `#file:app/schemas/historial.py`.
- Instrucciones de patrón AAA (`# Arrange`, `# Act`, `# Assert`), sin datos reales ni llamadas de red externas, sobre el endpoint `GET /api/v1/transacciones`.

**Salida obtenida:** 
- Suite de pruebas en `tests/test_transaction_create_endpoint.py` con fixtures y 7 casos de prueba ejecutados.

**Problema detectado:** 
1. **Happy Path dominante (Riesgo #4 de IA):** La propuesta inicial del LLM se concentraba casi exclusivamente en respuestas 200 OK, omitiendo los caminos de error y seguridad estipulados en los diagramas de secuencia.
2. **Oráculo inventado y tests tautológicos:** Tendencia a validar valores literales hardcodeados en lugar de verificar el comportamiento observable y la estructura (*shape*) del contrato.

**Cambio realizado por mí:** 
1. Estructuré la suite cubriendo explícitamente cada flujo del diagrama de secuencia y los casos de borde del PRD:
    - Happy Path (200 OK con validación de shape `data` y `pagination`).
    - Error de Negocio 400 Bad Request cuando el rango excede los 90 días (`error: "El rango excede el máximo permitido (90 días)"`).
    - Error de Seguridad 401 Unauthorized cuando falta la cabecera `Authorization`.
    - Error de Seguridad 401 Unauthorized cuando el token JWT es inválido o malformado.
    - Error de Validación Pydantic 422 Unprocessable Entity cuando `page_size` está fuera del rango permitido (`0` o `101`).
    - Caso borde de frontera temporal: rango exacto de 90 días respondiendo 200 OK exitosamente.
2. Verifiqué que la ejecución inicial con `uv run --frozen pytest -v` resulte en fallo completo (7 tests FAILED con código 404 Not Found), confirmando la Pantalla Roja legítima del TDD.

**Evidencia o criterio utilizado:** 
- Metodología TDD auténtica y las 5 preguntas de auditoría humana de tests ("El verde de un test es solo una hipótesis; la calidad del assert es lo que lo convierte en prueba").

**Pregunta todavía abierta:** 
- ¿Cuál será el esquema de claim específico que el token JWT contendrá para asociar la consulta al `comercio_id` en producción?

---

## Entrada 7 · 11-ago-2026 · Implementación Clean Architecture en 3 Capas (Paso 3 Rojo -> Verde)

**Objetivo:** Desarrollar la implementación mínima requerida siguiendo Clean Architecture (Router, Service, Repository) para hacer que todos los tests pasen a VERDE sin agregar funcionalidad accesoria.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- `#file:docs/prd/PRD.md`, `#file:app/schemas/historial.py`, `#file:tests/test_transaction_create_endpoint.py`.
- Restricciones: separación estricta en 3 capas, repositorio fake en memoria con 5 transacciones fijas, sin librerías externas adicionales.

**Salida obtenida:** 
- Archivos creados: `app/repositories/historial_repo.py`, `app/services/historial_service.py`, `app/routers/historial.py`, y registro en `app/main.py`.

**Problema detectado:** 
1. **Acoplamiento de capas:** El LLM inicialmente intentó colocar consultas directas de filtrado dentro del router y acceder a dependencias HTTP dentro de la capa de servicio.
2. **Exposición de datos sensibles (PCI-DSS):** En borradores preliminares se retornaba el campo `pan` sin enmascarar en la respuesta de la API.

**Cambio realizado por mí:** 
1. Creé `HistorialRepo` con 5 transacciones sintéticas deterministas (`tx1` a `tx5`) y ordenamiento ascendente por fecha para garantizar paginación reproducible.
2. En `HistorialService`, implementé el enmascaramiento PCI-DSS mediante `_mask_pan` (reemplazo por asteriscos conservando únicamente los últimos 4 dígitos) y la lógica de cursor opaco URL-safe en Base64 (`_encode_cursor` y `_decode_cursor`).
3. En `app/routers/historial.py`, mantuve la capa HTTP pura: validación de seguridad Bearer token mediante `secrets.compare_digest`, mapeo de `ValidationError` a HTTP 400 para la regla de 90 días, y orquestación hacia el servicio.
4. Conecté el router a la aplicación principal en `app/main.py`.
5. Ejecuté `pytest -v` y validé que los 7 tests de la suite pasaron exitosamente a VERDE (y 44/44 tests en el repositorio completo).

**Evidencia o criterio utilizado:** 
- Reglas de Clean Architecture: el Router no importa el Repository, el Service no depende de FastAPI ni de BD real, y el enmascaramiento PCI-DSS es obligatorio por política de seguridad B2B.

**Pregunta todavía abierta:** 
- ¿Cómo se desacoplará el repositorio fake para permitir la inyección transparente de SQLAlchemy/Postgres mediante dependencias de FastAPI (`Depends`) en el Módulo 4?

---

## Entrada 8 · 13-ago-2026 · Auditoría de Código, Refactor y Gobernanza (Paso 4)

**Objetivo:** Ejecutar la fase de auto-crítica y auditoría estática sobre el código generado, eliminando *AI code smells*, corrigiendo advertencias de linters y garantizando tipado estricto.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Archivos del Laboratorio 3 en `app/` y `tests/`.
- Linters y verificadores del stack: `ruff` (linter y formateador) y `mypy` (type checker).

**Salida obtenida:** 
- Reporte de análisis de calidad y código refactorizado listo para producción.

**Problema detectado:** 
1. **AI Smell de excepción ciega (`BLE001`):** En `historial_service.py`, la decodificación del cursor capturaba genéricamente `except Exception:`, lo cual oculta bugs no previstos y deuda técnica.
2. **Violación de convención PEP8 (`E402`):** En `app/main.py`, el import de `historial_router` había quedado ubicado después de instanciar la app FastAPI en lugar del bloque superior de imports.
3. **Incompatibilidades de tipos en MyPy:** `HistorialRepo._data` no contaba con anotación explícita de diccionario (`object` vs `date`), y el router utilizaba desempaquetado de diccionario genérico `**params`.

**Cambio realizado por mí:** 
1. Acoté el bloque de captura de excepción en `historial_service.py` a excepciones concretas: `except (ValueError, binascii.Error, UnicodeDecodeError): return 0`.
2. Reordené los imports en `app/main.py` colocándolos al inicio del archivo.
3. Tipé explícitamente `self._data: list[dict[str, Any]]` y utilicé el método idiomático `HistorialQueryParams.model_validate(params)` en el router.
4. Agregué filtros de advertencias en `pyproject.toml` para suprimir advertencias cosméticas de Starlette/httpx2.
5. Ejecuté `uv run --frozen ruff check .` logrando **"All checks passed!"** y `uv run --frozen mypy app/` con **"Success: no issues found in 8 source files"**.
6. Re-verifiqué el 100% de la suite con `uv run --frozen pytest -v` (44 pruebas aprobadas en 0.24s).

**Evidencia o criterio utilizado:** 
- Principios de Gobernanza de Inteligencia Artificial (EU AI Act Art. 14, Human Oversight; NIST AI RMF - Funciones Govern y Measure). Ningún verde generado por IA se acepta sin auditoría humana y validación cruzada con herramientas estáticas independientes.

**Pregunta todavía abierta:** 
- ¿Se incorporará un hook pre-commit automático en el repositorio para rechazar automáticamente commits que introduzcan smells de tipo `BLE001` o desajustes de linter?

---

## Entrada 9 · 25-ago-2026 · Arquitectura y Esqueleto del Agente ReAct (`app/agent/`)

**Objetivo:** Construir el esqueleto inicial del agente autónomo RAG (`tools.py`, `loop.py`, `logger.py`, `goal.md`) bajo el patrón ReAct.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- `#file:docs/prd/PRD.md`, objetivo del agente en `docs/agent/goal.md`, y especificación del Mock LLM en puerto 8001.
- Prompt canónico del Módulo 4 especificando patrón ReAct, esquema compatible con OpenAI y logger auditable JSONL.

**Salida obtenida:** 
- Archivos en `app/agent/`: `tools.py` con `buscar_regla_prd`, `loop.py` con `run_agent`, y `logger.py` con `log_step`.

**Problema detectado:** 
1. **Riesgo de pipeline determinístico:** Si no se enfatiza el patrón ReAct, la IA tiende a encadenar llamadas secuenciales rígidas en lugar de permitir que el modelo razone sobre la observación.
2. **Aislamiento de módulos:** Necesidad de garantizar que el nuevo agente no interfiera con el módulo de demo `agent/` preexistente en la raíz.

**Cambio realizado por mí:** 
1. Diseñé el agente en el submódulo independiente `app/agent/` con `__init__.py`.
2. Implementé `TOOLS_SCHEMA` siguiendo el estándar JSON Schema de OpenAI Chat Completions.
3. Configuré el retriever léxico en `buscar_regla_prd` con ventana de contexto de ±3 líneas y numeración exacta de líneas para trazabilidad.

**Evidencia o criterio utilizado:** 
- Principio de autonomía controlada del patrón ReAct (Reason -> Act -> Observe) y modularidad para aislar el módulo del proyecto final.

**Pregunta todavía abierta:** 
- ¿Qué estrategia de indexación o cacheo léxico sería conveniente si el PRD se expandiera a decenas de páginas?

---

## Entrada 10 · 25-ago-2026 · Implementación y Visibilidad de Barandas de Seguridad

**Objetivo:** Establecer e identificar explícitamente en código las barandas de seguridad del agente (Guardrails).

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Requerimientos de seguridad del Módulo 4: restricción de dominio y prevención de bucles infinitos.

**Salida obtenida:** 
- Constantes y directivas en `app/agent/loop.py`.

**Problema detectado:** 
1. **Falta de visibilidad:** Las restricciones suelen quedar implícitas o mezcladas en la lógica del código, dificultando su auditoría.
2. **Riesgo de denegación de servicio por recursión:** Ausencia de un límite estricto de pasos si el modelo no alcanza un estado final.

**Cambio realizado por mí:** 
1. Documenté con comentarios destacados las dos barandas críticas:
   - **Baranda #1 (SCOPE):** `SYSTEM_PROMPT` delimitando que solo responda sobre el PRD, no ejecute acciones destructivas y diga 'fuera de alcance' ante consultas ajenas.
   - **Baranda #3 (BUDGET):** `MAX_STEPS = 5` limitando las iteraciones del loop.
2. Añadí validación estricta en `_parse_decision` para descartar acciones no autorizadas (`buscar_regla_prd` y `final`).

**Evidencia o criterio utilizado:** 
- Marcos de seguridad de agentes (NIST AI RMF e ISO/IEC 42001 sobre confinamiento de acciones y presupuestos computacionales).

**Pregunta todavía abierta:** 
- ¿En qué casos de uso futuros se requeriría una baranda Human-in-the-Loop antes de invocar herramientas de mutación?

---

## Entrada 11 · 27-ago-2026 · Suite de Evaluación Golden Set (`evals/eval_agent.py`)

**Objetivo:** Desarrollar y validar el conjunto de pruebas automatizadas (Golden Set) para verificar outcome y trayectoria del agente.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- 3 casos de prueba del proyecto final: 2 positivos (`rango-90-dias`, `pan-solo-ultimos-4`) y 1 adversarial (`fuera-de-alcance`).

**Salida obtenida:** 
- Script de evaluación `evals/eval_agent.py` conectando contra el Mock LLM en puerto 8001.

**Problema detectado:** 
1. **Discrepancia léxica en caso PAN:** La prueba `pan-solo-ultimos-4` inicialmente fallaba porque en `PRD.md` la frase "solo últimos 4 dígitos" estaba en la sección de visión general pero no en la descripción textual de la regla `RN-02`.

**Cambio realizado por mí:** 
1. Ajusté `PRD.md` especificando `(solo últimos 4 dígitos)` dentro de `RN-02`, permitiendo que la búsqueda léxica recupere el contexto exacto.
2. Ejecuté `evals/eval_agent.py` obteniendo un resultado perfecto: **3/3 casos aprobados (100% PASS)**.

**Evidencia o criterio utilizado:** 
- Principio de evaluación empírica de agentes: sin evaluación automatizada y reproducible no existe garantía de calidad del comportamiento de un LLM.

**Pregunta todavía abierta:** 
- ¿Cómo integrar la ejecución del Golden Set como un step condicional en el flujo de CI cuando el mock LLM corre en un contenedor?

---

## Entrada 12 · 27-ago-2026 · Pruebas Unitarias de Agente, Tipado MyPy y Cobertura de CI

**Objetivo:** Incorporar pruebas unitarias formales para `app/agent` en pytest, garantizar tipado estricto y mantener la cobertura de código por encima del 60% en CI.

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Suite de CI en `.github/workflows/ci.yml` ejecutando `ruff`, `mypy`, `bandit` y `pytest --cov=app --cov-fail-under=60`.

**Salida obtenida:** 
- Archivo `tests/test_rag_agent.py` cubriendo casos de borde de tools, loop y logger.

**Problema detectado:** 
1. **Error de MyPy `[no-any-return]`:** `_call_llm` en `loop.py` retornaba `response.choices[0].message.content` (tipo `Any`) en una función tipada como `-> str`.
2. **Caída de cobertura de tests:** Al agregar `app/agent/` sin tests en pytest, la cobertura del paquete `app` descendió a 55.66%, lo que rompería el pipeline de CI.

**Cambio realizado por mí:** 
1. Corregí el tipado en `app/agent/loop.py` mediante `return str(content)`.
2. Creé 17 pruebas unitarias completas en `tests/test_rag_agent.py` con mocks de `OpenAI` y parches de sistema de archivos, elevando la cobertura total a **93.87%** (61/61 tests aprobados).
3. Verifiqué localmente que `ruff`, `mypy`, `bandit` y `pytest` pasaran al 100% en verde.

**Evidencia o criterio utilizado:** 
- Estándares de ingeniería de software robusta: la presencia de IA o agentes no exime al código del cumplimiento de linters, análisis de tipos y cobertura de código.

**Pregunta todavía abierta:** 
- ¿Qué mecanismos de inyección de dependencias (`Dependency Injection`) facilitarán alternar entre clientes de OpenAI reales y simulados en producción?

---

## Entrada 13 · 28-ago-2026 · Release Candidate, Postmortem y Transferencia (Handoff)

**Objetivo:** Consolidar los artefactos finales de entrega del Módulo 5 (`README.md` como Release Candidate, `postmortem_final.md`, log auditable y plan de handoff).

**Herramienta y modelo:** Antigravity IDE (Gemini 3.8 Flash de Google).

**Contexto proporcionado:** 
- Plantilla Release Candidate del diplomado, directrices de postmortem honesto y lineamientos de defensa profesional.

**Salida obtenida:** 
- `README.md` ampliado con las 5 secciones requeridas.
- `postmortem_final.md` con análisis de fallos, aciertos y 3 lecciones aprendidas.
- Propuesta de Handoff Issue para evolución del sistema.

**Problema detectado:** 
1. **Riesgo de opacidad técnica:** La tendencia a no declarar las limitaciones del retriever léxico frente a sinónimos.

**Cambio realizado por mí:** 
1. Documenté explícitamente las limitaciones conocidas (ausencia de embeddings semánticos y naturaleza determinística del Mock LLM).
2. Estructuré el postmortem con autocrítica constructiva y redacté el plan de handoff enfocado en la migración hacia búsqueda semántica con ChromaDB.

**Evidencia o criterio utilizado:** 
- Madurez profesional en entrega de software (Release Candidate) y transferencia explícita de conocimiento para el siguiente equipo de ingeniería.

**Pregunta todavía abierta:** 
- ¿Cuál será el costo computacional y financiero estimado de migrar el retriever a embeddings de OpenAI `text-embedding-3-small` en producción?
