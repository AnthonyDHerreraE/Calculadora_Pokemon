"""
Modelos de datos inmutables y fuertemente tipados para representar
los resultados del cálculo de efectividad de tipos.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple
from src.core.enums import EffectivenessCategory, PokemonType


@dataclass(frozen=True)
class TypeEffectivenessResult:
    """
    Representa el resultado exhaustivo del análisis defensivo de una combinación
    de 1 o 2 tipos de Pokémon frente a todos los tipos atacantes posibles.
    """
    primary_type: PokemonType
    secondary_type: Optional[PokemonType]
    multipliers: Mapping[PokemonType, float]

    @property
    def is_dual_type(self) -> bool:
        """Indica si el resultado corresponde a una combinación de dos tipos distintos."""
        return self.secondary_type is not None and self.secondary_type != self.primary_type

    @property
    def defending_types(self) -> Tuple[PokemonType, ...]:
        """Tupla con los tipos defensores activos."""
        if self.is_dual_type and self.secondary_type is not None:
            return (self.primary_type, self.secondary_type)
        return (self.primary_type,)

    @property
    def quad_weaknesses(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes que causan daño súper eficaz x4."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 4.0) < 1e-4)

    @property
    def weaknesses(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes que causan daño eficaz x2."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 2.0) < 1e-4)

    @property
    def neutral(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes que causan daño regular x1."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 1.0) < 1e-4)

    @property
    def resistances(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes que causan daño reducido x0.5."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 0.5) < 1e-4)

    @property
    def double_resistances(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes que causan daño súper reducido x0.25."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 0.25) < 1e-4)

    @property
    def immunities(self) -> Tuple[PokemonType, ...]:
        """Tipos atacantes frente a los cuales el defensor es totalmente inmune (x0)."""
        return tuple(t for t, m in self.multipliers.items() if abs(m - 0.0) < 1e-4)

    def get_multiplier(self, attacking_type: PokemonType | str) -> float:
        """
        Devuelve el multiplicador numérico frente a un tipo atacante específico.
        """
        if isinstance(attacking_type, str):
            attacking_type = PokemonType.from_string(attacking_type)
        return self.multipliers[attacking_type]

    def get_category(self, attacking_type: PokemonType | str) -> EffectivenessCategory:
        """
        Devuelve la categoría de efectividad correspondiente a un tipo atacante.
        """
        mult = self.get_multiplier(attacking_type)
        return EffectivenessCategory.from_multiplier(mult)

    def grouped_by_multiplier(self) -> Dict[float, List[PokemonType]]:
        """
        Agrupa los tipos atacantes en un diccionario ordenado por multiplicador
        de mayor vulnerabilidad a mayor resistencia.
        """
        result: Dict[float, List[PokemonType]] = {
            4.0: list(self.quad_weaknesses),
            2.0: list(self.weaknesses),
            1.0: list(self.neutral),
            0.5: list(self.resistances),
            0.25: list(self.double_resistances),
            0.0: list(self.immunities),
        }
        return result

    def grouped_by_category(self) -> Dict[EffectivenessCategory, List[PokemonType]]:
        """
        Agrupa los tipos atacantes según su categoría semántica.
        """
        return {
            EffectivenessCategory.QUAD_WEAKNESS: list(self.quad_weaknesses),
            EffectivenessCategory.WEAKNESS: list(self.weaknesses),
            EffectivenessCategory.NEUTRAL: list(self.neutral),
            EffectivenessCategory.RESISTANCE: list(self.resistances),
            EffectivenessCategory.DOUBLE_RESISTANCE: list(self.double_resistances),
            EffectivenessCategory.IMMUNITY: list(self.immunities),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta el resultado a una estructura de diccionario nativo, ideal
        para serialización JSON o consumo directo por la capa de presentación (GUI).
        """
        return {
            "defending_types": [t.value for t in self.defending_types],
            "is_dual_type": self.is_dual_type,
            "multipliers": {t.value: m for t, m in self.multipliers.items()},
            "quad_weaknesses": [t.value for t in self.quad_weaknesses],
            "weaknesses": [t.value for t in self.weaknesses],
            "neutral": [t.value for t in self.neutral],
            "resistances": [t.value for t in self.resistances],
            "double_resistances": [t.value for t in self.double_resistances],
            "immunities": [t.value for t in self.immunities],
        }

    def summary(self, lang: str = "es") -> str:
        """
        Genera un informe formateado en texto plano para visualización en consola.
        """
        if lang == "es":
            names = " / ".join(t.display_name_es for t in self.defending_types)
            header = f"=== Perfil Defensivo: {names} ==="
            sections = [
                ("Vulnerabilidad Extrema (x4):", self.quad_weaknesses, lambda t: t.display_name_es),
                ("Debilidades (x2):", self.weaknesses, lambda t: t.display_name_es),
                ("Daño Normal (x1):", self.neutral, lambda t: t.display_name_es),
                ("Resistencias (x0.5):", self.resistances, lambda t: t.display_name_es),
                ("Súper Resistencias (x0.25):", self.double_resistances, lambda t: t.display_name_es),
                ("Inmunidades (x0):", self.immunities, lambda t: t.display_name_es),
            ]
        else:
            names = " / ".join(t.display_name_en for t in self.defending_types)
            header = f"=== Defensive Profile: {names} ==="
            sections = [
                ("Quad Weaknesses (x4):", self.quad_weaknesses, lambda t: t.display_name_en),
                ("Weaknesses (x2):", self.weaknesses, lambda t: t.display_name_en),
                ("Neutral (x1):", self.neutral, lambda t: t.display_name_en),
                ("Resistances (x0.5):", self.resistances, lambda t: t.display_name_en),
                ("Double Resistances (x0.25):", self.double_resistances, lambda t: t.display_name_en),
                ("Immunities (x0):", self.immunities, lambda t: t.display_name_en),
            ]

        lines = [header]
        for label, items, format_fn in sections:
            items_str = ", ".join(format_fn(t) for t in items) if items else "-"
            lines.append(f"  {label:<30} [{len(items):02d}] -> {items_str}")
        lines.append("=" * len(header))
        return "\n".join(lines)
