import cv2
import numpy as np
import pandas as pd
import time as time_module
from create_video.elements import icon_background, center_content_on_background
from create_video.helper_functions import (
    check_content,
    place_icon_at_position,
    apply_red_tint,
)
import os


def overlay_video(
    data_with_peaks,
    content,
    graph_file=None,
    GSR=True,
    FACET=True,
    Pupil=True,
    eye_tracking=True,
    HeartRate=True,
    graph=True,
    save=True,
    show=True,
    icons=None,
    update_progress=None,
):
    """
    Args:
        data_with_peaks: cleaned data file with all the participants
        content: dictionary with the content
        GSR: boolean if the GSR data is present
        FACET: boolean if the FACET data is present
        Pupil: boolean if the Pupil data is present
        eye_tracking: boolean if the eye tracking data is present
        Conductance: boolean if the Conductance data is present
        HeartRate: boolean if the HeartRate data is present
        graph: boolean if the graph of the data should be displayed
        video: boolean if the video of the data should be displayed
        save: boolean if the video of the data should be saved
        show: boolean if the video of the data should be shown
    Returns:
        Video of sensors overlayed on content
    """
    # load icons
    # icons = {
    #     "Joy": "create_video/icons/joy.png",
    #     "Anger": "create_video/icons/anger.png",
    #     "Surprise": "create_video/icons/surprise.png",
    #     "Fear": "create_video/icons/fear.png",
    #     "Disgust": "create_video/icons/disgust.png",
    #     "Sadness": "create_video/icons/sad.png",
    #     "Contempt": "create_video/icons/contempt.png",
    #     "Frustration": "create_video/icons/frustration.png",
    #     "Confusion": "create_video/icons/confusion.png",
    #     "Neutral": "create_video/icons/neutral.png",
    #     "Heart": "create_video/icons/heart_icon.png",
    #     "GSR": "create_video/icons/GSR.png",
    #     "Pupil": "create_video/icons/pupil.png",
    # }
    # takeout medium column from data_with_peaks
    data = pd.read_csv(data_with_peaks)
    mediums = data["Medium"].unique()
    check_content(content, mediums)

    # set paramters for video
    frame_width = 1920
    frame_height = 1080
    fps = 30

    # Load the icons and resize them
    icon_size = 60

    for key in icons:
        # Load the icon with its alpha channel
        icon = cv2.imread(icons[key], cv2.IMREAD_UNCHANGED)
        # Resize the icon, preserving transparency
        icon = cv2.resize(icon, (icon_size, icon_size), interpolation=cv2.INTER_AREA)

        # Normalize the alpha channel to [0, 1] range
        alpha_mask = icon[:, :, 3] / 255.0
        # Compute the inverse alpha mask
        inverse_alpha_mask = 1 - alpha_mask

        # Store the resized icon, its alpha mask, and inverse alpha mask together
        icons[key] = {
            "image": icon[:, :, :3],  # RGB channels of the icon
            "alpha_mask": alpha_mask,  # Normalized alpha mask for blending
            "inverse_alpha_mask": inverse_alpha_mask,  # Inverse of the alpha mask
        }

    graph_height = 0
    # load the graph
    if graph:
        graph_height = 150
        graph_image = cv2.imread(graph_file, cv2.IMREAD_UNCHANGED)
        graph_image = cv2.resize(graph_image, (frame_width, graph_height))

        # precalculate alpha mask for the graph
        graph_alpha = graph_image[:, :, 3] / 255.0
        # make only have 3 channels
        graph_rgb = graph_image[:, :, :3]

    # split icons into emoji and last 3 as sensor icons
    sensor_icons = {key: icons[key] for key in list(icons.keys())[10:]}
    emoji_icons = {key: icons[key] for key in list(icons.keys())[:10]}

    start_x = frame_width - 5 * icon_size
    start_y = frame_height - 2 * icon_size - graph_height

    # Take out the time and the x and y coordinates
    time = data["Time"]
    # make another column for time that is continuous empty array
    time_continuous = [0.0]  # Initialize the first element to 0 as specified

    # Iterate over the 'Time' column, starting from the second row (index 1)
    time_diffrence = time[1] - time[0]
    for i in range(1, len(data)):
        # Add the current time to the previous continuous time and append to the list
        time_continuous.append((time_diffrence) + time_continuous[-1])
    # set single participant as first entry
    Participant = data["Participant"][0]
    Medium = data["Medium"]
    if eye_tracking:
        x = data["Eye_X"]
        y = data["Eye_Y"]
    if Pupil:
        pupil = data["DilatedPupil"]
        pupil_peaks = data["PupilPeaks"]
    if GSR:
        conductance = data["GSR"]
        conductance_peaks = data["GSRPeaks"]
    if HeartRate:
        heart_rate = data["HR"]
        heart_rate_peaks = data["HRPeaks"]
    if FACET:
        # load the FACET data
        facet = data[
            [
                "Joy",
                "Anger",
                "Surprise",
                "Fear",
                "Disgust",
                "Sadness",
                "Contempt",
                "Frustration",
                "Confusion",
                "Neutral",
            ]
        ]

    # change all content into VideoCapture or MatLike
    for key in content:
        # if video then change to VideoCapture
        if ".mp4" in content[key]:
            # print(content[key] + "video")
            content[key] = cv2.VideoCapture(content[key])
            # fps = content[key].get(cv2.CAP_PROP_FPS)
            # print(f"Video {key} FPS: {fps}")

        # if image then change to MatLike
        elif ".jpg" in content[key]:
            # keep te image transparent
            content[key] = cv2.imread(content[key], cv2.IMREAD_UNCHANGED)
            # resize
            content[key] = center_content_on_background(content[key])

        elif ".png" in content[key]:
            # keep te image transparent
            img_with_alpha = cv2.imread(content[key], cv2.IMREAD_UNCHANGED)
            # Convert the image to 3 channels by discarding the alpha channel
            img_rgb = img_with_alpha[:, :, :3]
            # resize
            content[key] = center_content_on_background(img_rgb)

    # Create a video writer object
    if save:
        # check if the video is already created and ask the user if they want to overwrite it
        if os.path.exists(f"{Participant}_overlayed_video.mp4"):
            # overwrite = input("Do you want to overwrite the video? (yes or no): ")
            overwrite = "yes"
            if overwrite == "no":
                return
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            f"{Participant}_overlayed_video.mp4",
            fourcc,
            30,
            (frame_width, frame_height),
        )

    print("Creating video...")
    keep_red_tint_on = False
    last_successful_frame = None
    red_tint_counter = 0
    frame_delay = 1.0 / fps
    global_time = 0
    total_time = time_continuous[-1] * 1e6
    print(f"Total time: {total_time:.2f} seconds")
    # continue to go through the loop as long as global time does not go over the total time
    while global_time < total_time:
        print(f"{global_time:.2f}")
        # set to data the is closest to the global time
        i = np.argmin(np.abs(np.array(time_continuous) * 1e6 - global_time))
        medium = content[Medium[i]]
        # check if medium is a video or an image
        if type(medium) == cv2.VideoCapture:
            ret, frame = medium.read()
            if not ret:
                print(f"Error: Could not read frame {i} from video file.")
                if last_successful_frame is not None:
                    frame = (
                        last_successful_frame.copy()
                    )  # Use the last successful frame if read fails
                else:
                    # Handle the case where the very first frame read fails
                    print(
                        "Error: No frames have been successfully read from this video."
                    )
                    continue  # Skip further processing for this iteration
            else:
                frame = center_content_on_background(frame)
                last_successful_frame = frame.copy()  # Update the last successful frame
        else:
            try:
                frame = (
                    medium.copy()
                )  # This assumes 'medium' is an image, so we just use it directly
            except:
                print(f"Image Medium {Medium[i]} not found.")
                return  # This assumes 'medium' is an image, so we just use it directly

        if eye_tracking:
            # Overlay the x and y coordinates on the image

            # If the x or y coordinate is NaN or less than 0, don't display it
            if np.isnan(x[i]) or np.isnan(y[i]) or x[i] < 0 or y[i] < 0:
                last_time = time[i]
                continue

            adjusted_x = int(x[i] * 0.5)  # Scaling factor for x coordinate
            adjusted_y = int(y[i] * 0.5)  # Scaling factor for y coordinate

            # Optionally, adjust the dot size. Here, we use a radius of 3 for the smaller image
            frame = cv2.circle(
                frame.copy(), (adjusted_x, adjusted_y), 3, (0, 0, 255), -1
            )

        if GSR:
            # put GSR icon and value on the image
            # load the GSR icon
            gsr_icon = sensor_icons["GSR"]
            # place the GSR icon on the image in bottem left corner
            place_icon_at_position(
                frame, gsr_icon, 0, frame_height - icon_size - graph_height, icon_size
            )
            # place the GSR value in the bottem left corner
            cv2.putText(
                frame,
                f"{round(conductance[i],2)}",
                (50, frame_height - 20 - graph_height),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # print(conductance_peaks[i])
            # apply red tint to the image

            # if conductance_peaks[i] > 0 or keep_red_tint_on:
            #     frame = apply_red_tint(frame, conductance_peaks[i])
            #     keep_red_tint_on = True
            #     red_tint_counter += 1
            #     if red_tint_counter > 30:
            #         keep_red_tint_on = False
            #         red_tint_counter = 0

        # Modify the FACET part within the loop to arrange icons on the background and overlay it on the frame
        if FACET:
            # inicilize blank previous coloration values
            previous_coloration_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # Assuming 'i' is the index for the current frame
            facet_values = data.loc[
                i,
                [
                    "Joy",
                    "Anger",
                    "Surprise",
                    "Fear",
                    "Disgust",
                    "Sadness",
                    "Contempt",
                    "Frustration",
                    "Confusion",
                    "Neutral",
                ],
            ].values
            for idx, (emotion, icon_data) in enumerate(emoji_icons.items()):
                row, col = divmod(idx, 5)
                icon_pos_y, icon_pos_x = (
                    start_y + row * icon_size,
                    start_x + col * icon_size,
                )

                # Retrieve the coloration value for the current icon/emotion
                coloration = facet_values[
                    idx
                ]  # Assuming the order of facet_values matches the emoji_icons order

                # if coloration is NaN, set it to 0
                if np.isnan(coloration):
                    # previous coloration
                    coloration = previous_coloration_values[idx]
                else:
                    previous_coloration_values[idx] = coloration

                # Place the icon with the appropriate coloration
                place_icon_at_position(
                    frame,
                    icon_data,
                    icon_pos_x,
                    icon_pos_y,
                    icon_size,
                    coloration=coloration,
                )

        if Pupil:
            # overlay the pupil icon on the image
            # load the pupil icon
            pupil_icon = sensor_icons["Pupil"]
            # place the pupil icon on the image in top left corner
            place_icon_at_position(frame, pupil_icon, 0, 0, icon_size)
            # place the pupil size in the rectangle
            cv2.putText(
                frame,
                f"{round(pupil[i],2)}",
                (60, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if HeartRate:
            # overlay the heart rate on the image
            # create a gray rectangle on the image in the top right corner with the heart rate
            # load the heart icon
            heart_icon = sensor_icons["Heart"]
            place_icon_at_position(
                frame, heart_icon, frame_width - icon_size - 40, 0, icon_size
            )
            # place the heart rate in the rectangle
            cv2.putText(
                frame,
                f"{heart_rate[i]}",
                (frame_width - 50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if graph:
            # overlay the graph on the image
            # Calculate the position for the graph at the bottom
            bottom_left_y = frame_height - graph_height

            # Overlay the graph on the image
            for c in range(0, 3):  # Iterate through color channels
                frame[bottom_left_y : bottom_left_y + graph_height, :, c] = (
                    graph_alpha * graph_rgb[:, :, c]
                    + (1 - graph_alpha)
                    * frame[bottom_left_y : bottom_left_y + graph_height, :, c]
                )
            # define orange color
            orange = (0, 165, 255)

            # Place line on the graph (indicating current frame/time)
            current_frame_x = int(global_time / total_time * frame_width)
            cv2.line(
                frame,
                (current_frame_x, bottom_left_y),
                (current_frame_x, bottom_left_y + graph_height),
                orange,
                2,
            )
        if show:
            # Specify the size you want for the display
            display_width = 980  # Example width
            display_height = 580  # Example height, maintaining the aspect ratio

            # Resize the frame for display
            display_frame = cv2.resize(frame, (display_width, display_height))

            # Show the resized frame
            cv2.imshow("Medium", display_frame)
            cv2.waitKey(1)

            # Wait for the frame delay to simulate real-time playback
            if cv2.waitKey(int((frame_delay * 1000) / 2)) & 0xFF == ord("q"):
                break

        # wait for input to move to the next step by displaying the x and y coordinates
        if False:
            print(f"x_resized: {x[i]}, y_resized: {y[i]}")
            cv2.waitKey(0)

        global_time += frame_delay

        if True:
            # display the time in the bottem center
            cv2.putText(
                frame,
                f"{global_time:.2f}",
                (frame_width // 2, frame_height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if save:
            out.write(frame)

    # Close the window
    cv2.destroyAllWindows()


# test function
if __name__ == "__main__":
    #     ['Vid0' 'PupilMeasure_dot' 'JG_1226-lo_denim_resize' 'SAM Two Dimensions0'
    #  'Vid1' 'PupilMeasure_dot-1' 'MR1_0132-lo_denim_resize'
    #  'SAM Two Dimensions1' 'Vid2 with Alarm' 'PupilMeasure_dot-2'
    #  'JS_0744-lo_denim_resize' 'SAM Two Dimensions2']
    content = {
        "Vid0": "Kellie_Study/content/vid0.mp4",
        "JG_1226-lo_denim_resize": "Kellie_Study/content/JG_1226-lo_denim_neutral.jpg",
        "PupilMeasure_dot": "Kellie_Study/content/PupilMeasure_dot.jpg",
        "SAM Two Dimensions0": "Kellie_Study/content/SAM_Two_Dimensions_0.png",
        "Vid1": "Kellie_Study/content/vid1.mp4",
        "PupilMeasure_dot-1": "Kellie_Study/content/PupilMeasure_dot.jpg",
        "MR1_0132-lo_denim_resize": "Kellie_Study/content/MR1_0132-lo_denim_positive.jpg",
        "SAM Two Dimensions1": "Kellie_Study/content/SAM_Two_Dimensions_1.png",
        "Vid2 with Alarm": "Kellie_Study/content/Vid2_with_Alarm.mp4",
        "PupilMeasure_dot-2": "Kellie_Study/content/PupilMeasure_dot.jpg",
        "JS_0744-lo_denim_resize": "Kellie_Study/content/JS_0744-lo_denim_negative.jpg",
        "SAM Two Dimensions2": "Kellie_Study/content/SAM_Two_Dimensions_2.png",
    }

    data_with_peaks = "Kellie_Study/results/participants_peaks/0_with_peaks.csv"

    overlay_video(
        data_with_peaks,
        content,
        graph_file="Kellie_Study/results/participants_peak_graph/0_peak_graph.png",
        GSR=True,
        FACET=True,
        Pupil=True,
        HeartRate=True,
        graph=True,
        save=True,
        show=True,
        eye_tracking=True,
    )
