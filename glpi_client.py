"""
glpi_client.py
--------------
Funciones utilitarias para:
1. Crear una sesión contra la API REST de GLPI.
2. Obtener tickets abiertos.
3. Cerrar la sesión (buena práctica).

Requiere que en `.env` existan:
  GLPI_BASE_URL   - p.ej. https://midominio/glpi
  GLPI_APP_TOKEN  - token de aplicación (Setup ▸ General ▸ API)
  GLPI_USER_TOKEN - token personal del usuario API
"""

import os, requests
from contextlib import contextmanager
from typing import List, Dict
from config import GLPI_BASE_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN

HEADERS = {
    "Content-Type": "application/json",
    "App-Token": GLPI_APP_TOKEN,
    "Authorization": f"user_token {GLPI_USER_TOKEN}"
}

def _init_session() -> str:
    """Devuelve el Session-Token obtenido en /initSession"""
    url = f"{GLPI_BASE_URL}/apirest.php/initSession"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()["session_token"]

def _kill_session(session_token: str) -> None:
    url = f"{GLPI_BASE_URL}/apirest.php/killSession"
    h = {**HEADERS, "Session-Token": session_token}
    requests.get(url, headers=h, timeout=10)

@contextmanager
def glpi_session():
    """Context manager → yielder de Session-Token seguro."""
    token = _init_session()
    try:
        yield token
    finally:
        _kill_session(token)

def get_open_tickets(limit: int = 20) -> List[Dict]:
    """
    Devuelve una lista de dicts con id, name y content para los tickets abiertos.
    Por simplicidad usa /Ticket/?range=0-{limit-1}.
    """
    with glpi_session() as sess:
        url = f"{GLPI_BASE_URL}/apirest.php/Ticket/?range=0-{limit-1}"
        h = {**HEADERS, "Session-Token": sess}
        r = requests.get(url, headers=h, timeout=10)
        r.raise_for_status()
        tickets = r.json()
        return [
            {
                "id": t.get("id"),
                "name": t.get("name"),
                "content": t.get("content", "")
            }
            for t in tickets
            if t.get("status") in (1, 2)  # 1=Nuevo, 2=En curso
        ]
