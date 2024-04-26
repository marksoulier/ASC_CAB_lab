import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

DEBUG = True


def append_peaks(ind, cleaned_data, stdPupil=2, stdGSR=2, stdHeartRate=2):
    """
    Args:
        Cleaned data file
    Returns:
        Cleaned data file with peaks appended
    """
    # Load the CSV file using pandas
    data = pd.read_csv(cleaned_data)
    if DEBUG:
        print("Data Loaded")

    # Do the pupil peaks by getting the mean and enter all values Zscore in peak column if greater than std
    pupil = data["DilatedPupil"]
    pupil_mean = pupil.mean()
    pupil_std = pupil.std()
    pupil_zscore = (pupil - pupil_mean) / pupil_std

    if DEBUG:
        print("Pupil Zscored")

    # place 0 if not over std and Zscore if over std
    pupil_peaks = np.where(pupil_zscore > stdPupil, pupil_zscore, 0)

    model = LinearRegression()
    # Fit the model only on valid GSR data
    valid_data = data.dropna(subset=["GSR"])
    model.fit(valid_data["Time"].values.reshape(-1, 1), valid_data["GSR"].values)

    # Predict conductance for the full time data
    all_predicted_conductance = model.predict(data["Time"].values.reshape(-1, 1))

    # Calculate residuals for valid GSR data
    valid_data["Residuals"] = valid_data["GSR"] - model.predict(
        valid_data["Time"].values.reshape(-1, 1)
    )

    # Merge residuals back to the main data, setting residuals as NaN where GSR was NaN
    data = data.merge(valid_data[["Time", "Residuals"]], on="Time", how="left")

    # Standardize residuals (handle NaN properly by using NaN-safe operations)
    conductance_residuals_mean = data["Residuals"].mean()
    conductance_residuals_std = data["Residuals"].std()
    data["ConductanceZscore"] = (
        data["Residuals"].sub(conductance_residuals_mean).div(conductance_residuals_std)
    )

    # Identify peaks and replace NaN z-scores with None
    data["GSRPeaks"] = np.where(
        data["ConductanceZscore"].abs() > stdGSR,
        np.abs(data["ConductanceZscore"]),
        None,
    )

    if DEBUG:
        print("GSR Zscored")

    # Do the HR by getting the mean and enter all values Zscore in peak column if greater than std
    HR = data["HR"]
    HR_mean = HR.mean()
    HR_std = HR.std()
    HR_zscore = (HR - HR_mean) / HR_std
    HR_peaks = np.where(HR_zscore > stdHeartRate, HR_zscore, 0)

    if DEBUG:
        print("HR Zscored")

    # append the peaks to the data
    data["PupilPeaks"] = np.abs(pupil_peaks)
    data["HRPeaks"] = np.abs(HR_peaks)

    # current directory
    current_dir = os.getcwd()
    save_dir = os.path.join(current_dir, "results/participants_peaks")
    # if results folder does not exist create it
    if not os.path.exists("results/participants_peaks"):
        os.makedirs("results/participants_peaks")

    # save the df to a new csv file
    save_file = os.path.join(save_dir, f"participant_{ind}_peaks.csv")
    data.to_csv(save_file, index=False)

    return save_file
