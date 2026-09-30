from ultralytics import YOLO
import cv2
import pyttsx3
import time

from memory import create_database, save_memory, get_memories

# -----------------------------
# SETUP
# -----------------------------
model = YOLO("yolo11n.pt")

engine = pyttsx3.init()


def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()


important_objects = {
    "person": "Person",
    "chair": "Chair",
    "bench": "Bench",
    "car": "Vehicle",
    "bus": "Bus",
    "truck": "Truck",
    "motorcycle": "Motorcycle",
    "bicycle": "Bicycle"
}


# -----------------------------
# DATABASE
# -----------------------------
create_database()


def get_previous_objects():
    memories = get_memories()

    previous_objects = set()

    for memory in memories:
        object_name = memory[0]
        previous_objects.add(object_name)

    return previous_objects


# -----------------------------
# CAMERA
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha.")
    exit()


# Existing memory
previous_objects = get_previous_objects()

print("Previous memory:", previous_objects)

last_save_time = 0
save_interval = 10

last_alert = ""
last_alert_time = 0
alert_cooldown = 5


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        print("Frame read nahi ho raha.")
        break

    results = model(frame, verbose=False)

    current_objects = set()

    # -------------------------
    # DETECTIONS
    # -------------------------
    for result in results:

        for box in result.boxes:

            confidence = float(box.conf[0])

            if confidence < 0.5:
                continue

            class_id = int(box.cls[0])
            object_name = model.names[class_id]

            if object_name in important_objects:
                current_objects.add(object_name)


    # -------------------------
    # CHANGE DETECTION
    # -------------------------
    new_objects = current_objects - previous_objects
    removed_objects = previous_objects - current_objects


    # New object
    if new_objects:

        for obj in new_objects:

            message = (
                f"Change detected. "
                f"New {important_objects[obj]} detected."
            )

            current_time = time.time()

            if (
                message != last_alert
                or current_time - last_alert_time > alert_cooldown
            ):
                speak(message)

                last_alert = message
                last_alert_time = current_time


    # Removed object
    if removed_objects:

        for obj in removed_objects:

            message = (
                f"Change detected. "
                f"{important_objects[obj]} is no longer present."
            )

            current_time = time.time()

            if (
                message != last_alert
                or current_time - last_alert_time > alert_cooldown
            ):
                speak(message)

                last_alert = message
                last_alert_time = current_time


    # -------------------------
    # SAVE NEW MEMORY
    # -------------------------
    current_time = time.time()

    if (
        current_objects
        and current_time - last_save_time > save_interval
    ):

        for obj in current_objects:
            save_memory(obj, "detected")

        previous_objects = current_objects.copy()

        last_save_time = current_time

        print(
            "🧠 Memory updated:",
            previous_objects
        )


    # -------------------------
    # DISPLAY
    # -------------------------
    annotated_frame = results[0].plot()

    cv2.imshow(
        "AI Accessibility Memory",
        annotated_frame
    )


    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()