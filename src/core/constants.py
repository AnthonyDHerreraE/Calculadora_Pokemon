"""
Matriz de efectividades elementales de Pokémon (Generación VI en adelante).
Define con exactitud matemática el multiplicador de daño de cada tipo atacante
contra cada tipo defensor.

Reglas canónicas Gen VI+:
- Inclusión del tipo Hada (Fairy).
- Inmunidad de Hada frente a ataques de Dragón.
- Acero pierde resistencias frente a Siniestro y Fantasma (ahora reciben daño x1.0).
"""

from typing import Dict, Final
from types import MappingProxyType
from src.core.enums import PokemonType

# Multiplicadores elementales
IMMUNE: Final[float] = 0.0
RESIST: Final[float] = 0.5
NORMAL: Final[float] = 1.0
SUPER: Final[float] = 2.0

# Modificaciones explícitas sobre el daño base neutro (1.0)
# Estructura: {TIPO_ATACANTE: {TIPO_DEFENSOR: MULTIPLICADOR}}
_RAW_TYPE_CHART_OVERRIDES: Final[Dict[PokemonType, Dict[PokemonType, float]]] = {
    PokemonType.NORMAL: {
        PokemonType.ROCK: RESIST,
        PokemonType.GHOST: IMMUNE,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.FIRE: {
        PokemonType.FIRE: RESIST,
        PokemonType.WATER: RESIST,
        PokemonType.GRASS: SUPER,
        PokemonType.ICE: SUPER,
        PokemonType.BUG: SUPER,
        PokemonType.ROCK: RESIST,
        PokemonType.DRAGON: RESIST,
        PokemonType.STEEL: SUPER,
    },
    PokemonType.WATER: {
        PokemonType.FIRE: SUPER,
        PokemonType.WATER: RESIST,
        PokemonType.GRASS: RESIST,
        PokemonType.GROUND: SUPER,
        PokemonType.ROCK: SUPER,
        PokemonType.DRAGON: RESIST,
    },
    PokemonType.GRASS: {
        PokemonType.FIRE: RESIST,
        PokemonType.WATER: SUPER,
        PokemonType.GRASS: RESIST,
        PokemonType.POISON: RESIST,
        PokemonType.GROUND: SUPER,
        PokemonType.FLYING: RESIST,
        PokemonType.BUG: RESIST,
        PokemonType.ROCK: SUPER,
        PokemonType.DRAGON: RESIST,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.ELECTRIC: {
        PokemonType.WATER: SUPER,
        PokemonType.ELECTRIC: RESIST,
        PokemonType.GRASS: RESIST,
        PokemonType.GROUND: IMMUNE,
        PokemonType.FLYING: SUPER,
        PokemonType.DRAGON: RESIST,
    },
    PokemonType.ICE: {
        PokemonType.FIRE: RESIST,
        PokemonType.WATER: RESIST,
        PokemonType.GRASS: SUPER,
        PokemonType.ICE: RESIST,
        PokemonType.GROUND: SUPER,
        PokemonType.FLYING: SUPER,
        PokemonType.DRAGON: SUPER,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.FIGHTING: {
        PokemonType.NORMAL: SUPER,
        PokemonType.ICE: SUPER,
        PokemonType.POISON: RESIST,
        PokemonType.FLYING: RESIST,
        PokemonType.PSYCHIC: RESIST,
        PokemonType.BUG: RESIST,
        PokemonType.ROCK: SUPER,
        PokemonType.GHOST: IMMUNE,
        PokemonType.DARK: SUPER,
        PokemonType.STEEL: SUPER,
        PokemonType.FAIRY: RESIST,
    },
    PokemonType.POISON: {
        PokemonType.GRASS: SUPER,
        PokemonType.POISON: RESIST,
        PokemonType.GROUND: RESIST,
        PokemonType.ROCK: RESIST,
        PokemonType.GHOST: RESIST,
        PokemonType.STEEL: IMMUNE,
        PokemonType.FAIRY: SUPER,
    },
    PokemonType.GROUND: {
        PokemonType.FIRE: SUPER,
        PokemonType.ELECTRIC: SUPER,
        PokemonType.GRASS: RESIST,
        PokemonType.POISON: SUPER,
        PokemonType.FLYING: IMMUNE,
        PokemonType.BUG: RESIST,
        PokemonType.ROCK: SUPER,
        PokemonType.STEEL: SUPER,
    },
    PokemonType.FLYING: {
        PokemonType.ELECTRIC: RESIST,
        PokemonType.GRASS: SUPER,
        PokemonType.FIGHTING: SUPER,
        PokemonType.BUG: SUPER,
        PokemonType.ROCK: RESIST,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.PSYCHIC: {
        PokemonType.FIGHTING: SUPER,
        PokemonType.POISON: SUPER,
        PokemonType.PSYCHIC: RESIST,
        PokemonType.DARK: IMMUNE,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.BUG: {
        PokemonType.FIRE: RESIST,
        PokemonType.GRASS: SUPER,
        PokemonType.FIGHTING: RESIST,
        PokemonType.POISON: RESIST,
        PokemonType.FLYING: RESIST,
        PokemonType.PSYCHIC: SUPER,
        PokemonType.GHOST: RESIST,
        PokemonType.DARK: SUPER,
        PokemonType.STEEL: RESIST,
        PokemonType.FAIRY: RESIST,
    },
    PokemonType.ROCK: {
        PokemonType.FIRE: SUPER,
        PokemonType.ICE: SUPER,
        PokemonType.FIGHTING: RESIST,
        PokemonType.GROUND: RESIST,
        PokemonType.FLYING: SUPER,
        PokemonType.BUG: SUPER,
        PokemonType.STEEL: RESIST,
    },
    PokemonType.GHOST: {
        PokemonType.NORMAL: IMMUNE,
        PokemonType.PSYCHIC: SUPER,
        PokemonType.GHOST: SUPER,
        PokemonType.DARK: RESIST,
    },
    PokemonType.DRAGON: {
        PokemonType.DRAGON: SUPER,
        PokemonType.STEEL: RESIST,
        PokemonType.FAIRY: IMMUNE,
    },
    PokemonType.DARK: {
        PokemonType.FIGHTING: RESIST,
        PokemonType.PSYCHIC: SUPER,
        PokemonType.GHOST: SUPER,
        PokemonType.DARK: RESIST,
        PokemonType.FAIRY: RESIST,
    },
    PokemonType.STEEL: {
        PokemonType.FIRE: RESIST,
        PokemonType.WATER: RESIST,
        PokemonType.ELECTRIC: RESIST,
        PokemonType.ICE: SUPER,
        PokemonType.ROCK: SUPER,
        PokemonType.STEEL: RESIST,
        PokemonType.FAIRY: SUPER,
    },
    PokemonType.FAIRY: {
        PokemonType.FIRE: RESIST,
        PokemonType.FIGHTING: SUPER,
        PokemonType.POISON: RESIST,
        PokemonType.DRAGON: SUPER,
        PokemonType.DARK: SUPER,
        PokemonType.STEEL: RESIST,
    },
}


def _build_complete_matrix() -> Dict[PokemonType, Dict[PokemonType, float]]:
    """
    Construye la matriz densa de 18x18 inicializando todos los cruces a 1.0 (daño neutro)
    y aplicando los modificadores elementales de la Generación VI+.
    """
    matrix: Dict[PokemonType, Dict[PokemonType, float]] = {}
    for atk in PokemonType:
        matrix[atk] = {}
        overrides = _RAW_TYPE_CHART_OVERRIDES.get(atk, {})
        for defender in PokemonType:
            matrix[atk][defender] = overrides.get(defender, NORMAL)
    return matrix


# Matriz densa completa inmutable en tiempo de ejecución
TYPE_CHART: Final[Dict[PokemonType, Dict[PokemonType, float]]] = _build_complete_matrix()

# Lista canónica ordenada de todos los tipos
ALL_TYPES: Final[tuple[PokemonType, ...]] = tuple(PokemonType)
