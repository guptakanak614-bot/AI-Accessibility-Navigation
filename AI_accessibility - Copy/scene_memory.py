import sqlite3
from datetime import datetime

DB_NAME = "accessibility_memory.db"


def create_scene_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_name TEXT,
            objects TEXT,
            accessibility_status TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_scene(scene_name, objects, accessibility_status):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    objects_text = ", ".join(objects)

    cursor.execute("""
        INSERT INTO scenes
        (scene_name, objects, accessibility_status, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        scene_name,
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
        SELECT scene_name, objects,
               accessibility_status, timestamp
        FROM scenes
        ORDER BY id DESC
    """)

    scenes = cursor.fetchall()

    conn.close()

    return scenes


if __name__ == "__main__":

    create_scene_database()

    save_scene(
        "College Entrance",
        ["person", "chair", "bicycle"],
        "Path partially blocked"
    )

    scenes = get_scenes()

    print("\n🧠 Saved Scenes:\n")

    for scene in scenes:
        print(scene)