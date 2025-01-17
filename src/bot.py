from .planner import Planner
from minigrid.envs.babyai.core.verifier import *

class Bot:

    def __init__ (self, env):

        #Init plan instance of bot passing only env
        self.plan = Planner(env)


    def take_action(self, environment):

        #First action is update plan instance 
        self.plan()

        return self.plan.execute_subgoals()