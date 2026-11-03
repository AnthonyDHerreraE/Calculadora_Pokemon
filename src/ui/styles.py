"""
Sistema de estilos, tokens de diseño y stylesheet global (Dark Theme)
para la interfaz de escritorio de la Calculadora de Tipos Pokémon.
"""

from typing import Tuple


# Paleta cromática del tema oscuro (Dark Mode Premium)
COLOR_BG_CANVAS = "#0D0F14"       # Fondo más profundo de la ventana
COLOR_BG_CARD = "#151821"         # Fondo de tarjetas y paneles principales
COLOR_BG_SURFACE = "#1C202C"      # Superficie de controles interactivos
COLOR_BG_ELEVATED = "#252B3B"     # Fondo elevado para estados hover
COLOR_BORDER_SUBTLE = "#282E40"   # Bordes secundarios discretos
COLOR_BORDER_STRONG = "#3B445E"   # Bordes destacados / foco
COLOR_ACCENT = "#6366F1"          # Acento primario (Indigo eléctrico)
COLOR_ACCENT_HOVER = "#818CF8"    # Acento primario hover
COLOR_TEXT_PRIMARY = "#F8FAFC"    # Texto de máxima legibilidad
COLOR_TEXT_SECONDARY = "#94A3B8"  # Texto secundario y subtítulos
COLOR_TEXT_MUTED = "#64748B"      # Texto atenuado y etiquetas pequeñas
COLOR_SUCCESS = "#10B981"         # Verde para estados positivos/resistencias
COLOR_DANGER = "#EF4444"          # Rojo para debilidades


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convierte un código hexadecimal (#RRGGBB) a tupla (R, G, B)."""
    clean_hex = hex_code.lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    return (
        int(clean_hex[0:2], 16),
        int(clean_hex[2:4], 16),
        int(clean_hex[4:6], 16),
    )


def hex_to_rgba(hex_code: str, alpha: float) -> str:
    """Convierte un código hexadecimal a una cadena CSS 'rgba(r, g, b, alpha)'."""
    r, g, b = hex_to_rgb(hex_code)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def get_contrast_text_color(hex_bg: str) -> str:
    """Calcula el color de texto óptimo (blanco o casi negro) según la luminancia del fondo."""
    r, g, b = hex_to_rgb(hex_bg)
    # Fórmula de luminancia relativa estándar W3C
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0F1117" if luminance > 0.65 else "#FFFFFF"


# Hoja de estilos global en QSS (Qt Style Sheets)
GLOBAL_DARK_STYLESHEET = f"""
/* Ventana y contenedores base */
QMainWindow {{
    background-color: {COLOR_BG_CANVAS};
    color: {COLOR_TEXT_PRIMARY};
}}

QWidget#CentralWidget {{
    background-color: {COLOR_BG_CANVAS};
}}

/* Paneles y Tarjetas */
QFrame.CardPanel {{
    background-color: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER_SUBTLE};
    border-radius: 14px;
}}

QFrame.SubCardPanel {{
    background-color: {COLOR_BG_SURFACE};
    border: 1px solid {COLOR_BORDER_SUBTLE};
    border-radius: 10px;
}}

/* Tipografía y Etiquetas */
QLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
}}

QLabel#HeaderTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {COLOR_TEXT_PRIMARY};
    letter-spacing: 0.5px;
}}

QLabel#HeaderSubtitle {{
    font-size: 12px;
    color: {COLOR_TEXT_SECONDARY};
}}

QLabel#SectionTitle {{
    font-size: 13px;
    font-weight: 700;
    color: {COLOR_TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QLabel#BadgeCount {{
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    background-color: {COLOR_BG_ELEVATED};
    color: {COLOR_ACCENT_HOVER};
    border-radius: 8px;
    border: 1px solid {COLOR_BORDER_STRONG};
}}

/* Botones de acción general */
QPushButton#ActionButton {{
    background-color: {COLOR_BG_SURFACE};
    color: {COLOR_TEXT_SECONDARY};
    border: 1px solid {COLOR_BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#ActionButton:hover {{
    background-color: {COLOR_BG_ELEVATED};
    color: {COLOR_TEXT_PRIMARY};
    border-color: {COLOR_BORDER_STRONG};
}}

QPushButton#ActionButton:pressed {{
    background-color: {COLOR_BORDER_SUBTLE};
}}

/* ScrollBars personalizadas para diseño moderno */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER_STRONG};
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Tooltips */
QToolTip {{
    background-color: {COLOR_BG_ELEVATED};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER_STRONG};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}
"""
