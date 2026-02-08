-- ============================================================
-- TRUTHS AND RIGHTS — Database Schema v1.0
-- App de derechos ciudadanos ante intervenciones policiales
-- País: Perú (extensible a otros países)
-- ============================================================

-- ============================================================
-- 1. FUENTES LEGALES
-- La base de todo: cada dato debe ser rastreable a su fuente
-- ============================================================

CREATE TABLE legal_sources (
    id TEXT PRIMARY KEY,                    -- 'const_art2_inc24_f'
    source_type TEXT NOT NULL,              -- 'constitucion', 'codigo_procesal', 'decreto_legislativo', 'ley', 'jurisprudencia', 'tratado_internacional'
    name TEXT NOT NULL,                     -- 'Constitución Política del Perú'
    article TEXT,                           -- 'Artículo 2, inciso 24, literal f'
    full_text TEXT NOT NULL,                -- Texto literal oficial
    summary TEXT NOT NULL,                  -- Resumen en lenguaje simple
    publication_date TEXT,                  -- Fecha de publicación en El Peruano
    last_modified TEXT,                     -- Última modificación conocida
    official_url TEXT,                      -- URL de fuente oficial (SPIJ, TC, etc.)
    status TEXT DEFAULT 'vigente',          -- 'vigente', 'modificado', 'derogado'
    country TEXT DEFAULT 'PE',             
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. SITUACIONES
-- El punto de entrada del usuario: "¿qué me está pasando?"
-- ============================================================

CREATE TABLE situations (
    id TEXT PRIMARY KEY,                    -- 'police_id_check'
    category TEXT NOT NULL,                 -- 'identificacion', 'registro', 'detencion', 'domicilio', 'comunicaciones', 'protesta', 'vehicular', 'uso_fuerza'
    title TEXT NOT NULL,                    -- 'La policía me pide DNI'
    description TEXT NOT NULL,              -- Descripción detallada de la situación
    keywords TEXT NOT NULL,                 -- 'dni,identidad,documento,identificacion,papeles' (para búsqueda)
    natural_queries TEXT NOT NULL,          -- 'me piden DNI|me piden documentos|me piden identificarme|me paran en la calle' (consultas naturales del usuario)
    severity TEXT DEFAULT 'medium',         -- 'low', 'medium', 'high', 'critical'
    icon TEXT,                              -- Icono para UI
    parent_situation_id TEXT,               -- Para situaciones anidadas (ej: registro > registro_mochila, registro_celular)
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (parent_situation_id) REFERENCES situations(id)
);

-- ============================================================
-- 3. CONTEXTOS
-- Modificadores que cambian los derechos aplicables
-- ============================================================

CREATE TABLE contexts (
    id TEXT PRIMARY KEY,                    -- 'estado_emergencia_seguridad'
    name TEXT NOT NULL,                     -- 'Estado de emergencia por seguridad ciudadana'
    description TEXT NOT NULL,              -- Qué implica este contexto
    context_type TEXT NOT NULL,             -- 'estado_emergencia', 'toque_queda', 'operativo', 'normal'
    affects_rights TEXT,                    -- JSON array de IDs de derechos que modifica
    is_currently_active BOOLEAN DEFAULT FALSE,
    active_regions TEXT,                    -- JSON array: ['lima_metropolitana', 'callao']
    decree_number TEXT,                     -- 'DS N° 006-2026-PCM'
    start_date TEXT,
    end_date TEXT,
    source_id TEXT,
    FOREIGN KEY (source_id) REFERENCES legal_sources(id)
);

-- ============================================================
-- 4. DERECHOS
-- Qué derechos tiene el ciudadano en cada situación
-- ============================================================

CREATE TABLE rights (
    id TEXT PRIMARY KEY,                    -- 'right_no_cell_search'
    title TEXT NOT NULL,                    -- 'No pueden revisar tu celular'
    description TEXT NOT NULL,              -- Explicación en lenguaje simple
    legal_basis TEXT NOT NULL,              -- Resumen de base legal
    is_absolute BOOLEAN DEFAULT FALSE,      -- TRUE = no se suspende ni en emergencia
    never_suspended BOOLEAN DEFAULT FALSE,  -- TRUE = ni en estado de emergencia
    category TEXT NOT NULL,                 -- 'libertad', 'integridad', 'comunicaciones', 'propiedad', 'debido_proceso', 'dignidad'
    display_order INTEGER DEFAULT 0
);

-- Relación: qué derechos aplican a qué situación
CREATE TABLE situation_rights (
    situation_id TEXT NOT NULL,
    right_id TEXT NOT NULL,
    context_id TEXT DEFAULT 'normal',       -- En qué contexto aplica esta relación
    applies BOOLEAN DEFAULT TRUE,           -- TRUE = el derecho aplica, FALSE = está suspendido en este contexto
    notes TEXT,                             -- Notas específicas de esta combinación
    PRIMARY KEY (situation_id, right_id, context_id),
    FOREIGN KEY (situation_id) REFERENCES situations(id),
    FOREIGN KEY (right_id) REFERENCES rights(id),
    FOREIGN KEY (context_id) REFERENCES contexts(id)
);

-- Relación: qué fuentes legales respaldan qué derechos
CREATE TABLE right_sources (
    right_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    relevance TEXT DEFAULT 'primary',       -- 'primary', 'supporting', 'jurisprudence'
    PRIMARY KEY (right_id, source_id),
    FOREIGN KEY (right_id) REFERENCES rights(id),
    FOREIGN KEY (source_id) REFERENCES legal_sources(id)
);

-- ============================================================
-- 5. ACCIONES
-- Qué puede HACER el ciudadano en cada situación
-- ============================================================

CREATE TABLE actions (
    id TEXT PRIMARY KEY,                    -- 'action_request_police_id'
    action_type TEXT NOT NULL,              -- 'decir', 'hacer', 'no_hacer', 'grabar', 'llamar', 'documentar'
    title TEXT NOT NULL,                    -- 'Exige identificación del policía'
    description TEXT NOT NULL,              -- 'Tienes derecho a pedir nombre, grado y dependencia del policía'
    script TEXT,                            -- Texto sugerido para decir: "Oficial, ¿podría identificarse por favor?"
    priority INTEGER DEFAULT 0,            -- Orden de importancia (1 = primero que debes hacer)
    is_recommended BOOLEAN DEFAULT TRUE,    -- TRUE = recomendado, FALSE = opcional pero legal
    warning TEXT,                           -- Advertencia: "No te resistas físicamente aunque tengas derecho"
    legal_basis_summary TEXT               -- Base legal resumida
);

-- Relación: qué acciones corresponden a qué situación
CREATE TABLE situation_actions (
    situation_id TEXT NOT NULL,
    action_id TEXT NOT NULL,
    context_id TEXT DEFAULT 'normal',
    step_order INTEGER NOT NULL,            -- Orden: paso 1, paso 2, etc.
    is_available BOOLEAN DEFAULT TRUE,      -- Disponible en este contexto
    PRIMARY KEY (situation_id, action_id, context_id),
    FOREIGN KEY (situation_id) REFERENCES situations(id),
    FOREIGN KEY (action_id) REFERENCES actions(id),
    FOREIGN KEY (context_id) REFERENCES contexts(id)
);

-- ============================================================
-- 6. LÍMITES TEMPORALES
-- Plazos máximos legales (el temporizador de la app)
-- ============================================================

CREATE TABLE time_limits (
    id TEXT PRIMARY KEY,                    -- 'limit_retention_national'
    situation_id TEXT NOT NULL,
    description TEXT NOT NULL,              -- 'Retención por identificación (nacionales)'
    max_hours REAL NOT NULL,                -- 4.0
    max_hours_emergency REAL,               -- Puede cambiar en emergencia
    applies_to TEXT DEFAULT 'nacional',     -- 'nacional', 'extranjero', 'todos'
    after_expiry_action TEXT NOT NULL,      -- 'Deben soltarte o conseguir orden judicial'
    source_id TEXT NOT NULL,
    FOREIGN KEY (situation_id) REFERENCES situations(id),
    FOREIGN KEY (source_id) REFERENCES legal_sources(id)
);

-- ============================================================
-- 7. CONTACTOS DE EMERGENCIA INSTITUCIONALES
-- A quién llamar según la situación
-- ============================================================

CREATE TABLE emergency_contacts (
    id TEXT PRIMARY KEY,                    -- 'defensoria_pueblo'
    institution TEXT NOT NULL,              -- 'Defensoría del Pueblo'
    description TEXT NOT NULL,              -- 'Organismo autónomo que supervisa comisarías'
    phone TEXT,                             -- '0800-15-170'
    whatsapp TEXT,                          -- '+51 947 951 412'
    email TEXT,                             -- 'consulta@defensoria.gob.pe'
    website TEXT,                           -- 'apps2.defensoria.gob.pe/sidPublic/'
    address TEXT,                           -- 'Jr. Ucayali 394-398, Lima'
    is_free BOOLEAN DEFAULT TRUE,           -- Servicio gratuito
    requires_lawyer BOOLEAN DEFAULT FALSE,  -- Necesita abogado
    available_hours TEXT,                   -- '24/7' o 'L-V 8:00-17:00'
    contact_type TEXT NOT NULL,             -- 'denuncia', 'asesoria', 'emergencia', 'habeas_corpus'
    priority INTEGER DEFAULT 0             -- Orden de recomendación
);

-- Relación: qué contactos son relevantes para qué situación
CREATE TABLE situation_contacts (
    situation_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    priority INTEGER DEFAULT 0,             -- Orden de recomendación para esta situación
    notes TEXT,                             -- Nota específica: "Llamar si la retención supera 4 horas"
    PRIMARY KEY (situation_id, contact_id),
    FOREIGN KEY (situation_id) REFERENCES situations(id),
    FOREIGN KEY (contact_id) REFERENCES emergency_contacts(id)
);

-- ============================================================
-- 8. SUSTANCIAS Y CANTIDADES LEGALES
-- Tabla específica para posesión personal (Art. 299 CP)
-- ============================================================

CREATE TABLE legal_possession (
    id TEXT PRIMARY KEY,                    -- 'cannabis'
    substance TEXT NOT NULL,                -- 'Marihuana (Cannabis sativa)'
    max_grams REAL NOT NULL,                -- 8.0
    legal_article TEXT NOT NULL,            -- 'Artículo 299, Código Penal'
    notes TEXT,                             -- 'Para consumo personal inmediato'
    is_punishable_below_limit BOOLEAN DEFAULT FALSE,  -- FALSE = no es delito bajo el límite
    source_id TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES legal_sources(id)
);

-- ============================================================
-- 9. NIVELES DE FUERZA POLICIAL
-- Referencia de qué nivel de fuerza es legal en cada situación
-- ============================================================

CREATE TABLE force_levels (
    id TEXT PRIMARY KEY,                    -- 'level_1_presence'
    level_number INTEGER NOT NULL,          -- 1
    citizen_behavior TEXT NOT NULL,         -- 'Cooperador / Riesgo latente'
    authorized_response TEXT NOT NULL,      -- 'Presencia policial y verbalización'
    description TEXT NOT NULL,              -- Explicación en lenguaje simple
    examples_legal TEXT,                    -- Ejemplos de uso legal
    examples_illegal TEXT,                  -- Ejemplos de abuso en este nivel
    source_id TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES legal_sources(id)
);

-- ============================================================
-- 10. REPORTES CIUDADANOS (Fase 3 - Comunidad)
-- Registro anónimo de intervenciones para el mapa de calor
-- ============================================================

CREATE TABLE incident_reports (
    id TEXT PRIMARY KEY,                    -- UUID generado
    reported_at TEXT NOT NULL,              -- Timestamp del reporte
    incident_date TEXT NOT NULL,            -- Fecha del incidente
    incident_time TEXT,                     -- Hora aproximada
    latitude REAL,                          -- Ubicación GPS
    longitude REAL,
    district TEXT,                          -- 'Callao', 'San Juan de Lurigancho', etc.
    region TEXT,                            -- 'Lima Metropolitana'
    situation_ids TEXT,                      -- JSON array de situaciones que aplican
    violations TEXT,                         -- JSON array: ['registro_ilegal', 'exceso_fuerza', 'detencion_arbitraria']
    police_station TEXT,                    -- Comisaría involucrada (opcional)
    police_identified BOOLEAN DEFAULT FALSE, -- ¿Se identificó el policía?
    duration_minutes INTEGER,               -- Duración de la intervención
    had_recording BOOLEAN DEFAULT FALSE,    -- ¿Grabó la intervención?
    description TEXT,                        -- Descripción libre (opcional)
    outcome TEXT,                            -- 'liberado', 'detenido', 'comisaria', 'golpeado'
    is_anonymous BOOLEAN DEFAULT TRUE,
    user_id TEXT,                            -- NULL si anónimo
    verified BOOLEAN DEFAULT FALSE           -- Verificado por moderadores/abogados
);

-- ============================================================
-- 11. USUARIOS (Fase 2-3)
-- Datos mínimos, privacidad máxima
-- ============================================================

CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    region TEXT,                            -- Para contextualizar (emergencia local, etc.)
    emergency_contacts TEXT,                -- JSON array cifrado de contactos personales
    panic_message TEXT,                     -- Mensaje personalizado para botón de pánico
    is_witness_volunteer BOOLEAN DEFAULT FALSE,  -- ¿Disponible como testigo?
    witness_radius_km REAL DEFAULT 1.0      -- Radio de alerta como testigo
);

-- ============================================================
-- 12. PREGUNTAS FRECUENTES
-- Para la sección educativa (el tío de Loko)
-- ============================================================

CREATE TABLE myths (
    id TEXT PRIMARY KEY,                    -- 'myth_ddhh_protect_criminals'
    myth TEXT NOT NULL,                     -- 'Los derechos humanos protegen a los delincuentes'
    reality TEXT NOT NULL,                  -- 'Los DDHH protegen el proceso justo...'
    explanation TEXT NOT NULL,              -- Explicación detallada en lenguaje simple
    related_sources TEXT,                   -- JSON array de source IDs
    category TEXT NOT NULL,                 -- 'derechos_humanos', 'poder_policial', 'estado_emergencia', 'drogas'
    display_order INTEGER DEFAULT 0
);

-- ============================================================
-- ÍNDICES para búsqueda rápida (offline performance)
-- ============================================================

CREATE INDEX idx_situations_category ON situations(category);
CREATE INDEX idx_situations_keywords ON situations(keywords);
CREATE INDEX idx_rights_category ON rights(category);
CREATE INDEX idx_contexts_active ON contexts(is_currently_active);
CREATE INDEX idx_time_limits_situation ON time_limits(situation_id);
CREATE INDEX idx_incident_reports_district ON incident_reports(district);
CREATE INDEX idx_incident_reports_date ON incident_reports(incident_date);
CREATE INDEX idx_legal_sources_type ON legal_sources(source_type);
CREATE INDEX idx_legal_sources_status ON legal_sources(status);

-- ============================================================
-- VISTAS útiles para la app
-- ============================================================

-- Vista: Situación completa con derechos, acciones y contactos
CREATE VIEW v_situation_full AS
SELECT 
    s.id AS situation_id,
    s.title AS situation_title,
    s.category,
    s.severity,
    r.title AS right_title,
    r.description AS right_description,
    r.is_absolute,
    sr.context_id,
    sr.applies
FROM situations s
JOIN situation_rights sr ON s.id = sr.situation_id
JOIN rights r ON sr.right_id = r.id
WHERE s.is_active = TRUE;

-- Vista: Acciones paso a paso por situación
CREATE VIEW v_situation_steps AS
SELECT 
    s.id AS situation_id,
    s.title AS situation_title,
    a.title AS action_title,
    a.description AS action_description,
    a.script,
    a.action_type,
    a.warning,
    sa.step_order,
    sa.context_id
FROM situations s
JOIN situation_actions sa ON s.id = sa.situation_id
JOIN actions a ON sa.action_id = a.id
WHERE sa.is_available = TRUE
ORDER BY sa.step_order;

-- Vista: Mapa de calor de reportes
CREATE VIEW v_heatmap AS
SELECT 
    district,
    region,
    COUNT(*) AS total_reports,
    SUM(CASE WHEN had_recording THEN 1 ELSE 0 END) AS with_recording,
    AVG(duration_minutes) AS avg_duration
FROM incident_reports
GROUP BY district, region;
