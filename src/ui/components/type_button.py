"""
Botón interactivo personalizado para cada tipo de Pokémon.
Implementa efectos de brillo (glow), animaciones fluidas con QPropertyAnimation,
distinción visual de selección (100% vs 50% de opacidad) y badges de ranura (1º / 2º).
"""

from typing import Optional
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QFrame,
)

from src.core.enums import PokemonType
from src.ui.styles import (
    hex_to_rgba,
    get_contrast_text_color,
    COLOR_BG_CARD,
    COLOR_BORDER_SUBTLE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)


class TypeButton(QPushButton):
    """
    Componente visual de botón para seleccionar un tipo Pokémon.
    Extiende QPushButton incorporando sombra reactiva, animaciones de brillo
    y visualización del orden de selección.
    """

    def __init__(self, pokemon_type: PokemonType, parent: Optional[QFrame] = None) -> None:
        super().__init__(parent)
        self.pokemon_type = pokemon_type
        self._is_selected: bool = False
        self._slot_index: Optional[int] = None
        self._is_dimmed: bool = False

        self.setFixedSize(138, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Efecto de resplandor / elevación (Glow Effect)
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setOffset(0, 3)
        self._shadow_effect.setBlurRadius(0)
        base_color = QColor(self.pokemon_type.hex_color)
        base_color.setAlpha(0)
        self._shadow_effect.setColor(base_color)
        self.setGraphicsEffect(self._shadow_effect)

        # Animación de brillo
        self._blur_anim = QPropertyAnimation(self._shadow_effect, b"blurRadius", self)
        self._blur_anim.setDuration(200)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Layout interno del botón
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 8, 0)
        self._layout.setSpacing(6)

        # 1. Indicador de color (Pill Dot)
        self._color_dot = QLabel(self)
        self._color_dot.setFixedSize(8, 8)
        self._color_dot.setStyleSheet(
            f"background-color: {self.pokemon_type.hex_color}; border-radius: 4px;"
        )
        self._layout.addWidget(self._color_dot)

        # 2. Nombre del Tipo en Español
        self._title_label = QLabel(self.pokemon_type.display_name_es, self)
        self._title_label.setStyleSheet("font-size: 12px; font-weight: 700; background: transparent;")
        self._layout.addWidget(self._title_label, 1)

        # 3. Badge de Ranura de Selección (1º / 2º)
        self._badge_label = QLabel(self)
        self._badge_label.setFixedHeight(20)
        self._badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_label.setVisible(False)
        self._layout.addWidget(self._badge_label)

        # Aplicar estilo inicial
        self._update_style(hovered=False)

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    def set_selection_state(
        self,
        is_selected: bool,
        slot_index: Optional[int] = None,
        is_dimmed: bool = False,
    ) -> None:
        """
        Actualiza el estado de selección del botón.

        Args:
            is_selected: True si el botón está seleccionado (1º o 2º tipo).
            slot_index: 1 para primer tipo, 2 para segundo tipo, o None.
            is_dimmed: True si hay 2 tipos seleccionados y este no es uno de ellos.
        """
        self._is_selected = is_selected
        self._slot_index = slot_index
        self._is_dimmed = is_dimmed

        # Configurar badge de orden
        if self._is_selected and slot_index:
            badge_text = "1º TIPO" if slot_index == 1 else "2º TIPO"
            self._badge_label.setText(badge_text)
            self._badge_label.setVisible(True)
        else:
            self._badge_label.setVisible(False)

        # Actualizar efectos y sombras
        color = QColor(self.pokemon_type.hex_color)
        if self._is_selected:
            color.setAlpha(190)
            self._shadow_effect.setColor(color)
            self._shadow_effect.setBlurRadius(20)
            self._shadow_effect.setOffset(0, 4)
        else:
            color.setAlpha(0)
            self._shadow_effect.setColor(color)
            self._shadow_effect.setBlurRadius(0)
            self._shadow_effect.setOffset(0, 2)

        self._update_style(hovered=False)

    def _update_style(self, hovered: bool) -> None:
        """Genera y aplica el QSS dinámico según el estado actual."""
        hex_color = self.pokemon_type.hex_color

        if self._is_selected:
            # Estado Seleccionado: Color vibrante del tipo, 100% opacidad, resplandor
            text_color = get_contrast_text_color(hex_color)
            bg_gradient = (
                f"qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                f"stop:0 {hex_color}, stop:1 {hex_to_rgba(hex_color, 0.85)})"
            )
            border_color = "#FFFFFF" if hovered else hex_to_rgba("#FFFFFF", 0.75)
            opacity = "1.0"
            badge_bg = "rgba(0, 0, 0, 0.35)"
            badge_text = "#FFFFFF"

            self.setStyleSheet(f"""
                QPushButton {{
                    background: {bg_gradient};
                    border: 2px solid {border_color};
                    border-radius: 12px;
                    opacity: {opacity};
                }}
            """)
            self._title_label.setStyleSheet(f"color: {text_color}; font-weight: 800; font-size: 13px;")
            self._color_dot.setStyleSheet("background-color: #FFFFFF; border-radius: 5px;")
            self._badge_label.setStyleSheet(f"""
                background-color: {badge_bg};
                color: {badge_text};
                border-radius: 9px;
                padding: 0 5px;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.2px;
            """)

        else:
            # Estado No Seleccionado
            opacity = "0.45" if self._is_dimmed else "1.0"
            if hovered:
                bg_color = hex_to_rgba(hex_color, 0.15)
                border_color = hex_color
                title_color = COLOR_TEXT_PRIMARY
            else:
                bg_color = COLOR_BG_CARD
                border_color = hex_to_rgba(hex_color, 0.35)
                title_color = COLOR_TEXT_SECONDARY if not self._is_dimmed else "#525C76"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: 1.5px solid {border_color};
                    border-radius: 12px;
                    opacity: {opacity};
                }}
            """)
            self._title_label.setStyleSheet(f"color: {title_color}; font-weight: 600; font-size: 13px;")
            self._color_dot.setStyleSheet(
                f"background-color: {hex_color}; border-radius: 5px;"
            )

    def enterEvent(self, event) -> None:
        """Animación suave de resplandor al posar el cursor."""
        super().enterEvent(event)
        if not self._is_selected:
            color = QColor(self.pokemon_type.hex_color)
            color.setAlpha(140)
            self._shadow_effect.setColor(color)
            self._blur_anim.stop()
            self._blur_anim.setStartValue(self._shadow_effect.blurRadius())
            self._blur_anim.setEndValue(16)
            self._blur_anim.start()
        self._update_style(hovered=True)

    def leaveEvent(self, event) -> None:
        """Retorno suave a reposo al retirar el cursor."""
        super().leaveEvent(event)
        if not self._is_selected:
            self._blur_anim.stop()
            self._blur_anim.setStartValue(self._shadow_effect.blurRadius())
            self._blur_anim.setEndValue(0)
            self._blur_anim.start()
        self._update_style(hovered=False)
