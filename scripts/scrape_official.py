#!/usr/bin/env python3
"""
Truths and Rights — Official Sources Scraper
Descarga textos legales de fuentes oficiales peruanas para verificacion.

Fuentes soportadas:
  - TC (Tribunal Constitucional) — sentencias en HTML/PDF
  - El Peruano (diario oficial) — normas por fecha
  - Congreso (Archivo Digital) — legislacion por numero

Uso:
    python scrape_official.py --all
    python scrape_official.py --check-updates
    python scrape_official.py --check-emergency
    python scrape_official.py --source tc --query "00413-2022-PHC/TC"
    python scrape_official.py --source peruano --query "estado de emergencia"
    python scrape_official.py --source congreso --query "Decreto Legislativo 1186"

Notas:
    - Respetar rate limits (2 segundos entre requests minimo)
    - Guardar textos raw en data/PE/sources/raw/ para auditoria
    - NO modifica los JSON de datos existentes
"""

import io
import json
import os
import sys
import time
import re
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, quote

# Fix encoding on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Se necesitan 'requests' y 'beautifulsoup4'.")
    print("Instalar: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# ============================================================
# CONFIGURACION
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "PE"
RAW_DIR = DATA_DIR / "sources" / "raw"
SOURCES_DIR = DATA_DIR / "sources"

REQUEST_DELAY = 2  # segundos entre requests

# Leyes que necesitamos verificar
TARGET_LAWS = {
    "constitucion": {
        "name": "Constitucion Politica del Peru",
        "articles": [
            "1", "2.1", "2.7", "2.9", "2.10", "2.24.e", "2.24.f", "2.24.h",
            "137", "139.14", "162", "200"
        ],
    },
    "dl_957": {
        "name": "Decreto Legislativo 957 - Codigo Procesal Penal",
        "articles": ["71", "159", "205", "208", "209", "210", "259", "261"],
    },
    "dl_635": {
        "name": "Decreto Legislativo 635 - Codigo Penal",
        "articles": ["299", "321", "368", "376", "377"],
    },
    "dl_1186": {
        "name": "Decreto Legislativo 1186 - Uso de la fuerza por la PNP",
        "articles": "all",
    },
    "dl_1267": {
        "name": "Decreto Legislativo 1267 - Ley de la PNP",
        "articles": ["relevant"],
    },
    "ley_32130": {
        "name": "Ley 32130 - Registro audiovisual de intervenciones",
        "articles": "all",
    },
    "ley_31307": {
        "name": "Ley 31307 - Nuevo Codigo Procesal Constitucional",
        "articles": ["relevant"],
    },
}

TARGET_JURISPRUDENCE = {
    "tc_00413_2022": {
        "court": "TC",
        "expediente": "00413-2022-PHC/TC",
        "topic": "Control de identidad, actitud sospechosa inaceptable",
        "number": "00413",
        "year": "2022",
        "type": "PHC",
    },
    "tc_00008_2021": {
        "court": "TC",
        "expediente": "00008-2021-PI/TC",
        "topic": "Ley de Proteccion Policial, proporcionalidad",
        "number": "00008",
        "year": "2021",
        "type": "PI",
    },
    "tc_02513_2023": {
        "court": "TC",
        "expediente": "02513-2023-PHC/TC",
        "topic": "Caso UNMSM, detencion masiva ilegal",
        "number": "02513",
        "year": "2023",
        "type": "PHC",
    },
    "tc_03830_2017": {
        "court": "TC",
        "expediente": "03830-2017-PHC/TC",
        "topic": "Solo detencion por mandato judicial o flagrancia",
        "number": "03830",
        "year": "2017",
        "type": "PHC",
    },
}

# ============================================================
# UTILIDADES
# ============================================================

def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_raw(content, filename):
    filepath = RAW_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            f.write(content)
    print(f"    Guardado: {filepath.name}")
    return filepath


def save_raw_binary(content, filename):
    filepath = RAW_DIR / filename
    with open(filepath, 'wb') as f:
        f.write(content)
    print(f"    Guardado: {filepath.name} ({len(content)} bytes)")
    return filepath


def content_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def rate_limit():
    time.sleep(REQUEST_DELAY)


def make_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'TruthsAndRights/1.0 (Legal Research, Open Source, https://github.com/ELLokoAkrata/truths-and-rights)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-PE,es;q=0.9,en;q=0.5',
    })
    return session


# ============================================================
# SCRAPER: TRIBUNAL CONSTITUCIONAL
# ============================================================

class TCScraper:
    """
    Scraper para el Tribunal Constitucional del Peru.
    Busca sentencias por expediente y descarga HTML/PDF.

    Endpoints:
      - Busqueda: GET /consultas-de-causas/?bus=tc&action=search&n_exp={num}&a_exp={year}
      - Texto: /jurisprudencia/{year}/{case_id}.html
      - PDF:   /jurisprudencia/{year}/{case_id}.pdf
    """

    BASE_URL = "https://www.tc.gob.pe"

    def __init__(self, session=None):
        self.session = session or make_session()

    def search(self, expediente):
        """
        Busca sentencia por expediente.
        Ej: search("00413-2022-PHC/TC")
        """
        # Parsear expediente: "00413-2022-PHC/TC" -> n_exp=00413, a_exp=2022
        parts = expediente.replace('/TC', '').split('-')
        if len(parts) >= 2:
            n_exp = parts[0]
            a_exp = parts[1]
        else:
            n_exp = expediente
            a_exp = ''

        print(f"  Buscando en TC: Exp. {expediente}")

        url = f"{self.BASE_URL}/consultas-de-causas/"
        params = {
            'bus': 'tc',
            'action': 'search',
            'n_exp': n_exp,
            'a_exp': a_exp,
        }

        try:
            resp = self.session.get(url, params=params, timeout=30)
            rate_limit()

            if resp.status_code != 200:
                print(f"    TC respondio {resp.status_code}")
                return None

            safe_name = expediente.replace('/', '_')
            save_raw(resp.text, f"tc_search_{safe_name}.html")

            # Parsear resultados
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = self._parse_search_results(soup)

            if results:
                print(f"    Encontrado: {len(results)} resultado(s)")
                save_raw(results, f"tc_results_{safe_name}.json")
            else:
                print(f"    Sin resultados en la pagina de busqueda")

            return results

        except requests.RequestException as e:
            print(f"    Error de conexion: {e}")
            return None

    def _parse_search_results(self, soup):
        """Extrae datos de la tabla de resultados."""
        results = []
        table = soup.find('table')
        if not table:
            return results

        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 3:
                link = row.find('a', href=True)
                result = {
                    'expediente': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                    'detalle_url': link['href'] if link else '',
                }
                results.append(result)

        return results

    def download_sentencia(self, case_id, year):
        """
        Descarga el texto HTML de una sentencia.
        Ej: download_sentencia("00413-2022-AA", "2022")
        """
        # Intentar con diferentes formatos de URL
        patterns = [
            f"{self.BASE_URL}/jurisprudencia/{year}/{case_id}.html",
            f"{self.BASE_URL}/jurisprudencia/{year}/{case_id.lower()}.html",
        ]

        for url in patterns:
            try:
                print(f"    Intentando: {url}")
                resp = self.session.get(url, timeout=30)
                rate_limit()

                if resp.status_code == 200 and len(resp.text) > 500:
                    safe = case_id.replace('/', '_')
                    save_raw(resp.text, f"tc_sentencia_{safe}.html")
                    print(f"    Sentencia descargada ({len(resp.text)} chars)")
                    return resp.text

            except requests.RequestException as e:
                print(f"    Error: {e}")
                continue

        print(f"    No se pudo descargar la sentencia")
        return None

    def download_pdf(self, case_id, year):
        """Descarga PDF de una sentencia."""
        url = f"{self.BASE_URL}/jurisprudencia/{year}/{case_id}.pdf"

        try:
            print(f"    Descargando PDF: {url}")
            resp = self.session.get(url, timeout=60)
            rate_limit()

            if resp.status_code == 200 and len(resp.content) > 1000:
                safe = case_id.replace('/', '_')
                save_raw_binary(resp.content, f"tc_{safe}.pdf")
                return True

        except requests.RequestException as e:
            print(f"    Error descargando PDF: {e}")

        return False

    def scrape_target_jurisprudence(self):
        """Descarga todas las sentencias objetivo."""
        print("\n=== Tribunal Constitucional: Jurisprudencia ===")
        results = {}

        for key, info in TARGET_JURISPRUDENCE.items():
            if info['court'] != 'TC':
                continue

            print(f"\n  [{key}] {info['topic']}")
            exp = info['expediente']

            # Buscar
            search_results = self.search(exp)

            # Intentar descargar el texto
            # El case_id tipicamente es: {number}-{year}-{type}
            case_id = f"{info['number']}-{info['year']}-{info['type']}"
            html = self.download_sentencia(case_id, info['year'])

            results[key] = {
                'expediente': exp,
                'found_in_search': bool(search_results),
                'html_downloaded': bool(html),
                'html_hash': content_hash(html) if html else None,
                'timestamp': datetime.now().isoformat(),
            }

        return results


# ============================================================
# SCRAPER: EL PERUANO (Diario Oficial)
# ============================================================

class ElPeruanoScraper:
    """
    Scraper para el Diario Oficial El Peruano.
    Busca normas por fecha y decreto de emergencia vigentes.

    Endpoints:
      - Normas por fecha: GET /Normas (con rango de fechas)
      - Cuadernillo diario: GET busquedas.elperuano.pe/cuadernillo/NL/{YYYYMMDD}
    """

    BASE_URL = "https://diariooficial.elperuano.pe"
    BUSQUEDAS_URL = "https://busquedas.elperuano.pe"

    def __init__(self, session=None):
        self.session = session or make_session()

    def search_norma(self, query):
        """Busca normas en El Peruano."""
        print(f"  Buscando en El Peruano: {query}")

        try:
            resp = self.session.get(
                f"{self.BASE_URL}/Normas",
                params={'query': query},
                timeout=30,
            )
            rate_limit()

            if resp.status_code == 200:
                save_raw(resp.text, f"peruano_search_{quote(query, safe='')}.html")
                print(f"    Pagina obtenida ({len(resp.text)} chars)")
                return resp.text

        except requests.RequestException as e:
            print(f"    Error: {e}")

        return None

    def get_daily_norms(self, date_str):
        """
        Obtiene normas publicadas en una fecha especifica.
        date_str: formato YYYYMMDD
        """
        url = f"{self.BUSQUEDAS_URL}/cuadernillo/NL/{date_str}"
        print(f"  Obteniendo normas del {date_str}")

        try:
            resp = self.session.get(url, timeout=30)
            rate_limit()

            if resp.status_code == 200:
                save_raw(resp.text, f"peruano_normas_{date_str}.html")

                soup = BeautifulSoup(resp.text, 'html.parser')
                norms = self._parse_daily_norms(soup)

                if norms:
                    print(f"    {len(norms)} norma(s) encontrada(s)")
                    save_raw(norms, f"peruano_normas_{date_str}.json")

                return norms

        except requests.RequestException as e:
            print(f"    Error: {e}")

        return None

    def _parse_daily_norms(self, soup):
        """Extrae normas de la pagina del cuadernillo."""
        norms = []
        articles = soup.find_all(['article', 'div'], class_=re.compile(r'norma|item|result'))
        for art in articles:
            title = art.find(['h2', 'h3', 'h4', 'a'])
            if title:
                norms.append({
                    'title': title.get_text(strip=True),
                    'link': title.get('href', ''),
                })
        return norms

    def check_emergency_decrees(self):
        """Busca decretos de emergencia recientes."""
        print("\n=== El Peruano: Decretos de Emergencia ===")

        result = self.search_norma("decreto supremo estado de emergencia 2026")
        if result:
            soup = BeautifulSoup(result, 'html.parser')
            # Buscar menciones a decretos de emergencia
            text = soup.get_text()
            emergency_mentions = re.findall(
                r'D\.?S\.?\s*N?[°o]?\s*\d{3}-\d{4}-PCM',
                text
            )
            if emergency_mentions:
                print(f"    Decretos mencionados: {set(emergency_mentions)}")
            else:
                print(f"    No se encontraron decretos en la pagina")

        return result


# ============================================================
# SCRAPER: CONGRESO (Archivo Digital de Legislacion)
# ============================================================

class CongresoScraper:
    """
    Scraper para el Archivo Digital de Legislacion del Peru.
    Alternativa a SPIJ para obtener textos de leyes.

    URL: https://leyes.congreso.gob.pe
    """

    BASE_URL = "https://leyes.congreso.gob.pe"

    def __init__(self, session=None):
        self.session = session or make_session()

    def search_law(self, query):
        """
        Busca legislacion en el archivo del Congreso.
        Ej: search_law("Decreto Legislativo 1186")
        """
        print(f"  Buscando en Congreso: {query}")

        try:
            # Intentar la pagina principal del buscador
            resp = self.session.get(
                f"{self.BASE_URL}/LeyNumePP.aspx",
                params={'xNorma': '0'},
                timeout=30,
            )
            rate_limit()

            if resp.status_code == 200:
                save_raw(resp.text, f"congreso_search_{quote(query, safe='')}.html")
                print(f"    Pagina del buscador obtenida ({len(resp.text)} chars)")

                # Intentar buscar por texto
                soup = BeautifulSoup(resp.text, 'html.parser')
                form_data = self._extract_form_data(soup, query)
                if form_data:
                    return self._submit_search(form_data)

                return resp.text

        except requests.RequestException as e:
            print(f"    Error: {e}")

        return None

    def _extract_form_data(self, soup, query):
        """Extrae datos del formulario ASP.NET para hacer la busqueda."""
        form = soup.find('form')
        if not form:
            return None

        data = {}
        # Extraer campos ocultos de ASP.NET
        for inp in form.find_all('input', type='hidden'):
            name = inp.get('name', '')
            value = inp.get('value', '')
            if name:
                data[name] = value

        # Agregar el query al campo de titulo
        title_field = soup.find('input', {'id': re.compile(r'txtTitulo|txt_titulo', re.I)})
        if title_field:
            data[title_field['name']] = query

        return data if len(data) > 2 else None

    def _submit_search(self, form_data):
        """Envia el formulario de busqueda."""
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/LeyNumePP.aspx?xNorma=0",
                data=form_data,
                timeout=30,
            )
            rate_limit()

            if resp.status_code == 200:
                save_raw(resp.text, "congreso_results.html")
                print(f"    Resultados obtenidos ({len(resp.text)} chars)")
                return resp.text

        except requests.RequestException as e:
            print(f"    Error en busqueda: {e}")

        return None


# ============================================================
# VERIFICADOR DE ACTUALIZACIONES
# ============================================================

class UpdateChecker:
    """Verifica si las fuentes legales siguen vigentes."""

    def check_all_sources(self):
        """Verifica vigencia de todas las fuentes."""
        print("\nVerificando vigencia de fuentes legales...")

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
            'timestamp': datetime.now().isoformat(),
        }

        for source in all_sources:
            sid = source.get('id', '?')
            status = source.get('status', 'unknown')

            if status == 'derogado':
                continue

            last_modified = source.get('last_modified')
            if last_modified:
                print(f"  ! {sid}: modificado ({last_modified}) - verificar")
                results['needs_update'].append({
                    'id': sid,
                    'reason': f'Modificado: {last_modified}',
                    'source_type': source.get('source_type'),
                })
            else:
                results['verified'].append(sid)

        report_path = RAW_DIR / f"verification_report_{datetime.now().strftime('%Y%m%d')}.json"
        ensure_dirs()
        save_raw(results, report_path.name)

        print(f"\n  Verificadas: {len(results['verified'])}")
        print(f"  Necesitan revision: {len(results['needs_update'])}")
        print(f"  Errores: {len(results['errors'])}")

        return results

    def check_emergency_status(self):
        """Verifica si hay estados de emergencia vencidos o por vencer."""
        print("\nVerificando estados de emergencia...")

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
                        print(f"  VENCIDO: {ctx['decree_number']}")
                        print(f"    Vencio: {end_date}")
                        print(f"    ACCION: Verificar si fue renovado en El Peruano")
                    else:
                        days_left = (end - today).days
                        print(f"  Vigente: {ctx['decree_number']} ({days_left} dias restantes)")
                        if days_left <= 7:
                            print(f"    Vence pronto - verificar renovacion")


# ============================================================
# ORQUESTADOR
# ============================================================

def scrape_all():
    """Scrape completo de todas las fuentes accesibles."""
    ensure_dirs()
    session = make_session()

    print("Truths and Rights - Official Sources Scraper")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {len(TARGET_LAWS)} leyes, {len(TARGET_JURISPRUDENCE)} sentencias")

    # 1. Tribunal Constitucional (mas accesible)
    tc = TCScraper(session)
    tc_results = tc.scrape_target_jurisprudence()

    # 2. El Peruano (decretos de emergencia)
    peruano = ElPeruanoScraper(session)
    peruano.check_emergency_decrees()

    # 3. Congreso (leyes)
    print("\n=== Congreso: Legislacion ===")
    congreso = CongresoScraper(session)
    for law_key, law_info in TARGET_LAWS.items():
        print(f"\n  [{law_key}] {law_info['name']}")
        congreso.search_law(law_info['name'])

    # Resumen
    print("\n" + "=" * 50)
    print("Scraping completado. Archivos raw en:")
    print(f"  {RAW_DIR}")

    raw_files = list(RAW_DIR.glob("*"))
    print(f"  Total archivos descargados: {len(raw_files)}")

    # Guardar resumen
    summary = {
        'timestamp': datetime.now().isoformat(),
        'tc_results': tc_results,
        'raw_files': [f.name for f in raw_files],
    }
    save_raw(summary, f"scrape_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json")


def check_updates():
    """Verificar actualizaciones sin descargar."""
    ensure_dirs()
    checker = UpdateChecker()
    checker.check_all_sources()
    checker.check_emergency_status()


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Scraper de fuentes legales oficiales peruanas'
    )
    parser.add_argument('--all', action='store_true',
                        help='Scrape completo de todas las fuentes')
    parser.add_argument('--check-updates', action='store_true',
                        help='Verificar vigencia de fuentes (sin descargar)')
    parser.add_argument('--check-emergency', action='store_true',
                        help='Verificar estados de emergencia')
    parser.add_argument('--source', choices=['tc', 'peruano', 'congreso'],
                        help='Fuente especifica')
    parser.add_argument('--query', type=str,
                        help='Consulta de busqueda')

    args = parser.parse_args()

    if args.check_updates:
        check_updates()
    elif args.check_emergency:
        ensure_dirs()
        UpdateChecker().check_emergency_status()
    elif args.all:
        scrape_all()
    elif args.source and args.query:
        ensure_dirs()
        session = make_session()
        if args.source == 'tc':
            tc = TCScraper(session)
            tc.search(args.query)
        elif args.source == 'peruano':
            ep = ElPeruanoScraper(session)
            ep.search_norma(args.query)
        elif args.source == 'congreso':
            cs = CongresoScraper(session)
            cs.search_law(args.query)
    else:
        parser.print_help()
        print("\nEjemplos:")
        print('  python scrape_official.py --all')
        print('  python scrape_official.py --check-updates')
        print('  python scrape_official.py --check-emergency')
        print('  python scrape_official.py --source tc --query "00413-2022-PHC/TC"')
        print('  python scrape_official.py --source congreso --query "Decreto Legislativo 1186"')


if __name__ == "__main__":
    main()
