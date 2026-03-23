"""
history.py
──────────
Mechanizm cofania zmian (Ctrl+Z).
Przechowuje listę stanów obrazu (PIL.Image).

Użycie w main_frame.py:
    self.history.push(nowy_obraz)     # przed każdą modyfikacją
    obraz = self.history.undo()       # cofnij
    obraz = self.history.current()    # pobierz aktualny stan
"""

from typing import Optional
from PIL import Image

# Maksymalna liczba stanów w historii
MAX_HISTORY = 10 

class History:
    def __init__(self):
        self._stack: list[Image.Image] = []

    #Czyści historię i ustawia nowy obraz jako stan początkowy. Przy otwieraniu nowego pliku używany
    def reset(self, image: Image.Image) -> None:
        self._stack = [image.copy()]

    # Zapisuje nowy stan obrazu
    def push(self, image: Image.Image) -> None:
        self._stack.append(image.copy())
        if len(self._stack) > MAX_HISTORY:
            self._stack.pop(0)   

    # Cofa ostatnią operację, zwraca poprzedni stan
    def undo(self) -> Optional[Image.Image]:
        if len(self._stack) <= 1:
            return None
        self._stack.pop()
        return self._stack[-1].copy()

    # Zwraca aktualny stan obrazu bez modyfikowania historii
    def current(self) -> Optional[Image.Image]:
        if not self._stack:
            return None
        return self._stack[-1].copy()

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def can_undo(self) -> bool:
        return len(self._stack) > 1
