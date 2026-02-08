#!/usr/bin/env python3
"""
Truths and Rights — Scraper Health Check

Verifica que los sitios gubernamentales estan accesibles.
HEAD requests a los 4 sitios principales: TC, El Peruano, Congreso, SPIJ.

Uso:
    python scripts/check_scraper_health.py
"""

import sys
import json
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: Se necesita 'requests'. Instalar: pip install requests")
    sys.exit(1)


SITES = [
    {
        "id": "tc",
        "name": "Tribunal Constitucional",
        "url": "https://www.tc.gob.pe",
    },
    {
        "id": "peruano",
        "name": "El Peruano (Diario Oficial)",
        "url": "https://diariooficial.elperuano.pe",
    },
    {
        "id": "congreso",
        "name": "Congreso (Archivo Digital)",
        "url": "https://leyes.congreso.gob.pe",
    },
    {
        "id": "spij",
        "name": "SPIJ (Ministerio de Justicia)",
        "url": "https://spij.minjus.gob.pe",
    },
]

TIMEOUT = 15


def check_site(site):
    """HEAD request a un sitio, retorna resultado."""
    try:
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.headers.update({
            'User-Agent': 'TruthsAndRights/1.0 (Health Check)',
        })

        resp = session.head(site["url"], timeout=TIMEOUT, allow_redirects=True)
        return {
            "id": site["id"],
            "name": site["name"],
            "url": site["url"],
            "status_code": resp.status_code,
            "ok": resp.status_code < 400,
            "response_time_ms": int(resp.elapsed.total_seconds() * 1000),
        }
    except requests.RequestException as e:
        return {
            "id": site["id"],
            "name": site["name"],
            "url": site["url"],
            "status_code": None,
            "ok": False,
            "error": str(e),
            "response_time_ms": None,
        }


def main():
    print("Truths and Rights — Health Check de sitios gubernamentales")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    results = []
    all_ok = True

    for site in SITES:
        result = check_site(site)
        results.append(result)

        if result["ok"]:
            ms = result.get("response_time_ms", "?")
            print(f"  OK  {site['name']:40s} {result['status_code']} ({ms}ms)")
        else:
            all_ok = False
            error = result.get("error", f"HTTP {result.get('status_code', '?')}")
            print(f"  FAIL {site['name']:39s} {error}")

    print(f"\nResultado: {'Todos accesibles' if all_ok else 'Sitio(s) caido(s) detectado(s)'}")

    report = {
        "timestamp": datetime.now().isoformat(),
        "all_ok": all_ok,
        "sites": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
