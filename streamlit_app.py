import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
import cv2
import copy

st.set_page_config(layout="wide")

if "markers" not in st.session_state:
    st.session_state["markers"] = []
if "num_dots" not in st.session_state:
    st.session_state["num_dots"] = 0
if "image" not in st.session_state:
    st.session_state["image"] = None

def count_dots(image,color='blue',rad=27,small=25):

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])

    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

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
    for con in contours:
        M = cv2.moments(con)
        if M['m00'] > small:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center_new = True
            for center in st.session_state["markers"]:
                if (cx-center[0])**2+(cy-center[1])**2 < D:
                    center_new = False
                    break
            if center_new:
                st.session_state["num_dots"] += 1
                st.session_state["markers"].append([cx,cy])

def draw_markers(img):
    for marker in st.session_state["markers"]:
        cv2.drawMarker(img, marker, (255, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=40, thickness=3)
    return img

def main_loop():

    st.title("CELL COUNTING APP")
    st.subheader('Cell Count: '+str(st.session_state["num_dots"]))

    if st.checkbox("check for red    (default=blue)"):
        color = "red"
    else:
        color = "blue"

    rad = st.slider("Max Clump Diameter (recomended: 25)", min_value=0, max_value=50)
    small = st.slider("Min Cell Diameter (recomended: 25)", min_value=0, max_value=50)

    image_file = st.file_uploader("Upload Your Image", type=['jpg', 'png', 'jpeg', 'tif'])
    if image_file is not None:
        if st.session_state["image"] is None:
            file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
            st.session_state["image"] = cv2.imdecode(file_bytes, 1)
            count_dots(st.session_state["image"],color,rad,small)
            st.rerun()
        show = copy.deepcopy(st.session_state["image"])
        show = draw_markers(show)

        if st.checkbox("Remove Markers"):
            st.text("Removing Markers")
            removeing = True
        else:
            st.text("Adding Markers")
            removeing = False

        value = streamlit_image_coordinates(source=np.asarray(show),use_column_width="always")
        if value is not None:
            x = int(value['x'] * (show.shape[1]/value['width']))
            y = int(value['y'] * (show.shape[0]/value['height']))

            if not removeing:
                st.session_state["markers"].append([x,y])
                st.session_state["num_dots"] += 1
                st.rerun()
            else:
                if st.session_state["markers"]:
                    min_dist = float('inf')
                    min_index = -1
                    for i, marker in enumerate(st.session_state["markers"]):
                        dist = (marker[0] - x)**2 + (marker[1] - y)**2
                        if dist < min_dist:
                            min_dist = dist
                            min_index = i
                    if min_index != -1:
                        del st.session_state["markers"][min_index]
                        st.session_state["num_dots"] -= 1
                        st.rerun()

if __name__ == '__main__':
    main_loop()
