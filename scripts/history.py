#!/usr/bin/env python3
"""
Truths and Rights — Verification History Module

Mantiene un historial de verificaciones en formato JSONL (una linea JSON por
verificacion). Este archivo SI se versiona: es el audit trail del proyecto.

Archivo de salida: data/PE/verification_history.jsonl
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_ROOT / "data" / "PE" / "verification_history.jsonl"


def append_to_history(report):
    """
    Agrega un registro de verificacion al historial.

    Args:
        report: dict con los resultados de la verificacion.
                Debe contener al menos 'check_type' y 'timestamp'.
    """
    entry = {
        "timestamp": report.get("timestamp", datetime.now().isoformat()),
        "check_type": report.get("check_type", "unknown"),
        "verified_count": len(report.get("verified", [])),
        "needs_update_count": len(report.get("needs_update", [])),
        "errors_count": len(report.get("errors", [])),
        "summary": _build_summary(report),
        "details": {
            "needs_update": report.get("needs_update", []),
            "errors": report.get("errors", []),
        },
    }

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def read_history(limit=50):
    """Lee las ultimas N entradas del historial."""
    if not HISTORY_FILE.exists():
        return []

    entries = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    return entries[-limit:]


def _build_summary(report):
    """Genera un resumen legible de la verificacion."""
    check_type = report.get("check_type", "unknown")
    verified = len(report.get("verified", []))
    needs_update = len(report.get("needs_update", []))
    errors = len(report.get("errors", []))

    if check_type == "emergency":
        items = report.get("needs_update", [])
        if items:
            labels = [i.get("decree", i.get("id", "?")) for i in items]
            return f"Emergencia: {', '.join(labels)} requiere atencion"
        return "Emergencia: todo vigente"
    elif check_type == "sources":
        return f"Fuentes: {verified} OK, {needs_update} necesitan revision, {errors} errores"
    elif check_type == "full_scrape":
        return f"Scrape completo: {verified} OK, {needs_update} cambios detectados, {errors} errores"
    else:
        return f"{check_type}: {verified} OK, {needs_update} pendientes, {errors} errores"
