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

    def binarize(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        img = np.array(image.convert("L"))  # greyscale numpy
        rows, cols = img.shape
        result = np.zeros((rows, cols), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                result[i,j] = 255 if img[i,j] > threshold else 0
        return Image.fromarray(result).convert("RGB")

    def negative(self, image: Image.Image) -> Image.Image:
        img = np.array(image)
        rows, cols = img.shape[:2]
        neg = np.zeros_like(img)
        for i in range(rows):
            for j in range(cols):
                neg[i,j,0] = 255 - img[i,j,0]
                neg[i,j,1] = 255 - img[i,j,1]
                neg[i,j,2] = 255 - img[i,j,2]
        return Image.fromarray(neg)
    
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