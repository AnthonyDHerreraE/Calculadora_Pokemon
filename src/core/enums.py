"""
Módulo de enumeraciones para el sistema de tipos de Pokémon.
Proporciona tipado estricto, soporte bilingüe (ES/EN) y metadatos visuales para la UI.
"""

from __future__ import annotations
import unicodedata
from enum import Enum, unique
from typing import Dict, Optional, Tuple


@unique
class PokemonType(str, Enum):
    """
    Enumeración de los 18 tipos elementales canónicos desde la Generación VI.
    Hereda de str para facilitar serialización e interoperabilidad.
    """
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"
    NUCLEAR = "nuclear"

    @property
    def display_name_en(self) -> str:
        """Nombre formal en inglés (capitalizado)."""
        return self.value.capitalize()

    @property
    def display_name_es(self) -> str:
        """Nombre oficial en español."""
        es_map: Dict[PokemonType, str] = {
            PokemonType.NORMAL: "Normal",
            PokemonType.FIRE: "Fuego",
            PokemonType.WATER: "Agua",
            PokemonType.GRASS: "Planta",
            PokemonType.ELECTRIC: "Eléctrico",
            PokemonType.ICE: "Hielo",
            PokemonType.FIGHTING: "Lucha",
            PokemonType.POISON: "Veneno",
            PokemonType.GROUND: "Tierra",
            PokemonType.FLYING: "Volador",
            PokemonType.PSYCHIC: "Psíquico",
            PokemonType.BUG: "Bicho",
            PokemonType.ROCK: "Roca",
            PokemonType.GHOST: "Fantasma",
            PokemonType.DRAGON: "Dragón",
            PokemonType.DARK: "Siniestro",
            PokemonType.STEEL: "Acero",
            PokemonType.FAIRY: "Hada",
            PokemonType.NUCLEAR: "Nuclear",
        }
        return es_map[self]

    @property
    def hex_color(self) -> str:
        """
        Código de color hexadecimal representativo del tipo,
        optimizado para su uso en paletas de interfaz gráfica (UI/UX).
        """
        color_map: Dict[PokemonType, str] = {
            PokemonType.NORMAL: "#9FA19F",
            PokemonType.FIRE: "#E62829",
            PokemonType.WATER: "#2980EF",
            PokemonType.GRASS: "#3FA129",
            PokemonType.ELECTRIC: "#FAC000",
            PokemonType.ICE: "#3DCEF3",
            PokemonType.FIGHTING: "#FF8000",
            PokemonType.POISON: "#9141CB",
            PokemonType.GROUND: "#915121",
            PokemonType.FLYING: "#81B9EF",
            PokemonType.PSYCHIC: "#EF4179",
            PokemonType.BUG: "#91A119",
            PokemonType.ROCK: "#AFA981",
            PokemonType.GHOST: "#704170",
            PokemonType.DRAGON: "#5060E1",
            PokemonType.DARK: "#624D4E",
            PokemonType.STEEL: "#60A1B8",
            PokemonType.FAIRY: "#EF70EF",
            PokemonType.NUCLEAR: "#39FF14",
        }
        return color_map[self]

    @classmethod
    def from_string(cls, value: str) -> PokemonType:
        """
        Parsea un string a un PokemonType válido, tolerando mayúsculas,
        espacios, acentos y nombres tanto en español como en inglés.

        Raises:
            ValueError: Si el texto no corresponde a ningún tipo válido.
        """
        if not isinstance(value, str):
            raise TypeError(f"Se esperaba una cadena de texto, pero se recibió {type(value).__name__}.")

        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        clean_text = "".join(c for c in normalized if not unicodedata.combining(c))

        # Diccionario de alias unificado (Español e Inglés sin tildes)
        aliases: Dict[str, PokemonType] = {
            # Inglés
            "normal": PokemonType.NORMAL,
            "fire": PokemonType.FIRE,
            "water": PokemonType.WATER,
            "grass": PokemonType.GRASS,
            "electric": PokemonType.ELECTRIC,
            "ice": PokemonType.ICE,
            "fighting": PokemonType.FIGHTING,
            "poison": PokemonType.POISON,
            "ground": PokemonType.GROUND,
            "flying": PokemonType.FLYING,
            "psychic": PokemonType.PSYCHIC,
            "bug": PokemonType.BUG,
            "rock": PokemonType.ROCK,
            "ghost": PokemonType.GHOST,
            "dragon": PokemonType.DRAGON,
            "dark": PokemonType.DARK,
            "steel": PokemonType.STEEL,
            "fairy": PokemonType.FAIRY,
            "nuclear": PokemonType.NUCLEAR,
            # Español
            "fuego": PokemonType.FIRE,
            "agua": PokemonType.WATER,
            "planta": PokemonType.GRASS,
            "electrico": PokemonType.ELECTRIC,
            "hielo": PokemonType.ICE,
            "lucha": PokemonType.FIGHTING,
            "veneno": PokemonType.POISON,
            "tierra": PokemonType.GROUND,
            "volador": PokemonType.FLYING,
            "psiquico": PokemonType.PSYCHIC,
            "bicho": PokemonType.BUG,
            "roca": PokemonType.ROCK,
            "fantasma": PokemonType.GHOST,
            "siniestro": PokemonType.DARK,
            "acero": PokemonType.STEEL,
            "hada": PokemonType.FAIRY,
        }

        if clean_text in aliases:
            return aliases[clean_text]

        valid_options = ", ".join(t.value for t in cls)
        raise ValueError(
            f"Tipo Pokémon inválido: '{value}'. Opciones válidas: {valid_options}"
        )


@unique
class EffectivenessCategory(Enum):
    """
    Categorías de multiplicador de daño en combate.
    """
    QUAD_WEAKNESS = (4.0, "Súper Débil (x4)", "#7A0000")
    WEAKNESS = (2.0, "Débil (x2)", "#C0392B")
    NEUTRAL = (1.0, "Normal (x1)", "#7F8C8D")
    RESISTANCE = (0.5, "Resistente (x0.5)", "#27AE60")
    DOUBLE_RESISTANCE = (0.25, "Súper Resistente (x0.25)", "#1E8449")
    IMMUNITY = (0.0, "Inmune (x0)", "#2C3E50")

    def __init__(self, multiplier: float, label_es: str, color_hex: str) -> None:
        self.multiplier = multiplier
        self.label_es = label_es
        self.color_hex = color_hex

    @classmethod
    def from_multiplier(cls, mult: float) -> EffectivenessCategory:
        """Obtiene la categoría correspondiente a un multiplicador numérico."""
        for cat in cls:
            if abs(cat.multiplier - mult) < 1e-4:
                return cat
        raise ValueError(f"Multiplicador no estándar: {mult}")
