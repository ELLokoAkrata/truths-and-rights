# Truths and Rights 🛡️

**App ciudadana de derechos ante intervenciones policiales.**

> Porque conocer tus derechos no debería requerir un título en derecho.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Country: Peru](https://img.shields.io/badge/Country-Peru-red.svg)](#)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](#)
[![Portal de Datos](https://img.shields.io/badge/Portal-Live-brightgreen.svg)](https://ellokoakrata.github.io/truths-and-rights/)
[![Validar datos y tests](https://github.com/ELLokoAkrata/truths-and-rights/actions/workflows/validate.yml/badge.svg)](https://github.com/ELLokoAkrata/truths-and-rights/actions/workflows/validate.yml)

### [Ver el portal de datos en vivo](https://ellokoakrata.github.io/truths-and-rights/)

---

## ¿Qué es esto? / What is this?

**ES:** Una app móvil que te dice tus derechos en tiempo real durante una intervención policial. Buscas tu situación ("me quieren revisar la mochila"), y la app te responde con tus derechos, qué hacer paso a paso, los límites legales, y a quién llamar si todo se complica. Funciona offline porque en la calle no siempre hay señal.

**EN:** A mobile app that tells you your rights in real-time during a police intervention. You search your situation ("they want to search my backpack"), and the app responds with your rights, step-by-step actions, legal time limits, and who to call if things escalate. Works offline because you don't always have signal on the street.

---

## ¿Por qué existe? / Why does this exist?

En Perú, entre enero y febrero de 2025 se registraron **698 denuncias por conductas indebidas policiales** — una cada 105 minutos. Y esas son solo las denunciadas.

El marco legal peruano tiene protecciones robustas para los ciudadanos: plazos máximos de retención, prohibición de registros arbitrarios, protección de comunicaciones privadas. Pero existe una **brecha enorme** entre lo que dice la ley y lo que pasa en la calle.

Esta app ataca la **asimetría de conocimiento**: el policía sabe (o cree saber) qué puede hacer; el ciudadano no sabe qué puede exigir.

---

## Probarlo ahora / Try it now

Solo necesitas Python 3.8+ instalado. No requiere dependencias externas.

### 1. Clonar el repo

```bash
git clone https://github.com/ELLokoAkrata/truths-and-rights.git
cd truths-and-rights
```

### 2. Construir la base de datos

```bash
python scripts/build_db.py --country PE
```

Esto genera `build/truths_and_rights_pe.db` (256 KB) a partir de los datos en JSON.

### 3. Usar el CLI

**Consulta directa** — escribe tu situación entre comillas:

```bash
python scripts/cli.py "me quieren revisar el celular"
python scripts/cli.py "me encuentran con marihuana"
python scripts/cli.py "me piden el DNI"
python scripts/cli.py "puedo grabar al policía"
python scripts/cli.py "me llevan a la comisaría"
python scripts/cli.py "cuánto tiempo me pueden retener"
```

**Modo interactivo** — sin argumentos, y vas escribiendo consultas:

```bash
python scripts/cli.py
```

### 4. Qué te muestra

Para cada consulta, el CLI responde con:

- **Situación detectada** — qué escenario legal aplica
- **Tus derechos** — con base legal y notas por contexto (normal / estado de emergencia)
- **Qué hacer paso a paso** — acciones ordenadas con textos sugeridos para decirle al policía
- **Límites de tiempo** — cuántas horas pueden retenerte legalmente
- **A quién llamar** — teléfonos y WhatsApp de la Defensoría, Fiscalía, ONGs

### 5. Ejemplo de salida

```
$ python scripts/cli.py "me encuentran con marihuana"

  SITUACION DETECTADA
  Me encuentran con marihuana
  Severidad: HIGH

  TUS DERECHOS
  Posesión de cannabis menor a 8g NO es delito [NUNCA SE SUSPENDE]
  Base legal: Art. 299 Código Penal
  Nota: Menos de 8g = NO es delito. No hay flagrancia.

  QUE HACER (PASO A PASO)
  Paso 1 [HACER] Mantén la calma
  Paso 2 [GRABAR] Activa grabación inmediatamente
  Paso 3 [DECIR] Exige identificación del policía
    "Oficial, ¿podría proporcionarme su nombre, grado y
     dependencia policial, por favor?"
  Paso 5 [DECIR] Informa que la cantidad es legal
    "Esta cantidad es para consumo personal. Es menor a 8 gramos,
     lo cual no es punible según el Artículo 299 del Código Penal."
  ...

  A QUIEN LLAMAR
  Defensoría del Pueblo — 0800-15-170 (24/7, gratuito)
  WhatsApp: +51 947 951 412
```

### Situaciones disponibles

| Consulta de ejemplo | Situación |
|---|---|
| "me piden el DNI" | Control de identidad |
| "me quieren revisar la mochila" | Registro de pertenencias |
| "quieren ver mi celular" | Revisión de celular / IMEI |
| "me llevan a la comisaría" | Conducción sin detención |
| "me niego a mostrar documentos" | Negativa a identificarse |
| "puedo grabar al policía" | Grabación de intervención |
| "cuánto tiempo me pueden retener" | Límites de retención |
| "no me dicen por qué me paran" | Sin motivo informado |
| "me encuentran con marihuana" | Posesión de cannabis |

---

## Portal publico de datos

Los datos legales del proyecto estan disponibles como sitio web estatico:

**[https://ellokoakrata.github.io/truths-and-rights/](https://ellokoakrata.github.io/truths-and-rights/)**

El portal incluye:
- Estado de emergencia actual con dias restantes
- Las 9 situaciones con derechos, acciones y contactos
- Los 20+ derechos agrupados por categoria
- Las 43+ fuentes legales con enlaces oficiales
- Mitos desmentidos con base legal
- Contactos de emergencia
- Dashboard de verificacion de frescura de datos

El sitio se regenera automaticamente con cada cambio en los datos via GitHub Pages.

Para generar el sitio localmente:
```bash
make site          # Genera site/
make serve         # Sirve en localhost:8000
```

---

## Automatizacion

El proyecto tiene workflows automatizados de GitHub Actions:

| Workflow | Frecuencia | Que hace |
|---|---|---|
| **Check emergencia** | Semanal (lunes) | Verifica si el decreto de emergencia vencio o esta por vencer |
| **Check fuentes** | Quincenal (dia 1 y 15) | Verifica vigencia de las 43+ fuentes legales |
| **Scrape completo** | Mensual (dia 1) | Descarga textos actualizados de fuentes oficiales |
| **Validacion** | Cada push/PR | Valida datos, construye DB, corre tests |
| **Deploy portal** | Cada cambio en datos | Regenera y publica el sitio estatico |

Los workflows **nunca modifican datos legales automaticamente**. Solo crean Issues para revision humana. Los datos legales requieren verificacion de abogado.

---

## App movil

La app movil para Android esta en `mobile/`. Funciona 100% offline con la base de datos SQLite embebida.

### Requisitos

- Node.js 18+
- npm o yarn
- Android Studio (para emulador) o dispositivo Android 8+ (API 26)

### Desarrollo

```bash
make mobile-install    # Instalar dependencias
make mobile-copy-db    # Copiar DB a assets
make mobile-start      # Iniciar servidor de desarrollo
```

### Build APK

```bash
make mobile-build-apk  # Genera APK via EAS Build
```

### Tests

```bash
make mobile-test       # Correr tests unitarios
```

---

## Arquitectura

```
truths-and-rights/
├── schema/                     # Base de datos legal
│   ├── database_schema.sql     # Estructura de tablas (SQLite)
│   └── SCHEMA_DOCS.md          # Documentación del schema
│
├── data/                       # Datos legales por país
│   └── PE/                     # Perú
│       ├── sources/            # Textos legales oficiales
│       ├── situations/         # Escenarios ciudadanos
│       ├── rights/             # Derechos por situación
│       ├── actions/            # Acciones paso a paso
│       ├── contacts/           # Contactos de emergencia
│       ├── myths/              # Mitos desmontados
│       ├── contexts/           # Contextos (normal, emergencia)
│       └── substances/         # Cantidades legales
│
├── scripts/                    # Scripts de utilidad
│   ├── build_db.py             # Genera el .db desde los JSON
│   ├── validate_sources.py     # Valida integridad de datos
│   ├── search.py               # Buscador de lenguaje natural
│   ├── cli.py                  # CLI de consulta
│   └── scrape_official.py      # Scraping de fuentes oficiales
│
├── mobile/                     # App movil (Expo, Android)
│   ├── App.tsx                 # Entry point
│   ├── src/                    # Codigo fuente
│   │   ├── database/           # DB provider, queries, search engine
│   │   ├── screens/            # 8 pantallas
│   │   ├── components/         # UI + situation components
│   │   ├── hooks/              # Custom hooks
│   │   ├── navigation/         # React Navigation (tabs + stacks)
│   │   └── store/              # Zustand state
│   ├── assets/db/              # DB embebida (copiada de build/)
│   └── __tests__/              # Tests unitarios
│
├── build/                      # Generado (no versionado)
│   └── truths_and_rights_pe.db # Base de datos SQLite (256 KB)
│
├── docs/                       # Documentación del proyecto
│   ├── LEGAL_METHODOLOGY.md    # Cómo verificamos la información legal
│   ├── ADDING_A_COUNTRY.md     # Guía para agregar otro país
│   └── DATA_FORMAT.md          # Formato de los archivos de datos
│
├── CONTRIBUTING.md             # Guía para contribuir
├── CODE_OF_CONDUCT.md          # Código de conducta
├── LICENSE                     # GPL v3
└── README.md                   # Este archivo
```

---

## Funcionalidades planeadas

### Fase 1 — MVP: Información
- [x] Schema de base de datos (12 tablas)
- [x] Base de datos legal de Perú (43 fuentes, 20 derechos, 9 situaciones, 17 acciones)
- [x] Buscador por situación en lenguaje natural
- [x] CLI con derechos, acciones, scripts y contactos
- [x] Funciona offline (SQLite, 256 KB)
- [x] App móvil Android (Expo, offline-first)

### Fase 2 — Protección activa
- [ ] Botón de pánico (grabación + GPS + alertas)
- [ ] Temporizador legal (alerta si exceden plazos)
- [ ] Grabación en segundo plano
- [ ] Mensaje pregrabado de derechos

### Fase 3 — Comunidad
- [ ] Reporte anónimo de intervenciones
- [ ] Mapa de calor de abusos policiales
- [ ] Red de testigos voluntarios

### Fase 4 — Expansión
- [ ] Otros países de Latinoamérica
- [ ] API pública para ONGs y periodistas
- [ ] Sección educativa (desmontando mitos)

---

## ¿Cómo contribuir? / How to contribute?

**No necesitas saber programar para contribuir.** Hay muchas formas de ayudar:

| Perfil | Cómo puedes ayudar |
|---|---|
| 🧑‍⚖️ **Abogado/a** | Verificar información legal, agregar jurisprudencia, revisar precisión |
| 💻 **Programador/a** | Código, scripts, app móvil, backend |
| 📝 **Escritor/a** | Simplificar lenguaje legal, redactar scripts, traducir |
| 🎨 **Diseñador/a** | UX/UI de la app, iconografía, accesibilidad |
| 🌎 **Activista / ONG** | Agregar datos de tu país, difundir, conectar con comunidades |
| 👤 **Ciudadano/a** | Reportar errores, sugerir situaciones, testear |

Lee [CONTRIBUTING.md](CONTRIBUTING.md) para los detalles.

---

## Stack técnico

- **Base de datos:** SQLite (offline-first)
- **Datos:** SQL + JSON (legibles y editables por humanos)
- **App móvil:** Expo / React Native (Android, offline-first)
- **Backend (Fase 3):** Por definir
- **Idiomas:** Español (principal), Inglés (documentación técnica)

---

## Datos legales: fuentes oficiales

Cada dato legal en la app es rastreable a su fuente oficial:

| Fuente | URL | Qué contiene |
|---|---|---|
| SPIJ | spij.minjus.gob.pe | Legislación peruana actualizada |
| El Peruano | diariooficial.elperuano.pe | Diario oficial — leyes y decretos |
| Tribunal Constitucional | tc.gob.pe | Sentencias y jurisprudencia |
| Congreso | congreso.gob.pe | Textos de leyes aprobadas |
| Corte IDH | corteidh.or.cr | Jurisprudencia interamericana |

**Principio fundamental:** si no tiene fuente oficial verificable, no entra a la base de datos.

---

## Licencia

**GPL v3** — Este proyecto es y será siempre libre. Cualquiera puede usarlo, modificarlo y distribuirlo, pero debe mantener el código abierto bajo la misma licencia.

¿Por qué GPL y no MIT? Porque no queremos que alguien tome esto, lo cierre y lo venda. Los derechos ciudadanos no son un producto comercial.

---

## Origen

Este proyecto nació en un bus en Lima, Perú, en febrero de 2026. Nació de la experiencia directa de ciudadanos que vivieron intervenciones policiales abusivas y descubrieron después que tenían derechos que nadie les informó.

**No es una app anti-policía. Es una app pro-proceso justo.** Protege tanto al ciudadano inocente como a la víctima real de un delito, porque un proceso justo significa que el culpable verdadero no se escapa y el inocente no cae.

---

## Contacto

- Issues: [GitHub Issues](https://github.com/truths-and-rights/truths-and-rights/issues)
- Discusiones: [GitHub Discussions](https://github.com/truths-and-rights/truths-and-rights/discussions)

*"La injusticia en cualquier parte es una amenaza a la justicia en todas partes."* — Martin Luther King Jr.
