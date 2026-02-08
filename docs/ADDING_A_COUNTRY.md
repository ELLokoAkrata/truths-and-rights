# Cómo agregar un nuevo país / Adding a New Country

## Visión

Truths and Rights nació en Perú pero está diseñado para ser **global**. El schema es agnóstico al país — cada tabla tiene un campo `country` que permite datos paralelos para múltiples jurisdicciones.

---

## Lo que necesitas

### Mínimo viable (lo esencial)

1. **Constitución o ley fundamental** — derechos del ciudadano ante la policía
2. **Código procesal penal** — procedimientos de detención, registro, retención
3. **Ley de la policía** — facultades y límites
4. **Regulación de uso de la fuerza** — niveles autorizados
5. **Al menos 5 escenarios prácticos** documentados con derechos y acciones
6. **Contactos de emergencia** institucionales (defensoría, fiscalía, ONGs)

### Ideal (para una versión robusta)

- Jurisprudencia relevante (tribunal constitucional o equivalente)
- Régimen de estados de excepción
- Leyes sobre posesión de sustancias (si aplica)
- Protocolos policiales oficiales
- Estadísticas de abuso policial
- Revisión por abogado local

---

## Estructura de archivos

```
data/
└── XX/                          # Código ISO del país (PE, CO, MX, AR, CL, BR...)
    ├── metadata.json            # Info del país y estado de completitud
    ├── sources/                 # Fuentes legales
    │   ├── constitution.json
    │   ├── criminal_procedure.json
    │   ├── police_law.json
    │   ├── force_regulation.json
    │   └── jurisprudence.json
    ├── situations/              # Escenarios ciudadanos
    │   ├── id_check.json
    │   ├── bag_search.json
    │   ├── phone_search.json
    │   ├── detention.json
    │   └── ...
    ├── rights/                  # Derechos
    │   └── rights.json
    ├── actions/                 # Acciones sugeridas
    │   └── actions.json
    ├── contacts/                # Contactos de emergencia
    │   └── emergency_contacts.json
    ├── contexts/                # Estados de excepción, etc.
    │   └── contexts.json
    ├── substances/              # Posesión legal (si aplica)
    │   └── legal_possession.json
    └── myths/                   # Mitos locales
        └── myths.json
```

---

## metadata.json de ejemplo

```json
{
  "country_code": "CO",
  "country_name": "Colombia",
  "legal_system": "civil_law",
  "language": "es",
  "currency": "COP",
  "emergency_number": "123",
  "police_name": "Policía Nacional de Colombia",
  "human_rights_body": "Defensoría del Pueblo",
  "completeness": {
    "sources": "partial",
    "situations": "minimal",
    "rights": "partial",
    "actions": "minimal",
    "contacts": "complete",
    "review_by_lawyer": false
  },
  "contributors": [
    {
      "role": "legal_data",
      "github": "@usuario"
    }
  ],
  "last_verified": "2026-02-01",
  "notes": "Versión inicial. Necesita revisión por abogado colombiano."
}
```

---

## Pasos para contribuir un país

### Paso 1: Abre un Issue
Título: `[Country] Agregar datos para [nombre del país]`
Describe qué tienes disponible y qué falta.

### Paso 2: Investiga las fuentes oficiales
Busca el equivalente a:
- SPIJ (base de datos legislativa oficial)
- Tribunal Constitucional (jurisprudencia)
- Diario oficial (publicación de leyes)
- Defensoría del Pueblo o equivalente

### Paso 3: Documenta lo básico
Empieza con los 5 escenarios más comunes:
1. Control de identidad en la calle
2. Registro de pertenencias
3. Revisión de celular
4. Detención / conducción a comisaría
5. Uso de fuerza policial

### Paso 4: Crea los archivos JSON
Sigue el formato de `data/PE/` como referencia.

### Paso 5: Abre un Pull Request
Incluso si está incompleto — una versión parcial verificada es mejor que nada.

---

## Notas importantes

- **Cada país es diferente.** No asumas que lo que aplica en Perú aplica en tu país.
- **Prioriza precisión sobre completitud.** 5 escenarios correctos valen más que 20 dudosos.
- **Marca lo no verificado.** Si no tienes revisión de abogado, indícalo en metadata.json.
- **Las leyes cambian.** Incluye siempre la fecha de última verificación.
