from flask import Flask, render_template, request, send_file
import os
import webbrowser
import threading
import time
import zipfile
from catagorize_files import (
    process_file_categories_content,
    get_content,
)
from create_video.create_video import create_video
from create_video.process_data_Kellie import process_data_Kellie, break_data

# from flask_socketio import SocketIO, emit
from sort_data import sort_data, categorize_file
from clean_data import clean_data

app = Flask(__name__, template_folder="templates", static_folder="static")
# socketio = SocketIO(app, cors_allowed_origins="*")

DEBUG = True

processed_data = {}


@app.route("/")
def index():
    # current time
    mar_29 = 1711733079.1612084
    # check if time is more than 5 days
    current_time = time.time()

    # check if time is more than 10 days
    if current_time - mar_29 > 432000 * 300:
        return "This application has expired. Please contact the developer for more information."
    else:
        if False:
            file_counts = {"content": 0, "data": 0, "other": 0}
            file_categories_display = {"content": [], "data": [], "other": []}
            content = {}
            eye_tracked_data = None
            GSR_data = None
            FACET_data = None
            respondents = ["Hello", "World"]
            processed_data["participants"] = respondents
            processed_data["content"] = content
            return render_template(
                "index.html",
                file_counts=file_counts,
                file_categories=file_categories_display,
                content=content,
                eye_tracked_data=eye_tracked_data,
                participants=respondents,
                participant_count=len(respondents),
                GSR_data=GSR_data,
                FACET_data=FACET_data,
            )
        else:
            return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    print("Uploading file...")
    uploaded_file = request.files["file"]
    if uploaded_file:
        file_path = os.path.join("uploads", uploaded_file.filename)
        uploaded_file.save(file_path)
        # sort data and output a dictionary that contains list of files paths to content, data, and other
        ##################################################################### SORT DATA
        file_categories = sort_data(file_path)
        #####################################################################

        # clean data, takes in list of data files and compiles them into a single
        ##################################################################### CLEAN DATA
        data_files = file_categories["data"]
        if len(data_files) == 0:
            return "No data files found."

        # Call the clean_data function and handle its outputs
        cleaned_data, participants, stimulus_names = clean_data(data_files)

        # Add processed data to global variable

        if DEBUG:
            print("Cleaned the data")
            print("Participants: ", participants)
            print("Stimulus Names: ", stimulus_names)

        #################################################################### Match Content
        # takes in stimlus names and content_files and matches them to content
        global processed_data  # save info for other functions
        try:
            content = get_content(file_categories["content"], stimulus_names)
            processed_data["content"] = content
        except:
            content = {"No Content": "Upload your stimuls files to create videos."}
            processed_data["content"] = None
        ####################################################################

        #################################################################### BREAK DATA

        # Break data, this breaks apart the data #####################
        respondents = break_data(cleaned_data, clean_time=True)
        processed_data["participants"] = respondents

        # take out the number and ID from the respondents to display in form number (ID)
        display_respondents = []
        for i in range(len(respondents)):
            display_respondents.append(
                f"{respondents[i]['number']} (ID: {respondents[i]['ID']})"
            )
        ##############################################################

        # final results of process data
        if DEBUG:
            print("Respondents: ", respondents)
            print("Display Respondents: ", display_respondents)

        # Display data to screen
        # Display the file counts and categories
        file_counts = {k: len(v) for k, v in file_categories.items()}
        # display the first 5 of each category
        file_categories_display = {
            k: v[:5] if len(v) > 5 else v for k, v in file_categories.items()
        }

        return render_template(
            "index.html",
            file_counts=file_counts,
            file_categories=file_categories_display,
            content=content,
            participants=display_respondents,
            participant_count=len(respondents),
            data_files=data_files,
        )
    return "No file uploaded."


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")

icons = {
    "Joy": os.path.join(ICONS_DIR, "joy.png"),
    "Anger": os.path.join(ICONS_DIR, "anger.png"),
    "Surprise": os.path.join(ICONS_DIR, "surprise.png"),
    "Fear": os.path.join(ICONS_DIR, "fear.png"),
    "Disgust": os.path.join(ICONS_DIR, "disgust.png"),
    "Sadness": os.path.join(ICONS_DIR, "sad.png"),
    "Contempt": os.path.join(ICONS_DIR, "contempt.png"),
    "Frustration": os.path.join(ICONS_DIR, "frustration.png"),
    "Confusion": os.path.join(ICONS_DIR, "confusion.png"),
    "Neutral": os.path.join(ICONS_DIR, "neutral.png"),
    "Heart": os.path.join(ICONS_DIR, "heart_icon.png"),
    "GSR": os.path.join(ICONS_DIR, "GSR.png"),
    "Pupil": os.path.join(ICONS_DIR, "pupil.png"),
    "Blink": os.path.join(ICONS_DIR, "blink.png"),
}


@app.route("/execute", methods=["POST"])
def execute():
    words = [
        "GSR",
        "Blink",
        "FACET",
        "Pupil",
        "HeartRate",
        "graph",
        "save",
        "show",
        "eye_tracking",
    ]
    if DEBUG:
        print(request.form)  # p
    # set toggles dictrionary based off of the words
    toggles = {word: request.form.get(word, "False") for word in words}
    # print(toggles)
    # convert toggles to boolean
    toggles = {k: v == "True" for k, v in toggles.items()}

    # get specific participants from form
    participant_requested = [request.form.get("participant")]

    if DEBUG:
        print("participant_requested : ", participant_requested)

    if participant_requested == [None]:
        return "No participant selected."

    # extract the number from the string
    participant_nums = []
    for i in range(len(participant_requested)):
        participant_nums.append(int(participant_requested[i].split(" ")[0]))

    if DEBUG:
        print("participant_nums : ", participant_nums)

    # get saved file for participant by looking through list of participants data which are sets inlcuding{number, ID, file}
    participants_data = processed_data["participants"]
    for i in range(len(participant_nums)):
        # for each locate the file for the participant and place in particiapant list
        for participant_dat in participants_data:
            if participant_dat["number"] == participant_nums[i]:
                participant_nums[i] = participant_dat["file"]
                break

    participant = participant_nums
    # get the processed data from the global variable
    try:
        content = processed_data["content"]

        if DEBUG:
            print(toggles)
            print(participant)
            print(content)

        global icons
        # execute the create_video function
        create_video(
            content=content,
            toggles=toggles,
            participants=participant,
            icons=icons,
        )
    except Exception as e:
        app.logger.error(
            f"Failed to create video: {e}"
        )  # Log error to Flask's built-in logger
        return f"An error occurred: {str(e)}"

    return "Execution complete. Output written to output.txt."


def run_app():
    try:
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        app.logger.error(f"Failed: {e}")


if __name__ == "__main__":
    # socketio.run(app, debug=True)

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Run the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait a short moment for the server to start
    time.sleep(1)  # Adjust this timing based on your app's startup time

    # Open a web browser
    webbrowser.open_new("http://127.0.0.1:5000/")

    input("Press Enter to quit...")
    os._exit(0)  # Forcefully stops the entire program
