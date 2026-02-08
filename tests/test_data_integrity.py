"""
Tests de integridad de datos.
Verifica que todos los JSON son validos, campos obligatorios presentes,
IDs no duplicados, valores dentro de rangos permitidos.
"""

import json
from pathlib import Path

import pytest


# ============================================================
# JSON validos
# ============================================================

def get_all_json_files():
    data_dir = Path(__file__).parent.parent / "data" / "PE"
    return list(data_dir.rglob("*.json"))


@pytest.mark.parametrize("json_file", get_all_json_files(), ids=lambda f: f.name)
def test_json_is_valid(json_file):
    """Cada archivo JSON debe ser parseable."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data is not None


@pytest.mark.parametrize("json_file", get_all_json_files(), ids=lambda f: f.name)
def test_json_is_utf8(json_file):
    """Cada archivo JSON debe ser UTF-8."""
    with open(json_file, "rb") as f:
        raw = f.read()
    raw.decode("utf-8")


# ============================================================
# Fuentes legales
# ============================================================

class TestSources:
    REQUIRED_FIELDS = ["id", "source_type", "name", "full_text", "summary", "status"]
    VALID_TYPES = [
        "constitucion", "codigo_penal", "codigo_procesal",
        "decreto_legislativo", "ley", "jurisprudencia", "tratado_internacional",
    ]
    VALID_STATUS = ["vigente", "modificado", "derogado", "parcialmente_inconstitucional"]

    def test_sources_not_empty(self, all_sources):
        assert len(all_sources) > 0

    def test_no_duplicate_ids(self, all_sources):
        ids = [s["id"] for s in all_sources]
        assert len(ids) == len(set(ids)), f"IDs duplicados: {[x for x in ids if ids.count(x) > 1]}"

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_sources, field):
        for s in all_sources:
            assert field in s and s[field], f"Fuente '{s.get('id', '?')}' sin campo '{field}'"

    def test_valid_source_types(self, all_sources):
        for s in all_sources:
            assert s["source_type"] in self.VALID_TYPES, (
                f"Fuente '{s['id']}': tipo invalido '{s['source_type']}'"
            )

    def test_valid_status(self, all_sources):
        for s in all_sources:
            assert s["status"] in self.VALID_STATUS, (
                f"Fuente '{s['id']}': status invalido '{s['status']}'"
            )


# ============================================================
# Derechos
# ============================================================

class TestRights:
    REQUIRED_FIELDS = ["id", "title", "description", "legal_basis", "category"]
    VALID_CATEGORIES = [
        "libertad", "integridad", "comunicaciones",
        "propiedad", "debido_proceso", "dignidad",
    ]

    def test_rights_not_empty(self, all_rights):
        assert len(all_rights) > 0

    def test_no_duplicate_ids(self, all_rights):
        ids = [r["id"] for r in all_rights]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_rights, field):
        for r in all_rights:
            assert field in r and r[field], f"Derecho '{r.get('id', '?')}' sin campo '{field}'"

    def test_valid_categories(self, all_rights):
        for r in all_rights:
            assert r["category"] in self.VALID_CATEGORIES, (
                f"Derecho '{r['id']}': categoria invalida '{r['category']}'"
            )

    def test_ids_have_right_prefix(self, all_rights):
        for r in all_rights:
            assert r["id"].startswith("right_"), f"Derecho '{r['id']}' no tiene prefijo 'right_'"


# ============================================================
# Acciones
# ============================================================

class TestActions:
    REQUIRED_FIELDS = ["id", "action_type", "title", "description"]
    VALID_TYPES = ["decir", "hacer", "no_hacer", "grabar", "llamar", "documentar"]

    def test_actions_not_empty(self, all_actions):
        assert len(all_actions) > 0

    def test_no_duplicate_ids(self, all_actions):
        ids = [a["id"] for a in all_actions]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_actions, field):
        for a in all_actions:
            assert field in a and a[field], f"Accion '{a.get('id', '?')}' sin campo '{field}'"

    def test_valid_action_types(self, all_actions):
        for a in all_actions:
            assert a["action_type"] in self.VALID_TYPES, (
                f"Accion '{a['id']}': tipo invalido '{a['action_type']}'"
            )

    def test_ids_have_action_prefix(self, all_actions):
        for a in all_actions:
            assert a["id"].startswith("action_"), f"Accion '{a['id']}' no tiene prefijo 'action_'"


# ============================================================
# Contactos
# ============================================================

class TestContacts:
    REQUIRED_FIELDS = ["id", "institution", "description", "contact_type"]

    def test_contacts_not_empty(self, all_contacts):
        assert len(all_contacts) > 0

    def test_no_duplicate_ids(self, all_contacts):
        ids = [c["id"] for c in all_contacts]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_contacts, field):
        for c in all_contacts:
            assert field in c and c[field], f"Contacto '{c.get('id', '?')}' sin campo '{field}'"

    def test_at_least_one_contact_method(self, all_contacts):
        for c in all_contacts:
            has_method = any(c.get(f) for f in ["phone", "whatsapp", "email", "website"])
            assert has_method, f"Contacto '{c['id']}' sin medio de contacto"


# ============================================================
# Situaciones
# ============================================================

class TestSituations:
    REQUIRED_FIELDS = ["id", "category", "title", "description", "keywords", "natural_queries"]

    def test_situations_not_empty(self, all_situations):
        assert len(all_situations) > 0

    def test_no_duplicate_ids(self, all_situations):
        ids = [s["id"] for s in all_situations]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_situations, field):
        for s in all_situations:
            assert field in s and s[field], f"Situacion '{s.get('id', '?')}' sin campo '{field}'"

    def test_keywords_are_list(self, all_situations):
        for s in all_situations:
            assert isinstance(s["keywords"], list), f"Situacion '{s['id']}': keywords no es lista"
            assert len(s["keywords"]) > 0, f"Situacion '{s['id']}': keywords vacio"

    def test_natural_queries_are_list(self, all_situations):
        for s in all_situations:
            assert isinstance(s["natural_queries"], list), f"Situacion '{s['id']}': natural_queries no es lista"
            assert len(s["natural_queries"]) > 0, f"Situacion '{s['id']}': natural_queries vacio"

    def test_situations_have_rights(self, all_situations):
        for s in all_situations:
            assert "rights" in s and len(s["rights"]) > 0, (
                f"Situacion '{s['id']}' no tiene derechos asociados"
            )

    def test_situations_have_actions(self, all_situations):
        for s in all_situations:
            assert "actions" in s and len(s["actions"]) > 0, (
                f"Situacion '{s['id']}' no tiene acciones asociadas"
            )

    def test_situations_have_contacts(self, all_situations):
        for s in all_situations:
            assert "contacts" in s and len(s["contacts"]) > 0, (
                f"Situacion '{s['id']}' no tiene contactos asociados"
            )


# ============================================================
# Mitos
# ============================================================

class TestMyths:
    REQUIRED_FIELDS = ["id", "myth", "reality", "explanation", "category"]

    def test_myths_not_empty(self, all_myths):
        assert len(all_myths) > 0

    def test_no_duplicate_ids(self, all_myths):
        ids = [m["id"] for m in all_myths]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_fields_present(self, all_myths, field):
        for m in all_myths:
            assert field in m and m[field], f"Mito '{m.get('id', '?')}' sin campo '{field}'"


# ============================================================
# Contextos
# ============================================================

class TestContexts:
    def test_contexts_not_empty(self, all_contexts):
        assert len(all_contexts) > 0

    def test_normal_context_exists(self, all_contexts):
        ids = [c["id"] for c in all_contexts]
        assert "normal" in ids, "Falta contexto 'normal' (obligatorio)"
