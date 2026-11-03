"""
Conjunto exhaustivo de pruebas unitarias para validar la precisión matemática
de la matriz de tipos de Generación VI+ y el motor de cálculo TypeCalculator.
"""

import unittest
from src.core.enums import PokemonType, EffectivenessCategory
from src.core.constants import TYPE_CHART, ALL_TYPES
from src.core.calculator import TypeCalculator
from src.core.models import TypeEffectivenessResult


class TestTypeMatrixIntegrity(unittest.TestCase):
    """Pruebas de integridad estructural y canonicidad de la matriz de efectividades."""

    def test_matrix_dimensions(self) -> None:
        """Verifica que la matriz contenga exactamente los 18 tipos elementales (18x18 = 324 cruces)."""
        self.assertEqual(len(ALL_TYPES), 18)
        self.assertEqual(len(TYPE_CHART), 18)
        for atk_type, defenders in TYPE_CHART.items():
            self.assertEqual(
                len(defenders),
                18,
                f"El tipo atacante {atk_type} no tiene 18 defensores definidos."
            )

    def test_valid_multiplier_values(self) -> None:
        """Verifica que todos los valores de la matriz base sean estándar (0.0, 0.5, 1.0, 2.0)."""
        valid_multipliers = {0.0, 0.5, 1.0, 2.0}
        for atk, defenders in TYPE_CHART.items():
            for defender, mult in defenders.items():
                self.assertIn(
                    mult,
                    valid_multipliers,
                    f"Multiplicador inválido {mult} en {atk} -> {defender}"
                )

    def test_gen6_steel_nerf(self) -> None:
        """Verifica que en Gen VI+, Acero NO resista Fantasma ni Siniestro (daño 1.0x)."""
        self.assertEqual(TYPE_CHART[PokemonType.GHOST][PokemonType.STEEL], 1.0)
        self.assertEqual(TYPE_CHART[PokemonType.DARK][PokemonType.STEEL], 1.0)

    def test_gen6_fairy_interactions(self) -> None:
        """Verifica las reglas oficiales introducidas con el tipo Hada."""
        # Hada defiende: inmune a Dragón, débil a Veneno y Acero, resiste Lucha, Bicho, Siniestro
        self.assertEqual(TYPE_CHART[PokemonType.DRAGON][PokemonType.FAIRY], 0.0)
        self.assertEqual(TYPE_CHART[PokemonType.POISON][PokemonType.FAIRY], 2.0)
        self.assertEqual(TYPE_CHART[PokemonType.STEEL][PokemonType.FAIRY], 2.0)
        self.assertEqual(TYPE_CHART[PokemonType.FIGHTING][PokemonType.FAIRY], 0.5)
        self.assertEqual(TYPE_CHART[PokemonType.BUG][PokemonType.FAIRY], 0.5)
        self.assertEqual(TYPE_CHART[PokemonType.DARK][PokemonType.FAIRY], 0.5)


class TestMonoTypeCalculations(unittest.TestCase):
    """Pruebas para perfiles de Pokémon con un único tipo elemental."""

    def test_pure_normal(self) -> None:
        """Verifica el perfil defensivo del tipo Normal puro."""
        res = TypeCalculator.calculate(PokemonType.NORMAL)
        self.assertFalse(res.is_dual_type)
        self.assertEqual(res.weaknesses, (PokemonType.FIGHTING,))
        self.assertEqual(res.immunities, (PokemonType.GHOST,))
        self.assertEqual(len(res.resistances), 0)
        self.assertEqual(len(res.neutral), 16)

    def test_pure_ghost(self) -> None:
        """Verifica el perfil defensivo del tipo Fantasma puro."""
        res = TypeCalculator.calculate(PokemonType.GHOST)
        self.assertCountEqual(res.immunities, [PokemonType.NORMAL, PokemonType.FIGHTING])
        self.assertCountEqual(res.weaknesses, [PokemonType.GHOST, PokemonType.DARK])
        self.assertCountEqual(res.resistances, [PokemonType.POISON, PokemonType.BUG])

    def test_pure_steel(self) -> None:
        """Verifica el perfil defensivo del tipo Acero puro en Gen VI+."""
        res = TypeCalculator.calculate(PokemonType.STEEL)
        self.assertCountEqual(res.weaknesses, [PokemonType.FIRE, PokemonType.FIGHTING, PokemonType.GROUND])
        self.assertCountEqual(res.immunities, [PokemonType.POISON])
        self.assertEqual(len(res.resistances), 10)
        self.assertIn(PokemonType.FAIRY, res.resistances)
        # Neutros: Agua, Eléctrico, Fantasma, Siniestro
        self.assertCountEqual(
            res.neutral,
            [PokemonType.WATER, PokemonType.ELECTRIC, PokemonType.GHOST, PokemonType.DARK]
        )


class TestDualTypeComplexCombinations(unittest.TestCase):
    """Pruebas para combinaciones compuestas de doble tipo requeridas explícitamente."""

    def test_steel_fairy(self) -> None:
        """
        Caso de prueba: Acero / Hada (Ej. Zacian-C, Tinkaton, Mawile, Klefki).
        Debilidades (x2): Fuego, Tierra.
        Neutros (x1): Agua, Eléctrico, Lucha, Fantasma, Acero.
        Resistencias (x0.5): Normal, Planta, Hielo, Volador, Psíquico, Roca, Siniestro, Hada (8 tipos).
        Súper Resistencia (x0.25): Bicho (1 tipo).
        Inmunidades (x0): Veneno, Dragón (2 tipos).
        """
        res = TypeCalculator.calculate(PokemonType.STEEL, PokemonType.FAIRY)
        self.assertTrue(res.is_dual_type)
        self.assertEqual(len(res.quad_weaknesses), 0)
        self.assertCountEqual(res.weaknesses, [PokemonType.FIRE, PokemonType.GROUND])
        self.assertCountEqual(
            res.neutral,
            [PokemonType.WATER, PokemonType.ELECTRIC, PokemonType.FIGHTING, PokemonType.GHOST, PokemonType.STEEL]
        )
        self.assertCountEqual(
            res.resistances,
            [
                PokemonType.NORMAL, PokemonType.GRASS, PokemonType.ICE,
                PokemonType.FLYING, PokemonType.PSYCHIC, PokemonType.ROCK,
                PokemonType.DARK, PokemonType.FAIRY
            ]
        )
        self.assertCountEqual(res.double_resistances, [PokemonType.BUG])
        self.assertCountEqual(res.immunities, [PokemonType.POISON, PokemonType.DRAGON])
        # Validación de cruces específicos
        self.assertEqual(res.get_multiplier(PokemonType.POISON), 0.0)  # Inmunidad de Acero anula debilidad de Hada
        self.assertEqual(res.get_multiplier(PokemonType.DRAGON), 0.0)  # Inmunidad de Hada anula resistencia de Acero
        self.assertEqual(res.get_multiplier(PokemonType.FIGHTING), 1.0) # Acero (x2) * Hada (x0.5) = x1.0

    def test_water_ground(self) -> None:
        """
        Caso de prueba: Agua / Tierra (Ej. Swampert, Quagsire, Gastrodon).
        Súper Débil (x4): Planta.
        Débil (x2): Ninguno.
        Inmune (x0): Eléctrico (Tierra anula debilidad de Agua).
        Resistente (x0.5): Fuego, Veneno, Roca, Acero (4 tipos).
        Súper Resistente (x0.25): Ninguno.
        Neutros (x1): 12 tipos (incluyendo Agua, ya que Agua resiste Agua 0.5x
                      pero Tierra es débil a Agua 2.0x, cancelándose a 1.0x).
        """
        res = TypeCalculator.calculate(PokemonType.WATER, PokemonType.GROUND)
        self.assertCountEqual(res.quad_weaknesses, [PokemonType.GRASS])
        self.assertEqual(len(res.weaknesses), 0)
        self.assertCountEqual(res.immunities, [PokemonType.ELECTRIC])
        self.assertEqual(len(res.double_resistances), 0)
        self.assertCountEqual(
            res.resistances,
            [PokemonType.FIRE, PokemonType.POISON, PokemonType.ROCK, PokemonType.STEEL]
        )
        self.assertEqual(len(res.neutral), 12)
        self.assertEqual(res.get_multiplier(PokemonType.ELECTRIC), 0.0)
        self.assertEqual(res.get_multiplier(PokemonType.GRASS), 4.0)
        self.assertEqual(res.get_multiplier(PokemonType.WATER), 1.0)
        self.assertEqual(res.get_multiplier(PokemonType.STEEL), 0.5)

    def test_ghost_dark(self) -> None:
        """
        Caso de prueba: Fantasma / Siniestro (Ej. Spiritomb, Sableye).
        En Gen VI+, su única debilidad es Hada (x2).
        Inmunidades (x0): Normal, Lucha, Psíquico.
        Resistencias (x0.5): Veneno.
        Neutro (x1): Los 13 tipos restantes.
        """
        res = TypeCalculator.calculate(PokemonType.GHOST, PokemonType.DARK)
        self.assertCountEqual(res.weaknesses, [PokemonType.FAIRY])
        self.assertEqual(len(res.quad_weaknesses), 0)
        self.assertCountEqual(
            res.immunities,
            [PokemonType.NORMAL, PokemonType.FIGHTING, PokemonType.PSYCHIC]
        )
        self.assertCountEqual(res.resistances, [PokemonType.POISON])
        self.assertEqual(len(res.neutral), 13)

    def test_bug_steel(self) -> None:
        """
        Caso de prueba: Bicho / Acero (Ej. Scizor, Genesect, Forretress).
        Vulnerabilidad extrema (x4): Fuego.
        Inmunidad (x0): Veneno.
        Súper Resistente (x0.25): Planta.
        Resistente (x0.5): Normal, Hielo, Psíquico, Bicho, Dragón, Acero, Hada (7 tipos).
        Neutro (x1): Agua, Eléctrico, Lucha, Tierra, Volador, Roca, Fantasma, Siniestro (8 tipos).
        Nota: Roca es neutro (1x) porque Bicho es débil (x2) y Acero lo resiste (x0.5).
        """
        res = TypeCalculator.calculate(PokemonType.BUG, PokemonType.STEEL)
        self.assertCountEqual(res.quad_weaknesses, [PokemonType.FIRE])
        self.assertEqual(len(res.weaknesses), 0)
        self.assertCountEqual(res.immunities, [PokemonType.POISON])
        self.assertCountEqual(res.double_resistances, [PokemonType.GRASS])
        self.assertCountEqual(
            res.resistances,
            [
                PokemonType.NORMAL, PokemonType.ICE, PokemonType.PSYCHIC,
                PokemonType.BUG, PokemonType.DRAGON, PokemonType.STEEL, PokemonType.FAIRY
            ]
        )
        self.assertEqual(len(res.resistances), 7)
        self.assertEqual(len(res.neutral), 8)
        self.assertEqual(res.get_multiplier(PokemonType.ROCK), 1.0)
        self.assertEqual(res.get_multiplier(PokemonType.FIRE), 4.0)


class TestCalculatorBehaviorAndEdgeCases(unittest.TestCase):
    """Pruebas de comportamiento matemático, conmutatividad y manejo de errores."""

    def test_commutativity(self) -> None:
        """El orden de los tipos no debe alterar el resultado: f(A, B) == f(B, A)."""
        res1 = TypeCalculator.calculate(PokemonType.WATER, PokemonType.GROUND)
        res2 = TypeCalculator.calculate(PokemonType.GROUND, PokemonType.WATER)
        self.assertEqual(res1.multipliers, res2.multipliers)

        res_sf1 = TypeCalculator.calculate(PokemonType.STEEL, PokemonType.FAIRY)
        res_sf2 = TypeCalculator.calculate(PokemonType.FAIRY, PokemonType.STEEL)
        self.assertEqual(res_sf1.multipliers, res_sf2.multipliers)

    def test_duplicate_types_collapsing(self) -> None:
        """Si se pasa el mismo tipo dos veces, se debe tratar con gracia como mono-tipo."""
        res_mono = TypeCalculator.calculate(PokemonType.FIRE)
        res_dual_same = TypeCalculator.calculate(PokemonType.FIRE, PokemonType.FIRE)
        self.assertFalse(res_dual_same.is_dual_type)
        self.assertEqual(res_mono.multipliers, res_dual_same.multipliers)

    def test_string_parsing_and_bilingual_support(self) -> None:
        """Valida que acepte strings en español/inglés, con tildes y mayúsculas."""
        res_es = TypeCalculator.calculate("acero", "hada")
        res_en = TypeCalculator.calculate("Steel", "FAIRY")
        res_accents = TypeCalculator.calculate("eléctrico", "dragón")
        self.assertEqual(res_es.defending_types, (PokemonType.STEEL, PokemonType.FAIRY))
        self.assertEqual(res_en.defending_types, (PokemonType.STEEL, PokemonType.FAIRY))
        self.assertEqual(res_accents.defending_types, (PokemonType.ELECTRIC, PokemonType.DRAGON))

    def test_invalid_type_raises_error(self) -> None:
        """Valida excepciones controladas ante tipos inválidos."""
        with self.assertRaises(ValueError):
            TypeCalculator.calculate("tipo_inventado")

        with self.assertRaises(TypeError):
            TypeCalculator.calculate(12345)  # type: ignore

    def test_model_serialization(self) -> None:
        """Verifica que to_dict y summary produzcan estructuras consistentes."""
        res = TypeCalculator.calculate(PokemonType.STEEL, PokemonType.FAIRY)
        data = res.to_dict()
        self.assertIn("multipliers", data)
        self.assertIn("quad_weaknesses", data)
        self.assertEqual(data["immunities"], ["poison", "dragon"])

        summary = res.summary(lang="es")
        self.assertIn("Acero / Hada", summary)
        self.assertIn("Inmunidades (x0)", summary)


if __name__ == "__main__":
    unittest.main()
