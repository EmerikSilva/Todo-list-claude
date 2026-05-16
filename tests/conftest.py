import pytest
import requests
from playwright.sync_api import Page, expect

FRONTEND_URL = "http://localhost:8501"
API_URL      = "http://localhost:8000"

# Credenciales de prueba aisladas (no tocan usuarios reales)
TEST_USER = {
    "name":     "Playwright Tester",
    "email":    "playwright_e2e@test.com",
    "password": "test12345",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def api_register(user=None):
    """Registra el usuario de prueba vía API (idempotente)."""
    u = user or TEST_USER
    r = requests.post(f"{API_URL}/register", json=u)
    return r.status_code in (200, 400)  # 400 = ya existía


def css_var(page: Page, var: str) -> str:
    """Lee el valor de una variable CSS del :root del documento."""
    return page.evaluate(
        f"() => getComputedStyle(document.documentElement).getPropertyValue('{var}').trim()"
    )


def force_theme(page: Page, theme: str):
    """Simula que el JS detector ha detectado el tema indicado."""
    page.evaluate(
        f"() => document.documentElement.setAttribute('data-theme', '{theme}')"
    )


def wait_app(page: Page):
    """Espera que Streamlit haya terminado de renderizar."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


# ── Fixture: página nueva para cada test ─────────────────────────────────────

@pytest.fixture
def page(page: Page):
    page.set_default_timeout(15_000)
    return page


# ── Fixture: sesión autenticada ───────────────────────────────────────────────

@pytest.fixture
def auth_page(page: Page):
    """Devuelve una página ya logueada con el usuario de prueba."""
    api_register()
    page.goto(FRONTEND_URL)
    wait_app(page)

    page.get_by_text("Iniciar sesión").click()
    page.get_by_label("📧 Email").fill(TEST_USER["email"])
    page.get_by_label("🔒 Contraseña").first.fill(TEST_USER["password"])
    page.get_by_role("button", name="Entrar →").click()
    wait_app(page)

    return page
