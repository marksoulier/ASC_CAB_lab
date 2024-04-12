# Main script that will run the program on a folder of documents
from create_video.process_data_Kellie import process_data_Kellie, break_data
from create_video.process_peaks import append_peaks
from create_video.video_overlay import overlay_video
from create_video.create_peaks_graph import plot_peak_graph


def create_video(content, toggles, participants, icons, update_progress):
    """
    Input:
        eye_tracked_data: path to the eye tracking data
        GSR_data: path to the GSR data
        FACET_data: path to the FACET data
        content: dictionary of content names and file locations
        toggles: dictionary of toggles for the video creation
        participants: list of participants to create videos
        icons: dictionary of icons for the video creation
    Output:
        overlayed_video: path to the overlayed video
    """

    # Define all the datasets and content currently being worked with
    # eye_tracked_data = "Kellie_Study/Aligned_ET-data_combined.csv"
    # GSR_data = (
    #     "Kellie_Study/Aligned_GSR_data_combined.csv"  # contains both GSR and HR data
    # )
    # FACET_data = "Kellie_Study/Aligned_FACET_data_combined.csv"
    # content = {
    #     "Vid0": "Kellie_Study/content/vid0.mp4",
    #     "JG_1226-lo_denim_resize": "Kellie_Study/content/JG_1226-lo_denim_neutral.jpg",
    #     "PupilMeasure_dot": "Kellie_Study/content/PupilMeasure_dot.jpg",
    #     "SAM Two Dimensions0": "Kellie_Study/content/SAM_Two_Dimensions_0.png",
    #     "Vid1": "Kellie_Study/content/vid1.mp4",
    #     "PupilMeasure_dot-1": "Kellie_Study/content/PupilMeasure_dot.jpg",
    #     "MR1_0132-lo_denim_resize": "Kellie_Study/content/MR1_0132-lo_denim_positive.jpg",
    #     "SAM Two Dimensions1": "Kellie_Study/content/SAM_Two_Dimensions_1.png",
    #     "Vid2 with Alarm": "Kellie_Study/content/Vid2_with_Alarm.mp4",
    #     "PupilMeasure_dot-2": "Kellie_Study/content/PupilMeasure_dot.jpg",
    #     "JS_0744-lo_denim_resize": "Kellie_Study/content/JS_0744-lo_denim_negative.jpg",
    #     "SAM Two Dimensions2": "Kellie_Study/content/SAM_Two_Dimensions_2.png",
    # }

    # run a cleaning script that returns path to file of cleaned data in the form of
    # time, conductance, x, y coordinates, pupil size, heart rate, Each FACET of a single respondent over their time

    print("Data Broken apart")

    ind = 0
    for individual in participants:

        print("Individual: ", individual)

        print("Appending Peaks")
        # append on the peak values by adding peakPupil, peakConductance, peakHeartRate
        individual = append_peaks(ind, individual, stdPupil=1, stdGSR=1, stdHeartRate=1)
        ind += 1
        update_progress(15)
        print("Creating Peaks Graph")
        # create peaks graph
        individual_graph = plot_peak_graph(
            results_folder="results",
            respondent_file=individual,
            gsr=toggles["GSR"],
            heart=toggles["HeartRate"],
            pupil=toggles["Pupil"],
        )

        print("Overlaying Video")
        # Creation of overlayed data on the content
        overlayed_video = overlay_video(
            individual,
            content,
            graph_file=individual_graph,
            GSR=toggles["GSR"],
            FACET=toggles["FACET"],
            Pupil=toggles["Pupil"],
            HeartRate=toggles["HeartRate"],
            graph=toggles["graph"],
            save=toggles["save"],
            show=toggles["show"],
            eye_tracking=toggles["eye_tracking"],
            icons=icons,
            update_progress=update_progress,
        )

        if ind == 1:
            break


if __name__ == "__main__":
    create_video()
