"""
Tests de referencias cruzadas.
Verifica que todos los IDs referenciados en situaciones
existen en sus tablas correspondientes.
"""

import pytest


class TestRightsReferences:
    def test_situation_rights_reference_existing_rights(self, all_situations, all_rights):
        """Cada right_id en situaciones debe existir en rights.json."""
        right_ids = {r["id"] for r in all_rights}

        for sit in all_situations:
            for right_rel in sit.get("rights", []):
                rid = right_rel["right_id"]
                assert rid in right_ids, (
                    f"Situacion '{sit['id']}' referencia derecho inexistente: '{rid}'"
                )

    def test_all_rights_are_referenced(self, all_situations, all_rights):
        """Cada derecho deberia estar referenciado en al menos una situacion."""
        referenced = set()
        for sit in all_situations:
            for right_rel in sit.get("rights", []):
                referenced.add(right_rel["right_id"])

        all_ids = {r["id"] for r in all_rights}
        unreferenced = all_ids - referenced

        # Warning, no error: algunos derechos son generales
        if unreferenced:
            pytest.skip(f"Derechos sin usar (no es error critico): {unreferenced}")


class TestActionsReferences:
    def test_situation_actions_reference_existing_actions(self, all_situations, all_actions):
        """Cada action_id en situaciones debe existir en actions.json."""
        action_ids = {a["id"] for a in all_actions}

        for sit in all_situations:
            for action_rel in sit.get("actions", []):
                aid = action_rel["action_id"]
                assert aid in action_ids, (
                    f"Situacion '{sit['id']}' referencia accion inexistente: '{aid}'"
                )

    def test_all_actions_are_referenced(self, all_situations, all_actions):
        """Cada accion deberia estar referenciada en al menos una situacion."""
        referenced = set()
        for sit in all_situations:
            for action_rel in sit.get("actions", []):
                referenced.add(action_rel["action_id"])

        all_ids = {a["id"] for a in all_actions}
        unreferenced = all_ids - referenced

        if unreferenced:
            pytest.skip(f"Acciones sin usar (no es error critico): {unreferenced}")


class TestContactsReferences:
    def test_situation_contacts_reference_existing_contacts(self, all_situations, all_contacts):
        """Cada contact_id en situaciones debe existir en emergency_contacts.json."""
        contact_ids = {c["id"] for c in all_contacts}

        for sit in all_situations:
            for cid in sit.get("contacts", []):
                assert cid in contact_ids, (
                    f"Situacion '{sit['id']}' referencia contacto inexistente: '{cid}'"
                )


class TestSourcesReferences:
    def test_rights_source_ids_exist(self, all_rights, all_sources):
        """Cada source_id en derechos debe existir en las fuentes."""
        source_ids = {s["id"] for s in all_sources}

        for right in all_rights:
            for sid in right.get("source_ids", []):
                assert sid in source_ids, (
                    f"Derecho '{right['id']}' referencia fuente inexistente: '{sid}'"
                )

    def test_myths_source_ids_exist(self, all_myths, all_sources):
        """Cada source_id en mitos debe existir en las fuentes."""
        source_ids = {s["id"] for s in all_sources}

        for myth in all_myths:
            for sid in myth.get("related_source_ids", []):
                assert sid in source_ids, (
                    f"Mito '{myth['id']}' referencia fuente inexistente: '{sid}'"
                )


class TestContextsReferences:
    def test_situation_rights_contexts_exist(self, all_situations, all_contexts):
        """Cada context_id en situation.rights debe existir en contexts.json."""
        context_ids = {c["id"] for c in all_contexts}

        for sit in all_situations:
            for right_rel in sit.get("rights", []):
                ctx = right_rel.get("context", "normal")
                assert ctx in context_ids, (
                    f"Situacion '{sit['id']}' referencia contexto inexistente: '{ctx}'"
                )


class TestTimeLimitsReferences:
    def test_time_limits_reference_existing_sources(self, all_situations, all_sources):
        """Cada source_id en time_limits debe existir en las fuentes."""
        source_ids = {s["id"] for s in all_sources}

        for sit in all_situations:
            for tl in sit.get("time_limits", []):
                sid = tl.get("source_id")
                if sid:
                    assert sid in source_ids, (
                        f"Situacion '{sit['id']}', time_limit '{tl['id']}' "
                        f"referencia fuente inexistente: '{sid}'"
                    )
