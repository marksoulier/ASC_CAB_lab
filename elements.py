import numpy as np


def icon_background():
    icon_grid_background = np.zeros(
        (200, 500, 4), dtype=np.uint8
    )  # 2 rows, 5 columns, considering each icon is 100x100
    icon_grid_background[:, :, 3] = 128  # Set alpha channel to 128 for transparency
    icon_grid_background[:, :, :3] = 128  # Set RGB channels to create gray color
    return icon_grid_background


def center_content_on_background(content, bg_width=1920, bg_height=1080):
    # Calculate the starting position to center the content on the background
    start_x = (bg_width - content.shape[1]) // 2
    start_y = (bg_height - content.shape[0]) // 2

    # Create a black background frame
    background = np.zeros((bg_height, bg_width, 3), dtype=np.uint8)

    # Place the content onto the background frame
    background[
        start_y : start_y + content.shape[0], start_x : start_x + content.shape[1]
    ] = content
    return background
