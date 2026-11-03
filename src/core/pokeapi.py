"""
Módulo cliente híbrido para la búsqueda de Pokémon (Local-First + PokéAPI Fallback).
Consulta en primer lugar una base de datos local JSON (custom_pokedex.json) para soportar
Pokémon de fan-games (ej. Pokémon Uranium) sin latencia ni llamadas de red.
Si no se encuentra localmente, delega la consulta a la PokéAPI oficial en segundo plano (QThread).
"""

from __future__ import annotations
import json
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import requests
from PySide6.QtCore import QThread, Signal

from src.core.enums import PokemonType


# Excepciones de Dominio para Búsqueda
class PokeApiError(Exception):
    """Excepción base para fallas al consultar PokéAPI."""
    pass


class PokemonNotFoundError(PokeApiError):
    """Lanzada cuando el Pokémon no existe ni en la Pokédex local ni en PokéAPI."""
    pass


class PokeApiNetworkError(PokeApiError):
    """Lanzada por tiempos de espera agotados o fallos de conexión."""
    pass


@dataclass(frozen=True)
class PokemonData:
    """
    Entidad inmutable que encapsula la información esencial de un Pokémon.
    Soporta Pokémon canónicos oficiales y creaciones de fan-games.
    """
    id: int
    name: str
    types: Tuple[PokemonType, ...]
    sprite_url: Optional[str] = None
    is_custom: bool = False

    @property
    def display_title(self) -> str:
        """Formato estandarizado para presentación en la UI."""
        if self.is_custom or self.id <= 0:
            return f"{self.name.capitalize()} (Fan-Game)"
        return f"#{self.id:04d} {self.name.capitalize()}"

    @property
    def types_display_es(self) -> str:
        """Cadena formateada de los tipos en español (ej. 'Normal / Nuclear')."""
        return " / ".join(t.display_name_es for t in self.types)


class HybridPokemonClient:
    """
    Cliente de repositorio híbrido (Local-First con fallback a PokéAPI).
    - Fase 1: Búsqueda local en custom_pokedex.json (resolución en 0ms).
    - Fase 2: Consulta HTTP remota hacia PokéAPI v2 con sesión y caché en memoria.
    """

    BASE_URL = "https://pokeapi.co/api/v2/pokemon"

    def __init__(
        self,
        custom_pokedex_path: Optional[Union[str, Path]] = None,
        timeout: float = 6.0,
    ) -> None:
        self.timeout = timeout
        self._cache: Dict[str, PokemonData] = {}
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "PokemonTypeCalculator-PySide6/1.0 (DesktopApp)",
            "Accept": "application/json",
        })

        # Cargar base de datos local de fan-games
        if custom_pokedex_path is None:
            base_meipass = getattr(sys, "_MEIPASS", None)
            if base_meipass:
                custom_pokedex_path = Path(base_meipass) / "src" / "data" / "custom_pokedex.json"
            else:
                custom_pokedex_path = (
                    Path(__file__).resolve().parent.parent / "data" / "custom_pokedex.json"
                )
        self.custom_pokedex_path = Path(custom_pokedex_path)
        self._custom_pokedex: Dict[str, Any] = self._load_custom_pokedex()

    def _load_custom_pokedex(self) -> Dict[str, Any]:
        """Carga el diccionario local desde el archivo JSON si existe."""
        if not self.custom_pokedex_path.is_file():
            return {}
        try:
            with open(self.custom_pokedex_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def normalize_query(query: Union[str, int]) -> str:
        """
        Normaliza el nombre o identificador (minúsculas, sin acentos ni espacios).
        Ejemplos: 'Tapu Koko' -> 'tapu-koko', 'Flabébé' -> 'flabebe', 'Nucleon' -> 'nucleon'.
        """
        if isinstance(query, int):
            return str(query)

        text = query.strip().lower()
        normalized = unicodedata.normalize("NFKD", text)
        clean = "".join(c for c in normalized if not unicodedata.combining(c))
        clean = clean.replace(".", "").replace("'", "").replace(":", "").replace(" ", "-")
        return clean

    def get_local_pokemon(self, name_or_id: Union[str, int]) -> Optional[PokemonData]:
        """
        Busca el Pokémon en la base de datos local JSON (custom_pokedex.json).
        Retorna inmediatamente el objeto PokemonData o None si no se encuentra.
        """
        clean_key = self.normalize_query(name_or_id)
        if not clean_key or clean_key not in self._custom_pokedex:
            return None

        raw_entry = self._custom_pokedex[clean_key]

        # Soporta formato lista: ["normal", "nuclear"] o formato objeto: {"types": [...], "id": ...}
        if isinstance(raw_entry, list):
            types_list = [PokemonType.from_string(t) for t in raw_entry]
            p_id = 0
            p_name = clean_key.capitalize()
        elif isinstance(raw_entry, dict):
            types_list = [PokemonType.from_string(t) for t in raw_entry.get("types", [])]
            p_id = int(raw_entry.get("id", 0))
            p_name = str(raw_entry.get("name", clean_key.capitalize()))
        else:
            return None

        if not types_list:
            return None

        return PokemonData(
            id=p_id,
            name=p_name,
            types=tuple(types_list[:2]),
            is_custom=True,
        )

    def fetch_pokemon(self, name_or_id: Union[str, int]) -> PokemonData:
        """
        Estrategia de búsqueda híbrida:
        1. Resuelve localmente desde custom_pokedex.json si coincide.
        2. Verifica la caché en memoria de consultas previas.
        3. Realiza la solicitud HTTP hacia PokéAPI oficial.
        """
        clean_key = self.normalize_query(name_or_id)
        if not clean_key:
            raise ValueError("El parámetro de búsqueda no puede estar vacío.")

        # 1. Búsqueda local en el diccionario custom (0ms)
        local_match = self.get_local_pokemon(clean_key)
        if local_match is not None:
            return local_match

        # 2. Retorno desde caché en memoria si ya fue consultado
        if clean_key in self._cache:
            return self._cache[clean_key]

        # 3. Fallback a PokéAPI oficial
        url = f"{self.BASE_URL}/{clean_key}"

        try:
            response = self._session.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise PokeApiNetworkError(f"Tiempo de espera agotado al conectar con PokéAPI ({self.timeout}s).") from e
        except requests.exceptions.RequestException as e:
            raise PokeApiNetworkError(f"Error de red al consultar PokéAPI: {e}") from e

        if response.status_code == 404:
            raise PokemonNotFoundError(
                f"No se encontró '{name_or_id}' ni en la Pokédex local ni en la PokéAPI oficial."
            )
        elif response.status_code != 200:
            raise PokeApiError(f"Respuesta inesperada del servidor (HTTP {response.status_code}).")

        try:
            data = response.json()
            pokemon_id = int(data["id"])
            pokemon_name = str(data["name"])

            sorted_types = sorted(data["types"], key=lambda x: x["slot"])
            parsed_types = [PokemonType.from_string(t["type"]["name"]) for t in sorted_types]

            sprites = data.get("sprites", {})
            other = sprites.get("other", {})
            official_artwork = other.get("official-artwork", {})
            sprite_url = official_artwork.get("front_default") or sprites.get("front_default")

            result = PokemonData(
                id=pokemon_id,
                name=pokemon_name,
                types=tuple(parsed_types[:2]),
                sprite_url=sprite_url,
                is_custom=False,
            )

            self._cache[clean_key] = result
            self._cache[str(pokemon_id)] = result
            self._cache[pokemon_name.lower()] = result

            return result

        except (KeyError, ValueError, TypeError) as e:
            raise PokeApiError(f"Error al procesar la respuesta JSON de PokéAPI: {e}") from e


# Alias retrocompatible
PokeApiClient = HybridPokemonClient


class PokemonSearchWorker(QThread):
    """
    Trabajador asíncrono en hilo secundario (QThread) que ejecuta la consulta de red
    sin bloquear el hilo principal de la interfaz gráfica de PySide6.
    """

    search_started = Signal(str)
    pokemon_found = Signal(object)  # Emite PokemonData
    search_failed = Signal(str)     # Emite mensaje legible de error
    search_finished = Signal()

    def __init__(
        self,
        query: str,
        client: Optional[HybridPokemonClient] = None,
        parent: Optional[QThread] = None,
    ) -> None:
        super().__init__(parent)
        self.query = query
        self.client = client or HybridPokemonClient()

    def run(self) -> None:
        """Ejecuta la búsqueda en el hilo secundario."""
        self.search_started.emit(self.query)
        try:
            pokemon_data = self.client.fetch_pokemon(self.query)
            self.pokemon_found.emit(pokemon_data)
        except PokemonNotFoundError as e:
            self.search_failed.emit(str(e))
        except PokeApiNetworkError as e:
            self.search_failed.emit(str(e))
        except Exception as e:
            self.search_failed.emit(f"Error inesperado: {e}")
        finally:
            self.search_finished.emit()
