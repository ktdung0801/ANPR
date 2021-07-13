import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys

stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
import keras
sys.stderr = stderr
from keras.models import model_from_json, Sequential
from os.path import splitext

import cv2
import numpy as np


from utils import detect_lp

wpod_net = Sequential()


def Wpod_Init(path_json):
    global wpod_net
    wpod_net = load_model(path_json)


def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        return model
    except Exception as e:
        print(e)


def preprocess_image(image_path, resize=False):
    if isinstance(image_path, str):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img = image_path.copy()
    img = img / 255
    if resize:
        img = cv2.resize(img, (224, 224))
    return img


def get_plate(vehicle_image):
    Dmax = 608
    Dmin = 288
    vehicle = vehicle_image.copy()
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    _, LpImg, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    return LpImg, cor


# Visualize our result
def draw_box(vehicle_img, cor, thickness=2):
    vehicle_image = vehicle_img.copy()
    for j in range(len(cor)):
        pts = []
        x_coordinates = cor[j][0]
        y_coordinates = cor[j][1]
        # store the top-left, top-right, bottom-left, bottom-right
        # of the plate license respectively
        for i in range(4):
            pts.append([int(x_coordinates[i]), int(y_coordinates[i])])

        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))

        vehicle_image = cv2.polylines(vehicle_image, [pts], True, (0, 255, 0), thickness)
    return vehicle_image


def Wpod_detect(path):
    vehicle_image = preprocess_image(path)
    LpImg_arr, cor = get_plate(vehicle_image)
    if LpImg_arr is not None:
        vehicle_image = draw_box(vehicle_image, cor)
        x_arr = []
        y_arr = []
        for i in range(len(cor)):
            x_arr.append(min(cor[i][0]))
            y_arr.append(min(cor[i][1]))
        vehicle_image = cv2.convertScaleAbs(vehicle_image, alpha=255.0)
        vehicle_image = cv2.cvtColor(vehicle_image, cv2.COLOR_BGR2RGB)
        for i in range(len(LpImg_arr)):
            LpImg_arr[i] = cv2.convertScaleAbs(LpImg_arr[i], alpha=255.0)
            LpImg_arr[i] = cv2.cvtColor(LpImg_arr[i], cv2.COLOR_BGR2RGB)
        return LpImg_arr, vehicle_image, x_arr, y_arr
    else:
        vehicle_image = cv2.convertScaleAbs(vehicle_image, alpha=255.0)
        vehicle_image = cv2.cvtColor(vehicle_image, cv2.COLOR_BGR2RGB)
        return LpImg_arr, vehicle_image, None, None

# LpImg_arr, Image, x_arr, y_arr = Wpod_detect('0449.jpg')
# testig = draw_box(test_image, cor)
#
# plate_image = cv2.convertScaleAbs(testig, alpha=(255.0))
# plate_image = cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB)
# print(x_arr)
# print(y_arr)
# cv2.imshow('tt', Image)
# cv2.waitKey(0)
