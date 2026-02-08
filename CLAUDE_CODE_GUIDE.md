# Guía de inicio con Claude Code

## Paso 0: Preparar el repo

```bash
# En tu terminal (NO en Claude Code todavía)
cd ~/proyectos  # o donde quieras
mkdir truths-and-rights
# Descomprime el último zip aquí
# Borra schema/sample_data.sql si quieres limpiar

cd truths-and-rights
git init
git add .
git commit -m "init: Truths and Rights v0.2.0 — schema, datos PE, scripts"
```

## Paso 1: Primera instrucción para Claude Code

Copia y pega esto como tu primer mensaje:

---

```
Lee el archivo AI_BRIEF.md completo. Ese es tu contexto del proyecto.

Luego:

1. Instala las dependencias: pip install -r requirements.txt
2. Corre el validador: python3 scripts/validate_sources.py --country PE
3. Corre el build: python3 scripts/build_db.py --country PE
4. Confirma que todo funciona y dime qué tienes disponible.

No modifiques nada todavía. Solo familiarízate con la estructura.
```

---

## Paso 2: Scraping de fuentes oficiales

Una vez que confirmó que todo funciona:

---

```
Ahora necesito que trabajes en scripts/scrape_official.py.

El script tiene 3 scrapers (SPIJ, TC, El Peruano) con la estructura lista
pero necesitan adaptarse a las URLs reales.

Tareas en orden:

1. Prueba acceder a https://spij.minjus.gob.pe — explora la estructura
   del sitio y adapta SPIJScraper para buscar y descargar textos de las
   leyes listadas en TARGET_LAWS.

2. Prueba acceder a https://www.tc.gob.pe/jurisprudencia/ — adapta
   TCScraper para buscar las sentencias en TARGET_JURISPRUDENCE.

3. Prueba acceder a https://diariooficial.elperuano.pe — adapta
   ElPeruanoScraper para buscar decretos de emergencia vigentes.

Guarda todo el contenido raw en data/PE/sources/raw/ para auditoría.
Respeta rate limits (2 segundos entre requests mínimo).
No modifiques los JSON de datos existentes — solo descarga los textos
oficiales para comparación y futura actualización.

Haz commits descriptivos por cada scraper que funcione.
```

---

## Paso 3: Buscador de lenguaje natural

---

```
Crea un módulo de búsqueda que matchee consultas en lenguaje natural
del usuario con las situaciones en la base de datos.

La DB tiene:
- situations.keywords (palabras clave separadas por coma)
- situations.natural_queries (consultas reales separadas por |)

Necesito un script scripts/search.py que:
1. Reciba una consulta: "me quieren revisar el celular"
2. Busque en keywords y natural_queries
3. Retorne la situación más relevante con sus derechos, acciones y contactos

Usa sqlite3 contra build/truths_and_rights_pe.db.
Empieza simple (keyword matching + fuzzy), no necesitamos embeddings todavía.
Debe funcionar offline.

Prueba con estas consultas reales:
- "me piden el DNI"
- "quieren ver mi celular"
- "me llevan a la comisaría"
- "me encuentran con marihuana"
- "puedo grabar al policía"
- "cuánto tiempo me pueden retener"
```

---

## Notas importantes para Claude Code

- El proyecto NO tiene acceso a dominios externos excepto los listados
  en la configuración de red. Si Claude Code no puede acceder a SPIJ
  o TC, puede que necesites correr el scraping tú mismo y pasar los
  resultados.
- Los datos legales existentes fueron investigados exhaustivamente.
  Claude Code NO debe modificarlos sin verificación.
- Commits en español están bien.
