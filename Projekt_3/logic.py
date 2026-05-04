import numpy as np
from PIL import Image

class ImageProcessor:

    def _get_structuring_element(self, size: int, shape: str) -> np.ndarray:
        se = np.zeros((size, size), dtype=np.uint8)
        center = size // 2
        if shape == 'ellipse':
            for i in range(size):
                for j in range(size):
                    if ((i - center) ** 2 + (j - center) ** 2) <= center ** 2:
                        se[i, j] = 1
        elif shape == 'cross':
            se[center, :] = 1
            se[:, center] = 1

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
    
    def skeletonize(self, image: Image.Image, threshold: int = 128) -> np.ndarray:
        gray    = self._to_gray(image)
        current = (gray > threshold).astype(np.uint8) * 255 

        se = self._get_structuring_element(3, 'cross')

        skeleton = np.zeros_like(current)

        while True:
            eroded = self._erode(current, se)

            opened = self._dilate(eroded, se)

            temp = np.clip(current.astype(np.int16) - opened.astype(np.int16),
                        0, 255).astype(np.uint8)

            skeleton = np.maximum(skeleton, temp)

            current = eroded

            if np.max(current) == 0:
                break

        return skeleton
    
    def KMM(self, image: Image.Image, threshold: int = 128) -> np.ndarray:
        gray    = self._to_gray(image)
        img = (gray < threshold).astype(np.uint8) 

        deletion_array = np.array([
            3, 5, 7, 12, 13, 14, 15, 20,
            21, 22, 23, 28, 29, 30, 31, 48,
            52, 53, 54, 55, 56, 60, 61, 62,
            63, 65, 67, 69, 71, 77, 79, 80,
            81, 83, 84, 85, 86, 87, 88, 89,
            91, 92, 93, 94, 95, 97, 99, 101,
            103, 109, 111, 112, 113, 115, 116, 117,
            118, 119, 120, 121, 123, 124, 125, 126,
            127, 131, 133, 135, 141, 143, 149, 151,
            157, 159, 181, 183, 189, 191, 192, 193,
            195, 197, 199, 205, 207, 208, 209, 211,
            212, 213, 214, 215, 216, 217, 219, 220,
            221, 222, 223, 224, 225, 227, 229, 231,
            237, 239, 240, 241, 243, 244, 245, 246,
            247, 248, 249, 251, 252, 253, 254, 255
        ])

        def get_neighbors_count(mask: np.ndarray) -> np.ndarray:
            padded = np.pad(mask, 1, mode='constant', constant_values=0)
            return (padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:] +
                    padded[:-2, :-2] + padded[:-2, 2:] + padded[2:, :-2] + padded[2:, 2:])

        def get_weights(mask: np.ndarray) -> np.ndarray:
            padded = np.pad(mask, 1, mode='constant', constant_values=0)
            return (padded[1:-1, 2:] * 1 +     
                    padded[:-2, 2:] * 2 +      
                    padded[:-2, 1:-1] * 4 +    
                    padded[:-2, :-2] * 8 +     
                    padded[1:-1, :-2] * 16 +   
                    padded[2:, :-2] * 32 +     
                    padded[2:, 1:-1] * 64 +    
                    padded[2:, 2:] * 128)
        
        while True:
            prev_img = img.copy()
            padded = np.pad(img, 1, mode='constant', constant_values=0)

            # Piksele 1 styające się z tłem -> 2
            edge_bg = (padded[:-2, 1:-1] == 0) | (padded[2:, 1:-1] == 0) | \
                      (padded[1:-1, :-2] == 0) | (padded[1:-1, 2:] == 0)
            img[(img == 1) & edge_bg] = 2

            # Piksele 1 stykające się rogiem z tłem -> 3
            corner_bg = (padded[:-2, :-2] == 0) | (padded[:-2, 2:] == 0) | \
                        (padded[2:, :-2] == 0) | (padded[2:, 2:] == 0)
            img[(img == 1) & corner_bg] = 3

            # Punkty konturowe z 2, 3 lub 4 stykającymi się sąsiadami -> 4
            contour_mask = (img == 2) | (img == 3)
            neighbors_count = get_neighbors_count(contour_mask.astype(np.uint8))
            
            cond_4 = contour_mask & ((neighbors_count == 2) | (neighbors_count == 3) | (neighbors_count == 4))
            img[cond_4] = 4

            # Usuwamy 4
            img[img == 4] = 0

            for N in [2, 3]:
                n_mask = (img == N)
                
                if not np.any(n_mask):
                    continue
                
                # Wagi liczone są na podstawie wszystkiego, co stanowi obiekt (czyli wartości > 0)
                bin_mask = (img > 0).astype(np.uint8)
                weights = get_weights(bin_mask)
                
                in_deletion_array = np.isin(weights, deletion_array)
                
                img[n_mask & in_deletion_array] = 0
                img[n_mask & ~in_deletion_array] = 1

            # Sprawdzenie one pixel wide skeleton - warunek stopu
            if np.array_equal(img, prev_img):
                break

        return (img* 255).astype(np.uint8)


