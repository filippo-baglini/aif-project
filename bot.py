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


    def take_action(self, environment):

        #First action is update plan instance 
        self.plan()

        return self.plan.execute_subgoals()