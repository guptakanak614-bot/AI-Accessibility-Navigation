from memory import create_database, get_memories


def compare_current_objects(current_objects):
    memories = get_memories()

    # Database में पहले detected objects
    previous_objects = set()

    for memory in memories:
        object_name = memory[0]
        previous_objects.add(object_name)

    current_objects = set(current_objects)

    # New objects
    new_objects = current_objects - previous_objects

    # Objects that disappeared
    removed_objects = previous_objects - current_objects

    if new_objects:
        print("\n🔴 NEW OBJECTS:")
        for obj in new_objects:
            print(f"- {obj}")

    if removed_objects:
        print("\n🟢 REMOVED OBJECTS:")
        for obj in removed_objects:
            print(f"- {obj}")

    if not new_objects and not removed_objects:
        print("\n✅ No major change detected.")


if __name__ == "__main__":

    create_database()

    # Example current camera detection
    current_objects = [
        "person",
        "chair"
    ]

    compare_current_objects(current_objects)