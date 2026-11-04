"""
Componente visual TypeChip para representar tipos elementales (atacantes o defensores).
Diseño ligero tipo píldora (pill badge) con indicador cromático, tipografía nítida,
soporte para subtítulo enriquecido (desglose defensivo y fuente STAB) y micro-interacciones hover.
"""

from typing import Optional, Tuple
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget

from src.core.enums import PokemonType
from src.ui.styles import hex_to_rgba, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY


class TypeChip(QFrame):
    """
    Píldora gráfica ligera que representa un tipo elemental.
    Utiliza el color oficial del tipo para su dot indicador y su borde sutil.
    Soporta la indicación visual de subtítulos enriquecidos (HTML) o fuente atacante STAB.
    """

    def __init__(
        self,
        pokemon_type: PokemonType,
        multiplier: Optional[float] = None,
        source_types: Optional[Tuple[PokemonType, ...]] = None,
        subtitle_rich_text: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.pokemon_type = pokemon_type
        self.multiplier = multiplier
        self.source_types = source_types
        self.subtitle_rich_text = subtitle_rich_text

        # Ajuste de altura según presencia de subtítulo (defensivo enriquecido u ofensivo)
        if self.source_types or self.subtitle_rich_text:
            self.setFixedHeight(40)
        else:
            self.setFixedHeight(30)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_ui()
        self._apply_style(hovered=False)

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        v_pad = 3 if (self.source_types or self.subtitle_rich_text) else 2
        layout.setContentsMargins(10, v_pad, 12, v_pad)
        layout.setSpacing(8)

        # 1. Dot indicador de color del tipo
        self._dot = QLabel(self)
        self._dot.setFixedSize(8, 8)
        self._dot.setStyleSheet(
            f"background-color: {self.pokemon_type.hex_color}; border-radius: 4px;"
        )
        layout.addWidget(self._dot)

        # 2. Bloque de texto
        if self.subtitle_rich_text:
            text_container = QVBoxLayout()
            text_container.setContentsMargins(0, 0, 0, 0)
            text_container.setSpacing(0)

            self._name_label = QLabel(self.pokemon_type.display_name_es, self)
            self._name_label.setStyleSheet(
                f"font-size: 11px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;"
            )
            text_container.addWidget(self._name_label)

            self._subtitle_label = QLabel(self)
            self._subtitle_label.setTextFormat(Qt.TextFormat.RichText)
            self._subtitle_label.setText(self.subtitle_rich_text)
            self._subtitle_label.setStyleSheet(
                "font-size: 9px; font-weight: 700; background: transparent; border: none;"
            )
            text_container.addWidget(self._subtitle_label)

            layout.addLayout(text_container)
        elif self.source_types:
            text_container = QVBoxLayout()
            text_container.setContentsMargins(0, 0, 0, 0)
            text_container.setSpacing(0)

            self._name_label = QLabel(self.pokemon_type.display_name_es, self)
            self._name_label.setStyleSheet(
                f"font-size: 11px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;"
            )
            text_container.addWidget(self._name_label)

            if len(self.source_types) == 1:
                st = self.source_types[0]
                via_str = f"vía {st.display_name_es}"
                sub_color = st.hex_color
            else:
                names = " / ".join(t.display_name_es for t in self.source_types)
                via_str = f"vía {names}"
                sub_color = COLOR_TEXT_SECONDARY

            self._source_label = QLabel(via_str, self)
            self._source_label.setStyleSheet(
                f"font-size: 9px; font-weight: 700; color: {sub_color}; background: transparent; border: none;"
            )
            text_container.addWidget(self._source_label)

            layout.addLayout(text_container)
        else:
            self._name_label = QLabel(self.pokemon_type.display_name_es, self)
            self._name_label.setStyleSheet(
                f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;"
            )
            layout.addWidget(self._name_label)

        # Tooltip informativo contextualizado
        mult_str = f" (Daño x{self.multiplier})" if self.multiplier is not None else ""
        if self.subtitle_rich_text:
            clean_sub = re.sub(r"<[^>]+>", "", self.subtitle_rich_text)
            self.setToolTip(f"Tipo: {self.pokemon_type.display_name_es}{mult_str}\nDesglose: {clean_sub}")
        elif self.source_types:
            via_names = " / ".join(t.display_name_es for t in self.source_types)
            self.setToolTip(f"Defensor: {self.pokemon_type.display_name_es}{mult_str}\nFuente STAB: {via_names}")
        else:
            self.setToolTip(f"Tipo: {self.pokemon_type.display_name_es}{mult_str}")

    def _apply_style(self, hovered: bool) -> None:
        hex_color = self.pokemon_type.hex_color
        if hovered:
            bg_color = hex_to_rgba(hex_color, 0.28)
            border_color = hex_color
        else:
            bg_color = hex_to_rgba(hex_color, 0.14)
            border_color = hex_to_rgba(hex_color, 0.40)

        border_radius = 12 if (self.source_types or self.subtitle_rich_text) else 14
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: {border_radius}px;
            }}
        """)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._apply_style(hovered=True)

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._apply_style(hovered=False)
