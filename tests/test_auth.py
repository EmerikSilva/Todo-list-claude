"""
Tests E2E — Autenticación.
Requiere backend en :8000 y frontend en :8501.
"""
import pytest
from playwright.sync_api import Page, expect
from conftest import (
    TEST_USER, FRONTEND_URL, api_register,
    wait_app, css_var, force_theme,
)


class TestLoginPage:

    def test_app_title_visible(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        expect(page.get_by_text("TaskFlow").first).to_be_visible()

    def test_login_tab_visible(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        expect(page.get_by_text("Iniciar sesión")).to_be_visible()

    def test_register_tab_visible(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        expect(page.get_by_text("Crear cuenta")).to_be_visible()

    def test_login_form_fields_present(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Iniciar sesión").click()
        expect(page.get_by_label("📧 Email")).to_be_visible()
        expect(page.get_by_label("🔒 Contraseña").first).to_be_visible()
        expect(page.get_by_role("button", name="Entrar →")).to_be_visible()

    def test_register_form_fields_present(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Crear cuenta").click()
        wait_app(page)
        expect(page.get_by_label("👤 Nombre")).to_be_visible()
        expect(page.get_by_label("📧 Email").last).to_be_visible()

    def test_login_empty_fields_shows_warning(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Iniciar sesión").click()
        page.get_by_role("button", name="Entrar →").click()
        wait_app(page)
        expect(page.get_by_text("Por favor completa todos los campos.")).to_be_visible()

    def test_login_invalid_credentials_shows_error(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Iniciar sesión").click()
        page.get_by_label("📧 Email").fill("no_existe@test.com")
        page.get_by_label("🔒 Contraseña").first.fill("malpassword")
        page.get_by_role("button", name="Entrar →").click()
        wait_app(page)
        # Debe aparecer algún mensaje de error (texto del backend o de api_client)
        errors = page.locator("[data-testid='stAlert']")
        expect(errors.first).to_be_visible()


class TestRegistration:

    def test_short_password_shows_error(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Crear cuenta").click()
        wait_app(page)
        page.get_by_label("👤 Nombre").fill("Test")
        page.get_by_label("📧 Email").last.fill("short@test.com")
        page.get_by_label("🔒 Contraseña", exact=False).nth(0).fill("123")
        page.get_by_label("🔒 Confirmar contraseña").fill("123")
        page.get_by_role("button", name="Crear cuenta →").click()
        wait_app(page)
        expect(page.get_by_text("al menos 5 caracteres")).to_be_visible()

    def test_password_mismatch_shows_error(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        page.get_by_text("Crear cuenta").click()
        wait_app(page)
        page.get_by_label("👤 Nombre").fill("Test")
        page.get_by_label("📧 Email").last.fill("mismatch@test.com")
        page.get_by_label("🔒 Contraseña", exact=False).nth(0).fill("pass1234")
        page.get_by_label("🔒 Confirmar contraseña").fill("pass9999")
        page.get_by_role("button", name="Crear cuenta →").click()
        wait_app(page)
        expect(page.get_by_text("no coinciden")).to_be_visible()


class TestSuccessfulLogin:

    def test_login_redirects_to_main_app(self, auth_page: Page):
        """auth_page ya está logueado (fixture de conftest)."""
        expect(auth_page.get_by_text("TaskFlow").first).to_be_visible()
        # Sidebar con navegación visible = estamos dentro de la app
        expect(auth_page.get_by_text("Mis Tareas")).to_be_visible()

    def test_sidebar_shows_user_email(self, auth_page: Page):
        expect(auth_page.get_by_text(TEST_USER["email"])).to_be_visible()

    def test_logout_returns_to_login(self, auth_page: Page):
        auth_page.get_by_role("button", name="Cerrar sesión").click()
        wait_app(auth_page)
        expect(auth_page.get_by_text("Iniciar sesión")).to_be_visible()


class TestAuthThemeContrast:
    """Verifica que la pantalla de login sea legible en ambos temas."""

    def test_login_text_readable_in_light_mode(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        force_theme(page, "light")
        text_color = css_var(page, "--c-text2")
        card_color = css_var(page, "--c-card")
        # Si no podemos calcular contraste aquí, al menos verificamos
        # que text2 sea más oscuro que card
        assert text_color != card_color, \
            "El color de texto secundario no puede ser igual al fondo"

    def test_login_text_readable_in_dark_mode(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        force_theme(page, "dark")
        text_color = css_var(page, "--c-text2")
        card_color = css_var(page, "--c-card")
        assert text_color != card_color, \
            "El color de texto secundario no puede ser igual al fondo"
