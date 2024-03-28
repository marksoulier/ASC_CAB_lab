from catagorize_files import assign_best_matches, get_content


def test_find_best_match():
    # Example usage
    categories_keywords = {
        "content": ["SlideEvent", "content", "slide"],
        "participant": ["ID", "participant", "user"],
    }

    choices = [
        "SlideEvent",
        "ET_PupilLeft",
        "ET_PupilRight",
        "ID",
        "AlignedTimeSec",
        "Time",
    ]

    assigned_matches = assign_best_matches(categories_keywords, choices, threshold=60)
    for category, match in assigned_matches.items():
        print(f"{category}: {match}")


def test_get_content():
    content_files = [
        "uploads\\Kellie_study\\content/JG_1226-lo_denim_neutral.jpg",
        "uploads\\Kellie_study\\content/JS_0744-lo_denim_negative.jpg",
        "uploads\\Kellie_study\\content/MR1_0132-lo_denim_positive.jpg",
        "uploads\\Kellie_study\\content/PupilMeasure_dot.jpg",
        "uploads\\Kellie_study\\content/PupilMeasure_dot-1.jpg",
        "uploads\\Kellie_study\\content/PupilMeasure_dot-2.jpg",
        "uploads\\Kellie_study\\content/SAM_Two_Dimensions_0.png",
        "uploads\\Kellie_study\\content/SAM_Two_Dimensions_1.PNG",
        "uploads\\Kellie_study\\content/SAM_Two_Dimensions_2.PNG",
        "uploads\\Kellie_study\\content/Vid0.mp4",
        "uploads\\Kellie_study\\content/Vid1.mp4",
        "uploads\\Kellie_study\\content/Vid2_with_Alarm.mp4",
    ]
    content_names = [
        "SAM Two Dimensions2",
        "Vid1",
        "JS_0744-lo_denim_resize",
        "MR1_0132-lo_denim_resize",
        "Vid2 with Alarm",
        "JG_1226-lo_denim_resize",
        "PupilMeasure_dot",
        "PupilMeasure_dot-1",
        "PupilMeasure_dot-2",
        "SAM Two Dimensions0",
        "Vid0",
        "SAM Two Dimensions1",
    ]

    content = get_content(content_files, content_names, threshold=40)
    for name, file_path in content.items():
        print(f"{name}: {file_path}")

    print(content)


if __name__ == "__main__":
    # test_find_best_match()
    test_get_content()
