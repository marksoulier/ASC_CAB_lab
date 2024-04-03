from flask import Flask, render_template, request, send_file
import os
import webbrowser
import threading
import time
import zipfile
from catagorize_files import (
    categorize_file,
    process_file_categories_content,
    get_content,
)
from create_video.create_video import create_video
from create_video.process_data_Kellie import process_data_Kellie, break_data

app = Flask(__name__, template_folder="templates", static_folder="static")

DEBUG = True

processed_data = {}


@app.route("/")
def index():
    # current time
    mar_29 = 1711733079.1612084
    # check if time is more than 5 days
    current_time = time.time()

    # check if time is more than 5 days
    if current_time - mar_29 > 432000:
        return "The application has expired. Please contact the developer for more information."
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
    uploaded_file = request.files["file"]
    if uploaded_file:
        file_path = os.path.join("uploads", uploaded_file.filename)
        uploaded_file.save(file_path)

        if zipfile.is_zipfile(file_path):
            extracted_dir = os.path.join(
                "uploads", os.path.splitext(uploaded_file.filename)[0]
            )
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                # Extract files to 'uploads' directory
                zip_ref.extractall(
                    os.path.join("uploads", os.path.splitext(uploaded_file.filename)[0])
                )

                file_categories = {"content": [], "data": [], "other": []}
                for file_name in zip_ref.namelist():
                    # Construct the full path for each extracted file
                    full_file_path = os.path.join(extracted_dir, file_name)

                    # Here you can replace 'categorize_file' with the logic to categorize your files
                    category = categorize_file(file_name)
                    # Append the full file path instead of just the file name
                    file_categories[category].append(full_file_path)

                # Display only the first 5 files in each category
                file_categories_display = dict()

                # Limit display to first 5 files in each category
                for category in file_categories:
                    file_categories_display[category] = file_categories[category][:5]

                # Count files in each category
                file_counts = {k: len(v) for k, v in file_categories.items()}
                print("File Categories: ", file_categories)
                print("File Counts: ", file_counts)
        else:
            return "Uploaded file is not a ZIP archive."

        # create storage variabels
        content_names = set()
        participants = set()
        eye_tracked_data, GSR_data, FACET_data = None, None, None

        # process file_catagories data and identify list of content names, list of participants, and return files locations to eye_tracked_data, GSR_data, FACET_data
        content_names, participants, eye_tracked_data, GSR_data, FACET_data = (
            process_file_categories_content(file_categories["data"])
        )
        # get content dictionary that links content names to file locations
        content = get_content(file_categories["content"], content_names)

        print("Content Names: ", content_names)
        print("Participants: ", participants)
        print("Eye Tracked Data: ", eye_tracked_data)
        print("GSR Data: ", GSR_data)
        print("FACET Data: ", FACET_data)
        print("Content: ", content)

        global processed_data
        # Add processed data to global variable
        processed_data["content"] = content

        if DEBUG:
            print("Cleaning the data")
        # clean data and return that it is now cleaned and loaded
        cleaned_data = process_data_Kellie(eye_tracked_data, GSR_data, FACET_data)
        # cleaned_data = "Kellie_Study/results/cleaned_sensors.csv"

        # #break apart for each respondent their sensor data
        respondents = break_data(cleaned_data, clean_time=True)

        processed_data["participants"] = respondents

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
}


@app.route("/execute", methods=["POST"])
def execute():
    words = [
        "GSR",
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
    participant = [request.form.get("participant")]

    if participant == [None]:
        return "No participant selected."

    # get the processed data from the global variable
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
    with open("output.txt", "w") as f:
        for word in words:
            state = request.form.get(word, "False")
            f.write(f"{word}={state}\n")

    return "Execution complete. Output written to output.txt."


def run_app():
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
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
