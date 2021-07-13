import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys

stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
import keras
sys.stderr = stderr
from keras.models import model_from_json, Sequential
from sklearn.preprocessing import LabelEncoder
from segmentation import *
from data_utils import *

model = Sequential()
labels = LabelEncoder()

plate_color = None
plate_square = None


def LoadModelMobileNets(json_path, weights_path, label_path):
    global model, labels
    # Load model architecture, weight and labels
    json_file = open(json_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(weights_path)

    # print("[INFO] Model loaded successfully...")

    # labels = LabelEncoder()
    labels.classes_ = np.load(label_path)
    # print("[INFO] Labels loaded successfully...")


# pre-processing input images and pedict with model
# def predict_from_model(image):
#     image = cv2.resize(image, (80, 80))
#     image = np.stack((image,) * 3, axis=-1)
#
#     prediction = labels.inverse_transform([np.argmax(model.predict(image[np.newaxis, :]))])
#     return prediction


def predict_from_model(image, curr_line, curr_char):
    image = cv2.resize(image, (80, 80))
    image = np.stack((image,) * 3, axis=-1)

    temp = np.argsort(model.predict(image[np.newaxis, :])).flatten()[::-1]
    prediction = []
    check = 0

    for i in range(len(temp)):
        prediction = labels.inverse_transform([temp[i]])
        # Bien so vuong

        if plate_square == 1:
            # Dong thu 2 phai la so
            if str(prediction[0]).isdigit() and curr_line == 2:
                check = 1
                break
            # Bien so do dong thu 1 phai la chu
            if str(prediction[0]).isupper() and plate_color == 'red' and curr_line == 1:
                check = 1
                break
            # Bien so trang, xanh, dong thu 1; 2 ky tu dau tien phai la so
            if str(prediction[0]).isdigit() and (plate_color != 'red') and curr_line == 1 and curr_char < 2:
                check = 1
                break
            # Bien so trang, xanh, dong thu 1; ky tu thu 3 phai la chu
            if str(prediction[0]).isupper() and (plate_color != 'red') and curr_line == 1 and curr_char == 2:
                check = 1
                break
        # Bien so dai
        else:
            # Bien so do; 2 ky tu dau tien phai la chu
            if str(prediction[0]).isupper() and plate_color == 'red' and curr_char < 2:
                check = 1
                break
            # Bien so do; nhung ky tu con lai phai la so
            if str(prediction[0]).isdigit() and plate_color == 'red' and curr_char >= 2:
                check = 1
                break
            # Bien so trang, xanh, dong thu 1; 2 ky tu dau tien phai la so
            if str(prediction[0]).isdigit() and (plate_color != 'red') and curr_char < 2:
                check = 1
                break
            # Bien so trang, xanh; ky tu thu 3 phai la chu
            if str(prediction[0]).isupper() and (plate_color != 'red') and curr_char == 2:
                check = 1
                break
            # Bien so trang, xanh; ky tu thu 5 -> end phai la so
            if str(prediction[0]).isdigit() and (plate_color != 'red') and curr_char >= 4:
                check = 1
                break
    if check == 0:
        prediction = labels.inverse_transform([temp[0]])
    return prediction


def g_recognition(crop_characters, crop_characters_line2, LpRegion):
    if len(crop_characters) == 0:
        return ""
    final_string = ''
    final_string_line2 = ''
    global plate_color
    global plate_square
    plate_color = get_bgcolor_LP(LpRegion)
    if len(crop_characters_line2) == 0:
        plate_square = 0
    else:
        plate_square = 1
    # line 1
    for i, character in enumerate(crop_characters):
        title = np.array2string(predict_from_model(character, 1, i))
        final_string += title.strip("'[]")

    # line 2
    if len(crop_characters_line2) > 0:
        for i, character in enumerate(crop_characters_line2):
            title = np.array2string(predict_from_model(character, 2, i))
            final_string_line2 += title.strip("'[]")

    final_string = final_string + final_string_line2
    # plt.show()
    return final_string


def visualize_g_recognition(crop_characters, crop_characters_line2, LpRegion):
    if len(crop_characters) == 0:
        return ""
    final_string = ''
    final_string_line2 = ''
    global plate_color
    global plate_square
    plate_color = get_bgcolor_LP(LpRegion)
    if len(crop_characters_line2) == 0:
        plate_square = 0
    else:
        plate_square = 1
    # line 1
    fig = plt.figure(figsize=(15, 3))
    cols = len(crop_characters)
    grid = gridspec.GridSpec(ncols=cols, nrows=1, figure=fig)

    for i, character in enumerate(crop_characters):
        fig.add_subplot(grid[i])
        title = np.array2string(predict_from_model(character, 1, i))
        plt.title('{}'.format(title.strip("'[]"), fontsize=20))
        final_string += title.strip("'[]")
        plt.axis(False)
        plt.imshow(character, cmap='gray')
    plt.savefig("visualize/recognition_leter.png", dpi=100)

    # line 2
    if len(crop_characters_line2) > 0:
        fig = plt.figure(figsize=(15, 3))
        cols = len(crop_characters_line2)
        grid = gridspec.GridSpec(ncols=cols, nrows=1, figure=fig)

        for i, character in enumerate(crop_characters_line2):
            fig.add_subplot(grid[i])
            title = np.array2string(predict_from_model(character, 2, i))
            plt.title('{}'.format(title.strip("'[]"), fontsize=20))
            final_string_line2 += title.strip("'[]")
            plt.axis(False)
            plt.imshow(character, cmap='gray')
        plt.savefig("visualize/recognition_leter_line2.png", dpi=100)
    final_string = final_string + final_string_line2
    return final_string
