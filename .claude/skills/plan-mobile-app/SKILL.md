---
name: plan-mobile-app
description: Planificar e implementar la app movil de Truths and Rights. Usa este skill cuando trabajes en la app React Native.
disable-model-invocation: true
argument-hint: "[componente o feature a trabajar]"
---

# Truths and Rights — App movil

## Objetivo

App movil React Native que funcione **offline** para consultar derechos ciudadanos durante intervenciones policiales en Peru.

## Requisitos criticos

1. **Offline-first**: Toda la data legal debe funcionar sin internet. La DB SQLite (~256KB) se embebe en la app.
2. **Velocidad**: El usuario esta en una situacion de estres. La respuesta debe ser instantanea (<200ms).
3. **Simplicidad**: Interfaz minima. Buscar situacion → ver derechos + que hacer. Sin login, sin registro.
4. **Modo panico**: Boton de emergencia visible que grabe audio/video y comparta ubicacion con contacto de confianza.
5. **Accesibilidad**: Texto grande legible, alto contraste, funcionar en telefonos baratos con Android 8+.

## Stack sugerido (a confirmar con el usuario)

- **React Native** con Expo (simplifica build y distribucion)
- **SQLite** via expo-sqlite o react-native-quick-sqlite (la DB ya existe)
- **Busqueda**: FTS5 de SQLite (ya hay keywords y natural_queries en los datos)
- **Estado**: Zustand o React Context (app simple, no necesita Redux)
- **Navegacion**: React Navigation (stack + tabs)
- **Almacenamiento**: AsyncStorage para preferencias del usuario

## DB disponible

La base de datos SQLite se genera con `python scripts/build_db.py --country PE`.
Archivo: `build/truths_and_rights_pe.db` (~256KB).

Tablas principales que la app consumira:
- `situations` — Punto de entrada del usuario
- `rights` — Derechos (con flag never_suspended)
- `actions` — Pasos a seguir (con suggested_script = frases exactas)
- `situation_rights` — Mapeo situacion→derechos por contexto
- `situation_actions` — Pasos ordenados por situacion
- `emergency_contacts` — Telefonos de ayuda
- `contexts` — Estado de emergencia actual
- `legal_sources` — Para "ver fuente" (link a ley/articulo)
- `myths` — Mitos desmentidos
- `time_limits` — Plazos maximos

Hay views predefinidas en el schema:
- `v_situation_full` — Situacion con todos sus derechos, acciones y contactos
- `v_active_emergency` — Estado de emergencia actual con derechos afectados
- `v_rights_with_sources` — Derechos con sus fuentes legales

## Pantallas principales

| Pantalla | Funcion |
|---|---|
| **Home** | Buscador principal + situaciones frecuentes + banner de emergencia |
| **Situacion** | Detalle: derechos, pasos, limites de tiempo, contactos |
| **Derechos** | Lista de todos los derechos, filtrable por categoria |
| **Emergencia** | Estado de emergencia actual: que se suspende y que NO |
| **Mitos** | Mitos comunes desmentidos |
| **Contactos** | Telefonos de emergencia (con boton de llamar directo) |
| **Busqueda** | Resultados de busqueda por texto libre |

## Flujo principal del usuario

```
Abre app → Ve buscador + situaciones frecuentes
       ↓
Busca "me revisan la mochila" o toca tarjeta de situacion
       ↓
Ve pantalla de situacion:
  - Banner: estado de emergencia (si aplica)
  - Tus derechos (con badge NUNCA SE SUSPENDE)
  - Que hacer paso a paso (con frases exactas para decir)
  - Limites de tiempo
  - A quien llamar (boton directo)
  - Ver fuentes legales (link a articulo)
```

## Busqueda offline

Los datos ya tienen campos optimizados para busqueda:
- `situations.keywords`: "dni,identidad,documento,identificacion,papeles"
- `situations.natural_queries`: "me piden DNI|me piden documentos|me piden identificarme"

Opciones de implementacion:
1. **FTS5 de SQLite** — Mejor opcion. Crear tabla FTS virtual con keywords + natural_queries + title
2. **Busqueda simple** — LIKE queries contra keywords (funciona pero peor)

## Estado de emergencia (logica critica)

La app debe verificar `contexts` al inicio:
- Si `is_currently_active == true` y `end_date >= hoy`: mostrar banner prominente
- Filtrar derechos segun contexto: algunos derechos tienen `applies: false` en contexto de emergencia
- Los derechos con `never_suspended: true` SIEMPRE se muestran como vigentes

La app puede actualizar el estado de emergencia via:
- Check al `status.json` del portal (https://ellokoakrata.github.io/truths-and-rights/status.json)
- Solo cuando hay internet, y guardar en cache local

## Archivos relevantes para leer

Antes de empezar, leer estos archivos para entender los datos:
- `data/PE/metadata.json` — Config del pais
- `data/PE/situations/01_id_check.json` — Ejemplo de situacion
- `data/PE/rights/rights.json` — Todos los derechos
- `data/PE/actions/actions.json` — Todas las acciones
- `data/PE/contacts/emergency_contacts.json` — Contactos
- `data/PE/contexts/contexts.json` — Contextos (normal + emergencia)
- `schema/database_schema.sql` — Schema completo de la DB
- `schema/SCHEMA_DOCS.md` — Documentacion del schema

## Lo que ya existe y NO hay que rehacer

- La DB SQLite ya se genera y funciona
- Los datos legales estan completos y verificados
- El portal web ya esta en produccion
- La automatizacion de verificacion ya funciona
- Los tests ya validan la integridad de los datos

## Lo que falta construir

La app movil es el siguiente paso. Todo lo demas (datos, DB, portal, CI) ya esta listo.
