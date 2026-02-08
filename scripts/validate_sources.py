#!/usr/bin/env python3
"""
Truths and Rights — Data Validator
Verifica integridad y consistencia de todos los datos legales.

Uso:
    python validate_sources.py              # Validar todo
    python validate_sources.py --country PE # Solo Perú
    python validate_sources.py --fix        # Intentar corregir errores menores

Verifica:
  - Todos los archivos JSON son válidos
  - Todos los IDs referenciados existen
  - Campos obligatorios están presentes
  - No hay IDs duplicados
  - Las fuentes citadas en rights/situations existen en sources
  - Los contactos citados existen
  - Build funciona sin errores
"""

import json
import sys
import io
from pathlib import Path
from collections import Counter

# Fix encoding on Windows consoles (cp1252 can't handle emojis)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# ============================================================
# VALIDADORES
# ============================================================

class Validator:
    def __init__(self, country_code):
        self.country = country_code
        self.country_dir = DATA_DIR / country_code
        self.errors = []
        self.warnings = []
        self.stats = Counter()
        
        # Registros de IDs para cross-reference
        self.source_ids = set()
        self.right_ids = set()
        self.action_ids = set()
        self.situation_ids = set()
        self.contact_ids = set()
        self.context_ids = set()
    
    def error(self, msg):
        self.errors.append(msg)
        print(f"  ✗ ERROR: {msg}")
    
    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  ⚠ WARN: {msg}")
    
    def ok(self, msg):
        print(f"  ✓ {msg}")
    
    def load_json(self, filepath):
        """Carga JSON con manejo de errores."""
        if not filepath.exists():
            self.warn(f"Archivo no encontrado: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.stats['files_loaded'] += 1
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            self.error(f"JSON inválido en {filepath}: {e}")
            return []
    
    def load_all_from_dir(self, dirname):
        """Carga todos los JSON de un directorio."""
        dirpath = self.country_dir / dirname
        all_data = []
        if dirpath.exists():
            for f in sorted(dirpath.glob("*.json")):
                if f.name == 'raw':
                    continue
                all_data.extend(self.load_json(f))
        return all_data
    
    # --- Validadores específicos ---
    
    def validate_sources(self):
        """Valida fuentes legales."""
        print("\n📚 Validando fuentes legales...")
        sources = self.load_all_from_dir("sources")
        
        required = ['id', 'source_type', 'name', 'full_text', 'summary', 'status']
        valid_types = ['constitucion', 'codigo_penal', 'codigo_procesal',
                       'decreto_legislativo', 'ley', 'jurisprudencia', 'tratado_internacional']
        valid_status = ['vigente', 'modificado', 'derogado', 'parcialmente_inconstitucional']
        
        for s in sources:
            sid = s.get('id', '???')
            self.stats['sources'] += 1
            
            # Campos obligatorios
            for field in required:
                if not s.get(field):
                    self.error(f"Fuente '{sid}': falta campo '{field}'")
            
            # Tipo válido
            if s.get('source_type') and s['source_type'] not in valid_types:
                self.error(f"Fuente '{sid}': source_type inválido: {s['source_type']}")
            
            # Status válido
            if s.get('status') and s['status'] not in valid_status:
                self.error(f"Fuente '{sid}': status inválido: {s['status']}")
            
            # ID duplicado
            if sid in self.source_ids:
                self.error(f"Fuente '{sid}': ID DUPLICADO")
            self.source_ids.add(sid)
        
        self.ok(f"{len(sources)} fuentes validadas")
    
    def validate_rights(self):
        """Valida derechos."""
        print("\n⚖️ Validando derechos...")
        rights = self.load_json(self.country_dir / "rights" / "rights.json")
        
        required = ['id', 'title', 'description', 'legal_basis', 'category']
        valid_categories = ['libertad', 'integridad', 'comunicaciones',
                           'propiedad', 'debido_proceso', 'dignidad']
        
        for r in rights:
            rid = r.get('id', '???')
            self.stats['rights'] += 1
            
            for field in required:
                if not r.get(field):
                    self.error(f"Derecho '{rid}': falta campo '{field}'")
            
            if r.get('category') and r['category'] not in valid_categories:
                self.error(f"Derecho '{rid}': categoría inválida: {r['category']}")
            
            # Verificar que source_ids referencian fuentes existentes
            for src_id in r.get('source_ids', []):
                if src_id not in self.source_ids:
                    self.error(f"Derecho '{rid}': referencia fuente inexistente: {src_id}")
            
            if rid in self.right_ids:
                self.error(f"Derecho '{rid}': ID DUPLICADO")
            self.right_ids.add(rid)
        
        self.ok(f"{len(rights)} derechos validados")
    
    def validate_actions(self):
        """Valida acciones."""
        print("\n🎬 Validando acciones...")
        actions = self.load_json(self.country_dir / "actions" / "actions.json")
        
        required = ['id', 'action_type', 'title', 'description']
        valid_types = ['decir', 'hacer', 'no_hacer', 'grabar', 'llamar', 'documentar']
        
        for a in actions:
            aid = a.get('id', '???')
            self.stats['actions'] += 1
            
            for field in required:
                if not a.get(field):
                    self.error(f"Acción '{aid}': falta campo '{field}'")
            
            if a.get('action_type') and a['action_type'] not in valid_types:
                self.error(f"Acción '{aid}': action_type inválido: {a['action_type']}")
            
            if aid in self.action_ids:
                self.error(f"Acción '{aid}': ID DUPLICADO")
            self.action_ids.add(aid)
        
        self.ok(f"{len(actions)} acciones validadas")
    
    def validate_contacts(self):
        """Valida contactos."""
        print("\n📞 Validando contactos...")
        contacts = self.load_json(self.country_dir / "contacts" / "emergency_contacts.json")
        
        required = ['id', 'institution', 'description', 'contact_type']
        
        for c in contacts:
            cid = c.get('id', '???')
            self.stats['contacts'] += 1
            
            for field in required:
                if not c.get(field):
                    self.error(f"Contacto '{cid}': falta campo '{field}'")
            
            # Al menos un medio de contacto
            has_contact = any(c.get(f) for f in ['phone', 'whatsapp', 'email', 'website'])
            if not has_contact:
                self.warn(f"Contacto '{cid}': sin medio de contacto (teléfono, web, etc.)")
            
            if cid in self.contact_ids:
                self.error(f"Contacto '{cid}': ID DUPLICADO")
            self.contact_ids.add(cid)
        
        self.ok(f"{len(contacts)} contactos validados")
    
    def validate_contexts(self):
        """Valida contextos."""
        print("\n🌐 Validando contextos...")
        contexts = self.load_json(self.country_dir / "contexts" / "contexts.json")
        
        for ctx in contexts:
            cid = ctx.get('id', '???')
            self.stats['contexts'] += 1
            self.context_ids.add(cid)
        
        if 'normal' not in self.context_ids:
            self.error("Falta contexto 'normal' (obligatorio)")
        
        self.ok(f"{len(contexts)} contextos validados")
    
    def validate_situations(self):
        """Valida situaciones y sus referencias cruzadas."""
        print("\n🔍 Validando situaciones...")
        situations = self.load_all_from_dir("situations")
        
        required = ['id', 'category', 'title', 'description', 'keywords', 'natural_queries']
        
        for s in situations:
            sid = s.get('id', '???')
            self.stats['situations'] += 1
            
            for field in required:
                if not s.get(field):
                    self.error(f"Situación '{sid}': falta campo '{field}'")
            
            # Verificar que los derechos referenciados existen
            for right_rel in s.get('rights', []):
                rid = right_rel.get('right_id')
                if rid and rid not in self.right_ids:
                    self.error(f"Situación '{sid}': referencia derecho inexistente: {rid}")
                
                ctx = right_rel.get('context', 'normal')
                if ctx not in self.context_ids:
                    self.error(f"Situación '{sid}': referencia contexto inexistente: {ctx}")
            
            # Verificar que las acciones referenciadas existen
            for action_rel in s.get('actions', []):
                aid = action_rel.get('action_id')
                if aid and aid not in self.action_ids:
                    self.error(f"Situación '{sid}': referencia acción inexistente: {aid}")
            
            # Verificar que los contactos referenciados existen
            for cid in s.get('contacts', []):
                if cid not in self.contact_ids:
                    self.error(f"Situación '{sid}': referencia contacto inexistente: {cid}")
            
            # Verificar parent_situation_id
            parent = s.get('parent_situation_id')
            if parent and parent not in self.situation_ids and parent != sid:
                self.warn(f"Situación '{sid}': parent '{parent}' podría no existir aún")
            
            if sid in self.situation_ids:
                self.error(f"Situación '{sid}': ID DUPLICADO")
            self.situation_ids.add(sid)
        
        self.ok(f"{len(situations)} situaciones validadas")
    
    def validate_myths(self):
        """Valida mitos."""
        print("\n💡 Validando mitos...")
        myths = self.load_json(self.country_dir / "myths" / "myths.json")
        
        for m in myths:
            mid = m.get('id', '???')
            self.stats['myths'] += 1
            
            for field in ['id', 'myth', 'reality', 'explanation', 'category']:
                if not m.get(field):
                    self.error(f"Mito '{mid}': falta campo '{field}'")
            
            for src_id in m.get('related_source_ids', []):
                if src_id not in self.source_ids:
                    self.warn(f"Mito '{mid}': referencia fuente inexistente: {src_id}")
        
        self.ok(f"{len(myths)} mitos validados")
    
    def validate_build(self):
        """Intenta construir la base de datos."""
        print("\n🔨 Validando build...")
        
        build_script = PROJECT_ROOT / "scripts" / "build_db.py"
        if not build_script.exists():
            self.error("build_db.py no encontrado")
            return
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(build_script), '--country', self.country, '--validate'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            self.ok("Build exitoso")
        else:
            self.error(f"Build falló: {result.stderr}")
    
    # --- Ejecución ---
    
    def run(self):
        """Ejecuta todas las validaciones."""
        print(f"\n{'='*50}")
        print(f"🛡️  Validando datos para: {self.country}")
        print(f"{'='*50}")
        
        if not self.country_dir.exists():
            self.error(f"Directorio no existe: {self.country_dir}")
            return self.report()
        
        # Orden importa: sources primero porque otros dependen de ellos
        self.validate_contexts()
        self.validate_sources()
        self.validate_rights()
        self.validate_actions()
        self.validate_contacts()
        self.validate_situations()
        self.validate_myths()
        self.validate_build()
        
        return self.report()
    
    def report(self):
        """Imprime reporte final."""
        print(f"\n{'='*50}")
        print(f"📊 REPORTE DE VALIDACIÓN — {self.country}")
        print(f"{'='*50}")
        
        print(f"\nRegistros:")
        for key, count in sorted(self.stats.items()):
            print(f"  {key}: {count}")
        
        print(f"\n✗ Errores: {len(self.errors)}")
        print(f"⚠ Advertencias: {len(self.warnings)}")
        
        if not self.errors and not self.warnings:
            print("\n✓ ¡Todos los datos son válidos!")
        elif not self.errors:
            print("\n✓ Sin errores críticos (hay advertencias)")
        else:
            print("\n✗ HAY ERRORES — corregir antes de build")
        
        return len(self.errors) == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Truths and Rights data')
    parser.add_argument('--country', type=str, default=None, help='Country code')
    args = parser.parse_args()
    
    if args.country:
        countries = [args.country.upper()]
    else:
        countries = [d.name for d in DATA_DIR.iterdir() if d.is_dir()]
    
    all_ok = True
    for country in sorted(countries):
        validator = Validator(country)
        if not validator.run():
            all_ok = False
    
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
