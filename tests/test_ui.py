"""
Pruebas unitarias de la capa de interfaz gráfica (UI) y controlador de selección.
Valida el comportamiento de Signals & Slots, política FIFO y renderizado de componentes.
"""

import unittest
from PySide6.QtWidgets import QApplication

from src.core.enums import PokemonType
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.components.type_button import TypeButton
from src.ui.components.type_selector import TypeSelectorWidget
from src.ui.components.results_dashboard import ResultsDashboard
from src.ui.main_window import MainWindow

# Inicializar instancia única de QApplication para entornos de pruebas sin GUI activa
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestTypeSelectionController(unittest.TestCase):
    """Pruebas del controlador desacoplado de selección."""

    def setUp(self) -> None:
        self.controller = TypeSelectionController()

    def test_single_selection(self) -> None:
        """Seleccionar un tipo debe emitir la señal con una tupla de longitud 1."""
        emitted_tuples = []
        self.controller.selection_changed.connect(lambda t: emitted_tuples.append(t))

        self.controller.toggle_type(PokemonType.FIRE)
        self.assertEqual(len(emitted_tuples), 1)
        self.assertEqual(emitted_tuples[-1], (PokemonType.FIRE,))
        self.assertTrue(self.controller.is_selected(PokemonType.FIRE))
        self.assertEqual(self.controller.get_slot_index(PokemonType.FIRE), 1)

    def test_dual_selection(self) -> None:
        """Seleccionar un segundo tipo debe emitir una tupla de 2 tipos."""
        self.controller.toggle_type(PokemonType.STEEL)
        self.controller.toggle_type(PokemonType.FAIRY)

        self.assertEqual(
            self.controller.selected_types,
            (PokemonType.STEEL, PokemonType.FAIRY),
        )
        self.assertEqual(self.controller.get_slot_index(PokemonType.STEEL), 1)
        self.assertEqual(self.controller.get_slot_index(PokemonType.FAIRY), 2)

    def test_fifo_policy_on_third_selection(self) -> None:
        """
        Al seleccionar un tercer tipo con 2 ya activos, debe deseleccionar el primero
        (FIFO: First-In First-Out) y mantener el segundo + el nuevo.
        """
        self.controller.toggle_type(PokemonType.WATER)   # Slot 1
        self.controller.toggle_type(PokemonType.GROUND)  # Slot 2

        # Tercer clic: tipo PLANTA
        self.controller.toggle_type(PokemonType.GRASS)

        # AGUA debe haber salido; TIERRA pasa a Slot 1 y PLANTA queda en Slot 2
        self.assertEqual(
            self.controller.selected_types,
            (PokemonType.GROUND, PokemonType.GRASS),
        )
        self.assertFalse(self.controller.is_selected(PokemonType.WATER))
        self.assertEqual(self.controller.get_slot_index(PokemonType.GROUND), 1)
        self.assertEqual(self.controller.get_slot_index(PokemonType.GRASS), 2)

    def test_toggle_deselect(self) -> None:
        """Pulsar un tipo ya seleccionado debe deseleccionarlo inmediatamente."""
        self.controller.toggle_type(PokemonType.GHOST)
        self.controller.toggle_type(PokemonType.DARK)
        self.assertEqual(self.controller.count, 2)

        # Deseleccionar GHOST
        self.controller.toggle_type(PokemonType.GHOST)
        self.assertEqual(self.controller.selected_types, (PokemonType.DARK,))
        self.assertEqual(self.controller.count, 1)

    def test_clear_selection(self) -> None:
        """Limpiar la selección debe restablecer la lista y emitir las señales correspondientes."""
        cleared_emitted = []
        self.controller.selection_cleared.connect(lambda: cleared_emitted.append(True))

        self.controller.toggle_type(PokemonType.FIRE)
        self.controller.toggle_type(PokemonType.FLYING)
        self.controller.clear_selection()

        self.assertEqual(len(self.controller.selected_types), 0)
        self.assertEqual(len(cleared_emitted), 1)


class TestUIComponentsIntegration(unittest.TestCase):
    """Pruebas de inicialización y actualización de los componentes gráficos."""

    def setUp(self) -> None:
        self.controller = TypeSelectionController()

    def test_type_button_states(self) -> None:
        """Valida que TypeButton modifique sus estados visuales sin lanzar excepciones."""
        btn = TypeButton(PokemonType.STEEL)
        self.assertEqual(btn.pokemon_type, PokemonType.STEEL)
        self.assertFalse(btn.is_selected)

        # Simular selección en Slot 1
        btn.set_selection_state(is_selected=True, slot_index=1, is_dimmed=False)
        self.assertTrue(btn.is_selected)
        self.assertEqual(btn._slot_index, 1)
        self.assertFalse(btn._badge_label.isHidden())
        self.assertEqual(btn._badge_label.text(), "1º TIPO")

        # Simular atenuación (cuando otros 2 tipos están activos)
        btn.set_selection_state(is_selected=False, slot_index=None, is_dimmed=True)
        self.assertFalse(btn.is_selected)
        self.assertTrue(btn._badge_label.isHidden())

    def test_type_selector_widget(self) -> None:
        """Verifica que el TypeSelectorWidget inicialice los 19 botones y responda a clics."""
        selector = TypeSelectorWidget(self.controller)
        self.assertEqual(len(selector._buttons), 19)

        # Simular clic en Acero y Hada
        selector._on_button_clicked(PokemonType.STEEL)
        selector._on_button_clicked(PokemonType.FAIRY)

        self.assertEqual(self.controller.selected_types, (PokemonType.STEEL, PokemonType.FAIRY))
        self.assertTrue(selector._clear_btn.isEnabled())

    def test_results_dashboard_reactive_update(self) -> None:
        """Valida que el Dashboard maneje estados vacíos y vistas previas activas."""
        dashboard = ResultsDashboard()
        # Estado inicial vacío
        dashboard.update_selection(())
        self.assertEqual(dashboard._badges_layout.count(), 0)

        # Estado activo con doble tipo
        dashboard.update_selection((PokemonType.WATER, PokemonType.GROUND))
        self.assertEqual(dashboard._badges_layout.count(), 2)

    def test_type_chip_properties(self) -> None:
        """Verifica que TypeChip inicialice el nombre, dot y tooltip de forma correcta."""
        from src.ui.components.type_chip import TypeChip
        chip = TypeChip(PokemonType.FIRE, multiplier=2.0)
        self.assertEqual(chip.pokemon_type, PokemonType.FIRE)
        self.assertEqual(chip.multiplier, 2.0)
        self.assertIn("Fuego", chip.toolTip())
        self.assertIn("x2.0", chip.toolTip())

    def test_damage_group_section(self) -> None:
        """Verifica que DamageGroupSection albergue los TypeChips adecuados."""
        from src.ui.components.results_dashboard import DamageGroupSection
        section = DamageGroupSection(
            title="DEBILIDADES",
            multiplier_str="x2",
            badge_color="#EF4444",
            types=(PokemonType.FIRE, PokemonType.GROUND),
        )
        self.assertEqual(section.multiplier_str, "x2")
        self.assertEqual(len(section.types), 2)

    def test_dashboard_hides_empty_categories(self) -> None:
        """
        Regla UI: Si una categoría no tiene tipos, NO debe renderizarse.
        - Acero / Hada: NO tiene debilidades x4 -> el grupo x4 NO debe existir en el layout.
        - Agua / Tierra: TIENE debilidad x4 (Planta), pero NO tiene debilidades x2 ->
          el grupo x4 debe existir y el grupo x2 debe estar ausente.
        """
        from src.ui.components.results_dashboard import DamageGroupSection
        dashboard = ResultsDashboard()

        # 1. Evaluar Acero / Hada (Inmediato)
        dashboard._rebuild_content((PokemonType.STEEL, PokemonType.FAIRY))
        content_items = [
            dashboard._content_layout.itemAt(i).widget()
            for i in range(dashboard._content_layout.count())
            if dashboard._content_layout.itemAt(i) and dashboard._content_layout.itemAt(i).widget()
        ]
        sections = [w for w in content_items if isinstance(w, DamageGroupSection)]
        multipliers_rendered = [s.multiplier_str for s in sections]

        # Acero/Hada: no tiene x4, pero tiene x2, x0, x0.25, x0.5 y x1
        self.assertNotIn("x4", multipliers_rendered)
        self.assertIn("x2", multipliers_rendered)
        self.assertIn("x0", multipliers_rendered)
        self.assertIn("x0.25", multipliers_rendered)
        self.assertIn("x0.5", multipliers_rendered)
        self.assertIn("x1", multipliers_rendered)

        # 2. Evaluar Agua / Tierra
        dashboard._rebuild_content((PokemonType.WATER, PokemonType.GROUND))
        content_items_wg = [
            dashboard._content_layout.itemAt(i).widget()
            for i in range(dashboard._content_layout.count())
            if dashboard._content_layout.itemAt(i) and dashboard._content_layout.itemAt(i).widget()
        ]
        sections_wg = [w for w in content_items_wg if isinstance(w, DamageGroupSection)]
        multipliers_rendered_wg = [s.multiplier_str for s in sections_wg]

        # Agua/Tierra: TIENE x4 (Planta), NO tiene x2, TIENE x0 (Eléctrico), NO tiene x0.25, TIENE x0.5 y x1
        self.assertIn("x4", multipliers_rendered_wg)
        self.assertNotIn("x2", multipliers_rendered_wg)
        self.assertIn("x0", multipliers_rendered_wg)
        self.assertNotIn("x0.25", multipliers_rendered_wg)
        self.assertIn("x0.5", multipliers_rendered_wg)
        self.assertIn("x1", multipliers_rendered_wg)

    def test_memory_leak_free_cleanup(self) -> None:
        """Verifica que la función _clear_layout_recursively vacíe completamente el layout."""
        from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
        parent_widget = QWidget()
        layout = QVBoxLayout(parent_widget)
        lbl1 = QLabel("Test1", parent_widget)
        lbl2 = QLabel("Test2", parent_widget)
        layout.addWidget(lbl1)
        layout.addWidget(lbl2)
        self.assertEqual(layout.count(), 2)

        dashboard = ResultsDashboard()
        dashboard._clear_layout_recursively(layout)
        self.assertEqual(layout.count(), 0)

    def test_main_window_assembly(self) -> None:
        """Verifica que MainWindow ensamble todos los componentes y enlaces de señales."""
        window = MainWindow(auto_load_remote=False)
        self.assertIsNotNone(window.selector_widget)
        self.assertIsNotNone(window.results_dashboard)
        self.assertIsNotNone(window.controller)

        # Simular flujo completo a través del controlador
        window.controller.toggle_type(PokemonType.FIRE)
        self.assertIn("Fuego", window.statusBar().currentMessage())

        # Probar atajo Escape
        window.search_bar._input_field.setText("Pikachu")
        window._on_escape_pressed()
        self.assertEqual(window.search_bar._input_field.text(), "")
        self.assertEqual(window.controller.selected_types, ())

        window.close()


if __name__ == "__main__":
    unittest.main()
