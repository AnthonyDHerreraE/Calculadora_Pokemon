"""
Núcleo del dominio (Core Domain) de la Calculadora de Tipos Pokémon.
Exporta las clases, enumeraciones, constantes y cliente de red.
"""

from src.core.enums import PokemonType, EffectivenessCategory
from src.core.constants import TYPE_CHART, ALL_TYPES
from src.core.models import TypeEffectivenessResult
from src.core.calculator import TypeCalculator
from src.core.pokeapi import (
    PokeApiClient,
    PokemonData,
    PokemonSearchWorker,
    PokeApiError,
    PokemonNotFoundError,
    PokeApiNetworkError,
)

__all__ = [
    "PokemonType",
    "EffectivenessCategory",
    "TYPE_CHART",
    "ALL_TYPES",
    "TypeEffectivenessResult",
    "TypeCalculator",
    "PokeApiClient",
    "PokemonData",
    "PokemonSearchWorker",
    "PokeApiError",
    "PokemonNotFoundError",
    "PokeApiNetworkError",
]
