import tkinter as tk
from tkinter import ttk
from typing import Optional
from PIL import Image, ImageTk


class Sidebar:
    def __init__(self, parent: tk.Frame, callbacks: dict):
        self.cb = callbacks
        self._thumbnail = None
        self._build(parent)
        self.threshold  = tk.IntVar(value=128)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast   = tk.DoubleVar(value=1.0)

    def _build(self, parent):
        self._frame = tk.Frame(parent, width=220, bg="#f0f0f0",
                               relief=tk.SUNKEN, bd=1)
        self._frame.pack_propagate(False)

        # BOTTOM 
        self._thumb_label = tk.Label(self._frame, bg="#2b2b2b")
        self._thumb_label.pack(side=tk.BOTTOM, pady=(0, 8), padx=10)

        tk.Label(self._frame, text="Oryginał",
                 font=("Helvetica", 8), bg="#f0f0f0", fg="#888"
                 ).pack(side=tk.BOTTOM)

        ttk.Separator(self._frame, orient=tk.HORIZONTAL).pack(
            side=tk.BOTTOM, fill=tk.X, padx=10, pady=4)

        # TOP – nagłówek 
        self._title = tk.Label(self._frame, text="",
                       font=("Helvetica", 11, "bold"),
                       bg="#f0f0f0")
        self._title.pack(side=tk.TOP, pady=(12, 4))
        ttk.Separator(self._frame, orient=tk.HORIZONTAL).pack(
            side=tk.TOP, fill=tk.X, padx=10)

        # Przyciski 
        self._btn_frame = tk.Frame(self._frame, bg="#f0f0f0")
        tk.Button(self._btn_frame, text="✔ Zatwierdź",
                  command=self.cb.get("apply"),
                  bg="#4CAF50", fg="white", relief=tk.FLAT,
                  padx=8, pady=4).pack(fill=tk.X, pady=(0, 4))
        tk.Button(self._btn_frame, text="✘ Anuluj",
                  command=self.cb.get("cancel"),
                  bg="#e53935", fg="white", relief=tk.FLAT,
                  padx=8, pady=4).pack(fill=tk.X)

        # Obszar dynamiczny – zdefiniuj ale nie pakuj
        self._dynamic = tk.Frame(self._frame, bg="#f0f0f0")

    # ── Widoczność ────────────────────────────────────────────

    def show(self):
        self._frame.pack(side=tk.RIGHT, fill=tk.Y)

    def hide(self):
        self._frame.pack_forget()

    # ── Stany ─────────────────────────────────────────────────

    def set_idle(self):
        """Tylko nagłówek + miniaturka."""
        self._title.config(text="Podgląd")
        self._dynamic.pack_forget()
        self._btn_frame.pack_forget()
        self._clear_dynamic()

    def show_filter_controls(self, mode: str):
        """Suwak v przyciski."""
        titles = {
        "binarize":  "Binaryzacja",
        "brightness": "Jasność",
        "contrast":  "Kontrast",
        "gray_avg":  "Skala szarości",
        "gray_human": "Skala szarości",
        "negative":  "Negatyw",
        "avg_filter": "Filtr uśredniający",
        "gauss_filter": "Filtr Gaussa",
        "sharpen_filter": "Filtr wyostrzający",
        "roberts_cross": "Krzyż Robertsa",
        "prewitt_operator": "Operator Prewitta",
        "sobel_operator": "Operator Sobela"
        # "histogram": "Histogram"
        }
        self._title.config(text=titles.get(mode, "Edytor"))
        self._clear_dynamic()
        self._dynamic.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)
        self._btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 8))

        if mode == "binarize":
            self._make_slider("Próg binaryzacji", self.threshold, 0, 255, 1)
        elif mode == "brightness":
            self._make_slider("Jasność", self.brightness, 0.0, 3.0, 0.05)
        elif mode == "contrast":
            self._make_slider("Kontrast", self.contrast, 0.0, 3.0, 0.05)


        # elif mode == "histogram":
        #     # Tworzymy obszar wykresu wewnątrz sekcji dynamicznej
        #     self._hist_canvas = tk.Canvas(self._dynamic, width=200, height=100, 
        #                                   bg="#2b2b2b", highlightthickness=0)
        #     self._hist_canvas.pack(pady=5)
            
        #     tk.Label(self._dynamic, text="Rozkład jasności (0-255)", 
        #              bg="#f0f0f0", fg="#666", font=("Helvetica", 8)).pack()
            
        #     # Możesz zmienić tekst przycisku Zatwierdź na "Zamknij"
        #     for child in self._btn_frame.winfo_children():
        #         if "Zatwierdź" in child.cget("text"):
        #             child.config(text="✔ Ok")


        else:
            tk.Label(self._dynamic,
                     text="Podgląd aktywny.\nZatwierdź lub Anuluj.",
                     bg="#f0f0f0", fg="#555",
                     font=("Helvetica", 9), justify=tk.CENTER
                     ).pack(pady=8)

    def show_info(self, image: Image.Image, path: Optional[str] = None):
        """Informacje o obrazie, bez przycisków."""
        self._title.config(text="Informacje")
        self._clear_dynamic()
        self._btn_frame.pack_forget()
        self._dynamic.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        w, h = image.size
        name = path.split("/")[-1] if path else "—"
        tk.Label(self._dynamic,
                 text=f"Plik:       {name}\n"
                      f"Rozmiar: {w} × {h} px\n"
                      f"Tryb:       {image.mode}\n"
                      f"Piksele:  {w * h:,}",
                 bg="#f0f0f0", font=("Helvetica", 9), justify=tk.LEFT
                 ).pack(anchor=tk.W)
        

    # def update_histogram_plot(self, hist_data: dict):
    #     """Rysuje słupki na Canvasie w sekcji dynamicznej."""
    #     # Sprawdzamy, czy Canvas w ogóle istnieje (czy jesteśmy w trybie histogramu)
    #     if not hasattr(self, '_hist_canvas'): return

    #     self._hist_canvas.delete("all")
        
    #     # Pobieramy max do skalowania (zgodnie z Twoją funkcją compute_histogram)
    #     max_v = max(max(hist_data['R']), max(hist_data['G']), max(hist_data['B']), 1)
    #     w, h = 200, 100
        
    #     for i in range(256):
    #         x = (i / 256) * w
    #         # Rysujemy linie dla każdego kanału
    #         for ch, col in [('R', '#ff4444'), ('G', '#44ff44'), ('B', '#4444ff')]:
    #             val = (hist_data[ch][i] / max_v) * h
    #             if val > 0:
    #                 self._hist_canvas.create_line(x, h, x, h - val, fill=col)


    # ── Miniaturka ────────────────────────────────────────────

    def update_thumbnail(self, image: Image.Image):
        thumb = image.copy()
        thumb.thumbnail((200, 150))
        self._thumbnail = ImageTk.PhotoImage(thumb)
        self._thumb_label.config(image=self._thumbnail)

    # ── Helper ────────────────────────────────────────────────

    def _clear_dynamic(self):
        for w in self._dynamic.winfo_children():
            w.destroy()

    def _make_slider(self, label, variable, from_, to, resolution):
        tk.Label(self._dynamic, text=label, bg="#f0f0f0",
                 font=("Helvetica", 9, "bold"), anchor=tk.W).pack(fill=tk.X)

        val_label = tk.Label(self._dynamic, bg="#f0f0f0",
                             font=("Helvetica", 9), fg="#444")
        val_label.pack(anchor=tk.E)
        val_label.config(text=f"{variable.get():.2f}")

        def on_change(val):
            val_label.config(text=f"{float(val):.2f}")
            cb = self.cb.get("preview")
            if cb: cb()

        tk.Scale(self._dynamic,
                 from_=from_, to=to, resolution=resolution,
                 variable=variable, orient=tk.HORIZONTAL,
                 showvalue=False, command=on_change
                 ).pack(fill=tk.X)