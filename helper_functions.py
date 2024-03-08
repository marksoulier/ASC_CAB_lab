import os
import cv2
import numpy as np


def check_content(content, mediums):
    """
    Input:
        content: dictionary of content with keys as the name of the content and values as the path to the content

    Output:
        None
    """
    print("Checking Mediums and Content")
    # check that all the files exist
    for key, value in content.items():
        if not os.path.exists(value):
            raise FileNotFoundError(f"File {value} does not exist.")

    # check that all the files connect to all the mediums
    for medium in mediums:
        if medium not in content:
            raise KeyError(f"Medium {medium} not in content dictionary.")


def place_icon_at_position(
    frame, icon_data, icon_pos_x, icon_pos_y, icon_size, coloration=3
):
    """
    Improved coloration handling to ensure smoother transitions from grayscale to color.
    """
    # Copy the icon image data to avoid modifying the original
    icon_image = icon_data["image"].copy()

    # Convert the icon to grayscale and then back to BGR to prepare for blending
    gray_icon = cv2.cvtColor(icon_image, cv2.COLOR_BGR2GRAY)
    gray_icon = cv2.cvtColor(gray_icon, cv2.COLOR_GRAY2BGR)

    if coloration < 0:
        # Use the grayscale icon if coloration is negative
        icon_image = gray_icon
    else:
        # Scale the coloration value to be within 0-1
        if coloration > 3:
            coloration = 3
        coloration = np.clip(coloration / 3, 0, 1)  # Assuming max coloration value is 5

        # Blend the grayscale icon with the original based on the coloration value
        icon_image = cv2.addWeighted(
            gray_icon, 1 - coloration, icon_image, coloration, 0
        )

    # Blend the (possibly adjusted) icon image using the pre-computed masks
    frame_slice = frame[
        icon_pos_y : icon_pos_y + icon_size, icon_pos_x : icon_pos_x + icon_size
    ]
    frame_slice[:, :, :3] = (
        icon_data["inverse_alpha_mask"][:, :, None] * frame_slice[:, :, :3]
        + icon_data["alpha_mask"][:, :, None] * icon_image
    )


# edge red tint function
def apply_red_tint(frame, amplitude_value, edge_width=50):
    """
    Applies a red tint to the edges of the frame.

    Parameters:
    - frame: The original video frame.
    - amplitude_value: Controls the intensity of the red tint.
    - edge_width: The width of the edges where the tint will be applied.

    Returns:
    - The frame with a red tint applied to its edges.
    """
    # Create a copy of the frame to avoid modifying the original
    tinted_frame = frame.copy()

    # Calculate the intensity of the red tint
    tint_intensity = amplitude_value / 5

    # Apply red tint to the top edge
    tinted_frame[:edge_width, :, 2] = cv2.addWeighted(
        tinted_frame[:edge_width, :, 2],
        1,
        np.full_like(tinted_frame[:edge_width, :, 2], 255),
        tint_intensity,
        0,
    )

    # Apply red tint to the bottom edge
    tinted_frame[-edge_width:, :, 2] = cv2.addWeighted(
        tinted_frame[-edge_width:, :, 2],
        1,
        np.full_like(tinted_frame[-edge_width:, :, 2], 255),
        tint_intensity,
        0,
    )

    # Apply red tint to the left edge
    tinted_frame[:, :edge_width, 2] = cv2.addWeighted(
        tinted_frame[:, :edge_width, 2],
        1,
        np.full_like(tinted_frame[:, :edge_width, 2], 255),
        tint_intensity,
        0,
    )

    # Apply red tint to the right edge
    tinted_frame[:, -edge_width:, 2] = cv2.addWeighted(
        tinted_frame[:, -edge_width:, 2],
        1,
        np.full_like(tinted_frame[:, -edge_width:, 2], 255),
        tint_intensity,
        0,
    )

    return tinted_frame
