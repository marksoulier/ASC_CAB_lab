import csv
import pandas as pd
import warnings

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def format_number(x):
    # Check if the number is negative
    if x < 0:
        # Format the number without the minus sign and add '-' at the end
        # Also, ensure it has 6 leading digits, 1 digit after the decimal, followed by 0 and a minus sign.
        # The total width before the decimal is increased to account for the absence of a minus sign at the front.
        formatted = "{:08.2f}".format(-x) + "-"
    else:
        # Format positive numbers as before
        formatted = "{:09.3f}".format(x)
    return formatted


def process_date(data_file):
    # load the txt file which is tab delimited into a pd dataframe
    data = pd.read_csv(data_file, sep="\t", header=None)

    # put header names for each column
    data.columns = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
    ]

    # clean the data
    # if columns G,H,I,K,J,K are zero take out the row
    data = data[
        (data["G"] != 0)
        & (data["H"] != 0)
        & (data["I"] != 0)
        & (data["J"] != 0)
        & (data["K"] != 0)
    ]

    # remove column G
    data = data.drop("G", axis=1)

    # make new data frame with columns Anumber, integer, time, date
    new_data = pd.DataFrame(columns=["Code", "Anumber", "integer", "time", "date"])

    iterate = ["C", "D", "E", "F"]
    rows_to_append = []

    for index, row in data.iterrows():
        for char in iterate:
            # Append row data to rows_to_append list
            rows_to_append.append(
                {
                    "Code": row["A"],
                    "Anumber": row["B"],
                    "integer": int(row[char]),
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

    # Convert the list of dicts to a DataFrame
    rows_to_append_df = pd.DataFrame(rows_to_append)

    # Concatenate the new DataFrame with the original one
    new_data = pd.concat([new_data, rows_to_append_df], ignore_index=True)

    # Format the 'date' column to MM/DD/YYYY
    new_data["date"] = pd.to_datetime(new_data["date"]).dt.strftime("%m/%d/%y")

    # Apply custom formatting to 'time' column
    new_data["time"] = new_data["time"].apply(format_number)

    # Sort the DataFrame by 'integer'
    new_data = new_data.sort_values(by="integer")

    # Output to a tab-delimited file with ANSI encoding
    new_data.to_csv(
        "output.dat", sep="\t", header=False, index=False, encoding="cp1252"
    )


if __name__ == "__main__":
    data_file = "Feb_wk4_raw.txt"
    process_date(data_file)
