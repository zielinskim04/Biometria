"""
status_bar.py
─────────────
Pasek statusu na dole okna. Tylko widgety Tkinter, zero logiki.
Wyświetla komunikaty i wymiary aktualnego obrazu.
"""

import tkinter as tk
from typing import Optional
from PIL import Image


class StatusBar:
    def __init__(self, root: tk.Tk):
        self._build(root)

    def _build(self, root: tk.Tk):
        bar = tk.Frame(root, bd=1, relief=tk.SUNKEN, bg="#dcdcdc")
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Tekst po lewej – komunikaty
        self._text = tk.Label(bar, text="Gotowy. Otwórz plik, aby rozpocząć.",
                              anchor=tk.W, bg="#dcdcdc", font=("Helvetica", 9))
        self._text.pack(side=tk.LEFT, padx=6)

        # Wymiary po prawej
        self._dims = tk.Label(bar, text="", anchor=tk.E,
                              bg="#dcdcdc", font=("Helvetica", 9))
        self._dims.pack(side=tk.RIGHT, padx=6)

    def set_text(self, message: str) -> None:
        """Ustaw tekst komunikatu."""
        self._text.config(text=message)

    def set_info(self, image: Image.Image, path: Optional[str] = None) -> None:
        """Zaktualizuj tekst i wymiary na podstawie obrazu."""
        w, h = image.size
        name = path.split("/")[-1] if path else ""
        self._text.config(text=f"Otwarto: {name}")
        self._dims.config(text=f"{w} × {h} px  |  {image.mode}")

    def clear_dims(self) -> None:
        self._dims.config(text="")
