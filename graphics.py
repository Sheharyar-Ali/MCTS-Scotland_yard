import pygame as pg
# import cv2
import numpy as np
import matplotlib.pyplot as plt

def Draw_positions(player, seekers, immobile_seeker_locations):
    """
    Create a pygame window and draw the map and all relevant positions
    :param player: player entity
    :param seekers: list of seekers
    :param immobile_seeker_locations: list of seekers that can not move anymore
    """
    pg.init()
    pg.font.init()

    # Window size
    window = (1500, 671)

    # The map image
    map = pg.image.load("Images/map.png")
    background = pg.transform.scale(map, window)
    screen = pg.display.set_mode(window)
    screen.fill((0, 0, 0))

    # Draw the player's position
    player_station_info = player.get_station_info(station=player.position)
    pg.draw.circle(background, (0, 255, 0), player_station_info[1], 13, 5)

    # Draw the seekers' positions
    for seeker in seekers:
        seeker_station_info = seeker.get_station_info(seeker.position)
        pg.draw.circle(background, (255, 0, 0), seeker_station_info[1], 13, 3)
    if len(immobile_seeker_locations) > 0:
        for location in immobile_seeker_locations:
            location_info = player.get_station_info(location)
            pg.draw.circle(background, (255, 0, 255), location_info[1], 13, 3)
    screen.blit(background, [0, 0])
    pg.display.flip()


# Code used to find the positions of the stations
# def find_red_circles(image_path):
#     # Read the image
#     image = cv2.imread(image_path)
#
#     # Convert the image to the BGR color space (OpenCV's default)
#     # This is required because we'll be using color-based segmentation in BGR space
#     image_bgr = image.copy()
#
#     # Define the lower and upper bounds of the #FB0B1F color in BGR format
#     lower_red = np.array([31, 11, 251])
#     upper_red = np.array([31, 11, 251])
#
#     # Create a mask where the #FB0B1F color is segmented
#     mask_red = cv2.inRange(image_bgr, lower_red, upper_red)
#
#     # Find contours of the red regions
#     contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     # Initialize an empty list to store red circle positions
#     red_circle_positions = []
#
#     # Loop through the detected contours and filter out circular shapes
#     for contour in contours:
#         area = cv2.contourArea(contour)
#         perimeter = cv2.arcLength(contour, True)
#         circularity = 4 * np.pi * area / (perimeter * perimeter)
#
#         # Adjust the threshold value as needed for circularity detection
#         if 0.8 <= circularity <= 1.2:
#             # Find the center of the circle
#             M = cv2.moments(contour)
#             if M["m00"] != 0:
#                 cX = int(M["m10"] / M["m00"])
#                 cY = int(M["m01"] / M["m00"])
#                 red_circle_positions.append((cX, cY))
#
#     return red_circle_positions


#
#
# image_path = "locations.png"
#
# red_circle_positions = find_red_circles(image_path)
#
# print("Positions of  Circles:")
# for i, pos in enumerate(red_circle_positions):
#     print(f"Circle {i}: (x={pos[0]}, y={pos[1]})")
#
#     # Display the image with circles plotted at the detected positions
# image_rgb = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
# for pos in red_circle_positions:
#     cv2.circle(image_rgb, (pos[0], pos[1]), radius=5, color=(0, 255, 0), thickness=-1)
# i = 97


