# import numpy as np
# from image_utils import ImageUtils


# class KMMSkeletonizer:
#     """
#     Szkieletyzacja algorytmem KMM (Saeed, Rybnik, Tabędzki, Adamski 2002).

#     Wejście/wyjście wszystkich metod:
#         ndarray uint8 – 0 = piksel obiektu/szkieletu, 255 = tło.
#     """

#     def __init__(self):
#         self._lut_c = self._build_lut_c()
#         self._lut_b = self._build_lut_b()

#     # ------------------------------------------------------------------ #
#     # LUT-y (budowane raz)                                               #
#     # ------------------------------------------------------------------ #

#     @staticmethod
#     def _build_lut_c() -> np.ndarray:
#         """LUT fazy C – wagi podlegające usunięciu."""
#         lut = np.zeros(256, dtype=bool)
#         lut[[
#               3,   5,   7,  12,  13,  14,  15,  20,
#              21,  22,  23,  28,  29,  30,  31,  48,
#              52,  53,  54,  55,  56,  60,  61,  62,
#              63,  65,  67,  69,  71,  77,  79,  80,
#              81,  83,  84,  85,  86,  87,  88,  89,
#              91,  92,  93,  94,  95,  97,  99, 101,
#             103, 109, 111, 112, 113, 115, 116, 117,
#             118, 119, 120, 121, 123, 124, 125, 126,
#             127, 131, 133, 135, 141, 143, 149, 151,
#             157, 159, 181, 183, 189, 191, 192, 193,
#             195, 197, 199, 205, 207, 208, 209, 211,
#             212, 213, 214, 215, 216, 217, 219, 220,
#             221, 222, 223, 224, 225, 227, 229, 231,
#             237, 239, 240, 241, 243, 244, 245, 246,
#             247, 248, 249, 251, 252, 253, 254, 255,
#         ]] = True
#         return lut

#     @staticmethod
#     def _build_lut_b() -> np.ndarray:
#         """LUT fazy B – rozmiar największej spójnej składowej sąsiadów."""
#         adj = [
#             [1, 3],       # NW
#             [0, 2, 3, 4], # N
#             [1, 4],       # NE
#             [0, 1, 5, 6], # W
#             [1, 2, 6, 7], # E
#             [3, 6],       # SW
#             [3, 4, 5, 7], # S
#             [4, 6],       # SE
#         ]
#         lut = np.zeros(256, dtype=np.uint8)
#         for wzorzec in range(256):
#             bity = [i for i in range(8) if (wzorzec >> i) & 1]
#             if not bity: continue
#             zbior   = set(bity)
#             visited = set()
#             maks    = 0
#             for start in bity:
#                 if start in visited: continue
#                 queue   = [start]
#                 visited.add(start)
#                 size    = 0
#                 while queue:
#                     node = queue.pop(0)
#                     size += 1
#                     for nb in adj[node]:
#                         if nb in zbior and nb not in visited:
#                             visited.add(nb)
#                             queue.append(nb)
#                 maks = max(maks, size)
#             lut[wzorzec] = maks
#         return lut

#     # ------------------------------------------------------------------ #
#     # KMM                                                                 #
#     # ------------------------------------------------------------------ #

#     def skeletonize(self, binary: np.ndarray) -> np.ndarray:
#         """
#         Algorytm KMM: ścienienie do jednego piksela.

#         Parametry
#         ----------
#         binary : uint8 ndarray – 0 = grzbiet (obiekt), 255 = tło.

#         Zwraca
#         ------
#         uint8 ndarray – 0 = szkielet, 255 = tło.
#         """
#         Z   = dict(mode='constant', constant_values=0)
#         img = (binary == 0).astype(np.uint8)

#         while True:
#             prev = img.copy()

#             # Faza A – klasyfikacja pikseli brzegowych
#             p        = np.pad(img, 1, **Z)
#             edge     = ((p[:-2,1:-1]==0)|(p[2:,1:-1]==0)|
#                         (p[1:-1,:-2]==0)|(p[1:-1,2:]==0))
#             img[(img==1) & edge] = 2
#             corner   = ((p[:-2,:-2]==0)|(p[:-2,2:]==0)|
#                         (p[2:, :-2]==0)|(p[2:, 2:]==0))
#             img[(img==1) & corner] = 3

#             # Faza B – usuwanie pikseli konturowych
#             contour   = (img==2)|(img==3)
#             pc        = np.pad(contour.astype(np.uint8), 1, **Z)
#             pattern_b = (pc[:-2,:-2]         |
#                          pc[:-2,1:-1] * 2    |
#                          pc[:-2,2:  ] * 4    |
#                          pc[1:-1,:-2] * 8    |
#                          pc[1:-1,2: ] * 16   |
#                          pc[2:, :-2 ] * 32   |
#                          pc[2:, 1:-1] * 64   |
#                          pc[2:, 2:  ] * 128).astype(np.uint8)
#             max_comp  = self._lut_b[pattern_b]
#             img[contour & (max_comp >= 2) & (max_comp <= 4)] = 0

#             # Faza C – sekwencyjne ścienienie wagowe (rastrowe, N=2 → N=3)
#             H, W = img.shape
#             for N in (2, 3):
#                 for r, c in np.argwhere(img == N):
#                     w = 0
#                     if r > 0:
#                         if c > 0   and img[r-1,c-1]: w += 128
#                         if             img[r-1,c  ]: w +=   1
#                         if c < W-1 and img[r-1,c+1]: w +=   2
#                     if c > 0   and img[r,  c-1]: w +=  64
#                     if c < W-1 and img[r,  c+1]: w +=   4
#                     if r < H-1:
#                         if c > 0   and img[r+1,c-1]: w +=  32
#                         if             img[r+1,c  ]: w +=  16
#                         if c < W-1 and img[r+1,c+1]: w +=   8
#                     img[r, c] = 0 if self._lut_c[w] else 1

#             if np.array_equal(img, prev):
#                 break

#         return np.where(img == 1, np.uint8(0), np.uint8(255))

#     # ------------------------------------------------------------------ #
#     # Zhang-Suen (lepiej zachowuje bifurkacje niż KMM)                   #
#     # ------------------------------------------------------------------ #

#     def zhang_suen(self, binary: np.ndarray) -> np.ndarray:
#         """
#         Zhang-Suen thinning.

#         Zalecany gdy detekcja bifurkacji jest priorytetem — KMM ma tendencję
#         do „rozrywania" T-skrzyżowań, przez co bifurkacje znikają.
#         Wejście/wyjście: identyczne jak skeletonize().
#         """
#         img = (binary == 0).astype(np.uint8)

#         def _step(img, step):
#             to_del = []
#             for r, c in zip(*np.where(img == 1)):
#                 if r == 0 or r == img.shape[0]-1 or c == 0 or c == img.shape[1]-1:
#                     continue
#                 P = [img[r-1,c], img[r-1,c+1], img[r,c+1], img[r+1,c+1],
#                      img[r+1,c], img[r+1,c-1], img[r,c-1], img[r-1,c-1]]
#                 S = sum(P)
#                 if not (2 <= S <= 6): continue
#                 T = sum(1 for i in range(8) if P[i]==0 and P[(i+1)%8]==1)
#                 if T != 1: continue
#                 if step == 1:
#                     if P[0]*P[2]*P[4] != 0: continue
#                     if P[2]*P[4]*P[6] != 0: continue
#                 else:
#                     if P[0]*P[2]*P[6] != 0: continue
#                     if P[0]*P[4]*P[6] != 0: continue
#                 to_del.append((r, c))
#             for r, c in to_del:
#                 img[r, c] = 0
#             return len(to_del)

#         while True:
#             if _step(img, 1) == 0 and _step(img, 2) == 0:
#                 break
#         return np.where(img == 1, np.uint8(0), np.uint8(255))

#     # ------------------------------------------------------------------ #
#     # Szkielet morfologiczny                                              #
#     # ------------------------------------------------------------------ #


#     # ------------------------------------------------------------------ #
#     # K3M  (Saeed, Tabedzki, Rybnik, Adamski 2010)                      #
#     # ------------------------------------------------------------------ #

#     _K3M_A0 = frozenset([
#         3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96,
#         112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193,
#         195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247,
#         248, 249, 251, 252, 253, 254,
#     ])
#     _K3M_A1 = frozenset([7, 14, 28, 56, 112, 131, 193, 224])
#     _K3M_A2 = frozenset([
#         7, 14, 15, 28, 30, 56, 60, 112, 120, 131, 135, 193, 195, 224, 225, 240,
#     ])
#     _K3M_A3 = frozenset([
#         7, 14, 15, 28, 30, 31, 56, 60, 62, 112, 120, 124, 131, 135,
#         143, 193, 195, 199, 224, 225, 227, 240, 241, 248,
#     ])
#     _K3M_A4 = frozenset([
#         7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126,
#         131, 135, 143, 159, 193, 195, 199, 207, 224, 225, 227, 231,
#         240, 241, 243, 248, 249, 252,
#     ])
#     _K3M_A5 = frozenset([
#         7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126,
#         131, 135, 143, 159, 191, 193, 195, 199, 207, 224, 225, 227,
#         231, 239, 240, 241, 243, 248, 249, 251, 252, 254,
#     ])
#     _K3M_A1PIX = frozenset([
#         3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96,
#         112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193,
#         195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247,
#         248, 249, 251, 252, 253, 254,
#     ])
#     _K3M_W = np.array([[128, 1, 2], [64, 0, 4], [32, 16, 8]], dtype=np.uint8)

#     def _k3m_weight(self, img: np.ndarray, r: int, c: int) -> int:
#         """Waga sasiedztwa 3x3 piksela (r, c)."""
#         return int(np.sum((img[r-1:r+2, c-1:c+2] > 0).astype(np.uint8) * self._K3M_W))

#     def k3m(self, binary: np.ndarray) -> np.ndarray:
#         """
#         Algorytm K3M (Saeed, Tabedzki, Rybnik, Adamski 2010).

#         Rozwinięcie KMM z 5 fazami usuwania pikseli brzegowych (A1-A5).
#         Zapewnia lepszą redukcję bledu kata prostego niz KMM.

#         Struktura iteracji:
#             Faza 0    : piksele brzegowe (waga w A0)
#             Fazy 1-5  : usuwanie z rosnaca liczba sasiadow (A1-A5)
#             Faza konc : scienienie do 1 piksela (A1pix)

#         Wejscie/wyjscie: identyczne jak skeletonize().
#         """
#         img        = (binary == 0).astype(np.uint8)
#         rows, cols = img.shape
#         phases     = [self._K3M_A1, self._K3M_A2, self._K3M_A3,
#                       self._K3M_A4, self._K3M_A5]

#         while True:
#             modified = False

#             # Faza 0 - oznaczenie pikseli brzegowych
#             border = [
#                 (r, c)
#                 for r in range(1, rows - 1)
#                 for c in range(1, cols - 1)
#                 if img[r, c] == 1 and self._k3m_weight(img, r, c) in self._K3M_A0
#             ]

#             # Fazy 1-5 - usuwanie pikseli
#             for phase_lut in phases:
#                 to_del = [
#                     (r, c) for r, c in border
#                     if img[r, c] == 1 and self._k3m_weight(img, r, c) in phase_lut
#                 ]
#                 if to_del:
#                     for r, c in to_del:
#                         img[r, c] = 0
#                     modified = True

#             if not modified:
#                 break

#         # Faza koncowa - scienienie do 1 piksela (A1pix)
#         changed = True
#         while changed:
#             changed = False
#             to_del  = [
#                 (r, c)
#                 for r in range(1, rows - 1)
#                 for c in range(1, cols - 1)
#                 if img[r, c] == 1 and self._k3m_weight(img, r, c) in self._K3M_A1PIX
#             ]
#             if to_del:
#                 for r, c in to_del:
#                     img[r, c] = 0
#                 changed = True

#         return np.where(img == 1, np.uint8(0), np.uint8(255))

#     def morphological(self, binary: np.ndarray) -> np.ndarray:
#         """
#         Szkielet morfologiczny (iteracyjna erozja + residua).

#         Klasyczna alternatywa — wolniejsza, zachowuje topologię obiektu.
#         Wejście/wyjście: identyczne jak skeletonize().
#         """
#         img      = (binary == 0).astype(np.uint8)
#         img      = np.pad(img, 1, mode='constant', constant_values=0)
#         skeleton = np.zeros_like(img)

#         while img.max() > 0:
#             eroded   = ImageUtils.erode_cross(img)
#             opened   = ImageUtils.dilate_cross(eroded)
#             residue  = np.clip(img.astype(np.int16) - opened.astype(np.int16),
#                                0, 1).astype(np.uint8)
#             skeleton = np.maximum(skeleton, residue)
#             img      = eroded

#         skeleton = skeleton[1:-1, 1:-1]
#         return np.where(skeleton > 0, np.uint8(0), np.uint8(255))


import numpy as np
from image_utils import ImageUtils


class Skeletonizer:
    """
    Szkieletyzacja obrazu binarnego odcisku palca.

    Konwencja wejścia/wyjścia wszystkich metod:
        ndarray uint8 – 0 = piksel obiektu/szkieletu, 255 = tło

    Metody:
        kmm          – KMM (Saeed, Rybnik, Tabędzki, Adamski 2002)
        k3m          – K3M (Saeed, Tabędzki, Rybnik, Adamski 2010)
        zhang_suen   – Zhang-Suen (1984), najlepiej zachowuje bifurkacje
        morphological – szkielet morfologiczny (erozja krzyżowa + residua)
    """

    # ------------------------------------------------------------------ #
    # KMM — tablice LUT budowane raz przy pierwszym użyciu               #
    # ------------------------------------------------------------------ #

    def __init__(self):
        self._kmm_lut_c = self._build_kmm_lut_c()
        self._kmm_lut_b = self._build_kmm_lut_b()

    @staticmethod
    def _build_kmm_lut_c() -> np.ndarray:
        """LUT fazy C algorytmu KMM – wagi podlegające usunięciu."""
        lut = np.zeros(256, dtype=bool)
        lut[[
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
        return lut

    @staticmethod
    def _build_kmm_lut_b() -> np.ndarray:
        """LUT fazy B algorytmu KMM – rozmiar największej spójnej składowej."""
        adj = [
            [1, 3], [0, 2, 3, 4], [1, 4],
            [0, 1, 5, 6], [1, 2, 6, 7],
            [3, 6], [3, 4, 5, 7], [4, 6],
        ]
        lut = np.zeros(256, dtype=np.uint8)
        for wzorzec in range(256):
            bity = [i for i in range(8) if (wzorzec >> i) & 1]
            if not bity:
                continue
            zbior   = set(bity)
            visited = set()
            maks    = 0
            for start in bity:
                if start in visited:
                    continue
                queue = [start]
                visited.add(start)
                size  = 0
                while queue:
                    node = queue.pop(0)
                    size += 1
                    for nb in adj[node]:
                        if nb in zbior and nb not in visited:
                            visited.add(nb)
                            queue.append(nb)
                maks = max(maks, size)
            lut[wzorzec] = maks
        return lut

    # ------------------------------------------------------------------ #
    # K3M — tablice LUT jako atrybuty klasy                              #
    # ------------------------------------------------------------------ #

    _K3M_A0 = frozenset([
        3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96,
        112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193,
        195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247,
        248, 249, 251, 252, 253, 254,
    ])
    _K3M_A1 = frozenset([7, 14, 28, 56, 112, 131, 193, 224])
    _K3M_A2 = frozenset([
        7, 14, 15, 28, 30, 56, 60, 112, 120, 131, 135,
        193, 195, 224, 225, 240,
    ])
    _K3M_A3 = frozenset([
        7, 14, 15, 28, 30, 31, 56, 60, 62, 112, 120, 124, 131, 135,
        143, 193, 195, 199, 224, 225, 227, 240, 241, 248,
    ])
    _K3M_A4 = frozenset([
        7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126,
        131, 135, 143, 159, 193, 195, 199, 207, 224, 225, 227, 231,
        240, 241, 243, 248, 249, 252,
    ])
    _K3M_A5 = frozenset([
        7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126,
        131, 135, 143, 159, 191, 193, 195, 199, 207, 224, 225, 227,
        231, 239, 240, 241, 243, 248, 249, 251, 252, 254,
    ])
    _K3M_A1PIX = frozenset([
        3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96,
        112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193,
        195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247,
        248, 249, 251, 252, 253, 254,
    ])
    _K3M_W = np.array([[128, 1, 2], [64, 0, 4], [32, 16, 8]], dtype=np.uint8)

    def _k3m_weight(self, img: np.ndarray, r: int, c: int) -> int:
        return int(np.sum(
            (img[r-1:r+2, c-1:c+2] > 0).astype(np.uint8) * self._K3M_W
        ))

    # ------------------------------------------------------------------ #
    # Metody publiczne                                                    #
    # ------------------------------------------------------------------ #

    def kmm(self, binary: np.ndarray) -> np.ndarray:
        """
        Algorytm KMM (Saeed, Rybnik, Tabędzki, Adamski 2002).

        Każda iteracja:
            Faza A – oznaczenie pikseli brzegowych (etykiety 2 i 3)
            Faza B – usuwanie na podstawie spójności sąsiadów (LUT B)
            Faza C – sekwencyjne ścienienie wagowe rastrowe (LUT C)
        """
        Z   = dict(mode='constant', constant_values=0)
        img = (binary == 0).astype(np.uint8)

        while True:
            prev = img.copy()

            p      = np.pad(img, 1, **Z)
            edge   = ((p[:-2,1:-1]==0)|(p[2:,1:-1]==0)|
                      (p[1:-1,:-2]==0)|(p[1:-1,2:]==0))
            img[(img==1) & edge] = 2
            corner = ((p[:-2,:-2]==0)|(p[:-2,2:]==0)|
                      (p[2:, :-2]==0)|(p[2:, 2:]==0))
            img[(img==1) & corner] = 3

            contour   = (img==2)|(img==3)
            pc        = np.pad(contour.astype(np.uint8), 1, **Z)
            pattern_b = (pc[:-2,:-2]        |
                         pc[:-2,1:-1] * 2   |
                         pc[:-2,2:  ] * 4   |
                         pc[1:-1,:-2] * 8   |
                         pc[1:-1,2: ] * 16  |
                         pc[2:, :-2 ] * 32  |
                         pc[2:, 1:-1] * 64  |
                         pc[2:, 2:  ] * 128).astype(np.uint8)
            max_comp  = self._kmm_lut_b[pattern_b]
            img[contour & (max_comp >= 2) & (max_comp <= 4)] = 0

            H, W = img.shape
            for N in (2, 3):
                for r, c in np.argwhere(img == N):
                    w = 0
                    if r > 0:
                        if c > 0   and img[r-1,c-1]: w += 128
                        if             img[r-1,c  ]: w +=   1
                        if c < W-1 and img[r-1,c+1]: w +=   2
                    if c > 0   and img[r,  c-1]: w +=  64
                    if c < W-1 and img[r,  c+1]: w +=   4
                    if r < H-1:
                        if c > 0   and img[r+1,c-1]: w +=  32
                        if             img[r+1,c  ]: w +=  16
                        if c < W-1 and img[r+1,c+1]: w +=   8
                    img[r, c] = 0 if self._kmm_lut_c[w] else 1

            if np.array_equal(img, prev):
                break

        return np.where(img == 1, np.uint8(0), np.uint8(255))

    def k3m(self, binary: np.ndarray) -> np.ndarray:
        """
        Algorytm K3M (Saeed, Tabędzki, Rybnik, Adamski 2010).

        Każda iteracja:
            Faza 0    – wyznaczenie pikseli brzegowych (waga ∈ A0)
            Fazy 1–5  – usuwanie z rosnącą liczbą sąsiadów (A1–A5)
        Po zbieżności:
            Faza końcowa – ścienienie do 1 piksela (A1pix)
        """
        img        = (binary == 0).astype(np.uint8)
        rows, cols = img.shape
        phases     = [self._K3M_A1, self._K3M_A2, self._K3M_A3,
                      self._K3M_A4, self._K3M_A5]

        while True:
            modified = False
            border = [
                (r, c)
                for r in range(1, rows - 1)
                for c in range(1, cols - 1)
                if img[r, c] == 1 and self._k3m_weight(img, r, c) in self._K3M_A0
            ]
            for phase_lut in phases:
                to_del = [
                    (r, c) for r, c in border
                    if img[r, c] == 1 and self._k3m_weight(img, r, c) in phase_lut
                ]
                if to_del:
                    for r, c in to_del:
                        img[r, c] = 0
                    modified = True
            if not modified:
                break

        changed = True
        while changed:
            changed = False
            to_del  = [
                (r, c)
                for r in range(1, rows - 1)
                for c in range(1, cols - 1)
                if img[r, c] == 1 and self._k3m_weight(img, r, c) in self._K3M_A1PIX
            ]
            if to_del:
                for r, c in to_del:
                    img[r, c] = 0
                changed = True

        return np.where(img == 1, np.uint8(0), np.uint8(255))

    def zhang_suen(self, binary: np.ndarray) -> np.ndarray:
        """
        Algorytm Zhang-Suen (1984).

        Równoległy, dwupodkrokowy.
        Zalecany gdy detekcja bifurkacji jest priorytetem —
        KMM i K3M mają tendencję do rozrywania T-skrzyżowań.
        """
        img = (binary == 0).astype(np.uint8)

        def _step(img: np.ndarray, step: int) -> int:
            to_del = []
            for r, c in zip(*np.where(img == 1)):
                if r == 0 or r == img.shape[0]-1 or c == 0 or c == img.shape[1]-1:
                    continue
                P = [img[r-1,c], img[r-1,c+1], img[r,c+1], img[r+1,c+1],
                     img[r+1,c], img[r+1,c-1], img[r,  c-1], img[r-1,c-1]]
                S = sum(P)
                if not (2 <= S <= 6): continue
                T = sum(1 for i in range(8) if P[i]==0 and P[(i+1)%8]==1)
                if T != 1: continue
                if step == 1:
                    if P[0]*P[2]*P[4] != 0: continue
                    if P[2]*P[4]*P[6] != 0: continue
                else:
                    if P[0]*P[2]*P[6] != 0: continue
                    if P[0]*P[4]*P[6] != 0: continue
                to_del.append((r, c))
            for r, c in to_del:
                img[r, c] = 0
            return len(to_del)

        while True:
            if _step(img, 1) == 0 and _step(img, 2) == 0:
                break
        return np.where(img == 1, np.uint8(0), np.uint8(255))

    def morphological(self, binary: np.ndarray) -> np.ndarray:
        """
        Szkielet morfologiczny (erozja krzyżowa + residua).

        Każdy krok:
            erodowany = erode_cross(img)
            residuum  = img - dilate_cross(erodowany)  → dodawane do szkieletu
            img       = erodowany
        Powtarzane do zaniku obiektu.
        """
        img      = (binary == 0).astype(np.uint8)
        img      = np.pad(img, 1, mode='constant', constant_values=0)
        skeleton = np.zeros_like(img)

        while img.max() > 0:
            eroded   = ImageUtils.erode_cross(img)
            opened   = ImageUtils.dilate_cross(eroded)
            residue  = np.clip(
                img.astype(np.int16) - opened.astype(np.int16), 0, 1
            ).astype(np.uint8)
            skeleton = np.maximum(skeleton, residue)
            img      = eroded

        skeleton = skeleton[1:-1, 1:-1]
        return np.where(skeleton > 0, np.uint8(0), np.uint8(255))