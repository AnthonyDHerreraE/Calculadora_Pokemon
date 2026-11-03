"""
Pruebas unitarias para el cliente de PokéAPI y el componente SearchBar.
Valida normalización de nombres, mapeo de tipos a PokemonType,
manejo de excepciones de red y sincronización con TypeSelectionController.
"""

import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication

from src.core.enums import PokemonType
from src.core.pokeapi import (
    PokeApiClient,
    PokemonData,
    PokemonNotFoundError,
    PokeApiNetworkError,
    PokeApiError,
    PokemonSearchWorker,
)
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.components.search_bar import SearchBar

# Inicializar instancia única de QApplication para entorno headless
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestPokeApiClient(unittest.TestCase):
    """Pruebas del cliente de PokéAPI y normalización de consultas."""

    def setUp(self) -> None:
        self.client = PokeApiClient()

    def test_query_normalization(self) -> None:
        """Verifica la normalización de nombres especiales, espacios y diacríticos."""
        self.assertEqual(PokeApiClient.normalize_query("Pikachu"), "pikachu")
        self.assertEqual(PokeApiClient.normalize_query("Tapu Koko"), "tapu-koko")
        self.assertEqual(PokeApiClient.normalize_query("Mr. Mime"), "mr-mime")
        self.assertEqual(PokeApiClient.normalize_query("Flabébé"), "flabebe")
        self.assertEqual(PokeApiClient.normalize_query("25"), "25")
        self.assertEqual(PokeApiClient.normalize_query(150), "150")

    @patch("requests.Session.get")
    def test_fetch_pokemon_success_dual_type(self, mock_get) -> None:
        """Verifica el mapeo exitoso de un Pokémon con doble tipo (ej. Lucario)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 448,
            "name": "lucario",
            "types": [
                {"slot": 1, "type": {"name": "fighting"}},
                {"slot": 2, "type": {"name": "steel"}},
            ],
            "sprites": {"front_default": "http://img/lucario.png"},
        }
        mock_get.return_value = mock_response

        pokemon = self.client.fetch_pokemon("Lucario")
        self.assertEqual(pokemon.id, 448)
        self.assertEqual(pokemon.name, "lucario")
        self.assertEqual(pokemon.types, (PokemonType.FIGHTING, PokemonType.STEEL))
        self.assertEqual(pokemon.types_display_es, "Lucha / Acero")
        self.assertEqual(pokemon.display_title, "#0448 Lucario")

    @patch("requests.Session.get")
    def test_fetch_pokemon_404_not_found(self, mock_get) -> None:
        """Verifica que una respuesta 404 lance PokemonNotFoundError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(PokemonNotFoundError):
            self.client.fetch_pokemon("Agumon")

    def test_local_custom_pokedex_resolution(self) -> None:
        """Verifica que Pokémon de fan-games se resuelvan en memoria sin llamar a la red."""
        # Nucleon debe resolverse directamente desde custom_pokedex.json
        p_nucleon = self.client.fetch_pokemon("Nucleon")
        self.assertEqual(p_nucleon.name.lower(), "nucleon")
        self.assertEqual(p_nucleon.types, (PokemonType.NORMAL, PokemonType.NUCLEAR))
        self.assertTrue(p_nucleon.is_custom)

        # Urayne
        p_urayne = self.client.fetch_pokemon("urayne")
        self.assertEqual(p_urayne.types, (PokemonType.NUCLEAR,))

        # Baariette (Siniestro / Lucha)
        p_baariette = self.client.fetch_pokemon("baariette")
        self.assertEqual(p_baariette.types, (PokemonType.DARK, PokemonType.FIGHTING))

    @patch("requests.Session.get")
    def test_unknown_pokemon_404_handling(self, mock_get) -> None:
        """Verifica que un Pokémon inexistente lance PokemonNotFoundError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(PokemonNotFoundError) as ctx:
            self.client.fetch_pokemon("InexistenteFakemon")
        self.assertIn("InexistenteFakemon", str(ctx.exception))

    @patch("requests.Session.get")
    def test_fetch_pokemon_timeout(self, mock_get) -> None:
        """Verifica que un timeout lance PokeApiNetworkError."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        with self.assertRaises(PokeApiNetworkError):
            self.client.fetch_pokemon("Pikachu")

    @patch("requests.Session.get")
    def test_in_memory_cache(self, mock_get) -> None:
        """Verifica que consultas repetidas no disparen peticiones HTTP adicionales."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 25,
            "name": "pikachu",
            "types": [{"slot": 1, "type": {"name": "electric"}}],
        }
        mock_get.return_value = mock_response

        # Primera consulta (va a la red)
        p1 = self.client.fetch_pokemon("pikachu")
        # Segunda consulta (debe salir de caché)
        p2 = self.client.fetch_pokemon("pikachu")

        self.assertIs(p1, p2)
        mock_get.assert_called_once()


class TestSearchBarIntegration(unittest.TestCase):
    """Pruebas del componente visual SearchBar y su sincronización con el controlador."""

    def setUp(self) -> None:
        self.controller = TypeSelectionController()
        self.search_bar = SearchBar(controller=self.controller, auto_load_remote=False)

    def tearDown(self) -> None:
        self.search_bar.stop_workers()

    def test_search_bar_success_updates_controller(self) -> None:
        """
        Al recibir un Pokémon encontrado, el SearchBar debe actualizar
        la selección en el TypeSelectionController y mostrar mensaje de éxito.
        """
        pokemon_data = PokemonData(
            id=94,
            name="gengar",
            types=(PokemonType.GHOST, PokemonType.POISON),
        )

        self.search_bar._on_pokemon_found(pokemon_data)

        # El controlador debe reflejar Fantasma y Veneno
        self.assertEqual(
            self.controller.selected_types,
            (PokemonType.GHOST, PokemonType.POISON),
        )
        self.assertFalse(self.search_bar._status_label.isHidden())
        self.assertIn("Gengar", self.search_bar._status_label.text())

    def test_search_bar_failure_feedback(self) -> None:
        """Al ocurrir un fallo, debe mostrar el mensaje de error."""
        self.search_bar._on_search_failed("No se encontró el Pokémon")
        self.assertFalse(self.search_bar._status_label.isHidden())
        self.assertIn("No se encontró el Pokémon", self.search_bar._status_label.text())

    def test_search_bar_loading_state(self) -> None:
        """Verifica que el estado de carga bloquee los inputs e ilumine el label de carga."""
        self.search_bar._set_loading_state(True)
        self.assertFalse(self.search_bar._input_field.isEnabled())
        self.assertFalse(self.search_bar._search_button.isEnabled())
        self.assertFalse(self.search_bar._loading_label.isHidden())

        self.search_bar._set_loading_state(False)
        self.assertTrue(self.search_bar._input_field.isEnabled())
        self.assertTrue(self.search_bar._search_button.isEnabled())
        self.assertTrue(self.search_bar._loading_label.isHidden())

    def test_search_bar_local_resolution_no_spinner(self) -> None:
        """
        Al buscar un Pokémon presente en la Pokédex local (ej. Nucleon),
        debe resolverse instantáneamente sin mostrar el indicador de carga.
        """
        self.search_bar._input_field.setText("Nucleon")
        self.search_bar._on_search_triggered()

        # No debe haber mostrado el spinner
        self.assertTrue(self.search_bar._loading_label.isHidden())
        # El controlador debe reflejar la selección de inmediato
        self.assertEqual(
            self.controller.selected_types,
            (PokemonType.NORMAL, PokemonType.NUCLEAR),
        )
        self.assertFalse(self.search_bar._status_label.isHidden())
        self.assertIn("Nucleon", self.search_bar._status_label.text())

    def test_search_bar_completer_initialization(self) -> None:
        """Verifica que el completer se configure con nombres de la Pokédex local."""
        known = self.search_bar._known_names
        self.assertIn("Nucleon", known)
        self.assertIn("Urayne", known)
        self.assertIn("Baariette", known)

        # Verificar que el modelo del QCompleter contenga estos datos
        model_strings = self.search_bar._completer_model.stringList()
        self.assertIn("Nucleon", model_strings)

    def test_search_bar_completer_activation_triggers_search(self) -> None:
        """
        Al seleccionar una sugerencia (clic o Enter en popup),
        debe disparar la búsqueda de inmediato sin segundo Enter.
        """
        self.search_bar._on_suggestion_activated("Urayne")
        self.assertEqual(self.search_bar._input_field.text(), "Urayne")
        self.assertEqual(self.controller.selected_types, (PokemonType.NUCLEAR,))

    def test_search_bar_remote_names_merge(self) -> None:
        """Verifica la fusión dinámica de nombres oficiales sin duplicados."""
        initial_count = len(self.search_bar._known_names)
        self.search_bar._on_remote_names_loaded(["Pikachu", "Charizard", "Nucleon"])
        self.assertIn("Pikachu", self.search_bar._known_names)
        self.assertIn("Charizard", self.search_bar._known_names)
        # Nucleon no debe estar duplicado
        self.assertEqual(self.search_bar._known_names.count("Nucleon"), 1)
        self.assertEqual(len(self.search_bar._known_names), initial_count + 2)

    def test_search_bar_focus_and_select_all(self) -> None:
        """Verifica el comportamiento del método para atajos de teclado."""
        self.search_bar._input_field.setText("Gengar")
        self.search_bar.focus_and_select_all()
        self.assertEqual(self.search_bar._input_field.selectedText(), "Gengar")


if __name__ == "__main__":
    unittest.main()
