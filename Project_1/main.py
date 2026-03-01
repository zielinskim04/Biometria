from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def read_image_rgb(path):
    try:
        img = Image.open(path).convert('RGB')
        return np.array(img)
    except Exception as e:
        print("Reading error")
        return None

# Converting to gray scale using raw average
def convert_to_gray_avg(img):
    rows, cols = img.shape[:2]
    gray_img = np.zeros((rows, cols), dtype='uint8')
    for i in range(rows):
        for j in range(cols):
            avg = (int(img[i,j,0]) + int(img[i,j,1]) + int(img[i,j,2])) // 3
            gray_img[i,j] = avg
    return gray_img


# Converting to gray scale using "human eye" average - channel-dependent luminance perception
def convert_to_gray_human(img):
    rows, cols = img.shape[:2]
    gray_img = np.zeros((rows, cols), dtype='uint8')
    for i in range(rows):
        for j in range(cols):
            avg = (int(img[i,j,0]) * 0.2126 + int(img[i,j,1]) * 0.7152 + int(img[i,j,2]) * 0.0722) // 3
            gray_img[i,j] = avg
    return gray_img

def binarize(img, threshold = 50):
    if img.ndim == 3:
        img = convert_to_gray_human(img)
    rows, cols = img.shape[:2]
    bin_img = np.zeros((rows, cols), dtype='uint8')
    for i in range(rows):
        for j in range(cols):
            if img[i,j] > threshold:
                bin_img[i,j] = 255
            else:
                bin_img[i,j] = 0
    return bin_img

def negative(img):
    rows, cols = img.shape[:2]
    if img.ndim == 3:
        neg_img = np.zeros((rows, cols, 3), dtype='uint8')
        for i in range(rows):
            for j in range(cols):
                r = 255 - img[i,j,0]
                g = 255 - img[i,j,1]
                b = 255 - img[i,j,2]
                neg_img[i,j,0] = r
                neg_img[i,j,1] = g
                neg_img[i,j,2] = b
    else:
        for i in range(rows):
            for j in range(cols):
                neg_img[i, j] = 255 - img[i, j]
    return neg_img


path = "images/stefan1.jpeg"
img = read_image_rgb(path)
gray_1 = convert_to_gray_avg(img)
gray_2 = convert_to_gray_human(img)
bin = binarize(img)
neg = negative(img)

# Wyświetlanie trzech obrazów obok siebie
plt.figure(figsize=(20, 5))

plt.subplot(1, 5, 1)
plt.title("Oryginał (RGB)")
plt.imshow(img)

plt.subplot(1, 5, 2)
plt.title("avg")
plt.imshow(gray_1, cmap='gray') 

plt.subplot(1, 5, 3)
plt.title("luminance")
plt.imshow(gray_2, cmap='gray')

plt.subplot(1, 5, 4)
plt.title("Binaryzacja")
plt.imshow(bin, cmap='gray')

plt.subplot(1, 5, 5)
plt.title("Negatyw")
plt.imshow(neg) 

plt.show()