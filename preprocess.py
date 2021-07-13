import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from data_utils import *
from plate import segment, noise, morph

plate_color = None


def preprocess_img(LpRegion):
    # LpImg = cv2.imread(path)
    # Scales, calculates absolute values, and converts the result to 8-bit.
    # square 280x200
    # long 470x110
    plate_image = LpRegion.copy()

    # plate_image = secondCrop(plate_image)
    # convert to grayscale and blur the image
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (7, 7), 0)

    ##############
    h, w = gray.shape
    global plate_color
    plate_color = get_bgcolor_LP(LpRegion)

    if plate_color == 'blue' or plate_color == 'red':
        gray = cv2.bitwise_not(gray)
    # bilateral filter
    wsize = h >> 3
    gray = cv2.bilateralFilter(gray, wsize, 30, wsize)
    # create a CLAHE object (Arguments are optional).
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # noise filtering
    filtered = noise.homomorphic(gray, 0.1, 1.0)

    # binarization
    _, img_bin = cv2.threshold(filtered, 0, 255, cv2.THRESH_OTSU)
    # img_bin = cv2.dilate(img_bin, cv2.getStructuringElement(cv2.MORPH_ERODE, (2, 2)), iterations=1)

    # clean contours & dilate
    contours, selected = morph.clean_contours(img_bin)
    mask = segment.draw_segmentation_mask(w, h, contours, selected)
    # mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ERODE, (2, 2)), iterations=1)

    # contours #2 & segment
    binary = segment.process_mask(filtered, mask)

    # contours final
    final = morph.clean_img_bin(binary, 20, h * w * 0.5)

    #######
    final = cv2.bitwise_not(final)
    if check_square(LpRegion) == 1:
        kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        final_dilate = cv2.morphologyEx(final, cv2.MORPH_DILATE, kernel3)
    else:
        final_dilate = final
    return plate_image, gray, filtered, img_bin, final_dilate


def visualize_results_preprocess(plate_image, gray, blur, binary, final_dilation):
    # visualize results
    fig = plt.figure(figsize=(12, 7))
    plt.rcParams.update({"font.size": 18})
    grid = gridspec.GridSpec(ncols=3, nrows=2, figure=fig)
    plot_image = [plate_image, gray, blur, binary, final_dilation]
    plot_name = ["plate_image", "gray", "blur", "binary", "final_dilation"]

    for i in range(len(plot_image)):
        fig.add_subplot(grid[i])
        plt.axis(False)
        plt.title(plot_name[i])
        if i == 0:
            plt.imshow(plot_image[i])
        else:
            plt.imshow(plot_image[i], cmap="gray")
    plt.show()
