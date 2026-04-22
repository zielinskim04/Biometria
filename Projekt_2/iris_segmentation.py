"""
iris_segmentation.py
--------------------
Segmentacja tęczówki – tylko numpy + PIL (Wersja zoptymalizowana i odchudzona).
Rozwiązanie czysto matematyczne bez użycia OpenCV.
"""

import numpy as np
from PIL import Image

class ImageProcessor:
    """Funkcje bazowe"""

    def _get_structuring_element(self, size: int, shape: str) -> np.ndarray:
        se = np.zeros((size, size), dtype=np.uint8)
        center = size // 2
        if shape == 'ellipse':
            for i in range(size):
                for j in range(size):
                    if ((i - center) ** 2 + (j - center) ** 2) <= center ** 2:
                        se[i, j] = 1
        return se

    def _to_gray(self, image: Image.Image) -> np.ndarray:
        return np.array(image.convert('L'))

    def _erode(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        size = se.shape[0]
        pad = size // 2
        padded = np.pad(img, pad, mode='edge')
        result = np.zeros_like(img)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i + size, j:j + size]
                result[i, j] = np.min(region[se == 1])
        return result

    def _dilate(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        size = se.shape[0]
        pad = size // 2
        padded = np.pad(img, pad, mode='edge')
        result = np.zeros_like(img)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i + size, j:j + size]
                result[i, j] = np.max(region[se == 1])
        return result



# Klasa segmentacji tęczówki
class IrisSegmentation(ImageProcessor):
    """
    Pełna logika segmentacji tęczówki
    """

    # ── 1. Próg P/X  ──────────────────────────────────

    def _mean_brightness(self, gray: np.ndarray) -> float:
        """P = (1/h*w) * sum A(i,j)"""
        h, w = gray.shape
        return float(np.sum(gray.astype(np.float64)) / (h * w))

    def binarize_px(self, image: Image.Image, X: float) -> np.ndarray:
        """
        Binaryzacja z progiem PP = P/X_pupil  lub  PI = P/X_iris
        """
        gray = self._to_gray(image)
        P = self._mean_brightness(gray)
        threshold = P / X
        result = np.zeros_like(gray)
        result[gray < threshold] = 255
        return result

    # ── 2. Morfologia ───────────────────────────────────────────────────────

    def _morph_close(self, img: np.ndarray, size: int, shape: str = 'ellipse') -> np.ndarray:
        se = self._get_structuring_element(size, shape)
        return self._erode(self._dilate(img, se), se)

    def _morph_open(self, img: np.ndarray, size: int, shape: str = 'ellipse') -> np.ndarray:
        se = self._get_structuring_element(size, shape)
        return self._dilate(self._erode(img, se), se)

    # ── 3. Największy spójny obszar (Connected Components) ─────────────────

    def _keep_largest_blob(self, binary: np.ndarray) -> np.ndarray:
        """
        Zachowuje tylko największy biały obszar.
        """
        rows, cols = binary.shape
        visited = np.zeros((rows, cols), dtype=bool)
        labels  = np.zeros((rows, cols), dtype=np.int32)
        label_id = 0
        label_sizes = {}
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for sr in range(rows):
            for sc in range(cols):
                if binary[sr, sc] == 255 and not visited[sr, sc]:
                    label_id += 1
                    queue = [(sr, sc)]
                    visited[sr, sc] = True
                    size = 0
                    while queue:
                        r, c = queue.pop()
                        labels[r, c] = label_id
                        size += 1
                        for dr, dc in neighbors:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < rows and 0 <= nc < cols:
                                if binary[nr, nc] == 255 and not visited[nr, nc]:
                                    visited[nr, nc] = True
                                    queue.append((nr, nc))
                    label_sizes[label_id] = size

        if not label_sizes:
            return binary

        best = max(label_sizes, key=label_sizes.get)
        result = np.zeros_like(binary)
        result[labels == best] = 255
        return result

    # ── 4. Środek i promień źrenicy, projekcje ───────────────────────────

    def _detect_circle_projection(self, binary: np.ndarray) -> tuple:
        proj_rows = binary.sum(axis=1).astype(np.float64)
        proj_cols = binary.sum(axis=0).astype(np.float64)
        # Funkcja pomocnicza do znalezienia środka i promienia dla danej osi
        def get_center_and_radius(proj: np.ndarray) -> tuple:
            # Szukamy miejsc, gdzie wykres ma >= 50% swojej maksymalnej wysokości
            indices = np.where(proj >= proj.max() * 0.5)[0]
            if len(indices) == 0:
                return int(np.argmax(proj)), 5
            # Środek to po prostu punkt w połowie między lewym a prawym brzegiem "górki"
            center = int((indices[0] + indices[-1]) / 2)

            diff = np.diff(proj)
            left_edge  = int(np.argmax(diff[:center])) if center > 0 else 0
            right_edge = int(np.argmin(diff[center:]) + center) if center < len(diff) else len(proj) - 1
            radius = max((right_edge - left_edge) // 2, 5)
            return center, radius
 
        cx, rx = get_center_and_radius(proj_cols)
        cy, ry = get_center_and_radius(proj_rows)
        return cx, cy, (rx + ry) // 2

    # ── 5. Detekcja promienia tęczówki ────────────────────────────────────

    def _detect_iris_radius(self, gray: np.ndarray, cx: int, cy: int, pupil_r: int, X_iris: float) -> int:
        h, w = gray.shape

        # Tworzymy obraz binarny (Tęczówka = 255, Tło = 0)
        P = self._mean_brightness(gray)
        binary = np.zeros_like(gray)
        binary[gray < P / X_iris] = 255

        # Usuwamy obszar źrenicy, żeby nie zakłócał maski
        yy, xx = np.ogrid[:h, :w]
        binary[(xx - cx) ** 2 + (yy - cy) ** 2 <= (pupil_r + 5) ** 2] = 0

        # Operacje morfologiczne - łatamy dziury po odblaskach i czyścimy tło
        binary = self._morph_close(binary, size=9, shape='ellipse')
        binary = self._morph_open(binary, size=5, shape='ellipse')

        # Ray-casting, ale tylko dwa
        angles_deg = [0, 180]  
        radii_found = []

        for deg in angles_deg:
            rad = np.deg2rad(deg)
            max_steps = min(cx, cy, w - cx, h - cy) - 5
            steps = np.arange(0, max_steps)
            
            # Pobieramy współrzędne dla promienia
            xs = np.clip((cx + steps * np.cos(rad)).astype(int), 0, w - 1)
            ys = np.clip((cy + steps * np.sin(rad)).astype(int), 0, h - 1)
            
            profile = binary[ys, xs]
            
            # Strefa ignorowania - odsuwamy się od źrenicy
            ignore_zone = int(pupil_r * 1.6)
            search_zone = profile[ignore_zone:-5]
            
            if len(search_zone) == 0:
                continue

            # Na masce binarnej zewnętrzna krawędź to ostatni biały piksel
            # Funkcja np.where zwraca indeksy wszystkich białych pikseli (255)
            white_pixels = np.where(search_zone == 255)[0]
           
            if len(white_pixels) == 0:
                continue
                
            # Bierzemy ostatni biały piksel i dodajemy strefę ignorowania
            last_white_idx = int(white_pixels[-1]) + ignore_zone
            radii_found.append(last_white_idx)

        if len(radii_found) == 2:
            radius = int(np.mean(radii_found))
        elif len(radii_found) == 1:
            radius = radii_found[0]
        else:
            radius = int(pupil_r * 2.5)

        max_r = min(cx, cy, w - cx, h - cy) - 5
        if radius < int(pupil_r * 1.2) or radius > max_r:
            radius = min(int(pupil_r * 2.5), max_r)
            
        return max(radius, int(pupil_r * 1.2))

    # ── 6. Rozwinięcie → prostokąt (Wektoryzacja + Interpolacja) ────────

    def unwrap_iris(self, img_array: np.ndarray, 
                    cx: int, cy: int, r_inner: int, 
                    r_outer: int, radial_res: int = 64, 
                    angular_res: int = 360) -> np.ndarray:
        """
        Zamiana biegunowych na kartezjańskie. Obsługuje zarówno szarość (2D) jak i kolor (3D RGB)
        """
        h, w = img_array.shape[:2]
        angles = np.linspace(0, 2 * np.pi, angular_res, endpoint=False)
        radii  = np.linspace(r_inner, r_outer, radial_res)

        # Wykrywanie czy obraz ma kolory
        if img_array.ndim == 3:
            unwrapped = np.zeros((radial_res, angular_res, img_array.shape[2]), dtype=np.uint8)
        else:
            unwrapped = np.zeros((radial_res, angular_res), dtype=np.uint8)

        for i, r in enumerate(radii):
            xs = np.clip((cx + r * np.cos(angles)).astype(int), 0, w - 1)
            ys = np.clip((cy + r * np.sin(angles)).astype(int), 0, h - 1)
            unwrapped[i, ...] = img_array[ys, xs]

        return unwrapped

    # ── 7. Rysowanie okręgu  ──────────────────────────────

    def _draw_circle(self, arr: np.ndarray, 
                     cx: int, cy: int, r: int, 
                     color: tuple, thickness: int = 2) -> np.ndarray:
        """
        Wyznacza okręgi, reprezentujące granice tęczówki i źrenicy.
        """
        result = arr.copy()
        rows, cols = result.shape[:2]
        for t in range(thickness):
            ri = r - t
            if ri <= 0: break
            angles = np.linspace(0, 2 * np.pi, max(8 * ri, 360), endpoint=False)
            xs = np.clip((cx + ri * np.cos(angles)).astype(int), 0, cols - 1)
            ys = np.clip((cy + ri * np.sin(angles)).astype(int), 0, rows - 1)
            result[ys, xs] = color
        return result

    # ── 8. Główna funkcja ─────────────────────────────────────────────────

    def segment(self, image: Image.Image,
                X_pupil: float = 1.5,
                X_iris:  float = 1.8,
                close_size_pupil: int = 15,
                open_size_pupil:  int = 7,
                radial_res:  int = 64,
                angular_res: int = 360,
                verbose: bool = True) -> dict:
        
        gray = self._to_gray(image)

        # ── Źrenica ───────────────────────────────────────────────────────
        bin_pupil  = self.binarize_px(image, X_pupil) 
        bin_closed = self._morph_close(bin_pupil, close_size_pupil, 'ellipse')
        bin_opened = self._morph_open(bin_closed, open_size_pupil,  'ellipse')
        bin_clean  = self._keep_largest_blob(bin_opened)

        cx, cy, pupil_r = self._detect_circle_projection(bin_clean)

        # ── Tęczówka ──────────────────────────────────────────────────────
        iris_r = self._detect_iris_radius(gray, cx, cy, pupil_r, X_iris)
        
        h, w = gray.shape
        yy, xx = np.ogrid[:h, :w]
        dist2 = (xx - cx) ** 2 + (yy - cy) ** 2
        iris_mask = np.zeros_like(gray)
        iris_mask[(dist2 <= iris_r ** 2) & (dist2 >= pupil_r ** 2)] = 255

        color_array = np.array(image.convert('RGB'))
        unwrapped = self.unwrap_iris(color_array, cx, cy, pupil_r, iris_r, radial_res, angular_res)

        if verbose:
            print(f"[INFO] Środek:  ({cx}, {cy})")
            print(f"[INFO] Źrenica: r = {pupil_r} px")
            print(f"[INFO] Tęczówka: r = {iris_r} px")

        return dict(
            gray=gray,
            binary_pupil=bin_pupil,
            binary_pupil_clean=bin_clean,
            iris_mask=iris_mask,
            cx=cx, cy=cy,
            pupil_r=pupil_r,
            iris_r=iris_r,
            unwrapped=unwrapped,
        )

    # ── 9. Obraz wynikowy z okręgami ──────────────────────────────────────
    def draw_result(self, image: Image.Image, result: dict) -> Image.Image:
        arr = np.array(image.convert('RGB'))
        cx, cy = result['cx'], result['cy']
        arr = self._draw_circle(arr, cx, cy, result['pupil_r'], (255, 0,   0), 2)
        arr = self._draw_circle(arr, cx, cy, result['iris_r'],  (0,   200, 0), 2)
        # punkt środka 5×5
        r0, r1 = max(0, cy - 2), min(arr.shape[0], cy + 3)
        c0, c1 = max(0, cx - 2), min(arr.shape[1], cx + 3)
        arr[r0:r1, c0:c1] = (255, 255, 0)
        return Image.fromarray(arr)


# Klasa do zakodowania tęczówki przy pomocy falki Gabora
class IrisEncoder:

    def __init__(self):
        self.num_points = 128

    def get_gaussian_window(self, size: int) -> np.ndarray:
        # Zwraca jednowymiarowe okno Gaussa do uśredniania w kierunku radialnym
        x = np.arange(size) - size // 2
        sigma = max(size / 3.0, 1.0)
        g = np.exp(-(x ** 2) / (2 * sigma ** 2))
        return g / g.sum()
    
    def get_gabor_filter(self, length: int, f: float) -> np.ndarray:
        # Filtr Gabora na podstawie książki
        sigma = 0.5 * np.pi * f
        # x = np.linspace(-length // 2, length // 2, length)
        # tutaj nie rozumiem jakie wartosci dac zeby dzialalo
        x = np.linspace(-np.pi, np.pi, length)
        gaussian = np.exp(-(x**2) / (sigma ** 2))
        wave = np.exp(-1j * 2 * np.pi * f * x)
        return gaussian * wave
    
    def extract_and_average_band(self, rectangle: np.ndarray, start_row: int, end_row: int, valid_cols: np.ndarray) -> np.ndarray:
        # Wycina pas, wybiera dozwolone kąty, uśrednia radialnie

        # Wycina odpowiednie wiersze i kolumny (kąty)
        band_pixels = rectangle[start_row:end_row, valid_cols]

        # Uśrednienie radialne (os Y) przy pomocy okna gaussa
        height = end_row - start_row
        g_window = self.get_gaussian_window(height)

        averaged = np.sum(band_pixels * g_window[:, None], axis=0) 
        # g_window[:, None] zmienia płaską tablicę okna Gaussa w pionową kolumnę, mnożymy pas przez wagi i sumujemy z góry do dołu do 1d

        # Wybór 128 punktow
        old_x = np.linspace(0, 1, len(averaged))
        new_x = np.linspace(0, 1, self.num_points)
        resampled = np.interp(new_x, old_x, averaged) # interpolacja liniowa, żeby mieć tyle samo punktów dla każdego paska

        return resampled
    
    def encode(self, rectangle: np.ndarray, f_gabor: float) -> np.ndarray:
        # Upewniamy się, że obraz jest w odcieniach szarości
        if rectangle.ndim == 3:
            rectangle = np.dot(rectangle[..., :3], [0.2989, 0.5870, 0.1140])
        else:
            rectangle = rectangle.astype(float)

        rows, cols = rectangle.shape
        # Zakładamy, że obraz ma 360 kolumn (każda to 1 stopień) oraz 64 wiersze
        band_height = rows // 8

        # Definiujemy dozwolone kąty (kolumny) dla 3 grup pasów: (zgodnie z książką)
        # Pasy 1-4 (wewnętrzne): omijamy [255, 285]
        cols_1_4 = np.concatenate([np.arange(0, 255), np.arange(285, 360)])
        
        # Pasy 5-6 (środkowe): omijamy po 67 stopni u góry i u dołu
        cols_5_6 = np.concatenate([np.arange(0, 57), np.arange(124, 237), np.arange(304, 360)])
        
        # Pasy 7-8 (zewnętrzne): zostawiamy tylko "czyste boki" (po 90 stopni z każdej strony)
        cols_7_8 = np.concatenate([np.arange(0, 45), np.arange(135, 225), np.arange(315, 360)])

        iris_code = np.zeros((8, self.num_points * 2), dtype=np.uint8)
        
        gabor_filter = self.get_gabor_filter(length=35, f=f_gabor)

        for band_idx in range(8):
            start_row = band_idx * band_height
            end_row = start_row + band_height

            if band_idx < 4:     # Pasy 0, 1, 2, 3 (czyli 1-4)
                valid_cols = cols_1_4
            elif band_idx < 6:   # Pasy 4, 5 (czyli 5-6)
                valid_cols = cols_5_6
            else:                # Pasy 6, 7 (czyli 7-8)
                valid_cols = cols_7_8

            signal_1d = self.extract_and_average_band(rectangle, start_row, end_row, valid_cols)

            # Splot sygnału z filtrem Gabora (wynik to liczby zespolone)
            # mode='same' zachowuje długość 128 punktów
            response = np.convolve(signal_1d, gabor_filter, mode='same')

            # Kwantyzacja fazy (demodulacja 2-bitowa)
            for i in range(self.num_points):
                re = np.real(response[i])
                im = np.imag(response[i])
                
                # Pierwszy bit = 1 jeśli Re > 0, w przeciwnym razie 0
                bit1 = 1 if re > 0 else 0
                # Drugi bit = 1 jeśli Im > 0, w przeciwnym razie 0
                bit2 = 1 if im > 0 else 0
                
                # Zapisujemy w macierzy (każdy punkt zajmuje 2 pozycje w kolumnie)
                iris_code[band_idx, 2 * i] = bit1
                iris_code[band_idx, 2 * i + 1] = bit2

        return iris_code
    
    def draw_code(self, iris_code: np.ndarray, scale_factor: int = 10) -> Image.Image:
        # 1. Sprawdzamy, czy kod ma dobry kształt (np. 8x256)
        if iris_code.ndim != 2 or iris_code.shape[0] != 8:
            raise ValueError(f"Oczekiwano kodu o kształcie (8, X), a otrzymano {iris_code.shape}")

        # 2. Zamieniamy zera i jedynki na odcienie szarości (uint8)
        # 0 -> 0 (czarny), 1 -> 255 (biały)
        image_data = (iris_code * 255).astype(np.uint8)

        # 3. Tworzymy mały, binarny obrazek z macierzy PIL
        small_image = Image.fromarray(image_data, mode='L') # mode 'L' to 8-bitowa szarość

        # 4. Skalujemy go, aby był widoczny na ekranie (np. 10x powiększenie)
        # Używamy Image.NEAREST, aby zachować ostre krawędzie "pikseli" kodu (nie chcemy rozmycia)
        width, height = small_image.size
        new_size = (width * scale_factor, height * scale_factor)
        drawn_code = small_image.resize(new_size, Image.NEAREST)

        return drawn_code

    def calculate_hamming_distance(self, code1: np.ndarray, code2: np.ndarray) -> float:
        # Zwraca ułamek różniących się bitów między kodami
        if code1.shape != code2.shape:
            raise ValueError("Kody muszą mieć ten sam wymiar!")
        
        mismatches = np.sum(code1 != code2)
        total_bits = code1.size
        
        return mismatches / total_bits