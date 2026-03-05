#!!! Nie jest używany w tym momencie!!!


"""
toolbar.py
──────────
Pasek narzędzi pod menu. Tylko widgety Tkinter, zero logiki.
Wszystkie akcje przekazywane przez słownik `callbacks`.

Callbacks wymagane:
    open, save, undo
"""

import tkinter as tk
from tkinter import ttk


class Toolbar:
    def __init__(self, root: tk.Tk, callbacks: dict):
        self.cb = callbacks
        self._build(root)

    def _build(self, root: tk.Tk):
        bar = tk.Frame(root, bd=1, relief=tk.RAISED, bg="#e8e8e8", pady=2)
        bar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(bar, text="📂 Otwórz", relief=tk.FLAT, padx=8,
                  command=self.cb.get("open")).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="💾 Zapisz", relief=tk.FLAT, padx=8,
                  command=self.cb.get("save")).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="↩ Cofnij", relief=tk.FLAT, padx=8,
                  command=self.cb.get("undo")).pack(side=tk.LEFT, padx=2)

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ SWOJE PRZYCISKI NARZĘDZI           ║
        # ║                                                  ║
        # ║  tk.Button(bar,                                  ║
        # ║      text="✂ Przytnij",                          ║
        # ║      relief=tk.FLAT, padx=8,                     ║
        # ║      command=self.cb.get("crop")                 ║
        # ║  ).pack(side=tk.LEFT, padx=2)                    ║
        # ╚══════════════════════════════════════════════════╝
