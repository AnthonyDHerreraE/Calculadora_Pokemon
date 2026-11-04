"""
Dashboard de Resultados de Efectividad Defensiva y Cobertura Ofensiva (Fase 3 & 6.1).
Muestra de forma categorizada y dinámica los grupos de daño defensivo (x4, x2, x0.5, x0.25, x0 y x1)
y la cobertura ofensiva STAB (x2, x1, x0.5, x0) en un sistema de pestañas (QTabWidget)
con TypeChips, animaciones fluidas y eliminación recursiva de widgets para prevenir Memory Leaks.
"""

from typing import List, Optional, Tuple, Union
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QScrollArea,
    QTabWidget,
    QTabBar,
    QGraphicsOpacityEffect,
    QLayout,
)

from src.core.enums import PokemonType
from src.core.calculator import TypeCalculator
from src.core.models import TypeEffectivenessResult, OffensiveCoverageResult
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
    COLOR_ACCENT_HOVER,
    get_contrast_text_color,
    hex_to_rgba,
)


class DamageGroupSection(QFrame):
    """
    Tarjeta visual que agrupa los tipos bajo un mismo multiplicador de daño.
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

        # Badge del multiplicador (ej. "x4", "x2", "x0.5")
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
    Panel principal de resultados con pestañas dobles (Defensa y Cobertura Ofensiva STAB),
    área con scroll responsivo, soporte de animaciones de opacidad (fade)
    y recolección garantizada de memoria contra Memory Leaks.
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

        # 1. Barra Superior del Dashboard (Título e insignias de tipos activos)
        self._top_bar = QHBoxLayout()
        self._top_bar.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("📊 DASHBOARD DE RESULTADOS", self)
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

        # 2. Sistema de Pestañas (QTabWidget) estilizado en Tema Oscuro
        self._tab_widget = QTabWidget(self)
        self._tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background-color: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_SECONDARY};
                border: 1px solid {COLOR_BORDER_SUBTLE};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 18px;
                margin-right: 6px;
                font-size: 12px;
                font-weight: 700;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_BG_ELEVATED};
                color: {COLOR_TEXT_PRIMARY};
                border-color: {COLOR_ACCENT};
                border-bottom: 2px solid {COLOR_ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLOR_BG_ELEVATED};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

        # Pestaña 1: Análisis Defensivo
        self._def_tab = QWidget()
        def_tab_layout = QVBoxLayout(self._def_tab)
        def_tab_layout.setContentsMargins(0, 8, 0, 0)
        def_tab_layout.setSpacing(0)

        self._def_scroll_area = self._create_scroll_area()
        self._def_content_widget = QWidget()
        self._def_content_layout = QVBoxLayout(self._def_content_widget)
        self._def_content_layout.setContentsMargins(0, 0, 6, 0)
        self._def_content_layout.setSpacing(12)
        self._def_scroll_area.setWidget(self._def_content_widget)
        def_tab_layout.addWidget(self._def_scroll_area)

        # Aliases retrocompatibles para pruebas existentes
        self._scroll_area = self._def_scroll_area
        self._content_widget = self._def_content_widget
        self._content_layout = self._def_content_layout

        self._tab_widget.addTab(self._def_tab, "🛡️ Análisis Defensivo")

        # Pestaña 2: Cobertura Ofensiva (STAB)
        self._atk_tab = QWidget()
        atk_tab_layout = QVBoxLayout(self._atk_tab)
        atk_tab_layout.setContentsMargins(0, 8, 0, 0)
        atk_tab_layout.setSpacing(0)

        self._atk_scroll_area = self._create_scroll_area()
        self._atk_content_widget = QWidget()
        self._atk_content_layout = QVBoxLayout(self._atk_content_widget)
        self._atk_content_layout.setContentsMargins(0, 0, 6, 0)
        self._atk_content_layout.setSpacing(12)
        self._atk_scroll_area.setWidget(self._atk_content_widget)
        atk_tab_layout.addWidget(self._atk_scroll_area)

        self._tab_widget.addTab(self._atk_tab, "⚔️ Cobertura Ofensiva (STAB)")

        self._root_layout.addWidget(self._tab_widget, 1)

        # 3. Efecto de opacidad y animación de desvanecimiento suave (Fade)
        self._opacity_effect = QGraphicsOpacityEffect(self._tab_widget)
        self._opacity_effect.setOpacity(1.0)
        self._tab_widget.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(160)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _create_scroll_area(self) -> QScrollArea:
        """Crea y configura un QScrollArea responsivo sin bordes residuales."""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        return scroll

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
        Regenera el contenido defensivo y ofensivo de forma inmediata e inicia una
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
        """Limpia los widgets anteriores y renderiza los estados defensivo y ofensivo."""
        # Limpieza recursiva de layouts sin fugas de memoria
        self._clear_layout_recursively(self._badges_layout)
        self._clear_layout_recursively(self._def_content_layout)
        self._clear_layout_recursively(self._atk_content_layout)

        if not selected_types:
            self._render_empty_states()
            return

        # 1. Renderizar badges de tipos activos en la cabecera
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

        t1 = selected_types[0]
        t2 = selected_types[1] if len(selected_types) > 1 else None

        # 2. Renderizado de Pestaña Defensiva
        self._rebuild_defensive_content(t1, t2)

        # 3. Renderizado de Pestaña Ofensiva (STAB)
        self._rebuild_offensive_content(t1, t2)

    def _rebuild_defensive_content(
        self,
        primary_type: PokemonType,
        secondary_type: Optional[PokemonType],
    ) -> None:
        """Construye las tarjetas de daño para el análisis defensivo."""
        res_def: TypeEffectivenessResult = TypeCalculator.calculate(primary_type, secondary_type)

        defensive_groups = [
            ("VULNERABILIDAD EXTREMA", "x4", "#DC2626", res_def.quad_weaknesses, False),
            ("DEBILIDADES", "x2", "#EF4444", res_def.weaknesses, False),
            ("INMUNIDADES TOTALES", "x0", "#8B5CF6", res_def.immunities, False),
            ("SÚPER RESISTENCIAS", "x0.25", "#059669", res_def.double_resistances, False),
            ("RESISTENCIAS", "x0.5", "#10B981", res_def.resistances, False),
        ]

        for title, mult_str, color, types_tuple, is_subtle in defensive_groups:
            if not types_tuple:
                continue

            section = DamageGroupSection(
                title=title,
                multiplier_str=mult_str,
                badge_color=color,
                types=types_tuple,
                is_subtle=is_subtle,
                parent=self._def_content_widget,
            )
            self._def_content_layout.addWidget(section)

        # Daño Normal x1 visible al final
        normal_section = DamageGroupSection(
            title="DAÑO NORMAL (NEUTRO)",
            multiplier_str="x1",
            badge_color="#475569",
            types=res_def.neutral,
            is_subtle=True,
            parent=self._def_content_widget,
        )
        self._def_content_layout.addWidget(normal_section)
        self._def_content_layout.addStretch()

    def _rebuild_offensive_content(
        self,
        primary_type: PokemonType,
        secondary_type: Optional[PokemonType],
    ) -> None:
        """Construye las tarjetas de daño para la cobertura ofensiva STAB (máximo daño infligido)."""
        res_atk: OffensiveCoverageResult = TypeCalculator.calculate_offensive_coverage(
            primary_type, secondary_type
        )

        offensive_groups = [
            ("SÚPER EFECTIVO", "x2", "#EF4444", res_atk.super_effective, False),
            ("SIN EFECTO", "x0", "#8B5CF6", res_atk.no_effect, False),
            ("POCO EFECTIVO", "x0.5", "#10B981", res_atk.not_very_effective, False),
        ]

        for title, mult_str, color, types_tuple, is_subtle in offensive_groups:
            if not types_tuple:
                continue

            section = DamageGroupSection(
                title=title,
                multiplier_str=mult_str,
                badge_color=color,
                types=types_tuple,
                is_subtle=is_subtle,
                parent=self._atk_content_widget,
            )
            self._atk_content_layout.addWidget(section)

        # Daño Normal x1 visible al final
        normal_section = DamageGroupSection(
            title="DAÑO NORMAL (NEUTRO)",
            multiplier_str="x1",
            badge_color="#475569",
            types=res_atk.neutral,
            is_subtle=True,
            parent=self._atk_content_widget,
        )
        self._atk_content_layout.addWidget(normal_section)
        self._atk_content_layout.addStretch()

    def _render_empty_states(self) -> None:
        """Renderiza las pantallas informativas en ambas pestañas cuando no hay selección."""
        # Estado vacío para pestaña defensiva
        self._render_single_empty_state(
            layout=self._def_content_layout,
            parent_widget=self._def_content_widget,
            icon="🛡️",
            title="Esperando Selección Defensiva",
            description=(
                "Selecciona 1 o 2 tipos en el panel izquierdo para calcular\n"
                "las debilidades (x4, x2), resistencias (x0.5, x0.25) e inmunidades (x0)."
            ),
        )

        # Estado vacío para pestaña ofensiva
        self._render_single_empty_state(
            layout=self._atk_content_layout,
            parent_widget=self._atk_content_widget,
            icon="⚔️",
            title="Esperando Selección Ofensiva (STAB)",
            description=(
                "Selecciona 1 o 2 tipos en el panel izquierdo para evaluar la cobertura\n"
                "máxima de ataque: súper efectivo (x2), neutro (x1), poco eficaz (x0.5) y nulo (x0)."
            ),
        )

    def _render_single_empty_state(
        self,
        layout: QVBoxLayout,
        parent_widget: QWidget,
        icon: str,
        title: str,
        description: str,
    ) -> None:
        """Genera una tarjeta elegante de estado vacío."""
        empty_frame = QFrame(parent_widget)
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

        icon_label = QLabel(icon, empty_frame)
        icon_label.setStyleSheet("font-size: 42px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_label)

        title_label = QLabel(title, empty_frame)
        title_label.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title_label)

        desc_label = QLabel(description, empty_frame)
        desc_label.setStyleSheet(
            f"font-size: 13px; color: {COLOR_TEXT_MUTED}; background: transparent; border: none;"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_label)

        layout.addWidget(empty_frame)
        layout.addStretch()
