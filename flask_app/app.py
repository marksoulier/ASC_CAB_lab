from flask import Flask, render_template, request, send_file
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "templates"),
    static_folder=os.path.join(os.getcwd(), "static"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files["file"]
    if uploaded_file:
        file_path = os.path.join("uploads", uploaded_file.filename)
        uploaded_file.save(file_path)
        return f'File "{uploaded_file.filename}" uploaded successfully.'
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


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
