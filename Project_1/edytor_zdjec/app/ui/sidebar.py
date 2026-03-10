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
        "sobel_operator": "Operator Sobela",
        "histogram": "Histogram",
        "equalize_histogram": "Wyrównanie histogramu"
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


        elif mode == "histogram":
            self._btn_frame.pack_forget()

            # Główny kontener na wszystkie wykresy
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
            
        elif mode == "projections":
            self._btn_frame.pack_forget()
            info = [("H", "Projekcja pozioma"),
                    ('V', 'Projekcja pionowa')]
            
            # DO dokonczenia

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
                      f"Piksele:  {w * h:,}",
                 bg="#f0f0f0", font=("Helvetica", 9), justify=tk.LEFT
                 ).pack(anchor=tk.W)
        

# jeden histogram
    # def update_histogram_plot(self, hist_data: dict):
    #     if not hasattr(self, '_hist_canvas'): return
    #     self._hist_canvas.delete("all")
        
    #     w, h = 200, 100
    #     margin_x = 15  # Odrobinę większy margines na tekst
    #     margin_y = 15  # Miejsce na napisy pod spodem
    #     draw_w = w - 2 * margin_x
    #     draw_h = h - margin_y - 5 # -5 dla odstępu od góry

    #     max_v = max(max(hist_data['R']), max(hist_data['G']), max(hist_data['B']), 1)
    #     is_gray = (list(hist_data['R']) == list(hist_data['G']) == list(hist_data['B']))

    #     # 1. Rysujemy oś poziomą (podstawę), żeby było wiadomo gdzie jest 0-255
    #     self._hist_canvas.create_line(margin_x, draw_h, margin_x + draw_w, draw_h, fill="#666666")

    #     # 2. Dodajemy napisy 0 i 255
    #     self._hist_canvas.create_text(margin_x, draw_h + 8, text="0", fill="#888888", font=("Arial", 7))
    #     self._hist_canvas.create_text(margin_x + draw_w, draw_h + 8, text="255", fill="#888888", font=("Arial", 7))

    #     # 3. Rysujemy dane
    #     for i in range(256):
    #         x = margin_x + (i / 255) * draw_w
            
    #         if is_gray:
    #             val = (hist_data['R'][i] / max_v) * draw_h
    #             if val > 0:
    #                 # Rysujemy od dołu do góry względem naszej nowej osi draw_h
    #                 self._hist_canvas.create_rectangle(x, draw_h, x + 1, draw_h - val, 
    #                                                    fill="white", outline="white")
    #         else:
    #             for ch, col in [('R', '#ff4444'), ('G', '#44ff44'), ('B', '#4444ff')]:
    #                 val = (hist_data[ch][i] / max_v) * draw_h
    #                 if val > 0:
    #                     self._hist_canvas.create_line(x, draw_h, x, draw_h - val, fill=col)


    def update_histogram_plot(self, hist_data: dict):
        if not hasattr(self, '_channels'): return

        # Sprawdzamy czy jest szary
        is_gray = (list(hist_data['R']) == list(hist_data['G']) == list(hist_data['B']))

        w, h = 200, 60
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
        draw_h = h - 15  # Linia bazowa (oś)
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