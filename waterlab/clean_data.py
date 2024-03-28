import csv
import pandas as pd
import warnings
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def format_number(x):
    if x < 0:
        formatted = "{:09.2f}".format(-x) + "-"
    else:
        formatted = "{:010.3f}".format(x)
    return formatted


def process_date(data_file):
    data = pd.read_csv(data_file, sep="\t", header=None)
    data.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    data = data[
        (data["G"] != 0)
        & (data["H"] != 0)
        & (data["I"] != 0)
        & (data["J"] != 0)
        & (data["K"] != 0)
    ]
    data = data.drop("G", axis=1)
    new_data = pd.DataFrame(columns=["Code", "Anumber", "integer", "time", "date"])
    iterate = ["C", "D", "E", "F"]
    rows_to_append = []

    for index, row in data.iterrows():
        for char in iterate:
            rows_to_append.append(
                {
                    "Code": row["A"],
                    "Anumber": row["B"],
                    "integer": row[char],
                    "time": row[
                        (
                            "H"
                            if char == "C"
                            else "I" if char == "D" else "J" if char == "E" else "K"
                        )
                    ],
                    "date": row["L"],
                }
            )

    rows_to_append_df = pd.DataFrame(rows_to_append)
    new_data = pd.concat([new_data, rows_to_append_df], ignore_index=True)
    new_data["date"] = pd.to_datetime(new_data["date"]).dt.strftime("%m/%d/%Y")
    new_data["time"] = new_data["time"].apply(format_number)
    new_data = new_data.sort_values(by="integer")
    # put filename + .dat
    fi = data_file.split("/")[-1].split(".")[0] + ".dat"
    new_data.to_csv(fi, sep="\t", header=False, index=False, encoding="cp1252")


def select_file():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    return filename


if __name__ == "__main__":
    data_file = select_file()
    if data_file:  # Proceed only if a file was selected
        process_date(data_file)
    else:
        print("No file selected.")
