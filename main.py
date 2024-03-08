# Main script that will run the program on a folder of documents
from process_data_Kellie import process_data_Kellie, break_data
from process_peaks import append_peaks
from video_overlay import overlay_video
from create_peaks_graph import plot_peak_graph


def main():
    """
    Input:
        Define files for sensor data sets and a dictionary for the content
    Output:
        Video of sensors overlayed on content
    """

    # Define all the datasets and content currently being worked with
    eye_tracked_data = "Kellie_Study/Aligned_ET-data_combined.csv"
    GSR_data = (
        "Kellie_Study/Aligned_GSR_data_combined.csv"  # contains both GSR and HR data
    )
    FACET_data = "Kellie_Study/Aligned_FACET_data_combined.csv"
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

    # run a cleaning script that returns path to file of cleaned data in the form of
    # time, conductance, x, y coordinates, pupil size, heart rate, Each FACET of a single respondent over their time
    # cleaned_data = process_data_Kellie(eye_tracked_data, GSR_data, FACET_data)
    cleaned_data = "Kellie_Study/results/cleaned_sensors.csv"

    # #break apart for each respondent their sensor data
    respondent = break_data(cleaned_data, clean_time=True)

    print("Data Broken apart")

    ind = 0
    for individual in respondent:
        # append on the peak values by adding peakPupil, peakConductance, peakHeartRate
        individual = append_peaks(ind, individual, stdPupil=1, stdGSR=2, stdHeartRate=1)
        ind += 1

        # create peaks graph
        individual_graph = plot_peak_graph(
            results_folder="Kellie_Study/results",
            respondent_file=individual,
            gsr=True,
            heart=True,
            pupil=True,
        )

        # Creation of overlayed data on the content
        # overlayed_video = overlay_video(
        #     individual,
        #     content,
        #     graph_file=individual_graph,
        #     GSR=True,
        #     FACET=True,
        #     Pupil=True,
        #     HeartRate=True,
        #     graph=True,
        #     save=True,
        #     show=False,
        #     eye_tracking=False,
        # )


if __name__ == "__main__":
    main()
