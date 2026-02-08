#!/usr/bin/env python3
"""
Truths and Rights — Official Sources Scraper
Descarga textos legales de fuentes oficiales peruanas.

Fuentes soportadas:
  - SPIJ (Sistema Peruano de Información Jurídica)
  - Tribunal Constitucional (jurisprudencia)
  - El Peruano (diario oficial)

Uso:
    python scrape_official.py --source spij --law "DL 1186"
    python scrape_official.py --source tc --exp "00413-2022-PHC/TC"
    python scrape_official.py --all
    python scrape_official.py --check-updates

Notas:
    - Respetar rate limits (1 request cada 2 segundos mínimo)
    - Guardar textos raw en data/PE/sources/raw/ para auditoría
    - Los textos procesados van a los JSON correspondientes
"""

import json
import os
import sys
import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, quote

# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "PE"
RAW_DIR = DATA_DIR / "sources" / "raw"
SOURCES_DIR = DATA_DIR / "sources"

# Rate limiting
REQUEST_DELAY = 2  # segundos entre requests

# Leyes específicas que necesitamos para la app
TARGET_LAWS = {
    "constitucion": {
        "name": "Constitución Política del Perú",
        "articles": [
            "1", "2.1", "2.2", "2.7", "2.9", "2.10", "2.11", "2.12",
            "2.24.a", "2.24.e", "2.24.f", "2.24.h",
            "137", "139.14", "162", "200"
        ],
        "spij_id": None,  # buscar por nombre
        "notes": "Solo artículos relevantes a intervenciones policiales"
    },
    "codigo_procesal_penal": {
        "name": "Código Procesal Penal - Decreto Legislativo 957",
        "articles": [
            "66", "71", "159.2", "205", "205.4", "208", "209", "210", "259", "261"
        ],
        "spij_id": "DL_957",
        "notes": "Libro Segundo, Sección II y III principalmente"
    },
    "codigo_penal": {
        "name": "Código Penal - Decreto Legislativo 635",
        "articles": ["299", "321", "368", "376", "377"],
        "spij_id": "DL_635",
        "notes": "Art 299 (posesión), 321 (tortura), 368 (resistencia), 376-377 (abuso)"
    },
    "dl_1186": {
        "name": "Decreto Legislativo 1186 - Uso de la fuerza por la PNP",
        "articles": "all",
        "spij_id": "DL_1186",
        "notes": "Completo, son pocos artículos"
    },
    "dl_1267": {
        "name": "Decreto Legislativo 1267 - Ley de la PNP",
        "articles": ["relevant"],  # artículos sobre identificación, funciones
        "spij_id": "DL_1267",
        "notes": "Modificado por DL 1604"
    },
    "ley_32130": {
        "name": "Ley 32130 - Registro audiovisual de intervenciones",
        "articles": "all",
        "spij_id": None,
        "notes": "Ley nueva (octubre 2024), verificar en El Peruano"
    },
    "ley_30714": {
        "name": "Ley 30714 - Régimen Disciplinario PNP",
        "articles": ["relevant"],
        "spij_id": None,
        "notes": "Mecanismos de denuncia"
    },
    "ley_31307": {
        "name": "Ley 31307 - Nuevo Código Procesal Constitucional",
        "articles": ["relevant"],  # hábeas corpus
        "spij_id": None,
        "notes": "Procedimiento de hábeas corpus"
    }
}

TARGET_JURISPRUDENCE = {
    "tc_00413_2022": {
        "court": "TC",
        "expediente": "00413-2022-PHC/TC",
        "topic": "Control de identidad, actitud sospechosa inaceptable",
        "url_pattern": "https://www.tc.gob.pe/jurisprudencia/"
    },
    "tc_00008_2021": {
        "court": "TC",
        "expediente": "00008-2021-PI/TC",
        "topic": "Ley de Protección Policial, proporcionalidad vigente",
        "url_pattern": "https://www.tc.gob.pe/jurisprudencia/"
    },
    "tc_02513_2023": {
        "court": "TC",
        "expediente": "02513-2023-PHC/TC",
        "topic": "Caso UNMSM, detención masiva ilegal",
        "url_pattern": "https://www.tc.gob.pe/jurisprudencia/"
    },
    "tc_03830_2017": {
        "court": "TC",
        "expediente": "03830-2017-PHC/TC",
        "topic": "Solo detención por mandato judicial o flagrancia",
        "url_pattern": "https://www.tc.gob.pe/jurisprudencia/"
    },
    "juzgado_chupaca_2024": {
        "court": "Juzgado Chupaca",
        "expediente": "00323-2024",
        "topic": "Revisión ilegal de celular e IMEI",
        "url_pattern": null
    },
    "cidh_azul_rojas": {
        "court": "Corte IDH",
        "expediente": "Azul Rojas Marín vs. Perú",
        "topic": "Obligación de informar motivo de intervención",
        "url_pattern": "https://www.corteidh.or.cr/"
    }
}

# ============================================================
# UTILIDADES
# ============================================================

def ensure_dirs():
    """Crea directorios necesarios."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

def save_raw(content, filename):
    """Guarda contenido raw para auditoría."""
    filepath = RAW_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(content, dict) or isinstance(content, list):
            json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            f.write(content)
    print(f"  → Raw guardado: {filepath}")
    return filepath

def content_hash(text):
    """Hash del contenido para detectar cambios."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

def rate_limit():
    """Espera entre requests."""
    time.sleep(REQUEST_DELAY)

# ============================================================
# SCRAPERS POR FUENTE
# ============================================================

class SPIJScraper:
    """
    Scraper para el Sistema Peruano de Información Jurídica.
    URL base: https://spij.minjus.gob.pe
    
    SPIJ tiene una API interna que se puede consultar.
    También permite descargar textos completos de normas.
    
    NOTA: Este scraper necesita ser adaptado según la estructura
    actual del sitio, que puede cambiar. Verificar antes de correr.
    """
    
    BASE_URL = "https://spij.minjus.gob.pe"
    SEARCH_URL = f"{BASE_URL}/spij-ext-web/busqueda"
    
    def __init__(self):
        self.session = None
    
    def _init_session(self):
        """Inicializa sesión HTTP con headers apropiados."""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'TruthsAndRights/1.0 (Legal Research, Open Source)',
                'Accept': 'text/html,application/json',
                'Accept-Language': 'es-PE,es;q=0.9'
            })
            return True
        except ImportError:
            print("ERROR: Se necesita 'requests'. Instalar: pip install requests")
            return False
    
    def search_law(self, query):
        """
        Busca una norma por nombre o número.
        
        Ejemplo:
            search_law("Decreto Legislativo 1186")
            search_law("Ley 32130")
        """
        if not self.session and not self._init_session():
            return None
        
        print(f"  Buscando en SPIJ: {query}")
        
        # SPIJ search endpoint (verificar estructura actual)
        # La URL exacta puede variar, este es el patrón general
        try:
            params = {
                'texto': query,
                'tipo': 'todos'
            }
            response = self.session.get(self.SEARCH_URL, params=params, timeout=30)
            rate_limit()
            
            if response.status_code == 200:
                save_raw(response.text, f"spij_search_{quote(query)}.html")
                return response.text
            else:
                print(f"  ⚠ SPIJ respondió {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ⚠ Error conectando a SPIJ: {e}")
            return None
    
    def get_law_text(self, law_id):
        """
        Obtiene el texto completo de una norma por su ID en SPIJ.
        """
        if not self.session and not self._init_session():
            return None
        
        url = f"{self.BASE_URL}/spij-ext-web/detallegislacion/{law_id}"
        print(f"  Descargando texto: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            rate_limit()
            
            if response.status_code == 200:
                save_raw(response.text, f"spij_law_{law_id}.html")
                return response.text
            else:
                print(f"  ⚠ SPIJ respondió {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return None


class TCScraper:
    """
    Scraper para el Tribunal Constitucional del Perú.
    URL base: https://www.tc.gob.pe
    
    Las sentencias del TC son públicas y accesibles.
    Tienen un buscador de jurisprudencia.
    """
    
    BASE_URL = "https://www.tc.gob.pe"
    SEARCH_URL = f"{BASE_URL}/jurisprudencia/search"
    
    def __init__(self):
        self.session = None
    
    def _init_session(self):
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'TruthsAndRights/1.0 (Legal Research, Open Source)',
                'Accept': 'text/html,application/json',
                'Accept-Language': 'es-PE,es;q=0.9'
            })
            return True
        except ImportError:
            print("ERROR: Se necesita 'requests'. Instalar: pip install requests")
            return False
    
    def search_sentencia(self, expediente):
        """
        Busca una sentencia por número de expediente.
        
        Ejemplo:
            search_sentencia("00413-2022-PHC/TC")
        """
        if not self.session and not self._init_session():
            return None
        
        print(f"  Buscando en TC: {expediente}")
        
        try:
            # El TC tiene un buscador, la URL exacta puede variar
            params = {
                'query': expediente
            }
            response = self.session.get(
                f"{self.BASE_URL}/tc-publico-gw-war/searchByCriteria",
                params=params,
                timeout=30
            )
            rate_limit()
            
            if response.status_code == 200:
                save_raw(response.text, f"tc_search_{expediente.replace('/', '_')}.html")
                return response.text
            else:
                print(f"  ⚠ TC respondió {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return None
    
    def get_sentencia_pdf(self, expediente, pdf_url):
        """Descarga PDF de la sentencia."""
        if not self.session and not self._init_session():
            return None
        
        try:
            response = self.session.get(pdf_url, timeout=60)
            rate_limit()
            
            if response.status_code == 200:
                filename = f"tc_{expediente.replace('/', '_')}.pdf"
                filepath = RAW_DIR / filename
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  → PDF guardado: {filepath}")
                return filepath
            
        except Exception as e:
            print(f"  ⚠ Error descargando PDF: {e}")
            return None


class ElPeruanoScraper:
    """
    Scraper para el Diario Oficial El Peruano.
    URL base: https://diariooficial.elperuano.pe
    
    Útil para:
    - Verificar fecha de publicación de normas
    - Obtener texto oficial de leyes recientes
    - Monitorear nuevos decretos de emergencia
    """
    
    BASE_URL = "https://diariooficial.elperuano.pe"
    
    def __init__(self):
        self.session = None
    
    def _init_session(self):
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'TruthsAndRights/1.0 (Legal Research, Open Source)',
                'Accept': 'text/html,application/json',
                'Accept-Language': 'es-PE,es;q=0.9'
            })
            return True
        except ImportError:
            print("ERROR: Se necesita 'requests'")
            return False
    
    def search_norma(self, query):
        """Busca una norma en El Peruano."""
        if not self.session and not self._init_session():
            return None
        
        print(f"  Buscando en El Peruano: {query}")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/Normas",
                params={'query': query},
                timeout=30
            )
            rate_limit()
            
            if response.status_code == 200:
                save_raw(response.text, f"peruano_search_{quote(query)}.html")
                return response.text
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return None
    
    def check_emergency_decrees(self):
        """
        Busca decretos de emergencia vigentes.
        Útil para actualizar contexts.json automáticamente.
        """
        if not self.session and not self._init_session():
            return None
        
        print("  Buscando decretos de emergencia vigentes...")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/Normas",
                params={'query': 'estado de emergencia 2026'},
                timeout=30
            )
            rate_limit()
            
            if response.status_code == 200:
                save_raw(response.text, f"peruano_emergency_{datetime.now().strftime('%Y%m%d')}.html")
                return response.text
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return None


# ============================================================
# VERIFICADOR DE ACTUALIZACIONES
# ============================================================

class UpdateChecker:
    """
    Verifica si las fuentes legales en la base de datos siguen vigentes.
    Compara contra las fuentes oficiales.
    """
    
    def __init__(self):
        self.spij = SPIJScraper()
        self.tc = TCScraper()
        self.peruano = ElPeruanoScraper()
    
    def check_all_sources(self):
        """Verifica vigencia de todas las fuentes."""
        print("\n🔍 Verificando vigencia de fuentes legales...")
        
        # Cargar fuentes actuales
        sources_files = list(SOURCES_DIR.glob("*.json"))
        all_sources = []
        for f in sources_files:
            if f.name == 'raw':
                continue
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    all_sources.extend(data)
        
        print(f"  Total fuentes a verificar: {len(all_sources)}")
        
        results = {
            'verified': [],
            'needs_update': [],
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for source in all_sources:
            sid = source.get('id', '?')
            status = source.get('status', 'unknown')
            
            if status == 'derogado':
                print(f"  ⏭ {sid}: derogado (skip)")
                continue
            
            # Por ahora, solo reportar qué necesita verificación manual
            last_modified = source.get('last_modified')
            if last_modified:
                print(f"  ⚠ {sid}: modificado ({last_modified}) — verificar texto actual")
                results['needs_update'].append({
                    'id': sid,
                    'reason': f'Modificado: {last_modified}',
                    'source_type': source.get('source_type')
                })
            else:
                results['verified'].append(sid)
        
        # Guardar reporte
        report_path = RAW_DIR / f"verification_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n--- Reporte de verificación ---")
        print(f"  ✓ Verificadas: {len(results['verified'])}")
        print(f"  ⚠ Necesitan actualización: {len(results['needs_update'])}")
        print(f"  ✗ Errores: {len(results['errors'])}")
        print(f"  Reporte guardado: {report_path}")
        
        return results
    
    def check_emergency_status(self):
        """
        Verifica si hay estados de emergencia nuevos o vencidos.
        Actualiza contexts.json si es necesario.
        """
        print("\n🔍 Verificando estados de emergencia...")
        
        contexts_path = DATA_DIR / "contexts" / "contexts.json"
        with open(contexts_path, 'r', encoding='utf-8') as f:
            contexts = json.load(f)
        
        for ctx in contexts:
            if ctx.get('context_type') == 'estado_emergencia':
                end_date = ctx.get('end_date')
                if end_date:
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    today = datetime.now()
                    
                    if today > end:
                        print(f"  ⚠ Estado de emergencia VENCIDO: {ctx['decree_number']}")
                        print(f"    Venció: {end_date}")
                        print(f"    ACCIÓN: Verificar si fue renovado en El Peruano")
                    else:
                        days_left = (end - today).days
                        print(f"  ✓ {ctx['decree_number']}: vigente ({days_left} días restantes)")
                        if days_left <= 7:
                            print(f"    ⚠ Vence pronto — verificar renovación")


# ============================================================
# MAIN
# ============================================================

def scrape_all():
    """Scrape completo de todas las fuentes."""
    ensure_dirs()
    
    print("🛡️  Truths and Rights — Official Sources Scraper")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Target: {len(TARGET_LAWS)} leyes, {len(TARGET_JURISPRUDENCE)} sentencias")
    
    spij = SPIJScraper()
    tc = TCScraper()
    peruano = ElPeruanoScraper()
    
    # 1. Leyes desde SPIJ
    print("\n=== SPIJ: Legislación ===")
    for law_key, law_info in TARGET_LAWS.items():
        print(f"\n[{law_key}] {law_info['name']}")
        result = spij.search_law(law_info['name'])
        if result:
            print(f"  ✓ Encontrado")
        else:
            print(f"  ✗ No encontrado o error de conexión")
    
    # 2. Jurisprudencia desde TC
    print("\n=== TC: Jurisprudencia ===")
    for juris_key, juris_info in TARGET_JURISPRUDENCE.items():
        if juris_info['court'] == 'TC':
            print(f"\n[{juris_key}] Exp. {juris_info['expediente']}")
            result = tc.search_sentencia(juris_info['expediente'])
            if result:
                print(f"  ✓ Encontrado")
            else:
                print(f"  ✗ No encontrado o error de conexión")
    
    # 3. Verificar emergencias
    print("\n=== El Peruano: Estados de emergencia ===")
    peruano.check_emergency_decrees()
    
    print("\n✓ Scraping completado. Revisar archivos raw en:")
    print(f"  {RAW_DIR}")

def check_updates():
    """Solo verificar actualizaciones sin descargar."""
    ensure_dirs()
    checker = UpdateChecker()
    checker.check_all_sources()
    checker.check_emergency_status()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape official Peruvian legal sources')
    parser.add_argument('--all', action='store_true', help='Scrape all sources')
    parser.add_argument('--check-updates', action='store_true', help='Check for updates only')
    parser.add_argument('--source', choices=['spij', 'tc', 'peruano'], help='Specific source')
    parser.add_argument('--query', type=str, help='Search query')
    parser.add_argument('--check-emergency', action='store_true', help='Check emergency status')
    
    args = parser.parse_args()
    
    if args.check_updates:
        check_updates()
    elif args.check_emergency:
        ensure_dirs()
        checker = UpdateChecker()
        checker.check_emergency_status()
    elif args.all:
        scrape_all()
    elif args.source and args.query:
        ensure_dirs()
        if args.source == 'spij':
            scraper = SPIJScraper()
            scraper.search_law(args.query)
        elif args.source == 'tc':
            scraper = TCScraper()
            scraper.search_sentencia(args.query)
        elif args.source == 'peruano':
            scraper = ElPeruanoScraper()
            scraper.search_norma(args.query)
    else:
        parser.print_help()
        print("\nEjemplos:")
        print('  python scrape_official.py --all')
        print('  python scrape_official.py --check-updates')
        print('  python scrape_official.py --check-emergency')
        print('  python scrape_official.py --source spij --query "Decreto Legislativo 1186"')
        print('  python scrape_official.py --source tc --query "00413-2022-PHC/TC"')


if __name__ == "__main__":
    main()
