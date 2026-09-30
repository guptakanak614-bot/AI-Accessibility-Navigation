import pyttsx3


def speak(text):
    print("AI:", text)

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def speak_navigation(destination, distance_km, walking_minutes):
    message = (
        f"Your destination is {destination}. "
        f"The distance is {distance_km:.2f} kilometers. "
        f"Estimated walking time is {walking_minutes:.0f} minutes."
    )

    speak(message)


if __name__ == "__main__":
    speak_navigation(
        "VCE College Meerut",
        2.5,
        30
    )