"""
Narzędzia do przetwarzania odcisków palców i szkieletyzacji KMM.
Używane biblioteki: wyłącznie numpy i PIL.
 
Typowe użycie
-------------
    from PIL import Image
    from image_processor import ImageProcessor
 
    proc     = ImageProcessor()
    obraz    = Image.open("odcisk.png")
 
    # Pełny potok (zalecane)
    binarny  = proc.preprocess_fingerprint(obraz)   # uint8, 0 = grzbiet, 255 = tło
    szkielet = proc.KMM(binarny)                     # uint8, 0 = szkielet, 255 = tło
 
    # Szybka binaryzacja bez Gabora
    szary    = proc._to_gray(obraz)
    binarny  = (szary > 128).astype("uint8") * 255   # 255 = tło, wtedy...
    # ...odwróć konwencję: 0 = grzbiet
    binarny  = 255 - binarny
    szkielet = proc.KMM(binarny)
"""
 
import numpy as np
from PIL import Image
 
 
class ImageProcessor:
 
    # ══════════════════════════════════════════════════════════════════════
    # ① Operacje morfologiczne
    # ══════════════════════════════════════════════════════════════════════
 
    def _get_structuring_element(self, size: int, shape: str) -> np.ndarray:
        """Tworzy element strukturalny o podanym rozmiarze i kształcie."""
        se = np.zeros((size, size), dtype=np.uint8)
        c  = size // 2
        if shape == 'ellipse':
            Y, X = np.ogrid[:size, :size]
            se[(Y - c) ** 2 + (X - c) ** 2 <= c ** 2] = 1
        elif shape == 'cross':
            se[c, :] = se[:, c] = 1
        elif shape == 'square':
            se[:] = 1
        return se
 
    def _to_gray(self, image: Image.Image) -> np.ndarray:
        """Konwertuje obraz PIL do tablicy odcieni szarości (uint8)."""
        return np.array(image.convert('L'))
 
    def _erode(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Erozja morfologiczna (minimum lokalne)."""
        pad = se.shape[0] // 2
        p   = np.pad(img, pad, mode='edge')
        out = np.full_like(img, 255)
        for di, dj in np.argwhere(se):
            out = np.minimum(out, p[di:di + img.shape[0], dj:dj + img.shape[1]])
        return out
 
    def _dilate(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Dylatacja morfologiczna (maksimum lokalne)."""
        pad = se.shape[0] // 2
        p   = np.pad(img, pad, mode='edge')
        out = np.zeros_like(img)
        for di, dj in np.argwhere(se):
            out = np.maximum(out, p[di:di + img.shape[0], dj:dj + img.shape[1]])
        return out
 
    def _open(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Otwarcie morfologiczne (erozja → dylatacja) – usuwa małe obiekty."""
        return self._dilate(self._erode(img, se), se)
 
    def _close(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Domknięcie morfologiczne (dylatacja → erozja) – wypełnia małe luki."""
        return self._erode(self._dilate(img, se), se)
 
    # ══════════════════════════════════════════════════════════════════════
    # ② Splotowanie 2D przez FFT (szybsze niż pętla naiwna)
    # ══════════════════════════════════════════════════════════════════════
 
    def _convolve2d(self, img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Splot liniowy 2D przez FFT. Zwraca tablicę o tym samym rozmiarze co `img`."""
        sh = tuple(
            int(2 ** np.ceil(np.log2(s + k - 1)))
            for s, k in zip(img.shape, kernel.shape)
        )
        out = np.real(np.fft.ifft2(
            np.fft.fft2(img.astype(np.float64),    sh) *
            np.fft.fft2(kernel.astype(np.float64), sh)
        ))
        ph, pw = kernel.shape[0] // 2, kernel.shape[1] // 2
        return out[ph: ph + img.shape[0], pw: pw + img.shape[1]]
 
    # ══════════════════════════════════════════════════════════════════════
    # ③ Bank filtrów Gabora
    # ══════════════════════════════════════════════════════════════════════
 
    def _gabor_kernel(self, size: int, theta: float, freq: float,
                      sigma_perp: float = 4.0,
                      sigma_par:  float = 4.0) -> np.ndarray:
        """
        Rzeczywiste (cosinusoidalne) jądro Gabora skierowane wzdłuż orientacji grzbietu `theta`.
 
        Układ współrzędnych:
          xr – prostopadle do grzbietu → oś oscylacji sinusoidalnych
          yr – wzdłuż grzbietu         → oś wydłużenia gaussowskiego
 
        Parametry
        ---------
        size       : rozmiar jądra (zalecana nieparzysta liczba całkowita)
        theta      : orientacja grzbietu w radianach
        freq       : częstotliwość przestrzenna w cyklach/piksel (typowo 1/8 … 1/12)
        sigma_perp : odchylenie standardowe Gaussa prostopadłe do grzbietu
        sigma_par  : odchylenie standardowe Gaussa wzdłuż grzbietu (≥ sigma_perp)
        """
        h            = size // 2
        x, y         = np.meshgrid(np.arange(-h, h + 1), np.arange(-h, h + 1))
        cos_t, sin_t = np.cos(theta), np.sin(theta)
        xr = -x * sin_t + y * cos_t   # oś prostopadła do grzbietów
        yr =  x * cos_t + y * sin_t   # oś wzdłuż grzbietów
        kernel = (np.exp(-0.5 * (xr ** 2 / sigma_perp ** 2 +
                                  yr ** 2 / sigma_par  ** 2))
                  * np.cos(2.0 * np.pi * freq * xr))
        kernel -= kernel.mean()        # zerowa średnia → brak przesunięcia DC
        return kernel
 
    def _estimate_orientation(self, gray: np.ndarray,
                               block: int = 16) -> np.ndarray:
        """
        Blokowa estymacja orientacji grzbietów metodą kwadratów gradientów
        (Hong, Wan & Jain 1998).
 
        Zwraca obraz orientacji z wartościami w [0, π),
        gdzie 0 oznacza poziomy grzbiet.
        """
        Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)  # filtr Sobela X
        gx = self._convolve2d(gray.astype(float), Kx)
        gy = self._convolve2d(gray.astype(float), Kx.T)              # filtr Sobela Y
 
        # Komponenty podwójnego kąta: eliminują niejednoznaczność π w orientacji grzbietów
        Vx = 2.0 * gx * gy        # ≈ sin(2θ)
        Vy = gx ** 2 - gy ** 2    # ≈ cos(2θ)
 
        H, W = gray.shape
        ori  = np.zeros((H, W), float)
 
        for r in range(0, H, block):
            for c in range(0, W, block):
                bvx = Vx[r:r + block, c:c + block].mean()
                bvy = Vy[r:r + block, c:c + block].mean()
                # θ_grzbiet = ½ · arctan2(Vx, Vy) + π/2
                ori[r:r + block, c:c + block] = \
                    0.5 * np.arctan2(bvx, bvy) + np.pi / 2.0
        return ori
 
    def gabor_enhance(self, gray: np.ndarray,
                      n_angles:   int   = 8,
                      freq:       float = 1.0 / 9.0,
                      ksize:      int   = 21,
                      sigma_perp: float = 4.0,
                      sigma_par:  float = 4.5) -> np.ndarray:
        """
        Wzmocnienie grzbietów odcisku palca za pomocą kierunkowego banku filtrów Gabora.
 
        Zakłada, że grzbiecie są CIEMNE na jasnym tle (typowy skaner optyczny).
        Zwraca tablicę float64 w [0, 1], gdzie JASNE wartości odpowiadają grzbietom.
 
        Strategia
        ---------
        1. Odwróć i znormalizuj, aby grzbiecie stały się jasne.
        2. Splot z jądrami Gabora dla n_angles orientacji.
        3. W każdym pikselu wybierz odpowiedź filtru najbliższego lokalnej orientacji.
        4. Znormalizuj odpowiedź do [0, 1].
        """
        # Odwracamy obraz (ciemne grzbiecie → jasne) i normalizujemy do [0, 1]
        f = gray.astype(np.float64)
        f = (f.max() - f) / (f.max() - f.min() + 1e-8)
 
        angles  = np.linspace(0, np.pi, n_angles, endpoint=False)
        kernels = [self._gabor_kernel(ksize, t, freq, sigma_perp, sigma_par)
                   for t in angles]
 
        # Stos wszystkich odpowiedzi Gabora: kształt (n_angles, H, W)
        resps = np.stack([self._convolve2d(f, k) for k in kernels])
 
        # Orientacja per piksel → indeks najbliższego jądra Gabora
        ori = self._estimate_orientation(gray)
        idx = np.round(
            (ori % np.pi) / np.pi * n_angles
        ).astype(int) % n_angles
 
        # Wybranie odpowiedzi dopasowanej do lokalnej orientacji (wektoryzowane)
        rows   = np.arange(gray.shape[0])[:, None]
        cols   = np.arange(gray.shape[1])[None, :]
        picked = resps[idx, rows, cols]
 
        # Normalizacja odpowiedzi do [0, 1]
        picked -= picked.min()
        picked /= (picked.max() + 1e-8)
        return picked
 
    # ══════════════════════════════════════════════════════════════════════
    # ④ Region zainteresowania (ROI)
    # ══════════════════════════════════════════════════════════════════════
 
    def _compute_roi(self, gray: np.ndarray,
                     block:      int   = 16,
                     var_thresh: float = 100.0,
                     morph_size: int   = 33) -> np.ndarray:
        """
        Oblicza maskę ROI na podstawie lokalnej wariancji jasności.
 
        Obszary o niskiej wariancji (jednolite tło lub szum na brzegach obrazu)
        są wykluczane z dalszego przetwarzania. Maska jest wygładzana morfologicznie,
        aby usunąć artefakty wynikające z podziału blokowego.
 
        Parametry
        ---------
        block      : rozmiar bloku (piksele) do obliczania wariancji lokalnej
        var_thresh : minimalna wariancja wymagana do zakwalifikowania bloku jako ROI
        morph_size : rozmiar elementu strukturalnego do morfologicznego wygładzania maski
 
        Zwraca
        ------
        Tablicę bool: True = piksel wewnątrz ROI (zawiera linie papilarne).
        """
        H, W  = gray.shape
        maska = np.zeros((H, W), dtype=np.uint8)
        f     = gray.astype(float)
 
        # Bloki o wystarczającej wariancji → wewnątrz ROI
        for r in range(0, H, block):
            for c in range(0, W, block):
                blok = f[r:r + block, c:c + block]
                if blok.var() >= var_thresh:
                    maska[r:r + block, c:c + block] = 255
 
        # Domknięcie + otwarcie: wypełnia dziury wewnątrz ROI i usuwa małe wyspy
        se    = self._get_structuring_element(morph_size, 'ellipse')
        maska = self._open(self._close(maska, se), se)
        return maska > 0
 
    # ══════════════════════════════════════════════════════════════════════
    # ⑤ Pełny potok przetwarzania wstępnego odcisku palca
    # ══════════════════════════════════════════════════════════════════════
 
    def preprocess_fingerprint(self,
                                image:      Image.Image,
                                threshold:  int   = 128,
                                freq:       float = 1.0 / 9.0,
                                n_angles:   int   = 8,
                                ksize:      int   = 21,
                                sigma_perp: float = 4.0,
                                sigma_par:  float = 4.5,
                                morph_size: int   = 3,
                                roi_block:  int   = 16,
                                roi_var:    float = 100.0) -> np.ndarray:
        """
        Pełny potok przetwarzania wstępnego:
            skala szarości → wzmocnienie Gaborem → binaryzacja progowa → maska ROI
 
        Zwraca
        ------
        uint8 ndarray –  0 = piksel grzbietu (czarny linia),  255 = tło (białe).
        Wynik można przekazać bezpośrednio do KMM().
 
        Parametry
        ----------
        threshold  : próg binaryzacji (0–255) nakładany na wzmocniony obraz Gabora.
                     Piksele o wartości >= threshold → grzbiet (0, czarny).
                     Piksele o wartości  < threshold → tło    (255, białe).
                     Wartość domyślna 128 = połowa zakresu; dostosuj empirycznie:
                       wyższy próg  → mniej grzbietów (surowsza selekcja),
                       niższy próg  → więcej grzbietów (łagodniejsza selekcja).
        freq       : częstotliwość przestrzenna grzbietów (cykle/piksel).
                     Domyślnie 1/9 ≈ 500 dpi.
        n_angles   : liczba orientacji banku Gabora.
        ksize      : rozmiar jądra Gabora w pikselach (powinna być nieparzysta).
        sigma_perp : σ Gabora prostopadłe do grzbietu.
        sigma_par  : σ Gabora wzdłuż grzbietu (wydłużenie filtru).
        morph_size : rozmiar elementu strukturalnego do morfologicznego czyszczenia.
        roi_block  : rozmiar bloku (piksele) do wyznaczania ROI.
        roi_var    : próg wariancji do wyznaczania ROI.
        """
        szary = self._to_gray(image)
 
        # ① Wzmocnienie grzbietów filtrem Gabora
        #    Wynik: float [0, 1], JASNE wartości = grzbiecie
        wzmocniony = self.gabor_enhance(szary,
                                        n_angles=n_angles, freq=freq,
                                        ksize=ksize,
                                        sigma_perp=sigma_perp,
                                        sigma_par=sigma_par)
 
        # ② Morfologiczne czyszczenie wzmocnionego obrazu
        #    Domknięcie zamyka drobne luki w grzbietach; otwarcie usuwa szum
        wzmU8 = (wzmocniony * 255).astype(np.uint8)
        se    = self._get_structuring_element(morph_size, 'ellipse')
        wzmU8 = self._open(self._close(wzmU8, se), se)
 
        # ③ Binaryzacja z podanym progiem
        #    Jasny piksel (wzmU8 >= threshold) = grzbiet → 0  (czarny)
        #    Ciemny piksel (wzmU8  < threshold) = tło    → 255 (biały)
        binarny = np.where(wzmU8 >= threshold,
                           np.uint8(0),
                           np.uint8(255))
 
        # ④ Wyznaczenie i zastosowanie maski ROI
        #    Piksele poza ROI (szum na brzegach, tło skanera) → tło (255)
        roi = self._compute_roi(szary,
                                block=roi_block,
                                var_thresh=roi_var,
                                morph_size=max(3, roi_block * 2 + 1))
        binarny[~roi] = 255
 
        return binarny
 
    # ══════════════════════════════════════════════════════════════════════
    # ⑥ Szkieletyzacja KMM  (Saeed, Rybnik, Tabędzki, Adamski 2002)
    # ══════════════════════════════════════════════════════════════════════
 
    def KMM(self, binarny: np.ndarray) -> np.ndarray:
        """
        Algorytm szkieletyzacji KMM – ścienienie do jednego piksela szerokości.
 
        Wejście
        -------
        binarny : uint8 ndarray –  0 = piksel grzbietu (obiekt), 255 = tło.
                  Uzyskaj go z preprocess_fingerprint() lub innej binaryzacji.
 
        Wyjście
        -------
        uint8 ndarray –  0 = piksel szkieletu, 255 = tło.
 
        Kroki algorytmu (powtarzane do zbieżności)
        -------------------------------------------
        1. Piksele obiektu (1) dotykające tła krawędziowo (4-spójność)   → etykieta 2
        2. Piksele obiektu (1) dotykające tła wyłącznie narożnikowo       → etykieta 3
        3. Piksele konturowe (2 lub 3), dla których największa spójna
           składowa ich sąsiadów konturowych ma rozmiar 2–4               → usuń (→ 0)
        4. Pozostałe piksele z N=2: oblicz wagę 8 sąsiadów, sprawdź LUT
              waga w LUT → usuń (→ 0);   waga poza LUT → zachowaj (→ 1)
        5. To samo dla N=3.
        6. Jeśli obraz niezmieniony → stop.
 
        Kodowanie wag (z artykułu):
            128 │  1 │  2
             64 │  x │  4
             32 │ 16 │  8
        Kierunek N = góra (mniejszy indeks wiersza w tablicy), S = dół.
        """
        # ── Tablica LUT usuwania – faza C (indeksowanie boole'owskie, O(1)) ─
        _lut = np.zeros(256, dtype=bool)
        _lut[[
              3,   5,   7,  12,  13,  14,  15,  20,
             21,  22,  23,  28,  29,  30,  31,  48,
             52,  53,  54,  55,  56,  60,  61,  62,
             63,  65,  67,  69,  71,  77,  79,  80,
             81,  83,  84,  85,  86,  87,  88,  89,
             91,  92,  93,  94,  95,  97,  99, 101,
            103, 109, 111, 112, 113, 115, 116, 117,
            118, 119, 120, 121, 123, 124, 125, 126,
            127, 131, 133, 135, 141, 143, 149, 151,
            157, 159, 181, 183, 189, 191, 192, 193,
            195, 197, 199, 205, 207, 208, 209, 211,
            212, 213, 214, 215, 216, 217, 219, 220,
            221, 222, 223, 224, 225, 227, 229, 231,
            237, 239, 240, 241, 243, 244, 245, 246,
            247, 248, 249, 251, 252, 253, 254, 255,
        ]] = True
 
        # ── Stałe pomocnicze ────────────────────────────────────────────────
        _Z = dict(mode='constant', constant_values=0)
 
        # ── Tablica LUT fazy B: rozmiar największej spójnej składowej ───────
        #
        # Sąsiedzi kodowani bitami: bit0=NW, bit1=N, bit2=NE, bit3=W,
        #                           bit4=E,  bit5=SW, bit6=S, bit7=SE
        #
        # Dwa sąsiedzi są „przylegający" (pol. „przylegający do siebie"),
        # jeśli są 8-spójni ze sobą w pierścieniu 3×3, tzn. różnią się
        # co najwyżej o 1 w każdym wymiarze.
        _adj_b = [
            [1, 3],          # NW(0)  sąsiaduje z: N, W
            [0, 2, 3, 4],    # N(1)   sąsiaduje z: NW, NE, W, E
            [1, 4],          # NE(2)  sąsiaduje z: N, E
            [0, 1, 5, 6],    # W(3)   sąsiaduje z: NW, N, SW, S
            [1, 2, 6, 7],    # E(4)   sąsiaduje z: N, NE, S, SE
            [3, 6],          # SW(5)  sąsiaduje z: W, S
            [3, 4, 5, 7],    # S(6)   sąsiaduje z: W, E, SW, SE
            [4, 6],          # SE(7)  sąsiaduje z: E, S
        ]
        _lut_b = np.zeros(256, dtype=np.uint8)
        for _wzorzec in range(256):
            _bity = [i for i in range(8) if (_wzorzec >> i) & 1]
            if not _bity:
                continue
            _zbior   = set(_bity)
            _odwiedz = set()
            _maks    = 0
            for _start in _bity:
                if _start in _odwiedz:
                    continue
                # BFS po grafie sąsiedztwa w pierścieniu 3×3
                _kolejka = [_start]
                _odwiedz.add(_start)
                _rozmiar = 0
                while _kolejka:
                    _wezel = _kolejka.pop(0)
                    _rozmiar += 1
                    for _nb in _adj_b[_wezel]:
                        if _nb in _zbior and _nb not in _odwiedz:
                            _odwiedz.add(_nb)
                            _kolejka.append(_nb)
                _maks = max(_maks, _rozmiar)
            _lut_b[_wzorzec] = _maks
 
        # ── Obraz roboczy: {0 = tło, 1 = obiekt} ───────────────────────────
        # Wejście: 0 = grzbiet (obiekt), 255 = tło → odwracamy konwencję wewnętrznie
        img = (binarny == 0).astype(np.uint8)
 
        while True:
            poprzedni = img.copy()
 
            # ── Faza A: klasyfikacja pikseli brzegowych ─────────────────────
            p = np.pad(img, 1, **_Z)
 
            # Piksel obiektu z 4-spójnym sąsiadem tła → kontur krawędziowy (2)
            krawedz = ((p[:-2, 1:-1] == 0) | (p[2:, 1:-1] == 0) |
                       (p[1:-1, :-2] == 0) | (p[1:-1, 2:] == 0))
            img[(img == 1) & krawedz] = 2
 
            # Piksel obiektu z sąsiadem tła wyłącznie po przekątnej → etykieta 3
            naroznik = ((p[:-2, :-2] == 0) | (p[:-2, 2:] == 0) |
                        (p[2:,  :-2] == 0) | (p[2:,  2:] == 0))
            img[(img == 1) & naroznik] = 3
 
            # ── Faza B: usuwanie pikseli konturowych ────────────────────────
            #
            # Kryterium: piksel konturowy jest usuwany, gdy największa spójna
            # składowa jego KONTUROWYCH sąsiadów (etykieta 2 lub 3) w pierścieniu
            # 3×3 ma rozmiar 2–4.
            #
            # „Sąsiadujący ze sobą" oznacza 8-spójność w pierścieniu (patrz _adj_b).
            # Dzięki temu:
            #   – środkowy piksel poziomej linii szkieletu ma sąsiadów W i E,
            #     które NIE sąsiadują ze sobą (odległość 2 kolumny) → maks=1 → zachowany ✓
            #   – narożnik prostokąta ma sąsiadów E i S, które sąsiadują → maks=2 → usunięty ✓
            kontur = (img == 2) | (img == 3)
            pc = np.pad(kontur.astype(np.uint8), 1, **_Z)
            # Kodowanie sąsiadów konturowych jako 8-bitowy wzorzec (NW=bit0 … SE=bit7)
            wzorzec_b = (pc[:-2, :-2]          |
                         pc[:-2, 1:-1] * 2     |
                         pc[:-2, 2:  ] * 4     |
                         pc[1:-1, :-2] * 8     |
                         pc[1:-1, 2: ] * 16    |
                         pc[2:,  :-2 ] * 32    |
                         pc[2:,  1:-1] * 64    |
                         pc[2:,  2:  ] * 128).astype(np.uint8)
            maks_skladowa = _lut_b[wzorzec_b]
            img[kontur & (maks_skladowa >= 2) & (maks_skladowa <= 4)] = 0
 
            # ── Faza C: sekwencyjne ścienienie wagowe, N=2 potem N=3 ────────
            #
            # Schemat blokowy z artykułu (Dodatek) pokazuje jawną pętlę rastrową
            # i=1..i_max. Usuwanie równoległe (wektoryzowane) jest BŁĘDNE:
            # dla paska 2-pikselowego oba wiersze mają wagi w LUT jednocześnie
            # i cały obiekt znika. Kolejność rastrowa (góra→dół, lewo→prawo)
            # zapewnia, że pierwszy wiersz jest usunięty przed obliczeniem wagi
            # drugiego – drugi widzi wagę 68 (spoza LUT) i przeżywa jako szkielet.
            H, W = img.shape
            for N in (2, 3):
                for r, c in np.argwhere(img == N):   # kolejność rastrowa gwarantowana
                    # Waga obliczana na bieżąco z już zaktualizowanego obrazu
                    w = 0
                    if r > 0:
                        if c > 0   and img[r-1, c-1]: w += 128  # NW
                        if             img[r-1, c  ]: w +=   1  # N
                        if c < W-1 and img[r-1, c+1]: w +=   2  # NE
                    if c > 0   and img[r,   c-1]: w +=  64  # W
                    if c < W-1 and img[r,   c+1]: w +=   4  # E
                    if r < H-1:
                        if c > 0   and img[r+1, c-1]: w +=  32  # SW
                        if             img[r+1, c  ]: w +=  16  # S
                        if c < W-1 and img[r+1, c+1]: w +=   8  # SE
                    img[r, c] = 0 if _lut[w] else 1
 
            # ── Sprawdzenie zbieżności ─────────────────────────────────────
            if np.array_equal(img, poprzedni):
                break
 
        # Powrót do konwencji wyjściowej: 0 = szkielet (czarny), 255 = tło (białe)
        return np.where(img == 1, np.uint8(0), np.uint8(255))


       # ══════════════════════════════════════════════════════════════════════
    # ⑦ Szkielet morfologiczny (zachowany do porównania z KMM)
    # ══════════════════════════════════════════════════════════════════════
 
    def skeletonize(self, binarny: np.ndarray) -> np.ndarray:
        """
        Szkielet morfologiczny.
 
        Algorytm iteracyjnie eroduje obraz i zbiera resztki (residua) między
        kolejnymi krokami erozji a ich otwarciem, aż obiekt całkowicie zniknie.
        Suma residuów tworzy szkielet.
 
        Wejście
        -------
        binarny : uint8 ndarray – 0 = piksel grzbietu, 255 = tło.
                  Ten sam format co wejście/wyjście KMM().
 
        Wyjście
        -------
        uint8 ndarray – 0 = piksel szkieletu, 255 = tło.
        """
        # Konwersja do konwencji wewnętrznej: 255 = obiekt, 0 = tło
        aktualny = np.where(binarny == 0, np.uint8(255), np.uint8(0))
 
        # _erode używa mode='edge', więc wypełniony obiekt bez ramki nigdy nie
        # zostałby wyerodowany. Dodajemy 1-pikselową ramkę zer, aby erozja
        # mogła stopniowo zjadać krawędzie i algorytm mógł osiągnąć zbieżność.
        aktualny = np.pad(aktualny, 1, mode='constant', constant_values=0)
 
        se       = self._get_structuring_element(3, 'cross')
        szkielet = np.zeros_like(aktualny)
 
        while aktualny.max() > 0:
            erodowany = self._erode(aktualny, se)
            otwarty   = self._dilate(erodowany, se)
            # Residuum: piksele obiektu utracone podczas otwarcia
            residuum  = np.clip(
                aktualny.astype(np.int16) - otwarty.astype(np.int16), 0, 255
            ).astype(np.uint8)
            szkielet  = np.maximum(szkielet, residuum)
            aktualny  = erodowany
 
        # Odcinamy pomocniczą ramkę i wracamy do konwencji: 0 = szkielet, 255 = tło
        szkielet = szkielet[1:-1, 1:-1]
        return np.where(szkielet > 0, np.uint8(0), np.uint8(255))
    
    import numpy as np

    # def skeletonize(self, image: np.ndarray, kernel: np.ndarray = None) -> np.ndarray:
    #     """
    #     Szkieletyzacja morfologiczna oparta wyłącznie na NumPy i metodach klasy.
    #     Konwencja: obiekt = jasne piksele (>0), tło = czarne piksele (0).
    #     """
    #     # Jeśli nie podano kernela, pobieramy domyślny z metody klasy
    #     if kernel is None:
    #         kernel = self._get_structuring_element(3, 'cross')

    #     # Dodajemy 1-pikselową ramkę zer, aby zapobiec nieskończonej pętli
    #     # w przypadku, gdy obiekt dotyka krawędzi obrazu.
    #     img = np.pad(image.copy(), 1, mode='constant', constant_values=0)
    #     skeleton = np.zeros_like(img)

    #     # Główna pętla szkieletyzacji Lantuéjoula
    #     while img.max() > 0:  # img.max() > 0 jest szybsze i bezpieczniejsze niż np.sum() == 0
    #         # Zastępujemy cv.erode i cv.dilate wewnętrznymi metodami
    #         erosion = self._erode(img, kernel)
    #         dilatate = self._dilate(erosion, kernel)

    #         # Bezpieczne odejmowanie zapobiegające błędom underflow (wartości ujemnych)
    #         subs_img = np.clip(
    #             img.astype(np.int16) - dilatate.astype(np.int16), 0, 255
    #         ).astype(np.uint8)

    #         # Zastępujemy cv.bitwise_or operatorem np.maximum (dla maski 0 i 255 działa identycznie)
    #         skeleton = np.maximum(skeleton, subs_img)
            
    #         # Aktualizujemy obraz do kolejnej iteracji
    #         img = erosion

    #     # Odcinamy pomocniczą ramkę
    #     skeleton = skeleton[1:-1, 1:-1]

    #     # =====================================================================
    #     # ORYGINALNY POST-PROCESSING Z PRZESUNIĘCIAMI (Przetłumaczony na NumPy)
    #     # Odkomentuj poniższy kod tylko wtedy, gdy na pewno go potrzebujesz!
    #     # =====================================================================
        
    #     # Przesunięcie w dół
    #     down = np.zeros_like(skeleton)
    #     down[1:-1, :] = skeleton[0:-2, :]
    #     down_mask = np.clip(down.astype(np.int16) - skeleton.astype(np.int16), 0, 255).astype(np.uint8)
    #     down_mask[0:-2, :] = down_mask[1:-1, :]

    #     # Przesunięcie w lewo
    #     left = np.zeros_like(skeleton)
    #     left[:, 1:-1] = skeleton[:, 0:-2]
    #     left_mask = np.clip(left.astype(np.int16) - skeleton.astype(np.int16), 0, 255).astype(np.uint8)
    #     left_mask[:, 0:-2] = left_mask[:, 1:-1]

    #     # Zastąpienie obrazu samą maską 'down_mask' (zgodnie z oryginalnym cv.bitwise_or)
    #     skeleton = down_mask.copy()
        

    #     # Finalne formatowanie wyjścia
    #     output = np.zeros_like(skeleton)
    #     output[skeleton < 250] = 255

    #     return output
    
        # ══════════════════════════════════════════════════════════════════════
    # ⑧ Wykrywanie minucji metodą liczby skrzyżowań (crossing number)
    # ══════════════════════════════════════════════════════════════════════
 
    def detect_minutiae(self,
                        szkielet:    np.ndarray,
                        margines:    int = 10) -> dict:
        """
        Wykrywa minucje na obrazie szkieletu metodą liczby skrzyżowań (CN).
 
        Liczba skrzyżowań dla piksela p:
            CN = 1/2 * sum|P_k - P_{k+1}|   (k = 1..8, indeksowanie cykliczne)
        gdzie P_k to wartości 8 sasiadow w kolejnosci zgodnej z ruchem wskazowek
        zegara, zakodowane jako 0/1.
 
        Interpretacja CN:
            CN = 1  zakończenie grzbietu  (ridge ending)
            CN = 3  bifurkacja            (ridge bifurcation)
 
        Parametry
        ----------
        szkielet  : uint8 ndarray - 0 = piksel szkieletu, 255 = tlo.
                    Wynik KMM() lub skeletonize().
        margines  : szerokosc ramki (piksele) wykluczanej z detekcji.
                    Usuwa falszywe minucje na brzegach obrazu / maski ROI.
 
        Zwraca
        ------
        Slownik z kluczami:
            'zakonczenia' : lista krotek (wiersz, kolumna) zakonczen grzbietow
            'bifurkacje'  : lista krotek (wiersz, kolumna) bifurkacji
        """
        # Binaryzacja szkieletu: 1 = piksel szkieletu, 0 = tlo
        s = (szkielet == 0).astype(np.int16)
 
        H, W = s.shape
        p    = np.pad(s, 1, mode='constant', constant_values=0)
 
        # 8 sasiadow w kolejnosci zgodnej z ruchem wskazowek zegara:
        #   NW -> N -> NE -> E -> SE -> S -> SW -> W
        sasiedzi = np.stack([
            p[:-2, :-2],    # NW
            p[:-2, 1:-1],   # N
            p[:-2, 2:  ],   # NE
            p[1:-1, 2: ],   # E
            p[2:,   2: ],   # SE
            p[2:,  1:-1],   # S
            p[2:,  :-2 ],   # SW
            p[1:-1, :-2],   # W
        ], axis=0)  # ksztalt: (8, H, W)
 
        # CN = 1/2 * sum|P_k - P_{k+1}|  (k cykliczne po 8 sasiadach)
        suma = np.zeros((H, W), dtype=np.int16)
        for k in range(8):
            suma += np.abs(sasiedzi[k] - sasiedzi[(k + 1) % 8])
        cn = (suma // 2).astype(np.uint8)
 
        # Maska aktywnych pikseli szkieletu (bez marginesu przy brzegu)
        maska = np.zeros((H, W), dtype=bool)
        maska[margines:H - margines, margines:W - margines] = True
        maska &= (s == 1)
 
        zakonczenia = [tuple(pkt) for pkt in np.argwhere(maska & (cn == 1))]
        bifurkacje  = [tuple(pkt) for pkt in np.argwhere(maska & (cn == 3))]
 
        return {
            'zakonczenia': zakonczenia,
            'bifurkacje':  bifurkacje,
        }
 
    def rysuj_minucje(self,
                      szkielet: np.ndarray,
                      minucje:  dict,
                      r:        int = 4) -> np.ndarray:
        """
        Rysuje minucje na kopii obrazu szkieletu jako kolorowy obraz RGB.
 
        Zakonczenia  czerwone kolka
        Bifurkacje   niebieskie kolka
 
        Parametry
        ----------
        szkielet : uint8 ndarray - 0 = piksel szkieletu, 255 = tlo.
        minucje  : slownik zwrocony przez detect_minutiae().
        r        : promien kolka oznaczajacego minucje (piksele).
 
        Zwraca
        ------
        uint8 ndarray ksztaltu (H, W, 3) - obraz RGB gotowy do zapisu/wyswietlenia.
        """
        # Konwersja szkieletu do RGB (czarne linie na bialym tle)
        rgb = np.stack([szkielet, szkielet, szkielet], axis=-1).copy()
 
        H, W = szkielet.shape
        Y, X = np.ogrid[:H, :W]
 
        def _kolo(srodek, promien):
            wy, wx = srodek
            return (Y - wy) ** 2 + (X - wx) ** 2 <= promien ** 2
 
        # Zakonczenia - czerwone (R=255, G=0, B=0)
        for pkt in minucje.get('zakonczenia', []):
            m = _kolo(pkt, r)
            rgb[m, 0] = 255
            rgb[m, 1] = 0
            rgb[m, 2] = 0
 
        # Bifurkacje - niebieskie (R=0, G=0, B=255)
        for pkt in minucje.get('bifurkacje', []):
            m = _kolo(pkt, r)
            rgb[m, 0] = 0
            rgb[m, 1] = 0
            rgb[m, 2] = 255
 
        return rgb.astype(np.uint8)

