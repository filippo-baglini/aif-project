from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX, STATE_TO_IDX
from minigrid.envs.babyai.core.verifier import *
from subgoals import GoNextToSubgoal, OpenSubgoal, PickupSubgoal, DropSubgoal
import time



def process_desc(desc):
        goal = desc #extract the goal from the mission information
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