"""
canvas.py
─────────
Obszar roboczy z obrazem. Tylko widgety Tkinter, zero logiki.
Wyświetla obiekt PIL.Image na tk.Canvas z paskami przewijania.
"""

import tkinter as tk
from PIL import Image, ImageTk


class ImageCanvas:
    def __init__(self, parent: tk.Frame):
        self._photo = None   # referencja – zapobiega garbage collection
        self._build(parent)

    def _build(self, parent: tk.Frame):
        frame = tk.Frame(parent, bg="#2b2b2b")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        scroll_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            frame,
            bg="#2b2b2b",
            cursor="crosshair",
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.canvas.yview)
        scroll_x.config(command=self.canvas.xview)

        self._placeholder()

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ PODEPNIJ ZDARZENIA MYSZY                 ║
        # ║                                                  ║
        # ║  self.canvas.bind("<B1-Motion>",    ...)         ║
        # ║  self.canvas.bind("<ButtonPress-1>",...)         ║
        # ║  self.canvas.bind("<ButtonRelease-1>",...)       ║
        # ╚══════════════════════════════════════════════════╝

    def show(self, image: Image.Image) -> None:
        """Wyświetl obraz PIL na canvasie."""
        self.canvas.delete("all")
        self._photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def fit_to_window(self, image: Image.Image) -> None:
        """Wyświetl obraz dopasowany do rozmiarów canvasa (podgląd)."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        preview = image.copy()
        preview.thumbnail((w, h))
        self.show(preview)

    def _placeholder(self) -> None:
        self.canvas.create_text(
            400, 300,
            text="Otwórz zdjęcie:  Plik → Otwórz  lub  Ctrl+O",
            fill="#888888",
            font=("Helvetica", 14),
            tags="placeholder",
        )
