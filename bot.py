import numpy as np
import gymnasium as gym
from minigrid.utils.baby_ai_bot import BabyAIBot

class Bot:

    def __init__ (self, environment):
        
        #environment to solve
        self.environment = environment

        #Initial goal
        self.mission = self.environment.unwrapped.mission

    def take_action(self, environment):
        return(self.environment.action_space.sample())



