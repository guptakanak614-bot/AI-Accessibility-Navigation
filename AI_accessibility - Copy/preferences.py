# -----------------------------
# USER PREFERENCES
# -----------------------------

user_preferences = {
    "high_priority": [
        "car",
        "bus",
        "truck",
        "motorcycle",
        "bicycle"
    ],

    "medium_priority": [
        "chair",
        "bench"
    ],

    "low_priority": [
        "person"
    ]
}


# -----------------------------
# GET OBJECT PRIORITY
# -----------------------------

def get_priority(object_name):

    if object_name in user_preferences["high_priority"]:
        return "HIGH"

    elif object_name in user_preferences["medium_priority"]:
        return "MEDIUM"

    elif object_name in user_preferences["low_priority"]:
        return "LOW"

    else:
        return "NORMAL"


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    test_objects = [
        "car",
        "chair",
        "person",
        "bicycle"
    ]

    print("\n🧠 Personalized Accessibility Preferences\n")

    for obj in test_objects:

        priority = get_priority(obj)

        print(
            f"{obj} → {priority} priority"
        )