import numpy as np
from goal_parser import understand_goal
from environment_handler import _process_obs
from utils import manhattan_distance
from planner import Planner
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX
from minigrid.envs.babyai.core.verifier import *

class Bot:

    def __init__ (self, env):

        #Init plan instance of bot passing only env
        self.plan = Planner(env)
        self.goal_pos = None


    def take_action(self, environment):

        #First action is update plan instance 
        self.plan()

        # Check if the goal is visible
        self.goal_pos= self.plan.look_for_goal()  # Returns the goal's position if visible, else None
        if self.goal_pos is None:
            #print("Goal not visible, exploring env..")
            self.goal_pos = self.plan.look_for_goal()
            if self.goal_pos:
                return self.plan.move_to_target(self.goal_pos)
            return self.plan.find_frontiers() # Rotate left to explore

        else:
            if (self.plan.carrying == True and isinstance(self.plan.mission, PickupInstr)):
                return self.plan.put_down()
            return self.plan.move_to_target(self.goal_pos)