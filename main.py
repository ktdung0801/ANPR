import argparse
import timeit

from natsort import natsorted

from WpodDetect import *
from preprocess import *
from recognition import *
from segmentation import *


def folder_image(path_f):
    pathfolder = path_f
    files_path = get_filepaths(pathfolder)
    files_path = natsorted(files_path)
    for j in range(len(files_path)):
        start = timeit.default_timer()
        crop_LP_arr, image_dectect, x_arr, y_arr = Wpod_detect(files_path[j])
        stop_yolo = timeit.default_timer()
        time_yolo = stop_yolo - start
        time_execute_preprocess = 0
        time_execute_g_segement = 0
        time_execute_recognition = 0
        if crop_LP_arr is None:
            cv2.imwrite('output/' + path_leaf(files_path[j]), image_dectect)
            break
        print('Image:', path_leaf(files_path[j]))
        for i in range(len(crop_LP_arr)):
            start_preprocess = timeit.default_timer()
            plate_image, gray, blur, binary, final = preprocess_img(crop_LP_arr[i])
            # cv2.imwrite('output/' + str(i+j+10000) + '.jpg', crop_LP_arr[0])
            stop_preprocess = timeit.default_timer()
            time_execute_preprocess = time_execute_preprocess + stop_preprocess - start_preprocess

            start_g_segment = timeit.default_timer()
            _, crop_characters, crop_characters_line2 = g_segment(plate_image, final, final)
            stop_g_segment = timeit.default_timer()
            time_execute_g_segement = time_execute_g_segement + stop_g_segment - start_g_segment

            start_recognition = timeit.default_timer()
            s = g_recognition(crop_characters, crop_characters_line2, crop_LP_arr[i])
            stop_recognition = timeit.default_timer()
            time_execute_recognition = time_execute_recognition + stop_recognition - start_recognition

            plate_color = get_bgcolor_LP(crop_LP_arr[i])
            if len(crop_characters_line2) == 0:
                plate_square = 'long'
            else:
                plate_square = 'square'

            if (len(s)) >= 6:
                print('LP: ', s)
                print('Type: ', plate_square)
                print('Color: ', plate_color)
                if len(crop_characters) > 3 and len(crop_characters_line2) > 0:
                    print('Vehicle: motorbike\n')
                else:
                    print('Vehicle: car\n')
                image_dectect = draw_number(image_dectect, x_arr[i], y_arr[i], s)
            if i == 0:
                with open("list.txt", "a") as myfile:
                    myfile.write(path_leaf(files_path[j]) + '\t' + s + '\n')

        print('Time detect wpod: ', time_yolo)
        print('Time preprocess: ', time_execute_preprocess)
        print('Time segmentation: ', time_execute_g_segement)
        print('Time recognition: ', time_execute_recognition)
        print('Total time: ', time_yolo + time_execute_preprocess + time_execute_g_segement + time_execute_recognition)
        print('\n')
        cv2.imwrite('output/' + path_leaf(files_path[j]), image_dectect)


def one_image(path):
    filelist = [f for f in os.listdir('visualize')]
    for f in filelist:
        os.remove(os.path.join('visualize', f))

    start = timeit.default_timer()
    crop_LP_arr, image_dectect, x_arr, y_arr = Wpod_detect(path)
    stop_yolo = timeit.default_timer()
    time_yolo = stop_yolo - start
    time_execute_preprocess = 0
    time_execute_g_segement = 0
    time_execute_recognition = 0
    if crop_LP_arr is None:
        cv2.imwrite('visualize/done.jpg', image_dectect)
        cv2.imshow('done', image_dectect)
        cv2.waitKey()
        cv2.destroyAllWindows()
        return image_dectect
    for i in range(len(crop_LP_arr)):
        start_preprocess = timeit.default_timer()
        plate_image, gray, blur, binary, final = preprocess_img(crop_LP_arr[i])
        cv2.imwrite('visualize/LP_' + str(i) + '.jpg', crop_LP_arr[i])
        stop_preprocess = timeit.default_timer()
        time_execute_preprocess = time_execute_preprocess + stop_preprocess - start_preprocess

        visualize_results_preprocess(plate_image, gray, blur, binary, final)

        cv2.imwrite('visualize/preprocess.png', final)
        start_g_segment = timeit.default_timer()
        ig, crop_characters, crop_characters_line2 = g_segment(plate_image, final, final)
        stop_g_segment = timeit.default_timer()
        time_execute_g_segement = time_execute_g_segement + stop_g_segment - start_g_segment

        visualize_segment(ig, crop_characters, crop_characters_line2)

        start_recognition = timeit.default_timer()
        s = visualize_g_recognition(crop_characters, crop_characters_line2, crop_LP_arr[i])
        stop_recognition = timeit.default_timer()
        #plt.show()
        time_execute_recognition = time_execute_recognition + stop_recognition - start_recognition

        plate_color = get_bgcolor_LP(crop_LP_arr[i])
        if len(crop_characters_line2) == 0:
            plate_square = 'long'
        else:
            plate_square = 'square'

        print('LP: ', s)
        print('Type: ', plate_square)
        print('Color: ', plate_color)
        '''if len(crop_characters) > 3 and len(crop_characters_line2) > 0:
            print('Vehicle: Motorbike\n')
        else:
            print('Vehicle: Car\n')'''
        if len(s)>0:
            image_dectect = draw_number(image_dectect, x_arr[i], y_arr[i], s)

    print('Time detect wpod: ', time_yolo)
    print('Time preprocess: ', time_execute_preprocess)
    print('Time segmentation: ', time_execute_g_segement)
    print('Time recognition: ', time_execute_recognition)
    print('Total time: ', time_yolo + time_execute_preprocess + time_execute_g_segement + time_execute_recognition)

    cv2.imwrite('visualize/done.jpg', image_dectect)
    # cv2.namedWindow('done', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('done', 600, 600)
    cv2.imshow('done', image_dectect)
    cv2.waitKey()
    cv2.destroyAllWindows()


def video_image(path):
    crop_LP_arr, image_dectect, x_arr, y_arr = Wpod_detect(path)

    if crop_LP_arr is None:
        return image_dectect
    plate_image, gray, blur, binary, final = preprocess_img(crop_LP_arr[0])

    ig, crop_characters, crop_characters_line2 = g_segment(plate_image, final, final)

    s = g_recognition(crop_characters, crop_characters_line2, crop_LP_arr[0])

    if (len(s)) >= 6:
        image_dectect = draw_number(image_dectect, x_arr[0], y_arr[0], s)

    return image_dectect


def load_video(path):
    import cv2

    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(path)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error opening video stream or file")

    # Read until video is completed
    t = 0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:

            start = timeit.default_timer()

            frame = frame[300:1080, 0:1000]
            frame = video_image(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("Frame", frame)

            stop = timeit.default_timer()
            time = 1.0 / (stop - start)
            print('FPS:', time)

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            t = t+1
            if t == 1000:
                t = 0
        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--image', required=False,
                    help='path to input image')
    ap.add_argument('-f', '--folder', required=False, default=0,
                    help='path to input folder image')
    ap.add_argument('-v', '--video', required=False, default=0,
                    help='path to video')
    args = ap.parse_args()

    # MobileNets
    json_path = 'MobileNets_character_recognition.json'
    weights_path = 'License_character_recognition.h5'
    label_path = 'license_character_classes.npy'

    # Yolo
    classes_path = 'obj.names'
    weights_yolo_path = 'yolov3-obj_last.weights'
    config_path = 'yolo-obj-v3.cfg'

    # Wpod
    json_path_wpod = 'wpod-net.json'

    start = timeit.default_timer()
    LoadModelMobileNets(json_path, weights_path, label_path)
    stop = timeit.default_timer()
    print('\nTime load MobileNets: ', stop - start)

    start = timeit.default_timer()
    Wpod_Init(json_path_wpod)
    stop = timeit.default_timer()
    print('Time load WPOD: ', stop - start)
    print('\n')

    if args.folder != 0:
        folder_image(args.folder)
    elif args.video != 0:
        load_video(args.video)
    else:
        one_image(args.image)
