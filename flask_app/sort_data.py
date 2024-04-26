import os
import zipfile


def sort_data(zip_file_path):
    # Ensure the file is a valid ZIP file
    if not zipfile.is_zipfile(zip_file_path):
        raise ValueError("Uploaded file is not a ZIP archive.")

    extracted_dir = os.path.join(
        "uploads", os.path.splitext(os.path.basename(zip_file_path))[0]
    )

    # Create a directory to store extracted files
    os.makedirs(extracted_dir, exist_ok=True)

    file_categories = {"content": [], "data": [], "other": []}

    # Open the ZIP file and extract its contents
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extracted_dir)
        print("Extracted files: ")

        # Iterate over the names of the files in the ZIP
        for file_name in zip_ref.namelist():
            # Construct the full path for each extracted file
            full_file_path = os.path.join(extracted_dir, file_name)

            # Use a hypothetical function 'categorize_file' to determine the file category
            category = categorize_file(file_name)

            # Append the file path to the appropriate category
            if category in file_categories:
                file_categories[category].append(full_file_path)
            else:
                file_categories["other"].append(full_file_path)

    return file_categories


# Helper function to determine the category of a file
def categorize_file(filename):
    content_extensions = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi"]
    data_extensions = [".csv", ".xlsx", ".xls", ".txt"]

    extension = os.path.splitext(filename)[1].lower()
    if extension in content_extensions:
        return "content"
    elif extension in data_extensions:
        return "data"
    else:
        return "other"
