# """
# sidebar.py
# ──────────
# Panel boczny z suwakami, opcjami i informacjami o obrazie.
# Tylko widgety Tkinter, zero logiki.

# Callbacks wymagane:
#     apply  – przycisk "Zastosuj zmiany"
# """

# import tkinter as tk
# from tkinter import ttk
# from typing import Optional
# from PIL import Image


# class Sidebar:
#     def __init__(self, parent: tk.Frame, callbacks: dict):
#         self.cb = callbacks
#         self._build(parent)

#     # def _build(self, parent: tk.Frame):
#     #     frame = tk.Frame(parent, width=220, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
#     #     frame.pack(side=tk.RIGHT, fill=tk.Y)
#     #     frame.pack_propagate(False)

#     #     # ── Nagłówek ──────────────────────────────────────────
#     #     tk.Label(frame, text="Ustawienia", font=("Helvetica", 11, "bold"),
#     #              bg="#f0f0f0").pack(pady=(12, 4))
#     #     ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

#     #     # ── Suwaki ────────────────────────────────────────────
#     #     # W metodzie _build() w sidebar.py, zamiast placeholdera:

#     #     # Binaryzacja – suwak progu
#     #     self.threshold = tk.IntVar(value=128)
#     #     tk.Label(frame, text="Próg binaryzacji", bg="#f0f0f0",
#     #             font=("Helvetica", 8)).pack(pady=(8,0))
        
#     #     tk.Scale(frame,
#     #         from_=0, to=255,
#     #         variable=self.threshold,
#     #         orient=tk.HORIZONTAL,
#     #         command=lambda val: self.cb.get("preview") and self.cb.get("preview")()
#     #     ).pack(fill=tk.X, padx=10)

#     #     # for label in ["[ Suwak 1 – np. Jasność ]",
#     #     #               "[ Suwak 2 – np. Kontrast ]",
#     #     #               "[ Suwak 3 – np. Nasycenie ]"]:
#     #     #     tk.Label(frame, text=label, bg="#f0f0f0",
#     #     #              font=("Helvetica", 8), fg="#888").pack(pady=(8, 0))
#     #     #     ttk.Scale(frame, from_=0, to=200, value=100,
#     #     #               orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

#     #     ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

#     #     # ── Informacje o obrazie ──────────────────────────────
#     #     tk.Label(frame, text="Informacje", font=("Helvetica", 10, "bold"),
#     #              bg="#f0f0f0").pack(pady=(0, 4))
#     #     self._info_label = tk.Label(frame, text="Brak obrazu", bg="#f0f0f0",
#     #                                 font=("Helvetica", 9), justify=tk.LEFT, wraplength=190)
#     #     self._info_label.pack(padx=10, anchor=tk.W)

#     #     # ── Przycisk zastosuj ─────────────────────────────────
#     #     tk.Button(frame, text="▶ Zastosuj zmiany",
#     #               command=self.cb.get("apply"),
#     #               bg="#4CAF50", fg="white", relief=tk.FLAT,
#     #               padx=8, pady=4).pack(pady=16, padx=10, fill=tk.X)



#     # def update_info(self, image: Image.Image, path: Optional[str] = None) -> None:
#     #     """Zaktualizuj etykietę z informacjami o obrazie."""
#     #     w, h  = image.size
#     #     mode  = image.mode
#     #     name  = path.split("/")[-1] if path else "—"
#     #     self._info_label.config(text=f"Plik: {name}\nRozmiar: {w} × {h} px\nTryb: {mode}")
#     def _build(self, parent):
#         frame = tk.Frame(parent, width=220, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
#         frame.pack(side=tk.RIGHT, fill=tk.Y)
#         frame.pack_propagate(False)

#         tk.Label(frame, text="Ustawienia", font=("Helvetica", 11, "bold"),
#                 bg="#f0f0f0").pack(pady=(12, 4))
#         ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

#         # ── Próg binaryzacji ──────────────────────────────────────
#         tk.Label(frame, text="Próg binaryzacji", bg="#f0f0f0",
#                 font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
#         self.threshold = tk.IntVar(value=128)
#         tk.Scale(frame, from_=0, to=255, variable=self.threshold,
#                 orient=tk.HORIZONTAL,
#                 command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
#                 ).pack(fill=tk.X, padx=10)

#         # ── Jasność ───────────────────────────────────────────────
#         tk.Label(frame, text="Jasność", bg="#f0f0f0",
#                 font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
#         self.brightness = tk.DoubleVar(value=1.0)
#         tk.Scale(frame, from_=0.0, to=3.0, resolution=0.05,
#                 variable=self.brightness, orient=tk.HORIZONTAL,
#                 command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
#                 ).pack(fill=tk.X, padx=10)

#         # ── Kontrast ──────────────────────────────────────────────
#         tk.Label(frame, text="Kontrast", bg="#f0f0f0",
#                 font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
#         self.contrast = tk.DoubleVar(value=1.0)
#         tk.Scale(frame, from_=0.0, to=3.0, resolution=0.05,
#                 variable=self.contrast, orient=tk.HORIZONTAL,
#                 command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
#                 ).pack(fill=tk.X, padx=10)

#         ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

#         # ── Info ──────────────────────────────────────────────────
#         tk.Label(frame, text="Informacje", font=("Helvetica", 10, "bold"),
#                 bg="#f0f0f0").pack(pady=(0, 4))
#         self._info_label = tk.Label(frame, text="Brak obrazu", bg="#f0f0f0",
#                                     font=("Helvetica", 9), justify=tk.LEFT, wraplength=190)
#         self._info_label.pack(padx=10, anchor=tk.W)

#         tk.Button(frame, text="▶ Zastosuj zmiany",
#                 command=self.cb.get("apply"),
#                 bg="#4CAF50", fg="white", relief=tk.FLAT,
#                 padx=8, pady=4).pack(pady=16, padx=10, fill=tk.X)

#     def update_info(self, image, path=None):
#         w, h = image.size
#         name = path.split("/")[-1] if path else "—"
#         self._info_label.config(text=f"Plik: {name}\nRozmiar: {w}×{h} px\nTryb: {image.mode}")

"""
sidebar.py
──────────
Dynamiczny panel boczny – pokazuje kontrolki zależnie od aktywnego filtra.
Wywołaj show_controls("binarize" | "brightness" | "contrast" | None)
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from PIL import Image


class Sidebar:
    def __init__(self, parent: tk.Frame, callbacks: dict):
        self.cb = callbacks
        self._build(parent)


    def _build(self, parent: tk.Frame):
        self._parent = parent  # zapamiętaj rodzica do pack()

        self._frame = tk.Frame(parent, width=220, bg="#f0f0f0",
                                relief=tk.SUNKEN, bd=1)
        self._frame.pack_propagate(False)
        # sidebar zaczyna ukryty – NIE pakujemy _frame

        # ── Nagłówek ──────────────────────────────────────────────
        tk.Label(self._frame, text="Ustawienia",
                font=("Helvetica", 11, "bold"),
                bg="#f0f0f0").pack(pady=(12, 4))
        ttk.Separator(self._frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

        # ── Obszar dynamiczny ─────────────────────────────────────
        self._controls_frame = tk.Frame(self._frame, bg="#f0f0f0")
        self._controls_frame.pack(fill=tk.X, padx=10, pady=8)

        ttk.Separator(self._frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

        # ── Informacje o obrazie ──────────────────────────────────
        self._info_title = tk.Label(self._frame, text="Informacje",
                             font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        self._info_title.pack(pady=(8, 4))
        self._info_label = tk.Label(self._frame, text="Brak obrazu",
                                        bg="#f0f0f0", font=("Helvetica", 9),
                                        justify=tk.LEFT, wraplength=190)
        self._info_label.pack(padx=10, anchor=tk.W)

        # ── Przycisk Zastosuj (nie pakowany na starcie) ───────────
        self._apply_btn = tk.Button(
                self._frame, text="▶ Zastosuj zmiany",
                command=self.cb.get("apply"),
                bg="#4CAF50", fg="white", relief=tk.FLAT, padx=8, pady=4
        )

        # ── Zmienne suwaków ───────────────────────────────────────
        self.threshold  = tk.IntVar(value=128)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast   = tk.DoubleVar(value=1.0)

        

    # ──────────────────────────────────────────────────────────
    #  GŁÓWNA METODA – przełącza widoczne kontrolki lub info
    # ──────────────────────────────────────────────────────────

    def show_controls(self, mode):
        for widget in self._controls_frame.winfo_children():
                widget.destroy()

        if mode is None:
                self.hide()
                return

        self.show()
        self._info_label.pack_forget()
        self._info_title.pack_forget()
        self._apply_btn.pack(pady=16, padx=10, fill=tk.X)

        if mode == "binarize":
                self._make_slider(label="Próg binaryzacji", variable=self.threshold,
                                from_=0, to=255, resolution=1, callback="preview")
        elif mode == "brightness":
                self._make_slider(label="Jasność", variable=self.brightness,
                                from_=0.0, to=3.0, resolution=0.05, callback="preview")
        elif mode == "contrast":
                self._make_slider(label="Kontrast", variable=self.contrast,
                                from_=0.0, to=3.0, resolution=0.05, callback="preview")
        
    def show_info(self, image, path=None):
        self.show()
        for widget in self._controls_frame.winfo_children():
                widget.destroy()
        self._apply_btn.pack_forget()
        self._info_title.pack(pady=(8, 4))
        self._info_label.pack(padx=10, anchor=tk.W)
        self.update_info(image, path)

    # ──────────────────────────────────────────────────────────
    #  HELPER – buduje suwak z etykietą i wyświetlaną wartością
    # ──────────────────────────────────────────────────────────

    def _make_slider(self, label, variable, from_, to, resolution, callback):
        tk.Label(self._controls_frame, text=label, bg="#f0f0f0",
                 font=("Helvetica", 9, "bold"), anchor=tk.W).pack(fill=tk.X)

        # Etykieta pokazująca aktualną wartość
        val_label = tk.Label(self._controls_frame, bg="#f0f0f0",
                             font=("Helvetica", 9), fg="#444")
        val_label.pack(anchor=tk.E)

        def on_change(val):
            val_label.config(text=f"{float(val):.2f}")
            cb = self.cb.get(callback)
            if cb:
                cb()

        # Ustaw aktualną wartość w etykiecie od razu
        val_label.config(text=f"{variable.get():.2f}")

        tk.Scale(
            self._controls_frame,
            from_=from_, to=to,
            resolution=resolution,
            variable=variable,
            orient=tk.HORIZONTAL,
            showvalue=False,       
            command=on_change
        ).pack(fill=tk.X)

    # ──────────────────────────────────────────────────────────
    def hide(self):
        self._frame.pack_forget()
        

    def show(self):
        self._frame.pack(side=tk.RIGHT, fill=tk.Y)

#     def show_info(self, image, path=None):
#         """Pokazuje sidebar z samymi informacjami o obrazie."""
#         self.show()
#         for widget in self._controls_frame.winfo_children():
#                 widget.destroy()
#         self._hint.config(text="")
#         self._apply_btn.pack_forget()
#         self.update_info(image, path)    

    def update_info(self, image: Image.Image, path: Optional[str] = None) -> None:
        w, h = image.size
        name = path.split("/")[-1] if path else "—"
        self._info_label.config(
            text=f"Plik: {name}\nRozmiar: {w}×{h} px\nTryb: {image.mode}"
        )
        

