from scene_memory import (
    create_scene_database,
    get_scenes
)

# -----------------------------
# DATABASE
# -----------------------------
create_scene_database()

# -----------------------------
# GET SAVED SCENES
# -----------------------------
scenes = get_scenes()

print("\n🧠 AI Accessibility Memory")
print("=" * 40)

if not scenes:
    print("No scene memories found.")

else:

    print(f"Total saved scenes: {len(scenes)}\n")

    # Show latest 5 memories
    recent_scenes = scenes[:5]

    for i, scene in enumerate(recent_scenes, start=1):

        scene_name = scene[0]
        objects = scene[1]
        accessibility_status = scene[2]
        timestamp = scene[3]

        print(f"Memory {i}")
        print(f"Location: {scene_name}")
        print(f"Objects: {objects}")
        print(f"Accessibility: {accessibility_status}")
        print(f"Time: {timestamp}")
        print("-" * 40)

# -----------------------------
# SIMPLE RECALL
# -----------------------------
if scenes:

    latest_scene = scenes[0]

    print("\n🔊 AI Recall:")
    print(
        f"This location was previously observed. "
        f"{latest_scene[1]} were present. "
        f"Accessibility status: "
        f"{latest_scene[2]}."
    )