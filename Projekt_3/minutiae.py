import numpy as np
from image_utils import ImageUtils


class MinutiaeExtractor:
    """
    Detekcja i wizualizacja minucji metodą liczby skrzyżowań (CN).

    CN = 1  → zakończenie grzbietu (ridge ending)
    CN = 3  → bifurkacja           (ridge bifurcation)

    Dodatkowy warunek dla zakończeń:  suma sąsiadów == 1
    Dodatkowy warunek dla bifurkacji: suma sąsiadów >= 3
    """

    @staticmethod
    def _crossing_number(neighbors: list) -> float:
        """CN = ½ · Σ|P_k − P_{k+1}| (k cykliczne po 8 sąsiadach)."""
        cn = 0
        for i in range(8):
            cn += abs(int(neighbors[i]) - int(neighbors[(i+1) % 8]))
        return cn / 2

    def detect(self,
               skeleton: np.ndarray,
               mask:     np.ndarray,
               erosions: int = 15) -> tuple:
        """
        Wykrywa minucje na obrazie szkieletu.

        Parametry
        ----------
        skeleton : uint8 ndarray – 0 = piksel szkieletu, 255 = tło.
        mask     : uint8 ndarray – maska ROI (0/1); brzeg maski jest erodowany
                   `erosions` razy, żeby wyeliminować fałszywe minucje przy krawędziach.
        erosions : liczba iteracji erozji maski przed detekcją.

        Zwraca
        ------
        endings       : lista krotek (r, c)
        bifurcations  : lista krotek (r, c)
        """
        skeleton = (skeleton > 0).astype(np.uint8)

        # Erozja maski – odsuwa detekcję od krawędzi ROI
        eroded_mask = mask.copy()
        for _ in range(erosions):
            eroded_mask = ImageUtils.erode(eroded_mask)

        rows, cols   = skeleton.shape
        endings      = []
        bifurcations = []

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if skeleton[r, c] != 1: continue
                if eroded_mask[r, c] == 0: continue

                neighbors = [
                    skeleton[r-1, c],   skeleton[r-1, c+1],
                    skeleton[r,   c+1], skeleton[r+1, c+1],
                    skeleton[r+1, c],   skeleton[r+1, c-1],
                    skeleton[r,   c-1], skeleton[r-1, c-1],
                ]
                cn  = self._crossing_number(neighbors)
                nbr = sum(neighbors)

                if abs(cn - 1) < 0.1 and nbr == 1:
                    endings.append((r, c))
                elif abs(cn - 3) < 0.1 and nbr >= 3:
                    bifurcations.append((r, c))

        return endings, bifurcations

    def draw(self,
             skeleton:     np.ndarray,
             endings:      list,
             bifurcations: list,
             radius:       int = 3) -> np.ndarray:
        """
        Rysuje minucje na kopii szkieletu jako obraz RGB.

        Zakończenia  → czerwone kółka (255, 0, 0)
        Bifurkacje   → niebieskie kółka (0, 0, 255)

        Zwraca uint8 ndarray (H, W, 3).
        """
        # Czarny szkielet na białym tle → RGB
        base = (255 - (skeleton > 0).astype(np.uint8) * 255).astype(np.uint8)
        rgb  = np.stack([base, base, base], axis=-1).copy()

        H, W = skeleton.shape
        Y, X = np.ogrid[:H, :W]

        def _circle(r, c, rad):
            return (Y - r) ** 2 + (X - c) ** 2 <= rad ** 2

        for r, c in endings:
            rgb[_circle(r, c, radius)] = [255, 0, 0]

        for r, c in bifurcations:
            rgb[_circle(r, c, radius)] = [0, 0, 255]

        return rgb.astype(np.uint8)
