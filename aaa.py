import gymnasium as gym
from minigrid.utils.baby_ai_bot import BabyAIBot
import bot 
import utils
import time
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX

print(OBJECT_TO_IDX)
print(COLOR_TO_IDX)

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
    # Run a specific environment for debugging
    for env_id in babyai_envs:  # Loop through all environments
        print(f"Testing environment: {env_id}")
        env = gym.make(env_id)
        env = gym.make(env_id, render_mode="human")
        env.reset()
        grid = env.unwrapped.grid
        bot = bot.Bot(env)
        max_steps = 100

        mission = bot.mission
        print(mission)
        goal = utils.parse_mission(mission) #extract the goal from the mission information
        goal_type, goal_color = goal
        goal_type = OBJECT_TO_IDX[goal_type]
        goal_color = COLOR_TO_IDX[goal_color]
        grid = env.unwrapped.grid
        print(grid)

        for i in range (max_steps):
            action = bot.take_action(env)  # Call the test function
            obs, reward, terminated, truncated, info = env.step(action)
            #print(obs)
            partial_obs = obs['image']
            for i in range(partial_obs.shape[0]):  # Columns in the observation
                for j in range(partial_obs.shape[1]):  # Rows in the observation
                    obj_type, obj_color, obj_state = partial_obs[i, j]
                    print(f"Cell ({i}, {j}): Type={obj_type}, Color={obj_color}, State={obj_state}")
                    if obj_type == goal_type and obj_color == goal_color:
                        print(f"Goal found at relative position ({i}, {j})")

# Locate the goal in the full grid
            '''for x in range(grid.width):
                for y in range(grid.height):
                    obj = grid.get(x, y)
                    if obj:
                        print(f"object type = {obj.type} at position ({x}, {y})")
                    if obj and obj.type == goal_type and obj.color == goal_color:
                        print(f"Goal found at absolute position ({x}, {y})")   '''
            time.sleep(1000000)
            env.render()
        env.close()

