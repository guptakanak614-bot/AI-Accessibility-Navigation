import sqlite3
from datetime import datetime

DB_NAME = "accessibility_memory.db"


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ------------------------------------------------
    # OBJECT MEMORIES
    # ------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_name TEXT,
            distance TEXT,
            timestamp TEXT
        )
    """)

    # ------------------------------------------------
    # LOCATION-SPECIFIC SCENE MEMORIES
    # ------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_name TEXT,
            location_name TEXT,
            objects TEXT,
            accessibility_status TEXT,
            timestamp TEXT
        )
    """)

    # ------------------------------------------------
    # SAVED DESTINATIONS
    # ------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            latitude REAL,
            longitude REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# OBJECT MEMORY FUNCTIONS
# ==================================================

def save_memory(object_name, distance):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO memories
        (
            object_name,
            distance,
            timestamp
        )
        VALUES (?, ?, ?)
    """, (
        object_name,
        distance,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_memories():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            object_name,
            distance,
            timestamp
        FROM memories
        ORDER BY id DESC
    """)

    memories = cursor.fetchall()

    conn.close()

    return memories


# ==================================================
# LOCATION-SPECIFIC SCENE MEMORY
# ==================================================

def save_scene(
    scene_name,
    location_name,
    objects,
    accessibility_status
):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    objects_text = ", ".join(objects)

    cursor.execute("""
        INSERT INTO scenes
        (
            scene_name,
            location_name,
            objects,
            accessibility_status,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        scene_name,
        location_name,
        objects_text,
        accessibility_status,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_scenes():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            scene_name,
            location_name,
            objects,
            accessibility_status,
            timestamp
        FROM scenes
        ORDER BY id DESC
    """)

    scenes = cursor.fetchall()

    conn.close()

    return scenes


def get_location_scenes(location_name):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            scene_name,
            location_name,
            objects,
            accessibility_status,
            timestamp
        FROM scenes
        WHERE location_name = ?
        ORDER BY id DESC
    """, (location_name,))

    scenes = cursor.fetchall()

    conn.close()

    return scenes


# ==================================================
# SAVED DESTINATION FUNCTIONS
# ==================================================

def save_destination(
    name,
    latitude,
    longitude
):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT OR REPLACE INTO saved_destinations
        (
            name,
            latitude,
            longitude,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        latitude,
        longitude,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_saved_destinations():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            name,
            latitude,
            longitude
        FROM saved_destinations
        ORDER BY id DESC
    """)

    destinations = cursor.fetchall()

    conn.close()

    return destinations


def delete_destination(name):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM saved_destinations
        WHERE name = ?
    """, (name,))

    conn.commit()
    conn.close()


# ==================================================
# TEST DATABASE
# ==================================================

if __name__ == "__main__":

    # Create all tables
    create_database()

    print("====================================")
    print("✅ DATABASE READY")
    print("====================================")

    # ------------------------------------------------
    # Test Object Memory
    # ------------------------------------------------

    save_memory(
        "bicycle",
        "near"
    )

    print("\n🧠 Object Memories:")

    memories = get_memories()

    for memory in memories:
        print(memory)

    # ------------------------------------------------
    # Test Location Scene Memory
    # ------------------------------------------------

    save_scene(
        "College Entrance",
        "My College",
        [
            "person",
            "bicycle",
            "chair"
        ],
        "Path partially blocked"
    )

    print("\n📍 Location Scene Memories:")

    scenes = get_scenes()

    for scene in scenes:
        print(scene)

    # ------------------------------------------------
    # Test Specific Location Search
    # ------------------------------------------------

    print("\n🔎 Memories for My College:")

    college_scenes = get_location_scenes(
        "My College"
    )

    for scene in college_scenes:
        print(scene)

    # ------------------------------------------------
    # Test Saved Destination
    # ------------------------------------------------

    save_destination(
        "My College",
        28.9845,
        77.7064
    )

    print("\n🗺️ Saved Destinations:")

    destinations = get_saved_destinations()

    for destination in destinations:
        print(destination)

    print("\n====================================")
    print("✅ ALL MEMORY FEATURES WORKING")
    print("====================================")