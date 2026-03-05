"""
file.py
───────
Odpowiada wyłącznie za operacje na plikach:
otwieranie, zapisywanie, wybór ścieżki.
Nie importuje nic z Tkinter (oprócz dialogów).
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

    def open_image(self) -> Optional[Image.Image]:
        """Otwiera dialog i zwraca obiekt PIL.Image lub None."""
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

    def save(self, image: Optional[Image.Image]) -> bool:
        """Zapisuje pod tą samą ścieżką. Jeśli brak ścieżki – wywołuje save_as."""
        if image is None:
            messagebox.showwarning("Uwaga", "Brak obrazu do zapisania.")
            return False
        if self.path is None:
            return self.save_as(image)
        return self._write(image, self.path)

    def save_as(self, image: Optional[Image.Image]) -> bool:
        """Otwiera dialog 'Zapisz jako' i zapisuje plik."""
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

    def _write(self, image: Image.Image, path: str) -> bool:
        """Właściwy zapis – obsługa wyjątków."""
        try:
            image.save(path)
            return True
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać pliku:\n{e}")
            return False
