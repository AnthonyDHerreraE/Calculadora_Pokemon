"""
Dashboard de Resultados de Efectividad Defensiva (Fase 3).
Muestra de forma categorizada y dinámica los grupos de daño (x4, x2, x0.5, x0.25, x0 y x1)
utilizando TypeChips, animaciones fluidas de transición (fade) y eliminación
recursiva de widgets para prevenir fugas de memoria (Memory Leaks).
"""

from typing import List, Optional, Tuple
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QScrollArea,
    QGraphicsOpacityEffect,
    QLayout,
)

from src.core.enums import PokemonType
from src.core.calculator import TypeCalculator
from src.core.models import TypeEffectivenessResult
from src.ui.components.type_chip import TypeChip
from src.ui.components.flow_layout import FlowLayout
from src.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_SURFACE,
    COLOR_BG_ELEVATED,
    COLOR_BORDER_SUBTLE,
    COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    get_contrast_text_color,
    hex_to_rgba,
)


class DamageGroupSection(QFrame):
    """
    Tarjeta visual que agrupa los tipos atacantes bajo un mismo multiplicador de daño.
    Contiene una barra de título con badge de multiplicador y un FlowLayout
    que distribuye dinámicamente los TypeChips.
    """

    def __init__(
        self,
        title: str,
        multiplier_str: str,
        badge_color: str,
        types: Tuple[PokemonType, ...],
        is_subtle: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.multiplier_str = multiplier_str
        self.badge_color = badge_color
        self.types = types
        self.is_subtle = is_subtle

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Estilo del contenedor de la tarjeta
        border_opacity = 0.25 if self.is_subtle else 0.50
        border_col = hex_to_rgba(self.badge_color, border_opacity)
        bg_col = COLOR_BG_CARD if not self.is_subtle else COLOR_BG_SURFACE

        self.setStyleSheet(f"""
            DamageGroupSection {{
                background-color: {bg_col};
                border: 1px solid {COLOR_BORDER_SUBTLE};
                border-left: 4px solid {self.badge_color};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(10)

        # 1. Cabecera del Grupo (Badge multiplicador + Título + Contador)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Badge del multiplicador (ej. "x4", "x0.5")
        mult_badge = QLabel(f" {self.multiplier_str} ", self)
        mult_text_color = "#FFFFFF" if not self.is_subtle else COLOR_TEXT_PRIMARY
        mult_badge.setStyleSheet(f"""
            background-color: {self.badge_color};
            color: {mult_text_color};
            font-size: 11px;
            font-weight: 800;
            border-radius: 6px;
            padding: 2px 6px;
        """)
        header_layout.addWidget(mult_badge)

        # Título de la categoría
        title_label = QLabel(self.title, self)
        font_size = "11px" if self.is_subtle else "12px"
        title_color = COLOR_TEXT_MUTED if self.is_subtle else COLOR_TEXT_PRIMARY
        title_label.setStyleSheet(
            f"font-size: {font_size}; font-weight: 700; color: {title_color}; letter-spacing: 0.5px; background: transparent; border: none;"
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Contador de tipos
        count_label = QLabel(f"{len(self.types)} tipo{'s' if len(self.types) != 1 else ''}", self)
        count_label.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED}; background: transparent; border: none;"
        )
        header_layout.addWidget(count_label)

        layout.addLayout(header_layout)

        # 2. Contenedor de Chips usando FlowLayout
        chips_container = QWidget(self)
        chips_container.setStyleSheet("background: transparent; border: none;")
        chips_layout = FlowLayout(chips_container, margin=0, h_spacing=8, v_spacing=8)

        # Multiplicador numérico estimado para tooltip
        try:
            mult_val = float(self.multiplier_str.replace("x", ""))
        except ValueError:
            mult_val = None

        for ptype in self.types:
            chip = TypeChip(ptype, multiplier=mult_val, parent=chips_container)
            chips_layout.addWidget(chip)

        layout.addWidget(chips_container)


class ResultsDashboard(QFrame):
    """
    Panel principal de resultados con soporte de animaciones de opacidad (fade),
    área con scroll responsivo y recolección garantizada de memoria.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("ResultsDashboardCard")
        self.setProperty("class", "CardPanel")

        self._current_types: Tuple[PokemonType, ...] = ()
        self._is_animating: bool = False

        self._setup_ui()
        self.update_selection(())

    def _setup_ui(self) -> None:
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(20, 16, 20, 18)
        self._root_layout.setSpacing(12)

        # 1. Barra Superior del Dashboard (Título e insignias de tipos defensores)
        self._top_bar = QHBoxLayout()
        self._top_bar.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("📊 DASHBOARD DE RESULTADOS (ANÁLISIS DEFENSIVO)", self)
        title_label.setObjectName("SectionTitle")
        self._top_bar.addWidget(title_label)

        self._top_bar.addStretch()

        # Contenedor de insignias activas
        self._badges_container = QWidget(self)
        self._badges_layout = QHBoxLayout(self._badges_container)
        self._badges_layout.setContentsMargins(0, 0, 0, 0)
        self._badges_layout.setSpacing(8)
        self._top_bar.addWidget(self._badges_container)

        self._root_layout.addLayout(self._top_bar)

        # 2. ScrollArea para albergar los grupos de daño dinámicos
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        # Widget interno alojado dentro del ScrollArea
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 6, 0)
        self._content_layout.setSpacing(12)

        self._scroll_area.setWidget(self._content_widget)
        self._root_layout.addWidget(self._scroll_area, 1)

        # 3. Efecto de opacidad y animación de desvanecimiento suave (Fade)
        self._opacity_effect = QGraphicsOpacityEffect(self._content_widget)
        self._opacity_effect.setOpacity(1.0)
        self._content_widget.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(160)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _clear_layout_recursively(self, layout: Optional[QLayout]) -> None:
        """
        Estrategia de eliminación recursiva de elementos para prevenir Memory Leaks en Qt:
        1. Desconecta y retira los elementos con takeAt(0).
        2. Si el elemento aloja un QWidget, lo desvincula de su padre (setParent(None))
           y delega su destrucción segura al recolector de Qt vía deleteLater().
        3. Si el elemento aloja un sub-layout, aplica recursividad en profundidad.
        """
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self._clear_layout_recursively(sub_layout)

    def update_selection(
        self,
        selected_types: Tuple[PokemonType, ...],
        animate: bool = True,
    ) -> None:
        """
        Punto de entrada reactivo ante la señal selection_changed.
        Regenera el contenido del dashboard de forma inmediata e inicia una
        animación suave de entrada (fade-in) para una transición visual pulida.
        """
        self._current_types = selected_types
        self._rebuild_content(selected_types)

        if animate and self.isVisible():
            self._fade_anim.stop()
            self._fade_anim.setStartValue(0.25)
            self._fade_anim.setEndValue(1.0)
            self._fade_anim.start()
        else:
            self._opacity_effect.setOpacity(1.0)

    def _rebuild_content(self, selected_types: Tuple[PokemonType, ...]) -> None:
        """Limpia los widgets anteriores y renderiza el nuevo estado defensivo."""
        # Limpieza sin fugas de memoria
        self._clear_layout_recursively(self._badges_layout)
        self._clear_layout_recursively(self._content_layout)

        if not selected_types:
            self._render_empty_state()
            return

        # 1. Renderizar badges de tipos defensores en la cabecera
        for ptype in selected_types:
            badge = QLabel(f" {ptype.display_name_es.upper()} ", self._badges_container)
            text_color = get_contrast_text_color(ptype.hex_color)
            badge.setStyleSheet(f"""
                background-color: {ptype.hex_color};
                color: {text_color};
                font-weight: 800;
                font-size: 11px;
                border-radius: 8px;
                padding: 4px 10px;
            """)
            self._badges_layout.addWidget(badge)

        # 2. Cálculo matemático exacto mediante TypeCalculator (Fase 1)
        t1 = selected_types[0]
        t2 = selected_types[1] if len(selected_types) > 1 else None
        res: TypeEffectivenessResult = TypeCalculator.calculate(t1, t2)

        # 3. Mapeo de grupos de daño con paleta semántica
        # Regla UI: Ocultar categorías vacías, mostrar Daño Normal x1 al final
        combat_groups = [
            ("VULNERABILIDAD EXTREMA", "x4", "#DC2626", res.quad_weaknesses, False),
            ("DEBILIDADES", "x2", "#EF4444", res.weaknesses, False),
            ("INMUNIDADES TOTALES", "x0", "#8B5CF6", res.immunities, False),
            ("SÚPER RESISTENCIAS", "x0.25", "#059669", res.double_resistances, False),
            ("RESISTENCIAS", "x0.5", "#10B981", res.resistances, False),
        ]

        active_sections_count = 0
        for title, mult_str, color, types_tuple, is_subtle in combat_groups:
            # Si la categoría no tiene tipos, NO se renderiza (Regla UI)
            if not types_tuple:
                continue

            section = DamageGroupSection(
                title=title,
                multiplier_str=mult_str,
                badge_color=color,
                types=types_tuple,
                is_subtle=is_subtle,
                parent=self._content_widget,
            )
            self._content_layout.addWidget(section)
            active_sections_count += 1

        # 4. Sección "Daño Normal x1" siempre visible al final
        normal_section = DamageGroupSection(
            title="DAÑO NORMAL (NEUTRO)",
            multiplier_str="x1",
            badge_color="#475569",
            types=res.neutral,
            is_subtle=True,
            parent=self._content_widget,
        )
        self._content_layout.addWidget(normal_section)

        # Espaciador elástico final para asegurar compactación visual
        self._content_layout.addStretch()

    def _render_empty_state(self) -> None:
        """Renderiza la pantalla informativa inicial cuando no hay tipos seleccionados."""
        empty_frame = QFrame(self._content_widget)
        empty_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_SURFACE};
                border: 1px dashed {COLOR_BORDER_SUBTLE};
                border-radius: 12px;
                padding: 30px;
            }}
        """)
        empty_layout = QVBoxLayout(empty_frame)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(10)

        icon_label = QLabel("🎯", empty_frame)
        icon_label.setStyleSheet("font-size: 42px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_label)

        title = QLabel("Esperando Selección de Tipos", empty_frame)
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title)

        desc = QLabel(
            "Selecciona 1 o 2 tipos en el panel superior para desplegar dinámicamente\n"
            "las debilidades (x4, x2), resistencias (x0.5, x0.25) e inmunidades (x0).",
            empty_frame,
        )
        desc.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_MUTED}; background: transparent; border: none;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc)

        self._content_layout.addWidget(empty_frame)
        self._content_layout.addStretch()
