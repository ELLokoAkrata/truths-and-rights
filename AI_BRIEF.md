# AI AGENT BRIEF — Truths and Rights

> Este documento es el punto de entrada para cualquier agente de IA (Claude Code, Cursor, Copilot, Aider, GPT, etc.) que trabaje en este proyecto. Léelo completo antes de tocar código.

## ¿Qué es este proyecto?

App móvil open source que informa a ciudadanos sus derechos legales durante intervenciones policiales. País actual: Perú. Diseñado para expandirse a cualquier país.

## Problema que resuelve

Asimetría de conocimiento: el policía sabe (o cree saber) qué puede hacer; el ciudadano no sabe qué puede exigir. Las leyes existen pero no llegan al ciudadano en el momento que las necesita.

## Arquitectura actual

```
truths-and-rights/
├── data/PE/                    # Datos legales de Perú en JSON
│   ├── metadata.json           # Estado del país, emergencias activas
│   ├── sources/                # Fuentes legales (Constitución, CPP, DL, jurisprudencia)
│   ├── situations/             # 9 escenarios ciudadanos
│   ├── rights/                 # 20 derechos documentados
│   ├── actions/                # 17 acciones con scripts pregrabados
│   ├── contacts/               # 7 contactos de emergencia
│   ├── substances/             # Cantidades legales (Art. 299 CP)
│   ├── contexts/               # Normal + estado de emergencia
│   └── myths/                  # 7 mitos desmontados
├── schema/                     # Schema SQLite (12 tablas)
├── scripts/
│   ├── build_db.py             # JSON → SQLite (funcional)
│   ├── scrape_official.py      # TODO: scraping de fuentes oficiales
│   └── validate_sources.py     # TODO: verificar vigencia de normas
├── build/
│   └── truths_and_rights_pe.db # DB generada (256 KB)
├── docs/                       # Documentación completa
└── [README, CONTRIBUTING, LICENSE, etc.]
```

## Stack

- **Datos:** JSON (legibles por humanos y máquinas)
- **Base de datos:** SQLite (offline-first, se empaqueta en la app)
- **Build:** Python 3 (scripts/build_db.py)
- **App móvil:** POR DEFINIR (React Native o Flutter)
- **Licencia:** GPL v3

## Flujo de datos

```
JSON en data/PE/ → build_db.py → SQLite .db → App móvil consulta offline
```

## Convenciones críticas

### IDs
- Snake_case en inglés: `right_no_cell_search`, `action_stay_calm`
- Prefijos por tipo: `right_`, `action_`, `limit_`, `myth_`, `const_`, `cpp_`, `cp_`, `dl_`, `tc_`
- Descriptivos, nunca numéricos

### Datos legales
- CADA dato legal DEBE tener fuente oficial verificable
- `full_text` = texto literal de la ley (copiar exacto)
- `summary` = lenguaje que entienda cualquier persona de 16 años
- `status` = vigente | modificado | derogado
- Fechas en ISO: YYYY-MM-DD

### Archivos JSON
- Arrays en el nivel raíz: `[{...}, {...}]`
- UTF-8 con caracteres españoles (á, é, í, ó, ú, ñ, ¿, ¡)
- Ver docs/DATA_FORMAT.md para schemas completos

## Fuentes oficiales de Perú

| Fuente | URL | Qué tiene |
|---|---|---|
| SPIJ | spij.minjus.gob.pe | Legislación completa, tiene API |
| El Peruano | diariooficial.elperuano.pe | Diario oficial, decretos y leyes |
| TC | tc.gob.pe | Sentencias constitucionales |
| Congreso | congreso.gob.pe | Textos de leyes |
| Corte IDH | corteidh.or.cr | Jurisprudencia interamericana |

## Estado actual (2026-02-07)

### Verificado y funcional
- [x] Schema de base de datos SQLite (12 tablas) — completo
- [x] Datos legales de Perú en JSON — 43 fuentes, 20 derechos, 17 acciones, 9 situaciones, 7 contactos, 7 mitos, 2 contextos
- [x] `scripts/validate_sources.py` — funcional, 0 errores, 0 advertencias
- [x] `scripts/build_db.py` — funcional, genera `truths_and_rights_pe.db` (256 KB)
- [x] Fix de encoding UTF-8 para compatibilidad con Windows
- [x] Dependencias instaladas (requests, beautifulsoup4, lxml)

### Nota técnica
Los scripts `validate_sources.py` y `build_db.py` fueron corregidos para manejar encoding UTF-8 en consolas Windows (cp1252 no soporta emojis). Se agregó `io.TextIOWrapper` al inicio de ambos archivos.

## Tareas pendientes (prioridad)

### Tarea 1 — Scraping de fuentes oficiales `[P0 — Crítico]`
- [ ] Adaptar `scripts/scrape_official.py` a estructura real de los sitios
- [ ] Scraper SPIJ: buscar leyes de TARGET_LAWS (ej: Decreto Legislativo 1186)
- [ ] Scraper TC: buscar sentencias de TARGET_JURISPRUDENCE (ej: Exp. 00413-2022-PHC/TC)
- [ ] Scraper El Peruano: buscar decretos de emergencia vigentes 2026
- [ ] Guardar resultados raw en `data/PE/sources/raw/` para auditoría
- [ ] Respetar rate limits (mínimo 2 segundos entre requests)
- [ ] No modificar JSON de datos existentes — solo descargar textos oficiales

### Tarea 2 — Buscador de lenguaje natural `[P1 — Importante]`
- [ ] Crear `scripts/search.py` con función `search_situation(query) -> situation_id`
- [ ] Usar `situations.keywords` y `situations.natural_queries` para matching
- [ ] Implementar búsqueda fuzzy simple (sin ML, sin embeddings)
- [ ] Debe funcionar offline (SQLite + Python puro)
- [ ] Queries de prueba mínimas:
  - "me piden el DNI"
  - "quieren ver mi celular"
  - "me llevan a la comisaría"
  - "me encuentran con marihuana"
  - "puedo grabar al policía"
  - "cuánto tiempo me pueden retener"
- [ ] Tests con al menos 20 queries de ejemplo

### Tarea 3 — CLI de consulta `[P1 — Importante]`
- [ ] Crear `scripts/cli.py`
- [ ] Uso: `python scripts/cli.py "me encuentran con marihuana"`
- [ ] Salida esperada:
  - Situación detectada
  - Tus derechos (con notas contextuales)
  - Qué hacer paso a paso (con scripts pregrabados)
  - Límites de tiempo
  - A quién llamar
- [ ] Usar la DB generada por `build_db.py`

### Tarea 4 — Tests automatizados `[P1 — Importante]`
- [ ] Crear `tests/test_data_integrity.py` — JSON válidos, IDs no duplicados
- [ ] Crear `tests/test_build.py` — build genera DB correcta
- [ ] Crear `tests/test_search.py` — buscador encuentra situaciones correctas
- [ ] Crear `tests/test_cross_references.py` — referencias cruzadas válidas
- [ ] Usar pytest, ejecutable con `make test`

### Tarea 5 — GitHub Actions CI `[P2 — Deseable]`
- [ ] Crear `.github/workflows/validate.yml`
- [ ] Ejecutar en cada push y PR: validate_sources.py, build_db.py, tests
- [ ] Fallar si hay errores en datos o build

### Futuro (sin asignar)
- [ ] App móvil MVP (React Native o Flutter, offline-first)
- [ ] Botón de pánico (grabación + GPS + alertas)
- [ ] Temporizador legal
- [ ] Reporte anónimo de intervenciones
- [ ] Mapa de calor de abusos

## Reglas para agentes de IA

1. **No inventar datos legales.** Si no estás seguro de un artículo o sentencia, déjalo como TODO con nota.
2. **No modificar datos existentes sin verificar.** Los datos actuales fueron investigados exhaustivamente.
3. **Mantener formato JSON consistente.** Ver docs/DATA_FORMAT.md.
4. **Probar build después de cambios en datos.** Correr: `python3 scripts/build_db.py --country PE`
5. **Commits descriptivos.** `data: add protest situation PE` no `update files`
6. **Documentar fuentes.** Todo dato legal nuevo necesita `source_id` que apunte a `legal_sources`.
7. **No romper offline.** La consulta de derechos debe funcionar sin internet.
8. **Respetar la estructura de directorios.** No reorganizar sin discutir en un Issue.

## Cómo probar

```bash
# Build la base de datos
python3 scripts/build_db.py --country PE

# Verificar que funciona
python3 -c "
import sqlite3
conn = sqlite3.connect('build/truths_and_rights_pe.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM situations')
print(f'Situaciones: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM rights')
print(f'Derechos: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM legal_sources')
print(f'Fuentes: {c.fetchone()[0]}')
conn.close()
"
```

## Contexto humano

Este proyecto nació de la experiencia directa con abuso policial en Perú. No es académico ni teórico — existe porque ciudadanos fueron detenidos ilegalmente, maltratados, y descubrieron después que tenían derechos que nadie les informó. El rigor legal no es opcional; la información incorrecta puede empeorar la situación de alguien en una intervención real.
