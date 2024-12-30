from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX, STATE_TO_IDX

# def parse_mission(mission):
#     words = mission.split()
#     if "go to" in mission:
#         # Extract object and color from "go to the <color> <object>"
#         color = words[-2]
#         obj_type = words[-1]
#     elif "pick up" in mission:
#         # Extract object and color from "pick up the <color> <object>"
#         color = words[-2]
#         obj_type = words[-1]
#     elif "open" in mission:
#         color = words[-2]
#         obj_type = words[-1]
#     else:
#         raise ValueError(f"Unknown mission format: {mission}")
    
    
#     return obj_type, color


def understand_goal(instr):
        goal = instr.desc #extract the goal from the mission information
        goal_type = goal.type
        goal_color = goal.color
        goal_lock = goal.loc
        if (goal_lock is None):
            goal_lock = "open"
        #print(goal_type, goal_color, goal_lock)

        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]
        goal_lock = STATE_TO_IDX[goal_lock]

        return goal_type, goal_color, goal_lock