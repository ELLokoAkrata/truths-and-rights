#!/usr/bin/env python3
"""
Truths and Rights — Static Site Generator

Lee los JSON de data/PE/ y genera un portal publico HTML en site/.
Python puro con string templates (sin Jinja2, sin dependencias extra).

Uso:
    python scripts/generate_site.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "PE"
SITE_DIR = PROJECT_ROOT / "site"
HISTORY_FILE = DATA_DIR / "verification_history.jsonl"

# ============================================================
# DATA LOADING
# ============================================================

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_data():
    """Carga todos los JSON del proyecto."""
    data = {}
    data['metadata'] = load_json(DATA_DIR / "metadata.json")
    data['contexts'] = load_json(DATA_DIR / "contexts" / "contexts.json")
    data['rights'] = load_json(DATA_DIR / "rights" / "rights.json")
    data['contacts'] = load_json(DATA_DIR / "contacts" / "emergency_contacts.json")
    data['myths'] = load_json(DATA_DIR / "myths" / "myths.json")
    data['actions'] = load_json(DATA_DIR / "actions" / "actions.json")

    # Situaciones (multiples archivos)
    data['situations'] = []
    sit_dir = DATA_DIR / "situations"
    for f in sorted(sit_dir.glob("*.json")):
        sits = load_json(f)
        if isinstance(sits, list):
            data['situations'].extend(sits)
        else:
            data['situations'].append(sits)

    # Fuentes legales (multiples archivos)
    data['sources'] = []
    src_dir = DATA_DIR / "sources"
    for f in sorted(src_dir.glob("*.json")):
        srcs = load_json(f)
        if isinstance(srcs, list):
            data['sources'].extend(srcs)

    # Sustancias
    sub_path = DATA_DIR / "sources" / "substances" / "legal_possession.json"
    if sub_path.exists():
        data['substances'] = load_json(sub_path)
    else:
        data['substances'] = []

    # Historial de verificacion
    data['history'] = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data['history'].append(json.loads(line))

    return data

# ============================================================
# HTML TEMPLATES
# ============================================================

CSS = """
:root {
    --bg: #0f172a;
    --surface: #1e293b;
    --surface2: #334155;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --accent2: #818cf8;
    --danger: #f87171;
    --success: #4ade80;
    --warning: #fbbf24;
    --border: #475569;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; scroll-behavior: smooth; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.container { max-width: 900px; margin: 0 auto; padding: 0 1rem; }
header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1rem 0;
    position: sticky; top: 0; z-index: 100;
}
header .container { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }
header h1 { font-size: 1.25rem; }
header h1 a { color: var(--text); }
nav { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.9rem; }
nav a { color: var(--text-muted); }
nav a:hover { color: var(--accent); text-decoration: none; }
main { padding: 2rem 0; }
h2 { font-size: 1.5rem; margin-bottom: 1rem; color: var(--accent); }
h3 { font-size: 1.15rem; margin: 1.5rem 0 0.5rem; }
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.card h3 { margin-top: 0; color: var(--text); }
.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-danger { background: var(--danger); color: #000; }
.badge-success { background: var(--success); color: #000; }
.badge-warning { background: var(--warning); color: #000; }
.badge-info { background: var(--accent); color: #000; }
.badge-purple { background: var(--accent2); color: #fff; }
.alert {
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid;
}
.alert-danger { background: #451a1a; border-color: var(--danger); }
.alert-warning { background: #422006; border-color: var(--warning); }
.alert-info { background: #0c2d48; border-color: var(--accent); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.stat { text-align: center; padding: 1.5rem; }
.stat .number { font-size: 2rem; font-weight: 700; color: var(--accent); }
.stat .label { font-size: 0.85rem; color: var(--text-muted); }
footer {
    border-top: 1px solid var(--border);
    padding: 2rem 0;
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 3rem;
}
table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
th, td { padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; }
ul, ol { padding-left: 1.5rem; margin: 0.5rem 0; }
li { margin-bottom: 0.3rem; }
p { margin-bottom: 0.75rem; }
.tag-list { display: flex; gap: 0.4rem; flex-wrap: wrap; margin: 0.5rem 0; }
@media (max-width: 600px) {
    nav { font-size: 0.8rem; gap: 0.5rem; }
    .grid { grid-template-columns: 1fr; }
    header h1 { font-size: 1.1rem; }
}
"""

NAV_LINKS = [
    ("index.html", "Inicio"),
    ("situaciones.html", "Situaciones"),
    ("derechos.html", "Derechos"),
    ("fuentes.html", "Fuentes"),
    ("emergencia.html", "Emergencia"),
    ("mitos.html", "Mitos"),
    ("contactos.html", "Contactos"),
    ("verificacion.html", "Verificacion"),
]


def page_template(title, body, active=""):
    nav = ""
    for href, label in NAV_LINKS:
        cls = ' style="color:var(--accent);font-weight:600"' if href == active else ""
        nav += f'<a href="{href}"{cls}>{label}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Truths and Rights</title>
<style>{CSS}</style>
</head>
<body>
<header>
<div class="container">
<h1><a href="index.html">Truths &amp; Rights</a></h1>
<nav>{nav}</nav>
</div>
</header>
<main>
<div class="container">
{body}
</div>
</main>
<footer>
<div class="container">
<p>Truths and Rights — Datos legales verificables de fuentes oficiales.</p>
<p>No es asesoria legal. <a href="https://github.com/ELLokoAkrata/truths-and-rights">Codigo fuente (GPL v3)</a></p>
</div>
</footer>
</body>
</html>"""


def esc(text):
    """Escape HTML."""
    if text is None:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

# ============================================================
# PAGE GENERATORS
# ============================================================

def gen_index(data):
    meta = data['metadata']
    emergencies = meta.get('active_emergencies', [])
    stats = meta.get('key_statistics', {})

    alert_html = ""
    for em in emergencies:
        end = em.get('end_date', 'N/A')
        decree = esc(em.get('decree', ''))
        regions = ", ".join(em.get('regions', []))
        suspends = ", ".join(em.get('suspends', []))
        alert_html += f"""<div class="alert alert-danger">
<strong>Estado de emergencia vigente</strong><br>
{decree} — Regiones: {esc(regions)}<br>
Vigente hasta: <strong>{esc(end)}</strong><br>
Derechos suspendidos: {esc(suspends)}<br>
<a href="emergencia.html">Ver detalles completos</a>
</div>"""

    body = f"""
<h2>Conoce tus derechos</h2>
<p>Informacion legal verificable sobre tus derechos ante intervenciones policiales en Peru.</p>
{alert_html}
<div class="grid">
<div class="card stat">
<div class="number">{len(data['sources'])}</div>
<div class="label">Fuentes legales verificadas</div>
</div>
<div class="card stat">
<div class="number">{len(data['rights'])}</div>
<div class="label">Derechos documentados</div>
</div>
<div class="card stat">
<div class="number">{len(data['situations'])}</div>
<div class="label">Situaciones cubiertas</div>
</div>
<div class="card stat">
<div class="number">{len(data['contacts'])}</div>
<div class="label">Contactos de emergencia</div>
</div>
</div>

<h3>Situaciones frecuentes</h3>
<div class="grid">
"""
    for sit in data['situations']:
        title = esc(sit.get('title', sit.get('id', '')))
        severity = sit.get('severity', 'medium')
        badge_cls = 'badge-danger' if severity == 'high' else 'badge-warning' if severity == 'medium' else 'badge-info'
        body += f"""<a href="situaciones.html#{esc(sit['id'])}" class="card" style="text-decoration:none;color:var(--text)">
<h3>{title}</h3>
<span class="badge {badge_cls}">{esc(severity)}</span>
</a>"""

    body += f"""</div>

<h3>Estadisticas</h3>
<div class="card">
<p><strong>{stats.get('police_misconduct_reports_jan_feb_2025', 'N/A')}</strong> denuncias por conducta policial indebida (ene-feb 2025)</p>
<p>Frecuencia: <strong>{esc(stats.get('report_frequency', 'N/A'))}</strong></p>
<p>Fuente: {esc(stats.get('source', 'N/A'))}</p>
</div>

<h3>Principio fundamental</h3>
<div class="alert alert-info">
Si no tiene fuente oficial verificable, no entra a la base de datos.
</div>
"""
    return page_template("Inicio", body, "index.html")


def gen_situaciones(data):
    rights_map = {r['id']: r for r in data['rights']}
    actions_map = {a['id']: a for a in data.get('actions', [])}

    body = "<h2>Situaciones</h2>\n<p>Escenarios comunes en intervenciones policiales y que hacer en cada uno.</p>\n"

    for sit in data['situations']:
        sid = esc(sit['id'])
        title = esc(sit.get('title', sid))
        desc = esc(sit.get('description', ''))
        severity = sit.get('severity', 'medium')
        badge_cls = 'badge-danger' if severity == 'high' else 'badge-warning' if severity == 'medium' else 'badge-info'

        body += f'<div class="card" id="{sid}">\n<h3>{title} <span class="badge {badge_cls}">{esc(severity)}</span></h3>\n<p>{desc}</p>\n'

        # Rights for this situation
        sit_rights = sit.get('rights', [])
        normal_rights = [r for r in sit_rights if r.get('context') == 'normal' and r.get('applies')]
        if normal_rights:
            body += "<h4 style='margin-top:0.75rem;color:var(--accent)'>Tus derechos</h4><ul>\n"
            for sr in normal_rights:
                rid = sr['right_id']
                right = rights_map.get(rid, {})
                rtitle = esc(right.get('title', rid))
                notes = sr.get('notes')
                never = right.get('never_suspended', False)
                badge = ' <span class="badge badge-success">NUNCA SE SUSPENDE</span>' if never else ''
                note_html = f' <em style="color:var(--text-muted)">— {esc(notes)}</em>' if notes else ''
                body += f"<li><strong>{rtitle}</strong>{badge}{note_html}</li>\n"
            body += "</ul>\n"

        # Actions
        sit_actions = sit.get('actions', [])
        if sit_actions:
            body += "<h4 style='margin-top:0.75rem;color:var(--accent)'>Que hacer (paso a paso)</h4><ol>\n"
            for sa in sorted(sit_actions, key=lambda x: x.get('step_order', 99)):
                aid = sa['action_id']
                action = actions_map.get(aid, {})
                atitle = esc(action.get('title', aid))
                script = action.get('suggested_script')
                script_html = f'<br><em style="color:var(--text-muted)">"{esc(script)}"</em>' if script else ''
                body += f"<li>{atitle}{script_html}</li>\n"
            body += "</ol>\n"

        # Time limits
        limits = sit.get('time_limits', [])
        if limits:
            body += "<h4 style='margin-top:0.75rem;color:var(--accent)'>Limites de tiempo</h4><ul>\n"
            for lim in limits:
                hours = lim.get('max_hours', '?')
                ldesc = esc(lim.get('description', ''))
                body += f"<li><strong>{hours} horas</strong> — {ldesc}</li>\n"
            body += "</ul>\n"

        # Contacts
        sit_contacts = sit.get('contacts', [])
        if sit_contacts:
            contacts_map = {c['id']: c for c in data['contacts']}
            body += "<h4 style='margin-top:0.75rem;color:var(--accent)'>A quien llamar</h4><ul>\n"
            for cid in sit_contacts:
                contact = contacts_map.get(cid, {})
                inst = esc(contact.get('institution', cid))
                phone = esc(contact.get('phone', ''))
                body += f"<li><strong>{inst}</strong> — {phone}</li>\n"
            body += "</ul>\n"

        body += "</div>\n"

    return page_template("Situaciones", body, "situaciones.html")


def gen_derechos(data):
    body = "<h2>Derechos del ciudadano</h2>\n<p>Derechos documentados con base legal verificable.</p>\n"

    # Group by category
    categories = {}
    for r in data['rights']:
        cat = r.get('category', 'otros')
        categories.setdefault(cat, []).append(r)

    cat_labels = {
        'dignidad': 'Dignidad',
        'debido_proceso': 'Debido proceso',
        'comunicaciones': 'Comunicaciones',
        'propiedad': 'Propiedad',
        'libertad': 'Libertad',
        'otros': 'Otros',
    }

    for cat, rights in categories.items():
        label = cat_labels.get(cat, cat.replace('_', ' ').title())
        body += f'<h3>{esc(label)}</h3>\n'
        for r in sorted(rights, key=lambda x: x.get('display_order', 99)):
            title = esc(r.get('title', r['id']))
            desc = esc(r.get('description', ''))
            basis = esc(r.get('legal_basis', ''))
            never = r.get('never_suspended', False)
            badge = '<span class="badge badge-success">NUNCA SE SUSPENDE</span>' if never else '<span class="badge badge-warning">SUSPENDIBLE en emergencia</span>'

            body += f"""<div class="card">
<h3>{title} {badge}</h3>
<p>{desc}</p>
<p style="color:var(--text-muted);font-size:0.85rem">Base legal: {basis}</p>
</div>"""

    return page_template("Derechos", body, "derechos.html")


def gen_fuentes(data):
    body = "<h2>Fuentes legales</h2>\n"
    body += f"<p>{len(data['sources'])} fuentes legales verificadas de fuentes oficiales.</p>\n"

    # Group by source_type
    types = {}
    for s in data['sources']:
        st = s.get('source_type', 'otros')
        types.setdefault(st, []).append(s)

    type_labels = {
        'constitucion': 'Constitucion',
        'codigo_procesal': 'Codigo Procesal Penal',
        'codigo_penal': 'Codigo Penal',
        'decreto_legislativo': 'Decretos Legislativos',
        'ley': 'Leyes',
        'jurisprudencia': 'Jurisprudencia',
        'tratado_internacional': 'Tratados Internacionales',
        'resolucion_ministerial': 'Resoluciones Ministeriales',
        'casacion': 'Casaciones',
    }

    for stype, sources in types.items():
        label = type_labels.get(stype, stype.replace('_', ' ').title())
        body += f'<h3>{esc(label)} ({len(sources)})</h3>\n'
        body += '<table><thead><tr><th>Fuente</th><th>Articulo</th><th>Estado</th></tr></thead><tbody>\n'
        for s in sources:
            name = esc(s.get('name', s.get('id', '?')))
            article = esc(s.get('article', '-'))
            status = s.get('status', 'desconocido')
            url = s.get('official_url', '')
            status_badge = 'badge-success' if status == 'vigente' else 'badge-warning' if status == 'modificado' else 'badge-danger'

            name_html = f'<a href="{esc(url)}" target="_blank" rel="noopener">{name}</a>' if url else name
            body += f'<tr><td>{name_html}</td><td>{article}</td><td><span class="badge {status_badge}">{esc(status)}</span></td></tr>\n'
        body += '</tbody></table>\n'

    return page_template("Fuentes legales", body, "fuentes.html")


def gen_emergencia(data):
    contexts = [c for c in data['contexts'] if c.get('context_type') == 'estado_emergencia']
    meta = data['metadata']
    emergencies = meta.get('active_emergencies', [])

    body = "<h2>Estado de emergencia</h2>\n"

    if not emergencies:
        body += '<div class="alert alert-info">No hay estados de emergencia activos registrados.</div>\n'
    else:
        for em in emergencies:
            decree = esc(em.get('decree', 'N/A'))
            regions = ", ".join(em.get('regions', []))
            start = em.get('start_date', 'N/A')
            end = em.get('end_date', 'N/A')
            suspends = em.get('suspends', [])

            # Calculate days remaining
            try:
                end_dt = datetime.strptime(end, '%Y-%m-%d')
                days_left = (end_dt - datetime.now()).days
                if days_left < 0:
                    status_text = f'VENCIDO (hace {abs(days_left)} dias)'
                    alert_class = 'alert-danger'
                elif days_left <= 7:
                    status_text = f'Vence en {days_left} dias'
                    alert_class = 'alert-warning'
                else:
                    status_text = f'Vigente ({days_left} dias restantes)'
                    alert_class = 'alert-info'
            except ValueError:
                status_text = 'Fecha no disponible'
                alert_class = 'alert-warning'

            body += f"""<div class="alert {alert_class}">
<strong>{decree}</strong><br>
Estado: {status_text}<br>
Regiones: {esc(regions)}<br>
Periodo: {esc(start)} al {esc(end)}
</div>"""

            body += '<h3>Derechos suspendidos</h3>\n<div class="card"><ul>\n'
            for s in suspends:
                body += f'<li><span class="badge badge-danger">SUSPENDIDO</span> {esc(s.replace("_", " ").title())}</li>\n'
            body += '</ul></div>\n'

    # Show what is NOT suspended
    body += '<h3>Derechos que NUNCA se suspenden</h3>\n'
    body += '<p>Estos derechos siguen vigentes incluso durante estado de emergencia:</p>\n'
    never_suspended = [r for r in data['rights'] if r.get('never_suspended')]
    body += '<div class="card"><ul>\n'
    for r in never_suspended:
        body += f'<li><span class="badge badge-success">VIGENTE</span> <strong>{esc(r["title"])}</strong> — {esc(r.get("legal_basis", ""))}</li>\n'
    body += '</ul></div>\n'

    # Context details
    for ctx in contexts:
        desc = esc(ctx.get('description', ''))
        body += f'<div class="card"><h3>Detalle del contexto</h3><p>{desc}</p></div>\n'

    return page_template("Estado de emergencia", body, "emergencia.html")


def gen_mitos(data):
    body = "<h2>Mitos y realidades</h2>\n"
    body += "<p>Mitos comunes desmentidos con base legal verificable.</p>\n"

    for m in sorted(data['myths'], key=lambda x: x.get('display_order', 99)):
        myth = esc(m.get('myth', ''))
        reality = esc(m.get('reality', ''))
        explanation = esc(m.get('explanation', ''))
        category = esc(m.get('category', ''))

        body += f"""<div class="card">
<h3><span class="badge badge-danger">MITO</span> "{myth}"</h3>
<p><span class="badge badge-success">REALIDAD</span> <strong>{reality}</strong></p>
<p>{explanation}</p>
<p style="color:var(--text-muted);font-size:0.85rem">Categoria: {category}</p>
</div>"""

    return page_template("Mitos y realidades", body, "mitos.html")


def gen_contactos(data):
    body = "<h2>Contactos de emergencia</h2>\n"
    body += "<p>Telefonos y canales para denunciar abusos o pedir ayuda.</p>\n"

    for c in sorted(data['contacts'], key=lambda x: x.get('priority', 99)):
        inst = esc(c.get('institution', ''))
        desc = esc(c.get('description', ''))
        phone = esc(c.get('phone', ''))
        whatsapp = esc(c.get('whatsapp', ''))
        email = esc(c.get('email', ''))
        website = c.get('website', '')
        hours = esc(c.get('available_hours', ''))
        is_free = c.get('is_free', False)

        free_badge = ' <span class="badge badge-success">GRATUITO</span>' if is_free else ''

        body += f'<div class="card">\n<h3>{inst}{free_badge}</h3>\n<p>{desc}</p>\n'
        if phone:
            body += f'<p><strong>Telefono:</strong> {phone}</p>\n'
        if whatsapp:
            body += f'<p><strong>WhatsApp:</strong> {whatsapp}</p>\n'
        if email:
            body += f'<p><strong>Email:</strong> {email}</p>\n'
        if website:
            body += f'<p><strong>Web:</strong> <a href="{esc(website)}" target="_blank" rel="noopener">{esc(website)}</a></p>\n'
        if hours:
            body += f'<p><strong>Horario:</strong> {hours}</p>\n'
        body += '</div>\n'

    return page_template("Contactos de emergencia", body, "contactos.html")


def gen_verificacion(data):
    body = "<h2>Dashboard de verificacion</h2>\n"
    body += "<p>Estado de frescura de los datos legales del proyecto.</p>\n"

    meta = data['metadata']
    last_verified = meta.get('last_verified', 'N/A')
    body += f"""<div class="card">
<h3>Ultima verificacion general</h3>
<p><strong>{esc(last_verified)}</strong></p>
</div>"""

    # Source status summary
    total = len(data['sources'])
    vigente = sum(1 for s in data['sources'] if s.get('status') == 'vigente')
    body += f"""<div class="grid">
<div class="card stat">
<div class="number">{total}</div>
<div class="label">Fuentes totales</div>
</div>
<div class="card stat">
<div class="number">{vigente}</div>
<div class="label">Vigentes</div>
</div>
<div class="card stat">
<div class="number">{total - vigente}</div>
<div class="label">Requieren revision</div>
</div>
</div>"""

    # Verification history
    history = data.get('history', [])
    if history:
        body += '<h3>Historial de verificaciones</h3>\n'
        body += '<table><thead><tr><th>Fecha</th><th>Tipo</th><th>Resultado</th></tr></thead><tbody>\n'
        for entry in reversed(history[-20:]):
            ts = esc(entry.get('timestamp', 'N/A')[:19])
            ctype = esc(entry.get('check_type', '?'))
            summary = esc(entry.get('summary', ''))
            body += f'<tr><td>{ts}</td><td>{ctype}</td><td>{summary}</td></tr>\n'
        body += '</tbody></table>\n'
    else:
        body += '<div class="alert alert-info">Aun no hay verificaciones registradas. Ejecuta <code>make check-emergency</code> para iniciar.</div>\n'

    return page_template("Verificacion", body, "verificacion.html")


def gen_status_json(data):
    """Genera status.json para badges dinamicos y consumo programatico."""
    meta = data['metadata']
    emergencies = meta.get('active_emergencies', [])

    emergency_status = "none"
    for em in emergencies:
        end = em.get('end_date', '')
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d')
            if datetime.now() > end_dt:
                emergency_status = "expired"
            elif (end_dt - datetime.now()).days <= 7:
                emergency_status = "expiring_soon"
            else:
                emergency_status = "active"
        except ValueError:
            emergency_status = "unknown"

    return json.dumps({
        "generated_at": datetime.now().isoformat(),
        "country": "PE",
        "sources_count": len(data['sources']),
        "rights_count": len(data['rights']),
        "situations_count": len(data['situations']),
        "contacts_count": len(data['contacts']),
        "last_verified": meta.get('last_verified', None),
        "emergency_status": emergency_status,
        "emergencies": emergencies,
    }, ensure_ascii=False, indent=2)

# ============================================================
# MAIN
# ============================================================

def main():
    print("Truths and Rights — Generador de sitio estatico")
    print(f"Leyendo datos de {DATA_DIR}")

    data = load_all_data()
    print(f"  {len(data['sources'])} fuentes, {len(data['rights'])} derechos, {len(data['situations'])} situaciones")

    SITE_DIR.mkdir(parents=True, exist_ok=True)

    pages = [
        ("index.html", gen_index(data)),
        ("situaciones.html", gen_situaciones(data)),
        ("derechos.html", gen_derechos(data)),
        ("fuentes.html", gen_fuentes(data)),
        ("emergencia.html", gen_emergencia(data)),
        ("mitos.html", gen_mitos(data)),
        ("contactos.html", gen_contactos(data)),
        ("verificacion.html", gen_verificacion(data)),
    ]

    for filename, content in pages:
        path = SITE_DIR / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Generado: {filename}")

    # status.json
    status_path = SITE_DIR / "status.json"
    with open(status_path, 'w', encoding='utf-8') as f:
        f.write(gen_status_json(data))
    print(f"  Generado: status.json")

    print(f"\nSitio generado en {SITE_DIR}/")
    print(f"  Total: {len(pages)} paginas + status.json")


if __name__ == "__main__":
    main()
