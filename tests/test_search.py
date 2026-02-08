"""
Tests del buscador de lenguaje natural.
Verifica que search.py encuentra la situacion correcta
para distintas consultas en espanol.
"""

import sys
from pathlib import Path

import pytest

# Agregar scripts/ al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search import search_situation, get_situation_details, normalize, tokenize


# ============================================================
# Tests de utilidades
# ============================================================

class TestNormalize:
    def test_lowercase(self):
        assert normalize("HOLA MUNDO") == "hola mundo"

    def test_remove_accents(self):
        assert normalize("policía intervención") == "policia intervencion"

    def test_remove_punctuation(self):
        assert normalize("¿hola, mundo!") == "hola mundo"

    def test_collapse_spaces(self):
        assert normalize("  hola   mundo  ") == "hola mundo"

    def test_combined(self):
        assert normalize("¿Cuánto TIEMPO me pueden retener?") == "cuanto tiempo me pueden retener"


class TestTokenize:
    def test_basic(self):
        assert tokenize("hola mundo") == {"hola", "mundo"}

    def test_dedup(self):
        assert tokenize("hola hola mundo") == {"hola", "mundo"}

    def test_normalizes(self):
        assert tokenize("Policía POLICÍA policía") == {"policia"}


# ============================================================
# Tests del buscador — la situacion correcta debe ser el primer resultado
# ============================================================

class TestSearchCorrectMatch:
    """
    Cada test verifica que la consulta devuelve la situacion esperada
    como primer resultado. Estos son los 20+ queries de prueba requeridos.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db_path):
        self.db_path = db_path

    def _first_id(self, query):
        results = search_situation(query, db_path=self.db_path)
        assert len(results) > 0, f"Sin resultados para: '{query}'"
        return results[0]["situation_id"]

    # --- DNI / Identificacion ---

    def test_me_piden_el_dni(self):
        assert self._first_id("me piden el DNI") == "police_id_check"

    def test_me_piden_documentos(self):
        assert self._first_id("me piden documentos") == "police_id_check"

    def test_me_paran_en_la_calle(self):
        assert self._first_id("me paran en la calle") == "police_id_check"

    # --- Mochila / Registro ---

    def test_quieren_revisar_mi_mochila(self):
        assert self._first_id("quieren revisar mi mochila") == "police_bag_search"

    def test_me_quieren_registrar(self):
        assert self._first_id("me quieren registrar la mochila") == "police_bag_search"

    # --- Celular ---

    def test_quieren_ver_mi_celular(self):
        assert self._first_id("quieren ver mi celular") == "police_phone_search"

    def test_me_piden_el_imei(self):
        assert self._first_id("me piden el IMEI") == "police_phone_search"

    def test_me_piden_desbloquear_celular(self):
        assert self._first_id("me piden desbloquear el celular") == "police_phone_search"

    # --- Comisaria ---

    def test_me_llevan_a_comisaria(self):
        assert self._first_id("me llevan a la comisaría") == "police_station_no_arrest"

    def test_me_quieren_llevar_comisaria(self):
        assert self._first_id("me quieren llevar a la comisaría") == "police_station_no_arrest"

    # --- Negarse a documentos ---

    def test_me_niego_mostrar_documentos(self):
        assert self._first_id("me niego a mostrar documentos") == "refuse_show_documents"

    # --- Grabar ---

    def test_puedo_grabar_al_policia(self):
        assert self._first_id("puedo grabar al policía") == "recording_police"

    def test_es_legal_grabar(self):
        assert self._first_id("es legal grabar a la policía") == "recording_police"

    # --- Retencion ---

    def test_cuanto_tiempo_retener(self):
        assert self._first_id("cuánto tiempo me pueden retener") == "retention_time"

    def test_cuantas_horas_retenerme(self):
        assert self._first_id("cuántas horas pueden retenerme") == "retention_time"

    # --- Sin motivo ---

    def test_no_me_dicen_motivo(self):
        assert self._first_id("no me dicen por qué me paran") == "no_reason_given"

    def test_sin_razon(self):
        assert self._first_id("me intervienen sin razón") == "no_reason_given"

    # --- Cannabis ---

    def test_me_encuentran_con_marihuana(self):
        assert self._first_id("me encuentran con marihuana") == "cannabis_possession"

    def test_me_ven_fumando(self):
        assert self._first_id("me ven fumando") == "cannabis_possession"

    def test_tengo_hierba_encima(self):
        assert self._first_id("tengo hierba encima") == "cannabis_possession"

    def test_me_encontraron_un_porro(self):
        assert self._first_id("me encontraron un porro") == "cannabis_possession"


# ============================================================
# Tests de calidad del buscador
# ============================================================

class TestSearchQuality:
    @pytest.fixture(autouse=True)
    def setup(self, db_path):
        self.db_path = db_path

    def test_returns_multiple_results(self):
        results = search_situation("me piden documentos", db_path=self.db_path)
        assert len(results) >= 1

    def test_results_are_sorted_by_score(self):
        results = search_situation("me piden el DNI", db_path=self.db_path)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_best_score_is_highest(self):
        results = search_situation("me encuentran con marihuana", db_path=self.db_path)
        assert results[0]["score"] >= results[-1]["score"]

    def test_results_have_required_fields(self):
        results = search_situation("me piden el DNI", db_path=self.db_path)
        for r in results:
            assert "situation_id" in r
            assert "title" in r
            assert "score" in r
            assert "match_details" in r

    def test_empty_query_returns_empty(self):
        results = search_situation("", db_path=self.db_path)
        assert len(results) == 0

    def test_gibberish_returns_empty_or_low_score(self):
        results = search_situation("xyzabc123", db_path=self.db_path)
        if results:
            assert results[0]["score"] < 0.2


# ============================================================
# Tests de get_situation_details
# ============================================================

class TestGetSituationDetails:
    @pytest.fixture(autouse=True)
    def setup(self, db_path):
        self.db_path = db_path

    def test_returns_rights(self):
        details = get_situation_details("police_id_check", db_path=self.db_path)
        assert len(details["rights"]) > 0

    def test_returns_actions(self):
        details = get_situation_details("police_id_check", db_path=self.db_path)
        assert len(details["actions"]) > 0

    def test_returns_contacts(self):
        details = get_situation_details("police_id_check", db_path=self.db_path)
        assert len(details["contacts"]) > 0

    def test_actions_are_ordered(self):
        details = get_situation_details("cannabis_possession", db_path=self.db_path)
        steps = [a["step_order"] for a in details["actions"]]
        assert steps == sorted(steps)

    def test_cannabis_has_time_limits(self):
        details = get_situation_details("cannabis_possession", db_path=self.db_path)
        assert len(details["time_limits"]) > 0

    def test_nonexistent_situation_returns_empty(self):
        details = get_situation_details("nonexistent_id", db_path=self.db_path)
        assert len(details["rights"]) == 0
        assert len(details["actions"]) == 0
