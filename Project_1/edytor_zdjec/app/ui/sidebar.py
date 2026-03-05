"""
sidebar.py
──────────
Panel boczny z suwakami, opcjami i informacjami o obrazie.
Tylko widgety Tkinter, zero logiki.

Callbacks wymagane:
    apply  – przycisk "Zastosuj zmiany"
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from PIL import Image


class Sidebar:
    def __init__(self, parent: tk.Frame, callbacks: dict):
        self.cb = callbacks
        self._build(parent)

    # def _build(self, parent: tk.Frame):
    #     frame = tk.Frame(parent, width=220, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
    #     frame.pack(side=tk.RIGHT, fill=tk.Y)
    #     frame.pack_propagate(False)

    #     # ── Nagłówek ──────────────────────────────────────────
    #     tk.Label(frame, text="Ustawienia", font=("Helvetica", 11, "bold"),
    #              bg="#f0f0f0").pack(pady=(12, 4))
    #     ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

    #     # ── Suwaki ────────────────────────────────────────────
    #     # W metodzie _build() w sidebar.py, zamiast placeholdera:

    #     # Binaryzacja – suwak progu
    #     self.threshold = tk.IntVar(value=128)
    #     tk.Label(frame, text="Próg binaryzacji", bg="#f0f0f0",
    #             font=("Helvetica", 8)).pack(pady=(8,0))
        
    #     tk.Scale(frame,
    #         from_=0, to=255,
    #         variable=self.threshold,
    #         orient=tk.HORIZONTAL,
    #         command=lambda val: self.cb.get("preview") and self.cb.get("preview")()
    #     ).pack(fill=tk.X, padx=10)

    #     # for label in ["[ Suwak 1 – np. Jasność ]",
    #     #               "[ Suwak 2 – np. Kontrast ]",
    #     #               "[ Suwak 3 – np. Nasycenie ]"]:
    #     #     tk.Label(frame, text=label, bg="#f0f0f0",
    #     #              font=("Helvetica", 8), fg="#888").pack(pady=(8, 0))
    #     #     ttk.Scale(frame, from_=0, to=200, value=100,
    #     #               orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

    #     ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

    #     # ── Informacje o obrazie ──────────────────────────────
    #     tk.Label(frame, text="Informacje", font=("Helvetica", 10, "bold"),
    #              bg="#f0f0f0").pack(pady=(0, 4))
    #     self._info_label = tk.Label(frame, text="Brak obrazu", bg="#f0f0f0",
    #                                 font=("Helvetica", 9), justify=tk.LEFT, wraplength=190)
    #     self._info_label.pack(padx=10, anchor=tk.W)

    #     # ── Przycisk zastosuj ─────────────────────────────────
    #     tk.Button(frame, text="▶ Zastosuj zmiany",
    #               command=self.cb.get("apply"),
    #               bg="#4CAF50", fg="white", relief=tk.FLAT,
    #               padx=8, pady=4).pack(pady=16, padx=10, fill=tk.X)



    # def update_info(self, image: Image.Image, path: Optional[str] = None) -> None:
    #     """Zaktualizuj etykietę z informacjami o obrazie."""
    #     w, h  = image.size
    #     mode  = image.mode
    #     name  = path.split("/")[-1] if path else "—"
    #     self._info_label.config(text=f"Plik: {name}\nRozmiar: {w} × {h} px\nTryb: {mode}")
    def _build(self, parent):
        frame = tk.Frame(parent, width=220, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        frame.pack(side=tk.RIGHT, fill=tk.Y)
        frame.pack_propagate(False)

        tk.Label(frame, text="Ustawienia", font=("Helvetica", 11, "bold"),
                bg="#f0f0f0").pack(pady=(12, 4))
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

        # ── Próg binaryzacji ──────────────────────────────────────
        tk.Label(frame, text="Próg binaryzacji", bg="#f0f0f0",
                font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.threshold = tk.IntVar(value=128)
        tk.Scale(frame, from_=0, to=255, variable=self.threshold,
                orient=tk.HORIZONTAL,
                command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
                ).pack(fill=tk.X, padx=10)

        # ── Jasność ───────────────────────────────────────────────
        tk.Label(frame, text="Jasność", bg="#f0f0f0",
                font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.brightness = tk.DoubleVar(value=1.0)
        tk.Scale(frame, from_=0.0, to=3.0, resolution=0.05,
                variable=self.brightness, orient=tk.HORIZONTAL,
                command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
                ).pack(fill=tk.X, padx=10)

        # ── Kontrast ──────────────────────────────────────────────
        tk.Label(frame, text="Kontrast", bg="#f0f0f0",
                font=("Helvetica", 9, "bold")).pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.contrast = tk.DoubleVar(value=1.0)
        tk.Scale(frame, from_=0.0, to=3.0, resolution=0.05,
                variable=self.contrast, orient=tk.HORIZONTAL,
                command=lambda v: self.cb.get("preview") and self.cb.get("preview")()
                ).pack(fill=tk.X, padx=10)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

        # ── Info ──────────────────────────────────────────────────
        tk.Label(frame, text="Informacje", font=("Helvetica", 10, "bold"),
                bg="#f0f0f0").pack(pady=(0, 4))
        self._info_label = tk.Label(frame, text="Brak obrazu", bg="#f0f0f0",
                                    font=("Helvetica", 9), justify=tk.LEFT, wraplength=190)
        self._info_label.pack(padx=10, anchor=tk.W)

        tk.Button(frame, text="▶ Zastosuj zmiany",
                command=self.cb.get("apply"),
                bg="#4CAF50", fg="white", relief=tk.FLAT,
                padx=8, pady=4).pack(pady=16, padx=10, fill=tk.X)

    def update_info(self, image, path=None):
        w, h = image.size
        name = path.split("/")[-1] if path else "—"
        self._info_label.config(text=f"Plik: {name}\nRozmiar: {w}×{h} px\nTryb: {image.mode}")