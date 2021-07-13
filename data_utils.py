import cv2
import os
import numpy as np
import ntpath
import numexpr as ne


def bincount_numexpr_app(a):
    a2D = a.reshape(-1, a.shape[-1])
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    eval_params = {'a0': a2D[:, 0], 'a1': a2D[:, 1], 'a2': a2D[:, 2],
                   's0': col_range[0], 's1': col_range[1]}
    a1D = ne.evaluate('a0*s0*s1+a1*s0+a2', eval_params)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


def get_bgcolor_LP(LpRegion):
    """
    rows, cols, _ = LpRegion.shape

    color_B = 0
    color_G = 0
    color_R = 0
    color_N = 0  # neutral/gray color

    for i in range(rows):
        for j in range(cols):
            k = LpRegion[i, j]
            color_B = color_B + k[0]
            color_G = color_G + k[1]
            color_R = color_R + k[2]

    pix_total = rows * cols
    sums = pix_total
    # print('Blue:', color_B/sums, 'Green:', color_G/sums, 'Red:', color_R/sums, 'Gray:', color_N*255 / pix_total)
    """
    bgr = bincount_numexpr_app(LpRegion)
    # bgr = (color_B / sums, color_G / sums, color_R / sums)
    if bgr[0] > 140 and bgr[1] > 140 and bgr[2] > 140:
        return 'white'
    if bgr[0] > 128 and bgr[0] > bgr[2]:
        return 'blue'
    if bgr[2] > 128 and bgr[2] > bgr[0]:
        return 'red'
    return 'white'


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def draw_number(img, xx, yy, number):
    # Draw black background rectangle
    overlay = img.copy()
    x = int(xx) - 10
    y = int(yy) - 10
    start_point = (x, y - 20)
    end_point = (x + 130, y + 5)
    cv2.rectangle(overlay, start_point, end_point, (0, 0, 0), -1)
    alpha = 0.5  # Transparency factor.

    # Following line overlays transparent rectangle over the image
    img_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    cv2.putText(img_new, number, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    return img_new


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def resizeimg(img, scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)
    return resized


def check_square(img):
    if img.shape[1] / float(img.shape[0]) > 1.5:
        return 0
    else:
        return 1


def order_points(x_min, y_min, width, height):
    rect = np.zeros((4, 2), dtype="float32")

    # top left - top right - bottom left - bottom right
    rect[0] = np.array([round(x_min), round(y_min)])
    rect[1] = np.array([round(x_min + width), round(y_min)])
    rect[2] = np.array([round(x_min), round(y_min + height)])
    rect[3] = np.array([round(x_min + width), round(y_min + height)])

    return rect
