"""
Capa de interfaz gráfica (UI) de la Calculadora de Tipos Pokémon.
Exporta la ventana principal y los componentes visuales.
"""

from src.ui.main_window import MainWindow
from src.ui.components.type_button import TypeButton
from src.ui.components.type_selector import TypeSelectorWidget
from src.ui.components.results_dashboard import ResultsDashboard
from src.ui.controllers.selection_controller import TypeSelectionController
from src.ui.styles import GLOBAL_DARK_STYLESHEET

__all__ = [
    "MainWindow",
    "TypeButton",
    "TypeSelectorWidget",
    "ResultsDashboard",
    "TypeSelectionController",
    "GLOBAL_DARK_STYLESHEET",
]
