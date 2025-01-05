from __future__ import annotations

import gymnasium as gym
import pytest

from minigrid.utils.baby_ai_bot import BabyAIBot

# see discussion starting here: https://github.com/Farama-Foundation/Minigrid/pull/381#issuecomment-1646800992
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

result_list = []
@pytest.mark.parametrize("env_id", babyai_envs)
def test_bot(env_id):
    """
    The BabyAI Bot should be able to solve all BabyAI environments,
    allowing us therefore to generate demonstrations.
    """
    # Use the parameter env_id to make the environment
    #env = gym.make(env_id)
    env = gym.make("BabyAI-MiniBossLevel-v0", render_mode="human") # for visual debugging

    # reset env
    curr_seed = 0

    num_steps = 240
    fava = 0
    terminated = False
    while not terminated:
        env.reset(seed=1)
        #print (env.observation_space)

        # create expert bot
        expert = BabyAIBot(env)
        #print(expert.mission)

        last_action = None
        for _step in range(num_steps):
            action = expert.replan(last_action)
            obs, reward, terminated, truncated, info = env.step(action)
            fava += 1
            last_action = action
            env.render()

            if terminated:
                print(f"PROVA NUM_STEPS: {fava}")
                result = (env_id, fava)
                result_list.append(result)
                break

        # try again with a different seed
        #curr_seed += 1

    env.close()

if __name__ == "__main__":
    # Run a specific environment for debugging
    for i, env_id in enumerate(babyai_envs):  # Loop through all environments
        if i == 50:
            break
        print(f"Testing environment: {env_id}")
        test_bot(env_id)  # Call the test function
    print(result_list)
    sum_steps = 0
    for i in range(len(result_list)):
        sum_steps += result_list[i][1] 
    print(sum_steps)