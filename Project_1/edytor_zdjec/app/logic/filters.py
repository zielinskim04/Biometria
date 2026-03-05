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
        return Image.fromarray(gray).convert("RGB")  # ← PIL.Image z powrotem

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
        img = np.array(image.convert("L"))  # greyscale numpy
        rows, cols = img.shape
        result = np.zeros((rows, cols), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                result[i,j] = 255 if img[i,j] > threshold else 0
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
        """Filtr uśredniający – każdy piksel = średnia z otoczenia"""
        img = np.array(image).astype('float32')
        pad = size // 2
        result = np.zeros_like(img)
        padded = np.pad(img, ((pad,pad),(pad,pad),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                result[i,j] = np.mean(padded[i:i+size, j:j+size], axis=(0,1))
        return Image.fromarray(result.astype('uint8'))

    def gaussian_filter(self, image, size=3, sigma=1.0):
        """Filtr Gaussa – ważona średnia z otoczenia"""
        # Generuj jądro Gaussa ręcznie
        kernel = np.zeros((size, size))
        center = size // 2
        for x in range(size):
            for y in range(size):
                kernel[x,y] = np.exp(-((x-center)**2 + (y-center)**2) / (2*sigma**2))
        kernel /= kernel.sum()  # normalizacja

        img = np.array(image).astype('float32')
        pad = size // 2
        result = np.zeros_like(img)
        padded = np.pad(img, ((pad,pad),(pad,pad),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for c in range(3):
                    result[i,j,c] = np.sum(padded[i:i+size, j:j+size, c] * kernel)
        return Image.fromarray(result.astype('uint8'))

    def sharpen_filter(self, image):
        """Filtr wyostrzający – jądro z ujemnymi wagami wokół centrum"""
        kernel = np.array([[ 0, -1,  0],
                        [-1,  5, -1],
                        [ 0, -1,  0]], dtype='float32')
        img = np.array(image).astype('float32')
        result = np.zeros_like(img)
        padded = np.pad(img, ((1,1),(1,1),(0,0)), mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for c in range(3):
                    result[i,j,c] = np.sum(padded[i:i+3, j:j+3, c] * kernel)
        result = np.clip(result, 0, 255)
        return Image.fromarray(result.astype('uint8'))
    

    #Do histogramu i wyrównywania histogramu, jeszcze nie są używane
    def compute_histogram(self, image):
        """Zwraca histogram jako dict {R: array, G: array, B: array}"""
        img = np.array(image)
        hist = {}
        for i, channel in enumerate(['R', 'G', 'B']):
            hist[channel] = np.zeros(256, dtype=int)
            for val in img[:,:,i].flatten():
                hist[channel][val] += 1
        return hist

    def equalize_histogram(self, image):
        """Wyrównywanie histogramu – poprawia kontrast"""
        img = np.array(image.convert('L'))
        hist = np.zeros(256, dtype=int)
        for val in img.flatten():
            hist[val] += 1
        n = img.size
        cdf = np.cumsum(hist)
        cdf_min = cdf[cdf > 0][0]
        lut = np.round((cdf - cdf_min) / (n - cdf_min) * 255).astype('uint8')
        result = lut[img]
        return Image.fromarray(result).convert('RGB')