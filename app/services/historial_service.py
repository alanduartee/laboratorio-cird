from __future__ import annotations

import base64
import binascii
from datetime import date
from typing import Any


class HistorialService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def _mask_pan(self, pan: str) -> str:
        """Enmascara el PAN cumpliendo normativa PCI-DSS (conserva solo últimos 4 dígitos)."""
        if not pan or len(pan) <= 4:
            return "*" * len(pan)
        return "*" * (len(pan) - 4) + pan[-4:]

    def _encode_cursor(self, index: int) -> str:
        """Codifica un índice numérico como cursor URL-safe opaco en base64."""
        return base64.urlsafe_b64encode(str(index).encode()).decode()

    def _decode_cursor(self, cursor: str | None) -> int:
        """Decodifica un cursor opaco; si es ausente o inválido, inicia en el índice 0."""
        if not cursor:
            return 0
        try:
            raw = base64.urlsafe_b64decode(cursor.encode()).decode()
            return int(raw)
        except (ValueError, binascii.Error, UnicodeDecodeError):
            return 0


    def get_historial(self, qp) -> dict[str, Any]:
        """Aplica las reglas de negocio de historial, filtros, enmascaramiento y paginación con cursor."""
        desde: date = qp.desde
        hasta: date = qp.hasta
        page_size: int = qp.page_size
        estado = qp.estado
        cursor = qp.cursor

        items = self.repo.filter(desde, hasta, estado)

        start = self._decode_cursor(cursor)
        end = start + page_size
        page = items[start:end]

        data: list[dict[str, Any]] = [
            {
                "id": t["id"],
                "fecha": t["fecha"].isoformat(),
                "pan": self._mask_pan(t.get("pan", "")),
                "monto": t.get("monto"),
                "estado": t.get("estado"),
            }
            for t in page
        ]

        has_more = end < len(items)
        next_cursor = self._encode_cursor(end) if has_more else None

        return {
            "data": data,
            "pagination": {"next_cursor": next_cursor, "has_more": has_more},
        }
