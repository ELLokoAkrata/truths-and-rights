# Instrucciones para Claude Code

## Setup inicial (una sola vez)

```bash
# 1. Ir al directorio del proyecto
cd ~/truths-and-rights

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar git
git init
git add .
git commit -m "init: truths and rights v0.2.0 - base de datos legal completa PE"

# 4. Verificar que todo funciona
python3 scripts/validate_sources.py --country PE
python3 scripts/build_db.py --country PE
```

## Primer prompt para Claude Code

Copia y pega esto:

---

Lee el archivo AI_BRIEF.md completo. Ese es el documento maestro del proyecto.

Después lee estos archivos en orden:
1. README.md (visión general)
2. docs/DATA_FORMAT.md (formato de datos)
3. docs/LEGAL_METHODOLOGY.md (metodología)

Luego verifica que el proyecto funciona:
1. Correr: python3 scripts/validate_sources.py --country PE
2. Correr: python3 scripts/build_db.py --country PE
3. Verificar que build/truths_and_rights_pe.db existe y tiene datos

Confirma qué entendiste del proyecto y qué ves como próximos pasos.

---

## Tareas para darle después (en orden de prioridad)

### Tarea 1: Probar scraping contra URLs reales
```
El script scripts/scrape_official.py tiene scrapers para SPIJ, TC y El Peruano 
pero necesita adaptarse a la estructura actual de esos sitios. 

Prueba estas URLs y adapta los parsers:
- https://spij.minjus.gob.pe (buscar "Decreto Legislativo 1186")
- https://www.tc.gob.pe/jurisprudencia/ (buscar expediente 00413-2022-PHC/TC)
- https://diariooficial.elperuano.pe (buscar "estado de emergencia 2026")

Guarda los resultados raw en data/PE/sources/raw/ para auditoría.
No modifiques los JSON de datos existentes — solo el script de scraping.
```

### Tarea 2: Buscador de lenguaje natural
```
Necesitamos un módulo que reciba texto del usuario como:
- "me quieren revisar la mochila"
- "cuánto tiempo pueden tenerme"
- "es legal grabar a la policía"

Y devuelva la situación más relevante de la base de datos SQLite.

Usa los campos situations.keywords y situations.natural_queries para el match.
Implementa búsqueda fuzzy simple (no necesita ML por ahora).
Debe funcionar offline (SQLite + Python puro o algo embebible).

Crea: scripts/search.py con una función search_situation(query) → situation_id
Incluye tests con al menos 20 queries de ejemplo.
```

### Tarea 3: CLI de consulta
```
Crea un CLI simple que simule la experiencia de la app:

python3 scripts/cli.py "me encuentran con marihuana"

Salida esperada:
- Situación detectada
- Tus derechos (con notas contextuales)
- Qué hacer paso a paso (con scripts)
- Límites de tiempo
- A quién llamar

Usa la DB generada por build_db.py.
```

### Tarea 4: Tests automatizados
```
Crea tests/ con:
- test_data_integrity.py (que todos los JSON sean válidos, IDs no duplicados)
- test_build.py (que el build genere DB correcta)
- test_search.py (que el buscador encuentre situaciones correctas)
- test_cross_references.py (que todas las referencias cruzadas sean válidas)

Usa pytest. Que se puedan correr con: make test
```

### Tarea 5: GitHub Actions CI
```
Crea .github/workflows/validate.yml que:
- Se ejecute en cada push y PR
- Corra validate_sources.py
- Corra build_db.py
- Corra los tests
- Falle si hay errores en datos o build
```
