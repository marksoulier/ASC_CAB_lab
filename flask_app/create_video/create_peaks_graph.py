import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Use the Anti-Grain Geometry non-GUI backend suited for scripts
import matplotlib.pyplot as plt
import os


def plot_peak_graph(
    results_folder,
    respondent_file,
    gsr=True,
    heart=True,
    pupil=True,
):
    # Read the CSV file
    data = pd.read_csv(respondent_file)
    # Extract the Time, PupilPeaks,GSRPeaks,HRPeaks
    time = data["Time"]  # Time
    GSR_peaks = data["GSRPeaks"]  # GSR Peaks
    HR_peaks = data["HRPeaks"]  # Heart Rate Peaks
    Pupil_peaks = data["PupilPeaks"]  # Pupil Peaks

    # extract the last value of the time
    last_time = time.iloc[-1]

    # Create a figure and axes for the graph
    fig, ax = plt.subplots(figsize=(8, 2))  # Set the figure size as needed

    # Set the background color of the plot
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # plot each of the peaks on the graph for each sensor
    if gsr:
        GSR_peaks = GSR_peaks * 100
        ax.plot(time, GSR_peaks, color="tan", label="GSR Peaks")
    if heart:
        HR_peaks = HR_peaks * 100
        ax.plot(time, HR_peaks, color="red", label="HR Peaks")
    if pupil:
        Pupil_peaks = Pupil_peaks * 100
        ax.plot(time, Pupil_peaks, color="blue", label="Pupil Peaks")

    # Set the title, x-axis label, and y-axis label
    ax.set_title("")  # Set an empty title
    ax.set_xlabel("")  # Remove x-axis label
    ax.set_ylabel("")  # Remove y-axis label
    ax.set_yticks([])  # Remove y-axis scale
    ax.set_xticks([])  # Remove x-axis scale
    # Set x-axis limits from 0 to 105
    ax.set_xlim(0, last_time)
    # file save location
    # find the respondent number be seraching for the integer in the file name
    respondent_number = [int(s) for s in respondent_file if s.isdigit()][0]

    if not os.path.exists(f"{results_folder}/participants_peak_graph"):
        os.makedirs(f"{results_folder}/participants_peak_graph")

    file_save_location = (
        f"{results_folder}/participants_peak_graph/{respondent_number}_peak_graph.png"
    )
    # Save the plot as an image with 0 padding around the edges and no graph border
    plt.savefig(file_save_location, bbox_inches="tight", pad_inches=0, transparent=True)

    # Close the plot to free up memory
    plt.close()

    return file_save_location


# test the peak function
if __name__ == "__main__":
    plot_peak_graph(
        results_folder="Kellie_Study/results",
        respondent_file="Kellie_Study/results/participants_peaks/0_with_peaks.csv",
        gsr=True,
        heart=True,
        pupil=True,
    )
