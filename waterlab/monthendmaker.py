import pandas as pd
import tkinter as tk
from tkinter import filedialog

def file_grab():
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt the user to select a file
    file_path = filedialog.askopenfilename(title="Select File", filetypes=[("Text Files", "*.tab")])

    # Read the txt file into a Pandas DataFrame
    if file_path:  # Check if a file was selected
        df = pd.read_csv(file_path, header=None, sep='\t')  # Assuming tab-separated values
        return df
    
    else:
        print("No file selected.")

def converter(df):

    # Place third row into second row nulls
    df[2] = df[2].combine_first(df[3])
    df[2] = df[2].astype(int)
    
    # Drop Columns
    df.drop(columns=range(3, 6), inplace=True)
    df.drop(columns=range(7, 11), inplace=True)

    #Convert columns to correct format
    df[6] = df[6].apply(lambda x: f"{x:.3f}".zfill(9))
    df[11] = pd.to_datetime(df[11]).dt.strftime('%m/%d/%y')
    df[0] = df[0].apply(lambda x: f"{x}00")

    def swap_first_last(s):
    # Check if the first character is '-'
        if s[0] == '-':
            # Swap the first and last characters
            return s[-1] + s[1:-1] + s[0]
        else:
            return s

    # negative handling
    df[6] = df[6].apply(lambda x: swap_first_last(str(x)))

    return df

selected_df = file_grab()
print(selected_df)
output_df = converter(selected_df)
print(output_df)
output_csv = output_df.to_csv(index=False, header=False, sep='\t')
output_bytes = output_csv.encode('cp1252')

# Write the ANSI-encoded DataFrame to a file
with open('mo_end_output.dat', 'wb') as f:
     f.write(output_bytes)