# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

## [0.2.1] - 2026-02-07

### Setup inicial con Claude Code

**Sesión:** Primera integración con Claude Code para desarrollo asistido.

#### Realizado
- Lectura completa de documentos del proyecto: AI_BRIEF.md, README.md, DATA_FORMAT.md, LEGAL_METHODOLOGY.md
- Instalación de dependencias verificada (requests, beautifulsoup4, lxml ya instalados)
- Validación de datos ejecutada: **0 errores, 0 advertencias**
  - 43 fuentes legales, 20 derechos, 17 acciones, 9 situaciones, 7 contactos, 7 mitos, 2 contextos
- Build de base de datos ejecutado: `truths_and_rights_pe.db` generada (256 KB)
- Verificación de integridad de la DB: todas las tablas pobladas correctamente

#### Corregido
- Fix de encoding UTF-8 en `scripts/validate_sources.py` y `scripts/build_db.py` para compatibilidad con consola Windows (cp1252 no soporta emojis en print)

#### Tareas pendientes (por orden de prioridad)

**Tarea 1 — Scraping de fuentes oficiales** `[P0]`
- Adaptar `scripts/scrape_official.py` a las URLs reales de SPIJ, TC y El Peruano
- Probar contra: spij.minjus.gob.pe, tc.gob.pe/jurisprudencia, diariooficial.elperuano.pe
- Guardar resultados raw en `data/PE/sources/raw/`
- No modificar los JSON de datos existentes

**Tarea 2 — Buscador de lenguaje natural** `[P1]`
- Crear `scripts/search.py` con función `search_situation(query) -> situation_id`
- Usar campos `situations.keywords` y `situations.natural_queries` para matching
- Búsqueda fuzzy simple (sin ML), offline (SQLite + Python puro)
- Tests con al menos 20 queries de ejemplo

**Tarea 3 — CLI de consulta** `[P1]`
- Crear `scripts/cli.py` que simule la experiencia de la app
- Entrada: `python scripts/cli.py "me encuentran con marihuana"`
- Salida: situación detectada, derechos, acciones paso a paso, límites de tiempo, contactos
- Usar la DB generada por build_db.py

**Tarea 4 — Tests automatizados** `[P1]`
- Crear `tests/test_data_integrity.py` (JSON válidos, IDs no duplicados)
- Crear `tests/test_build.py` (build genera DB correcta)
- Crear `tests/test_search.py` (buscador encuentra situaciones correctas)
- Crear `tests/test_cross_references.py` (referencias cruzadas válidas)
- Usar pytest, ejecutable con `make test`

**Tarea 5 — GitHub Actions CI** `[P2]`
- Crear `.github/workflows/validate.yml`
- Ejecutar en cada push y PR: validate_sources.py, build_db.py, tests
- Fallar si hay errores en datos o build

## [0.2.0] - 2026-02-07

### Agregado
- Base de datos completa de Perú poblada en formato JSON
  - 43 fuentes legales (Constitución, CPP, CP, DL, jurisprudencia, CIDH)
  - 20 derechos documentados con fuentes verificables
  - 17 acciones con scripts pregrabados
  - 9 situaciones completas
  - 7 contactos de emergencia
  - 7 mitos desmontados
  - 7 sustancias con cantidades legales
  - 2 contextos (normal + estado de emergencia)
- Build script funcional: `python3 scripts/build_db.py --country PE` → SQLite 256 KB
- Validador de datos: `python3 scripts/validate_sources.py` → 0 errores
- Script de scraping para fuentes oficiales (SPIJ, TC, El Peruano)
- AI_BRIEF.md — documento para que cualquier agente de IA pueda trabajar en el proyecto
- Makefile con tareas comunes
- requirements.txt

### Validación
- 0 errores, 0 advertencias en validación completa
- Build exitoso, DB funcional con consultas probadas

## [0.1.0] - 2026-02-07

### Agregado
- Schema de base de datos (12 tablas, índices, vistas)
- Documentación del schema con diagramas de flujo
- Datos de ejemplo: escenario cannabis < 8g (Perú)
- README del proyecto
- Guía de contribución (CONTRIBUTING.md)
- Código de conducta (CODE_OF_CONDUCT.md)
- Metodología legal (LEGAL_METHODOLOGY.md)
- Guía para agregar países (ADDING_A_COUNTRY.md)
- Formato de datos (DATA_FORMAT.md)
- Licencia GPL v3

### País: Perú (PE)
- 6 fuentes legales documentadas
- 4 situaciones iniciales
- 8 derechos documentados
- 8 acciones con scripts pregrabados
- 4 contactos de emergencia
- 3 mitos desmontados
- 3 sustancias con cantidades legales
- 3 niveles de fuerza policial

### Próximo
- Completar los 8 escenarios del marco legal
- Script de build (JSON → SQLite)
- Script de scraping de fuentes oficiales
- Validación automática de datos
