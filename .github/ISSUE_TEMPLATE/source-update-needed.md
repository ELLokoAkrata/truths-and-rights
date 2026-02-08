---
name: Fuente legal requiere actualizacion
about: Una fuente legal ha sido modificada, derogada o necesita verificacion
labels: legal-data, legal-review
---

## Fuente legal

**ID en la base de datos:** <!-- ej: const_art2_inc24f -->
**Nombre:** <!-- ej: Constitucion Art. 2 inc. 24.f -->
**Tipo:** <!-- constitucion / codigo_procesal / decreto_legislativo / ley / jurisprudencia -->

## Que cambio

<!-- Describir que se modifico, derogo o agrego -->

## Fuente oficial del cambio

- URL: <!-- link a SPIJ, El Peruano, TC, etc. -->
- Fecha de publicacion: <!-- YYYY-MM-DD -->
- Norma que modifica: <!-- ej: Ley 32XXX -->

## Acciones requeridas

- [ ] Verificar el cambio en la fuente oficial
- [ ] Actualizar JSON en `data/PE/sources/`
- [ ] Verificar si afecta derechos en `data/PE/rights/rights.json`
- [ ] Verificar si afecta situaciones en `data/PE/situations/`
- [ ] Revision por abogado (si el cambio es sustantivo)
- [ ] Correr validacion: `make validate-pe`
- [ ] Correr tests: `make test`
- [ ] Actualizar CHANGELOG.md

## Impacto estimado

- [ ] Afecta derechos del ciudadano
- [ ] Afecta procedimientos policiales
- [ ] Afecta estados de emergencia
- [ ] Solo cambio formal (sin impacto sustantivo)
