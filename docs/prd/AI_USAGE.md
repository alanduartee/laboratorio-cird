# AI Usage Log — Laboratorio 2 y 3 (LegacyPay)

Este documento registra la trazabilidad y la auditoría humana aplicada a cada artefacto de especificación, arquitectura y código generado con la asistencia de Inteligencia Artificial.

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
