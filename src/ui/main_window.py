"""
Ventana Principal (MainWindow) de la Calculadora de Tipos de Pokémon.
Organiza la arquitectura visual de dos paneles (Selector y Dashboard)
integrando controladores y el stylesheet global en un tema oscuro premium.
"""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QStatusBar,
)

from src.ui.styles import (
    GLOBAL_DARK_STYLESHEET,
    COLOR_BG_CARD,
    COLOR_BORDER_SUBTLE,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
)
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.components.search_bar import SearchBar
from src.ui.components.type_selector import TypeSelectorWidget
from src.ui.components.results_dashboard import ResultsDashboard


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación de escritorio.
    Estructura la pantalla en tres paneles integrados:
    - Barra de Búsqueda inteligente (SearchBar con PokéAPI asíncrona).
    - Selector interactivo de tipos (TypeSelectorWidget).
    - Dashboard de resultados defensivos (ResultsDashboard).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calculadora de Tipos Pokémon • Generación VI+")
        self.setMinimumSize(1080, 720)
        self.resize(1260, 820)

        # Controlador de estado desacoplado
        self.controller = TypeSelectionController(self)

        # Aplicar stylesheet global
        self.setStyleSheet(GLOBAL_DARK_STYLESHEET)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 14, 20, 14)
        root_layout.setSpacing(14)

        # 1. Encabezado superior de la aplicación (Branding & Status)
        header_frame = self._create_header()
        root_layout.addWidget(header_frame)

        # 2. Contenedor horizontal de Dos Columnas (Widescreen 16:9)
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(18)

        # --- COLUMNA IZQUIERDA: Panel de Entrada (Búsqueda + Selector de Tipos) ---
        left_panel = QWidget(self)
        left_panel.setFixedWidth(464)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Barra de Búsqueda inteligente
        self.search_bar = SearchBar(self.controller, parent=left_panel)
        left_layout.addWidget(self.search_bar)

        # Selector interactivo de tipos (3 columnas x 6 filas)
        self.selector_widget = TypeSelectorWidget(self.controller, parent=left_panel)
        left_layout.addWidget(self.selector_widget)

        # Espaciador para anclar controles arriba
        left_layout.addStretch()

        columns_layout.addWidget(left_panel, 0)

        # Línea divisoria vertical sutil entre columnas
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BORDER_SUBTLE};
                border: none;
                width: 1px;
            }}
        """)
        columns_layout.addWidget(divider)

        # --- COLUMNA DERECHA: Dashboard de Resultados (Expansión completa) ---
        self.results_dashboard = ResultsDashboard(self)
        columns_layout.addWidget(self.results_dashboard, 1)

        root_layout.addLayout(columns_layout, 1)

        # Barra de estado inferior
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLOR_BG_CARD};
                color: {COLOR_TEXT_MUTED};
                border-top: 1px solid {COLOR_BORDER_SUBTLE};
                font-size: 11px;
                padding: 4px 12px;
            }}
        """)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Motor de cálculo activo • PokéAPI conectada • PySide6 UI")

    def _create_header(self) -> QFrame:
        """Crea la barra de marca superior de la aplicación."""
        header = QFrame(self)
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {COLOR_BORDER_SUBTLE};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(4, 0, 4, 8)
        layout.setSpacing(12)

        # Icono Pokéball estilizado
        icon_badge = QLabel("⚡", header)
        icon_badge.setStyleSheet(f"""
            font-size: 18px;
            background-color: {COLOR_ACCENT};
            color: #FFFFFF;
            border-radius: 15px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
        """)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_badge)

        # Bloque de Títulos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        text_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("CALCULADORA DE TIPOS POKÉMON", header)
        title_label.setObjectName("HeaderTitle")

        subtitle_label = QLabel("Sistema de Análisis Defensivo • Motor Nativo PySide6 • Búsqueda PokéAPI v2", header)
        subtitle_label.setObjectName("HeaderSubtitle")

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        layout.addLayout(text_layout)

        layout.addStretch()

        # Tag de versión
        version_badge = QLabel("FASE 4 • FINAL", header)
        version_badge.setStyleSheet(f"""
            background-color: #1F2433;
            color: {COLOR_ACCENT_HOVER};
            border: 1px solid {COLOR_BORDER_SUBTLE};
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(version_badge)

        return header

    def _connect_signals(self) -> None:
        """Conecta las señales del controlador para sincronizar los paneles."""
        self.controller.selection_changed.connect(self.results_dashboard.update_selection)
        self.controller.selection_changed.connect(self._on_selection_updated)
        self.search_bar.pokemon_selected.connect(self._on_pokemon_searched)

    def _on_pokemon_searched(self, pokemon_data) -> None:
        """Actualiza la barra de estado cuando se carga un Pokémon vía PokéAPI."""
        self.statusBar().showMessage(
            f"Pokémon cargado: {pokemon_data.display_title} ({pokemon_data.types_display_es})"
        )

    def _on_selection_updated(self, selected_types: tuple) -> None:
        """Actualiza el mensaje de la barra de estado según la selección actual."""
        if not selected_types:
            self.statusBar().showMessage("Ningún tipo seleccionado. Elige hasta 2 tipos.")
        elif len(selected_types) == 1:
            t1 = selected_types[0]
            self.statusBar().showMessage(f"Tipo seleccionado: {t1.display_name_es} (Mono-tipo)")
        else:
            t1, t2 = selected_types
            self.statusBar().showMessage(f"Tipos seleccionados: {t1.display_name_es} / {t2.display_name_es} (Doble-tipo)")
