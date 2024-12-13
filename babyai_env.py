import gymnasium as gym
from minigrid.utils.baby_ai_bot import BabyAIBot

from bot import Bot
import utils
import time
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX

# print(OBJECT_TO_IDX)
# print(COLOR_TO_IDX)

broken_bonus_envs = {
    "BabyAI-PutNextS5N2Carrying-v0",
    "BabyAI-PutNextS6N3Carrying-v0",
    "BabyAI-PutNextS7N4Carrying-v0",
    "BabyAI-KeyInBox-v0",
}


# get all babyai envs (except the broken ones)
babyai_envs = []
for k_i in gym.envs.registry.keys():
    if k_i.split("-")[0] == "BabyAI":
        if k_i not in broken_bonus_envs:
            babyai_envs.append(k_i)

if __name__ == "__main__":

    for env_id in babyai_envs:  # Loop through all environments
        print(f"Testing environment: {env_id}")
        env = gym.make(env_id, render_mode="human", agent_pov = False)
        # env = gym.make("BabyAI-Open-v0", render_mode = "human")
        env.reset()  

        width = env.unwrapped.width
        height= env.unwrapped.height

        agent_position = env.unwrapped.agent_pos
        agen_view_size = env.unwrapped.agent_view_size

        bot = Bot(env)
        max_steps = 100

        mission = bot.mission
        print(mission)
        
        goal = utils.parse_mission(mission) #extract the goal from the mission information
        goal_type, goal_color = goal
        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]

  


        for i in range (max_steps):
            # time.sleep(1)
            action = bot.take_action(env)  # Call the test function
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated:
                break

            env.render()
        env.close()

