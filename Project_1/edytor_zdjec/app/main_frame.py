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
from app.ui.menu       import AppMenu
from app.ui.toolbar    import Toolbar
from app.ui.canvas     import ImageCanvas
from app.ui.sidebar    import Sidebar
from app.ui.status_bar import StatusBar
from app.logic.file    import FileHandler
from app.logic.history import History
from app.logic.filters import Filters


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

        # ── UI ────────────────────────────────────────────────
        self.menu       = AppMenu(root,     callbacks=self._menu_callbacks())
        # self.toolbar    = Toolbar(root,     callbacks=self._toolbar_callbacks())
        self.status_bar = StatusBar(root)

        # Środkowa część okna: canvas + sidebar obok siebie
        main_area = tk.Frame(root)
        main_area.pack(fill=tk.BOTH, expand=True)

        self.canvas  = ImageCanvas(main_area)
        self.sidebar = Sidebar(main_area, callbacks=self._sidebar_callbacks())

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
            "gray_avg":   self._gray_avg,
            "gray_human": self._gray_human,
            "negative":   self._negative,
            "binarize":   self._set_filter_binarize,    
            "brightness": self._set_filter_brightness,
            "contrast":   self._set_filter_contrast,
            "avg_filter":    self._avg_filter,
            "gauss_filter":  self._gauss_filter,
            "sharpen_filter": self._sharpen_filter,
            "show_info": self._show_info,
        }

    # def _toolbar_callbacks(self) -> dict:
    #     return {
    #         "open":  self._open,
    #         "save":  self._save,
    #         "undo":  self._undo,
    #         # "crop": self._crop,       
    #     }

    def _sidebar_callbacks(self) -> dict:
        return {
            "apply": self._apply_changes,
            "preview": self._preview, 
        }

    # ──────────────────────────────────────────────────────────
    #  AKCJE (łączą UI ↔ logikę)
    # ──────────────────────────────────────────────────────────

    def _open(self):
        image = self.file.open_image()
        if image:
            self.history.reset(image)
            self.canvas.show(image)
            self.status_bar.set_info(image, self.file.path)

    def _save(self):
        image = self.history.current()
        self.file.save(image)
        self.status_bar.set_text(f"Zapisano: {self.file.path}")

    def _save_as(self):
        image = self.history.current()
        self.file.save_as(image)
        self.status_bar.set_text(f"Zapisano jako: {self.file.path}")

    def _undo(self):
        image = self.history.undo()
        if image:
            self._preview_base = image.copy()
            self.active_filter = None
            self.canvas.show(image)
            self.status_bar.set_text("Cofnięto.")

    
    # ── Preview – zawsze na _preview_base ────────────────────────
    def _preview(self):
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
        else:
            return
        self.canvas.show(result)


    def _apply_changes(self):
        if self._preview_base is None or self.active_filter is None:
            self.status_bar.set_text("Najpierw wybierz filtr z menu.")
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
        else:
            return

        self.history.push(result)
        self._preview_base = result.copy()   
        self.active_filter = None            
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano zmiany.")
        self.sidebar.show_controls(None)


    def _gray_avg(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.convert_to_gray_avg(current)
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Skala szarości (avg)")

    def _gray_human(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.convert_to_gray_human(current)
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Skala szarości (luminancja)")

    def _negative(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.negative(current)
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Negatyw")

    def _avg_filter(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.average_filter(current)
        self._preview_base = result.copy()
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Filtr uśredniający")

    def _gauss_filter(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.gaussian_filter(current)
        self._preview_base = result.copy()
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Filtr Gaussa")

    def _sharpen_filter(self):
        current = self.history.current()
        if current is None: return
        self.history.push(current)
        result = self.filters.sharpen_filter(current)
        self._preview_base = result.copy()
        self.canvas.show(result)
        self.status_bar.set_text("Zastosowano: Filtr wyostrzający")

    
    # ── Ustawianie aktywnego filtra ───────────────────────────────
    def _set_filter_binarize(self):
        self._preview_base = self.history.current()
        self.active_filter = "binarize"
        self.sidebar.show_controls("binarize")   
        self._preview()

    def _set_filter_brightness(self):
        self._preview_base = self.history.current()
        self.active_filter = "brightness"
        self.sidebar.show_controls("brightness") 
        self._preview()

    def _set_filter_contrast(self):
        self._preview_base = self.history.current()
        self.active_filter = "contrast"
        self.sidebar.show_controls("contrast")   
        self._preview()

    # Info o obrazie
    def _show_info(self):
        current = self.history.current()
        if current is None:
            self.status_bar.set_text("Brak obrazu.")
            return
        self.sidebar.show_info(current, self.file.path)