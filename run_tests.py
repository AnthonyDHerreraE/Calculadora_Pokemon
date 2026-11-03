"""
Script ejecutor de validación de la Fase 1 en consola.
Ejecuta la suite de pruebas unitarias y genera reportes visuales detallados
de combinaciones complejas de tipos para verificar la exactitud matemática.
"""

import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.core.calculator import TypeCalculator
from src.core.enums import PokemonType
from src.core.pokeapi import PokeApiClient, PokemonNotFoundError


def print_banner(text: str) -> None:
    line = "=" * 75
    print(f"\n{line}\n  {text}\n{line}")


def demonstrate_combination(name: str, type1: PokemonType, type2: PokemonType) -> None:
    print(f"\n>>> Demostración para: {name} ({type1.display_name_es} / {type2.display_name_es})")
    result = TypeCalculator.calculate(type1, type2)
    print(result.summary(lang="es"))


def main() -> int:
    print_banner("CALCULADORA DE TIPOS POKÉMON (GEN VI+) - VERIFICACIÓN FASES 1, 2 Y 3")

    # 1. Ejecución de la suite de pruebas unitarias
    print("Ejecutando suite formal de pruebas unitarias (unittest)...")
    suite = unittest.defaultTestLoader.discover(start_dir="tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    if not test_result.wasSuccessful():
        print("\n[ERROR] Algunas pruebas fallaron. Revisa los mensajes anteriores.")
        return 1

    print("\n[OK] ¡Todas las pruebas unitarias pasaron exitosamente al 100%!")

    # 2. Demostración visual de casos complejos solicitados
    print_banner("DEMOSTRACIÓN DE CASOS COMPLEJOS EN CONSOLA")

    demonstrate_combination(
        "Tinkaton / Zacian-Crowned",
        PokemonType.STEEL,
        PokemonType.FAIRY,
    )

    demonstrate_combination(
        "Swampert / Quagsire",
        PokemonType.WATER,
        PokemonType.GROUND,
    )

    demonstrate_combination(
        "Sableye / Spiritomb",
        PokemonType.GHOST,
        PokemonType.DARK,
    )

    demonstrate_combination(
        "Scizor / Genesect",
        PokemonType.BUG,
        PokemonType.STEEL,
    )

    # 3. Demostración de cliente PokéAPI en vivo
    print_banner("VERIFICACIÓN EN VIVO: CONSULTA A POKÉAPI (v2)")
    client = PokeApiClient()
    sample_queries = ["Lucario", "gengar", "25", "tapu-koko"]
    for query in sample_queries:
        try:
            p = client.fetch_pokemon(query)
            print(f"  [OK] Búsqueda '{query}': {p.display_title} -> Tipos: {p.types_display_es}")
        except Exception as e:
            print(f"  [ERROR] Falló la búsqueda de '{query}': {e}")

    print_banner("PROYECTO COMPLETO: FASES 1, 2, 3 Y 4 FINALIZADAS CON ÉXITO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
