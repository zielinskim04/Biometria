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
        self._image = None      # aktualna PIL.Image
        self._zoom = 1.0 
        self._build(parent)

    def _build(self, parent):
        frame = tk.Frame(parent, bg="#2b2b2b")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Pasek zoom ────────────────────────────────────────
        zoom_bar = tk.Frame(frame, bg="#1e1e1e", pady=2)
        zoom_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(zoom_bar, text="−", command=self.zoom_out,
                  bg="#1e1e1e", fg="white", relief=tk.FLAT,
                  font=("Helvetica", 12), padx=8).pack(side=tk.LEFT, padx=2)

        self._zoom_label = tk.Label(zoom_bar, text="100%",
                                    bg="#1e1e1e", fg="#aaa",
                                    font=("Helvetica", 9), width=6)
        self._zoom_label.pack(side=tk.LEFT)

        tk.Button(zoom_bar, text="+", command=self.zoom_in,
                  bg="#1e1e1e", fg="white", relief=tk.FLAT,
                  font=("Helvetica", 12), padx=8).pack(side=tk.LEFT, padx=2)

        tk.Button(zoom_bar, text="↺ Reset", command=self.zoom_reset,
                  bg="#1e1e1e", fg="#aaa", relief=tk.FLAT,
                  font=("Helvetica", 9), padx=8).pack(side=tk.LEFT, padx=8)

        # ── Canvas ────────────────────────────────────────────
        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        scroll_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(frame, bg="#2b2b2b", cursor="crosshair",
                                xscrollcommand=scroll_x.set,
                                yscrollcommand=scroll_y.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.canvas.yview)
        scroll_x.config(command=self.canvas.xview)

        # ── Skróty klawiszowe ─────────────────────────────────
        self.canvas.bind("<Control-equal>", lambda e: self.zoom_in())
        self.canvas.bind("<Control-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<MouseWheel>",    self._on_mousewheel)

        self._placeholder()

    # ── Zoom ──────────────────────────────────────────────────

    def zoom_in(self):
        self._zoom = min(self._zoom * 1.25, 8.0)   # max 800%
        self._refresh_zoom()

    def zoom_out(self):
        self._zoom = max(self._zoom * 0.8, 0.1)    # min 10%
        self._refresh_zoom()

    def zoom_reset(self):
        self._zoom = 1.0
        self._refresh_zoom()

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def _refresh_zoom(self):
        if self._image is None:
            return
        w, h = self._image.size
        new_w = max(1, int(w * self._zoom))
        new_h = max(1, int(h * self._zoom))
        resized = self._image.resize((new_w, new_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self._zoom_label.config(text=f"{int(self._zoom * 100)}%")

    # ── Wyświetlanie ──────────────────────────────────────────

    def show(self, image: Image.Image):
        self._image = image        # zapamiętaj oryginał do zoomowania
        self._refresh_zoom()       # rysuj z aktualnym zoomem

    def _placeholder(self):
        self.canvas.create_text(400, 300,
                                text="Otwórz zdjęcie:  Plik → Otwórz  lub  Ctrl+O",
                                fill="#888888", font=("Helvetica", 14))
    # def show(self, image: Image.Image) -> None:
    #     """Wyświetl obraz PIL na canvasie."""
    #     self.canvas.delete("all")
    #     self._photo = ImageTk.PhotoImage(image)
    #     self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)
    #     self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    # # def fit_to_window(self, image: Image.Image) -> None:
    # #     """Wyświetl obraz dopasowany do rozmiarów canvasa (podgląd)."""
    # #     w = self.canvas.winfo_width()
    # #     h = self.canvas.winfo_height()
    # #     preview = image.copy()
    # #     preview.thumbnail((w, h))
    # #     self.show(preview)

    # def _placeholder(self) -> None:
    #     self.canvas.create_text(
    #         400, 300,
    #         text="Otwórz zdjęcie:  Plik → Otwórz  lub  Ctrl+O",
    #         fill="#888888",
    #         font=("Helvetica", 14),
    #         tags="placeholder",
    #     )
