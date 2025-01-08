import gymnasium as gym

from bot import Bot
from goal_parser import *
import time
from minigrid.core.constants import OBJECT_TO_IDX, COLOR_TO_IDX
from minigrid.envs.babyai.core.verifier import *

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

# get all minigrid envs
minigrid_envs = []
for k_i in gym.envs.registry.keys():
    if k_i.split("-")[0] == "MiniGrid":
        minigrid_envs.append(k_i)

reward_list = []

if __name__ == "__main__":
    print(len(babyai_envs))

    for i, env_id in enumerate(babyai_envs): # Loop through all environments
        print(f"Testing environment: {env_id}")
        #env = gym.make(env_id, render_mode ="human", agent_pov = False) #Uncomment to test all the different levels with visuals
        env = gym.make(env_id) #Uncomment to test all the different levels without visuals
        #env = gym.make("BabyAI-UnlockPickupDist-v0", render_mode = "human")
        #env = gym.make("BabyAI-PutNextS6N3-v0", render_mode = "human")
        #env = gym.make("BabyAI-BlockedUnlockPickup-v0", render_mode = "human")
        #env = gym.make("BabyAI-SynthS5R2-v0", render_mode = "human")
        env.reset(seed=1)

        print(env.unwrapped.mission) 

        bot = Bot(env)
        max_steps = 240
        num_steps = 0

        for i in range (max_steps):
            #time.sleep(50)
            action = bot.take_action(env)  # Call the test function
            if action == "FAILURE":
                print(f"LIVELLO FALLITO: {env}")
                break
            
            obs, reward, terminated, truncated, info = env.step(action)
            num_steps += 1
            
            if terminated:
                print(f"PROVA NUM_STEPS: {num_steps}")
                reward_list.append((env_id, num_steps))
                break
        
            env.render()
            if i == (max_steps - 1):
                print("MAX STEPS TAKEN")
        env.close()
    
    print(reward_list)
    sum_steps = 0
    for i in range(len(reward_list)):
        sum_steps += reward_list[i][1] 
    print(sum_steps)
    print(f"Num Mission completed {len(reward_list)}")