# Truths and Rights — Schema Documentation v1.0

## Flujo de datos: del usuario a la respuesta

```
USUARIO DICE: "Me quieren revisar la mochila"
         │
         ▼
┌─────────────────────────┐
│  BÚSQUEDA SITUACIÓN     │  ← Match por keywords + natural_queries
│  situations.keywords     │     'mochila,revisar,registro,bolso'
│  situations.natural_q    │     'me quieren revisar la mochila'
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  DETECTAR CONTEXTO      │  ← ¿Hay estado de emergencia activo?
│  contexts.is_active      │     ¿En qué región está el usuario?
│  contexts.active_regions │     Modifica los derechos aplicables
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  DERECHOS APLICABLES    │  ← Filtrados por situación + contexto
│  situation_rights        │     Algunos se suspenden en emergencia
│  rights.is_absolute      │     Los absolutos NUNCA se suspenden
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  ACCIONES PASO A PASO   │  ← Qué hacer, en qué orden
│  situation_actions       │     Paso 1: Pregunta el motivo
│  actions.script          │     Paso 2: Exige identificación
│  actions.priority        │     Paso 3: Graba
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  LÍMITES TEMPORALES     │  ← ¿Cuánto tiempo pueden retenerte?
│  time_limits.max_hours   │     4h retención, 48h detención, etc.
│  → activa temporizador   │     La app empieza a contar
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  CONTACTOS RELEVANTES   │  ← A quién llamar si escala
│  situation_contacts      │     Defensoría: 0800-15-170
│  emergency_contacts      │     Fiscalía, IDL, APRODEH
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  RESPUESTA AL USUARIO   │
│                         │
│  "No pueden revisar tu  │
│   mochila sin fundadas  │
│   razones. Esto es lo   │
│   que puedes hacer..."  │
└─────────────────────────┘
```

## Las 12 tablas y por qué existen

### Núcleo legal (el cerebro)
| Tabla | Para qué | Ejemplo |
|---|---|---|
| `legal_sources` | Cada ley citada con texto oficial | Art. 299 CP - posesión personal |
| `rights` | Derechos del ciudadano | "No pueden revisar tu celular" |
| `situations` | Lo que le está pasando al usuario | "Me piden el IMEI" |
| `contexts` | Qué modifica los derechos | Estado de emergencia en Lima |
| `actions` | Qué puede hacer el ciudadano | "Di esto, graba, llama aquí" |
| `time_limits` | Plazos máximos legales | 4 horas retención máxima |

### Protección (el escudo)
| Tabla | Para qué | Ejemplo |
|---|---|---|
| `emergency_contacts` | Instituciones de ayuda | Defensoría: 0800-15-170 |
| `force_levels` | Niveles de fuerza legal | Resistencia pasiva → solo verbal |
| `legal_possession` | Cantidades legales de sustancias | Cannabis: máximo 8 gramos |

### Comunidad (la red)
| Tabla | Para qué | Ejemplo |
|---|---|---|
| `incident_reports` | Reportes anónimos de abuso | Mapa de calor por comisaría |
| `users` | Datos mínimos del usuario | Contactos de emergencia, testigo voluntario |
| `myths` | Sección educativa anti-mitos | "Los DDHH no protegen delincuentes" |

## Relaciones clave

```
situations ──┬── situation_rights ──── rights ──── right_sources ──── legal_sources
             │
             ├── situation_actions ─── actions
             │
             ├── situation_contacts ── emergency_contacts
             │
             └── time_limits ───────── legal_sources
             
contexts ────── modifica ──── situation_rights.applies (TRUE/FALSE)

force_levels ── referencia ── legal_sources

legal_possession ── referencia ── legal_sources

myths ── referencia ── legal_sources
```

## Categorías de situaciones (situations.category)

1. **identificacion** — Te piden DNI, documentos
2. **registro** — Quieren revisar mochila, celular, vehículo
3. **detencion** — Te llevan a comisaría, te esposan
4. **domicilio** — Quieren entrar a tu casa
5. **comunicaciones** — Quieren tu celular, IMEI, contraseña
6. **protesta** — Estás en una manifestación
7. **vehicular** — Te paran en el carro, operativo vehicular
8. **uso_fuerza** — Te están golpeando, usando fuerza excesiva

## Ejemplo de consulta completa

```sql
-- Usuario dice: "Me quieren revisar la mochila"
-- Contexto: Estado de emergencia activo en Lima

-- 1. Encontrar la situación
SELECT * FROM situations 
WHERE keywords LIKE '%mochila%' OR keywords LIKE '%registro%';
-- → situation_id: 'police_bag_search'

-- 2. Obtener derechos aplicables en estado de emergencia
SELECT r.title, r.description, sr.applies, sr.notes
FROM situation_rights sr
JOIN rights r ON sr.right_id = r.id
WHERE sr.situation_id = 'police_bag_search'
AND sr.context_id = 'estado_emergencia_seguridad';

-- 3. Obtener acciones paso a paso
SELECT a.title, a.description, a.script, a.warning, sa.step_order
FROM situation_actions sa
JOIN actions a ON sa.action_id = a.id
WHERE sa.situation_id = 'police_bag_search'
AND sa.context_id = 'estado_emergencia_seguridad'
ORDER BY sa.step_order;

-- 4. Obtener límites temporales
SELECT description, max_hours, after_expiry_action
FROM time_limits
WHERE situation_id = 'police_bag_search';

-- 5. Obtener contactos relevantes
SELECT ec.institution, ec.phone, ec.whatsapp, sc.notes
FROM situation_contacts sc
JOIN emergency_contacts ec ON sc.contact_id = ec.id
WHERE sc.situation_id = 'police_bag_search'
ORDER BY sc.priority;
```

## Decisiones de diseño

### ¿Por qué SQLite?
- Funciona **offline** (crítico para la calle, sin datos móviles)
- Se empaqueta dentro de la app móvil
- Ligero, rápido, no necesita servidor
- Se actualiza descargando un nuevo archivo .db

### ¿Por qué IDs tipo texto y no autonuméricos?
- Legibilidad: 'police_id_check' dice más que '47'
- Portabilidad: al migrar datos no se rompen referencias
- Colaboración: dos personas pueden crear datos sin colisión de IDs

### ¿Por qué contextos como tabla separada?
- Los estados de emergencia cambian frecuentemente
- Se pueden activar/desactivar sin tocar el resto de datos
- Permiten respuestas diferentes para la misma situación según contexto

### ¿Por qué scripts pregrabados en actions?
- En la calle, con adrenalina, no piensas claro
- La app puede reproducir el texto en audio
- Estandariza el lenguaje para que sea legal y respetuoso

## Próximo paso: poblar la base de datos
Con el schema definido, el siguiente paso es:
1. Scraping/descarga de fuentes oficiales → poblar `legal_sources`
2. Mapear los 8 escenarios del PDF → poblar `situations`, `rights`, `actions`
3. Agregar límites temporales y contactos
4. Crear la tabla de mitos con los argumentos educativos
5. Validar con un abogado (ideal)
