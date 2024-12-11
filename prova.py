import gymnasium as gym

from minigrid.core.constants import COLOR_NAMES
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key, Wall
from minigrid.manual_control import ManualControl
from minigrid.minigrid_env import MiniGridEnv
import numpy as np


env = gym.make("BabyAI-GoToRedBallGrey-v0", render_mode="human")
observation, info = env.reset(seed=42)
print(env.action_space)
print(env.observation_space)
for _ in range(1000):
   action = env.action_space.sample()  # User-defined policy function
   observation, reward, terminated, truncated, info = env.step(action)
   #print(info)

   if terminated or truncated:
      observation, info = env.reset()
env.close()