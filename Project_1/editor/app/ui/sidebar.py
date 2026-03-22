import tkinter as tk
from tkinter import ttk
from typing import Optional
from PIL import Image, ImageTk
import numpy as np

class Sidebar:
    def __init__(self, parent: tk.Frame, callbacks: dict):
        self.cb = callbacks
        self._thumbnail = None 
        self._build(parent)
        self.threshold  = tk.IntVar(value=128) # Do binaryzacji
        self.brightness = tk.DoubleVar(value=1.0) # Do jasności
        self.contrast   = tk.DoubleVar(value=1.0) # Do kontrastu
        self.power_trans = tk.DoubleVar(value=1.0) # Do potęgowania
        self.sigma       = tk.DoubleVar(value=1.0) #Do filtru Gaussa
        self.filter_size = tk.IntVar(value=3)       # Rozmiar kernela 3/5/7
        self.sharpen_preset = tk.StringVar(value="mean_removal") # Preset dla filtru wyostrzającego
        self.custom_kernel_entries = [] # Lista Entry dla własnego kernela
        self.morph_size  = tk.IntVar(value=3) # Rozmiar elementu strukturyzującego (operacje morfologiczne)
        self.morph_shape = tk.StringVar(value="rect") # Kształt eleentu struktuzyjącego (operacje morfologiczne)
        self.hom_preset = tk.StringVar(value="isolated") # Preset dla operacji hit-or-miss

    def _build(self, parent):
        self._frame = tk.Frame(parent, width=250, bg="#f0f0f0",
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

        # Część, która zmienia się w zależności od aktywnego filtra
        self._dynamic = tk.Frame(self._frame, bg="#f0f0f0")

    # ── Widoczność ────────────────────────────────────────────

    def show(self):
        self._frame.pack(side=tk.RIGHT, fill=tk.Y)

    def hide(self):
        self._frame.pack_forget()

    # ── Stany ─────────────────────────────────────────────────

    # Tylko nagłówek i minaiturka.
    def set_idle(self):
        self._title.config(text="Podgląd")
        self._dynamic.pack_forget()
        self._btn_frame.pack_forget()
        self._clear_dynamic()

    # Pokazanie suwaka lub przycisków w zależności od trybu.
    def show_filter_controls(self, mode: str):
        titles = {
        "binarize":  "Binaryzacja",
        "brightness": "Jasność",
        "contrast":  "Kontrast",
        "gray_avg":  "Skala szarości",
        "gray_human": "Skala szarości",
        "negative":  "Negatyw",
        "power_trans": "Potęgowanie",
        "log_trans": "Logarytmowanie",
        "avg_filter": "Filtr uśredniający",
        "gauss_filter": "Filtr Gaussa",
        "sharpen_filter": "Filtr wyostrzający",
        "custom_filter": "Własny filtr",
        "roberts_cross": "Krzyż Robertsa",
        "prewitt_operator": "Operator Prewitta",
        "sobel_operator": "Operator Sobela",
        "histogram": "Histogram",
        "equalize_histogram": "Wyrównanie histogramu",
        "erosion":  "Erozja", 
        "dilation": "Dylatacja",
        "opening":  "Otwarcie",
        "closing":  "Zamknięcie",
        "hit_or_miss": "Hit-or-Miss",
        "skeletonize": "Szkieletowanie",
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
        elif mode == "power_trans":
            self._make_slider("Potęgowanie", self.power_trans, 0.0, 3.0, 0.05)
        elif mode == "avg_filter":
            self._set_kernel_size()
        elif mode == "gauss_filter":
            self._set_kernel_size()
            self._make_slider("Sigma", self.sigma, 0.1, 5.0, 0.1)
        elif mode == "sharpen_filter":
            self._make_preset_selector()
        elif mode == "custom_filter":
            self._make_custom_kernel()
        elif mode == "histogram":
            self._btn_frame.pack_forget()

            self._hist_container = tk.Frame(self._dynamic, bg="#f0f0f0")
            self._hist_container.pack(fill=tk.BOTH, expand=True)

            self._channels = {}
            colors_info = [('R', 'Red', '#ff4444'), ('G', 'Green', '#44ff44'), ('B', 'Blue', '#4444ff')]
            
            for ch, label, col in colors_info:
                # Ramka dla kazdego koloru
                frame = tk.Frame(self._hist_container, bg="#f0f0f0")
                
                lbl = tk.Label(frame, text=label, bg="#f0f0f0", fg=col, font=("Arial", 7, "bold"))
                lbl.pack()
                
                canvas = tk.Canvas(frame, width=200, height=60, bg="#1a1a1a", highlightthickness=0)
                canvas.pack()
                
                self._channels[ch] = {'frame': frame, 'canvas': canvas, 'label': lbl, 'default_col': col}

            self._close_btn = tk.Button(self._dynamic, text="Zamknij", 
                      command=self.set_idle, bg="#9e9e9e", fg="white")

        elif mode in ("erosion", "dilation", "opening", "closing"):
            self._make_morphology_controls() 
        elif mode == "hit_or_miss":
            self._make_hit_or_miss_controls()
        elif mode == "skeletonize":
            self._make_slider("Próg binaryzacji", self.threshold, 0, 255, 1)
        else:
            tk.Label(self._dynamic,
                     text="Podgląd aktywny.\nZatwierdź lub Anuluj.",
                     bg="#f0f0f0", fg="#555",
                     font=("Helvetica", 9), justify=tk.CENTER
                     ).pack(pady=8)

    # ── Info ────────────────────────────────────────────────
    def show_info(self, info: dict):
        self._title.config(text="Informacje")
        self._clear_dynamic()
        self._btn_frame.pack_forget()
        self._dynamic.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        for label, value in info.items():
            row = tk.Frame(self._dynamic, bg="#f0f0f0")
            row.pack(fill=tk.X, pady=1)

            tk.Label(row, text=f"{label}:", bg="#f0f0f0",
                    font=("Helvetica", 8, "bold"),
                    anchor=tk.W, width=14).pack(side=tk.LEFT)

            tk.Label(row, text=value, bg="#f0f0f0",
                    font=("Helvetica", 8),
                    anchor=tk.W, wraplength=120,
                    justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X)
        
    # ── Histogram ────────────────────────────────────────────────
    def update_histogram_plot(self, hist_data: dict):
        if not hasattr(self, '_channels'): return

        # Sprawdzamy czy jest szary
        is_gray = (list(hist_data['R']) == list(hist_data['G']) == list(hist_data['B']))

        w, h = 230, 70
        margin_x = 10
        draw_w = w - 2 * margin_x

        # Ukrywamy przyciski na poczatek
        for ch in ['R', 'G', 'B']:
            self._channels[ch]['frame'].pack_forget()
        
        if hasattr(self, '_close_btn'):
            self._close_btn.pack_forget()

        if is_gray:
            # TRYB SZARY
            f_info = self._channels['R']
            f_info['frame'].pack(pady=2, fill=tk.X)
            f_info['label'].config(text="Histogram Szarości", fg="black")
            self._draw_single_channel('R', hist_data['R'], "white", draw_w, margin_x, h)
        else:
            # TRYB KOLOROWY
            for ch in ['R', 'G', 'B']:
                f_info = self._channels[ch]
                f_info['frame'].pack(pady=2, fill=tk.X)
                f_info['label'].config(text=f"Kanał {ch}", fg="black")
                self._draw_single_channel(ch, hist_data[ch], f_info['default_col'], draw_w, margin_x, h)

        if hasattr(self, '_close_btn'):
            self._close_btn.pack(fill=tk.X, pady=10)


    def _draw_single_channel(self, ch, data, color, draw_w, margin_x, h):
        canvas = self._channels[ch]['canvas']
        canvas.delete("all")
        
        # Marginesy wewnątrz małego canvasu
        padding_top = 10
        draw_h = h - 15 
        available_h = draw_h - padding_top 
        
        max_v = max(data) if max(data) > 0 else 1

        # Szara oś
        canvas.create_line(margin_x, draw_h, margin_x + draw_w, draw_h, fill="#888888")

        for i in range(256):
            x = margin_x + (i / 255) * draw_w
            val = (data[i] / max_v) * available_h
            
            if val > 0:
                canvas.create_rectangle(x, draw_h, x + 1, draw_h - val, 
                                        fill=color, outline=color)

    # ── Miniaturka ────────────────────────────────────────────
    def update_thumbnail(self, image: Image.Image):
        thumb = image.copy()
        thumb.thumbnail((230, 160))
        self._thumbnail = ImageTk.PhotoImage(thumb)
        self._thumb_label.config(image=self._thumbnail)

    # ── Helper ────────────────────────────────────────────────
    def _clear_dynamic(self):
        for w in self._dynamic.winfo_children():
            w.destroy()

    # ── Do filtrów ────────────────────────────────────────────────
    # Slider do binaryzacji, jasności, kontrastu i sigma dla Gaussa
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

    # Slider do wyboru rozmiaru kernela dla filtrów uśredniającego i Gaussa    
    def _set_kernel_size(self):
        #Sigma
        tk.Label(self._dynamic, text="Rozmiar kernela",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X)

        btn_frame = tk.Frame(self._dynamic, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=4)

        #Rozmiar kernela
        for size in [3, 5, 7]:
            tk.Radiobutton(btn_frame, text=f"{size}×{size}",
                        variable=self.filter_size, value=size,
                        bg="#f0f0f0", command=lambda: self.cb.get("preview") and self.cb.get("preview")()
                        ).pack(side=tk.LEFT, padx=4)
            
    # Preset dla filtru wyostrzającego        
    def _make_preset_selector(self):
        tk.Label(self._dynamic, text="Preset wyostrzania",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X)

        presets = {
        "mean_removal": "Mean Removal",
        "HP1": "HP1",
        "HP2": "HP2",
        "HP3": "HP3",
        }
        for key, label in presets.items():
            tk.Radiobutton(self._dynamic, text=label,
                        variable=self.sharpen_preset, value=key,
                        bg="#f0f0f0",
                        command=lambda: self.cb.get("preview") and self.cb.get("preview")()
                        ).pack(anchor=tk.W, padx=4)
            
    # ── Własny kernel ────────────────────────────────────────────────       
    def _make_custom_kernel(self):
        tk.Label(self._dynamic, text="Rozmiar siatki",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X, pady=(0, 4))

        size_frame = tk.Frame(self._dynamic, bg="#f0f0f0")
        size_frame.pack(fill=tk.X, pady=(0, 6))

        self.custom_size = tk.IntVar(value=3)

        for s in [2, 3, 4, 5, 6, 7]:
            tk.Radiobutton(size_frame, text=str(s), variable=self.custom_size,
                        value=s, bg="#f0f0f0",
                        command=self._rebuild_custom_grid
                        ).pack(side=tk.LEFT, padx=2)

        tk.Label(self._dynamic, text="Wagi kernela",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X, pady=(0, 4))

        # Ramka na siatkę 
        self._grid_frame = tk.Frame(self._dynamic, bg="#f0f0f0")
        self._grid_frame.pack()

        self.custom_kernel_entries = []
        self._build_custom_grid(3)   

        tk.Button(self._dynamic, text="Podgląd",
                command=lambda: self.cb.get("preview") and self.cb.get("preview")(),
                relief=tk.FLAT, bg="#2196F3", fg="white",
                padx=6, pady=2).pack(pady=(6, 0))

    def _build_custom_grid(self, size: int):
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self.custom_kernel_entries = []

        for i in range(size):
            for j in range(size):
                default = 1 if (i == size//2 and j == size//2) else 0
                e = tk.Entry(self._grid_frame, width=4, justify=tk.CENTER,
                            font=("Helvetica", 9))
                e.insert(0, str(default))
                e.grid(row=i, column=j, padx=1, pady=1)
                self.custom_kernel_entries.append(e)

    # Przepudowuje siatkę, gdy zmieni sie rozmiar
    def _rebuild_custom_grid(self):
        self._build_custom_grid(self.custom_size.get())

    def get_custom_kernel(self):
        size = self.custom_size.get()
        vals = [float(e.get()) for e in self.custom_kernel_entries]
        return np.array(vals, dtype='float32').reshape(size, size)

    # ── Operacje morfologiczne ────────────────────────────────────────────────  
    # Rozmiar i kształt elementu struktuzyjącego
    def _make_morphology_controls(self):
        # Rozmiar
        tk.Label(self._dynamic, text="Rozmiar elementu strukturyzującego",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W, wraplength=190).pack(fill=tk.X)

        self.morph_size = tk.IntVar(value=3)
        size_frame = tk.Frame(self._dynamic, bg="#f0f0f0")
        size_frame.pack(fill=tk.X, pady=4)
        for s in [3, 5, 7, 9]:
            tk.Radiobutton(size_frame, text=str(s), variable=self.morph_size,
                        value=s, bg="#f0f0f0",
                        command=lambda: self.cb.get("preview") and self.cb.get("preview")()
                        ).pack(side=tk.LEFT, padx=4)

        # Kształt
        tk.Label(self._dynamic, text="Kształt elementu",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X, pady=(8, 0))

        self.morph_shape = tk.StringVar(value="rect")
        shapes = [
            ("Prostokąt",      "rect"),
            ("Krzyż",          "cross"),
            ("Elipsa",         "ellipse"),
            ("Linia pozioma",  "horizontal"),
            ("Linia pionowa",  "vertical"),
        ]
        for label, val in shapes:
            tk.Radiobutton(self._dynamic, text=label,
                        variable=self.morph_shape, value=val,
                        bg="#f0f0f0",
                        command=lambda: self.cb.get("preview") and self.cb.get("preview")()
                        ).pack(anchor=tk.W, padx=4)
            
    def _make_hit_or_miss_controls(self):
        # Próg binaryzacji
        self._make_slider("Próg binaryzacji", self.threshold, 0, 255, 1)

        # Wybór presetu
        tk.Label(self._dynamic, text="Wzorzec",
                bg="#f0f0f0", font=("Helvetica", 9, "bold"),
                anchor=tk.W).pack(fill=tk.X, pady=(8, 4))

        self.hom_preset = tk.StringVar(value="isolated")
        presets = [
            ("Izolowany piksel", "isolated"),
            ("Kwadrat 2×2",      "square_2x2"),
            ("Krzyż",            "cross"),
            ("Przekątna ↖",      "diagonal_tl"),
            ("Przekątna ↘",      "diagonal_br"),
        ]
        for label, val in presets:
            tk.Radiobutton(self._dynamic, text=label,
                        variable=self.hom_preset, value=val,
                        bg="#f0f0f0",
                        command=lambda: self.cb.get("preview") and self.cb.get("preview")()
                        ).pack(anchor=tk.W, padx=4)