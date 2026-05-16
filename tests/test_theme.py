"""
Tests E2E — Modo claro y oscuro.

Verifican que las variables CSS se apliquen correctamente y que el contraste
sea suficiente en ambos modos.  No dependen de Streamlit corriendo: solo
necesitan que el frontend esté en http://localhost:8501.
"""
import pytest
from playwright.sync_api import Page
from conftest import css_var, force_theme, wait_app, FRONTEND_URL


def hex_brightness(hex_color: str) -> float:
    """Calcula el brillo perceptual (0–255) de un color hexadecimal."""
    h = hex_color.strip("#")
    if len(h) != 6:
        return -1
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """
    Calcula el ratio de contraste WCAG entre dos colores.
    Retorna un valor entre 1 y 21 (>=4.5 aprueba AA, >=7 aprueba AAA).
    """
    def relative_luminance(hex_c):
        h = hex_c.strip("#")
        vals = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in vals]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ─── Modo claro ───────────────────────────────────────────────────────────────

class TestLightMode:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        force_theme(page, "light")

    def test_card_background_is_white(self, page: Page):
        val = css_var(page, "--c-card")
        assert val == "#ffffff", f"Fondo de tarjeta en claro debe ser #ffffff, obtenido: {val!r}"

    def test_primary_text_is_dark(self, page: Page):
        val = css_var(page, "--c-text")
        assert val == "#0f172a", f"Texto primario en claro debe ser #0f172a, obtenido: {val!r}"

    def test_secondary_text_is_readable(self, page: Page):
        fg = css_var(page, "--c-text2")
        bg = css_var(page, "--c-card")
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, (
            f"Contraste WCAG AA no cumplido en modo claro: "
            f"--c-text2={fg} sobre --c-card={bg} → ratio={ratio:.2f} (mínimo 4.5)"
        )

    def test_tertiary_text_is_readable(self, page: Page):
        fg = css_var(page, "--c-text3")
        bg = css_var(page, "--c-card")
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 3.0, (
            f"--c-text3={fg} sobre --c-card={bg} → ratio={ratio:.2f} (mínimo 3.0)"
        )

    def test_dark_variables_are_not_active(self, page: Page):
        """Verifica que data-theme='dark' NO esté presente en modo claro."""
        theme = page.evaluate(
            "() => document.documentElement.getAttribute('data-theme')"
        )
        assert theme == "light", f"data-theme debe ser 'light', es: {theme!r}"

    def test_input_background_is_light(self, page: Page):
        val = css_var(page, "--c-input")
        brightness = hex_brightness(val)
        assert brightness > 200, (
            f"Fondo de input en claro debería ser claro (>200), obtenido: {val!r} → {brightness:.0f}"
        )


# ─── Modo oscuro ─────────────────────────────────────────────────────────────

class TestDarkMode:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)
        force_theme(page, "dark")

    def test_card_background_is_dark(self, page: Page):
        val = css_var(page, "--c-card")
        assert val == "#1e293b", f"Fondo de tarjeta en oscuro debe ser #1e293b, obtenido: {val!r}"

    def test_primary_text_is_light(self, page: Page):
        val = css_var(page, "--c-text")
        assert val == "#f1f5f9", f"Texto primario en oscuro debe ser #f1f5f9, obtenido: {val!r}"

    def test_secondary_text_is_readable(self, page: Page):
        fg = css_var(page, "--c-text2")
        bg = css_var(page, "--c-card")
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, (
            f"Contraste WCAG AA no cumplido en modo oscuro: "
            f"--c-text2={fg} sobre --c-card={bg} → ratio={ratio:.2f} (mínimo 4.5)"
        )

    def test_tertiary_text_is_readable(self, page: Page):
        fg = css_var(page, "--c-text3")
        bg = css_var(page, "--c-card")
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 3.0, (
            f"--c-text3={fg} sobre --c-card={bg} → ratio={ratio:.2f} (mínimo 3.0)"
        )

    def test_light_card_color_not_active(self, page: Page):
        val = css_var(page, "--c-card")
        brightness = hex_brightness(val)
        assert brightness < 100, (
            f"Fondo de tarjeta en modo oscuro debería ser oscuro (<100), obtenido: {val!r} → {brightness:.0f}"
        )

    def test_input_background_is_dark(self, page: Page):
        val = css_var(page, "--c-input")
        brightness = hex_brightness(val)
        assert brightness < 128, (
            f"Fondo de input en oscuro debería ser oscuro (<128), obtenido: {val!r} → {brightness:.0f}"
        )


# ─── Cambio dinámico de tema ──────────────────────────────────────────────────

class TestThemeSwitching:

    def test_switching_light_to_dark_updates_variables(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)

        force_theme(page, "light")
        card_light = css_var(page, "--c-card")

        force_theme(page, "dark")
        card_dark = css_var(page, "--c-card")

        assert card_light != card_dark, (
            "El fondo de tarjeta debe cambiar al alternar entre temas. "
            f"Claro={card_light!r}, Oscuro={card_dark!r}"
        )

    def test_switching_dark_to_light_restores_variables(self, page: Page):
        page.goto(FRONTEND_URL)
        wait_app(page)

        force_theme(page, "dark")
        force_theme(page, "light")

        val = css_var(page, "--c-text")
        assert val == "#0f172a", (
            f"Texto primario debe volver a #0f172a al restaurar modo claro, obtenido: {val!r}"
        )
