import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os


def process_data_Kellie(eye_tracked_data, GSR_data, FACET_data):
    """
    Args:
        raw_data: data file that I am working with
    Returns:
        cleaned_data: location of file with cleaned data

    """
    # Load the CSV file using pandas
    eye_data = pd.read_csv(eye_tracked_data)
    GSR_data = pd.read_csv(GSR_data)
    FACET_data = pd.read_csv(FACET_data)
    # Get the column names
    # column_names = GSR_data.columns.tolist()

    # # Print the column names
    # for column in column_names:
    #     print(column)
    # extract the time, Cal VsenseBatt (Shimmer Sensor), GazeLeftx, GazeLefty, GazeRightx, GazeRighty, pupilLeft, pupilRight

    # print the first 5 rows of the data for each
    # print(time.head())
    # print(cal_vsensebatt.head())
    # print(x_left.head())
    # print(y_left.head())
    # print(x_right.head())
    # print(y_right.head())
    # print(l_pupil.head())
    # print(r_pupil.head())
    time = eye_data["AlignedTimeSec"]
    Participant = eye_data["ID"]
    Medium = eye_data["SlideEvent"]
    DilatedPupil_Left = eye_data["ET_PupilLeft"]
    DilatedPupil_Right = eye_data["ET_PupilRight"]
    # if left or right eye is 0 then use the other eye else average the two eyes
    DilatedPupil = np.where(
        DilatedPupil_Left == 0,
        DilatedPupil_Right,
        np.where(
            DilatedPupil_Right == 0,
            DilatedPupil_Left,
            (DilatedPupil_Left + DilatedPupil_Right) / 2,
        ),
    )
    GSR_ = GSR_data["GSR"]
    HR_ = GSR_data["HR"]
    Joy = FACET_data["Joy"]
    Anger = FACET_data["Anger"]
    Surprise = FACET_data["Surprise"]
    Fear = FACET_data["Fear"]
    Disgust = FACET_data["Disgust"]
    Sadness = FACET_data["Sadness"]
    Contempt = FACET_data["Contempt"]
    Frustation = FACET_data["Frustration"]
    Confusion = FACET_data["Confusion"]
    Neutral = FACET_data["Neutral"]

    # add in eye tracking data with x, y positions that are set to 0 for entire time
    x = np.zeros(len(time))
    y = np.zeros(len(time))

    # create df with the time, conductance, dilation, GSR, HR, and FACET
    df = pd.DataFrame(
        {
            "Participant": Participant,
            "Medium": Medium,
            "Time": time,
            "DilatedPupil": DilatedPupil,
            "GSR": GSR_,
            "HR": HR_,
            "Eye_X": x,
            "Eye_Y": y,
            "Joy": Joy,
            "Anger": Anger,
            "Surprise": Surprise,
            "Fear": Fear,
            "Disgust": Disgust,
            "Sadness": Sadness,
            "Contempt": Contempt,
            "Frustration": Frustation,
            "Confusion": Confusion,
            "Neutral": Neutral,
        }
    )
    # current directory
    current_dir = os.getcwd()
    save_file = os.path.join(current_dir, "results/cleaned_sensors.csv")
    # if results folder does not exist create it
    if not os.path.exists("results"):
        os.makedirs("results")

    df.to_csv(save_file, index=False)
    return save_file


def break_data(cleaned_data_path, clean_time=False):
    """
    Args:
        cleaned_data_path: File path to the cleaned data CSV with all the participants
        clean_time: Boolean indicating whether to convert time to continuous for each participant
    Returns:
        respondents_file: List of file locations for each respondent's data
    """
    # Load the CSV file using pandas
    cleaned_data = pd.read_csv(cleaned_data_path)

    # get the unique participants
    unique_participants = cleaned_data["Participant"].unique()

    # Initialize an empty list to store the modified DataFrame for each participant
    modified_data_frames = []

    for participant in unique_participants:
        # Extract data for the current participant
        participant_data = cleaned_data[
            cleaned_data["Participant"] == participant
        ].copy()

        if clean_time:
            # clean time to be continuous for this participant
            time = participant_data["Time"]
            time_diffrence = time.iloc[1] - time.iloc[0]
            time_continuous = [time.iloc[0]]
            for i in range(1, len(time)):
                # Add the current time to the previous continuous time and append to the list
                time_continuous.append((time_diffrence) + time_continuous[-1])
            # set time to the continuous time
            time = np.array(time_continuous)

            # set time to be in the cleaned data
            participant_data["Time"] = time

        modified_data_frames.append(participant_data)

    # current directory
    current_dir = os.getcwd()
    save_dir = os.path.join(current_dir, "results/participants")
    # if results folder does not exist create it
    if not os.path.exists("results/participants"):
        os.makedirs("results/participants")

    respondents_file = []
    # save the df of each respondent to a new csv file
    for i, df in enumerate(modified_data_frames):
        save_file = os.path.join(save_dir, f"{i}_respondent_data.csv")
        df.to_csv(save_file, index=False)
        respondents_file.append(save_file)

    return respondents_file
