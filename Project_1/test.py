"""
╔══════════════════════════════════════════════════════════════╗
║              EDYTOR ZDJĘĆ – SZKIELET APLIKACJI              ║
║                  Tkinter + Pillow (PIL)                     ║
╚══════════════════════════════════════════════════════════════╝

Instalacja wymaganych bibliotek:
    pip install Pillow

Struktura aplikacji:
    - EdytorZdjec  →  główna klasa aplikacji
    - _zbuduj_menu()         →  pasek menu (Plik, Edycja, Widok...)
    - _zbuduj_pasek_narzedzi()  →  przyciski skrótów pod menu
    - _zbuduj_obszar_roboczy()  →  canvas + paski przewijania
    - _zbuduj_panel_boczny()    →  suwaki, opcje, ustawienia
    - _zbuduj_pasek_statusu()   →  informacje na dole okna
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


# ══════════════════════════════════════════════════════════════
#  GŁÓWNA KLASA APLIKACJI
# ══════════════════════════════════════════════════════════════

class EdytorZdjec:
    def __init__(self, root):
        self.root = root
        self.root.title("Edytor Zdjęć")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        # ── Stan aplikacji ─────────────────────────────────────
        self.oryginalny_obraz = None   # obiekt PIL.Image (oryginał)
        self.aktualny_obraz   = None   # obiekt PIL.Image (po edycji)
        self.obraz_tk         = None   # ImageTk do wyświetlania
        self.sciezka_pliku    = None   # ścieżka ostatnio otwartego pliku
        self.historia         = []     # lista stanów do cofania zmian (Ctrl+Z)

        # ── Budowanie interfejsu (kolejność ma znaczenie) ──────
        self._zbuduj_menu()
        self._zbuduj_pasek_narzedzi()
        self._zbuduj_glowny_uklad()     # dzieli okno na canvas i panel boczny
        self._zbuduj_pasek_statusu()

        # ── Skróty klawiszowe ──────────────────────────────────
        self.root.bind("<Control-o>", lambda e: self.wczytaj_obraz())
        self.root.bind("<Control-s>", lambda e: self.zapisz_obraz())
        self.root.bind("<Control-S>", lambda e: self.zapisz_jako())
        self.root.bind("<Control-z>", lambda e: self.cofnij())


    # ══════════════════════════════════════════════════════════
    #  MENU GÓRNE
    # ══════════════════════════════════════════════════════════

    def _zbuduj_menu(self):
        pasek_menu = tk.Menu(self.root)
        self.root.config(menu=pasek_menu)

        # ── Menu: Plik ─────────────────────────────────────────
        menu_plik = tk.Menu(pasek_menu, tearoff=0)
        pasek_menu.add_cascade(label="Plik", menu=menu_plik)

        menu_plik.add_command(label="Otwórz...          Ctrl+O", command=self.wczytaj_obraz)
        menu_plik.add_separator()
        menu_plik.add_command(label="Zapisz             Ctrl+S", command=self.zapisz_obraz)
        menu_plik.add_command(label="Zapisz jako...  Ctrl+Shift+S", command=self.zapisz_jako)
        menu_plik.add_separator()
        menu_plik.add_command(label="Wyjdź", command=self.root.quit)

        # ── Menu: Edycja ───────────────────────────────────────
        menu_edycja = tk.Menu(pasek_menu, tearoff=0)
        pasek_menu.add_cascade(label="Edycja", menu=menu_edycja)

        menu_edycja.add_command(label="Cofnij             Ctrl+Z", command=self.cofnij)
        menu_edycja.add_separator()

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ SWOJE OPERACJE W MENU EDYCJA       ║
        # ║                                                  ║
        # ║  Przykład:                                       ║
        # ║  menu_edycja.add_command(                        ║
        # ║      label="Przytnij",                           ║
        # ║      command=self.przytnij   ← Twoja metoda      ║
        # ║  )                                               ║
        # ╚══════════════════════════════════════════════════╝
        menu_edycja.add_command(label="[ Twoja operacja 1 ]", command=lambda: self._placeholder("Operacja 1"))
        menu_edycja.add_command(label="[ Twoja operacja 2 ]", command=lambda: self._placeholder("Operacja 2"))

        # ── Menu: Filtry ───────────────────────────────────────
        menu_filtry = tk.Menu(pasek_menu, tearoff=0)
        pasek_menu.add_cascade(label="Filtry", menu=menu_filtry)

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ FILTRY                             ║
        # ║                                                  ║
        # ║  Przykłady filtrów Pillow:                       ║
        # ║  ImageFilter.BLUR, ImageFilter.SHARPEN,          ║
        # ║  ImageEnhance.Brightness, ImageEnhance.Contrast  ║
        # ╚══════════════════════════════════════════════════╝
        menu_filtry.add_command(label="[ Filtr 1 – np. Rozmycie ]",   command=lambda: self._placeholder("Filtr 1"))
        menu_filtry.add_command(label="[ Filtr 2 – np. Czarno-biały ]", command=lambda: self._placeholder("Filtr 2"))
        menu_filtry.add_command(label="[ Filtr 3 – np. Wyostrzenie ]", command=lambda: self._placeholder("Filtr 3"))

        # ── Menu: Widok ────────────────────────────────────────
        menu_widok = tk.Menu(pasek_menu, tearoff=0)
        pasek_menu.add_cascade(label="Widok", menu=menu_widok)
        menu_widok.add_command(label="Dopasuj do okna", command=self.dopasuj_do_okna)
        menu_widok.add_command(label="Oryginalny rozmiar (100%)", command=self.oryginalny_rozmiar)


    # ══════════════════════════════════════════════════════════
    #  PASEK NARZĘDZI (ikonki / przyciski skrótów)
    # ══════════════════════════════════════════════════════════

    def _zbuduj_pasek_narzedzi(self):
        pasek = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#e8e8e8", pady=2)
        pasek.pack(side=tk.TOP, fill=tk.X)

        # Przyciski podstawowe
        tk.Button(pasek, text="📂 Otwórz",   command=self.wczytaj_obraz, relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(pasek, text="💾 Zapisz",    command=self.zapisz_obraz,  relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(pasek, text="↩ Cofnij",    command=self.cofnij,        relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)

        ttk.Separator(pasek, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ SWOJE PRZYCISKI NARZĘDZI           ║
        # ║                                                  ║
        # ║  tk.Button(pasek,                                ║
        # ║      text="✂ Przytnij",                          ║
        # ║      command=self.przytnij,                      ║
        # ║      relief=tk.FLAT, padx=8                      ║
        # ║  ).pack(side=tk.LEFT, padx=2)                    ║
        # ╚══════════════════════════════════════════════════╝
        tk.Button(pasek, text="[ Narzędzie 1 ]", relief=tk.FLAT, padx=8,
                  command=lambda: self._placeholder("Narzędzie 1")).pack(side=tk.LEFT, padx=2)
        tk.Button(pasek, text="[ Narzędzie 2 ]", relief=tk.FLAT, padx=8,
                  command=lambda: self._placeholder("Narzędzie 2")).pack(side=tk.LEFT, padx=2)


    # ══════════════════════════════════════════════════════════
    #  UKŁAD GŁÓWNY: CANVAS (lewo) + PANEL BOCZNY (prawo)
    # ══════════════════════════════════════════════════════════

    def _zbuduj_glowny_uklad(self):
        # Ramka dzieląca okno na dwie kolumny
        ramka_glowna = tk.Frame(self.root)
        ramka_glowna.pack(fill=tk.BOTH, expand=True)

        # Kolumna lewa – obszar roboczy z obrazem
        ramka_canvas = tk.Frame(ramka_glowna, bg="#2b2b2b")
        ramka_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._zbuduj_obszar_roboczy(ramka_canvas)

        # Kolumna prawa – panel z ustawieniami
        ramka_panel = tk.Frame(ramka_glowna, width=220, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        ramka_panel.pack(side=tk.RIGHT, fill=tk.Y)
        ramka_panel.pack_propagate(False)   # stała szerokość panelu
        self._zbuduj_panel_boczny(ramka_panel)


    # ══════════════════════════════════════════════════════════
    #  OBSZAR ROBOCZY – CANVAS Z PASKAMI PRZEWIJANIA
    # ══════════════════════════════════════════════════════════

    def _zbuduj_obszar_roboczy(self, rodzic):
        # Paski przewijania
        pasek_v = tk.Scrollbar(rodzic, orient=tk.VERTICAL)
        pasek_h = tk.Scrollbar(rodzic, orient=tk.HORIZONTAL)
        pasek_v.pack(side=tk.RIGHT,  fill=tk.Y)
        pasek_h.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas – tu rysowany jest obraz
        self.canvas = tk.Canvas(
            rodzic,
            bg="#2b2b2b",
            cursor="crosshair",
            xscrollcommand=pasek_h.set,
            yscrollcommand=pasek_v.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        pasek_v.config(command=self.canvas.yview)
        pasek_h.config(command=self.canvas.xview)

        # Etykieta pokazywana gdy brak obrazu
        self.canvas.create_text(
            400, 300,
            text="Otwórz zdjęcie: Plik → Otwórz  lub  Ctrl+O",
            fill="#888888",
            font=("Helvetica", 14),
            tags="placeholder"
        )

        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ MOŻESZ DODAĆ OBSŁUGĘ ZDARZEŃ MYSZY      ║
        # ║                                                  ║
        # ║  self.canvas.bind("<B1-Motion>", self.rysuj)     ║
        # ║  self.canvas.bind("<ButtonPress-1>", self.start) ║
        # ║  self.canvas.bind("<ButtonRelease-1>", self.stop)║
        # ╚══════════════════════════════════════════════════╝


    # ══════════════════════════════════════════════════════════
    #  PANEL BOCZNY – SUWAKI I OPCJE
    # ══════════════════════════════════════════════════════════

    def _zbuduj_panel_boczny(self, rodzic):
        tk.Label(rodzic, text="Ustawienia", font=("Helvetica", 11, "bold"),
                 bg="#f0f0f0").pack(pady=(12, 4))
        ttk.Separator(rodzic, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

        # ── Przykład suwaka ────────────────────────────────────
        # ╔══════════════════════════════════════════════════╗
        # ║  TUTAJ DODAJ SUWAKI / CHECKBOXY / OPCJE         ║
        # ║                                                  ║
        # ║  Wzór suwaka:                                    ║
        # ║  self.var_jasnosc = tk.IntVar(value=100)         ║
        # ║  tk.Scale(rodzic,                                ║
        # ║      label="Jasność",                            ║
        # ║      from_=0, to=200,                            ║
        # ║      variable=self.var_jasnosc,                  ║
        # ║      orient=tk.HORIZONTAL,                       ║
        # ║      command=self.zastosuj_jasnosc               ║
        # ║  ).pack(fill=tk.X, padx=10, pady=4)             ║
        # ╚══════════════════════════════════════════════════╝

        sekcje = ["[ Suwak 1 – np. Jasność ]",
                  "[ Suwak 2 – np. Kontrast ]",
                  "[ Suwak 3 – np. Nasycenie ]"]

        for nazwa in sekcje:
            tk.Label(rodzic, text=nazwa, bg="#f0f0f0",
                     font=("Helvetica", 8), fg="#888").pack(pady=(8, 0))
            ttk.Scale(rodzic, from_=0, to=200, value=100,
                      orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)

        ttk.Separator(rodzic, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

        # ── Informacje o obrazie ───────────────────────────────
        tk.Label(rodzic, text="Informacje o obrazie",
                 font=("Helvetica", 10, "bold"), bg="#f0f0f0").pack(pady=(0, 4))

        self.etykieta_info = tk.Label(
            rodzic,
            text="Brak obrazu",
            bg="#f0f0f0",
            font=("Helvetica", 9),
            justify=tk.LEFT,
            wraplength=190
        )
        self.etykieta_info.pack(padx=10, anchor=tk.W)

        # ── Przycisk "Zastosuj" ────────────────────────────────
        # ╔══════════════════════════════════════════════════╗
        # ║  Możesz tu dodać przycisk zatwierdzający zmiany ║
        # ╚══════════════════════════════════════════════════╝
        tk.Button(rodzic, text="▶ Zastosuj zmiany",
                  command=lambda: self._placeholder("Zastosuj"),
                  bg="#4CAF50", fg="white", relief=tk.FLAT,
                  padx=8, pady=4).pack(pady=16, padx=10, fill=tk.X)


    # ══════════════════════════════════════════════════════════
    #  PASEK STATUSU (na dole okna)
    # ══════════════════════════════════════════════════════════

    def _zbuduj_pasek_statusu(self):
        pasek = tk.Frame(self.root, bd=1, relief=tk.SUNKEN, bg="#dcdcdc")
        pasek.pack(side=tk.BOTTOM, fill=tk.X)

        self.status = tk.Label(pasek, text="Gotowy. Otwórz plik, aby rozpocząć.",
                               anchor=tk.W, bg="#dcdcdc", font=("Helvetica", 9))
        self.status.pack(side=tk.LEFT, padx=6)

        # Wymiary obrazu po prawej stronie paska
        self.status_wymiary = tk.Label(pasek, text="",
                                       anchor=tk.E, bg="#dcdcdc", font=("Helvetica", 9))
        self.status_wymiary.pack(side=tk.RIGHT, padx=6)


    # ══════════════════════════════════════════════════════════
    #  WCZYTYWANIE OBRAZU
    # ══════════════════════════════════════════════════════════

    def wczytaj_obraz(self):
        sciezka = filedialog.askopenfilename(
            title="Otwórz zdjęcie",
            filetypes=[
                ("Obrazy", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        if not sciezka:
            return   # użytkownik anulował

        try:
            self.oryginalny_obraz = Image.open(sciezka)
            self.aktualny_obraz   = self.oryginalny_obraz.copy()
            self.sciezka_pliku    = sciezka
            self.historia         = [self.aktualny_obraz.copy()]  # reset historii

            self._wyswietl_obraz(self.aktualny_obraz)
            self._aktualizuj_info()
            self._ustaw_status(f"Otwarto: {sciezka}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć pliku:\n{e}")


    # ══════════════════════════════════════════════════════════
    #  ZAPISYWANIE OBRAZU
    # ══════════════════════════════════════════════════════════

    def zapisz_obraz(self):
        """Zapisz pod tą samą nazwą (nadpisuje plik)."""
        if self.aktualny_obraz is None:
            messagebox.showwarning("Uwaga", "Brak obrazu do zapisania.")
            return
        if self.sciezka_pliku is None:
            self.zapisz_jako()
            return

        try:
            self.aktualny_obraz.save(self.sciezka_pliku)
            self._ustaw_status(f"Zapisano: {self.sciezka_pliku}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać pliku:\n{e}")

    def zapisz_jako(self):
        """Zapisz pod nową nazwą / w nowym formacie."""
        if self.aktualny_obraz is None:
            messagebox.showwarning("Uwaga", "Brak obrazu do zapisania.")
            return

        sciezka = filedialog.asksaveasfilename(
            title="Zapisz jako",
            defaultextension=".png",
            filetypes=[
                ("PNG",  "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP",  "*.bmp"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        if not sciezka:
            return

        try:
            self.aktualny_obraz.save(sciezka)
            self.sciezka_pliku = sciezka
            self._ustaw_status(f"Zapisano jako: {sciezka}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać pliku:\n{e}")


    # ══════════════════════════════════════════════════════════
    #  COFANIE ZMIAN (Ctrl+Z)
    # ══════════════════════════════════════════════════════════

    def cofnij(self):
        """
        Mechanizm cofania – opiera się na self.historia.
        Przed każdą modyfikacją obrazu zapisz stan:
            self.historia.append(self.aktualny_obraz.copy())
        """
        if len(self.historia) <= 1:
            self._ustaw_status("Nic do cofnięcia.")
            return

        self.historia.pop()                          # usuń ostatni stan
        self.aktualny_obraz = self.historia[-1].copy()
        self._wyswietl_obraz(self.aktualny_obraz)
        self._aktualizuj_info()
        self._ustaw_status("Cofnięto ostatnią operację.")


    # ══════════════════════════════════════════════════════════
    #  WIDOK – dopasowanie do okna / oryginalny rozmiar
    # ══════════════════════════════════════════════════════════

    def dopasuj_do_okna(self):
        if self.aktualny_obraz is None:
            return
        szer_canvas = self.canvas.winfo_width()
        wys_canvas  = self.canvas.winfo_height()
        kopia = self.aktualny_obraz.copy()
        kopia.thumbnail((szer_canvas, wys_canvas))
        self._wyswietl_obraz_tymczasowy(kopia)

    def oryginalny_rozmiar(self):
        if self.aktualny_obraz is None:
            return
        self._wyswietl_obraz(self.aktualny_obraz)


    # ══════════════════════════════════════════════════════════
    #  METODY POMOCNICZE (wewnętrzne)
    # ══════════════════════════════════════════════════════════

    def _wyswietl_obraz(self, obraz: Image.Image):
        """Wyświetl obraz PIL na canvasie (pełny rozmiar)."""
        self.canvas.delete("all")
        self.obraz_tk = ImageTk.PhotoImage(obraz)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.obraz_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def _wyswietl_obraz_tymczasowy(self, obraz: Image.Image):
        """Wyświetl obraz bez nadpisywania self.aktualny_obraz (np. podgląd)."""
        self.canvas.delete("all")
        self.obraz_tk = ImageTk.PhotoImage(obraz)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.obraz_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def _aktualizuj_info(self):
        """Odśwież etykietę z informacjami o obrazie."""
        if self.aktualny_obraz is None:
            return
        w, h   = self.aktualny_obraz.size
        tryb    = self.aktualny_obraz.mode
        nazwa   = self.sciezka_pliku.split("/")[-1] if self.sciezka_pliku else "—"
        tekst   = f"Plik: {nazwa}\nRozmiar: {w} × {h} px\nTryb: {tryb}"
        self.etykieta_info.config(text=tekst)
        self.status_wymiary.config(text=f"{w} × {h} px  |  {tryb}")

    def _ustaw_status(self, tekst: str):
        self.status.config(text=tekst)

    def _placeholder(self, nazwa: str):
        """Tymczasowa funkcja – zastąp własną implementacją."""
        messagebox.showinfo("TODO", f"Tu wstaw implementację: '{nazwa}'")


    # ══════════════════════════════════════════════════════════
    #  PRZYKŁAD – SCHEMAT WŁASNEJ FUNKCJI MODYFIKUJĄCEJ OBRAZ
    # ══════════════════════════════════════════════════════════
    #
    #  def moja_operacja(self):
    #      if self.aktualny_obraz is None:
    #          return
    #
    #      # 1. Zapisz obecny stan do historii (umożliwia Ctrl+Z)
    #      self.historia.append(self.aktualny_obraz.copy())
    #
    #      # 2. Wykonaj modyfikację na aktualnym obrazie
    #      #    np. z biblioteki Pillow:
    #      from PIL import ImageFilter
    #      self.aktualny_obraz = self.aktualny_obraz.filter(ImageFilter.BLUR)
    #
    #      # 3. Odśwież widok i pasek statusu
    #      self._wyswietl_obraz(self.aktualny_obraz)
    #      self._aktualizuj_info()
    #      self._ustaw_status("Zastosowano: Moja operacja")


# ══════════════════════════════════════════════════════════════
#  PUNKT WEJŚCIA
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = EdytorZdjec(root)
    root.mainloop()