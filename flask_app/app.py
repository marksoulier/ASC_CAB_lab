from flask import Flask, render_template, request, send_file
import os
import webbrowser
import threading
import time
import zipfile
from catagorize_files import categorize_file, process_file_categories_content

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
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
        # print("Content: ", content)

        return render_template(
            "index.html",
            file_counts=file_counts,
            file_categories=file_categories_display,
        )
    return "No file uploaded."


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
