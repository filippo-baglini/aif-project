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

# for env_id in babyai_envs:
#     env = gym.make(env_id, agent_pov = False)
#     env.reset()
#     instr = env.unwrapped.instrs
#     if isinstance(instr, BeforeInstr) or isinstance(instr, AndInstr):
#         print(instr.instr_b, instr.instr_a)
#     elif isinstance(instr, AfterInstr):
#         print(instr.instr_a, instr.instr_b)
#     else:
#         print(instr)
#     env.close()

if __name__ == "__main__":

    for env_id in babyai_envs:  # Loop through all environments
        print(f"Testing environment: {env_id}")
        env = gym.make(env_id, render_mode ="human", agent_pov = False)
        # env = gym.make("BabyAI-Open-v0", render_mode = "human")
        env.reset()  

        # print(env.unwrapped.instrs)
        # print(env.unwrapped.instrs.desc)
        # print(type(env.unwrapped.instrs.desc))

        width = env.unwrapped.width
        height= env.unwrapped.height

        agent_position = env.unwrapped.agent_pos
        agen_view_size = env.unwrapped.agent_view_size

        bot = Bot(env)
        max_steps = 240

  
        for i in range (max_steps):
            # time.sleep(1)
            action = bot.take_action(env)  # Call the test function
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated:
                print(reward)
                break
            # time.sleep(100)
            env.render()
        env.close()

