#!/usr/bin/env python3
"""
Truths and Rights — Buscador de lenguaje natural
Matchea consultas del usuario con situaciones en la base de datos.

Uso como modulo:
    from search import search_situation
    results = search_situation("me quieren revisar el celular")

Uso directo:
    python search.py "me quieren revisar el celular"

Funciona offline: SQLite + Python puro, sin dependencias externas.
"""

import io
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

# Fix encoding on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "build" / "truths_and_rights_pe.db"


def normalize(text):
    """Normaliza texto: minusculas, sin tildes, sin puntuacion."""
    text = text.lower().strip()
    # Quitar tildes
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Quitar puntuacion
    text = re.sub(r'[^\w\s]', '', text)
    # Colapsar espacios
    text = re.sub(r'\s+', ' ', text)
    return text


def tokenize(text):
    """Divide texto normalizado en tokens unicos."""
    return set(normalize(text).split())


# Palabras que no aportan al matching
STOPWORDS = {
    'me', 'mi', 'yo', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'en', 'a', 'al', 'por', 'para', 'con', 'sin', 'que', 'es',
    'y', 'o', 'no', 'si', 'se', 'lo', 'le', 'les', 'su', 'sus', 'como',
    'pero', 'mas', 'muy', 'ya', 'esta', 'esto', 'ese', 'esa', 'esos', 'esas',
    'hay', 'han', 'ha', 'he', 'ser', 'son', 'fue', 'van', 'ir', 'te', 'tu',
    'nos', 'cuando', 'donde', 'quien', 'cual', 'cuanto'
}


def tokens_sin_stopwords(text):
    """Tokeniza y filtra stopwords."""
    return tokenize(text) - STOPWORDS


def score_keyword_match(query_tokens, keywords_str):
    """Puntaje por coincidencia con keywords de la situacion."""
    kw_tokens = tokenize(keywords_str)
    matches = query_tokens & kw_tokens
    if not matches:
        return 0.0
    return len(matches) / len(kw_tokens)


def score_natural_query_match(query_norm, natural_queries_str):
    """Puntaje por similitud con natural_queries de la situacion."""
    queries = natural_queries_str.split('|')
    best = 0.0

    for nq in queries:
        nq_norm = normalize(nq)

        # Match exacto o contenido
        if query_norm == nq_norm:
            return 1.0
        if query_norm in nq_norm or nq_norm in query_norm:
            ratio = min(len(query_norm), len(nq_norm)) / max(len(query_norm), len(nq_norm))
            best = max(best, 0.7 + 0.3 * ratio)
            continue

        # Match por tokens compartidos
        q_tokens = tokens_sin_stopwords(query_norm)
        nq_tokens = tokens_sin_stopwords(nq_norm)

        if not q_tokens or not nq_tokens:
            continue

        shared = q_tokens & nq_tokens
        if shared:
            precision = len(shared) / len(q_tokens)
            recall = len(shared) / len(nq_tokens)
            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
                best = max(best, f1 * 0.8)

    return best


def score_title_match(query_norm, title):
    """Puntaje por similitud con el titulo de la situacion."""
    title_norm = normalize(title)
    q_tokens = tokens_sin_stopwords(query_norm)
    t_tokens = tokens_sin_stopwords(title_norm)

    if not q_tokens or not t_tokens:
        return 0.0

    shared = q_tokens & t_tokens
    if shared:
        return len(shared) / max(len(q_tokens), len(t_tokens)) * 0.5
    return 0.0


def score_partial_match(query_tokens, target_str):
    """Puntaje por coincidencia parcial (prefijos de 4+ caracteres)."""
    target_tokens = tokenize(target_str)
    score = 0.0

    for qt in query_tokens:
        if len(qt) < 4:
            continue
        for tt in target_tokens:
            if len(tt) < 4:
                continue
            # Prefijo comun
            prefix = qt[:4]
            if tt.startswith(prefix):
                overlap = 0
                for i in range(min(len(qt), len(tt))):
                    if qt[i] == tt[i]:
                        overlap += 1
                    else:
                        break
                ratio = overlap / max(len(qt), len(tt))
                score = max(score, ratio * 0.4)

    return score


def search_situation(query, db_path=None, limit=3):
    """
    Busca la situacion mas relevante para una consulta en lenguaje natural.

    Args:
        query: Texto del usuario (ej: "me quieren revisar el celular")
        db_path: Ruta a la base de datos SQLite (opcional)
        limit: Numero maximo de resultados

    Returns:
        Lista de dicts con situation_id, title, score, y match_details
    """
    if db_path is None:
        db_path = DB_PATH

    if not Path(db_path).exists():
        print(f"ERROR: No se encontro la base de datos: {db_path}")
        print("Ejecuta primero: python scripts/build_db.py --country PE")
        return []

    query_norm = normalize(query)
    query_tokens = tokens_sin_stopwords(query)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, keywords, natural_queries, severity, category
        FROM situations
        WHERE is_active = 1
    """)

    results = []

    for row in cursor.fetchall():
        s_id = row['id']
        keywords = row['keywords'] or ''
        natural_q = row['natural_queries'] or ''
        title = row['title'] or ''

        # Calcular puntajes parciales
        kw_score = score_keyword_match(query_tokens, keywords)
        nq_score = score_natural_query_match(query_norm, natural_q)
        title_score = score_title_match(query_norm, title)
        partial_score = score_partial_match(query_tokens, keywords + ' ' + natural_q)

        # Puntaje final ponderado
        total = (nq_score * 0.45) + (kw_score * 0.30) + (title_score * 0.15) + (partial_score * 0.10)

        if total > 0.05:
            results.append({
                'situation_id': s_id,
                'title': title,
                'description': row['description'],
                'severity': row['severity'],
                'category': row['category'],
                'score': round(total, 4),
                'match_details': {
                    'natural_query': round(nq_score, 3),
                    'keywords': round(kw_score, 3),
                    'title': round(title_score, 3),
                    'partial': round(partial_score, 3),
                }
            })

    conn.close()

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]


def get_situation_details(situation_id, db_path=None):
    """
    Obtiene todos los detalles de una situacion: derechos, acciones, contactos.

    Returns:
        Dict con rights, actions, contacts, time_limits
    """
    if db_path is None:
        db_path = DB_PATH

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Derechos
    c.execute("""
        SELECT r.id, r.title, r.description, r.legal_basis,
               r.is_absolute, r.never_suspended, r.category,
               sr.context_id, sr.applies, sr.notes
        FROM situation_rights sr
        JOIN rights r ON sr.right_id = r.id
        WHERE sr.situation_id = ?
        ORDER BY r.display_order
    """, (situation_id,))
    rights = [dict(row) for row in c.fetchall()]

    # Acciones
    c.execute("""
        SELECT a.id, a.action_type, a.title, a.description,
               a.script, a.warning, a.legal_basis_summary,
               sa.step_order
        FROM situation_actions sa
        JOIN actions a ON sa.action_id = a.id
        WHERE sa.situation_id = ? AND sa.is_available = 1
        ORDER BY sa.step_order
    """, (situation_id,))
    actions = [dict(row) for row in c.fetchall()]

    # Contactos
    c.execute("""
        SELECT ec.id, ec.institution, ec.description,
               ec.phone, ec.whatsapp, ec.email, ec.website,
               ec.available_hours, ec.is_free, ec.contact_type
        FROM situation_contacts sc
        JOIN emergency_contacts ec ON sc.contact_id = ec.id
        WHERE sc.situation_id = ?
        ORDER BY sc.priority
    """, (situation_id,))
    contacts = [dict(row) for row in c.fetchall()]

    # Limites de tiempo
    c.execute("""
        SELECT id, description, max_hours, max_hours_emergency,
               applies_to, after_expiry_action
        FROM time_limits
        WHERE situation_id = ?
    """, (situation_id,))
    time_limits = [dict(row) for row in c.fetchall()]

    conn.close()

    return {
        'rights': rights,
        'actions': actions,
        'contacts': contacts,
        'time_limits': time_limits,
    }


# --- Ejecucion directa ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python search.py \"tu consulta\"")
        print("Ejemplo: python search.py \"me quieren revisar el celular\"")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    print(f"\nBuscando: \"{query}\"\n")

    results = search_situation(query)

    if not results:
        print("No se encontraron situaciones relevantes.")
        sys.exit(0)

    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['score']:.2f}] {r['title']}")
        print(f"   ID: {r['situation_id']}")
        print(f"   Detalles: nq={r['match_details']['natural_query']:.2f} "
              f"kw={r['match_details']['keywords']:.2f} "
              f"ti={r['match_details']['title']:.2f} "
              f"pa={r['match_details']['partial']:.2f}")
        print()
