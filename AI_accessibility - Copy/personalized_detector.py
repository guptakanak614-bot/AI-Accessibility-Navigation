from ultralytics import YOLO
import cv2
import pyttsx3
import time

from preferences import get_priority

# -----------------------------
# YOLO MODEL
# -----------------------------
model = YOLO("yolo11n.pt")

# -----------------------------
# VOICE ENGINE
# -----------------------------
engine = pyttsx3.init()

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# IMPORTANT OBJECTS
# -----------------------------
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
# ALERT COOLDOWN
# -----------------------------
last_alerts = {}
alert_cooldown = 5

# -----------------------------
# CAMERA
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha.")
    exit()

print("\n🧠 Personalized AI Accessibility Assistant Started")
print("Q press karke exit karo.\n")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        print("Frame read nahi ho raha.")
        break

    results = model(frame, verbose=False)

    current_time = time.time()

    # -----------------------------
    # PROCESS DETECTIONS
    # -----------------------------
    for result in results:

        for box in result.boxes:

            confidence = float(box.conf[0])

            if confidence < 0.5:
                continue

            class_id = int(box.cls[0])

            object_name = model.names[class_id]

            if object_name not in important_objects:
                continue

            object_label = important_objects[object_name]

            # -------------------------
            # GET PERSONALIZED PRIORITY
            # -------------------------
            priority = get_priority(object_name)

            # -------------------------
            # CREATE ALERT
            # -------------------------
            if priority == "HIGH":

                message = (
                    f"High priority alert. "
                    f"{object_label} detected."
                )

            elif priority == "MEDIUM":

                message = (
                    f"Medium priority. "
                    f"{object_label} detected."
                )

            else:

                message = (
                    f"{object_label} detected."
                )

            # -------------------------
            # VOICE COOLDOWN
            # -------------------------
            last_time = last_alerts.get(
                object_name,
                0
            )

            if current_time - last_time > alert_cooldown:

                speak(message)

                last_alerts[object_name] = current_time

            # -------------------------
            # TERMINAL OUTPUT
            # -------------------------
            print(
                f"Detected: {object_label} | "
                f"Priority: {priority} | "
                f"Confidence: {confidence:.2f}"
            )

    # -----------------------------
    # SHOW DETECTION
    # -----------------------------
    annotated_frame = results[0].plot()

    cv2.imshow(
        "Personalized AI Accessibility Assistant",
        annotated_frame
    )

    # -----------------------------
    # EXIT
    # -----------------------------
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# RELEASE
# -----------------------------
cap.release()
cv2.destroyAllWindows()

print("\n✅ Personalized detector stopped.")