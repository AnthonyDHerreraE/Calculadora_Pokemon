"""
Motor de cálculo de efectividad de tipos Pokémon.
Implementa el cruce matemático de debilidades, resistencias e inmunidades
siguiendo las reglas canónicas de la Generación VI+.
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple, Union
from src.core.constants import ALL_TYPES, TYPE_CHART
from src.core.enums import PokemonType
from src.core.models import TypeEffectivenessResult


class TypeCalculator:
    """
    Calculadora desacoplada de la efectividad elemental.
    Proporciona métodos estáticos y de instancia de alto rendimiento
    para evaluar perfiles defensivos y ofensivos de Pokémon mono-tipo y doble-tipo.
    """

    @classmethod
    def _coerce_type(cls, pokemon_type: Union[PokemonType, str]) -> PokemonType:
        """
        Garantiza que el tipo provisto sea una instancia válida de PokemonType.
        """
        if isinstance(pokemon_type, PokemonType):
            return pokemon_type
        if isinstance(pokemon_type, str):
            return PokemonType.from_string(pokemon_type)
        raise TypeError(
            f"Tipo no admitido: se esperaba 'PokemonType' o 'str', pero se recibió '{type(pokemon_type).__name__}'."
        )

    @classmethod
    def calculate(
        cls,
        primary_type: Union[PokemonType, str],
        secondary_type: Optional[Union[PokemonType, str]] = None,
    ) -> TypeEffectivenessResult:
        """
        Calcula el perfil defensivo completo para un Pokémon con uno o dos tipos.

        Reglas matemáticas:
        - Multiplicador final = Daño(Atacante -> Defensor1) * Daño(Atacante -> Defensor2)
        - Cualquier multiplicador por 0.0 da 0.0 (las inmunidades tienen precedencia absoluta).
        - Si el tipo secundario es None o idéntico al primario, se evalúa como mono-tipo.

        Args:
            primary_type: Tipo primario del Pokémon (Enum o cadena de texto).
            secondary_type: Tipo secundario opcional (Enum, cadena de texto o None).

        Returns:
            TypeEffectivenessResult: Objeto inmutable con la matriz de multiplicadores
            y los agrupamientos semánticos (x4, x2, x1, x0.5, x0.25, x0).

        Raises:
            ValueError: Si alguna cadena de tipo no corresponde a un tipo Pokémon válido.
            TypeError: Si el parámetro recibido no es ni PokemonType ni str.
        """
        def1 = cls._coerce_type(primary_type)
        def2: Optional[PokemonType] = None

        if secondary_type is not None:
            coerced_def2 = cls._coerce_type(secondary_type)
            if coerced_def2 != def1:
                def2 = coerced_def2

        multipliers: Dict[PokemonType, float] = {}

        for atk in ALL_TYPES:
            mult1 = TYPE_CHART[atk][def1]
            if def2 is not None:
                mult2 = TYPE_CHART[atk][def2]
                final_mult = mult1 * mult2
            else:
                final_mult = mult1

            # Normalización numérica por posibles imprecisiones de coma flotante
            if abs(final_mult - 0.0) < 1e-4:
                final_mult = 0.0
            elif abs(final_mult - 0.25) < 1e-4:
                final_mult = 0.25
            elif abs(final_mult - 0.5) < 1e-4:
                final_mult = 0.5
            elif abs(final_mult - 1.0) < 1e-4:
                final_mult = 1.0
            elif abs(final_mult - 2.0) < 1e-4:
                final_mult = 2.0
            elif abs(final_mult - 4.0) < 1e-4:
                final_mult = 4.0

            multipliers[atk] = final_mult

        return TypeEffectivenessResult(
            primary_type=def1,
            secondary_type=def2,
            multipliers=multipliers,
        )

    @classmethod
    def get_offensive_coverage(
        cls,
        attacking_type: Union[PokemonType, str]
    ) -> Dict[PokemonType, float]:
        """
        Retorna la efectividad de daño cuando el tipo especificado ataca
        a cada uno de los 18 tipos puros en defensa.

        Args:
            attacking_type: Tipo atacante.

        Returns:
            Dict[PokemonType, float]: Multiplicadores de daño contra defensores puros.
        """
        atk = cls._coerce_type(attacking_type)
        return dict(TYPE_CHART[atk])

    @classmethod
    def get_defending_multipliers(
        cls,
        primary_type: Union[PokemonType, str],
        secondary_type: Optional[Union[PokemonType, str]] = None,
    ) -> Dict[str, float]:
        """
        Atajo conveniente que retorna un diccionario plano con claves en string
        del tipo atacante y valores numéricos float.
        """
        result = cls.calculate(primary_type, secondary_type)
        return {k.value: v for k, v in result.multipliers.items()}
