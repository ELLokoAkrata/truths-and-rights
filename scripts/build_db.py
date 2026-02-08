#!/usr/bin/env python3
"""
Truths and Rights — Build Script
Convierte los archivos JSON de datos legales a una base de datos SQLite.

Uso:
    python build_db.py                    # Build todos los países
    python build_db.py --country PE       # Build solo Perú
    python build_db.py --validate         # Solo validar, no construir
"""

import json
import sqlite3
import os
import sys
import io
import argparse
from datetime import datetime
from pathlib import Path

# Fix encoding on Windows consoles (cp1252 can't handle emojis)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "build"


def load_schema(conn):
    """Carga el schema SQL en la base de datos."""
    schema_path = SCHEMA_DIR / "database_schema.sql"
    if not schema_path.exists():
        print(f"ERROR: No se encontró {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    print("✓ Schema cargado")


def load_json(filepath):
    """Carga un archivo JSON con manejo de errores."""
    if not filepath.exists():
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data if isinstance(data, list) else [data]


def validate_source(source):
    """Valida que una fuente legal tenga los campos requeridos."""
    required = ['id', 'source_type', 'name', 'full_text', 'summary', 'status']
    missing = [f for f in required if f not in source or not source[f]]
    
    if missing:
        print(f"  ⚠ Fuente '{source.get('id', '?')}' le faltan campos: {missing}")
        return False
    
    valid_types = ['constitucion', 'codigo_penal', 'codigo_procesal', 
                   'decreto_legislativo', 'ley', 'jurisprudencia', 'tratado_internacional']
    if source['source_type'] not in valid_types:
        print(f"  ⚠ Fuente '{source['id']}' tiene source_type inválido: {source['source_type']}")
        return False
    
    return True


def validate_situation(situation):
    """Valida que una situación tenga los campos requeridos."""
    required = ['id', 'category', 'title', 'description', 'keywords', 'natural_queries']
    missing = [f for f in required if f not in situation or not situation[f]]
    
    if missing:
        print(f"  ⚠ Situación '{situation.get('id', '?')}' le faltan campos: {missing}")
        return False
    
    return True


def insert_sources(conn, sources, country):
    """Inserta fuentes legales en la base de datos."""
    count = 0
    for source in sources:
        if not validate_source(source):
            continue
        
        conn.execute("""
            INSERT OR REPLACE INTO legal_sources 
            (id, source_type, name, article, full_text, summary, 
             publication_date, last_modified, official_url, status, country,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source['id'],
            source['source_type'],
            source['name'],
            source.get('article'),
            source['full_text'],
            source['summary'],
            source.get('publication_date'),
            source.get('last_modified'),
            source.get('official_url'),
            source['status'],
            country,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        count += 1
    
    print(f"  ✓ {count} fuentes legales insertadas")


def insert_rights(conn, rights):
    """Inserta derechos en la base de datos."""
    count = 0
    for right in rights:
        conn.execute("""
            INSERT OR REPLACE INTO rights
            (id, title, description, legal_basis, is_absolute, never_suspended, category, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            right['id'],
            right['title'],
            right['description'],
            right['legal_basis'],
            right.get('is_absolute', False),
            right.get('never_suspended', False),
            right['category'],
            right.get('display_order', 0)
        ))
        
        # Insertar relación con fuentes
        for source_id in right.get('source_ids', []):
            conn.execute("""
                INSERT OR REPLACE INTO right_sources (right_id, source_id, relevance)
                VALUES (?, ?, 'primary')
            """, (right['id'], source_id))
        
        count += 1
    
    print(f"  ✓ {count} derechos insertados")


def insert_actions(conn, actions):
    """Inserta acciones en la base de datos."""
    count = 0
    for action in actions:
        conn.execute("""
            INSERT OR REPLACE INTO actions
            (id, action_type, title, description, script, priority, 
             is_recommended, warning, legal_basis_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action['id'],
            action['action_type'],
            action['title'],
            action['description'],
            action.get('script'),
            action.get('priority', 0),
            action.get('is_recommended', True),
            action.get('warning'),
            action.get('legal_basis_summary')
        ))
        count += 1
    
    print(f"  ✓ {count} acciones insertadas")


def insert_situations(conn, situations):
    """Inserta situaciones con sus relaciones."""
    count = 0
    for sit in situations:
        if not validate_situation(sit):
            continue
        
        keywords = ','.join(sit['keywords']) if isinstance(sit['keywords'], list) else sit['keywords']
        natural_q = '|'.join(sit['natural_queries']) if isinstance(sit['natural_queries'], list) else sit['natural_queries']
        
        conn.execute("""
            INSERT OR REPLACE INTO situations
            (id, category, title, description, keywords, natural_queries,
             severity, icon, parent_situation_id, display_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sit['id'],
            sit['category'],
            sit['title'],
            sit['description'],
            keywords,
            natural_q,
            sit.get('severity', 'medium'),
            sit.get('icon'),
            sit.get('parent_situation_id'),
            sit.get('display_order', 0),
            True
        ))
        
        # Insertar relaciones con derechos
        for right_rel in sit.get('rights', []):
            conn.execute("""
                INSERT OR REPLACE INTO situation_rights
                (situation_id, right_id, context_id, applies, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sit['id'],
                right_rel['right_id'],
                right_rel.get('context', 'normal'),
                right_rel.get('applies', True),
                right_rel.get('notes')
            ))
        
        # Insertar relaciones con acciones
        for action_rel in sit.get('actions', []):
            conn.execute("""
                INSERT OR REPLACE INTO situation_actions
                (situation_id, action_id, context_id, step_order, is_available)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sit['id'],
                action_rel['action_id'],
                action_rel.get('context', 'normal'),
                action_rel['step_order'],
                action_rel.get('is_available', True)
            ))
        
        # Insertar contactos
        for i, contact_id in enumerate(sit.get('contacts', [])):
            conn.execute("""
                INSERT OR REPLACE INTO situation_contacts
                (situation_id, contact_id, priority)
                VALUES (?, ?, ?)
            """, (sit['id'], contact_id, i + 1))
        
        count += 1
    
    print(f"  ✓ {count} situaciones insertadas (con relaciones)")


def insert_contacts(conn, contacts):
    """Inserta contactos de emergencia."""
    count = 0
    for contact in contacts:
        conn.execute("""
            INSERT OR REPLACE INTO emergency_contacts
            (id, institution, description, phone, whatsapp, email, website,
             address, is_free, requires_lawyer, available_hours, contact_type, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact['id'],
            contact['institution'],
            contact['description'],
            contact.get('phone'),
            contact.get('whatsapp'),
            contact.get('email'),
            contact.get('website'),
            contact.get('address'),
            contact.get('is_free', True),
            contact.get('requires_lawyer', False),
            contact.get('available_hours'),
            contact['contact_type'],
            contact.get('priority', 0)
        ))
        count += 1
    
    print(f"  ✓ {count} contactos de emergencia insertados")


def insert_contexts(conn, contexts):
    """Inserta contextos en la base de datos."""
    count = 0
    for ctx in contexts:
        conn.execute("""
            INSERT OR REPLACE INTO contexts
            (id, name, description, context_type, affects_rights,
             is_currently_active, active_regions, decree_number,
             start_date, end_date, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ctx['id'],
            ctx['name'],
            ctx['description'],
            ctx['context_type'],
            json.dumps(ctx.get('affects_rights', [])),
            ctx.get('is_currently_active', False),
            json.dumps(ctx.get('active_regions', [])),
            ctx.get('decree_number'),
            ctx.get('start_date'),
            ctx.get('end_date'),
            ctx.get('source_id'),
        ))
        count += 1

    print(f"  ✓ {count} contextos insertados")


def insert_time_limits(conn, situations):
    """Inserta limites de tiempo desde las situaciones."""
    count = 0
    for sit in situations:
        for tl in sit.get('time_limits', []):
            conn.execute("""
                INSERT OR REPLACE INTO time_limits
                (id, situation_id, description, max_hours, max_hours_emergency,
                 applies_to, after_expiry_action, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tl['id'],
                sit['id'],
                tl['description'],
                tl['max_hours'],
                tl.get('max_hours_emergency'),
                tl.get('applies_to', 'todos'),
                tl['after_expiry_action'],
                tl['source_id'],
            ))
            count += 1

    if count > 0:
        print(f"  ✓ {count} límites de tiempo insertados")


def insert_myths(conn, myths):
    """Inserta mitos para la sección educativa."""
    count = 0
    for myth in myths:
        conn.execute("""
            INSERT OR REPLACE INTO myths
            (id, myth, reality, explanation, related_sources, category, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            myth['id'],
            myth['myth'],
            myth['reality'],
            myth['explanation'],
            json.dumps(myth.get('related_source_ids', [])),
            myth['category'],
            myth.get('display_order', 0)
        ))
        count += 1
    
    print(f"  ✓ {count} mitos insertados")


def build_country(country_code, validate_only=False):
    """Construye la base de datos para un país."""
    country_dir = DATA_DIR / country_code
    
    if not country_dir.exists():
        print(f"ERROR: No existe directorio para {country_code}")
        return False
    
    # Cargar metadata
    metadata = load_json(country_dir / "metadata.json")
    if metadata:
        metadata = metadata[0]
        print(f"\n{'='*50}")
        print(f"País: {metadata.get('country_name', country_code)}")
        print(f"Última verificación: {metadata.get('last_verified', 'N/A')}")
        print(f"Revisión por abogado: {'Sí' if metadata.get('completeness', {}).get('review_by_lawyer') else 'No'}")
        print(f"{'='*50}")
    
    if validate_only:
        print("\n[Modo validación — no se genera base de datos]")
    
    # Crear directorio de build
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    db_path = OUTPUT_DIR / f"truths_and_rights_{country_code.lower()}.db"
    
    if not validate_only:
        # Eliminar DB anterior
        if db_path.exists():
            db_path.unlink()
        
        conn = sqlite3.connect(str(db_path))
        load_schema(conn)
    else:
        conn = sqlite3.connect(":memory:")
        load_schema(conn)
    
    # Cargar e insertar datos
    print("\nCargando datos...")
    
    # Contexts
    contexts = load_json(country_dir / "contexts" / "contexts.json")
    insert_contexts(conn, contexts)

    # Sources (buscar todos los JSON en sources/)
    sources_dir = country_dir / "sources"
    all_sources = []
    if sources_dir.exists():
        for f in sources_dir.glob("*.json"):
            all_sources.extend(load_json(f))
    insert_sources(conn, all_sources, country_code)

    # Rights
    rights = load_json(country_dir / "rights" / "rights.json")
    insert_rights(conn, rights)

    # Actions
    actions = load_json(country_dir / "actions" / "actions.json")
    insert_actions(conn, actions)

    # Contacts
    contacts = load_json(country_dir / "contacts" / "emergency_contacts.json")
    insert_contacts(conn, contacts)

    # Situations (buscar todos los JSON en situations/)
    situations_dir = country_dir / "situations"
    all_situations = []
    if situations_dir.exists():
        for f in situations_dir.glob("*.json"):
            all_situations.extend(load_json(f))
    insert_situations(conn, all_situations)

    # Time limits (extraidos de las situaciones)
    insert_time_limits(conn, all_situations)

    # Myths
    myths = load_json(country_dir / "myths" / "myths.json")
    insert_myths(conn, myths)
    
    conn.commit()
    
    # Stats
    cursor = conn.cursor()
    tables = ['legal_sources', 'situations', 'rights', 'actions', 
              'emergency_contacts', 'myths']
    
    print(f"\n--- Resumen ---")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} registros")
        except:
            print(f"  {table}: tabla vacía")
    
    conn.close()
    
    if not validate_only:
        print(f"\n✓ Base de datos generada: {db_path}")
        print(f"  Tamaño: {db_path.stat().st_size / 1024:.1f} KB")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Build Truths and Rights database')
    parser.add_argument('--country', type=str, help='Country code (e.g., PE)')
    parser.add_argument('--validate', action='store_true', help='Validate only, do not build')
    args = parser.parse_args()
    
    print("🛡️  Truths and Rights — Database Builder")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    if args.country:
        build_country(args.country.upper(), args.validate)
    else:
        # Build all countries
        if DATA_DIR.exists():
            countries = [d.name for d in DATA_DIR.iterdir() if d.is_dir()]
            for country in sorted(countries):
                build_country(country, args.validate)
        else:
            print(f"ERROR: No existe directorio de datos: {DATA_DIR}")


if __name__ == "__main__":
    main()
