import cv2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# Create sort_contours() function to grab the contour of each digit from left to right
def sort_contours(cnts, reverse=False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts


def g_segment(plate_image, binary, thre_mor):

    cont, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # creat a copy version "test_roi" of plat_image to draw bounding box
    test_roi = plate_image.copy()

    # Initialize a list which will be used to append charater image
    crop_characters = []
    crop_characters_line2 = []

    # define standard width and height of character
    digit_w, digit_h = 30, 60

    # check if lp is square
    if test_roi.shape[1] / float(test_roi.shape[0]) > 1.5:
        check_square = 'long'
    else:
        check_square = 'square'

    # for c in sort_contours(cont):
    if len(cont) != 0:
        for c in sort_contours(cont):
            (x, y, w, h) = cv2.boundingRect(c)

            # rule to determine characters
            aspectRatio = h / float(w)
            solidity = cv2.contourArea(c) / float(w * h)
            heightRatio = h / float(plate_image.shape[0])

            if 1.5 <= aspectRatio <= 4.5 and solidity > 0.1 and 0.33 < heightRatio < 0.5 and check_square == 'square':
                # Draw bounding box arroung digit number
                cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Sperate number and gibe prediction
                curr_num = thre_mor[y:y + h, x:x + w]
                curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                if y < plate_image.shape[0] / 3:
                    crop_characters.append(curr_num)
                else:
                    crop_characters_line2.append(curr_num)

            if 1.5 <= aspectRatio <= 4.5 and solidity > 0.1 and heightRatio > 0.5 and check_square == 'long':
                # Draw bounding box arroung digit number
                cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Sperate number and gibe prediction
                curr_num = thre_mor[y:y + h, x:x + w]
                curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                crop_characters.append(curr_num)

    return test_roi, crop_characters, crop_characters_line2


def visualize_segment(test_roi, crop_characters, crop_characters_line2):
    if len(crop_characters) == 0:
        return None
    print("Detect {} letters...".format(len(crop_characters) + len(crop_characters_line2)))
    plt.axis(False)
    plt.imshow(test_roi)
    plt.savefig('visualize/grab_digit_contour.png', dpi=100)

    fig = plt.figure(figsize=(14, 4))
    grid = gridspec.GridSpec(ncols=len(crop_characters), nrows=1, figure=fig)

    for i in range(len(crop_characters)):
        fig.add_subplot(grid[i])
        plt.axis(False)
        plt.imshow(crop_characters[i], cmap="gray")
    plt.savefig("visualize/segmented_leter.png", dpi=100)

    if len(crop_characters_line2) > 0:
        fig = plt.figure(figsize=(14, 4))
        grid = gridspec.GridSpec(ncols=len(crop_characters_line2), nrows=1, figure=fig)

        for i in range(len(crop_characters_line2)):
            fig.add_subplot(grid[i])
            plt.axis(False)
            plt.imshow(crop_characters_line2[i], cmap="gray")
        plt.savefig("visualize/segmented_leter_line2.png", dpi=100)

    #plt.show()
