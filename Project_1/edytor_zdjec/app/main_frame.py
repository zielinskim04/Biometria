"""
main_frame.py
─────────────
Główne okno aplikacji. Łączy wszystkie komponenty UI z logiką.
Tu obsługujesz zdarzenia (callbacki) przekazywane między UI a logiką.

Schemat działania:
    MainFrame
        ├── buduje UI (Menu, Toolbar, Canvas, Sidebar, StatusBar)
        ├── tworzy obiekty logiki (FileHandler, History)
        └── podpina callbacki: np. menu "Otwórz" → file.open_image()
"""

import tkinter as tk
from tkinter import messagebox
import os # dla show_info
import numpy as np
from app.ui.menu       import AppMenu
from app.ui.canvas     import ImageCanvas
from app.ui.sidebar    import Sidebar
from app.logic.file    import FileHandler
from app.logic.history import History
from app.logic.filters import Filters
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class MainFrame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Edytor Zdjęć")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        # ── Logika ────────────────────────────────────────────
        self.history = History()
        self.file    = FileHandler()
        self.filters = Filters()   
        self._preview_base  = None   # obraz przed bieżącą sesją filtra
        self.active_filter  = None   # "binarize" | "brightness" | "contrast" | None  
        self._pending_result = None   

        # ── UI ────────────────────────────────────────────────
        self.menu       = AppMenu(root,     callbacks=self._menu_callbacks())
        

        # Środkowa część okna: canvas + sidebar obok siebie
        main_area = tk.Frame(root)
        main_area.pack(fill=tk.BOTH, expand=True)

        self.sidebar = Sidebar(main_area, callbacks=self._sidebar_callbacks())
        self.canvas  = ImageCanvas(main_area)
        

        # ── Skróty klawiszowe ─────────────────────────────────
        root.bind("<Control-o>", lambda e: self._open())
        root.bind("<Control-s>", lambda e: self._save())
        root.bind("<Control-S>", lambda e: self._save_as())
        root.bind("<Control-z>", lambda e: self._undo())

    # ──────────────────────────────────────────────────────────
    #  CALLBACKI – słowniki przekazywane do komponentów UI
    # ──────────────────────────────────────────────────────────

    def _menu_callbacks(self) -> dict:
        return {
            "open":    self._open,
            "save":    self._save,
            "save_as": self._save_as,
            "quit":    self.root.quit,
            "undo":    self._undo,
            "reset": self._reset_to_original,
            "gray_avg":   self._gray_avg,
            "gray_human": self._gray_human,
            "negative":   self._negative,
            "binarize":   self._set_filter_binarize,
            "power_trans": self._set_filter_power,
            "log_trans": self._log_trans,    
            "brightness": self._set_filter_brightness,
            "contrast":   self._set_filter_contrast,
            "avg_filter":     self._set_filter_avg,
            "gauss_filter":   self._set_filter_gauss,
            "sharpen_filter": self._set_filter_sharpen,
            "custom_filter":  self._set_filter_custom,
            "show_info": self._show_info,
            "roberts_cross": self._roberts_cross,
            "prewitt_operator": self._prewitt_operator,
            "sobel_operator": self._sobel_operator,
            "histogram": self._on_histogram_click,
            "equalize_histogram": self._equalize_histogram,
            "erosion":  self._set_filter_erosion,
            "dilation": self._set_filter_dilation,
            "opening":  self._set_filter_opening,
            "closing":  self._set_filter_closing,
            "top_hat": self._set_filter_top_hat,
            "black_hat": self._set_filter_black_hat,
            "skeletonize": self._set_filter_skeletonize,
            "projections": self._projections
        }


    def _sidebar_callbacks(self) -> dict:
        return {
            "apply": self._apply_changes,
            "cancel":  self._cancel,
            "preview": self._preview, 
        }

    # ──────────────────────────────────────────────────────────
    #  AKCJE (łączą UI ↔ logikę)
    # ──────────────────────────────────────────────────────────


    # Poniższa funkcja dodaje miniaturkę w slidebar, który tworzy i resetuje też historię zmian. 
    def _open(self):
        image = self.file.open_image()
        if image:
            self.history.reset(image)
            self._preview_base = image.copy()
            self._original = image.copy()      
            self.active_filter = None
            self._pending_result = None
            self.canvas.show(image)
            self.sidebar.update_thumbnail(image)   
            self.sidebar.set_idle()
            self.sidebar.show()
        
    def _save(self):
        image = self.history.current()
        self.file.save(image)
        
    def _save_as(self):
        image = self.history.current()
        self.file.save_as(image)
        
    def _undo(self):
        image = self.history.undo()
        if image:
            self._preview_base = image.copy()
            self._pending_result = None
            self.active_filter = None
            self.canvas.show(image)
            self.sidebar.set_idle()

    def _reset_to_original(self):
        if self._original is None:
            return
        self.history.reset(self._original)
        self._preview_base = self._original.copy()
        self._pending_result = None
        self.active_filter = None
        self.canvas.show(self._original)
        self.sidebar.set_idle()

    def _cancel(self):
        if self._preview_base is None:
            return
        self._pending_result = None
        self.active_filter = None
        self.canvas.show(self._preview_base)
        self.sidebar.set_idle()

    def _preview(self):
        """Dla filtrów z suwakiem."""
        if self._preview_base is None or self.active_filter is None:
            return
        if self.active_filter == "binarize":
            result = self.filters.binarize(self._preview_base,
                        int(self.sidebar.threshold.get()))
        elif self.active_filter == "brightness":
            result = self.filters.brightness(self._preview_base,
                        float(self.sidebar.brightness.get()))
        elif self.active_filter == "contrast":
            result = self.filters.contrast(self._preview_base,
                        float(self.sidebar.contrast.get()))
        elif self.active_filter == "power_trans":
            result = self.filters.power_trans(self._preview_base,
                        float(self.sidebar.power_trans.get()))
        elif self.active_filter == "avg_filter":
            result = self.filters.average_filter(self._preview_base,
                        int(self.sidebar.filter_size.get()))
        elif self.active_filter == "gauss_filter":
            result = self.filters.gaussian_filter(self._preview_base,
                        int(self.sidebar.filter_size.get()),
                        float(self.sidebar.sigma.get()))
        elif self.active_filter == "sharpen_filter":
            result = self.filters.sharpen_filter(self._preview_base,
                        self.sidebar.sharpen_preset.get())
        elif self.active_filter == "custom_filter":
            try:
                kernel = self.sidebar.get_custom_kernel()
                result = self.filters.custom_filter(self._preview_base, kernel)
            except ValueError:
                messagebox.showwarning("Błąd kernela","Wszystkie pola kernela muszą zawierać liczby!")
                return
        elif self.active_filter in ("erosion", "dilation", "opening", "closing", "top_hat", "black_hat"):
            size  = int(self.sidebar.morph_size.get())
            shape = self.sidebar.morph_shape.get()
            fn = getattr(self.filters, self.active_filter)
            result = fn(self._preview_base, size, shape)
        elif self.active_filter == "skeletonize":
            result = self.filters.skeletonize(self._preview_base)
        else:
            return
        self._pending_result = result
        self.canvas.show(result)

    def _apply_changes(self):
        if self._pending_result is None:
            return
        self.history.push(self._pending_result)
        self._preview_base = self._pending_result.copy()
        self._pending_result = None
        self.active_filter = None
        self.canvas.show(self._preview_base)
        self.sidebar.set_idle()

    def _apply_one_click(self, filter_fn, label):
        """Dla filtrów bez suwaka."""
        current = self.history.current()
        if current is None:
            return
        self._preview_base = current.copy()
        self.active_filter = label
        result = filter_fn(current)
        self._pending_result = result              
        self.canvas.show(result)
        self.sidebar.show_filter_controls(label)  

    def _gray_avg(self):
        self._apply_one_click(self.filters.convert_to_gray_avg, "gray_avg")

    def _gray_human(self):
        self._apply_one_click(self.filters.convert_to_gray_human, "gray_human")

    def _negative(self):
        self._apply_one_click(self.filters.negative, "negative")

    def _log_trans(self):
        self._apply_one_click(self.filters.log_trans, "log_trans")

    def _roberts_cross(self):
        self._apply_one_click(self.filters.roberts_cross, "roberts_cross")

    def _prewitt_operator(self):
        self._apply_one_click(self.filters.prewitt_operator, "prewitt_operator")

    def _sobel_operator(self):
        self._apply_one_click(self.filters.sobel_operator, "sobel_operator")

    def _on_histogram_click(self):
        img = self.history.current()
        if img:       
            self.sidebar.show_filter_controls("histogram")
            self.root.update_idletasks()
            data = self.filters.compute_histogram(img)
            self.sidebar.update_histogram_plot(data)
    
    def _equalize_histogram(self):
        self._apply_one_click(self.filters.equalize_histogram, "equalize_histogram")

    def _projections(self):
        current = self.history.current()
        if current is None: return

        horiz, vert = self.filters.compute_projections(current)
        img_np = np.array(current.convert("L"))
        h, w = img_np.shape

        max_val = max(np.max(horiz), np.max(vert))

        fig, ax_main = plt.subplots(figsize=(12, 10))
        fig.canvas.manager.set_window_title("Analiza Projekcji - Dopasowanie do zdjęcia")

        ax_main.imshow(img_np, cmap='gray', aspect='equal')
        ax_main.axis('off')

        divider = make_axes_locatable(ax_main)

        ax_top = divider.append_axes("top", size="20%", pad=0.05, sharex=ax_main)
        ax_top.bar(range(w), vert, color='black', width=1.0, align='edge')
        ax_top.set_xlim(0, w)
        ax_top.axis('off')

        ax_right = divider.append_axes("right", size="20%", pad=0.05, sharey=ax_main)
        ax_right.barh(range(h), horiz, color='black', height=1.0, align='edge')
        ax_right.set_ylim(h, 0) 
        # ax_right.set_xlim(0, max_val)
        ax_right.axis('off')

        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
        plt.show()

    
    # ── Ustawianie aktywnego filtra ───────────────────────────────
    def _set_filter_binarize(self):
        self._preview_base = self.history.current()
        self.active_filter = "binarize"
        self._pending_result = None
        self.sidebar.show_filter_controls("binarize")   
        self._preview()

    def _set_filter_brightness(self):
        self._preview_base = self.history.current()
        self.active_filter = "brightness"
        self._pending_result = None
        self.sidebar.show_filter_controls("brightness") 
        self._preview()

    def _set_filter_contrast(self):
        self._preview_base = self.history.current()
        self.active_filter = "contrast"
        self._pending_result = None
        self.sidebar.show_filter_controls("contrast")   
        self._preview()

    def _set_filter_power(self):
        self._preview_base = self.history.current()
        self.active_filter = "power_trans"
        self._pending_result = None
        self.sidebar.show_filter_controls("power_trans")   
        self._preview()

    def _set_filter_avg(self):
        self._preview_base = self.history.current()
        self.active_filter = "avg_filter"
        self._pending_result = None
        self.sidebar.show_filter_controls("avg_filter")
        self._preview()

    def _set_filter_gauss(self):
        self._preview_base = self.history.current()
        self.active_filter = "gauss_filter"
        self._pending_result = None
        self.sidebar.show_filter_controls("gauss_filter")
        self._preview()

    def _set_filter_sharpen(self):
        self._preview_base = self.history.current()
        self.active_filter = "sharpen_filter"
        self._pending_result = None
        self.sidebar.show_filter_controls("sharpen_filter")
        self._preview()

    def _set_filter_custom(self):
        self._preview_base = self.history.current()
        self.active_filter = "custom_filter"
        self._pending_result = None
        self.sidebar.show_filter_controls("custom_filter")

    # ── Info o obrazie ───────────────────────────────   
    def _show_info(self):
        
        current = self.history.current()
        if current is None:
            self.status_bar.set_text("Brak obrazu.")
            return

        img_np = np.array(current.convert('L'))
        w, h   = current.size

        # Rozmiar pliku
        if self.file.path and os.path.exists(self.file.path):
            file_bytes = os.path.getsize(self.file.path)
            if file_bytes < 1024 * 1024:
                file_size = f"{file_bytes / 1024:.1f} KB"
            else:
                file_size = f"{file_bytes / (1024*1024):.2f} MB"
        else:
            file_size = "—"

        # Głębia koloru
        depth_map = {"RGB": "24-bit", "RGBA": "32-bit", "L": "8-bit",
                    "1": "1-bit", "P": "8-bit (paleta)"}
        depth = depth_map.get(current.mode, "—")

        info = {
            "Plik":         os.path.basename(self.file.path) if self.file.path else "—",
            "Ścieżka":      self.file.path or "—",
            "Rozmiar":      f"{w} × {h} px",
            "Rozmiar pliku":file_size,
            "Tryb":         current.mode,
            "Głębia":       depth,
            "Min jasność":  f"{img_np.min()}",
            "Max jasność":  f"{img_np.max()}",
            "Śr. jasność":  f"{img_np.mean():.1f}",
            "Odch. std":    f"{img_np.std():.1f}",
        }

        self.sidebar.show_info(info)
        self.sidebar.show()

    # ── Operacje morfologiczne ───────────────────────────────   
    def _set_morph_filter(self, name: str):
        """Wspólny schemat dla filtrów morfologicznych."""
        self._preview_base = self.history.current()
        self.active_filter = name
        self._pending_result = None
        self.sidebar.show_filter_controls(name)
        self._preview()

    def _set_filter_erosion(self):  self._set_morph_filter("erosion")
    def _set_filter_dilation(self): self._set_morph_filter("dilation")
    def _set_filter_opening(self):  self._set_morph_filter("opening")
    def _set_filter_closing(self):  self._set_morph_filter("closing")
    def _set_filter_top_hat(self):  self._set_morph_filter("top_hat")
    def _set_filter_black_hat(self):  self._set_morph_filter("black_hat")
    def _set_filter_skeletonize(self):
        self._apply_one_click(self.filters.skeletonize, "skeletonize")
    

    
