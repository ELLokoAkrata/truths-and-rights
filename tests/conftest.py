"""
Fixtures compartidos para todos los tests.
"""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "PE"
BUILD_DIR = PROJECT_ROOT / "build"
DB_PATH = BUILD_DIR / "truths_and_rights_pe.db"


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir():
    return DATA_DIR


@pytest.fixture(scope="session")
def db_path():
    """Genera la DB antes de los tests si no existe."""
    if not DB_PATH.exists():
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "build_db.py"), "--country", "PE"],
            check=True,
            capture_output=True,
        )
    return DB_PATH


@pytest.fixture(scope="session")
def db_conn(db_path):
    """Conexion a la DB de tests."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def all_sources(data_dir):
    """Carga todas las fuentes legales."""
    sources_dir = data_dir / "sources"
    data = []
    for f in sources_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
            if isinstance(loaded, list):
                data.extend(loaded)
            else:
                data.append(loaded)
    return data


@pytest.fixture(scope="session")
def all_situations(data_dir):
    """Carga todas las situaciones."""
    sit_dir = data_dir / "situations"
    data = []
    for f in sorted(sit_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
            if isinstance(loaded, list):
                data.extend(loaded)
            else:
                data.append(loaded)
    return data


@pytest.fixture(scope="session")
def all_rights(data_dir):
    """Carga todos los derechos."""
    path = data_dir / "rights" / "rights.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_actions(data_dir):
    """Carga todas las acciones."""
    path = data_dir / "actions" / "actions.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_contacts(data_dir):
    """Carga todos los contactos."""
    path = data_dir / "contacts" / "emergency_contacts.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_myths(data_dir):
    """Carga todos los mitos."""
    path = data_dir / "myths" / "myths.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_contexts(data_dir):
    """Carga todos los contextos."""
    path = data_dir / "contexts" / "contexts.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
