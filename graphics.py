import pygame as pg
import cv2
import numpy as np
import matplotlib.pyplot as plt

pg.init()
pg.font.init()
window = (1500, 671)
res = (2500, 1000)
map = pg.image.load("map.png")
background = pg.transform.scale(map, window)
screen = pg.display.set_mode(window)
running = True
screen.fill((0, 0, 0))
screen.blit(background, [0, 0])


# 33,246
# (+15, +13)
#


def find_red_circles(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to the BGR color space (OpenCV's default)
    # This is required because we'll be using color-based segmentation in BGR space
    image_bgr = image.copy()

    # Define the lower and upper bounds of the #FB0B1F color in BGR format
    lower_red = np.array([31, 11, 251])
    upper_red = np.array([31, 11, 251])

    # Create a mask where the #FB0B1F color is segmented
    mask_red = cv2.inRange(image_bgr, lower_red, upper_red)

    # Find contours of the red regions
    contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize an empty list to store red circle positions
    red_circle_positions = []

    # Loop through the detected contours and filter out circular shapes
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # Adjust the threshold value as needed for circularity detection
        if 0.8 <= circularity <= 1.2:
            # Find the center of the circle
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                red_circle_positions.append((cX, cY))

    return red_circle_positions


image_path = "locations.png"

red_circle_positions = find_red_circles(image_path)

print("Positions of  Circles:")
for i, pos in enumerate(red_circle_positions):
    print(f"Circle {i}: (x={pos[0]}, y={pos[1]})")

    # Display the image with circles plotted at the detected positions
image_rgb = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
for pos in red_circle_positions:
    cv2.circle(image_rgb, (pos[0], pos[1]), radius=5, color=(0, 255, 0), thickness=-1)
i = 97


pos_x = red_circle_positions[i][0] + -1
pos_y = red_circle_positions[i][1] + 2
pg.draw.circle(background, (255, 0, 0), (pos_x, pos_y), 13, 2)
# pg.draw.circle(background, (255, 0, 0), (1340, 379), 13, 2)
screen.blit(background, [0, 0])
pg.display.flip()
print(pos_x,pos_y )
