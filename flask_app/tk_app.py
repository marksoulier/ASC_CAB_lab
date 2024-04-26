import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from clean_data import clean_data
import os


def select_files_and_process():
    try:
        root = tk.Tk()
        root.withdraw()  # we don't want a full GUI, so keep the root window from appearing

        # Show an "Open" dialog box and return the paths to selected files
        filenames = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])

        # Check if any files were selected
        if filenames:
            print(f"Selected files: {filenames}")
            # Call the clean_data function with the selected files
            csv_files = [
                file
                for file in filenames
                if os.path.splitext(file)[1].lower() == ".csv"
            ]

            cleaned_data, participants, stimulus_names = clean_data(csv_files)
            print("Data cleaning complete.")

            # Here you could save the cleaned_data DataFrame to a file
            # cleaned_data.to_csv("path/to/save/cleaned_data.csv", index=False)

            # You can also process participants and stimulus_names as needed
        else:
            print("No files were selected.")
    except Exception as e:
        error_message = f"An error occurred:\n\n{str(e)}\n\nThe process failed."
        messagebox.showerror("Error", error_message)


if __name__ == "__main__":
    select_files_and_process()
