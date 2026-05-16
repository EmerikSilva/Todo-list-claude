"""
Tests E2E — Tareas (CRUD) y cronómetro.
Requiere backend en :8000 y frontend en :8501, usuario de prueba registrado.
"""
import time
import pytest
from playwright.sync_api import Page, expect
from conftest import wait_app, FRONTEND_URL, TEST_USER


# ─── Helpers ─────────────────────────────────────────────────────────────────

def create_todo_via_ui(page: Page, title: str, description: str = "", estimated_hours: float = 0):
    """Abre el expander de nueva tarea y crea una."""
    expander = page.get_by_text("➕ Nueva tarea")
    if expander.is_visible():
        expander.click()
        wait_app(page)

    page.get_by_label("Título de la tarea *").fill(title)
    if description:
        page.get_by_label("Descripción (opcional)").fill(description)
    if estimated_hours > 0:
        page.get_by_label("Estimación (h)").fill(str(estimated_hours))

    page.get_by_role("button", name="Crear tarea").click()
    wait_app(page)


# ─── Suite: creación de tareas ────────────────────────────────────────────────

class TestTodoCreation:

    def test_create_simple_todo(self, auth_page: Page):
        title = f"Test tarea simple {int(time.time())}"
        create_todo_via_ui(auth_page, title)
        expect(auth_page.get_by_text(title)).to_be_visible()

    def test_create_todo_with_description(self, auth_page: Page):
        title = f"Tarea con desc {int(time.time())}"
        create_todo_via_ui(auth_page, title, description="Mi descripción de prueba")
        expect(auth_page.get_by_text("Mi descripción de prueba")).to_be_visible()

    def test_create_todo_with_estimated_hours(self, auth_page: Page):
        title = f"Tarea estimada {int(time.time())}"
        create_todo_via_ui(auth_page, title, estimated_hours=2.5)
        # La barra de progreso aparece cuando hay estimación
        expect(auth_page.get_by_text(title)).to_be_visible()
        expect(auth_page.get_by_text("2.5h estimadas")).to_be_visible()

    def test_create_todo_empty_title_shows_error(self, auth_page: Page):
        expander = auth_page.get_by_text("➕ Nueva tarea")
        if expander.is_visible():
            expander.click()
            wait_app(auth_page)
        auth_page.get_by_role("button", name="Crear tarea").click()
        wait_app(auth_page)
        expect(auth_page.get_by_text("El título es obligatorio.")).to_be_visible()


# ─── Suite: completar y eliminar ─────────────────────────────────────────────

class TestTodoActions:

    def test_complete_todo(self, auth_page: Page):
        title = f"Para completar {int(time.time())}"
        create_todo_via_ui(auth_page, title)

        # La tarea aparece en Pendientes; la completamos
        auth_page.get_by_role("button", name="✔ Completar").first.click()
        wait_app(auth_page)

        # Debe aparecer en la sección Completadas
        expect(auth_page.get_by_text("✅ Completadas")).to_be_visible()

    def test_mark_completed_back_to_pending(self, auth_page: Page):
        title = f"Revertir {int(time.time())}"
        create_todo_via_ui(auth_page, title)

        auth_page.get_by_role("button", name="✔ Completar").first.click()
        wait_app(auth_page)
        auth_page.get_by_role("button", name="↩ Pendiente").first.click()
        wait_app(auth_page)

        expect(auth_page.get_by_text("📋 Pendientes")).to_be_visible()

    def test_delete_todo(self, auth_page: Page):
        title = f"Para borrar {int(time.time())}"
        create_todo_via_ui(auth_page, title)
        expect(auth_page.get_by_text(title)).to_be_visible()

        auth_page.get_by_role("button", name="🗑").first.click()
        wait_app(auth_page)

        expect(auth_page.get_by_text(title)).not_to_be_visible()


# ─── Suite: métricas del header ──────────────────────────────────────────────

class TestTodoMetrics:

    def test_metrics_visible(self, auth_page: Page):
        expect(auth_page.get_by_text("Total")).to_be_visible()
        expect(auth_page.get_by_text("Completadas")).to_be_visible()
        expect(auth_page.get_by_text("Pendientes")).to_be_visible()

    def test_pending_count_increases_on_new_todo(self, auth_page: Page):
        # Lee el valor actual de "Pendientes"
        pending_el = auth_page.locator("[data-testid='stMetricValue']").nth(2)
        before = int(pending_el.inner_text())

        create_todo_via_ui(auth_page, f"Métrica test {int(time.time())}")

        after = int(pending_el.inner_text())
        assert after == before + 1, f"Pendientes: esperado {before + 1}, obtenido {after}"


# ─── Suite: cronómetro ────────────────────────────────────────────────────────

class TestTimer:

    def test_start_timer_button_visible_on_pending_todo(self, auth_page: Page):
        create_todo_via_ui(auth_page, f"Timer test {int(time.time())}")
        expect(auth_page.get_by_role("button", name="▶ Iniciar").first).to_be_visible()

    def test_start_timer_shows_stop_button(self, auth_page: Page):
        create_todo_via_ui(auth_page, f"Timer start {int(time.time())}")
        auth_page.get_by_role("button", name="▶ Iniciar").first.click()
        wait_app(auth_page)
        expect(auth_page.get_by_role("button", name="⏹ Detener")).to_be_visible()

    def test_stop_timer_records_time(self, auth_page: Page):
        create_todo_via_ui(auth_page, f"Timer record {int(time.time())}")

        # Iniciar y dejar pasar ~2 s antes de parar
        auth_page.get_by_role("button", name="▶ Iniciar").first.click()
        wait_app(auth_page)
        auth_page.wait_for_timeout(2_500)

        auth_page.get_by_role("button", name="⏹ Detener").click()
        wait_app(auth_page)

        # Tras parar debe aparecer el texto "Total acumulado"
        expect(auth_page.get_by_text("Total acumulado:")).to_be_visible()

    def test_timer_not_visible_on_completed_todo(self, auth_page: Page):
        title = f"Timer done {int(time.time())}"
        create_todo_via_ui(auth_page, title)
        auth_page.get_by_role("button", name="✔ Completar").first.click()
        wait_app(auth_page)

        # En completadas no debe haber botón "▶ Iniciar"
        start_buttons = auth_page.get_by_role("button", name="▶ Iniciar")
        assert start_buttons.count() == 0, \
            "No debe haber botón de inicio de timer en tareas completadas"

    def test_progress_bar_visible_with_estimation(self, auth_page: Page):
        title = f"Timer+est {int(time.time())}"
        create_todo_via_ui(auth_page, title, estimated_hours=1.0)

        # Inicia y para el timer
        auth_page.get_by_role("button", name="▶ Iniciar").first.click()
        wait_app(auth_page)
        auth_page.wait_for_timeout(1_500)
        auth_page.get_by_role("button", name="⏹ Detener").click()
        wait_app(auth_page)

        # Debe aparecer el texto de progreso
        expect(auth_page.get_by_text("1.0h estimadas")).to_be_visible()
