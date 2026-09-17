# Postmortem · Proyecto Final Alan Duarte · 28-ago-2026

## 1. Qué funcionó

- **Arquitectura desacoplada del agente ReAct:** La separación modular en `app/agent/` entre herramientas (`tools.py`), orquestación de ciclo (`loop.py`) y auditoría estructurada (`logger.py`) permitió un sistema transparente, fácil de depurar y libre de interferencias con el módulo de demo existente en la raíz.
- **RAG léxico contextualizado:** La ventana de contexto de ±3 líneas con números de línea implementada en `buscar_regla_prd` demostró ser sumamente efectiva para proveer al agente de la evidencia exacta requerida para fundamentar sus respuestas sin sobrecargar el contexto.
- **Trazabilidad y gobernanza continua:** Registrar cada intervención humana y decisión asistida por IA en `AI_USAGE.md` desde el Laboratorio 2 hasta el Proyecto Final facilitó enormemente la redacción del Release Candidate y la justificación técnica de cada cambio.
- **Validación local estricta antes de CI:** Detectar tempranamente mediante `mypy` y `pytest --cov` que el nuevo módulo requería pruebas unitarias dedicadas permitió resolver el déficit de cobertura localmente (alcanzando 93.87%) antes de abrir el Pull Request en GitHub.

---

## 2. Qué no funcionó

- **Fragilidad de la búsqueda léxica pura:** Al depender de coincidencias textuales literales, la consulta `pan-solo-ultimos-4` inicialmente no recuperaba la evidencia esperada porque la frase "solo últimos 4 dígitos" figuraba en la introducción del PRD pero no en la línea de la regla `RN-02`. Esto evidenció la limitación del enfoque léxico ante pequeñas variaciones de redacción.
- **Falsa presunción sobre la cobertura de tests:** Inicialmente se consideró que el Golden Set (`evals/eval_agent.py`) sería suficiente para evaluar el agente; sin embargo, al ejecutarse de forma independiente fuera de pytest, la cobertura del paquete `app/` descendió al 55.66%, lo que hubiera quebrado el CI de no haberse implementado `tests/test_rag_agent.py`.
- **Incompatibilidad de tipos implícita (`Any` vs `str`):** La implementación sugerida para `_call_llm` delegaba en el objeto dinámico de la API de OpenAI, provocando un fallo de tipo en MyPy (`[no-any-return]`) que requirió corrección y tipado defensivo explícito.

---

## 3. Qué haría distinto

- **Incorporar búsqueda semántica con embeddings vectoriales:** En una próxima iteración, sustituiría o complementaría el grep léxico con un retriever semántico basado en embeddings (ej. `sentence-transformers` o `text-embedding-3-small` en ChromaDB/pgvector) para soportar consultas con sinónimos, paráfrasis o formulaciones indirectas.
- **Automatización de hooks de pre-commit:** Instalaría `pre-commit` con reglas automáticas de `ruff check --fix` y `mypy` para asegurar que ningún archivo con inconsistencias de estilo o tipos pueda ser commiteado localmente.
- **Ejecución integrada de evals en CI:** Parametrizaría el script de evaluación `eval_agent.py` para que pueda correr dentro de un step del pipeline de GitHub Actions levantando el Mock LLM en background en el runner de Ubuntu.

---

## 4. 3 Lecciones Aprendidas

1. **Sobre Agentes Autónomos:**  
   Un agente de IA no es un script determinístico disfrazado ni un flujo estático de preguntas y respuestas; requiere un bucle ReAct real donde el modelo determine la trayectoria en función de la evidencia recuperada, contenido obligatoriamente por barandas duales: semánticas (Scope en el prompt del sistema) y computacionales (Budget con límite estricto de pasos).

2. **Sobre RAG y Bases de Conocimiento:**  
   La calidad de un sistema RAG está determinada en un 80% por la calidad y estructura del documento de conocimiento. Si el PRD contiene ambigüedades, redundancias o reglas fragmentadas, el agente fallará independientemente de la potencia del LLM. La ingeniería de prompts y la ingeniería de requisitos deben converger.

3. **Sobre el Trabajo Profesional con IA:**  
   Acelerar el desarrollo con asistentes de inteligencia artificial solo es una ventaja competitiva si el desarrollador actúa como un auditor implacable. La verdadera maestría técnica radica en saber cuestionar las salidas del modelo, detectar smells semánticos, garantizar cobertura de código y entregar productos Release Candidate defendibles con métricas y evidencia demostrable.
