"""
Controlador de estado para la selección interactiva de tipos de Pokémon.
Mantiene desacoplada la vista (widgets) de la lógica de negocio y estado.
"""

from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal

from src.core.enums import PokemonType


class TypeSelectionController(QObject):
    """
    Controlador reactivo que administra la selección de hasta 2 tipos defensores.

    Señales:
        selection_changed (tuple): Emite la tupla actualizada de tipos seleccionados.
        selection_cleared (): Notifica que la selección ha sido restablecida a cero.
    """

    selection_changed = Signal(tuple)
    selection_cleared = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._selected_types: List[PokemonType] = []

    @property
    def selected_types(self) -> Tuple[PokemonType, ...]:
        """Tupla inmutable de los tipos actualmente seleccionados (longitud 0, 1 o 2)."""
        return tuple(self._selected_types)

    @property
    def count(self) -> int:
        """Cantidad de tipos seleccionados actualmente."""
        return len(self._selected_types)

    def is_selected(self, pokemon_type: PokemonType) -> bool:
        """Verifica si un tipo específico se encuentra activo en la selección."""
        return pokemon_type in self._selected_types

    def get_slot_index(self, pokemon_type: PokemonType) -> Optional[int]:
        """
        Retorna la posición de ranura de selección (1 para Tipo Primario, 2 para Secundario),
        o None si no está seleccionado.
        """
        try:
            return self._selected_types.index(pokemon_type) + 1
        except ValueError:
            return None

    def toggle_type(self, pokemon_type: PokemonType) -> None:
        """
        Alterna la selección de un tipo aplicando la regla de negocio de hasta 2 tipos:
        - Si el tipo ya está seleccionado: lo deselecciona.
        - Si hay menos de 2 tipos seleccionados: lo agrega al final.
        - Si ya hay 2 tipos seleccionados y se pulsa un tercero: deselecciona el primero
          (FIFO: First-In, First-Out) y añade el nuevo en segunda posición.
        """
        if pokemon_type in self._selected_types:
            self._selected_types.remove(pokemon_type)
        else:
            if len(self._selected_types) >= 2:
                # Política FIFO: el tipo más antiguo cede su lugar
                self._selected_types.pop(0)
            self._selected_types.append(pokemon_type)

        self.selection_changed.emit(self.selected_types)

    def clear_selection(self) -> None:
        """Restablece la selección vaciando todos los tipos activos."""
        if self._selected_types:
            self._selected_types.clear()
            self.selection_cleared.emit()
            self.selection_changed.emit(())

    def set_selection(self, types: Tuple[PokemonType, ...]) -> None:
        """Establece programáticamente una combinación específica de tipos."""
        self._selected_types = list(types[:2])
        self.selection_changed.emit(self.selected_types)
