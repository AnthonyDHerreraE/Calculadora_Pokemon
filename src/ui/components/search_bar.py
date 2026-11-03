"""
Barra de búsqueda inteligente conectada asíncronamente con PokéAPI.
Permite buscar Pokémon por nombre o ID, muestra un indicador de carga reactivo
y actualiza automáticamente los tipos en el TypeSelectionController.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
)

from src.core.pokeapi import PokeApiClient, PokemonData, PokemonSearchWorker
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
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
)


class SearchBar(QFrame):
    """
    Componente visual de búsqueda inteligente.
    Aloja el campo de entrada, botón de acción, indicador de carga asíncrono
    y el área de retroalimentación de estado.

    Señales:
        pokemon_selected (object): Emite el objeto PokemonData recuperado con éxito.
    """

    pokemon_selected = Signal(object)

    def __init__(
        self,
        controller: Optional[TypeSelectionController] = None,
        client: Optional[PokeApiClient] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.client = client or PokeApiClient()
        self._current_worker: Optional[PokemonSearchWorker] = None

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

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # 1. Fila de entrada de texto y botón de búsqueda
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(10)

        # Campo de texto moderno
        self._input_field = QLineEdit(self)
        self._input_field.setPlaceholderText("🔍 Buscar Pokémon (ej. Lucario, Gengar, 25)...")
        self._input_field.setClearButtonEnabled(True)
        self._input_field.setFixedHeight(40)
        self._input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 1.5px solid {COLOR_BORDER_SUBTLE};
                border-radius: 10px;
                padding: 0 14px;
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

        # Botón de búsqueda
        self._search_button = QPushButton("Buscar en PokéAPI", self)
        self._search_button.setFixedHeight(40)
        self._search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0 18px;
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

        # 2. Fila inferior de estado (Indicador de carga y mensajes de éxito/error)
        status_row = QHBoxLayout()
        status_row.setContentsMargins(4, 0, 4, 0)
        status_row.setSpacing(8)

        # Indicador de carga
        self._loading_label = QLabel("⏳ Conectando con PokéAPI...", self)
        self._loading_label.setStyleSheet(f"""
            color: {COLOR_ACCENT_HOVER};
            font-size: 11px;
            font-weight: 700;
        """)
        self._loading_label.setVisible(False)
        status_row.addWidget(self._loading_label)

        # Etiqueta de resultado o error
        self._status_label = QLabel("", self)
        self._status_label.setStyleSheet(f"font-size: 11px; font-weight: 600;")
        self._status_label.setVisible(False)
        status_row.addWidget(self._status_label)

        status_row.addStretch()
        main_layout.addLayout(status_row)

    def _on_text_changed(self, text: str) -> None:
        """Limpia el mensaje de error o estado anterior cuando el usuario modifica el texto."""
        if not text.strip():
            self._status_label.setVisible(False)

    def _on_search_triggered(self) -> None:
        """Inicia el proceso de búsqueda en segundo plano evitando bloqueos de UI."""
        query = self._input_field.text().strip()
        if not query:
            return

        # Si ya hay una consulta en ejecución, desconectar para evitar colisiones
        if self._current_worker and self._current_worker.isRunning():
            try:
                self._current_worker.pokemon_found.disconnect()
                self._current_worker.search_failed.disconnect()
            except RuntimeError:
                pass

        # Configurar estado visual de carga
        self._set_loading_state(True)
        self._status_label.setVisible(False)

        # Crear y arrancar el trabajador en QThread
        self._current_worker = PokemonSearchWorker(query, client=self.client, parent=self)
        self._current_worker.pokemon_found.connect(self._on_pokemon_found)
        self._current_worker.search_failed.connect(self._on_search_failed)
        self._current_worker.search_finished.connect(self._on_search_finished)
        self._current_worker.start()

    def _set_loading_state(self, is_loading: bool) -> None:
        """Activa o desactiva los controles de la interfaz durante la consulta."""
        self._input_field.setEnabled(not is_loading)
        self._search_button.setEnabled(not is_loading)
        self._loading_label.setVisible(is_loading)

    def _on_pokemon_found(self, pokemon_data: PokemonData) -> None:
        """Slot invocado en el hilo principal cuando la consulta es exitosa."""
        # Feedback visual de éxito
        self._status_label.setText(
            f"✓ {pokemon_data.display_title} cargado con éxito ({pokemon_data.types_display_es})"
        )
        self._status_label.setStyleSheet(f"""
            color: {COLOR_SUCCESS};
            font-size: 11px;
            font-weight: 700;
        """)
        self._status_label.setVisible(True)

        # Sincronización automática con el controlador
        if self.controller:
            self.controller.set_selection(pokemon_data.types)

        self.pokemon_selected.emit(pokemon_data)

    def _on_search_failed(self, error_message: str) -> None:
        """Slot invocado en el hilo principal ante 404 o fallos de red."""
        self._status_label.setText(f"✕ {error_message}")
        self._status_label.setStyleSheet(f"""
            color: {COLOR_DANGER};
            font-size: 11px;
            font-weight: 700;
        """)
        self._status_label.setVisible(True)

    def _on_search_finished(self) -> None:
        """Restaura los controles interactivos al finalizar la consulta."""
        self._set_loading_state(False)
        self._input_field.setFocus()
