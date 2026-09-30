import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

from navigation_voice import speak_navigation, speak
from streamlit_js_eval import get_geolocation
from memory import (
    save_destination,
    get_saved_destinations,
    save_scene,
    get_location_scenes
)
# ==================================================
# SAVE CURRENT SCENE TO LOCATION MEMORY
# ==================================================

def save_current_scene(objects, accessibility_status):
    
    location_name = st.session_state.get(
        "destination_name",
        "Unknown Location"
    )

    if not location_name:
        location_name = "Unknown Location"

    save_scene(
        scene_name=location_name,
        location_name=location_name,
        objects=objects,
        accessibility_status=accessibility_status
    )

    return location_name
# ==================================================
# COMPARE CURRENT SCENE WITH PREVIOUS MEMORY
# ==================================================

def compare_with_previous_memory(objects):

    location_name = st.session_state.get(
        "destination_name",
        ""
    )

    if not location_name:
        return None

    previous_scenes = get_location_scenes(
        location_name
    )

    if not previous_scenes:
        return {
            "status": "first_visit",
            "message": (
                f"No previous memory found for "
                f"{location_name}."
            )
        }

    # Most recent scene
    latest_scene = previous_scenes[0]

    previous_objects_text = latest_scene[2]

    previous_objects = [
        obj.strip()
        for obj in previous_objects_text.split(",")
        if obj.strip()
    ]

    current_objects = list(set(objects))
    previous_objects = list(set(previous_objects))

    added_objects = [
        obj for obj in current_objects
        if obj not in previous_objects
    ]

    removed_objects = [
        obj for obj in previous_objects
        if obj not in current_objects
    ]

    if not added_objects and not removed_objects:

        return {
            "status": "no_change",
            "message": (
                f"No major change detected at "
                f"{location_name}."
            )
        }

    return {
        "status": "changed",
        "location": location_name,
        "added": added_objects,
        "removed": removed_objects
    }
# ==================================================
# VOICE ALERT FOR LOCATION CHANGES
# ==================================================

def speak_memory_changes(objects):

    result = compare_with_previous_memory(objects)

    if result is None:
        return

    if result["status"] == "first_visit":

        speak(
            f"This is the first recorded visit to "
            f"{st.session_state.destination_name}."
        )

    elif result["status"] == "no_change":

        speak(
            f"No major change detected at "
            f"{st.session_state.destination_name}."
        )

    elif result["status"] == "changed":

        location = result["location"]
        added = result["added"]
        removed = result["removed"]

        message = (
            f"Change detected at {location}."
        )

        if added:
            message += (
                " Newly detected objects are "
                + ", ".join(added)
                + "."
            )

        if removed:
            message += (
                " Previously detected objects "
                "that are no longer present are "
                + ", ".join(removed)
                + "."
            )

        speak(message)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Accessibility Assistant",
    page_icon="🧭",
    layout="wide"
)


# ==================================================
# TITLE
# ==================================================

st.title("🧭 AI Accessibility Navigation & Memory Assistant")

st.write(
    "Accessible navigation and location memory "
    "assistant for blind and visually impaired users."
)


# ==================================================
# SESSION STATE
# ==================================================

if "current_location" not in st.session_state:
    st.session_state.current_location = None

if "destination" not in st.session_state:
    st.session_state.destination = None

if "current_name" not in st.session_state:
    st.session_state.current_name = ""

if "destination_name" not in st.session_state:
    st.session_state.destination_name = ""

if "gps_active" not in st.session_state:
    st.session_state.gps_active = False


# ==================================================
# LOCATION SEARCH FUNCTION
# ==================================================

def search_location(place):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "AI-Accessibility-Assistant"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data:

            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            display_name = data[0]["display_name"]

            return (
                latitude,
                longitude,
                display_name
            )

        return None

    except Exception as e:

        st.error(
            f"❌ Location search failed: {e}"
        )

        return None


# ==================================================
# WALKING ROUTE FUNCTION
# ==================================================

def get_walking_route(start, end):

    start_lat, start_lon = start
    end_lat, end_lon = end

    url = (
        "https://router.project-osrm.org/route/v1/"
        f"foot/{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "Ok":
            return None

        route = data["routes"][0]

        distance = route["distance"]
        duration = route["duration"]

        coordinates = route["geometry"]["coordinates"]

        route_coordinates = [
            [lat, lon]
            for lon, lat in coordinates
        ]


        # ==================================================
        # TURN-BY-TURN STEPS
        # ==================================================

        steps = route["legs"][0]["steps"]

        navigation_steps = []

        for step in steps:

            maneuver = step.get(
                "maneuver",
                {}
            )

            maneuver_type = maneuver.get(
                "type",
                ""
            )

            modifier = maneuver.get(
                "modifier",
                ""
            )

            street_name = step.get(
                "name",
                ""
            )


            # ----------------------------------------------
            # CREATE VOICE-FRIENDLY INSTRUCTION
            # ----------------------------------------------

            if maneuver_type == "depart":

                instruction = "Start walking"

            elif maneuver_type == "arrive":

                instruction = (
                    "You have arrived at your destination"
                )

            elif modifier:

                instruction = (
                    f"Turn {modifier}"
                )

                if street_name:

                    instruction += (
                        f" onto {street_name}"
                    )

            else:

                instruction = "Continue straight"

                if street_name:

                    instruction += (
                        f" on {street_name}"
                    )


            navigation_steps.append(
                instruction
            )


        return (
            route_coordinates,
            distance,
            duration,
            navigation_steps
        )

    except Exception as e:

        st.error(
            f"❌ Route calculation failed: {e}"
        )

        return None


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("📍 Location Setup")


mode = st.sidebar.radio(
    "What do you want to set?",
    [
        "Your Location",
        "Destination"
    ]
)
# ==================================================
# QUICK / FIXED DESTINATIONS
# ==================================================

st.sidebar.subheader("⭐ Quick Destinations")

if st.sidebar.button("🏫 College"):

    result = search_location("VCE College Meerut")

    if result:

        latitude, longitude, name = result

        st.session_state.destination = (
            latitude,
            longitude
        )

        st.session_state.destination_name = name

        st.sidebar.success(
            "🏫 College selected!"
        )

    else:

        st.sidebar.error(
            "College location nahi mili."
        )


if st.sidebar.button("🏥 Hospital"):

    result = search_location("District Hospital Meerut")

    if result:

        latitude, longitude, name = result

        st.session_state.destination = (
            latitude,
            longitude
        )

        st.session_state.destination_name = name

        st.sidebar.success(
            "🏥 Hospital selected!"
        )

    else:

        st.sidebar.error(
            "Hospital location not found."
        )


if st.sidebar.button("🏫 School"):

    result = search_location("School Meerut")

    if result:

        latitude, longitude, name = result

        st.session_state.destination = (
            latitude,
            longitude
        )

        st.session_state.destination_name = name

        st.sidebar.success(
            "🏫 School selected!"
        )

    else:

        st.sidebar.error(
            "School location not found."
        )
    # ==================================================
# SAVE CUSTOM DESTINATION
# ==================================================

st.sidebar.subheader("💾 Save Fixed Destination")

custom_name = st.sidebar.text_input(
    "Destination name",
    placeholder="Example: My College"
)

custom_location = st.sidebar.text_input(
    "Location",
    placeholder="Example: VCE College Meerut"
)

if st.sidebar.button("💾 Save Destination"):

    if custom_name.strip() and custom_location.strip():

        result = search_location(
            custom_location.strip()
        )

        if result:

            latitude, longitude, name = result

            st.session_state.destination = (
                latitude,
                longitude
            )

            st.session_state.destination_name = (
                custom_name.strip()
            )
            save_destination(
              custom_name.strip(),
              latitude,
              longitude
)

            st.sidebar.success(
                f"✅ {custom_name} saved!"
            )

        else:

            st.sidebar.error(
                "❌ Location not found."
            )

    else:

        st.sidebar.warning(
            "⚠️ Enter name and location."
        )
    # ==================================================
# SAVED DESTINATIONS
# ==================================================

st.sidebar.subheader("📍 My Saved Destinations")

saved_destinations = get_saved_destinations()

if saved_destinations:

    destination_options = [
        destination[0]
        for destination in saved_destinations
    ]

    selected_destination = st.sidebar.selectbox(
        "Select saved destination",
        destination_options
    )

    if st.sidebar.button("📍 Use Saved Destination"):

        for destination in saved_destinations:

            if destination[0] == selected_destination:

                name, latitude, longitude = destination

                st.session_state.destination = (
                    latitude,
                    longitude
                )

                st.session_state.destination_name = name

                st.sidebar.success(
                    f"✅ {name} selected!"
                )

                st.rerun()

else:

    st.sidebar.info(
        "No saved destinations yet."
    )


# ==================================================
# SEARCH LOCATION
# ==================================================

st.sidebar.subheader("🔎 Search Location")


with st.sidebar.form(
    "location_search_form"
):

    search_text = st.text_input(
        "Enter location name",
        placeholder="Example: VCE College Meerut"
    )

    search_clicked = st.form_submit_button(
        "🔍 Search"
    )


if search_clicked:

    if search_text.strip():

        result = search_location(
            search_text.strip()
        )

        if result:

            latitude, longitude, name = result


            # ----------------------------------------------
            # SET CURRENT LOCATION
            # ----------------------------------------------

            if mode == "Your Location":

                st.session_state.current_location = (
                    latitude,
                    longitude
                )

                st.session_state.current_name = name

                st.sidebar.success(
                    "📍 Your Location selected"
                )


            # ----------------------------------------------
            # SET DESTINATION
            # ----------------------------------------------

            else:

                st.session_state.destination = (
                    latitude,
                    longitude
                )

                st.session_state.destination_name = name

                st.sidebar.success(
                    "🎯 Destination selected"
                )

        else:

            st.sidebar.error(
                "❌ Location not found."
            )

    else:

        st.sidebar.warning(
            "⚠️ Enter Location name."
        )


# ==================================================
# MAP CENTER
# ==================================================

if st.session_state.current_location:

    map_center = list(
        st.session_state.current_location
    )

elif st.session_state.destination:

    map_center = list(
        st.session_state.destination
    )

else:

    # Default location: New Delhi

    map_center = [
        28.6139,
        77.2090
    ]


# ==================================================
# CREATE MAP
# ==================================================

m = folium.Map(
    location=map_center,
    zoom_start=14
)


# ==================================================
# CURRENT LOCATION MARKER
# ==================================================

if st.session_state.current_location:

    latitude, longitude = (
        st.session_state.current_location
    )

    folium.Marker(
        [
            latitude,
            longitude
        ],
        popup="📍 Your Location",
        tooltip="Your Location",
        icon=folium.Icon(
            color="blue",
            icon="home"
        )
    ).add_to(m)


# ==================================================
# DESTINATION MARKER
# ==================================================

if st.session_state.destination:

    latitude, longitude = (
        st.session_state.destination
    )

    folium.Marker(
        [
            latitude,
            longitude
        ],
        popup="🎯 Destination",
        tooltip="Destination",
        icon=folium.Icon(
            color="red",
            icon="flag"
        )
    ).add_to(m)


# ==================================================
# ROUTE
# ==================================================

route_info = None


if (
    st.session_state.current_location
    and
    st.session_state.destination
):

    route_info = get_walking_route(
        st.session_state.current_location,
        st.session_state.destination
    )

    if route_info:

        (
            route_coordinates,
            distance,
            duration,
            navigation_steps
        ) = route_info


        # ----------------------------------------------
        # DRAW ROUTE
        # ----------------------------------------------

        folium.PolyLine(
            route_coordinates,
            weight=6,
            opacity=0.8,
            tooltip="🚶 Walking Route"
        ).add_to(m)


# ==================================================
# DISPLAY MAP
# ==================================================

map_data = st_folium(
    m,
    width=1000,
    height=550
)


# ==================================================
# MAP CLICK LOCATION
# ==================================================

if map_data:

    last_clicked = map_data.get(
        "last_clicked"
    )

    if last_clicked:

        clicked_lat = last_clicked["lat"]
        clicked_lon = last_clicked["lng"]


        if mode == "Your Location":

            st.session_state.current_location = (
                clicked_lat,
                clicked_lon
            )

            st.session_state.current_name = (
                "Selected on Map"
            )


        else:

            st.session_state.destination = (
                clicked_lat,
                clicked_lon
            )

            st.session_state.destination_name = (
                "Selected on Map"
            )


        st.rerun()


# ==================================================
# LOCATION INFORMATION
# ==================================================

st.divider()

col1, col2 = st.columns(2)


# ==================================================
# YOUR LOCATION
# ==================================================

with col1:

    st.subheader(
        "📍 Your Location"
    )

    if st.session_state.current_location:

        st.write(
            st.session_state.current_name
        )

        latitude, longitude = (
            st.session_state.current_location
        )

        st.caption(
            f"{latitude:.5f}, "
            f"{longitude:.5f}"
        )

    else:

        st.warning(
            "Your location not selected."
        )


# ==================================================
# DESTINATION
# ==================================================

with col2:

    st.subheader(
        "🎯 Fixed Destination"
    )

    if st.session_state.destination:

        st.write(
            st.session_state.destination_name
        )

        latitude, longitude = (
            st.session_state.destination
        )

        st.caption(
            f"{latitude:.5f}, "
            f"{longitude:.5f}"
        )

    else:

        st.warning(
            "Destination not selected."
        )


# ==================================================
# NAVIGATION INFORMATION
# ==================================================

if route_info:

    (
        route_coordinates,
        distance,
        duration,
        navigation_steps
    ) = route_info


    distance_km = distance / 1000

    walking_minutes = duration / 60


    st.divider()

    st.subheader(
        "🚶 Navigation Information"
    )


    col1, col2, col3 = st.columns(3)


    # ----------------------------------------------
    # DISTANCE
    # ----------------------------------------------

    with col1:

        st.metric(
            "📏 Distance",
            f"{distance_km:.2f} km"
        )


    # ----------------------------------------------
    # WALKING TIME
    # ----------------------------------------------

    with col2:

        st.metric(
            "⏱️ Walking Time",
            f"{walking_minutes:.0f} min"
        )


    # ----------------------------------------------
    # DESTINATION
    # ----------------------------------------------

    with col3:

        st.metric(
            "🎯 Destination",
            "Selected"
        )


    st.success(
        "✅ Walking route successfully created!"
    )


    # ==================================================
    # START NAVIGATION
    # ==================================================

    if st.button(
        "▶️ Start Navigation"
    ):

        speak(
            f"Navigation started. "
            f"Your destination is "
            f"{st.session_state.destination_name}. "
            f"The distance is "
            f"{distance_km:.2f} kilometers. "
            f"Estimated walking time is "
            f"{walking_minutes:.0f} minutes."
        )
    # ==================================================
# DESTINATION ARRIVAL CHECK
# ==================================================

if st.session_state.current_location and st.session_state.destination:

    current_lat, current_lon = st.session_state.current_location
    dest_lat, dest_lon = st.session_state.destination

    lat_diff = abs(current_lat - dest_lat)
    lon_diff = abs(current_lon - dest_lon)

    if lat_diff < 0.001 and lon_diff < 0.001:

        st.success(
            "🎯 You have reached your destination!"
        )

        speak(
            f"You have reached "
            f"{st.session_state.destination_name}."
        )

        st.info(
            "📷 You can now use AI Camera "
            "to check the surroundings."
        )
    if st.button("🧠 Check Location Memory"):

       location_name = st.session_state.destination_name

    previous_scenes = get_location_scenes(location_name)

    if previous_scenes:

        latest_scene = previous_scenes[0]

        st.success(
            "🧠 Previous memory found."
        )

        st.write(
            "Previously detected objects: "
            + latest_scene[2]
        )

        speak(
            "Previous memory at "
            + location_name
            + ". "
            + latest_scene[2]
        )

    else:

        st.info(
            "📍 No previous memory found "
            "for this location."
        )

        speak(
            "No previous memory found at "
            + location_name
        )


    # ==================================================
    # BASIC VOICE NAVIGATION
    # ==================================================

    if st.button(
        "🔊 Speak Navigation"
    ):

        speak_navigation(
            st.session_state.destination_name,
            distance_km,
            walking_minutes
        )


    # ==================================================
    # TURN-BY-TURN DIRECTIONS
    # ==================================================

    st.subheader(
        "🧭 Turn-by-Turn Directions"
    )


    if navigation_steps:

        for index, instruction in enumerate(
            navigation_steps,
            start=1
        ):

            st.write(
                f"**{index}.** {instruction}"
            )


        # ----------------------------------------------
        # SPEAK DIRECTIONS
        # ----------------------------------------------

        if st.button(
            "🎙️ Speak Turn-by-Turn Directions"
        ):

            for instruction in navigation_steps:

                speak(
                    instruction
                )


# ==================================================
# LIVE GPS LOCATION
# ==================================================

st.divider()

st.subheader(
    "📍 Live GPS Location"
)


location = get_geolocation()


if location:

    # ==================================================
    # GPS ERROR
    # ==================================================

    if "error" in location:

        error_message = location["error"].get(
            "message",
            "Unable to get location"
        )

        st.error(
            f"❌ GPS Error: {error_message}"
        )


    # ==================================================
    # GPS SUCCESS
    # ==================================================

    else:

        latitude = location["coords"]["latitude"]

        longitude = location["coords"]["longitude"]


        st.success(
            "✅ Current GPS location detected!"
        )


        st.write(
            f"Latitude: {latitude:.6f}"
        )

        st.write(
            f"Longitude: {longitude:.6f}"
        )


        # ==================================================
        # USE GPS LOCATION
        # ==================================================

        if st.button(
            "📍 Use My GPS Location"
        ):

            st.session_state.current_location = (
                latitude,
                longitude
            )

            st.session_state.current_name = (
                "📡 Current GPS Location"
            )

            st.session_state.gps_active = True

            st.rerun()
        # =====================================================
# 📷 LIVE AI CAMERA + YOLO + VOICE ALERT
# =====================================================
from memory import (
    create_database,
    save_memory,
    save_scene,
    get_location_scenes
)
create_database()
st.markdown("---")
st.header("📷 Live AI Accessibility Camera")

st.write(
    "Real-time AI camera for detecting obstacles "
    "and providing voice alerts."
)

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
from ultralytics import YOLO
import time


# =====================================================
# LOAD YOLO MODEL
# =====================================================

@st.cache_resource
def load_yolo_model():
    return YOLO("yolo11n.pt")


model = load_yolo_model()


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
def save_current_scene(objects, location_name):
    if not objects:
        return

    unique_objects = list(set(objects))

    save_scene(
        scene_name=location_name,
        location_name=location_name,
        objects=unique_objects,
        accessibility_status="Objects detected"
    )

    print(
        f"🧠 Scene saved at {location_name}: "
        f"{unique_objects}"
    )
# Object priority for accessibility alerts

object_priority = {
    "car": "HIGH",
    "bus": "HIGH",
    "truck": "HIGH",
    "motorcycle": "HIGH",
    "bicycle": "HIGH",
    "chair": "MEDIUM",
    "bench": "MEDIUM",
    "person": "LOW"
}


# =====================================================
# VOICE COOLDOWN
# =====================================================

last_spoken = {}
VOICE_COOLDOWN = 5
latest_detected_objects = []


# =====================================================
# YOLO VIDEO PROCESSOR
# =====================================================
class YOLOVideoProcessor(VideoProcessorBase):

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        frame_height, frame_width = img.shape[:2]

        results = model(img, verbose=False)

        detected_objects = []

        for result in results:

            for box in result.boxes:

                confidence = float(box.conf[0])

                if confidence < 0.5:
                    continue

                class_id = int(box.cls[0])

                object_name = model.names[class_id]

                if object_name not in important_objects:
                    continue

                # Save detected object
                detected_objects.append(object_name)
                latest_detected_objects[:] = list(set(detected_objects))

                # Bounding box
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # LEFT / CENTER / RIGHT
                center_x = (x1 + x2) / 2

                if center_x < frame_width / 3:
                    position = "on your left"

                elif center_x > (frame_width * 2 / 3):
                    position = "on your right"

                else:
                    position = "ahead of you"

                # ROUGH DISTANCE
                box_width = x2 - x1
                box_height = y2 - y1

                object_area = box_width * box_height
                frame_area = frame_width * frame_height

                area_ratio = object_area / frame_area

                if area_ratio > 0.20:
                    distance = "very close"

                elif area_ratio > 0.07:
                    distance = "near"

                elif area_ratio > 0.02:
                    distance = "at medium distance"

                else:
                    distance = "far"

                object_label = important_objects[object_name]

                print(
                    f"Detected: {object_label} | "
                    f"Distance: {distance} | "
                    f"Position: {position} | "
                    f"Confidence: {confidence:.2f}"
                )

                # VOICE ALERT
                current_time = time.time()

                alert_key = (
                    f"{object_name}_{position}_{distance}"
                )

                if (
                    alert_key not in last_spoken
                    or
                    current_time - last_spoken[alert_key]
                    > VOICE_COOLDOWN
                ):

                    priority = object_priority.get(
                        object_name,
                        "NORMAL"
                    )

                    speak(
                        f"{priority} warning. "
                        f"{object_label} "
                        f"{distance} "
                        f"{position}."
                    )

                    last_spoken[alert_key] = current_time

        # YOLO boxes display
        annotated_frame = results[0].plot()

        return av.VideoFrame.from_ndarray(
            annotated_frame,
            format="bgr24"
        )
# =====================================================
# START LIVE CAMERA
# =====================================================

webrtc_streamer(
    key="live_ai_camera",

    video_processor_factory=YOLOVideoProcessor,

    media_stream_constraints={
        "video": True,
        "audio": False
    },

    async_processing=True
)
st.markdown("---")
st.subheader("🧠 Location Memory")

memory_location = st.session_state.get(
    "destination_name",
    "Current Location"
)

st.info(
    f"📍 Memory Location: {memory_location}"
)
if st.session_state.destination_name:
    st.success(
        f"🧠 AI Memory Active for: "
        f"{st.session_state.destination_name}"
    )
else:
    st.warning(
        "⚠️ First select any destination."
    )
previous_memories = get_location_scenes(memory_location)

if previous_memories:
    st.write("🧠 Previous Memory")

    latest_memory = previous_memories[0]

    st.write(
        "Previously detected objects: "
        + latest_memory[2]
    )
else:
    st.write(
        "📍 No previous memory recorded for this location."
    )

if st.button("💾 Save Current Scene"):

    current_objects = list(set(latest_detected_objects))

    if not current_objects:

        st.warning(
            "No important object detected."
        )

    else:

        # Previous scene check
        previous_scenes = get_location_scenes(
            memory_location
        )

        if previous_scenes:

            previous_objects_text = previous_scenes[0][2]

            previous_objects = [
                obj.strip()
                for obj in previous_objects_text.split(",")
                if obj.strip()
            ]

            previous_objects = list(set(previous_objects))

            added_objects = [
                obj
                for obj in current_objects
                if obj not in previous_objects
            ]

            removed_objects = [
                obj
                for obj in previous_objects
                if obj not in current_objects
            ]

            if added_objects or removed_objects:

                st.warning(
                    "🔄 Change detected at this location!"
                )

                if added_objects:

                    st.write(
                        "🆕 New objects: "
                        + ", ".join(added_objects)
                    )

                    speak(
                        "New objects detected: "
                        + ", ".join(added_objects)
                    )

                if removed_objects:

                    st.write(
                        "❌ Removed objects: "
                        + ", ".join(removed_objects)
                    )

                    speak(
                        "Objects no longer detected: "
                        + ", ".join(removed_objects)
                    )

            else:

                st.info(
                    "✅ No major change detected."
                )

                speak(
                    "No major change detected at "
                    + memory_location
                )

        else:

            st.info(
                "📍 This is the first recorded scene "
                "at this location."
            )

            speak(
                "This is the first recorded scene at "
                + memory_location
            )

        # Save current scene
        save_scene(
            scene_name=memory_location,
            location_name=memory_location,
            objects=current_objects,
            accessibility_status="Objects detected"
        )

        st.success(
            f"🧠 Scene saved at {memory_location}"
        )
        if previous_memories and latest_detected_objects:

           previous_objects = [
        obj.strip()
        for obj in latest_memory[2].split(",")
        if obj.strip()
    ]

    current_objects = list(
        set(latest_detected_objects)
    )

    added_objects = [
        obj for obj in current_objects
        if obj not in previous_objects
    ]

    removed_objects = [
        obj for obj in previous_objects
        if obj not in current_objects
    ]

    st.write("### 🔄 Change Summary")

    if added_objects:
        st.write(
            "🆕 Added: "
            + ", ".join(added_objects)
        )

    if removed_objects:
        st.write(
            "❌ Removed: "
            + ", ".join(removed_objects)
        )

    if not added_objects and not removed_objects:
        st.write("✅ No change detected.")