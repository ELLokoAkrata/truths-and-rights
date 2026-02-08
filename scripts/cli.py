#!/usr/bin/env python3
"""
Truths and Rights — CLI de consulta
Simula la experiencia de la app en la terminal.

Uso:
    python cli.py "me quieren revisar el celular"
    python cli.py "me encuentran con marihuana"
    python cli.py                                   # modo interactivo
"""

import io
import sys
from pathlib import Path

# Fix encoding on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar scripts/ al path para importar search
sys.path.insert(0, str(Path(__file__).parent))
from search import search_situation, get_situation_details


# --- Colores para terminal ---

class Color:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


def c(text, color):
    """Aplica color al texto."""
    return f"{color}{text}{Color.RESET}"


def separator(char='-', length=60):
    return char * length


def print_header():
    print()
    print(c(separator('='), Color.BLUE))
    print(c("  TRUTHS AND RIGHTS", Color.BOLD))
    print(c("  Tus derechos ante intervenciones policiales", Color.DIM))
    print(c(separator('='), Color.BLUE))


def print_situation(result):
    """Imprime la situacion detectada."""
    severity_colors = {
        'low': Color.GREEN,
        'medium': Color.YELLOW,
        'high': Color.RED,
        'critical': Color.RED,
    }
    sev_color = severity_colors.get(result['severity'], Color.WHITE)

    print()
    print(c(" SITUACION DETECTADA ", Color.BOLD))
    print(c(separator(), Color.DIM))
    print(f"  {c(result['title'], Color.BOLD)}")
    print(f"  {result['description']}")
    print(f"  Severidad: {c(result['severity'].upper(), sev_color)}")
    print(f"  Relevancia: {result['score']:.0%}")


def print_rights(rights):
    """Imprime derechos aplicables."""
    if not rights:
        return

    print()
    print(c(" TUS DERECHOS ", Color.BOLD))
    print(c(separator(), Color.DIM))

    # Agrupar por contexto, mostrar primero 'normal'
    normal_rights = [r for r in rights if r['context_id'] == 'normal' and r['applies']]
    emergency_rights = [r for r in rights if r['context_id'] != 'normal']

    seen = set()
    for r in normal_rights:
        if r['id'] in seen:
            continue
        seen.add(r['id'])

        absolute = ""
        if r['never_suspended']:
            absolute = c(" [NUNCA SE SUSPENDE]", Color.GREEN)

        print(f"\n  {c(r['title'], Color.CYAN)}{absolute}")
        print(f"  {r['description']}")
        print(f"  {c('Base legal:', Color.DIM)} {r['legal_basis']}")

        if r['notes']:
            print(f"  {c('Nota:', Color.YELLOW)} {r['notes']}")

    # Notas de estado de emergencia
    emergency_notes = []
    for r in emergency_rights:
        if r['notes'] and r['notes'] not in emergency_notes:
            emergency_notes.append(r['notes'])

    if emergency_notes:
        print(f"\n  {c('En estado de emergencia:', Color.YELLOW)}")
        for note in emergency_notes:
            print(f"    - {note}")


def print_actions(actions):
    """Imprime acciones paso a paso."""
    if not actions:
        return

    print()
    print(c(" QUE HACER (PASO A PASO) ", Color.BOLD))
    print(c(separator(), Color.DIM))

    for a in actions:
        type_labels = {
            'decir': 'DECIR',
            'hacer': 'HACER',
            'no_hacer': 'NO HACER',
            'grabar': 'GRABAR',
            'llamar': 'LLAMAR',
            'documentar': 'DOCUMENTAR',
        }
        type_label = type_labels.get(a['action_type'], a['action_type'].upper())
        type_color = Color.RED if a['action_type'] == 'no_hacer' else Color.GREEN

        step = a['step_order']
        print(f"\n  {c(f'Paso {step}', Color.BOLD)} [{c(type_label, type_color)}]")
        print(f"  {c(a['title'], Color.CYAN)}")
        print(f"  {a['description']}")

        if a['script']:
            print(f"\n  {c('Texto sugerido:', Color.YELLOW)}")
            print(f"  \"{a['script']}\"")

        if a['warning']:
            print(f"\n  {c('Advertencia:', Color.RED)} {a['warning']}")


def print_time_limits(time_limits):
    """Imprime limites de tiempo."""
    if not time_limits:
        return

    print()
    print(c(" LIMITES DE TIEMPO ", Color.BOLD))
    print(c(separator(), Color.DIM))

    for tl in time_limits:
        hours = tl['max_hours']
        label = f"{int(hours)} horas" if hours == int(hours) else f"{hours} horas"

        print(f"\n  {c(tl['description'], Color.CYAN)}")
        print(f"  Maximo: {c(label, Color.RED)}")

        if tl['max_hours_emergency'] and tl['max_hours_emergency'] != hours:
            e_hours = tl['max_hours_emergency']
            e_label = f"{int(e_hours)} horas" if e_hours == int(e_hours) else f"{e_hours} horas"
            print(f"  En emergencia: {c(e_label, Color.YELLOW)}")

        if tl['applies_to'] != 'todos':
            print(f"  Aplica a: {tl['applies_to']}")

        print(f"  {c('Si se excede:', Color.RED)} {tl['after_expiry_action']}")


def print_contacts(contacts):
    """Imprime contactos de emergencia."""
    if not contacts:
        return

    print()
    print(c(" A QUIEN LLAMAR ", Color.BOLD))
    print(c(separator(), Color.DIM))

    for ct in contacts:
        print(f"\n  {c(ct['institution'], Color.CYAN)}")
        print(f"  {ct['description']}")

        if ct['phone']:
            print(f"  Tel: {c(ct['phone'], Color.GREEN)}")
        if ct.get('whatsapp'):
            print(f"  WhatsApp: {c(ct['whatsapp'], Color.GREEN)}")
        if ct.get('website'):
            print(f"  Web: {ct['website']}")

        free_label = "Gratuito" if ct['is_free'] else "De pago"
        print(f"  {free_label} | {ct['available_hours']}")


def print_other_results(results):
    """Imprime otras situaciones posibles."""
    if len(results) <= 1:
        return

    print()
    print(c(" OTRAS SITUACIONES POSIBLES ", Color.DIM))
    print(c(separator(), Color.DIM))

    for r in results[1:]:
        print(f"  - {r['title']} ({r['score']:.0%})")


def print_footer():
    print()
    print(c(separator('='), Color.BLUE))
    print(c("  Esta informacion NO es asesoria legal.", Color.DIM))
    print(c("  Para casos especificos, consulta con un abogado.", Color.DIM))
    print(c(separator('='), Color.BLUE))
    print()


def run_query(query):
    """Ejecuta una consulta y muestra resultados completos."""
    print_header()
    print(f"\n  Consulta: \"{c(query, Color.BOLD)}\"")

    results = search_situation(query)

    if not results:
        print(f"\n  {c('No se encontraron situaciones relevantes.', Color.YELLOW)}")
        print(f"  Intenta con otras palabras, por ejemplo:")
        print(f"    - \"me piden el DNI\"")
        print(f"    - \"quieren revisar mi mochila\"")
        print(f"    - \"me llevan a la comisaria\"")
        print_footer()
        return

    best = results[0]
    print_situation(best)

    details = get_situation_details(best['situation_id'])
    print_rights(details['rights'])
    print_actions(details['actions'])
    print_time_limits(details['time_limits'])
    print_contacts(details['contacts'])
    print_other_results(results)
    print_footer()


def interactive_mode():
    """Modo interactivo: pregunta hasta que el usuario salga."""
    print_header()
    print(f"\n  {c('Modo interactivo', Color.BOLD)} — escribe tu situacion")
    print(f"  Escribe 'salir' para terminar.\n")

    while True:
        try:
            query = input(f"  {c('>', Color.CYAN)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue
        if query.lower() in ('salir', 'exit', 'quit', 'q'):
            break

        run_query(query)
        msg = 'Escribe otra consulta o "salir" para terminar.'
        print(f"\n  {c(msg, Color.DIM)}\n")


def main():
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        run_query(query)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
