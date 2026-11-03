"""
Componente visual TypeChip para representar tipos elementales atacantes.
Diseño ligero tipo píldora (pill badge) con indicador cromático, tipografía nítida
y micro-interacciones hover.
"""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from src.core.enums import PokemonType
from src.ui.styles import hex_to_rgba, COLOR_TEXT_PRIMARY


class TypeChip(QFrame):
    """
    Píldora gráfica ligera que representa un tipo atacante específico.
    Utiliza el color oficial del tipo para su dot indicador y su borde sutil.
    """

    def __init__(
        self,
        pokemon_type: PokemonType,
        multiplier: Optional[float] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.pokemon_type = pokemon_type
        self.multiplier = multiplier

        self.setFixedHeight(30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_ui()
        self._apply_style(hovered=False)

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 12, 2)
        layout.setSpacing(8)

        # 1. Dot indicador de color
        self._dot = QLabel(self)
        self._dot.setFixedSize(8, 8)
        self._dot.setStyleSheet(
            f"background-color: {self.pokemon_type.hex_color}; border-radius: 4px;"
        )
        layout.addWidget(self._dot)

        # 2. Nombre del tipo en español
        self._name_label = QLabel(self.pokemon_type.display_name_es, self)
        self._name_label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;"
        )
        layout.addWidget(self._name_label)

        # Tooltip informativo
        mult_str = f" (Daño x{self.multiplier})" if self.multiplier is not None else ""
        self.setToolTip(f"Tipo Atacante: {self.pokemon_type.display_name_es}{mult_str}")

    def _apply_style(self, hovered: bool) -> None:
        hex_color = self.pokemon_type.hex_color
        if hovered:
            bg_color = hex_to_rgba(hex_color, 0.28)
            border_color = hex_color
        else:
            bg_color = hex_to_rgba(hex_color, 0.14)
            border_color = hex_to_rgba(hex_color, 0.40)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: 14px;
            }}
        """)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._apply_style(hovered=True)

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._apply_style(hovered=False)
