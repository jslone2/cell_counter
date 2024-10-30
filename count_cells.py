import numpy as np
import cv2
from matplotlib import pyplot as plt
import copy


markers = []
num_dots = 0

def count_dots(image,color='blue',rad=27,small=25):
    global markers
    global num_dots

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])

    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create a mask for color
    if color == 'blue':
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
    elif color == 'red':
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

    D = rad**2

    # Find the contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    num_dots = 0
    markers = []
    for con in contours:
        M = cv2.moments(con)
        if M['m00'] > small:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center_new = True
            for center in markers:
                if (cx-center[0])**2+(cy-center[1])**2 < D:
                    center_new = False
                    break
            if center_new:
                num_dots += 1
                markers.append([cx,cy])

def mouse_callback(event, x, y, flags, param):
    global markers
    global num_dots

    x,y = x*3, y*3

    if event == cv2.EVENT_LBUTTONDOWN:
        markers.append([x,y])
        num_dots += 1
    elif event == cv2.EVENT_RBUTTONDOWN:
        if markers:
            # Remove the marker closest to the right-click position
            min_dist = float('inf')
            min_index = -1
            for i, marker in enumerate(markers):
                dist = (marker[0] - x)**2 + (marker[1] - y)**2
                if dist < min_dist:
                    min_dist = dist
                    min_index = i
            if min_index != -1:
                del markers[min_index]
                num_dots -= 1

def draw_markers(img):
    global markers
    for marker in markers:
        cv2.drawMarker(img, marker, (255, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=40, thickness=3)
    return img

# Example usage
# image_path = "demo.tif"

if __name__ == "__main__":
    print("What image do we want to count?")
    image_path = input()

    print("What color cells are we counting? 'blue' or 'red'")
    color = input()

    image = cv2.imread(image_path)
    count_dots(image,color)

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', mouse_callback)

    while True:
        show = copy.deepcopy(image)
        show = draw_markers(show)
        # print(show.shape)
        show = cv2.resize(show, (show.shape[1]//3, show.shape[0]//3))
        cv2.imshow('image', show)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
    print("Number of dots:", num_dots)
