import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os


def append_peaks(ind, cleaned_data, stdPupil=2, stdGSR=2, stdHeartRate=2):
    """
    Args:
        Cleaned data file
    Returns:
        Cleaned data file with peaks appended
    """
    # Load the CSV file using pandas
    data = pd.read_csv(cleaned_data)

    # Do the pupil peaks by getting the mean and enter all values Zscore in peak column if greater than std
    pupil = data["DilatedPupil"]
    pupil_mean = pupil.mean()
    pupil_std = pupil.std()
    pupil_zscore = (pupil - pupil_mean) / pupil_std

    # place 0 if not over std and Zscore if over std
    pupil_peaks = np.where(pupil_zscore > stdPupil, pupil_zscore, 0)

    # Do GSR but as a linear model, get residuals and then Zscore and then peaks
    time = data["Time"]
    conductance = data["GSR"]
    model = LinearRegression()
    model.fit(time.values.reshape(-1, 1), conductance.values)
    predicted_conductance = model.predict(time.values.reshape(-1, 1))
    conductance_residuals = conductance - predicted_conductance
    conductance_zscore = (
        conductance_residuals - conductance_residuals.mean()
    ) / conductance_residuals.std()
    conductance_peaks = np.where(conductance_zscore > stdGSR, conductance_zscore, 0)

    # Do the HR by getting the mean and enter all values Zscore in peak column if greater than std
    HR = data["HR"]
    HR_mean = HR.mean()
    HR_std = HR.std()
    HR_zscore = (HR - HR_mean) / HR_std
    HR_peaks = np.where(HR_zscore > stdHeartRate, HR_zscore, 0)

    # append the peaks to the data
    data["PupilPeaks"] = np.abs(pupil_peaks)
    data["GSRPeaks"] = np.abs(conductance_peaks)
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
