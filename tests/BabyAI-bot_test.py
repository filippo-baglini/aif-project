import sys
import os
# Get the absolute path of the parent directory of the project
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, "../"))

# Append the project directory to sys.path
sys.path.append(project_dir)

import gymnasium as gym
import pytest

from minigrid.utils.baby_ai_bot import BabyAIBot

# see discussion starting here: https://github.com/Farama-Foundation/Minigrid/pull/381#issuecomment-1646800992
broken_bonus_envs = {
    "BabyAI-PutNextS5N2Carrying-v0",
    "BabyAI-PutNextS6N3Carrying-v0",
    "BabyAI-PutNextS7N4Carrying-v0",
    "BabyAI-KeyInBox-v0",
    #"BabyAI-UnlockToUnlock-v0",
    #"BabyAI-GoToImpUnlock-v0",
    #"BabyAI-SynthS5R2-v0",
    #"BabyAI-Unlock-v0"
}

# get all babyai envs (except the broken ones)
babyai_envs = []
for k_i in gym.envs.registry.keys():
    if k_i.split("-")[0] == "BabyAI":
        if k_i not in broken_bonus_envs:
            babyai_envs.append(k_i)

result_list = []
@pytest.mark.parametrize("env_id", babyai_envs)
def test_bot(env_id):
    """
    The BabyAI Bot should be able to solve all BabyAI environments,
    allowing us therefore to generate demonstrations.
    """
    # Use the parameter env_id to make the environment
    env = gym.make(env_id)

    # reset env
    curr_seed = 0

    num_steps = 500
    steps = 0
    terminated = False
    while not terminated:
        env.reset(seed=98)

        # create expert bot
        expert = BabyAIBot(env)

        last_action = None
        for _step in range(num_steps):
            action = expert.replan(last_action)
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
            last_action = action
            env.render()

            if terminated:
                print(f"PROVA NUM_STEPS: {steps}")
                result = (env_id, steps)
                result_list.append(result)
                break

            if _step == num_steps - 1:
                return("MAX STEPS TAKEN")

    env.close()

if __name__ == "__main__":
    # Run a specific environment for debugging
    for i, env_id in enumerate(babyai_envs):  # Loop through all environments
        print(f"Testing environment: {env_id}")
        test_bot(env_id)  # Call the test function
    print(result_list)
    sum_steps = 0
    for i in range(len(result_list)):
        sum_steps += result_list[i][1]
    print(len(result_list)) 
    print(sum_steps)