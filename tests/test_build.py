"""
Tests del build de la base de datos.
Verifica que build_db.py genera una DB correcta con todas las tablas pobladas.
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


class TestBuildProcess:
    def test_build_script_exists(self):
        assert (PROJECT_ROOT / "scripts" / "build_db.py").exists()

    def test_build_runs_without_error(self, tmp_path):
        """El build debe ejecutarse sin errores."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "build_db.py"), "--country", "PE"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, f"Build fallo: {result.stderr}"

    def test_db_file_created(self, db_path):
        assert db_path.exists()

    def test_db_file_not_empty(self, db_path):
        assert db_path.stat().st_size > 0


class TestDatabaseTables:
    EXPECTED_TABLES = [
        "legal_sources",
        "situations",
        "contexts",
        "rights",
        "situation_rights",
        "right_sources",
        "actions",
        "situation_actions",
        "emergency_contacts",
        "situation_contacts",
        "time_limits",
        "myths",
    ]

    def test_all_tables_exist(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row["name"] for row in cursor.fetchall()}

        for table in self.EXPECTED_TABLES:
            assert table in tables, f"Tabla '{table}' no existe en la DB"

    @pytest.mark.parametrize("table,min_count", [
        ("legal_sources", 40),
        ("situations", 9),
        ("rights", 20),
        ("actions", 17),
        ("emergency_contacts", 7),
        ("myths", 7),
        ("contexts", 2),
        ("situation_rights", 1),
        ("situation_actions", 1),
        ("situation_contacts", 1),
    ])
    def test_table_has_minimum_records(self, db_conn, table, min_count):
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
        count = cursor.fetchone()["cnt"]
        assert count >= min_count, (
            f"Tabla '{table}': tiene {count} registros, se esperaban al menos {min_count}"
        )


class TestDatabaseViews:
    EXPECTED_VIEWS = ["v_situation_full", "v_situation_steps"]

    def test_views_exist(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = {row["name"] for row in cursor.fetchall()}

        for view in self.EXPECTED_VIEWS:
            assert view in views, f"Vista '{view}' no existe en la DB"

    def test_v_situation_full_returns_data(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM v_situation_full")
        assert cursor.fetchone()["cnt"] > 0

    def test_v_situation_steps_returns_data(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM v_situation_steps")
        assert cursor.fetchone()["cnt"] > 0


class TestDatabaseIndexes:
    EXPECTED_INDEXES = [
        "idx_situations_category",
        "idx_situations_keywords",
        "idx_rights_category",
    ]

    def test_indexes_exist(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row["name"] for row in cursor.fetchall()}

        for idx in self.EXPECTED_INDEXES:
            assert idx in indexes, f"Indice '{idx}' no existe en la DB"


class TestDatabaseContent:
    def test_all_situations_have_rights(self, db_conn):
        """Cada situacion debe tener al menos un derecho asociado."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT s.id FROM situations s
            LEFT JOIN situation_rights sr ON s.id = sr.situation_id
            WHERE sr.situation_id IS NULL
        """)
        orphans = [row["id"] for row in cursor.fetchall()]
        assert len(orphans) == 0, f"Situaciones sin derechos: {orphans}"

    def test_all_situations_have_actions(self, db_conn):
        """Cada situacion debe tener al menos una accion asociada."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT s.id FROM situations s
            LEFT JOIN situation_actions sa ON s.id = sa.situation_id
            WHERE sa.situation_id IS NULL
        """)
        orphans = [row["id"] for row in cursor.fetchall()]
        assert len(orphans) == 0, f"Situaciones sin acciones: {orphans}"

    def test_all_situations_have_contacts(self, db_conn):
        """Cada situacion debe tener al menos un contacto asociado."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT s.id FROM situations s
            LEFT JOIN situation_contacts sc ON s.id = sc.situation_id
            WHERE sc.situation_id IS NULL
        """)
        orphans = [row["id"] for row in cursor.fetchall()]
        assert len(orphans) == 0, f"Situaciones sin contactos: {orphans}"

    def test_action_steps_are_sequential(self, db_conn):
        """Los pasos de acciones deben ser secuenciales por situacion."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT situation_id, GROUP_CONCAT(step_order) as steps
            FROM situation_actions
            WHERE context_id = 'normal'
            GROUP BY situation_id
        """)
        for row in cursor.fetchall():
            steps = sorted(int(s) for s in row["steps"].split(","))
            expected = list(range(steps[0], steps[0] + len(steps)))
            assert steps == expected, (
                f"Situacion '{row['situation_id']}': pasos no secuenciales {steps}"
            )
