import numpy as np
from goal_parser import understand_goal
from environment_handler import _process_obs
from utils import manhattan_distance
from planner import Planner
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX

class Bot:

    def __init__ (self, environment):

        #environment to solve
        self.environment = environment


        #Initial goal
        self.mission = environment.unwrapped.mission
        self.actions = environment.unwrapped.actions

        self.vis_mask = np.zeros(
            shape=(environment.unwrapped.width, environment.unwrapped.height), dtype=bool
        )


        self.vis_obs= np.zeros(
            shape=(environment.unwrapped.width, environment.unwrapped.height), dtype=object
        )

        # self.goal_type = None
        # self.goal_color = None
        # self.goal_pos = None
        # self.scanned = 0


    def take_action(self, environment):

        # Update the visibility mask and observations
        self.vis_mask, self.vis_obs = _process_obs(environment, self.vis_mask, self.vis_obs)

        # Create a planner instance
        plan = Planner(self)

        # Check if the goal is visible
        goal_pos = plan.look_for_goal()  # Returns the goal's position if visible, else None
        if goal_pos is None:
            # print("Goal not visible, exploring...")
            
            return self.actions.left # Rotate left to explore

        else:
            return plan.move_to_target(goal_pos)






