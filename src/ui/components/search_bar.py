"""
Barra de búsqueda inteligente con autocompletado reactivo (QCompleter)
y carga en segundo plano de nombres oficiales y de fan-games.
"""

from typing import List, Optional
import requests
from PySide6.QtCore import Qt, Signal, QStringListModel, QThread
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QCompleter,
)

from src.core.pokeapi import HybridPokemonClient, PokemonData, PokemonSearchWorker
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_SURFACE,
    COLOR_BG_ELEVATED,
    COLOR_BORDER_SUBTLE,
    COLOR_BORDER_STRONG,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
)


class PokemonNamesLoaderWorker(QThread):
    """
    Hilo de trabajo ligero para descargar la lista completa de nombres oficiales
    desde PokéAPI al arrancar la aplicación sin bloquear la interfaz.
    """

    names_loaded = Signal(list)

    def run(self) -> None:
        try:
            url = "https://pokeapi.co/api/v2/pokemon?limit=1500"
            response = requests.get(
                url,
                timeout=8.0,
                headers={"User-Agent": "PokemonTypeCalculator-PySide6/1.0"},
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                official_names = [p["name"].capitalize() for p in results if "name" in p]
                self.names_loaded.emit(official_names)
        except Exception:
            # En caso de no tener conexión, simplemente se mantiene la lista local
            pass


class SearchBar(QFrame):
    """
    Barra de búsqueda moderna con autocompletado en tiempo real (QCompleter),
    soporte para atajos de teclado y resolución instantánea de sugerencias.

    Señales:
        pokemon_selected (object): Emite el objeto PokemonData recuperado con éxito.
    """

    pokemon_selected = Signal(object)

    def __init__(
        self,
        controller: Optional[TypeSelectionController] = None,
        client: Optional[HybridPokemonClient] = None,
        parent: Optional[QWidget] = None,
        auto_load_remote: bool = True,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.client = client or HybridPokemonClient()
        self._current_worker: Optional[PokemonSearchWorker] = None
        self._names_loader: Optional[PokemonNamesLoaderWorker] = None

        self.setObjectName("SearchBarCard")
        self.setProperty("class", "CardPanel")
        self.setFixedWidth(464)
        self.setStyleSheet(f"""
            QFrame#SearchBarCard {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER_SUBTLE};
                border-radius: 12px;
            }}
        """)

        # 1. Configuración de datos del autocompletado
        self._completer_model = QStringListModel(self)
        self._known_names: List[str] = self._get_initial_local_names()
        self._completer_model.setStringList(self._known_names)

        self._setup_ui()
        self._setup_completer()

        # 2. Descarga de nombres remotos en segundo plano
        if auto_load_remote:
            self._start_remote_names_loader()

    def _get_initial_local_names(self) -> List[str]:
        """Obtiene las claves iniciales del custom_pokedex.json para sugerencias inmediatas."""
        local_dict = getattr(self.client, "_custom_pokedex", {})
        return sorted([name.capitalize() for name in local_dict.keys()])

    def _start_remote_names_loader(self) -> None:
        """Inicia el worker en segundo plano para poblar el autocompletado con los 1000+ Pokémon."""
        self._names_loader = PokemonNamesLoaderWorker(self)
        self._names_loader.names_loaded.connect(self._on_remote_names_loaded)
        self._names_loader.start()

    def _on_remote_names_loaded(self, remote_names: List[str]) -> None:
        """Fusiona los nombres oficiales con los de fan-games preservando orden y unicidad."""
        combined = list(dict.fromkeys(self._known_names + remote_names))
        self._known_names = combined
        self._completer_model.setStringList(self._known_names)

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Fila de entrada de texto y botón de búsqueda
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(10)

        # Campo de texto moderno
        self._input_field = QLineEdit(self)
        self._input_field.setPlaceholderText("🔍 Buscar Pokémon (Ctrl+F)...")
        self._input_field.setClearButtonEnabled(True)
        self._input_field.setFixedHeight(40)
        self._input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 1.5px solid {COLOR_BORDER_SUBTLE};
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
                selection-background-color: {COLOR_ACCENT};
            }}
            QLineEdit:focus {{
                border-color: {COLOR_ACCENT};
                background-color: {COLOR_BG_ELEVATED};
            }}
            QLineEdit:disabled {{
                color: {COLOR_TEXT_MUTED};
            }}
        """)
        self._input_field.returnPressed.connect(self._on_search_triggered)
        self._input_field.textChanged.connect(self._on_text_changed)
        input_row.addWidget(self._input_field, 1)

        # Botón de búsqueda compacto
        self._search_button = QPushButton("Buscar", self)
        self._search_button.setFixedHeight(40)
        self._search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #4F46E5;
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_MUTED};
            }}
        """)
        self._search_button.clicked.connect(self._on_search_triggered)
        input_row.addWidget(self._search_button)

        main_layout.addLayout(input_row)

        # Fila inferior de estado (Indicador de carga y mensajes de éxito/error)
        status_row = QHBoxLayout()
        status_row.setContentsMargins(4, 0, 4, 0)
        status_row.setSpacing(8)

        self._loading_label = QLabel("⏳ Conectando con PokéAPI...", self)
        self._loading_label.setStyleSheet(f"""
            color: {COLOR_ACCENT_HOVER};
            font-size: 11px;
            font-weight: 700;
        """)
        self._loading_label.setVisible(False)
        status_row.addWidget(self._loading_label)

        self._status_label = QLabel("", self)
        self._status_label.setStyleSheet("font-size: 11px; font-weight: 600;")
        self._status_label.setVisible(False)
        status_row.addWidget(self._status_label)

        status_row.addStretch()
        main_layout.addLayout(status_row)

    def _setup_completer(self) -> None:
        """Configura el QCompleter con filtrado flexible e interactividad directa."""
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setMaxVisibleItems(8)

        # Estilización Dark Theme del popup de sugerencias
        popup = self._completer.popup()
        popup.setStyleSheet(f"""
            QListView {{
                background-color: {COLOR_BG_CARD};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER_STRONG};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {COLOR_ACCENT};
                selection-color: #FFFFFF;
                outline: none;
                font-size: 12px;
            }}
            QListView::item {{
                height: 26px;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QListView::item:hover {{
                background-color: {COLOR_BG_ELEVATED};
            }}
        """)

        # Asignar completer al campo de texto
        self._input_field.setCompleter(self._completer)

        # UX: Al seleccionar una sugerencia (clic o flechas+Enter), disparar búsqueda de inmediato
        self._completer.activated.connect(self._on_suggestion_activated)

    def _on_suggestion_activated(self, text: str) -> None:
        """Slot que dispara la búsqueda instantáneamente sin requerir pulsar Enter dos veces."""
        self._input_field.setText(text)
        self._on_search_triggered()

    def focus_and_select_all(self) -> None:
        """Atajo de teclado: Enfoca el campo y selecciona todo el texto actual."""
        self._input_field.setFocus()
        self._input_field.selectAll()

    def clear_input(self) -> None:
        """Atajo de teclado (Esc): Limpia el texto y oculta mensajes anteriores."""
        self._input_field.clear()
        self._status_label.setVisible(False)

    def _on_text_changed(self, text: str) -> None:
        if not text.strip():
            self._status_label.setVisible(False)

    def _on_search_triggered(self) -> None:
        """Inicia el proceso de búsqueda con resolución local inmediata (0ms) o fallback a PokéAPI."""
        query = self._input_field.text().strip()
        if not query:
            return

        # 1. Optimización UI: Resolución síncrona inmediata si existe en la Pokédex local
        if hasattr(self.client, "get_local_pokemon"):
            local_pokemon = self.client.get_local_pokemon(query)
            if local_pokemon is not None:
                self._status_label.setVisible(False)
                self._set_loading_state(False)
                self._on_pokemon_found(local_pokemon)
                return

        # 2. Si no es local, consultar PokéAPI en hilo secundario (QThread)
        if self._current_worker and self._current_worker.isRunning():
            try:
                self._current_worker.pokemon_found.disconnect()
                self._current_worker.search_failed.disconnect()
            except RuntimeError:
                pass

        self._set_loading_state(True)
        self._status_label.setVisible(False)

        self._current_worker = PokemonSearchWorker(query, client=self.client, parent=self)
        self._current_worker.pokemon_found.connect(self._on_pokemon_found)
        self._current_worker.search_failed.connect(self._on_search_failed)
        self._current_worker.search_finished.connect(self._on_search_finished)
        self._current_worker.start()

    def _set_loading_state(self, is_loading: bool) -> None:
        self._input_field.setEnabled(not is_loading)
        self._search_button.setEnabled(not is_loading)
        self._loading_label.setVisible(is_loading)

    def _on_pokemon_found(self, pokemon_data: PokemonData) -> None:
        self._status_label.setText(
            f"✓ {pokemon_data.display_title} ({pokemon_data.types_display_es})"
        )
        self._status_label.setStyleSheet(f"""
            color: {COLOR_SUCCESS};
            font-size: 11px;
            font-weight: 700;
        """)
        self._status_label.setVisible(True)

        if self.controller:
            self.controller.set_selection(pokemon_data.types)

        self.pokemon_selected.emit(pokemon_data)

    def _on_search_failed(self, error_message: str) -> None:
        self._status_label.setText(f"✕ {error_message}")
        self._status_label.setStyleSheet(f"""
            color: {COLOR_DANGER};
            font-size: 11px;
            font-weight: 700;
        """)
        self._status_label.setVisible(True)

    def _on_search_finished(self) -> None:
        self._set_loading_state(False)
        self._input_field.setFocus()

    def stop_workers(self) -> None:
        """Detiene de forma segura los hilos de fondo antes de destruir el componente."""
        if self._names_loader is not None and self._names_loader.isRunning():
            self._names_loader.quit()
            self._names_loader.wait(500)
        if self._current_worker is not None and self._current_worker.isRunning():
            self._current_worker.quit()
            self._current_worker.wait(500)

    def closeEvent(self, event) -> None:
        self.stop_workers()
        super().closeEvent(event)
