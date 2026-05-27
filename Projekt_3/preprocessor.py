import numpy as np
from collections import deque
from scipy import ndimage
from PIL import Image

from image_utils import ImageUtils

class FingerprintPreprocessor:
    """
    Pełny potok przetwarzania wstępnego odcisku palca.

    Kroki:
        1. normalize      – normalizacja kontrastu (Hong et al. / Cuevas)
        2. clahe          – lokalny CLAHE poprawiający kontrast przed Gaborem
        3. segment        – blokowa maska ROI (odchylenie std)
        4. gabor_enhance  – bank filtrów Gabora z mapą orientacji
        5. binarize       – próg Otsu (metoda Otsu / global_threshold)
        6. run            – pełny potok w jednym wywołaniu
    """

    # ------------------------------------------------------------------ #
    # 1. Normalizacja kontrastu                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def normalize(img: np.ndarray, m0: float = 100.0, v0: float = 100.0) -> np.ndarray:
        """
        Normalizacja kontrastu do zadanej średniej m0 i wariancji v0.
        Wzór: Hong et al. 1998 / Handbook of Fingerprint Recognition s. 148.
        """
        img = img.astype(np.float32)
        m   = np.mean(img)
        v   = np.var(img)
        h, w = img.shape
        out  = np.zeros((h, w), dtype=np.float32)
        for y in range(h):
            for x in range(w):
                diff = img[y, x] - m
                if diff >= 0:
                    out[y, x] = m0 + np.sqrt(v0 * diff ** 2 / (v + 1e-8))
                else:
                    out[y, x] = m0 - np.sqrt(v0 * diff ** 2 / (v + 1e-8))
        return np.clip(out, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------ #
    # 2. CLAHE                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def clahe(img: np.ndarray,
              clip_limit: float = 3.0,
              tile_size:  int   = 16) -> np.ndarray:
        """
        Contrast Limited Adaptive Histogram Equalization (tylko numpy).

        Rozszerza lokalny kontrast przed filtrem Gabora — kluczowe gdy
        rozkład odpowiedzi Gabora jest zbyt wąski (typowe dla dobrych skanerów).
        """
        H, W = img.shape
        out  = np.zeros_like(img, dtype=np.float64)
        for r in range(0, H, tile_size):
            for c in range(0, W, tile_size):
                tile  = img[r:r + tile_size, c:c + tile_size].astype(float)
                hist, _ = np.histogram(tile.ravel(), bins=256, range=(0, 255))
                clip    = int(clip_limit * tile.size / 256)
                excess  = np.maximum(hist - clip, 0).sum()
                hist    = np.minimum(hist, clip)
                hist   += excess // 256
                cdf     = np.cumsum(hist)
                cdf     = (cdf - cdf.min()) / (cdf.max() - cdf.min() + 1e-8) * 255
                lut     = cdf.astype(np.uint8)
                out[r:r + tile_size, c:c + tile_size] = lut[tile.astype(np.uint8)]
        return out.astype(np.uint8)

    # ------------------------------------------------------------------ #
    # 3. Segmentacja (maska ROI)                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _keep_largest_component(mask: np.ndarray) -> np.ndarray:
        """Zostawia tylko największy spójny obszar (finger ROI)."""
        h, w     = mask.shape
        visited  = np.zeros_like(mask)
        comps    = []

        def bfs(sy, sx):
            q    = deque([(sy, sx)])
            comp = []
            while q:
                y, x = q.popleft()
                if not (0 <= y < h and 0 <= x < w): continue
                if visited[y, x] or mask[y, x] == 0: continue
                visited[y, x] = 1
                comp.append((y, x))
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    q.append((y+dy, x+dx))
            return comp

        for y in range(h):
            for x in range(w):
                if mask[y, x] == 1 and not visited[y, x]:
                    comps.append(bfs(y, x))

        if not comps:
            return mask
        clean = np.zeros_like(mask)
        for y, x in max(comps, key=len):
            clean[y, x] = 1
        return clean

    @staticmethod
    def _fill_holes(mask: np.ndarray) -> np.ndarray:
        """Wypełnia dziury wewnątrz obszaru ROI metodą flood-fill z krawędzi."""
        h, w    = mask.shape
        visited = np.zeros_like(mask, dtype=np.uint8)
        q       = deque()
        for x in range(w):
            q.append((0, x)); q.append((h-1, x))
        for y in range(h):
            q.append((y, 0)); q.append((y, w-1))
        while q:
            y, x = q.popleft()
            if not (0 <= y < h and 0 <= x < w): continue
            if visited[y, x] or mask[y, x] == 1: continue
            visited[y, x] = 1
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                q.append((y+dy, x+dx))
        filled = mask.copy()
        filled[(mask == 0) & (visited == 0)] = 1
        return filled

    @staticmethod
    def _add_margin(mask: np.ndarray, margin: int = 8) -> np.ndarray:
        """Powiększa maskę ROI o podany margines (dylatacja prostokątna)."""
        h, w     = mask.shape
        expanded = mask.copy()
        for y in range(h):
            for x in range(w):
                if mask[y, x] == 1:
                    y0 = max(0, y - margin); y1 = min(h, y + margin + 1)
                    x0 = max(0, x - margin); x1 = min(w, x + margin + 1)
                    expanded[y0:y1, x0:x1] = 1
        return expanded

    def segment(self, img: np.ndarray,
                block_size: int   = 4,
                t_factor:   float = 0.2,
                margin:     int   = 8) -> np.ndarray:
        """
        Blokowa maska ROI na podstawie lokalnego odchylenia standardowego.

        Bloki o std > t_factor * std_globalny → ROI.
        Po binaryzacji: keep_largest_component → fill_holes → add_margin.

        Zwraca ndarray uint8 (0/1).
        """
        img   = img.astype(np.float32)
        h, w  = img.shape
        mask  = np.zeros((h, w), dtype=np.uint8)
        thresh = t_factor * np.std(img)

        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                block = img[y:y + block_size, x:x + block_size]
                if block.size == 0: continue
                if np.std(block) > thresh:
                    mask[y:y + block_size, x:x + block_size] = 1

        mask = self._keep_largest_component(mask)
        mask = self._fill_holes(mask)
        mask = self._add_margin(mask, margin=margin)
        return mask

    # ------------------------------------------------------------------ #
    # 4. Wzmocnienie Gaborem                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _orientation_map(img: np.ndarray, block_size: int = 16) -> np.ndarray:
        """Blokowa mapa orientacji grzbietów (Hong et al. 1998)."""
        kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        ky = np.array([[-1,-2,-1], [ 0, 0, 0], [ 1, 2, 1]], dtype=np.float32)
        gx = ndimage.convolve(img.astype(np.float32), kx, mode='nearest')
        gy = ndimage.convolve(img.astype(np.float32), ky, mode='nearest')
        h, w = img.shape
        ori  = np.zeros((h, w), dtype=np.float32)
        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                bx = gx[y:y + block_size, x:x + block_size]
                by = gy[y:y + block_size, x:x + block_size]
                if bx.size == 0: continue
                vx = np.sum(2 * bx * by)
                vy = np.sum(bx**2 - by**2)
                ori[y:y + block_size, x:x + block_size] = 0.5 * np.arctan2(vx, vy)
        return ori

    @staticmethod
    def _gabor_kernel(size: int, sigma: float,
                      theta: float, lambd: float) -> np.ndarray:
        """Jądro Gabora (Gauss × cosinus) dla orientacji theta."""
        half  = size // 2
        y, x  = np.mgrid[-half:half+1, -half:half+1]
        xr    =  x * np.cos(theta) + y * np.sin(theta)
        yr    = -x * np.sin(theta) + y * np.cos(theta)
        gb    = (np.exp(-0.5 * (xr**2 + yr**2) / sigma**2)
                 * np.cos(2 * np.pi * xr / lambd))
        return (gb - gb.mean()).astype(np.float32)

    def gabor_enhance(self, img: np.ndarray,
                      freq:       float = 0.1,
                      sigma:      float = 3.0,
                      n_angles:   int   = 16,
                      block_size: int   = 16) -> np.ndarray:
        """
        Wzmocnienie grzbietów bankiem filtrów Gabora z mapą orientacji.

        Zwraca uint8 ndarray w [0, 255]; jasne = grzbiecie.
        """
        img   = img.astype(np.float32)
        lambd = 1.0 / freq
        size  = int(sigma * 3)
        if size % 2 == 0: size += 1

        ori   = self._orientation_map(img, block_size)
        bank  = []
        for i in range(n_angles):
            angle = i * np.pi / n_angles
            bank.append(self._gabor_kernel(size, sigma, angle + np.pi / 2, lambd))

        responses  = [ndimage.convolve(img, k, mode='nearest') for k in bank]
        angle_idx  = ((ori + np.pi / 2) / np.pi * n_angles).astype(int) % n_angles
        out        = np.zeros_like(img)
        for i in range(n_angles):
            out[angle_idx == i] = responses[i][angle_idx == i]

        out = (out - out.min()) / (out.max() - out.min() + 1e-5) * 255
        return out.astype(np.uint8)

    # ------------------------------------------------------------------ #
    # 5. Binaryzacja (Otsu)                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def binarize(img: np.ndarray) -> np.ndarray:
        """
        Progowanie metodą Otsu (maksymalizacja wariancji międzyklasowej).

        Zwraca uint8 ndarray: 0 = grzbiet, 255 = tło.
        """
        hist, _ = np.histogram(img, bins=256, range=(0, 256))
        total   = img.size
        best_t  = 0
        best_v  = -1
        s_total = np.dot(np.arange(256), hist)
        s_back  = 0
        w_back  = 0

        for i in range(256):
            w_back += hist[i]
            if w_back == 0: continue
            w_fore = total - w_back
            if w_fore == 0: break
            s_back    += i * hist[i]
            m_back     = s_back / w_back
            m_fore     = (s_total - s_back) / w_fore
            var_between = w_back * w_fore * (m_back - m_fore) ** 2
            if var_between > best_v:
                best_v = var_between
                best_t = i

        out = np.zeros_like(img, dtype=np.uint8)
        # Jasny piksel (grzbiet po Gabor) → 0 (czarny)
        out[img <  best_t] = 255
        out[img >= best_t] = 0
        return out

    # ------------------------------------------------------------------ #
    # 6. Pełny potok                                                      #
    # ------------------------------------------------------------------ #

    def run(self,
            image:        Image.Image,
            m0:           float = 100.0,
            v0:           float = 100.0,
            clahe_clip:   float = 3.0,
            clahe_tile:   int   = 16,
            seg_block:    int   = 4,
            seg_t_factor: float = 0.2,
            seg_margin:   int   = 8,
            gabor_freq:   float = 0.1,
            gabor_sigma:  float = 3.0,
            gabor_angles: int   = 16) -> dict:
        """
        Pełny potok przetwarzania wstępnego.

        Kroki: PIL → szarość → normalize → CLAHE → segment → Gabor → Otsu → ROI.

        Zwraca słownik:
            'gray'       : uint8 ndarray – obraz w skali szarości
            'normalized' : uint8 ndarray – po normalizacji
            'clahe'      : uint8 ndarray – po CLAHE
            'mask'       : uint8 ndarray – maska ROI (0/1)
            'enhanced'   : uint8 ndarray – po Gaborze
            'binary'     : uint8 ndarray – 0 = grzbiet, 255 = tło
        """
        gray   = ImageUtils.to_gray_pil(image)

        # Segmentacja na surowym gray — przed CLAHE/normalize,
        # bo CLAHE wzmacnia kontrast też w tle i maska staje się za duża.
        mask   = self.segment(gray, block_size=seg_block,
                              t_factor=seg_t_factor, margin=seg_margin)

        norm   = self.normalize(gray, m0=m0, v0=v0)
        clahe_ = self.clahe(norm, clip_limit=clahe_clip, tile_size=clahe_tile)

        # Gabor na pełnym CLAHE — nie maskujemy przed Gaborem,
        # bo ostry brzeg maski byłby wykrywany przez Gabor jako grzbiet.
        enh    = self.gabor_enhance(clahe_, freq=gabor_freq,
                                    sigma=gabor_sigma, n_angles=gabor_angles)
        binary = self.binarize(enh)
        binary[mask == 0] = 255   # maska nakładana dopiero na wynik binarny

        return {
            'gray':       gray,
            'normalized': norm,
            'clahe':      clahe_,
            'mask':       mask,
            'enhanced':   enh,
            'binary':     binary,
        }
