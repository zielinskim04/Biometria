import numpy as np
from PIL import Image


class ImageUtils:
    """Konwersja do skali szarości i operacje morfologiczne."""

    # ------------------------------------------------------------------ #
    # Konwersja                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def to_gray_pil(image: Image.Image) -> np.ndarray:
        """Konwersja PIL → uint8 ndarray (skala szarości)."""
        return np.array(image.convert('L'))

    @staticmethod
    def to_gray(img: np.ndarray) -> np.ndarray:
        """
        Ręczna konwersja RGB → skala szarości (wzór BT.601).
        Wejście: ndarray (H, W, 3) uint8.
        """
        h, w = img.shape[:2]
        gray = np.zeros((h, w), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                r, g, b = img[y, x, 0], img[y, x, 1], img[y, x, 2]
                gray[y, x] = int(0.299 * r + 0.587 * g + 0.114 * b)
        return gray

    # ------------------------------------------------------------------ #
    # Morfologia pełna (maska kwadratowa 3×3)                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def erode(img: np.ndarray) -> np.ndarray:
        """Erozja morfologiczna maską 3×3."""
        h, w = img.shape
        out  = np.zeros_like(img)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                out[y, x] = np.min(img[y-1:y+2, x-1:x+2])
        return out

    @staticmethod
    def dilate(img: np.ndarray) -> np.ndarray:
        """Dylatacja morfologiczna maską 3×3."""
        h, w = img.shape
        out  = np.zeros_like(img)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                out[y, x] = np.max(img[y-1:y+2, x-1:x+2])
        return out

    @classmethod
    def opening(cls, img: np.ndarray) -> np.ndarray:
        """Otwarcie morfologiczne (erozja → dylatacja)."""
        return cls.dilate(cls.erode(img))

    @classmethod
    def closing(cls, img: np.ndarray) -> np.ndarray:
        """Domknięcie morfologiczne (dylatacja → erozja)."""
        return cls.erode(cls.dilate(img))

    # ------------------------------------------------------------------ #
    # Morfologia krzyżowa (element strukturalny +)                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def erode_cross(img: np.ndarray) -> np.ndarray:
        """Erozja morfologiczna elementem krzyżowym."""
        h, w = img.shape
        out  = np.zeros_like(img)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if (img[y, x] == 1 and img[y-1, x] == 1 and
                        img[y+1, x] == 1 and img[y, x-1] == 1 and
                        img[y, x+1] == 1):
                    out[y, x] = 1
        return out

    @staticmethod
    def dilate_cross(img: np.ndarray) -> np.ndarray:
        """Dylatacja morfologiczna elementem krzyżowym."""
        h, w = img.shape
        out  = img.copy()
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if img[y, x] == 1:
                    out[y-1, x] = out[y+1, x] = 1
                    out[y, x-1] = out[y, x+1] = 1
        return out

    @classmethod
    def opening_cross(cls, img: np.ndarray) -> np.ndarray:
        """Otwarcie morfologiczne elementem krzyżowym."""
        return cls.dilate_cross(cls.erode_cross(img))

    # ------------------------------------------------------------------ #
    # Splot 2D przez FFT (szybki, używany przez Gabor)                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def convolve2d_fft(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Splot liniowy 2D przez FFT; zwraca tablicę o rozmiarze wejścia."""
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
