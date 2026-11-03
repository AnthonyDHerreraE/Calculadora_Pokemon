"""
Módulo cliente para la integración asíncrona con PokéAPI (v2).
Permite buscar Pokémon por nombre o ID, mapea los tipos canónicos a PokemonType
y maneja hilos secundarios (QThread) para no bloquear la interfaz gráfica.
"""

from __future__ import annotations
import unicodedata
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union
import requests
from PySide6.QtCore import QThread, Signal

from src.core.enums import PokemonType


# Excepciones de Dominio para PokéAPI
class PokeApiError(Exception):
    """Excepción base para fallas al consultar PokéAPI."""
    pass


class PokemonNotFoundError(PokeApiError):
    """Lanzada cuando la API retorna 404 (Pokémon no existente)."""
    pass


class PokeApiNetworkError(PokeApiError):
    """Lanzada por tiempos de espera agotados o fallos de conexión."""
    pass


@dataclass(frozen=True)
class PokemonData:
    """
    Entidad inmutable que encapsula la información defensiva esencial
    recuperada desde PokéAPI.
    """
    id: int
    name: str
    types: Tuple[PokemonType, ...]
    sprite_url: Optional[str] = None

    @property
    def display_title(self) -> str:
        """Formato estandarizado para presentación (ej. '#0448 Lucario')."""
        return f"#{self.id:04d} {self.name.capitalize()}"

    @property
    def types_display_es(self) -> str:
        """Cadena formateada de los tipos en español (ej. 'Lucha / Acero')."""
        return " / ".join(t.display_name_es for t in self.types)


class PokeApiClient:
    """
    Cliente HTTP síncrono con caché local en memoria para consultar la PokéAPI oficial.
    Diseñado para ejecutarse dentro de un worker en hilo secundario (QThread).
    """

    BASE_URL = "https://pokeapi.co/api/v2/pokemon"

    def __init__(self, timeout: float = 6.0) -> None:
        self.timeout = timeout
        self._cache: Dict[str, PokemonData] = {}
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "PokemonTypeCalculator-PySide6/1.0 (DesktopApp)",
            "Accept": "application/json",
        })

    @staticmethod
    def normalize_query(query: Union[str, int]) -> str:
        """
        Normaliza el nombre o identificador para compatibilidad con los endpoints de PokéAPI.
        Ejemplos: 'Tapu Koko' -> 'tapu-koko', 'Mr. Mime' -> 'mr-mime', 'Flabébé' -> 'flabebe'.
        """
        if isinstance(query, int):
            return str(query)

        text = query.strip().lower()
        # Eliminar diacríticos (ej. Flabébé -> flabebe)
        normalized = unicodedata.normalize("NFKD", text)
        clean = "".join(c for c in normalized if not unicodedata.combining(c))

        # Reemplazar espacios y caracteres especiales
        clean = clean.replace(".", "").replace("'", "").replace(":", "").replace(" ", "-")
        return clean

    def fetch_pokemon(self, name_or_id: Union[str, int]) -> PokemonData:
        """
        Consulta la PokéAPI y retorna un objeto PokemonData con sus tipos validados.

        Args:
            name_or_id: Nombre en inglés o ID numérico en la Pokédex Nacional.

        Returns:
            PokemonData: Datos validados del Pokémon y sus tipos mapeados.

        Raises:
            PokemonNotFoundError: Si el Pokémon no existe (HTTP 404).
            PokeApiNetworkError: Si hay timeout o error de red.
            PokeApiError: Si la respuesta contiene datos malformados.
        """
        clean_key = self.normalize_query(name_or_id)
        if not clean_key:
            raise ValueError("El parámetro de búsqueda no puede estar vacío.")

        # Retorno inmediato desde caché en memoria si ya fue consultado
        if clean_key in self._cache:
            return self._cache[clean_key]

        url = f"{self.BASE_URL}/{clean_key}"

        try:
            response = self._session.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise PokeApiNetworkError(f"Tiempo de espera agotado al conectar con PokéAPI ({self.timeout}s).") from e
        except requests.exceptions.RequestException as e:
            raise PokeApiNetworkError(f"Error de red al consultar PokéAPI: {e}") from e

        if response.status_code == 404:
            raise PokemonNotFoundError(f"No se encontró ningún Pokémon con el nombre o ID '{name_or_id}'.")
        elif response.status_code != 200:
            raise PokeApiError(f"Respuesta inesperada del servidor (HTTP {response.status_code}).")

        try:
            data = response.json()
            pokemon_id = int(data["id"])
            pokemon_name = str(data["name"])

            # PokéAPI ordena los tipos por la clave 'slot' (slot 1 = primario, slot 2 = secundario)
            sorted_types = sorted(data["types"], key=lambda x: x["slot"])
            parsed_types = []
            for t in sorted_types:
                raw_type_name = t["type"]["name"]
                parsed_types.append(PokemonType.from_string(raw_type_name))

            # Obtener arte oficial o sprite frontal
            sprites = data.get("sprites", {})
            other = sprites.get("other", {})
            official_artwork = other.get("official-artwork", {})
            sprite_url = official_artwork.get("front_default") or sprites.get("front_default")

            result = PokemonData(
                id=pokemon_id,
                name=pokemon_name,
                types=tuple(parsed_types[:2]),
                sprite_url=sprite_url,
            )

            # Almacenar en caché por nombre e ID para futuras búsquedas instantáneas
            self._cache[clean_key] = result
            self._cache[str(pokemon_id)] = result
            self._cache[pokemon_name.lower()] = result

            return result

        except (KeyError, ValueError, TypeError) as e:
            raise PokeApiError(f"Error al procesar la respuesta JSON de PokéAPI: {e}") from e


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
        client: Optional[PokeApiClient] = None,
        parent: Optional[QThread] = None,
    ) -> None:
        super().__init__(parent)
        self.query = query
        self.client = client or PokeApiClient()

    def run(self) -> None:
        """Punto de ejecución en el hilo secundario del sistema operativo."""
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
