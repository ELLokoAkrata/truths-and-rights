---
name: truths-and-rights-context
description: Contexto completo del proyecto Truths and Rights. Usa este skill cuando necesites entender la arquitectura, los datos, los scripts o la automatizacion del proyecto.
user-invocable: true
---

# Truths and Rights — Contexto del proyecto

## Que es

App ciudadana que informa derechos ante intervenciones policiales en Peru. El ciudadano busca su situacion ("me quieren revisar la mochila") y recibe: sus derechos, que hacer paso a paso, limites legales y a quien llamar.

## Principio fundamental

**Si no tiene fuente oficial verificable, no entra a la base de datos.** Los datos legales nunca se modifican automaticamente. Todo cambio requiere verificacion humana (idealmente abogado).

## Estructura del proyecto

```
truths-and-rights/
├── data/PE/                    # Datos legales de Peru (JSON)
│   ├── metadata.json           # Config del pais, emergencias activas, estadisticas
│   ├── situations/             # 9 situaciones (01_id_check.json ... 08_cannabis.json)
│   ├── rights/rights.json      # 20+ derechos con never_suspended flag
│   ├── actions/actions.json    # 17+ acciones paso a paso con scripts sugeridos
│   ├── contacts/               # 7 contactos de emergencia
│   ├── contexts/contexts.json  # 2 contextos: normal + estado_emergencia
│   ├── myths/myths.json        # 7 mitos desmentidos
│   ├── sources/                # 43+ fuentes legales (constitucion, CPP, CP, DL, TC)
│   │   ├── constitution.json, criminal_procedure.json, jurisprudence.json, police_law.json
│   │   ├── substances/legal_possession.json  # Limites legales de sustancias
│   │   └── raw/               # Descargas del scraper (no versionado)
│   └── verification_history.jsonl  # Audit trail de verificaciones
├── schema/
│   ├── database_schema.sql     # 12 tablas + 3 junction + 3 support + 3 views
│   └── SCHEMA_DOCS.md
├── scripts/
│   ├── build_db.py             # JSON -> SQLite (la DB que usa la app)
│   ├── validate_sources.py     # Valida integridad de todos los JSON
│   ├── scrape_official.py      # Scraper de TC, El Peruano, Congreso (con --output-json, retry, historial)
│   ├── generate_site.py        # Generador de portal estatico (Python puro, sin deps)
│   ├── check_scraper_health.py # HEAD requests a sitios gubernamentales
│   ├── history.py              # Modulo de historial JSONL
│   ├── search.py               # Motor de busqueda (en desarrollo)
│   └── cli.py                  # CLI interactivo (en desarrollo)
├── build/                      # DB generada (no versionado)
│   └── truths_and_rights_pe.db # SQLite ~256KB
├── site/                       # Portal HTML generado (no versionado)
├── tests/                      # pytest
├── .github/
│   ├── workflows/
│   │   ├── validate.yml        # CI: valida datos + build DB + tests (cada push)
│   │   ├── check-emergency.yml # Semanal: verifica decreto de emergencia
│   │   ├── check-updates.yml   # Quincenal: verifica vigencia de fuentes
│   │   ├── full-scrape.yml     # Mensual: scrape completo
│   │   └── deploy-site.yml     # Auto: genera y publica portal en GitHub Pages
│   └── ISSUE_TEMPLATE/         # Templates para Issues automaticos
├── docs/
│   ├── AUTOMATION.md           # Guia completa de automatizacion
│   ├── LEGAL_METHODOLOGY.md    # Cadena de verificacion legal
│   ├── DATA_FORMAT.md          # Formato de datos
│   └── ADDING_A_COUNTRY.md     # Como agregar otro pais
├── Makefile                    # build-pe, validate-pe, test, site, serve, scrape, etc.
├── requirements.txt            # requests, beautifulsoup4, lxml, pytest
└── CHANGELOG.md                # Actualmente v0.3.0
```

## Base de datos SQLite

12 tablas principales:
- `legal_sources` — 43 fuentes oficiales (constitucion, leyes, sentencias TC, tratados)
- `situations` — 9 escenarios ciudadanos
- `contexts` — normal + estado_emergencia (modifica derechos)
- `rights` — 20+ derechos con flag `never_suspended`
- `actions` — 17+ pasos con `suggested_script` (frases exactas para decir)
- `time_limits` — Plazos maximos de retencion/detencion
- `emergency_contacts` — 7 lineas de ayuda
- `myths` — 7 mitos desmentidos
- `force_levels` — 4 niveles de fuerza policial (con legalidad)
- `legal_possession` — 7 sustancias con limites legales

Junction tables: `situation_rights` (mapea derechos por situacion y contexto), `situation_actions` (pasos ordenados), `situation_contacts`.

La DB se genera con: `python scripts/build_db.py --country PE`

## Formato de datos clave

Cada situacion tiene esta estructura:
```json
{
  "id": "police_id_check",
  "title": "La policia me pide DNI",
  "severity": "medium",
  "rights": [{"right_id": "right_know_reason", "context": "normal", "applies": true}],
  "actions": [{"action_id": "action_stay_calm", "step_order": 1}],
  "time_limits": [{"max_hours": 4, "description": "Maximo para verificacion de identidad"}],
  "contacts": ["defensoria_pueblo"]
}
```

Cada derecho:
```json
{
  "id": "right_no_cell_search",
  "title": "No pueden revisar tu celular",
  "never_suspended": true,
  "legal_basis": "Art. 2.10 Constitucion + Art. 230 CPP",
  "category": "comunicaciones"
}
```

## Estado de emergencia (critico)

El decreto DS N° 006-2026-PCM (Lima + Callao) suspende 4 derechos: libertad personal, inviolabilidad de domicilio, libertad de transito, libertad de reunion. Pero NUNCA se suspenden: dignidad, debido proceso, comunicaciones privadas, habeas corpus, derecho a abogado, prohibicion de tortura.

Los decretos se renuevan cada 30-60 dias. El workflow semanal verifica automaticamente.

## Automatizacion

- Los workflows crean Issues, nunca editan datos
- `verification_history.jsonl` es el audit trail
- Portal publico: https://ellokoakrata.github.io/truths-and-rights/
- Repo: https://github.com/ELLokoAkrata/truths-and-rights

## Convenciones

- Todos los textos legales en espanol
- IDs en snake_case ingles (right_no_cell_search)
- Fechas en ISO 8601 (YYYY-MM-DD)
- JSON con indent 2, UTF-8, ensure_ascii=False
- Licencia GPL v3
- El proyecto es extensible a otros paises (estructura data/{COUNTRY_CODE}/)
