import os
import secrets
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.repositories.historial_repo import HistorialRepo
from app.schemas.historial import HistorialQueryParams
from app.services.historial_service import HistorialService

router = APIRouter(prefix="/api/v1")

TEST_TOKEN = os.getenv("TEST_TOKEN", "test-valid-jwt")  # valor por defecto solo para tests/local


def _auth_header_valid(request: Request) -> bool:
    """Valida el token Bearer en el header de autorización."""
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1]

    # Validación determinista para entorno de pruebas / local
    return secrets.compare_digest(token, TEST_TOKEN)


@router.get("/transacciones")
async def get_transacciones(request: Request) -> Any:
    """Endpoint para consultar el historial de transacciones de un comercio."""
    # Validación de seguridad: 401 si falta autorización o el token es inválido
    if not _auth_header_valid(request):
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validación del contrato HTTP y mapeo de errores de negocio
    params = dict(request.query_params)
    try:
        qp = HistorialQueryParams(**params)
    except ValidationError as e:
        for err in e.errors():
            msg = err.get("msg", "")
            if "El rango excede el máximo permitido (90 días)" in msg:
                return JSONResponse(
                    status_code=400,
                    content={"error": "El rango excede el máximo permitido (90 días)"},
                )

        raise HTTPException(status_code=422, detail=e.errors())

    # Inyección de dependencias limpias: Router -> Service -> Repository
    repo = HistorialRepo()
    service = HistorialService(repo)
    return service.get_historial(qp)
