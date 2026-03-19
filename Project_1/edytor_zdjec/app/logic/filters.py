from PIL import Image
import numpy as np

class Filters:

    # Filtry
    def convert_to_gray_avg(self, image: Image.Image) -> Image.Image:
        img = np.array(image)
        rows, cols = img.shape[:2]
        gray = np.zeros((rows, cols), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                gray[i,j] = (int(img[i,j,0]) + int(img[i,j,1]) + int(img[i,j,2])) // 3
        return Image.fromarray(gray).convert("RGB")

    def convert_to_gray_human(self, image: Image.Image) -> Image.Image:
        img = np.array(image)
        rows, cols = img.shape[:2]
        gray = np.zeros((rows, cols), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                gray[i,j] = int(img[i,j,0]*0.2126 + img[i,j,1]*0.7152 + img[i,j,2]*0.0722)
        return Image.fromarray(gray).convert("RGB")
    
    def negative(self, image: Image.Image) -> Image.Image:
        img = np.array(image)
        rows, cols = img.shape[:2]
        neg = np.zeros_like(img)
        for i in range(rows):
            for j in range(cols):
                neg[i,j,0] = 255 - img[i,j,0]
                neg[i,j,1] = 255 - img[i,j,1]
                neg[i,j,2] = 255 - img[i,j,2]
        return Image.fromarray(neg).convert("RGB")

    def binarize(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        img = np.array(self.convert_to_gray_avg(image)) 
        rows, cols = img.shape[:2]
        result = np.zeros((rows, cols), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                result[i,j] = 255 if img[i,j,0] > threshold else 0
        return Image.fromarray(result).convert("RGB")

    def brightness(self, image: Image.Image, factor: float) -> Image.Image:
        """factor: 0.0 = czarny, 1.0 = bez zmian, 2.0 = 2x jaśniej"""
        img = np.array(image).astype('float32') 
        result = np.clip(img * factor, 0, 255).astype('uint8')
        return Image.fromarray(result)

    def contrast(self, image: Image.Image, factor: float) -> Image.Image:
        """factor: 0.0 = szary, 1.0 = bez zmian, 2.0 = 2x więcej kontrastu"""
        img = np.array(image).astype('float32')
        result = np.clip((img - 128) * factor + 128, 0, 255).astype('uint8')
        return Image.fromarray(result)

    def average_filter(self, image: Image.Image, size: int=3) -> Image.Image:
        """Filtr uśredniający, gdzie wielkość kernela jest wybierana"""
        img = np.array(image).astype('float32')
        pad = size // 2
        result = np.zeros_like(img)
        padded = np.pad(img, ((pad,pad),(pad,pad),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                result[i,j] = np.mean(padded[i:i+size, j:j+size], axis=(0,1))
        return Image.fromarray(result.astype('uint8'))
    

    def gaussian_filter(self, image: Image.Image, size: int=3, sigma: float=1.0) -> Image.Image:
        """Filtr Gaussa, gdzie wielkość kernela jest wybierana"""
        kernel = np.zeros((size, size))
        center = size // 2
        for x in range(size):
            for y in range(size):
                kernel[x,y] = np.exp(-((x-center)**2 + (y-center)**2) / (2*sigma**2))
        kernel /= kernel.sum()  

        img = np.array(image).astype('float32')
        pad = size // 2
        result = np.zeros_like(img)
        padded = np.pad(img, ((pad,pad),(pad,pad),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for c in range(3):
                    result[i,j,c] = np.sum(padded[i:i+size, j:j+size, c] * kernel)
        return Image.fromarray(result.astype('uint8'))
    
    def sharpen_filter(self, image: Image.Image, preset: str="mean_removal") -> Image.Image:
        """Na podstawie: http://www.algorytm.org/przetwarzanie-obrazow/filtrowanie-obrazow.html"""
        kernels = {
            "mean_removal": np.array([[ -1, -1,  -1],
                            [-1,  9, -1],
                            [ -1, -1,  -1]], dtype='float32'),
            "HP1": np.array([[ 0, -1,  0],
                            [-1,  5, -1],
                            [ 0, -1,  0]], dtype='float32'),
            "HP2": np.array([[1, -2, 1],
                            [-2,  5, -2],
                            [1, -2, 1]], dtype='float32'),
            "HP3": np.array([[ 0, -1,  0],
                            [-1,  20, -1],
                            [ 0, -1,  0]], dtype='float32'),
        }
        kernel = kernels.get(preset, kernels["mean_removal"])
        img = np.array(image).astype('float32')
        result = np.zeros_like(img)
        padded = np.pad(img, ((1,1),(1,1),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for c in range(3):
                    result[i,j,c] = np.sum(padded[i:i+3, j:j+3, c] * kernel)
        return Image.fromarray(np.clip(result, 0, 255).astype('uint8'))
    
    def roberts_cross(self, image: Image.Image) -> Image.Image:
        img_gray = np.array(self.convert_to_gray_avg(image)) 
        img = img_gray[:, :, 0].astype('float32') # tu wyciagam tylko 1 kanal skoro wszystkie sa takie same, tak samo mozna chyba w sharpen filter i jeden for mniej
        rows, cols = img.shape
        result = np.zeros((rows, cols), dtype='float32')
        padded = np.pad(img, ((0,1), (0,1)), mode='edge')
        kernel_x = np.array([[1, 0], [0, -1]], dtype='float32')
        kernel_y = np.array([[0, 1], [-1, 0]], dtype='float32')
        for i in range(rows):
            for j in range(cols):
                region = padded[i:i+2, j:j+2]
                gx = np.sum(region * kernel_x)
                gy = np.sum(region * kernel_y)
                result[i,j] = np.sqrt(gx**2 + gy**2)
                # lub 2 wersja szybsza - na prezentacji u niego bylo
                # abs(gx) + abs(gy)
        result = np.clip(result, 0, 255)
        return Image.fromarray(result.astype('uint8')).convert("RGB")
    
    def prewitt_operator(self, image: Image.Image) -> Image.Image:
        img_gray = np.array(self.convert_to_gray_avg(image))
        img = img_gray[:, :, 0].astype('float32')
        rows, cols = img.shape
        result = np.zeros((rows, cols), dtype='float32')
        padded = np.pad(img, ((1, 1), (1, 1)), mode='edge')
        masks = [
            np.array([[ 1,  1,  1], [ 0,  0,  0], [-1, -1, -1]]),
            np.array([[ 0,  1,  1], [-1,  0,  1], [-1, -1,  0]]), 
            np.array([[-1,  0,  1], [-1,  0,  1], [-1,  0,  1]]), 
            np.array([[-1, -1,  0], [-1,  0,  1], [ 0,  1,  1]]), 
            np.array([[-1, -1, -1], [ 0,  0,  0], [ 1,  1,  1]]),
            np.array([[ 0, -1, -1], [ 1,  0, -1], [ 1,  1,  0]]), 
            np.array([[ 1,  0, -1], [ 1,  0, -1], [ 1,  0, -1]]), 
            np.array([[ 1,  1,  0], [ 1,  0, -1], [ 0, -1, -1]]) 
        ]

        for i in range(rows):
            for j in range(cols):
                region = padded[i:i+3, j:j+3]
                max_val = 0
                for m in masks:
                    val = np.abs(np.sum(region * m))
                    if val > max_val:
                        max_val = val
                result[i, j] = max_val

        result = np.clip(result, 0, 255).astype('uint8')
        return Image.fromarray(result, mode='L').convert("RGB")
    

    def sobel_operator(self, image: Image.Image) -> Image.Image:
        # tutaj tez nie wiem czy nie trzeba sprawdzac 8 masek
        img_gray = np.array(self.convert_to_gray_avg(image))
        img = img_gray[:, :, 0].astype('float32')
        rows, cols = img.shape
        result = np.zeros((rows, cols), dtype='float32')
        padded = np.pad(img, ((1, 1), (1, 1)), mode='edge')
        
        kernel_x = np.array([[ -1,  0,  1], [ -2,  0,  2], [-1, 0, 1]])
        kernel_y = np.array([[ -1,  -2,  -1], [0,  0,  0], [1, 2,  1]]) 

        for i in range(rows):
            for j in range(cols):
                region = padded[i:i+3, j:j+3]
                gx = np.sum(region * kernel_x)
                gy = np.sum(region * kernel_y)
                result[i,j] = np.sqrt(gx**2 + gy**2)

        result = np.clip(result, 0, 255).astype('uint8')
        return Image.fromarray(result, mode='L').convert("RGB")

    def custom_filter(self, image: Image.Image, kernel: np.ndarray) -> Image.Image:
        size = kernel.shape[0]
        pad = size // 2
        img = np.array(image).astype('float32')
        result = np.zeros_like(img)

        # Dla parzystych rozmiarów
        pad_before = size // 2
        pad_after  = size - pad_before - 1

        padded = np.pad(img,
                        ((pad_before, pad_after),
                        (pad_before, pad_after),
                        (0, 0)),
                        mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for c in range(3):
                    result[i,j,c] = np.sum(padded[i:i+size, j:j+size, c] * kernel)
        return Image.fromarray(np.clip(result, 0, 255).astype('uint8'))
    

    # ── Operacje morfologiczne ────────────────────────────────────────────

    def _get_structuring_element(self, size: int, shape: str) -> np.ndarray:
        """
        Generuje element strukturyzujący.
        shape: 'rect' | 'cross' | 'ellipse' |'horizontal' | 'vertical'

        Na podstawie https://echoslayer.github.io/Digital-Image-Processing/Books/%E6%95%B8%E4%BD%8D%E5%BD%B1%E5%83%8F%E8%99%95%E7%90%86/PDF/Rafael-C.-Gonzalez,-Richard-E.-Woods---Digital-Image-Processing-Pearson-(2007).
        
        Rozdzial 9
        """
        se = np.zeros((size, size), dtype=np.uint8)
        center = size // 2

        if shape == 'rect':
            se[:] = 1

        elif shape == 'cross':
            se[center, :] = 1
            se[:, center] = 1

        elif shape == 'ellipse':
            for i in range(size):
                for j in range(size):
                    # równanie elipsy
                    if ((i - center)**2 + (j - center)**2) <= center**2:
                        se[i, j] = 1

        
        elif shape == 'horizontal':
            se[center, :] = 1      

        elif shape == 'vertical':
            se[:, center] = 1    
    
        return se

    # W przeciwieństwie do istniejącyh już fukcji poszarzających, ta funkcja zwraca obraz w odcieniach szarości, a nie RGB. Potrzebują tego operacje morfologiczne.
    def _to_gray(self, image: Image.Image) -> np.ndarray:
        """Konwertuje do grayscale numpy."""
        return np.array(image.convert('L'))

    def _erode(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Erozja – minimum w oknie SE."""
        size = se.shape[0]
        pad  = size // 2
        padded = np.pad(img, pad, mode='edge')
        result = np.zeros_like(img)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i+size, j:j+size]
                result[i, j] = np.min(region[se == 1])
        return result

    def _dilate(self, img: np.ndarray, se: np.ndarray) -> np.ndarray:
        """Dylatacja – maksimum w oknie SE."""
        size = se.shape[0]
        pad  = size // 2
        padded = np.pad(img, pad, mode='edge')
        result = np.zeros_like(img)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i+size, j:j+size]
                result[i, j] = np.max(region[se == 1])
        return result

    def erosion(self, image: Image.Image, size: int = 3, shape: str = 'rect') -> Image.Image:
        """Erozja – ściera jasne obszary, pogrubia ciemne."""
        se  = self._get_structuring_element(size, shape)
        img = self._to_gray(image)
        result = self._erode(img, se)
        return Image.fromarray(result).convert('RGB')

    def dilation(self, image: Image.Image, size: int = 3, shape: str = 'rect') -> Image.Image:
        """Dylatacja – rozszerza jasne obszary."""
        se  = self._get_structuring_element(size, shape)
        img = self._to_gray(image)
        result = self._dilate(img, se)
        return Image.fromarray(result).convert('RGB')

    def opening(self, image: Image.Image, size: int = 3, shape: str = 'rect') -> Image.Image:
        """Otwarcie = erozja → dylatacja. Usuwa małe jasne obiekty."""
        se  = self._get_structuring_element(size, shape)
        img = self._to_gray(image)
        result = self._dilate(self._erode(img, se), se)
        return Image.fromarray(result).convert('RGB')

    def closing(self, image: Image.Image, size: int = 3, shape: str = 'rect') -> Image.Image:
        """Zamknięcie = dylatacja → erozja. Wypełnia małe dziury."""
        se  = self._get_structuring_element(size, shape)
        img = self._to_gray(image)
        result = self._erode(self._dilate(img, se), se)
        return Image.fromarray(result).convert('RGB')
    
    def top_hat(self, image, size=3, shape='rect'):
        se = self._get_structuring_element(size, shape)
        img = self._to_gray(image).astype('int16')
        opened = self._dilate(self._erode(img.astype('uint8'), se), se).astype('int16')
        result = np.clip(img - opened, 0, 255).astype('uint8')
        return Image.fromarray(result).convert('RGB')

    def black_hat(self, image, size=3, shape='rect'):
        se = self._get_structuring_element(size, shape)
        img = self._to_gray(image).astype('int16')
        closed = self._erode(self._dilate(img.astype('uint8'), se), se).astype('int16')
        result = np.clip(closed - img, 0, 255).astype('uint8')
        return Image.fromarray(result).convert('RGB')
    
    def skeletonize(self, image: Image.Image) -> Image.Image:
    
        se = self._get_structuring_element(3, 'cross')

        gray = self.convert_to_gray_avg(image)
        img  = np.array(gray.convert('L'))
        current = (img > 128).astype(np.uint8) * 255

        skeleton = np.zeros_like(current)

        while True:
            # 1. Erozja
            eroded = self._erode(current, se)

            # 2. Otwarcie = dylatacja zerodowanego
            opened = self._dilate(eroded, se)

            # 3. Różnica: current - opened
            temp = np.clip(current.astype(np.int16) - opened.astype(np.int16),
                        0, 255).astype(np.uint8)

            # 4. Dodaj do szkieletu (OR)
            skeleton = np.maximum(skeleton, temp)

            # 5. Aktualizacja – pracujemy na zerodowanym
            current = eroded

            if np.max(current) == 0:
                break

        return Image.fromarray(skeleton).convert('RGB')

    # ── Histogram ────────────────────────────────────────────
    def compute_histogram(self, image: Image.Image) -> dict[str, np.ndarray]:
        img = np.array(image)
        # print(f"DEBUG: Kształt obrazu to: {img.shape}")
        # print(f"Max wartość w obrazie: {np.max(img)}")
        hist = {}
        for i, channel in enumerate(['R', 'G', 'B']):
            hist[channel] = np.zeros(256, dtype=int)
            for val in img[:,:,i].flatten():
                hist[channel][val] += 1
        return hist

    def equalize_histogram(self, image: Image.Image) -> Image.Image:
        img = np.array(self.convert_to_gray_avg(image))
        hist = np.zeros(256, dtype=int)
        for val in img.flatten():
            hist[val] += 1
        n = img.size
        cdf = np.cumsum(hist)
        cdf_min = cdf[cdf > 0][0]
        lut = np.round((cdf - cdf_min) / (n - cdf_min) * 255).astype('uint8')
        result = lut[img]
        return Image.fromarray(result).convert('RGB')
    
    # ── Projekcja ────────────────────────────────────────────
    
    def compute_projections(self, image: Image.Image) -> tuple[np.array, np.array]:
        img = np.array(self.negative(image).convert("L"))
        horizontal = np.sum(img, axis=1) # suma wierszy (pozioma)
        vertical = np.sum(img, axis=0) # suma kolumn (pionowa)
        
        return horizontal, vertical

    # ──  ────────────────────────────────────────────
    def power_trans(self, image: Image.Image, alpha: float) -> Image.Image:
        """Podniosi obraz do potęgi alfa, dla alfa>1 i całkowitego mamy mnożenie obrazów, 
        dla alfa<1 uzyskujemy pierwiastkowanie - korekta gamma,
        wzór z normalizacją i przeskalowaniem do pełnego zakresu"""
        img = np.array(image).astype(float)
        j_max = np.max(img)
        if j_max > 0:
            result = 255 * np.power(img / j_max, alpha)
        else:
            result = img

        result = np.clip(result, 0, 255).astype('uint8')

        return Image.fromarray(result).convert('RGB')
    
    def log_trans(self, image: Image.Image) -> Image.Image:
        """Operacja logarytmowania - wzór z normalizacją i przeskalowaniem do pełnego zakresu"""
        img = np.array(image).astype(float)
        x = 255 / np.log(1 + np.max(img))
        result = x * np.log(1 + img)
        result = np.clip(result, 0, 255).astype('uint8')

        return Image.fromarray(result).convert('RGB')
    
