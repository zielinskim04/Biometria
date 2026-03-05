"""
menu.py
───────
Pasek menu górnego. Tylko widgety Tkinter, zero logiki.
Wszystkie akcje przekazywane przez słownik `callbacks`.

Callbacks wymagane:
    open, save, save_as, quit, undo
"""

import tkinter as tk


class AppMenu:
    def __init__(self, root: tk.Tk, callbacks: dict):
        self.cb = callbacks
        self._build(root)

    def _build(self, root: tk.Tk):
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # ── Plik ──────────────────────────────────────────────
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Otwórz...          Ctrl+O",       command=self.cb.get("open"))
        file_menu.add_separator()
        file_menu.add_command(label="Zapisz             Ctrl+S",       command=self.cb.get("save"))
        file_menu.add_command(label="Zapisz jako...  Ctrl+Shift+S",   command=self.cb.get("save_as"))
        file_menu.add_separator()
        file_menu.add_command(label="Wyjdź",                          command=self.cb.get("quit"))

        # ── Edycja ────────────────────────────────────────────
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edycja", menu=edit_menu)
        edit_menu.add_command(label="Cofnij             Ctrl+Z",       command=self.cb.get("undo"))
        edit_menu.add_separator()

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ WPISY MENU EDYCJA                  ║
        # ║                                                  ║
        # ║  edit_menu.add_command(                          ║
        # ║      label="Przytnij",                           ║
        # ║      command=self.cb.get("crop")                 ║
        # ║  )                                               ║
        # ║  Pamiętaj dodać "crop" do callbacks w           ║
        # ║  main_frame._menu_callbacks()                    ║
        # ╚══════════════════════════════════════════════════╝

        # ── Filtry ────────────────────────────────────────────
        filter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filtry", menu=filter_menu)

        # filter_menu.add_command(label="Skala szarości (avg)",       command=self.cb.get("gray_avg"))
        # filter_menu.add_command(label="Skala szarości (luminancja)", command=self.cb.get("gray_human"))
        # filter_menu.add_command(label="Negatyw",                    command=self.cb.get("negative"))
        # filter_menu.add_command(label="Binaryzacja",                command=self.cb.get("binarize"))
        # # menu.py – w sekcji filter_menu

        filter_menu.add_command(label="Skala szarości (avg)",        command=self.cb.get("gray_avg"))
        filter_menu.add_command(label="Skala szarości (luminancja)", command=self.cb.get("gray_human"))
        filter_menu.add_command(label="Negatyw",                     command=self.cb.get("negative"))
        filter_menu.add_separator()
        filter_menu.add_command(label="Binaryzacja",                 command=self.cb.get("binarize"))
        filter_menu.add_command(label="Jasność",                     command=self.cb.get("brightness"))
        filter_menu.add_command(label="Kontrast",                    command=self.cb.get("contrast"))

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ FILTRY                             ║
        # ║                                                  ║
        # ║  filter_menu.add_command(                        ║
        # ║      label="Rozmycie",                           ║
        # ║      command=self.cb.get("blur")                 ║
        # ║  )                                               ║
        # ╚══════════════════════════════════════════════════╝
