"""This script is for functions that clean any data files into a single standardizzed cleaned data file that compiles all  important sensor data for each participant."""

import pandas as pd
from catagorize_files import assign_best_matches
import os

DEBUG = True


def clean_data(data_files):
    """
    Takes in data files and compiles them into a single cleaned data file.
    Returns the cleaned data, a list of participants, and a list of stimulus names.
    """
    if not data_files:
        return "No data files found.", None, None

    sensor_categories = {
        "Participant": ["Participant_ID", "Participant", "ID", "Respondent"],
        "Medium": ["Medium", "StimulusLabel", "SourceStimuliName", "SlideEvent"],
        "Time": ["AlignedTimeSec", "Time", "Timestamp", "Time_Stamp"],
        "DilatedPupilRight": [
            "DilatedPupil",
            "Pupil Size",
            "Pupil",
            "ET_PupiLeft",
        ],
        "DilatedPupilLeft": ["DilatiedPupilLeft", "Pupil Size Left", "ET_PupiLeft"],
        "GSR": ["GSR", "Conductance", "Skin Conductance"],
        "HR": ["HR", "Heart Rate"],
        "Blink": ["Blink", "Blinking"],
        "Eye_X": ["Eye_X", "X_Coordinate", "Gaze X"],
        "Eye_Y": ["Eye_Y", "Y_Coordinate", "Gaze Y"],
        "Joy": ["Joy"],
        "Anger": ["Anger"],
        "Surprise": ["Surprise"],
        "Fear": ["Fear"],
        "Disgust": ["Disgust"],
        "Sadness": ["Sadness"],
        "Contempt": ["Contempt"],
        "Frustration": ["Frustration"],
        "Confusion": ["Confusion"],
        "Neutral": ["Neutral"],
    }

    # Initialize a DataFrame to compile cleaned data
    # create df with the time, conductance, dilation, GSR, HR, and FACET
    cleaned_df = pd.DataFrame()

    # Variables to collect participants and stimulus names
    participants = set()
    stimulus_names = set()
    respondent_list = []
    merge_data_flag = False

    if DEBUG:
        print("Data files:", data_files)

    # Iterate through each data file
    for file_path in data_files:
        # aatempt to extract Respondent name
        respondent_name_flag = False
        respondent_name = "Unknown"
        with open(file_path, "r") as file:
            # go through all # starting lines to find the respondent name
            for line in file:
                # if DEBUG:
                # print("Line:", line)
                if line.startswith("#"):
                    if "Respondent Name" in line:
                        respondent_name = line.split(",")[1].strip()
                        respondent_name_flag = True
                        respondent_list.append(respondent_name)
                        # remove participant key from the sensor categories
                        if "Participant" in sensor_categories:
                            del sensor_categories["Participant"]
                        break

        if DEBUG:
            print("Respondent Name:", respondent_name)

        # Load the data file into a DataFrame
        try:
            data = pd.read_csv(file_path, comment="#")
        except:
            print(f"Error reading file: {file_path}")
            continue

        # Finding best matches for the columns in the current data file
        headers = data.columns.tolist()
        best_matches = assign_best_matches(sensor_categories, headers, threshold=80)

        if DEBUG:
            print("Headers:", headers)
            print("Best Matches:", best_matches)
            # input("Press any key to continue...")

        # Prepare data for merging
        data_clean = pd.DataFrame()

        # Check if there is a respondent name in the data set
        if respondent_name_flag:
            data_clean["Participant"] = [respondent_name] * len(data)
        elif (
            "Participant" in best_matches
            and best_matches["Participant"] in data.columns
        ):
            participant_column = data[best_matches["Participant"]].astype(str)
            participant_column = participant_column.apply(
                lambda x: x[:-2] if x.endswith(".0") else x
            )

            # Iterate through unique participants
            for participant in participant_column.unique():
                respondent_list.append(participant)

            # Assign preprocessed participant column to data_clean
            data_clean["Participant"] = participant_column
            merge_data_flag = True  # merge data now that there could be multiple participants in a single file
        else:
            data_clean["Participant"] = "Unknown"

        if "Medium" in best_matches and best_matches["Medium"] in data.columns:
            data_clean["Medium"] = data[best_matches["Medium"]]
            # Add any specific operations for Medium here
        else:
            data_clean["Medium"] = "Unknown"

        if "Time" in best_matches and best_matches["Time"] in data.columns:
            data_clean["Time"] = data[best_matches["Time"]]
        else:
            data_clean["Time"] = pd.NA

        if (
            "DilatedPupilRight" in best_matches
            and best_matches["DilatedPupilRight"] in data.columns
        ):
            if (
                "DilatedPupilLeft" in best_matches
                and best_matches["DilatedPupilLeft"] in data.columns
            ):
                data_clean["DilatedPupil"] = (
                    data[best_matches["DilatedPupilRight"]]
                    + data[best_matches["DilatedPupilLeft"]]
                ) / 2  # average the two pupil sizes
            else:
                data_clean["DilatedPupil"] = data[best_matches["DilatedPupilRight"]]
        else:
            data_clean["DilatedPupil"] = pd.NA

        columns_to_clean = [
            "Time",
            "GSR",
            "HR",
            "Blink",
            "Eye_X",
            "Eye_Y",
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

        for column in columns_to_clean:
            if column in best_matches and best_matches[column] in data.columns:
                data_clean[column] = data[best_matches[column]]
                # Add any specific operations for the column here
            else:
                data_clean[column] = pd.NA

        # Append the clean data to the master DataFrame
        cleaned_df = pd.concat([cleaned_df, data_clean], ignore_index=True)

        # Collect participants and stimulus names from the current file
        if "Participant" in data_clean.columns:
            participants.update(data_clean["Participant"].unique())
        if "Medium" in data_clean.columns:
            stimulus_names.update(data_clean["Medium"].unique())

        if DEBUG:
            print("Respondent List:", respondent_list)

    # write the cleaned data to a csv file and get file_location
    if merge_data_flag:
        cleaned_df = merge_data(cleaned_df)

    current_dir = os.getcwd()
    results_dir = os.path.join(current_dir, "results")
    cleaned_data_path = os.path.join(results_dir, "cleaned_data.csv")

    # if results folder does not exist create it
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # save the cleaned data
    cleaned_df.to_csv(cleaned_data_path, index=False)

    return cleaned_data_path, list(participants), list(stimulus_names)


def merge_data(df):
    """Script that merges sensor data captured about a single participant in order and on the same time scale

    Args:
        df: DataFrame with columns ['Participant', 'Medium', 'Time', 'Dilated', 'GSR', 'HR', 'Blink', 'Eye_X', 'Eye_Y', 'Joy', 'Anger', 'Surprise', 'Fear', 'Disgust', 'Sadness', 'Contempt', 'Frustration', 'Confusion', 'Neutral']
    """
    # Sort the data by participant and time
    df = df.sort_values(by=["Participant", "Time"])

    # Initialize a dictionary to store merged data
    merged_data = {}

    # Iterate through each row
    for index, row in df.iterrows():
        participant = row["Participant"]
        time = row["Time"]
        # Check if participant and time match an existing entry in merged_data
        if (participant, time) in merged_data:
            # Merge the current row with existing merged_data
            for column in df.columns:
                existing_value = merged_data[(participant, time)].get(column)
                new_value = row[column]
                # If both values are not null, handle conflict
                if pd.notnull(existing_value) and pd.notnull(new_value):
                    print(
                        f"Conflict for Participant {participant} at Time {time} in column {column}."
                    )
                # Choose the non-null value
                if pd.isnull(existing_value):
                    merged_data[(participant, time)][column] = new_value
        else:
            # Create a new entry in merged_data
            merged_data[(participant, time)] = row.to_dict()

    # Convert the merged_data dictionary to DataFrame
    merged_df = pd.DataFrame.from_dict(merged_data, orient="index")

    return merged_df


if __name__ == "__main__":
    data_files = ["001_29305.csv", "002_29254.csv"]
    cleaned_data, participants, stimulus_names = clean_data(data_files)
    print("Cleaned Data:")
    print(cleaned_data)
    print("Participants:", participants)
    print("Stimulus Names:", stimulus_names)
