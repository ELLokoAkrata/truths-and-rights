# Guía para contribuir / Contributing Guide

¡Gracias por querer aportar! Este proyecto es de todos y para todos.

---

## Principios del proyecto

1. **Fuentes oficiales o nada.** Cada dato legal debe ser verificable con una fuente oficial. Sin excepciones.
2. **Lenguaje simple.** Si un ciudadano promedio no lo entiende en 10 segundos, hay que reescribirlo.
3. **Offline first.** Todo lo que sea consulta de derechos debe funcionar sin internet.
4. **Privacidad máxima.** Mínimos datos del usuario, máxima protección.
5. **No partidista.** Esto no es de izquierda ni derecha. Es de derechos.

---

## ¿Cómo empezar?

### 1. Fork y clone

```bash
git clone https://github.com/tu-usuario/truths-and-rights.git
cd truths-and-rights
```

### 2. Elige en qué trabajar

Mira los [Issues abiertos](https://github.com/truths-and-rights/truths-and-rights/issues) o elige según tu perfil:

---

## Contribuciones por perfil

### 🧑‍⚖️ Abogados / Estudiantes de derecho

**Lo que más necesitamos.** La app es tan buena como la precisión de sus datos legales.

**Puedes:**
- Verificar datos existentes en `data/PE/`
- Agregar jurisprudencia nueva (sentencias del TC, Corte IDH)
- Corregir interpretaciones legales
- Agregar escenarios que falten
- Revisar que las fuentes estén vigentes

**Formato para agregar una fuente legal:**
```json
{
  "id": "identificador_unico",
  "source_type": "constitucion|codigo_procesal|decreto_legislativo|ley|jurisprudencia|tratado_internacional",
  "name": "Nombre oficial del cuerpo legal",
  "article": "Artículo específico",
  "full_text": "Texto literal oficial (copiar exacto)",
  "summary": "Explicación en lenguaje que entienda cualquier persona",
  "publication_date": "YYYY-MM-DD",
  "official_url": "URL de fuente oficial (SPIJ, TC, El Peruano)",
  "status": "vigente|modificado|derogado"
}
```

**Reglas para datos legales:**
- SIEMPRE incluir la fuente oficial con URL
- SIEMPRE verificar que la norma esté vigente
- El campo `summary` debe ser comprensible para alguien de 16 años
- Si una ley fue modificada, indicar la modificación más reciente
- En caso de duda, abrir un Issue para discutirlo

---

### 💻 Programadores

**Stack actual:** SQLite, Python (scripts), por definir app móvil.

**Puedes:**
- Mejorar scripts de build y validación en `scripts/`
- Trabajar en el buscador de lenguaje natural
- Desarrollar la app móvil (MVP)
- Optimizar para offline
- Crear tests automatizados para los datos

**Convenciones de código:**
- Commits en español o inglés (lo que te sea natural)
- Un commit = un cambio lógico
- PR con descripción clara de qué cambia y por qué
- Tests para cualquier funcionalidad nueva

---

### 📝 Escritores / Comunicadores

**Puedes:**
- Simplificar textos legales a lenguaje ciudadano
- Escribir los "scripts" (textos sugeridos para decir al policía)
- Redactar la sección de mitos y realidades
- Crear contenido educativo
- Traducir documentación

**Criterio de escritura:**
- Imagina que le explicas a tu mamá, tu tío o tu vecino
- Nada de jerga legal innecesaria
- Oraciones cortas y directas
- Si puedes decirlo en 10 palabras, no uses 30

---

### 🎨 Diseñadores

**Puedes:**
- Diseñar la UI/UX de la app
- Crear iconografía para situaciones
- Trabajar en accesibilidad (tamaños, contraste, lectores de pantalla)
- Diseñar el flujo del botón de pánico

**Criterios de diseño:**
- El usuario está estresado, con miedo, posiblemente de noche
- Botones grandes, texto legible, colores de alto contraste
- Máximo 2 toques para llegar a la información
- Debe funcionar con una mano (la otra puede estar ocupada)

---

### 🌎 Activistas / ONGs / Otros países

**Puedes:**
- Agregar el marco legal de tu país
- Conectar con organizaciones de DDHH
- Difundir el proyecto
- Reportar situaciones que la app debería cubrir

**Para agregar un nuevo país:**
Lee [ADDING_A_COUNTRY.md](docs/ADDING_A_COUNTRY.md) — necesitas:
1. Las leyes sobre intervenciones policiales de tu país
2. Los escenarios más comunes
3. Contactos de emergencia institucionales
4. Idealmente, revisión de un abogado local

---

## Scripts y herramientas (solo para desarrolladores/IAs)

Los scripts de este proyecto son herramientas de desarrollo y mantenimiento.
**El usuario final no los ejecuta** — solo usa la app movil, que ya tiene todo empaquetado.

### Quien ejecuta cada script

| Script | Quien lo corre | Proposito |
|---|---|---|
| `scripts/build_db.py` | Desarrollador / IA / CI | Genera la DB SQLite desde los JSON |
| `scripts/validate_sources.py` | Desarrollador / IA / CI | Verifica integridad de los datos |
| `scripts/scrape_official.py` | Desarrollador / IA | Verifica que las leyes siguen vigentes |
| `scripts/search.py` | La app internamente | Motor de busqueda (libreria) |
| `scripts/cli.py` | Desarrollador / IA | Probar la experiencia antes de construir la app |
| `pytest` | Desarrollador / IA / CI | Verificar que nada se rompio |

### Calendario de mantenimiento recomendado

> **Nota:** Las tres primeras tareas estan **automatizadas con GitHub Actions**.
> Los workflows crean Issues automaticamente cuando detectan cambios.
> La ejecucion manual sigue siendo posible para verificaciones inmediatas.

| Tarea | Frecuencia | Comando | Automatizado |
|---|---|---|---|
| **Verificar estado de emergencia** | Cada semana | `python scripts/scrape_official.py --check-emergency` | Si (lunes 9 AM Lima) |
| **Verificar vigencia de fuentes** | Cada 2 semanas | `python scripts/scrape_official.py --check-updates` | Si (dia 1 y 15) |
| **Scrape completo de fuentes** | Cada mes | `python scripts/scrape_official.py --all` | Si (dia 1) |
| **Correr tests** | Antes de cada commit | `python -m pytest tests/ -v` | Si (cada push/PR) |
| **Validar datos** | Antes de cada commit | `python scripts/validate_sources.py --country PE` | Si (cada push/PR) |
| **Rebuild de la DB** | Despues de modificar datos | `python scripts/build_db.py --country PE` | No |

### Por que estas frecuencias

- **Estado de emergencia (semanal):** Los decretos de emergencia en Peru se renuevan cada 30-60 dias. Verificar semanalmente evita que la app informe derechos suspendidos cuando ya no lo estan (o viceversa).
- **Vigencia de fuentes (quincenal):** Las leyes no cambian a diario, pero modificaciones al Codigo Procesal Penal o nuevas sentencias del TC pueden ocurrir en cualquier momento.
- **Scrape completo (mensual):** Descargar los textos oficiales actuales para comparar contra lo que tenemos y detectar cambios.
- **Tests y validacion (cada commit):** Esto lo hace GitHub Actions automaticamente en cada push y PR.

### Flujo de actualizacion de datos

```
1. Correr check-emergency y check-updates
2. Si algo cambio:
   a. Investigar el cambio en la fuente oficial
   b. Actualizar el JSON correspondiente en data/PE/
   c. Correr validate + build + tests
   d. Commit con descripcion del cambio legal
   e. Si es critico: publicar nueva version de la app
```

---

## Flujo de contribucion

```
1. Abre un Issue describiendo qué quieres hacer
2. Fork del repositorio
3. Crea una rama: git checkout -b tipo/descripcion
   Ejemplos:
   - data/add-scenario-protest
   - legal/update-dl1186
   - fix/typo-readme
   - feat/search-engine
4. Haz tus cambios
5. Abre un Pull Request referenciando el Issue
6. Revisión por al menos 1 persona
   - Si es dato legal: revisión por abogado o verificación de fuente
   - Si es código: revisión por otro dev
7. Merge
```

---

## Tipos de Issues

Usa estas etiquetas:

| Etiqueta | Descripción |
|---|---|
| `legal-data` | Agregar o corregir datos legales |
| `legal-review` | Necesita revisión de abogado |
| `bug` | Algo no funciona |
| `feature` | Funcionalidad nueva |
| `docs` | Documentación |
| `good-first-issue` | Ideal para empezar |
| `help-wanted` | Se necesita ayuda |
| `country:PE` | Específico de Perú |
| `myth-busting` | Contenido para sección educativa |

---

## Lo que NO aceptamos

- Datos legales sin fuente oficial verificable
- Contenido partidista o que promueva una agenda política
- Código malicioso o que comprometa la privacidad del usuario
- Contenido que promueva violencia contra policías o cualquier persona
- Información desactualizada presentada como vigente

---

## ¿Dudas?

Abre un Issue con la etiqueta `question` o únete a las [Discussions](https://github.com/truths-and-rights/truths-and-rights/discussions).

Ninguna pregunta es tonta. Si algo no está claro, es culpa de la documentación, no tuya.
