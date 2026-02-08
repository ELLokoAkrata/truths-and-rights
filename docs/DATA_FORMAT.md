# Formato de datos / Data Format

## Principio

Los datos legales se almacenan en JSON para que sean:
- **Legibles por humanos** (un abogado puede revisarlos sin saber programar)
- **Legibles por máquinas** (el script `build_db.py` los convierte a SQLite)
- **Versionables** (Git trackea cada cambio)

---

## Formato por tipo de dato

### Fuente legal (`sources/*.json`)

```json
[
  {
    "id": "const_art2_inc24f",
    "source_type": "constitucion",
    "name": "Constitución Política del Perú",
    "article": "Artículo 2, inciso 24, literal f",
    "full_text": "Nadie puede ser detenido sino por mandamiento escrito y motivado del juez o por las autoridades policiales en caso de flagrante delito.",
    "summary": "Solo te pueden detener con orden judicial escrita o si te atrapan cometiendo un delito. Nada más.",
    "publication_date": "1993-12-29",
    "last_modified": "2017-08-10",
    "official_url": "https://spij.minjus.gob.pe/...",
    "status": "vigente"
  }
]
```

**Campos obligatorios:** id, source_type, name, full_text, summary, status
**Campos opcionales:** article, publication_date, last_modified, official_url

---

### Situación (`situations/*.json`)

```json
[
  {
    "id": "phone_search",
    "category": "comunicaciones",
    "title": "Quieren revisar mi celular o pedir mi IMEI",
    "description": "La policía te pide desbloquear tu celular, revisar tus mensajes, fotos, o te solicita el código IMEI.",
    "keywords": ["celular", "telefono", "imei", "codigo", "desbloquear", "mensajes", "whatsapp"],
    "natural_queries": [
      "me piden el celular",
      "quieren revisar mi celular",
      "me piden el IMEI",
      "me piden desbloquear el celular",
      "quieren ver mis mensajes"
    ],
    "severity": "high",
    "icon": "📱",
    "parent_situation_id": null,
    "rights": [
      {
        "right_id": "right_no_cell_search",
        "context": "normal",
        "applies": true,
        "notes": "Necesitan orden judicial. Tu negativa no es delito."
      },
      {
        "right_id": "right_no_cell_search",
        "context": "estado_emergencia_seguridad",
        "applies": true,
        "notes": "Sigue protegido incluso en emergencia."
      }
    ],
    "actions": [
      {
        "action_id": "action_stay_calm",
        "step_order": 1
      },
      {
        "action_id": "action_start_recording",
        "step_order": 2
      },
      {
        "action_id": "action_refuse_cell_search",
        "step_order": 3
      }
    ],
    "time_limits": [],
    "contacts": ["defensoria_pueblo", "fiscalia_turno"]
  }
]
```

---

### Derecho (`rights/rights.json`)

```json
[
  {
    "id": "right_no_cell_search",
    "title": "No pueden revisar tu celular sin orden judicial",
    "description": "Tu celular está protegido por el derecho a la intimidad y el secreto de comunicaciones.",
    "legal_basis": "Art. 2 inc. 10 Constitución + Exp. 00323-2024 Juzgado Chupaca",
    "is_absolute": true,
    "never_suspended": true,
    "category": "comunicaciones",
    "source_ids": ["const_art2_inc10", "juzgado_chupaca_2024"]
  }
]
```

**Categorías de derechos:** libertad, integridad, comunicaciones, propiedad, debido_proceso, dignidad

---

### Acción (`actions/actions.json`)

```json
[
  {
    "id": "action_refuse_cell_search",
    "action_type": "decir",
    "title": "Niégate a entregar o desbloquear tu celular",
    "description": "No tienes obligación legal de entregar tu celular, desbloquearlo ni dar tu IMEI sin orden judicial.",
    "script": "Respetuosamente me niego a entregar mi celular. El artículo 2 inciso 10 de la Constitución protege mis comunicaciones. Se requiere orden judicial para revisarlo.",
    "priority": 6,
    "is_recommended": true,
    "warning": "Es probable que insistan o amenacen. Mantén tu posición con calma.",
    "legal_basis_summary": "Art. 2 inc. 10 Constitución + Exp. 00323-2024"
  }
]
```

**Tipos de acción:** decir, hacer, no_hacer, grabar, llamar, documentar

---

### Contacto de emergencia (`contacts/emergency_contacts.json`)

```json
[
  {
    "id": "defensoria_pueblo",
    "institution": "Defensoría del Pueblo",
    "description": "Organismo autónomo que supervisa comisarías.",
    "phone": "0800-15-170",
    "whatsapp": "+51 947 951 412",
    "email": "consulta@defensoria.gob.pe",
    "website": "https://apps2.defensoria.gob.pe/sidPublic/",
    "address": "Jr. Ucayali 394-398, Lima",
    "is_free": true,
    "requires_lawyer": false,
    "available_hours": "24/7",
    "contact_type": "emergencia",
    "priority": 1
  }
]
```

---

### Mito (`myths/myths.json`)

```json
[
  {
    "id": "myth_ddhh_protect_criminals",
    "myth": "Los derechos humanos protegen a los delincuentes",
    "reality": "Los DDHH protegen el proceso justo.",
    "explanation": "El mismo sistema que suelta delincuentes por corrupción es el que encarcela inocentes por abuso. Pedir menos derechos es darle más poder al policía abusivo, no al que combate el crimen.",
    "related_source_ids": ["const_art2_inc24f"],
    "category": "derechos_humanos"
  }
]
```

---

## Convenciones

### IDs
- Snake_case en inglés: `right_no_cell_search`, `action_stay_calm`
- Prefijo por tipo: `right_`, `action_`, `limit_`, `myth_`
- Descriptivos: `cannabis_possession` no `sit_001`

### Textos
- `title` y `summary`: lenguaje ciudadano simple
- `full_text`: texto legal literal (copiar exacto)
- `script`: texto sugerido en segunda persona ("Respetuosamente me niego...")
- `description`: explicación intermedia entre legal y ciudadano

### Fechas
- Formato ISO: `YYYY-MM-DD`

### Idioma
- Datos legales: en el idioma del país
- IDs y campos técnicos: en inglés
- Documentación del proyecto: bilingüe español/inglés
