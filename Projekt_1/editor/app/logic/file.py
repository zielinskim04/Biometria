"""
file.py
───────
Odpowiada wyłącznie za operacje na plikach:
otwieranie, zapisywanie, wybór ścieżki.
"""

from tkinter import filedialog, messagebox
from typing import Optional
from PIL import Image


SUPPORTED_OPEN = [
    ("Obrazy", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
    ("Wszystkie pliki", "*.*"),
]

SUPPORTED_SAVE = [
    ("PNG",  "*.png"),
    ("JPEG", "*.jpg *.jpeg"),
    ("BMP",  "*.bmp"),
    ("Wszystkie pliki", "*.*"),
]


class FileHandler:
    def __init__(self):
        self.path: str | None = None   # ścieżka aktualnie otwartego pliku

    # Otwiera dialog i zwraca obiekt PIL.Image lub None.
    def open_image(self) -> Optional[Image.Image]:
        path = filedialog.askopenfilename(
            title="Otwórz zdjęcie",
            filetypes=SUPPORTED_OPEN,
        )
        if not path:
            return None
        try:
            image = Image.open(path)
            self.path = path
            return image
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć pliku:\n{e}")
            return None

    # Zapisuje pod pod podaną ścieżką.
    def save_as(self, image: Optional[Image.Image]) -> bool:
        if image is None:
            messagebox.showwarning("Uwaga", "Brak obrazu do zapisania.")
            return False
        path = filedialog.asksaveasfilename(
            title="Zapisz jako",
            defaultextension=".png",
            filetypes=SUPPORTED_SAVE,
        )
        if not path:
            return False
        self.path = path
        return self._write(image, path)
    
    # Zapisuje pod tą samą ścieżką. Jeśli brak ścieżki – wywołuje save_as.
    def save(self, image: Optional[Image.Image]) -> bool:
        if image is None:
            messagebox.showwarning("Uwaga", "Brak obrazu do zapisania.")
            return False
        if self.path is None:
            return self.save_as(image)
        return self._write(image, self.path)

    # Właściwy zapis
    def _write(self, image: Image.Image, path: str) -> bool:
        try:
            image.save(path)
            return True
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać pliku:\n{e}")
            return False
