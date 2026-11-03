"""
Punto de entrada principal de la aplicación de escritorio nativa
Calculadora de Tipos Pokémon (PySide6 / Qt 6).
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow


def main() -> int:
    """Inicializa la aplicación Qt y arranca el bucle de eventos."""
    # Configuración de atributos de renderizado
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Calculadora de Tipos Pokémon")
    app.setApplicationDisplayName("Calculadora de Tipos Pokémon • Gen VI+")
    app.setOrganizationName("PokeTypeLab")

    # Instanciación y presentación de la ventana principal
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
