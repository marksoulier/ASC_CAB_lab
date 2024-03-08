import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def upload_file():
    global filepath
    filepath = filedialog.askopenfilename()
    if filepath:
        messagebox.showinfo("File Selected", f"File {filepath} has been selected.")


def create_blank_file():
    if filepath:
        # Assuming you want to create the blank file in the same directory as the selected file
        output_file = filepath.rsplit(".", 1)[0] + "_blank.txt"
        with open(output_file, "w") as file:
            pass  # This will create a blank file
        messagebox.showinfo("Success", f"Blank file created at {output_file}")
    else:
        messagebox.showerror("Error", "Please select a file first.")


# Creating the main window
root = tk.Tk()
root.title("File Processor")

# Setting the window size
root.geometry("300x200")

# Initializing filepath variable
filepath = ""

# Add a Header to the window saying "File Processor"
header = tk.Label(root, text="File Processor", font=("Arial", 18))
header.pack(pady=20)

# Adding a button to upload a file
upload_button = tk.Button(root, text="Upload File", command=upload_file)
upload_button.pack(pady=20)

# Adding a button to execute and create a blank file
execute_button = tk.Button(root, text="Execute", command=create_blank_file)
execute_button.pack(pady=20)

# Running the GUI application
root.mainloop()
