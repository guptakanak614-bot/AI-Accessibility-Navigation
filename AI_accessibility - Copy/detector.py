
from memory import (
    create_database,
    save_memory,
    save_scene,
    get_location_scenes
)

from ultralytics import YOLO
import cv2
import pyttsx3


# =====================================================
# YOLO MODEL
# =====================================================

model = YOLO("yolo11n.pt")


# =====================================================
# VOICE ENGINE
# =====================================================

engine = pyttsx3.init()


def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()


# =====================================================
# CURRENT LOCATION
# =====================================================

# Standalone testing ke liye location
# App integration ke time ye destination se aayegi.

CURRENT_LOCATION = "Standalone Camera Test"


# =====================================================
# IMPORTANT OBJECTS
# =====================================================

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


# =====================================================
# OBJECTS ALREADY SPOKEN
# =====================================================

spoken_objects = set()


# =====================================================
# DISTANCE ESTIMATION
# =====================================================

def estimate_distance(box, frame_width, frame_height):

    x1, y1, x2, y2 = box

    width = x2 - x1
    height = y2 - y1

    area_ratio = (
        (width * height)
        / (frame_width * frame_height)
    )

    if area_ratio > 0.20:
        return "very close"

    elif area_ratio > 0.07:
        return "near"

    elif area_ratio > 0.02:
        return "at medium distance"

    else:
        return "far"


# =====================================================
# SCENE MEMORY
# =====================================================

def save_detected_scene(objects):

    if not objects:
        return

    # Remove duplicates
    current_objects = list(set(objects))

    # Get previous scenes for this location
    previous_scenes = get_location_scenes(
        CURRENT_LOCATION
    )

    previous_objects = []

    # -------------------------------------------------
    # FIRST VISIT
    # -------------------------------------------------

    if not previous_scenes:

        speak(
            f"This is the first recorded scene "
            f"at {CURRENT_LOCATION}."
        )

    # -------------------------------------------------
    # PREVIOUS MEMORY EXISTS
    # -------------------------------------------------

    else:

        latest_scene = previous_scenes[0]

        # Database structure:
        # 0 = scene_name
        # 1 = location_name
        # 2 = objects
        # 3 = accessibility_status
        # 4 = timestamp

        previous_objects_text = latest_scene[2]

        previous_objects = [
            obj.strip()
            for obj in previous_objects_text.split(",")
            if obj.strip()
        ]

        previous_objects = list(
            set(previous_objects)
        )

        # -------------------------------------------------
        # NEW OBJECTS
        # -------------------------------------------------

        added_objects = [
            obj
            for obj in current_objects
            if obj not in previous_objects
        ]

        # -------------------------------------------------
        # REMOVED OBJECTS
        # -------------------------------------------------

        removed_objects = [
            obj
            for obj in previous_objects
            if obj not in current_objects
        ]

        # -------------------------------------------------
        # CHANGE DETECTED
        # -------------------------------------------------

        if added_objects or removed_objects:

            speak(
                f"Change detected at "
                f"{CURRENT_LOCATION}."
            )

            if added_objects:

                speak(
                    "New objects detected: "
                    + ", ".join(added_objects)
                )

            if removed_objects:

                speak(
                    "Previously detected objects "
                    "that are no longer present: "
                    + ", ".join(removed_objects)
                )

        # -------------------------------------------------
        # NO CHANGE
        # -------------------------------------------------

        else:

            speak(
                f"No major change detected at "
                f"{CURRENT_LOCATION}."
            )

    # =================================================
    # SAVE CURRENT SCENE
    # =================================================

    save_scene(
        scene_name=CURRENT_LOCATION,
        location_name=CURRENT_LOCATION,
        objects=current_objects,
        accessibility_status="Objects detected"
    )

    print(
        f"\nScene saved for: {CURRENT_LOCATION}"
    )

    print(
        f"Objects: {current_objects}"
    )


# =====================================================
# DATABASE
# =====================================================

create_database()


# =====================================================
# OPEN CAMERA
# =====================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("Camera open nahi ho raha.")

    exit()


print("\n====================================")
print("AI ACCESSIBILITY CAMERA STARTED")
print("====================================")
print("Press Q to exit.")
print("")


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("Frame read nahi ho raha.")

        break


    frame_height, frame_width = frame.shape[:2]


    # =================================================
    # YOLO DETECTION
    # =================================================

    results = model(
        frame,
        verbose=False
    )


    # Objects detected in current frame
    detected_objects = []


    # =================================================
    # PROCESS DETECTIONS
    # =================================================

    for result in results:

        for box in result.boxes:

            confidence = float(
                box.conf[0]
            )


            # -----------------------------------------
            # LOW CONFIDENCE IGNORE
            # -----------------------------------------

            if confidence < 0.5:

                continue


            # -----------------------------------------
            # CLASS ID
            # -----------------------------------------

            class_id = int(
                box.cls[0]
            )


            object_name = model.names[
                class_id
            ]


            # -----------------------------------------
            # ONLY IMPORTANT OBJECTS
            # -----------------------------------------

            if object_name not in important_objects:

                continue


            # -----------------------------------------
            # ADD TO CURRENT SCENE
            # -----------------------------------------

            detected_objects.append(
                object_name
            )


            # -----------------------------------------
            # BOUNDING BOX
            # -----------------------------------------

            coordinates = box.xyxy[
                0
            ].tolist()


            # -----------------------------------------
            # DISTANCE
            # -----------------------------------------

            distance = estimate_distance(
                coordinates,
                frame_width,
                frame_height
            )


            # -----------------------------------------
            # FRIENDLY OBJECT NAME
            # -----------------------------------------

            object_label = important_objects[
                object_name
            ]


            message = (
                f"{object_label} "
                f"{distance}."
            )


            # =========================================
            # VOICE ALERT
            # =========================================

            if object_name not in spoken_objects:

                speak(message)


                # Save object memory
                save_memory(
                    object_name,
                    distance
                )


                spoken_objects.add(
                    object_name
                )


            # =========================================
            # TERMINAL OUTPUT
            # =========================================

            print(
                f"Detected: {object_label} | "
                f"Distance: {distance} | "
                f"Confidence: "
                f"{confidence:.2f}"
            )


    # =================================================
    # SAVE / COMPARE SCENE
    # =================================================

    # Important:
    # Scene memory ko har frame par save nahi karna.
    #
    # Q press karne par current scene save hoga.
    # Isse database mein thousands of duplicate
    # scenes create nahi honge.

    key = cv2.waitKey(1) & 0xFF


    if key == ord("s"):

        save_detected_scene(
            detected_objects
        )


        # Reset spoken objects
        # next scene/test ke liye

        spoken_objects.clear()


    # =================================================
    # SHOW DETECTION
    # =================================================

    annotated_frame = results[0].plot()


    cv2.imshow(
        "AI Accessibility Memory",
        annotated_frame
    )


    # =================================================
    # PRESS Q TO EXIT
    # =================================================

    if key == ord("q"):

        break


# =====================================================
# RELEASE CAMERA
# =====================================================

cap.release()

cv2.destroyAllWindows()


print("\n====================================")
print("Camera stopped.")
print("====================================")