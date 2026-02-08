---
name: Cambio en decreto de emergencia
about: Decreto de emergencia vencido, renovado o nuevo
labels: legal-data, urgent, country:PE
---

## Decreto de emergencia

**Decreto:** <!-- DS N° XXX-YYYY-PCM -->
**Estado:** <!-- vencido / renovado / nuevo -->
**Fecha de vencimiento:** <!-- YYYY-MM-DD -->

## Detalle

<!-- Describir el cambio: si vencio, si fue renovado con nuevo numero, si cambio de regiones, etc. -->

## Fuente oficial

- URL de El Peruano: <!-- link -->
- Fecha de publicacion: <!-- YYYY-MM-DD -->

## Acciones requeridas

- [ ] Verificar el decreto en El Peruano
- [ ] Actualizar `data/PE/contexts/contexts.json`
- [ ] Actualizar `data/PE/metadata.json` (seccion `active_emergencies`)
- [ ] Actualizar fechas y regiones si cambio la cobertura
- [ ] Correr validacion: `make validate-pe`
- [ ] Correr tests: `make test`
- [ ] Actualizar CHANGELOG.md

## Impacto

<!-- Que derechos se ven afectados? Que situaciones cambian? -->
