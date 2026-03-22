"""Pasek menu górnego. """

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

        # ── Opcje ────────────────────────────────────────────
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opcje", menu=options_menu)
        options_menu.add_command(label="Cofnij             Ctrl+Z",       command=self.cb.get("undo"))
        options_menu.add_command(label="Ponów",                          command=self.cb.get("reset"))  
    
        # ── Edycja ────────────────────────────────────────────
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edycja", menu=edit_menu)

        pixel_menu = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label="Operacje na pikselach", menu=pixel_menu)
        pixel_menu.add_command(label="Skala szarości (avg)",        command=self.cb.get("gray_avg"))
        pixel_menu.add_command(label="Skala szarości (luminancja)", command=self.cb.get("gray_human"))
        pixel_menu.add_command(label="Negatyw",                     command=self.cb.get("negative"))
        pixel_menu.add_command(label="Binaryzacja",                 command=self.cb.get("binarize"))
        pixel_menu.add_command(label="Jasność",                     command=self.cb.get("brightness"))
        pixel_menu.add_command(label="Kontrast",                    command=self.cb.get("contrast"))
        pixel_menu.add_command(label="Potęgowanie",                    command=self.cb.get("power_trans"))
        pixel_menu.add_command(label="Logarytmowanie",                    command=self.cb.get("log_trans"))

        matrix_menu = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label="Filtry", menu=matrix_menu)
        matrix_menu.add_command(label="Filtr uśredniający", command=self.cb.get("avg_filter"))
        matrix_menu.add_command(label="Filtr Gaussa",       command=self.cb.get("gauss_filter"))
        matrix_menu.add_command(label="Filtr wyostrzający", command=self.cb.get("sharpen_filter"))
        matrix_menu.add_command(label="Własny filtr",        command=self.cb.get("custom_filter"))
        matrix_menu.add_command(label="Krzyż Robertsa", command=self.cb.get("roberts_cross"))
        matrix_menu.add_command(label="Operator Prewitta", command=self.cb.get("prewitt_operator"))
        matrix_menu.add_command(label="Operator Sobela", command=self.cb.get("sobel_operator"))

        # ── Operacje morfologiczne ────────────────────────────────
        menu_morph = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label="Morfologia", menu=menu_morph)
        menu_morph.add_command(label="Erozja",     command=self.cb.get("erosion"))
        menu_morph.add_command(label="Dylatacja",  command=self.cb.get("dilation"))
        menu_morph.add_command(label="Otwarcie",   command=self.cb.get("opening"))
        menu_morph.add_command(label="Zamknięcie", command=self.cb.get("closing"))
        menu_morph.add_command(label="Hit-or-Miss", command=self.cb.get("hit_or_miss"))
        menu_morph.add_command(label="Szkieletowanie", command=self.cb.get("skeletonize"))

        # ── Histogram ────────────────────────────────────────────
        edit_menu.add_command(label="Wyrównanie histogramu", command=self.cb.get("equalize_histogram"))

        # ── Info ──────────────────────────────────────────────────
        info_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Info", menu=info_menu)
        info_menu.add_command(label="Info o obrazie", command=self.cb.get("show_info"))
        info_menu.add_command(label="Projekcja pionowa i pozioma", command=self.cb.get("projections"))


        # ── Histogramy ────────────────────────────────────────────
        histogram_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Histogramy", menu=histogram_menu)
        histogram_menu.add_command(label="Histogram", command=self.cb.get("histogram"))

        


