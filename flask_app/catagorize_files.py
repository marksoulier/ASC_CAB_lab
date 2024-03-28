import os


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


from fuzzywuzzy import process
import pandas as pd
import os


def assign_best_matches(categories_keywords, choices, threshold=40):
    """
    Assigns the best match for each category from a list of choices, ensuring each
    category is matched to exactly one choice based on its list of keywords. After
    a match is found for a category, the matched choice is removed from further
    consideration.

    :param categories_keywords: A dictionary where keys are category names and
                                values are lists of keywords for that category.
    :param choices: A list of choices against which to match the category keywords.
    :param threshold: The score threshold for considering a match valid.
    :return: A dictionary where keys are category names and values are the best
             matching choice as a string.
    """
    assigned_matches = {}
    remaining_choices = choices[:]

    # Iterate over categories to find the best match for each
    for category, keywords in categories_keywords.items():
        category_best_score = threshold
        category_best_match = None

        # Iterate through keywords to find the best match for the category
        for keyword in keywords:
            best_match = process.extractOne(
                keyword, remaining_choices, score_cutoff=threshold
            )
            if best_match and best_match[1] > category_best_score:
                category_best_score = best_match[1]
                category_best_match = best_match[0]

        # If a best match was found for the category, assign it and remove from choices
        if category_best_match:
            assigned_matches[category] = category_best_match
            remaining_choices.remove(category_best_match)

    # if a category has no match, assign None
    for category in categories_keywords.keys():
        if category not in assigned_matches:
            assigned_matches[category] = None

    return assigned_matches


def process_file_categories_content(file_paths):
    content_names = set()
    participants = set()
    eye_tracked_data, GSR_data, FACET_data = None, None, None

    # Then, adjust the data_keywords and column_keywords to be lists of possible keywords
    data_keywords = {
        "eye_tracked_data": ["ET-data", "eyetracking", "eye track", "pupil"],
        "GSR_data": ["GSR", "galvanic skin response"],
        "FACET_data": ["FACET", "facial coding"],
    }

    column_keywords = {
        "content": ["SlideEvent", "content", "slide"],
        "participant": ["ID", "participant", "user"],
    }

    # Extract file names
    file_names = [os.path.basename(file_path).lower() for file_path in file_paths]

    # Assign best matches to each data type
    assigned_files = assign_best_matches(data_keywords, file_names, threshold=40)

    # Mapping back assigned file names to their full paths
    full_path_mapping = {os.path.basename(path).lower(): path for path in file_paths}
    print("Assigned files:", assigned_files)
    eye_tracked_data = full_path_mapping.get(assigned_files["eye_tracked_data"])
    GSR_data = full_path_mapping.get(assigned_files["GSR_data"])
    FACET_data = full_path_mapping.get(assigned_files["FACET_data"])

    def read_and_extract(file_path, data_type):
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        else:
            return None, None

        column_choices = df.columns.tolist()
        assigned_matches = assign_best_matches(column_keywords, column_choices)

        for category, match in assigned_matches.items():
            print(f"{category}: {match}")
            if category == "content":
                content_col = match
            if category == "participant":
                participant_col = match

        unique_contents = df[content_col].unique() if content_col else []
        unique_participants = df[participant_col].unique() if participant_col else []

        return unique_contents, unique_participants

    # Process each file based on the assigned category
    for category, file_name in assigned_files.items():
        if file_name:
            file_path = full_path_mapping[file_name]
            contents, parts = read_and_extract(file_path, category)
            content_names.update(contents)
            participants.update(parts)

    return (
        list(content_names),
        list(participants),
        eye_tracked_data,
        GSR_data,
        FACET_data,
    )


# get content function
def get_content(content_files, content_names, threshold=40):
    """
    Matches content names with content file paths based on similarity.

    :param content_files: List of file paths to content.
    :param content_names: List of content names to match with files.
    :param threshold: The score threshold for considering a match valid.
    :return: A dictionary with content names as keys and matched file paths as values.
             If a content name does not closely match any file, it maps to None.
    """
    content_mapping = {}

    # Simplify file paths to just the base name without extension for better matching
    simplified_files = {
        os.path.splitext(os.path.basename(f))[0].replace("_", " ").lower(): f
        for f in content_files
    }

    for name in content_names:
        # Attempt to find the best match for this content name among the content files
        best_match, best_score = process.extractOne(
            name.lower(), list(simplified_files.keys()), score_cutoff=threshold
        )

        # If a sufficiently close match is found, use the full path from the original list
        if best_match:
            content_mapping[name] = simplified_files[best_match]
        else:
            # No match found above the threshold
            content_mapping[name] = None

    return content_mapping
