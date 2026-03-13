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

    def average_filter(self, image, size=3):
        """Filtr uśredniający, gdzie wielkość kernela jest wybierana"""
        img = np.array(image).astype('float32')
        pad = size // 2
        result = np.zeros_like(img)
        padded = np.pad(img, ((pad,pad),(pad,pad),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                result[i,j] = np.mean(padded[i:i+size, j:j+size], axis=(0,1))
        return Image.fromarray(result.astype('uint8'))
    

    def gaussian_filter(self, image, size=3, sigma=1.0):
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
    
    def sharpen_filter(self, image, preset="mean_removal"):
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
    
    def roberts_cross(self, image) -> Image.Image:
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

    def custom_filter(self, image, kernel: np.ndarray):
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

    def compute_histogram(self, image: Image.Image):
        img = np.array(image)
        # print(f"DEBUG: Kształt obrazu to: {img.shape}")
        # print(f"Max wartość w obrazie: {np.max(img)}")
        hist = {}
        for i, channel in enumerate(['R', 'G', 'B']):
            hist[channel] = np.zeros(256, dtype=int)
            for val in img[:,:,i].flatten():
                hist[channel][val] += 1
        return hist

    def equalize_histogram(self, image):
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
    
    def compute_projections(self, image):
        img = np.array(self.convert_to_gray_avg(image))
        
        # axis=1 - suma wierszy (pozioma)
        # axis=0 - suma kolumn (pionowa)
        horizontal = np.sum(img, axis=1)
        vertical = np.sum(img, axis=0)
        
        return horizontal, vertical