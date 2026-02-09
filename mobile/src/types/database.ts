/**
 * Interfaces TypeScript para las tablas de la base de datos.
 * Corresponden al schema en schema/database_schema.sql.
 */

export interface Situation {
  id: string;
  category: string;
  title: string;
  description: string;
  keywords: string;
  natural_queries: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  icon: string | null;
  parent_situation_id: string | null;
  display_order: number;
  is_active: boolean;
}

export interface Context {
  id: string;
  name: string;
  description: string;
  context_type: 'estado_emergencia' | 'toque_queda' | 'operativo' | 'normal';
  affects_rights: string | null; // JSON array
  is_currently_active: boolean;
  active_regions: string | null; // JSON array
  decree_number: string | null;
  start_date: string | null;
  end_date: string | null;
  source_id: string | null;
}

export interface Right {
  id: string;
  title: string;
  description: string;
  legal_basis: string;
  is_absolute: boolean;
  never_suspended: boolean;
  category: string;
  display_order: number;
}

export interface SituationRight {
  situation_id: string;
  right_id: string;
  context_id: string;
  applies: boolean;
  notes: string | null;
  // Joined fields from rights table
  title: string;
  description: string;
  legal_basis: string;
  is_absolute: boolean;
  never_suspended: boolean;
  category: string;
}

export interface Action {
  id: string;
  action_type: 'decir' | 'hacer' | 'no_hacer' | 'grabar' | 'llamar' | 'documentar';
  title: string;
  description: string;
  script: string | null;
  priority: number;
  is_recommended: boolean;
  warning: string | null;
  legal_basis_summary: string | null;
}

export interface SituationAction {
  situation_id: string;
  action_id: string;
  context_id: string;
  step_order: number;
  is_available: boolean;
  // Joined fields from actions table
  action_type: string;
  title: string;
  description: string;
  script: string | null;
  warning: string | null;
  legal_basis_summary: string | null;
}

export interface TimeLimit {
  id: string;
  situation_id: string;
  description: string;
  max_hours: number;
  max_hours_emergency: number | null;
  applies_to: 'nacional' | 'extranjero' | 'todos';
  after_expiry_action: string;
}

export interface EmergencyContact {
  id: string;
  institution: string;
  description: string;
  phone: string | null;
  whatsapp: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  is_free: boolean;
  requires_lawyer: boolean;
  available_hours: string | null;
  contact_type: 'denuncia' | 'asesoria' | 'emergencia' | 'habeas_corpus';
  priority: number;
}

export interface Myth {
  id: string;
  myth: string;
  reality: string;
  explanation: string;
  related_sources: string | null; // JSON array
  category: string;
  display_order: number;
}

export interface LegalPossession {
  id: string;
  substance: string;
  max_grams: number;
  legal_article: string;
  notes: string | null;
  is_punishable_below_limit: boolean;
}

export interface ForceLevel {
  id: string;
  level_number: number;
  citizen_behavior: string;
  authorized_response: string;
  description: string;
  examples_legal: string | null;
  examples_illegal: string | null;
}

/** Resultado de busqueda */
export interface SearchResult {
  situation_id: string;
  title: string;
  description: string;
  severity: string;
  category: string;
  score: number;
  match_details: {
    natural_query: number;
    keywords: number;
    title: number;
    partial: number;
  };
}

/** Detalles completos de una situacion */
export interface SituationDetails {
  rights: SituationRight[];
  actions: SituationAction[];
  contacts: EmergencyContact[];
  time_limits: TimeLimit[];
}
