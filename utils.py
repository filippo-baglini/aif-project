def parse_mission(mission):
    words = mission.split()
    if "go to" in mission:
        # Extract object and color from "go to the <color> <object>"
        color = words[-2]
        obj_type = words[-1]
    elif "pick up" in mission:
        # Extract object and color from "pick up the <color> <object>"
        color = words[-2]
        obj_type = words[-1]
    else:
        raise ValueError(f"Unknown mission format: {mission}")
    return obj_type, color

