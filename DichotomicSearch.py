import random
import sys
from itertools import product

from PIL import Image
import cv2
import numpy as np
from math import inf
import time

# --- GLOBAL DECLARATIONS ---

BOXSIZE = 16
green = (0, 255, 0)
red = (0, 0, 255)

img72 = cv2.imread('Images/image072.png')
img92 = cv2.imread('Images/image092.png')

grayImg72 = cv2.cvtColor(img72, cv2.COLOR_RGB2YCrCb)[:, :, 0]
grayImg92 = cv2.cvtColor(img92, cv2.COLOR_RGB2YCrCb)[:, :, 0]


# creating a new image72 with padding 64

# h, w, channels = img72.shape
# new_image_width = w+128
# new_image_height = h+128
# color = (0, 0, 0)
# newImage72 = np.full((new_image_height, new_image_width, channels), color, dtype=np.uint8)
# newGrayImg72 = cv2.cvtColor(newImage72, cv2.COLOR_RGB2YCrCb)[:, :, 0]
# x_center = (new_image_width - w) // 2
# y_center = (new_image_height - h) // 2
# newImage72[y_center:y_center+h, x_center:x_center+w] = img72
# cv2.imwrite('ImagesDichotomic/image072Padding.png',newImage72)


img72padding = cv2.imread('ImagesDichotomic/image072Padding.png')
newGrayImg72 = cv2.cvtColor(img72padding, cv2.COLOR_RGB2YCrCb)[:, :, 0]
height, width, channels = img92.shape


# --- CREATING THE NEW IMAGE EMPTY ---
newImg = np.zeros((height, width), dtype=np.uint8)


# --- FUNCTIONS ---
def MSE(bloc1, bloc2):
    block1, block2 = np.array(bloc1), np.array(bloc2)
    return np.square(np.subtract(block1, block2)).mean()


def dichotomicSearch(bloc, pointi, pointj):
    global y, x, bloc72
    stepToVosin = 32
    debut_i = pointi + 64
    debut_j = pointj + 64
    minmse = inf

    '''(debut_i, debut_j) is the top left point of the 9 blocks '''

    while stepToVosin >= 1:
        fin = stepToVosin * 2 + BOXSIZE
        for p in product([debut_i - stepToVosin, debut_i, debut_i + stepToVosin],
                         [debut_j - stepToVosin, debut_j, debut_j + stepToVosin]):
            # Cropping the bloc from the 072image
            px, py = int(p[0] - 8), int(p[1] - 8)
            bloc72 = newGrayImg72[px:px + BOXSIZE, py:py + BOXSIZE]
            # Calculating the MSE between the two blocks
            loss = MSE(bloc, bloc72)
            if loss < minmse:
                minmse = loss
                x, y = p
        stepToVosin = int(stepToVosin / 2)
        # We continue from the block with the smallest MSE between the 9 blocks after every step
        # So the affectation of (x,y) into (debut_i, debut_j) is required
        debut_i = x
        debut_j = y

    # We return the coordinates of the last block ( when step == 1 )
    return x, y, minmse, bloc72


def main():
    for i in range(0, height - BOXSIZE, BOXSIZE):  # HEIGHT
        for j in range(0, width - BOXSIZE, BOXSIZE):  # WIDTH
            # Cropping the bloc from the 092image
            bloc92 = grayImg92[i:i + BOXSIZE, j:j + BOXSIZE]
            # Applying the function
            x, y, minmse, bloc = dichotomicSearch(bloc92, i + 8, j + 8)  # +8 for the center of the bloc
            x -= 72
            y -= 72
            # Checking the MSE value
            if minmse > 50:
                # The res??du
                blocRes = bloc92 - bloc
                # We add our res??du-bloc to our EMPTY IMAGE
                newImg[i:i + BOXSIZE, j:j + BOXSIZE] = blocRes
                # Generating colors and draw rectangles on the two images
                cv2.rectangle(img92, (j, i),
                              (j + BOXSIZE, i + BOXSIZE), red, 2)
                cv2.rectangle(img72, (y, x),
                              (y + BOXSIZE, x + BOXSIZE), green, 2)


# --- MAIN PROGRAM ---

if __name__ == '__main__':
    start_time = time.time()
    print('processing...')
    main()
    print('processing finished.')
    time = time.time() - start_time
    print(f"{time} seconds")
    # Converting the MATRIX of THE EMPTY IMAGE into an Image
    imgResu = Image.fromarray(newImg)
    # Saving the results
    imgResu.save('ImagesDichotomic/imageResuDichotomic.png')

    cv2.imwrite('ImagesDichotomic/image072withGreenRect.png', img72)  # u can use just cv2.show()
    cv2.imwrite('ImagesDichotomic/image092withRedRect.png', img92)
    sys.exit()