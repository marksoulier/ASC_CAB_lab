import csv
import pandas as pd
import warnings
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import math

DEBUG = False
# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def format_number(x):
    if x < 0:
        formatted = "{:09.2f}".format(-x) + "-"
    else:
        formatted = "{:010.3f}".format(x)
    return formatted


def process_data(data_files):
    aggregated_data = pd.DataFrame(
        columns=["Code", "Anumber", "integer", "time", "date"]
    )

    for data_file in data_files:
        data = pd.read_csv(data_file, sep="\t", header=None)
        data.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        data = data = data[~(data[["G", "H", "I", "J", "K"]] == 0).all(axis=1)]
        iterate = ["C", "D", "E", "F"]
        rows_to_append = []

        for index, row in data.iterrows():
            # inplement specific special cases
            # if column["C"] is a number and column["D"] is a Nan
            if math.isnan(row["D"]) and not math.isnan(row["C"]):
                rows_to_append.append(
                    {
                        "Code": row["A"],
                        "Anumber": row["B"],
                        "integer": int(row["C"]),
                        "time": row["G"],
                        "date": row["L"],
                    }
                )
            # else if column["C"] is a Nan and column["D"] is a number
            elif math.isnan(row["C"]) and not math.isnan(row["D"]):
                rows_to_append.append(
                    {
                        "Code": row["A"],
                        "Anumber": row["B"],
                        "integer": int(row["D"]),
                        "time": row["G"],
                        "date": row["L"],
                    }
                )
            elif (
                math.isnan(row["C"])
                and math.isnan(row["D"])
                and not math.isnan(row["E"])
            ):
                rows_to_append.append(
                    {
                        "Code": row["A"],
                        "Anumber": row["B"],
                        "integer": int(row["E"]),
                        "time": row["G"],
                        "date": row["L"],
                    }
                )
            elif (
                math.isnan(row["C"])
                and math.isnan(row["D"])
                and math.isnan(row["E"])
                and not math.isnan(row["F"])
            ):
                rows_to_append.append(
                    {
                        "Code": row["A"],
                        "Anumber": row["B"],
                        "integer": int(row["F"]),
                        "time": row["G"],
                        "date": row["L"],
                    }
                )
            else:
                print()
                for char in iterate:
                    if math.isnan(row[char]):
                        continue
                    rows_to_append.append(
                        {
                            "Code": row["A"],
                            "Anumber": row["B"],
                            "integer": int(row[char]),
                            "time": row[
                                (
                                    "H"
                                    if char == "C"
                                    else (
                                        "I"
                                        if char == "D"
                                        else "J" if char == "E" else "K"
                                    )
                                )
                            ],
                            "date": row["L"],
                        }
                    )

            if DEBUG:
                print(f"Current File: {data_file}")
                print(f"Current Row: {row}")
                print("Rows to append: ", rows_to_append)
                print("Press any key to continue...")
                input()

        rows_to_append_df = pd.DataFrame(rows_to_append)
        aggregated_data = pd.concat(
            [aggregated_data, rows_to_append_df], ignore_index=True
        )

    aggregated_data["date"] = pd.to_datetime(aggregated_data["date"]).dt.strftime(
        "%m/%d/%y"
    )
    aggregated_data["time"] = aggregated_data["time"].apply(format_number)
    aggregated_data = aggregated_data.sort_values(by="integer")

    if data_files:  # Ensure there is at least one file to name the output after
        output_filename = data_files[0].split("/")[-1].split(".")[0] + "_aggregated.dat"
        aggregated_data.to_csv(
            output_filename, sep="\t", header=False, index=False, encoding="cp1252"
        )
        print(f"Data aggregated and saved to {output_filename}")
    else:
        print("No files processed.")


def select_files():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filenames = askopenfilenames()
    return filenames


if __name__ == "__main__":
    data_files = select_files()
    if data_files:  # Proceed only if files were selected
        process_data(data_files)
    else:
        print("No file selected.")
