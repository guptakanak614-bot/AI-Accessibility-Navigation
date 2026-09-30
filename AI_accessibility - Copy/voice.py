import pyttsx3

engine = pyttsx3.init()

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    speak("AI Accessibility Memory is ready.")