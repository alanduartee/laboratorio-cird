"""evals/eval_agent.py — Golden Set del agente RAG del Proyecto Final."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent.loop import run_agent  # noqa: E402

CASES: list[dict[str, str]] = [
    {
        "id": "rango-90-dias",
        "question": "¿cuál es el rango máximo del historial?",
        "expected_substring": "90 días",
    },
    {
        "id": "pan-solo-ultimos-4",
        "question": "¿puedo exponer el PAN completo?",
        "expected_substring": "últimos 4",
    },
    {
        "id": "fuera-de-alcance",
        "question": "¿cuál es la capital de Francia?",
        "expected_substring": "Sin coincidencias",
    },
]


def evaluate_case(case: dict[str, str], client: Any) -> bool:
    answer = run_agent(case["question"], client, model="gpt-4o-mini")
    ok = case["expected_substring"].lower() in str(answer).lower()
    mark = "✅" if ok else "❌"
    print(f"{mark} {case['id']}: {'PASS' if ok else 'FAIL'}")
    print(f"  Pregunta: {case['question']}")
    print(f"  Respuesta: {answer[:180]}...")
    return ok


def evaluate() -> None:
    client = OpenAI(
        base_url="http://localhost:8001/v1",
        api_key="mock",
    )
    passed = 0
    print("Iniciando evaluación del Golden Set de agente RAG...\n")
    for case in CASES:
        if evaluate_case(case, client):
            passed += 1
    print(f"\nResultado final: {passed}/{len(CASES)} casos pasaron")


if __name__ == "__main__":
    evaluate()
