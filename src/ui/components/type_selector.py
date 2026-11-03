"""
Contenedor del selector interactivo de tipos Pokémon.
Organiza los 18 tipos en una cuadrícula responsiva (3x6) y gestiona la interacción
visual mediante Signals & Slots conectados al TypeSelectionController.
"""

from typing import Dict, Optional, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from src.core.enums import PokemonType
from src.core.constants import ALL_TYPES
from src.ui.components.type_button import TypeButton
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.styles import COLOR_BORDER_SUBTLE, COLOR_ACCENT, COLOR_TEXT_MUTED


class TypeSelectorWidget(QFrame):
    """
    Panel superior de la interfaz que alberga la cuadrícula de los 18 tipos Pokémon,
    el contador reactivo de selección y el botón de reinicio.
    """

    type_selected_signal = Signal(PokemonType)

    def __init__(
        self,
        controller: TypeSelectionController,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self._buttons: Dict[PokemonType, TypeButton] = {}

        self.setObjectName("TypeSelectorCard")
        self.setProperty("class", "CardPanel")
        self.setFixedWidth(464)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        # 1. Barra Superior del Selector (Encabezado, Contador y Botón Limpiar)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)

        # Título de la sección con icono sutil
        self._title_label = QLabel("⚡ TIPOS DEFENSORES", self)
        self._title_label.setObjectName("SectionTitle")
        top_bar.addWidget(self._title_label)

        # Contador de tipos seleccionados [0/2]
        self._count_badge = QLabel("0/2", self)
        self._count_badge.setObjectName("BadgeCount")
        top_bar.addWidget(self._count_badge)

        top_bar.addStretch()

        # Botón para limpiar / restablecer selección
        self._clear_btn = QPushButton("✕ Limpiar", self)
        self._clear_btn.setObjectName("ActionButton")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setEnabled(False)
        self._clear_btn.clicked.connect(self.controller.clear_selection)
        top_bar.addWidget(self._clear_btn)

        layout.addLayout(top_bar)

        # 2. Cuadrícula compacta de 18 tipos (6 filas x 3 columnas)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 4, 0, 0)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        columns = 3
        for index, pokemon_type in enumerate(ALL_TYPES):
            row = index // columns
            col = index % columns

            btn = TypeButton(pokemon_type, self)
            btn.clicked.connect(lambda checked=False, t=pokemon_type: self._on_button_clicked(t))
            self._buttons[pokemon_type] = btn
            grid_layout.addWidget(btn, row, col)

        layout.addLayout(grid_layout)

    def _connect_signals(self) -> None:
        """Conecta las señales del controlador con los slots de actualización visual."""
        self.controller.selection_changed.connect(self._on_selection_changed)

    def _on_button_clicked(self, pokemon_type: PokemonType) -> None:
        """Manejador de click del usuario, delega el cambio de estado al controlador."""
        self.controller.toggle_type(pokemon_type)
        self.type_selected_signal.emit(pokemon_type)

    def _on_selection_changed(self, selected_types: Tuple[PokemonType, ...]) -> None:
        """
        Slot invocado automáticamente cuando el controlador emite un cambio de selección.
        Actualiza el estado visual de los 18 botones, el badge contador y el botón limpiar.
        """
        count = len(selected_types)
        is_max = count >= 2

        # Actualizar estado y opacidad de cada botón
        for ptype, btn in self._buttons.items():
            if ptype in selected_types:
                slot_index = selected_types.index(ptype) + 1
                btn.set_selection_state(is_selected=True, slot_index=slot_index, is_dimmed=False)
            else:
                # Si ya se alcanzaron 2 tipos, atenuar ligeramente los no seleccionados
                btn.set_selection_state(is_selected=False, slot_index=None, is_dimmed=is_max)

        # Actualizar contador y botón limpiar
        if count == 0:
            self._count_badge.setText("0/2")
            self._clear_btn.setEnabled(False)
        elif count == 1:
            self._count_badge.setText("1/2 ACTIVO")
            self._clear_btn.setEnabled(True)
        else:
            self._count_badge.setText("2/2 MÁX")
            self._clear_btn.setEnabled(True)
