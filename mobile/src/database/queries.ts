import * as SQLite from 'expo-sqlite';
import type {
  Situation,
  Context,
  Right,
  SituationRight,
  SituationAction,
  TimeLimit,
  EmergencyContact,
  Myth,
  LegalPossession,
  ForceLevel,
  SituationDetails,
} from '../types/database';

/**
 * Queries SQL tipadas — todas las consultas que la app necesita.
 * Port de scripts/cli.py get_situation_details().
 */

// --- Situaciones ---

/** Obtiene todas las situaciones activas, ordenadas por display_order. */
export async function getAllSituations(db: SQLite.SQLiteDatabase): Promise<Situation[]> {
  return db.getAllAsync<Situation>(
    `SELECT id, category, title, description, keywords, natural_queries,
            severity, icon, parent_situation_id, display_order, is_active
     FROM situations
     WHERE is_active = 1
     ORDER BY display_order, title`
  );
}

/** Obtiene una situacion por ID. */
export async function getSituation(db: SQLite.SQLiteDatabase, id: string): Promise<Situation | null> {
  return db.getFirstAsync<Situation>(
    'SELECT * FROM situations WHERE id = ?',
    [id]
  );
}

// --- Contextos ---

/** Obtiene todos los contextos. */
export async function getAllContexts(db: SQLite.SQLiteDatabase): Promise<Context[]> {
  return db.getAllAsync<Context>('SELECT * FROM contexts');
}

/** Obtiene el contexto de emergencia activo, si existe. */
export async function getActiveEmergencyContext(db: SQLite.SQLiteDatabase): Promise<Context | null> {
  return db.getFirstAsync<Context>(
    `SELECT * FROM contexts
     WHERE is_currently_active = 1
       AND context_type = 'estado_emergencia'
     LIMIT 1`
  );
}

// --- Derechos por situacion ---

/** Obtiene derechos para una situacion, con info del contexto. */
export async function getRightsForSituation(
  db: SQLite.SQLiteDatabase,
  situationId: string
): Promise<SituationRight[]> {
  return db.getAllAsync<SituationRight>(
    `SELECT r.id, r.title, r.description, r.legal_basis,
            r.is_absolute, r.never_suspended, r.category,
            sr.context_id, sr.applies, sr.notes,
            sr.situation_id, sr.right_id
     FROM situation_rights sr
     JOIN rights r ON sr.right_id = r.id
     WHERE sr.situation_id = ?
     ORDER BY r.display_order`,
    [situationId]
  );
}

// --- Acciones por situacion ---

/** Obtiene acciones para una situacion, ordenadas por step_order. */
export async function getActionsForSituation(
  db: SQLite.SQLiteDatabase,
  situationId: string
): Promise<SituationAction[]> {
  return db.getAllAsync<SituationAction>(
    `SELECT a.id, a.action_type, a.title, a.description,
            a.script, a.warning, a.legal_basis_summary,
            sa.step_order, sa.context_id, sa.is_available,
            sa.situation_id, sa.action_id
     FROM situation_actions sa
     JOIN actions a ON sa.action_id = a.id
     WHERE sa.situation_id = ? AND sa.is_available = 1
     ORDER BY sa.step_order`,
    [situationId]
  );
}

// --- Limites de tiempo ---

/** Obtiene limites de tiempo para una situacion. */
export async function getTimeLimitsForSituation(
  db: SQLite.SQLiteDatabase,
  situationId: string
): Promise<TimeLimit[]> {
  return db.getAllAsync<TimeLimit>(
    `SELECT id, situation_id, description, max_hours, max_hours_emergency,
            applies_to, after_expiry_action
     FROM time_limits
     WHERE situation_id = ?`,
    [situationId]
  );
}

// --- Contactos por situacion ---

/** Obtiene contactos de emergencia para una situacion, ordenados por prioridad. */
export async function getContactsForSituation(
  db: SQLite.SQLiteDatabase,
  situationId: string
): Promise<EmergencyContact[]> {
  return db.getAllAsync<EmergencyContact>(
    `SELECT ec.id, ec.institution, ec.description,
            ec.phone, ec.whatsapp, ec.email, ec.website,
            ec.address, ec.available_hours, ec.is_free,
            ec.requires_lawyer, ec.contact_type, ec.priority
     FROM situation_contacts sc
     JOIN emergency_contacts ec ON sc.contact_id = ec.id
     WHERE sc.situation_id = ?
     ORDER BY sc.priority`,
    [situationId]
  );
}

/** Obtiene todos los detalles de una situacion en paralelo. */
export async function getSituationDetails(
  db: SQLite.SQLiteDatabase,
  situationId: string
): Promise<SituationDetails> {
  const [rights, actions, contacts, time_limits] = await Promise.all([
    getRightsForSituation(db, situationId),
    getActionsForSituation(db, situationId),
    getContactsForSituation(db, situationId),
    getTimeLimitsForSituation(db, situationId),
  ]);

  return { rights, actions, contacts, time_limits };
}

// --- Derechos ---

/** Obtiene todos los derechos, ordenados por categoria y display_order. */
export async function getAllRights(db: SQLite.SQLiteDatabase): Promise<Right[]> {
  return db.getAllAsync<Right>(
    `SELECT id, title, description, legal_basis, is_absolute,
            never_suspended, category, display_order
     FROM rights
     ORDER BY category, display_order`
  );
}

// --- Contactos ---

/** Obtiene todos los contactos de emergencia. */
export async function getAllContacts(db: SQLite.SQLiteDatabase): Promise<EmergencyContact[]> {
  return db.getAllAsync<EmergencyContact>(
    `SELECT * FROM emergency_contacts ORDER BY priority`
  );
}

// --- Mitos ---

/** Obtiene todos los mitos, ordenados por display_order. */
export async function getAllMyths(db: SQLite.SQLiteDatabase): Promise<Myth[]> {
  return db.getAllAsync<Myth>(
    'SELECT * FROM myths ORDER BY display_order'
  );
}

// --- Posesion legal ---

/** Obtiene todas las sustancias con limites legales. */
export async function getAllLegalPossession(db: SQLite.SQLiteDatabase): Promise<LegalPossession[]> {
  return db.getAllAsync<LegalPossession>(
    'SELECT * FROM legal_possession'
  );
}

// --- Niveles de fuerza ---

/** Obtiene todos los niveles de fuerza, ordenados por nivel. */
export async function getAllForceLevels(db: SQLite.SQLiteDatabase): Promise<ForceLevel[]> {
  return db.getAllAsync<ForceLevel>(
    'SELECT * FROM force_levels ORDER BY level_number'
  );
}
