# Automatizacion del proyecto

Guia completa de como funciona el pipeline automatizado de Truths and Rights.

---

## Vista general

```
                    AUTOMATICO (GitHub Actions)
                    ===========================

  Lunes 9AM Lima         Dia 1 y 15          Dia 1 del mes
       |                    |                      |
       v                    v                      v
  check-emergency.yml  check-updates.yml     full-scrape.yml
       |                    |                      |
       v                    v                      v
  Decreto vencido?     Fuentes cambiaron?    Textos nuevos?
       |                    |                      |
       v                    v                      v
  Crea Issue urgente   Crea Issue revision   Sube artifacts
       |                    |                  + Crea Issue
       |                    |                      |
       +--------------------+----------------------+
                            |
                            v
                   verification_history.jsonl
                   (audit trail versionado)


                    MANUAL (tu decides)
                    ===================

  Cambias datos en data/PE/ ---> push a main
       |
       v
  validate.yml (tests, build DB, validacion)
       |
       v
  deploy-site.yml (regenera portal publico)
       |
       v
  https://ellokoakrata.github.io/truths-and-rights/
```

---

## Los 5 workflows explicados

### 1. `check-emergency.yml` — Verificacion de emergencia (semanal)

**Cuando corre:** Cada lunes a las 14:00 UTC (9:00 AM hora de Lima).

**Que hace:**
1. Ejecuta `python scrape_official.py --check-emergency --output-json`
2. Lee `data/PE/contexts/contexts.json` y revisa la fecha `end_date` del decreto
3. Calcula cuantos dias faltan para que venza
4. Si el decreto **ya vencio** o **le quedan menos de 7 dias**: crea un Issue automatico

**Que Issue crea:**
- Titulo: "Estado de emergencia: verificar renovacion de decreto"
- Labels: `legal-data`, `urgent`, `country:PE`
- Contenido: decreto, estado, fecha, y checklist de acciones

**De-duplicacion:** Si ya existe un Issue abierto con esos labels, no crea otro.

**Lo que guarda:** Agrega un registro a `verification_history.jsonl` y hace commit automatico.

**Por que importa:** El decreto DS N° 006-2026-PCM vence el 19 de febrero de 2026. Si se renueva (como pasa casi siempre), hay que actualizar las fechas en los datos. Si no se renueva, hay que cambiar el contexto a "normal" y los derechos suspendidos vuelven a estar vigentes. La app podria dar informacion **peligrosamente incorrecta** si no se actualiza.

---

### 2. `check-updates.yml` — Verificacion de fuentes (quincenal)

**Cuando corre:** Dia 1 y 15 de cada mes a las 14:00 UTC.

**Que hace:**
1. Ejecuta `python scrape_official.py --check-updates --output-json`
2. Lee todos los JSON de `data/PE/sources/` (las 43+ fuentes legales)
3. Busca fuentes con campo `last_modified` (significa que fueron editadas)
4. Tambien verifica el estado de emergencia
5. Si encuentra fuentes desactualizadas: crea Issue

**Que Issue crea:**
- Titulo: "Fuentes legales: revision de vigencia necesaria"
- Labels: `legal-data`, `legal-review`
- Contenido: lista de fuentes que necesitan revision

**Por que importa:** Las leyes cambian. El Congreso puede modificar el Codigo Procesal Penal, el TC puede emitir una nueva sentencia vinculante, o pueden derogar un decreto legislativo. Si no verificamos, la app podria citar una ley que ya no existe o que dice algo diferente.

---

### 3. `full-scrape.yml` — Scrape completo (mensual)

**Cuando corre:** Dia 1 de cada mes a las 06:00 UTC.

**Que hace:**
1. Ejecuta `python scrape_official.py --all --output-json`
2. Intenta descargar textos actualizados de TC, El Peruano y Congreso
3. Usa `continue-on-error: true` (los sitios del gobierno peruano se caen con frecuencia)
4. Sube los archivos raw descargados como **artifacts** (se guardan 90 dias)
5. Si detecta cambios: crea Issue

**Artifacts:** Los archivos HTML/JSON descargados de los sitios oficiales quedan en la pestana Actions > Artifacts del run. Sirven para comparar contra lo que tenemos.

**Por que importa:** Es la unica forma de detectar si el **texto** de una ley cambio, no solo si el status cambio. Por ejemplo, si modifican un articulo del CPP, el status puede seguir como "vigente" pero el texto ya no dice lo mismo.

---

### 4. `validate.yml` — Validacion (cada push/PR)

**Cuando corre:** Cada push a `main` o PR, **solo si cambiaron archivos en** `data/`, `scripts/`, `schema/` o `tests/`.

**Que hace:**
1. Valida todos los JSON con `validate_sources.py`
2. Construye la base de datos SQLite
3. Corre los tests con pytest
4. Verifica que la DB tenga minimos: 9+ situaciones, 20+ derechos, 40+ fuentes

**Por que importa:** Es la red de seguridad. Si alguien (o tu mismo) edita un JSON y lo deja mal formateado, o borra un derecho por accidente, este workflow falla y bloquea el merge.

**Path filters:** Antes corria en TODOS los pushes. Ahora solo corre cuando se tocan archivos relevantes. Si solo editas el README, no se dispara (ahorra minutos de CI).

---

### 5. `deploy-site.yml` — Deploy del portal (automatico)

**Cuando corre:** Cada push a `main` que modifique `data/`, `scripts/generate_site.py` o `docs/`.

**Que hace:**
1. Instala dependencias
2. Construye la DB con `build_db.py`
3. Genera el sitio estatico con `generate_site.py`
4. Despliega a GitHub Pages

**Resultado:** El portal en `https://ellokoakrata.github.io/truths-and-rights/` siempre refleja los datos mas recientes.

**Requisito:** GitHub Pages debe estar habilitado en Settings > Pages > Source: GitHub Actions.

---

## Archivos clave de la automatizacion

### `scripts/scrape_official.py`

El script principal. Ahora tiene 3 mejoras:

| Mejora | Detalle |
|---|---|
| `--output-json` | Escribe resultado a `data/PE/sources/raw/latest_check.json` |
| Retry con backoff | 3 reintentos, backoff x2, para status 429/500/502/503/504 |
| Codigos de salida | `0` = sin cambios, `1` = cambios detectados, `2` = errores |

Los workflows leen el `latest_check.json` para decidir si crear Issues.

### `scripts/history.py`

Modulo de historial. Dos funciones:

- `append_to_history(report)` — Agrega una linea JSON a `verification_history.jsonl`
- `read_history(limit)` — Lee las ultimas N entradas

Cada linea del historial tiene:
```json
{
  "timestamp": "2026-02-08T01:09:48",
  "check_type": "emergency",
  "verified_count": 1,
  "needs_update_count": 0,
  "errors_count": 0,
  "summary": "Emergencia: todo vigente",
  "details": { "needs_update": [], "errors": [] }
}
```

### `scripts/check_scraper_health.py`

Health check de los sitios gubernamentales. Hace HEAD request a:
- TC (tc.gob.pe)
- El Peruano (diariooficial.elperuano.pe)
- Congreso (leyes.congreso.gob.pe)
- SPIJ (spij.minjus.gob.pe)

Exit code `0` si todos responden, `1` si alguno fallo.

### `scripts/generate_site.py`

Generador del portal publico. Lee los JSON de `data/PE/` y genera HTML puro (sin frameworks, sin dependencias). Genera:

| Pagina | Contenido |
|---|---|
| `index.html` | Portada con estado de emergencia, stats, links |
| `situaciones.html` | Las 9 situaciones con derechos, acciones, contactos |
| `derechos.html` | Los 20+ derechos agrupados por categoria |
| `fuentes.html` | Las 43+ fuentes con tabla, status y links oficiales |
| `emergencia.html` | Estado de emergencia: que se suspende y que NO |
| `mitos.html` | 7 mitos desmentidos con fuentes |
| `contactos.html` | Telefonos, WhatsApp, emails de emergencia |
| `verificacion.html` | Dashboard de frescura de datos |
| `status.json` | JSON para badges y consumo programatico |

---

## Archivos que se versionan vs. los que no

| Archivo | Se versiona? | Por que |
|---|---|---|
| `data/PE/verification_history.jsonl` | **Si** | Es el audit trail del proyecto |
| `data/PE/sources/raw/*` | **No** (.gitignore) | Son descargas temporales |
| `site/*` | **No** (.gitignore) | Se genera en CI |
| `build/*` | **No** (.gitignore) | Se genera en CI |

---

## A que estar atento

### Alertas criticas (actuar inmediatamente)

1. **Issue con label `urgent`** — Significa que un decreto de emergencia vencio o esta por vencer. Si vencio y no fue renovado, los derechos suspendidos vuelven a estar vigentes. Si fue renovado con otro numero, hay que actualizar los datos.

2. **Workflow falla con exit code 2** — Significa error en el scraper. Puede ser que un sitio gubernamental cambio su estructura HTML, o que esta caido por mas de lo normal.

### Alertas importantes (actuar en 1-2 dias)

3. **Issue con label `legal-review`** — Una fuente legal puede haber cambiado. Verificar en la fuente oficial y actualizar si es necesario.

4. **Health check falla** — Un sitio gubernamental esta caido. Normalmente se recuperan solos, pero si persiste por mas de una semana, puede significar que cambiaron la URL o la estructura.

### Revision periodica (mensual)

5. **Revisar la pestana Actions** — Verificar que los workflows estan corriendo segun su calendario. Si un cron no corre, puede ser que GitHub lo desactivo por inactividad del repo (pasa despues de 60 dias sin commits).

6. **Revisar `verification_history.jsonl`** — El dashboard en el portal muestra el historial. Si ves un hueco (semanas sin verificaciones), algo fallo silenciosamente.

7. **Revisar artifacts del scrape mensual** — Descargar los HTML/JSON raw y compararlos contra lo que tenemos para detectar cambios sutiles en textos legales.

---

## Comandos locales utiles

```bash
# Verificar estado de emergencia ahora
python scripts/scrape_official.py --check-emergency --output-json

# Verificar vigencia de fuentes ahora
python scripts/scrape_official.py --check-updates --output-json

# Scrape completo
python scripts/scrape_official.py --all --output-json

# Health check de sitios
python scripts/check_scraper_health.py

# Generar portal localmente
make site

# Ver portal en el navegador
make serve

# Correr tests
make test
```

---

## Que hacer cuando llega un Issue automatico

### Caso: decreto de emergencia vencido

```
1. Ir a diariooficial.elperuano.pe
2. Buscar "decreto supremo estado de emergencia"
3. Si fue renovado:
   a. Anotar el nuevo numero de decreto (ej: DS N° 012-2026-PCM)
   b. Anotar nuevas fechas y regiones
   c. Editar data/PE/contexts/contexts.json
   d. Editar data/PE/metadata.json
   e. make test
   f. Commit y push
4. Si NO fue renovado (la emergencia termino):
   a. Cambiar is_currently_active a false en contexts.json
   b. Quitar de active_emergencies en metadata.json
   c. make test
   d. Commit y push
5. Cerrar el Issue con comentario de que se hizo
```

### Caso: fuente legal modificada

```
1. Ir a la fuente oficial (SPIJ, TC, El Peruano)
2. Verificar que cambio exactamente
3. Si el cambio es sustantivo (afecta derechos):
   a. Actualizar el JSON de la fuente
   b. Revisar si afecta derechos en rights.json
   c. Revisar si afecta situaciones
   d. Idealmente: revision por abogado
   e. make test
   f. Commit y push
4. Si el cambio es formal (no afecta contenido):
   a. Actualizar fecha o status si aplica
   b. make test
   c. Commit y push
5. Cerrar el Issue
```

---

## Configuracion inicial de GitHub Pages (solo una vez)

El portal se publica en GitHub Pages. Esta configuracion solo se hace **una vez** al crear el repo:

1. Ir a **Settings** > **Pages** en el repositorio de GitHub
2. En **Source**, cambiar de "Deploy from a branch" a **GitHub Actions**
3. No seleccionar ningun template sugerido (Jekyll, Static HTML) — ya tenemos nuestro propio workflow `deploy-site.yml`
4. Listo. A partir de ahora, cada push a `main` que toque `data/`, `scripts/generate_site.py` o `docs/` regenera y publica el sitio automaticamente

Si el primer deploy falla (porque Pages no estaba configurado cuando el workflow corrio), ir a Actions > "Deploy portal publico" > "Re-run all jobs". Con Pages ya configurado, el re-run funciona.

**URL del portal:** https://ellokoakrata.github.io/truths-and-rights/

---

## Principio fundamental

**Los workflows NUNCA modifican datos legales automaticamente.** Solo crean Issues para revision humana. Esto es intencional: datos legales incorrectos pueden poner en riesgo a personas reales. Un robot puede detectar que algo cambio, pero solo un humano (idealmente un abogado) debe decidir como actualizar la informacion.
