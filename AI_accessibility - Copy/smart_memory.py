import sqlite3
from datetime import datetime

DB_NAME = "accessibility_memory.db"


# -----------------------------
# GET LATEST MEMORY
# -----------------------------
def get_latest_memory(object_name):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT object_name, distance, timestamp
        FROM memories
        WHERE object_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (object_name,))

    memory = cursor.fetchone()

    conn.close()

    return memory


# -----------------------------
# CHECK IF MEMORY SHOULD SAVE
# -----------------------------
def should_save_memory(object_name, priority):

    latest_memory = get_latest_memory(object_name)

    # No previous memory
    if latest_memory is None:
        return True

    previous_priority = latest_memory[1]

    # Save only if priority changed
    if previous_priority != priority:
        return True

    # Otherwise don't save duplicate
    return False


# -----------------------------
# SAVE SMART MEMORY
# -----------------------------
def save_smart_memory(object_name, priority):

    if should_save_memory(object_name, priority):

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO memories
            (object_name, distance, timestamp)
            VALUES (?, ?, ?)
        """, (
            object_name,
            priority,
            timestamp
        ))

        conn.commit()
        conn.close()

        print(
            f"🧠 Memory saved: "
            f"{object_name} → {priority}"
        )

        return True

    else:

        print(
            f"⏭️ Duplicate skipped: "
            f"{object_name}"
        )

        return False


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":

    print("\n🧠 Smart Memory Test\n")

    save_smart_memory(
        "bicycle",
        "HIGH"
    )

    save_smart_memory(
        "bicycle",
        "HIGH"
    )

    save_smart_memory(
        "chair",
        "MEDIUM"
    )
    