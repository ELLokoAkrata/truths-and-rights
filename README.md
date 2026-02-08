# Truths and Rights 🛡️

**App ciudadana de derechos ante intervenciones policiales.**

> Porque conocer tus derechos no debería requerir un título en derecho.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Country: Peru](https://img.shields.io/badge/Country-Peru-red.svg)](#)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](#)

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

## Arquitectura

```
truths-and-rights/
├── schema/                     # Base de datos legal
│   ├── database_schema.sql     # Estructura de tablas (SQLite)
│   ├── sample_data.sql         # Datos de ejemplo
│   └── SCHEMA_DOCS.md          # Documentación del schema
│
├── data/                       # Datos legales por país
│   └── PE/                     # Perú
│       ├── sources/            # Textos legales oficiales
│       ├── situations/         # Escenarios ciudadanos
│       ├── rights/             # Derechos por situación
│       ├── actions/            # Acciones paso a paso
│       └── contacts/           # Contactos de emergencia
│
├── scripts/                    # Scripts de utilidad
│   ├── build_db.py             # Genera el .db desde los datos
│   ├── validate_sources.py     # Verifica que las fuentes estén vigentes
│   └── scrape_official.py      # Scraping de fuentes oficiales
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

### Fase 1 — MVP: Información (en desarrollo)
- [x] Schema de base de datos
- [ ] Base de datos legal completa (Perú)
- [ ] Buscador por situación en lenguaje natural
- [ ] Respuestas con derechos, acciones y contactos
- [ ] Funciona offline (SQLite empaquetado)

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
- **App móvil:** Por definir (React Native o Flutter)
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
