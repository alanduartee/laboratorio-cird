"""tests/test_rag_agent.py — Pruebas unitarias para app/agent (tools, logger, loop)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.agent.logger import log_step
from app.agent.loop import _call_llm, _parse_decision, run_agent
from app.agent.tools import buscar_regla_prd


def test_buscar_regla_prd_empty_term() -> None:
    result = buscar_regla_prd("   ")
    assert "el término de búsqueda está vacío" in result


def test_buscar_regla_prd_no_hits() -> None:
    result = buscar_regla_prd("palabra_inexistente_xyz_123")
    assert "Sin coincidencias para el término" in result


def test_buscar_regla_prd_hit_success() -> None:
    result = buscar_regla_prd("90 días")
    assert "Hit en línea" in result
    assert "90 días" in result


def test_buscar_regla_prd_missing_file(tmp_path: Path) -> None:
    fake_path = tmp_path / "non_existent_prd.md"
    with patch("app.agent.tools.PRD_PATH", fake_path):
        result = buscar_regla_prd("test")
        assert "ERROR: no se encontró el PRD" in result


def test_logger_log_step(tmp_path: Path) -> None:
    fake_log = tmp_path / "logs" / "test_run.jsonl"
    with patch("app.agent.logger.LOG_PATH", fake_log):
        log_step(1, "buscar_regla_prd", {"termino": "90 días"}, "Resultado simulado")
        assert fake_log.exists()
        lines = fake_log.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["step"] == 1
        assert entry["tool"] == "buscar_regla_prd"
        assert entry["args"] == {"termino": "90 días"}
        assert entry["result_summary"] == "Resultado simulado"


def test_parse_decision_valid_final() -> None:
    raw = '{"thought": "listo", "action": "final", "action_input": {"respuesta": "OK"}}'
    action, action_input = _parse_decision(raw)
    assert action == "final"
    assert action_input == {"respuesta": "OK"}


def test_parse_decision_valid_tool() -> None:
    raw = '{"thought": "buscando", "action": "buscar_regla_prd", "action_input": {"termino": "pan"}}'
    action, action_input = _parse_decision(raw)
    assert action == "buscar_regla_prd"
    assert action_input == {"termino": "pan"}


def test_parse_decision_invalid_json() -> None:
    with pytest.raises(ValueError, match="El LLM no devolvió JSON válido"):
        _parse_decision("not a json")


def test_parse_decision_invalid_action() -> None:
    raw = '{"action": "unknown_tool", "action_input": {}}'
    with pytest.raises(ValueError, match="acción no permitida"):
        _parse_decision(raw)


def test_parse_decision_invalid_input_type() -> None:
    raw = '{"action": "final", "action_input": "not a dict"}'
    with pytest.raises(ValueError, match="debe ser un objeto JSON"):
        _parse_decision(raw)


def test_call_llm_empty_response() -> None:
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=""))
    ]
    with pytest.raises(ValueError, match="El LLM devolvió una respuesta vacía"):
        _call_llm(mock_client, [], "gpt-4o-mini")


def test_run_agent_final_immediately() -> None:
    mock_client = MagicMock()
    mock_decision = json.dumps(
        {
            "thought": "Respuesta directa",
            "action": "final",
            "action_input": {"respuesta": "Respuesta final de prueba"},
        }
    )
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=mock_decision))
    ]
    answer = run_agent("¿Hola?", mock_client)
    assert answer == "Respuesta final de prueba"


def test_run_agent_invalid_decision_error() -> None:
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="invalid json"))
    ]
    answer = run_agent("¿test?", mock_client)
    assert answer.startswith("Error del agente:")


def test_run_agent_invalid_final_response_format() -> None:
    mock_client = MagicMock()
    mock_decision = json.dumps(
        {
            "thought": "Final inválido",
            "action": "final",
            "action_input": {"respuesta": 12345},
        }
    )
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=mock_decision))
    ]
    answer = run_agent("¿test?", mock_client)
    assert "la respuesta final no es un texto válido" in answer


def test_run_agent_tool_loop_then_final(tmp_path: Path) -> None:
    fake_log = tmp_path / "logs" / "test_loop.jsonl"
    with patch("app.agent.logger.LOG_PATH", fake_log):
        mock_client = MagicMock()
        step1 = json.dumps(
            {
                "thought": "Buscar en PRD",
                "action": "buscar_regla_prd",
                "action_input": {"termino": "90 días"},
            }
        )
        step2 = json.dumps(
            {
                "thought": "Tengo la respuesta",
                "action": "final",
                "action_input": {"respuesta": "El rango es 90 días."},
            }
        )
        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=step1))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=step2))]),
        ]

        answer = run_agent("¿rango?", mock_client)
        assert answer == "El rango es 90 días."


def test_run_agent_invalid_termino_argument(tmp_path: Path) -> None:
    fake_log = tmp_path / "logs" / "test_arg.jsonl"
    with patch("app.agent.logger.LOG_PATH", fake_log):
        mock_client = MagicMock()
        step1 = json.dumps(
            {
                "thought": "Buscar con arg invalido",
                "action": "buscar_regla_prd",
                "action_input": {"termino": 999},
            }
        )
        step2 = json.dumps(
            {
                "thought": "Terminar",
                "action": "final",
                "action_input": {"respuesta": "terminado"},
            }
        )
        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=step1))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=step2))]),
        ]

        answer = run_agent("¿test?", mock_client)
        assert answer == "terminado"


def test_run_agent_reaches_max_steps() -> None:
    mock_client = MagicMock()
    step_infinite = json.dumps(
        {
            "thought": "Buscar siempre",
            "action": "buscar_regla_prd",
            "action_input": {"termino": "90 días"},
        }
    )
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=step_infinite))]
    )
    answer = run_agent("¿bucle?", mock_client)
    assert "se alcanzó el límite de 5 pasos" in answer
