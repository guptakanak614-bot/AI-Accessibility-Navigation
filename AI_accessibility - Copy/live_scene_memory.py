from ultralytics import YOLO
import cv2
import time

from scene_memory import (
    create_scene_database,
    save_scene
)

# -----------------------------
# YOLO MODEL
# -----------------------------
model = YOLO("yolo11n.pt")

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
# DATABASE
# -----------------------------
create_scene_database()

# -----------------------------
# CAMERA
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha.")
    exit()

# -----------------------------
# SCENE MEMORY SETTINGS
# -----------------------------
last_scene = set()
last_save_time = 0

save_interval = 10

scene_name = "Current Location"

print("\n🧠 Live Scene Memory Started")
print("Camera ke saamne objects lao.")
print("Scene change hoga toh memory update hogi.")
print("Q press karke exit karo.\n")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        print("Frame read nahi ho raha.")
        break

    # YOLO detection
    results = model(frame, verbose=False)

    current_objects = set()

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

            if object_name in important_objects:
                current_objects.add(object_name)

    # -----------------------------
    # CHECK SCENE CHANGE
    # -----------------------------
    if current_objects != last_scene:

        print("\n🔄 Scene Changed!")

        print(
            "Current Objects:",
            current_objects
        )

        # -------------------------
        # ACCESSIBILITY STATUS
        # -------------------------
        obstacle_objects = {
            "chair",
            "bench",
            "car",
            "bus",
            "truck",
            "motorcycle",
            "bicycle"
        }

        if current_objects.intersection(obstacle_objects):

            accessibility_status = (
                "Potential obstacle detected"
            )

        else:

            accessibility_status = (
                "No known obstacle detected"
            )

        # -------------------------
        # SAVE SCENE
        # -------------------------
        save_scene(
            scene_name,
            list(current_objects),
            accessibility_status
        )

        print(
            "🧠 Scene saved:",
            accessibility_status
        )

        last_scene = current_objects.copy()

        last_save_time = time.time()

    # -----------------------------
    # PERIODIC MEMORY UPDATE
    # -----------------------------
    current_time = time.time()

    if (
        current_objects
        and current_time - last_save_time > save_interval
    ):

        save_scene(
            scene_name,
            list(current_objects),
            "Scene observed again"
        )

        print("🧠 Scene memory updated.")

        last_save_time = current_time

    # -----------------------------
    # SHOW CAMERA
    # -----------------------------
    annotated_frame = results[0].plot()

    cv2.imshow(
        "AI Accessibility Memory - Live Scene",
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

print("\n✅ Live Scene Memory stopped.")